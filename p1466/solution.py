import collections


class Solution:

    def minReorder(self, n: int, connections: list[list[int]]) -> int:
        adj = collections.defaultdict(list)
        rev = collections.defaultdict(list)

        for s, d in connections:
            adj[s].append((d, 1))
            adj[d].append((s, 0))

        q = collections.deque()
        visited = [False] * n

        q.append(0)
        visited[0] = True
        res = 0
        
        while q:
            s = q.popleft()

            for d, is_wrong in adj[s]:
                if not visited[d]:
                    q.append(d)
                    visited[d] = True
                    res += is_wrong
            
        return res
