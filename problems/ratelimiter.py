from typing import Callable, Optional
import collections
import threading
import time

class ClientProfile:

    def __init__(self):
        self.last_accessed = -1
        self.queue = collections.deque()
        self.lock = threading.Lock()


class SlidingWindowRateLimiter:

    def __init__(self,
                 max_requests: int,
                 window_size_sec: float,
                 clock_fn : Optional[Callable[[], float]] = None):
        """
        :param max_requests: Max requests allowed within the sliding window.
        :param window_size_sec: Window duration in seconds (e.g., 60.0 for 1 minute).
        :param clock_fn: Callable returning current time in seconds (defaults to time.time).
                         Crucial for unit testing!
        """
        self.max_requests = max_requests
        self.window_size_sec = window_size_sec
        self.clock_fn = time.time if clock_fn is None else clock_fn

        self.client_map = {}
        self.global_lock = threading.Lock()

    def allow_request(self, client_id: str) -> bool:
        """
        Evaluates whether a request from client_id is permitted at the current time.
        Returns True if permitted (and records the event), or False if rate limit is exceeded.
        Must be thread-safe.
        """
        current_time = self.clock_fn()
        min_time = current_time - self.window_size_sec
        profile = None
        with self.global_lock:
            if client_id not in self.client_map:
                self.client_map[client_id] = ClientProfile()
            profile  = self.client_map[client_id]

        with profile.lock:
            profile.last_accessed = current_time
            queue = profile.queue
            while queue and queue[0] < min_time:
                queue.popleft()
            if len(queue) < self.max_requests:
                queue.append(current_time)
                return True
        return False
            

    def cleanup_inactive_clients(self, idle_timeout_sec: float) -> int:
        """
        Purges memory for clients who haven't sent a request in over idle_timeout_sec.
        Returns the number of client profiles removed.
        Must be thread-safe.
        """
        
        current_time = self.clock_fn()
        min_time = current_time - idle_timeout_sec
        
        with self.global_lock:
            clients = list(self.client_map.items())

        res = 0
        for client, profile in clients:
            with profile.lock:
                if profile.last_accessed < min_time:
                    with self.global_lock:
                        if client in self.client_map and self.client_map[client] is profile:
                            del self.client_map[client]
                            res += 1
        return res
