import collections
import heapq

class MedianFinder:

    def __init__(self):
        self.bottom = []
        self.top = []

    def addNum(self, num: int) -> None:
        heapq.heappush(self.bottom, -num)
        n = heapq.heappop(self.bottom)
        heapq.heappush(self.top, -n)
        if len(self.top) - 1 > len(self.bottom):
            n = heapq.heappop(self.top)
            heapq.heappush(self.bottom, -n)

        print(f"{self.bottom=}", f"{self.top=}")


    def findMedian(self) -> float:
        print(f"{self.bottom=}", f"{self.top=}")
        if len(self.top) > len(self.bottom):
            return self.top[0]
        return (-self.bottom[0] + (self.top[0])) / 2.0
