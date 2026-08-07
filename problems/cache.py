import collections
import time
import threading
import math

class LatencyTracker:

    SIZE = 60

    def __init__(self):
        self.count = [0] * self.SIZE
        self.latency = [.0] * self.SIZE
        self.timestamp = [-1] * self.SIZE
        self.lock = [threading.Lock() for _ in range(self.SIZE)]

    def add_sample(self, timestamp, latency):
        second = math.floor(timestamp)
        idx = second % self.SIZE

        with self.lock[idx]:
            if self.timestamp[idx] != second:
                self.timestamp[idx] = second
                self.count[idx] = 0
                self.latency[idx] = .0

            self.count[idx] += 1
            self.latency[idx] += latency

    def get_average(self, timestamp):
        second = math.floor(timestamp)

        total_latency = 0.0
        total_count = 0
        for i in range(self.SIZE):
            with self.lock[i]:
                if second - self.SIZE < self.timestamp[i] <= second:
                    total_count += self.count[i]
                    total_latency += self.latency[i]
        if total_count > 0:
            return total_latency / total_count
        return 0.0

class ConcurrentMap:

    def __init__(self):
        self.map = {}
        self.lock = threading.Lock()
        self.put_tracker = LatencyTracker()
        self.get_tracker = LatencyTracker()

    def put(self, key, value):
        start = time.monotonic()
        with self.lock:
            self.map[key] = value
        stop = time.monotonic()
        self.put_tracker.add_sample(start, stop - start)

    def get(self, key):
        start = time.monotonic()
        with self.lock:
            res = self.map.get(key, None)
        stop = time.monotonic()
        self.get_tracker.add_sample(start, stop - start)
        return res

    def get_put_load(self):
        return self.put_tracker.get_average(time.monotonic())

    def get_get_load(self):
        return self.get_tracker.get_average(time.monotonic())
        
