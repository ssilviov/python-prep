import collections

class Solution:

    def bfs(self, edges, src, dst):
        if src not in edges or dst not in edges:
            return -1

        if src == dst:
            return 1

        q = collections.deque()
        q.append((src, 1.0))
        visited = {src}
        val = 1.0

        while q:
            x, val = q.popleft()
            if x == dst:
                return val
            for next, mul in edges[x]:
                if next not in visited:
                    q.append((next, val * mul))
                    visited.add(next)

        return -1

    def calcEquation(
            self, equations: list[list[str]],
            values: list[float],
            queries: list[list[str]]) -> list[float]:

        edges = collections.defaultdict(list)

        for (src, dst), val in zip(equations, values): 
            edges[src].append((dst, val))
            edges[dst].append((src, 1.0 / val))

        return [self.bfs(edges, s, d) for s, d in queries]
