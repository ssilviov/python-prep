import heapq
import collections

class Element:

    def __init__(self, word: str, count: int):
        self.word = word
        self.count = count

    def __lt__(self, other: "Element") -> bool:
        if self.count != other.count:
            return self.count < other.count
        return self.word > other.word


class Solution:

    def topKFrequent(self, words: list[str], k: int) -> list[str]:

        counts = collections.defaultdict(int)
        for w in words:
            counts[w] += 1

        heap = []
        for w, c in counts.items():
            heapq.heappush(heap, Element(w,c))
            if len(heap) > k:
                heapq.heappop(heap)

        res = []
        while heap:
            res.append(heapq.heappop(heap).word)
        res.reverse()
        return res
            
