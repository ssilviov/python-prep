import unittest
import solution


class SolutionTest(unittest.TestCase):

    def testExample1(self):
        sol = solution.Solution()
        equations = [["a","b"],["b","c"]]
        values = [2.0,3.0]
        queries = [["a","c"],["b","a"],["a","e"],["a","a"],["x","x"]]

        self.assertEqual(sol.calcEquation(
            equations, values, queries),
            [6.0, 0.5, -1.0, 1.0, -1.0])

    def testExample2(self):
        sol = solution.Solution()
        equations = [["a","b"],["b","c"],["bc","cd"]]
        values = [1.5,2.5,5.0]
        queries = [["a","c"],["c","b"],["bc","cd"],["cd","bc"]]

        self.assertEqual(sol.calcEquation(
            equations, values, queries),
            [3.75000,0.40000,5.00000,0.20000])

    def testExample3(self):
        sol = solution.Solution()
        equations = [["a","b"]]
        values = [0.5]
        queries = [["a","b"],["b","a"],["a","c"],["x","y"]]
        self.assertEqual(sol.calcEquation(
            equations, values, queries),
            [0.50000,2.00000,-1.00000,-1.00000])


if __name__ == '__main__':
    unittest.main()
