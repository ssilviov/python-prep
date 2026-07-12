import unittest
import solution


class SolutionTest(unittest.TestCase):

    def test1(self):
        sol = solution.Solution()
        n = 6
        connections = [[0,1],[1,3],[2,3],[4,0],[4,5]]
        self.assertEqual(sol.minReorder(n, connections), 3)

    def test2(self):
        sol = solution.Solution()
        n = 5
        connections = [[1,0],[1,2],[3,2],[3,4]]
        self.assertEqual(sol.minReorder(n, connections), 2)

    def test3(self):
        sol = solution.Solution()
        n = 3
        connections = [[1,0],[2,0]]
        self.assertEqual(sol.minReorder(n, connections), 0)


if __name__ == '__main__':
    unittest.main()
