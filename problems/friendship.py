import collection

class DSU:

    def __init__(self, n):
        self.parents = list(range(n))
        self.size = [1] * n

    def find(self, a):
        if self.parents[a] != a:
            self.parents[a] = self.find(self.parents[a])
        return self.parents[a]

    def union(self, a, b):
        a = self.find(a)
        b = self.find(b)

        if a == b:
            return False

        if self.size[a] < self.size[b]:
            a, b = b, a
        self.parents[b] = a
        self.size[a] += self.size[b]

        return True


def find_earliest_friendships(n, connections):
    connections.sort(key=lambda x: x[0])
    dsu = DSU(n)
    components = n

    for t, a, b in connections:
        if dsu.union(a, b):
            components -= 1
        if components == 1:
            return t

    return -1


class DSUGroup(DSU):

    def __init__(self, n, group):
        super().__init__(n)
        self.has_group_member = [x in group for x in range(len(n))]

    def union_and_reduce(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        merged = super().union(a, b)
        if not merged:
            return False, 0

        reduced = 0
        if self.has_group_member[root_a] and self.has_group_member[root_b]:
            reduced = 1

        new_root = self.find(a)
        self.has_group_member[new_root] = (
            self.has_group_member[root_a] or self.has_group_member[root_b])
            
        return True, reduced


class DSUSize(DSU):

    def __init__(self, n):
        super().__init__(n)
        self.max_size = 1

    def union_and_max_size(self, a, b):
        root_a = self.find(a)
        root_b = self.find(b)

        merged = super().union(a, b)
        if merged:
            new_root = self.find(a)
            if self.size[new_root] > self.max_size:
                self.max_size = new_size
        return merged, self.max_size



def find_erliest_k_group(n, connections, k):
    connections.sort(key=lambda x: x[0])
    dsu = DSUSize(n)

    for t, a, b in connections:
        merged, max_size = dsu.union_and_max_size(a, b)
        if max_size >= k:
            return t

    return -1

