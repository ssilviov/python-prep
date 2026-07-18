import threading
import collections

class HitCounterQueue:

    SIZE = 300

    def __init__(self):
        self.counts = collections.deque()
        self.total = 0

    def hit(self, timestamp):
        if self.counts and self.counts[-1][0] == timestamp:
            self.counts[-1][1] += 1
        else:
            self.counts.append([timestamp, 1]) 
        self.total += 1
        while timestamp - self.counts[0][0] >= self.SIZE:
            c = self.counts.popleft()
            self.total -= c[1]
            
    def getHits(self, timestamp):
        while self.counts and timestamp - self.counts[0][0] >= self.SIZE:
            c = self.counts.popleft()
            self.total -= c[1]
        return self.total


class HitCounterCircular:

    SIZE = 300

    def __init__(self):
        self.hits = [0] * self.SIZE
        self.times = [0] * self.SIZE

    def hit(self, timestamp):
        idx = timestamp % self.SIZE
        if self.times[idx] == timestamp:
            self.hit[idx] += 1
        else:
            self.hit[idx] = 1
            self.times[idx] = timestamp

    def getHits(self, timestamp):
        res = 0
        for i in range(self.SIZE):
            if timestamp - self.times[i] < self.SIZE:
                res += self.hits[i]
        return res
                       
        
        
        
