import collections

class Solution:

    def findOrder(self, numCourses: int, prerequisites: list[list[int]]) -> list[int]:

        degrees = [0] * numCourses
        adjacencies = collections.defaultdict(list)

        for edge in prerequisites:
            a, b = edge
            degrees[a] += 1
            adjacencies[b].append(a)

        q = collections.deque()
        q.extend(k for k in range(numCourses) if degrees[k] == 0)
        res = []

        while q:
            n = q.popleft()
            res.append(n)

            for i in adjacencies[n]:
                degrees[i] -= 1
                if degrees[i] == 0:
                    q.append(i)

        return res if len(res) == numCourses else []
