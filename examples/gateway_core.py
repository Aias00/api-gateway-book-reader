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
