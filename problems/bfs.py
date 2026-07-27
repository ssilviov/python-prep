import collections

def find_path(adj: dict[str, list[str]], start: str, target: str) -> list[str] | None:
    if start == target:
        return [start]

    if start not in adj:
        return []

    queue = collections.deque()
    visited = dict()
    queue.appendleft(start)
    visited[start] = None
    while queue:
        a = queue.popleft()
        if a == target:
            break
        for b in adj[a]:
            if b in visited:
                continue
            visited[b] = a
            queue.append(b)

    if target not in visited:
        return []

    res = [target]
    while res[-1] != start:
        res.append(visited[res[-1]])

    res.reverse()
    return res

graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E', 'A'],  # Note the cycle B -> A -> B
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': [],
    'Z': ['Y']             # Disconnected component
}
              
assert( t == ['A', 'C', 'F'])
assert(find_path(graph, 'A', 'D') == ['A', 'B', 'D'])
assert(find_path(graph, 'A', 'Z') == [])

            
