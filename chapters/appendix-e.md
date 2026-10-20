[← 附录 D 参考资料与源码定位](appendix-d.md) · [全书目录](../README.md#全书目录) · [结语：设计的目标是可解释的行为 →](99-afterword.md)

---

# 附录 E 策略内核完整实现

本附录与配套工程文件同步生成，方便仅持有 EPUB 的读者复制实验。需要 Python 3.10 或以上版本。熔断模型采用连续失败阈值，不是滚动窗口错误率模型；同一时刻仅允许一个半开探测。生产代码需要并发同步与取消策略。

## gateway_core.py

``` python
"""Educational policy kernel. Single-threaded; not an HTTP proxy."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class Route:
    id: str
    prefix: str
    upstream: str
    priority: int = 0

@dataclass(frozen=True)
class Snapshot:
    revision: int
    routes: tuple[Route, ...]

    def match(self, path: str):
        candidates = [r for r in self.routes
                      if r.prefix == '/' or path == r.prefix
                      or path.startswith(r.prefix + '/')]
        return min(candidates,
                   key=lambda r: (-r.priority, -len(r.prefix), r.id),
                   default=None)

class ConfigStore:
    def __init__(self):
        self.current = Snapshot(0, ())

    def publish(self, revision, routes):
        if not isinstance(revision, int) or revision <= self.current.revision:
            return False
        routes = tuple(routes)
        ids = set()
        for r in routes:
            if not r.id or r.id in ids:
                raise ValueError('empty or duplicate route id')
            ids.add(r.id)
            if not r.prefix.startswith('/') or (r.prefix != '/' and r.prefix.endswith('/')):
                raise ValueError('use canonical path prefixes')
            if r.upstream not in {'orders', 'inventory', 'payments'}:
                raise ValueError('upstream outside allowlist')
        # Real concurrent runtimes require their own publication primitive.
        self.current = Snapshot(revision, routes)
        return True

class TokenBucket:
    def __init__(self, rate, capacity, now=0.0):
        if not all(isfinite(x) for x in (rate, capacity, now)) or rate <= 0 or capacity <= 0:
            raise ValueError('positive finite rate and capacity required')
        self.rate, self.capacity = rate, capacity
        self.tokens, self.last = float(capacity), now

    def allow(self, now, cost=1.0):
        if not isfinite(now) or not isfinite(cost) or cost <= 0:
            raise ValueError('finite time and positive cost required')
        if now < self.last:
            raise ValueError('monotonic time required')
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens < cost:
            return False
        self.tokens -= cost
        return True

@dataclass(frozen=True)
class Ticket:
    generation: int
    serial: int
    probe: bool

class CircuitBreaker:
    """Consecutive failures, one half-open probe, explicit completion tickets.

    Generation rejects late results from requests admitted before a state change.
    Every admitted ticket must be completed once, including cancellation paths.
    """
    def __init__(self, threshold=3, recovery=5.0):
        if threshold < 1 or not isfinite(recovery) or recovery <= 0:
            raise ValueError('invalid breaker parameters')
        self.threshold, self.recovery = threshold, recovery
        self.state, self.failures = 'closed', 0
        self.opened_at = 0.0
        self.generation, self.serial = 0, 0
        self.pending = set()
        self.probe_busy = False
        self.last_time = float('-inf')

    def _time(self, now):
        if not isfinite(now) or now < self.last_time:
            raise ValueError('monotonic time required')
        self.last_time = now

    def _transition(self, state):
        self.state = state
        self.generation += 1
        self.pending.clear()
        self.probe_busy = False

    def acquire(self, now):
        self._time(now)
        if self.state == 'open':
            if now - self.opened_at < self.recovery:
                return None
            self._transition('half-open')
        probe = self.state == 'half-open'
        if probe and self.probe_busy:
            return None
        self.probe_busy = probe
        self.serial += 1
        ticket = Ticket(self.generation, self.serial, probe)
        self.pending.add(ticket)
        return ticket

    def complete(self, ticket, success, now):
        self._time(now)
        if ticket not in self.pending:
            return False  # duplicate, stale or unrecognized result
        self.pending.remove(ticket)
        if ticket.probe:
            if success:
                self._transition('closed')
                self.failures = 0
            else:
                self._transition('open')
                self.opened_at = now
        elif success:
            self.failures = 0
        else:
            self.failures += 1
            if self.failures >= self.threshold:
                self._transition('open')
                self.opened_at = now
        return True

if __name__ == '__main__':
    store = ConfigStore()
    store.publish(1, [Route('orders', '/api/orders', 'orders')])
    captured = store.current
    print('route:', captured.match('/api/orders/42'))
    bucket = TokenBucket(rate=1, capacity=2)
    print('burst:', [bucket.allow(0) for _ in range(3)])
    store.publish(2, [Route('inventory', '/api/items', 'inventory')])
    print('captured revision:', captured.revision, 'new revision:', store.current.revision)
```

## test_gateway_core.py

``` python
import unittest
from gateway_core import Route, ConfigStore, TokenBucket, CircuitBreaker

class KernelTests(unittest.TestCase):
    def test_route_determinism_and_boundary(self):
        routes = [Route('z', '/api', 'orders'), Route('b', '/api/orders', 'orders'),
                  Route('a', '/api/orders', 'inventory')]
        for seq in (routes, list(reversed(routes))):
            s = ConfigStore(); s.publish(1, seq)
            self.assertEqual(s.current.match('/api/orders/42').id, 'a')
            self.assertIsNone(s.current.match('/apix'))
        s.publish(2, [*routes, Route('priority', '/', 'payments', 10)])
        self.assertEqual(s.current.match('/api/orders').id, 'priority')

    def test_snapshot_revision_and_rollback(self):
        s = ConfigStore(); old = [Route('a', '/a', 'orders')]
        self.assertTrue(s.publish(1, old))
        captured = s.current
        self.assertTrue(s.publish(2, []))
        self.assertFalse(s.publish(1, old))
        self.assertFalse(s.publish(2, old))
        self.assertIsNotNone(captured.match('/a'))
        self.assertIsNone(s.current.match('/a'))
        self.assertTrue(s.publish(3, old))
        self.assertIsNotNone(s.current.match('/a'))

    def test_reject_bad_config_without_partial_application(self):
        s = ConfigStore(); s.publish(1, [Route('a', '/a', 'orders')])
        for routes in ([Route('x', '/x', 'unknown')],
                       [Route('a', '/a', 'orders'), Route('a', '/b', 'inventory')],
                       [Route('x', '/x/', 'orders')]):
            with self.assertRaises(ValueError): s.publish(2, routes)
            self.assertEqual(s.current.revision, 1)

    def test_bucket_burst_refill_and_capacity(self):
        b = TokenBucket(2, 2)
        self.assertEqual([b.allow(0) for _ in range(3)], [True, True, False])
        self.assertFalse(b.allow(.49))
        self.assertTrue(b.allow(.5))
        self.assertTrue(b.allow(100, 2))
        self.assertFalse(b.allow(100))
        with self.assertRaises(ValueError): b.allow(99)
        with self.assertRaises(ValueError): b.allow(101, 0)

    def test_breaker_open_single_probe_and_recovery(self):
        b = CircuitBreaker(2, 5)
        for t in (0, 1): b.complete(b.acquire(t), False, t)
        self.assertEqual(b.state, 'open')
        self.assertIsNone(b.acquire(5.99))
        probe = b.acquire(6)
        self.assertIsNotNone(probe)
        self.assertIsNone(b.acquire(6))
        b.complete(probe, True, 6)
        self.assertEqual(b.state, 'closed')
        self.assertIsNotNone(b.acquire(6))

    def test_failed_probe_and_late_results(self):
        b = CircuitBreaker(1, 2)
        first, late = b.acquire(0), b.acquire(0)
        b.complete(first, False, 0)
        self.assertFalse(b.complete(late, True, 1))
        self.assertEqual(b.state, 'open')
        probe = b.acquire(2)
        b.complete(probe, False, 2)
        self.assertIsNone(b.acquire(3))
        next_probe = b.acquire(4)
        self.assertIsNotNone(next_probe)
        self.assertFalse(b.complete(probe, True, 4))
        b.complete(next_probe, True, 4)
        self.assertEqual(b.state, 'closed')

if __name__ == '__main__': unittest.main()
```

---

[← 附录 D 参考资料与源码定位](appendix-d.md) · [全书目录](../README.md#全书目录) · [结语：设计的目标是可解释的行为 →](99-afterword.md)
