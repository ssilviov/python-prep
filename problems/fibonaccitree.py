import functools

@functools.cache
def size(k: int):
    """Returns size of fibonacci tree of order k."""
    if k <= 2
        return 1

    a, b = 0, 1
    for i in range(2, k + 1):
        a, b = b, a + b
    return b

def find_rec(k: int, current: int, a: int):
    """Find path until node a from node current at rank k."""
    if current == a:
        return [current]

    if k <= 2:
        return []

    res = None
    size_left = size(k-1)
    if a <= size_left + current:
        res = find_rec(k - 1, current + 1, a)
    else:
        res = find_rec(k - 2, current + 1 + size_left, a)

    if res:
        res.append(current)
    return res

def find_path(k: int, a:int, b:int) -> list[int]:
    """Find path from node a to node b in a fibonacci tree.

    The nodes are labeled in preorder mode.
    """
    res = []

    path_a = list(reversed(find_rec(k, 0, a)))
    path_b = list(reversed(find_rec(k, 0, b)))

    idx = 0
    min_len = min(len(path_a), len(path_b))
    while idx < min_len and path_a[idx] == path_b[idx]:
        idx += 1
            
    return reversed(path_a[idx:]) + path_b[idx+1:]
