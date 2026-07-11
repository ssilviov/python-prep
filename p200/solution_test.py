import unittest
import solution


class SolutionTest(unittest.TestCase):

    def testGrid1(self):
        sol = solution.Solution()
        grid = [
            ["1","1","1","1","0"],
            ["1","1","0","1","0"],
            ["1","1","0","0","0"],
            ["0","0","0","0","0"]
        ]
        self.assertEqual(sol.numIslands(grid), 1)

    def testGrid2(self):
        sol = solution.Solution()
        grid = [
            ["1","1","0","0","0"],
            ["1","1","0","0","0"],
            ["0","0","1","0","0"],
            ["0","0","0","1","1"]
        ]
        self.assertEqual(sol.numIslands(grid), 3)


if __name__ == '__main__':
    unittest.main()
