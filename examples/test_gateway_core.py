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
