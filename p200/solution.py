import collections

LAND = '1'
WATER = '0'

NEIGHBOURS = [(0,1), (1, 0), (0, -1), (-1, 0)]

class Solution:
    """Implement solution for problem 200."""

    def validate_get_size(self, grid: list[list[str]]) -> tuple[int, int]:
        n = len(grid)
        if n == 0:
            return "Empty grid."

        m = len(grid[0])
        if m == 0:
            return "Grid with empty rows."
        if any(len(x) != m for x in grid):
            return "Grid has different lengths for rows."

        return n, m

    def bfs(self, i: int, j: int, grid: list[list[str]], n: int, m: int):
        q = collections.deque()
        q.append((i, j))
        grid[i][j] = WATER

        while q:
            x, y = q.popleft()
            for dx, dy in NEIGHBOURS:
                x1 = x + dx
                y1 = y + dy
                if 0 <= x1 < n and 0 <= y1 < m and grid[x1][y1] == LAND:
                    grid[x1][y1] = WATER
                    q.append((x1, y1))

    def numIslands(self, grid: list[list[str]]) -> int:
        """Return number of islands in the grid."""
        n, m = self.validate_get_size(grid)

        count = 0
        for i in range(n):
            for j in range(m):
                if grid[i][j] == LAND:
                    count += 1
                    self.bfs(i, j, grid, n, m)

        return count
