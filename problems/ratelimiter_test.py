import time
import threading
from collections import deque
from typing import Dict, Callable, Optional
import ratelimiter
import unittest

class MockClock:
    def __init__(self, initial_time: float = 1000.0):
        self._curr_time = initial_time
        self._lock = threading.Lock()

    def time(self) -> float:
        with self._lock:
            return self._curr_time

    def advance(self, seconds: float):
        with self._lock:
            self._curr_time += seconds


class RateLimiterTest(unittest.TestCase):

    def test_basic_sliding_window(self):
        clock = MockClock()
        limiter = ratelimiter.SlidingWindowRateLimiter(
            max_requests=3, window_size_sec=10.0, clock_fn=clock.time)

        # 3 requests at T=1000.0 -> All allowed
        self.assertTrue(limiter.allow_request("user_1"))
        self.assertTrue(limiter.allow_request("user_1"))
        self.assertTrue(limiter.allow_request("user_1"))

        # 4th request at T=1000.0 -> Rejected
        self.assertFalse(limiter.allow_request("user_1"))

        # Advance time by 6 seconds (T=1006.0) -> Still within 10s window of initial 3 requests
        clock.advance(6.0)
        self.assertFalse(limiter.allow_request("user_1"))

        # Advance time by 5 more seconds (T=1011.0) -> Initial 3 requests are now expired (>10s old)
        clock.advance(5.0)
        self.assertTrue(limiter.allow_request("user_1"))  # Allowed!


    def test_concurrent_requests(self):
        limiter = ratelimiter.SlidingWindowRateLimiter(
            max_requests=500, window_size_sec=1.0, clock_fn=time.time)
        allowed_count = 0
        lock = threading.Lock()

        def worker():
            nonlocal allowed_count
            for _ in range(100):
                if limiter.allow_request("concurrent_user"):
                    with lock:
                        allowed_count += 1

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Out of 1000 total attempts within <1s, exactly 500 must succeed
        self.assertEqual(allowed_count, 500)

if __name__ == "__main__":
    unittest.main()
