import unittest
import solution


class SolutionTest(unittest.TestCase):

    def testSimple(self):
        numCourses = 2
        prerequisites = [[1,0]]
        sol = solution.Solution()
        self.assertEqual(
            sol.findOrder(numCourses, prerequisites), [0, 1])

    def testLong(self):
        numCourses = 4
        prerequisites = [[1,0],[2,0],[3,1],[3,2]]
        sol = solution.Solution()
        self.assertIn(sol.findOrder(numCourses, prerequisites),
                      [[0, 2, 1, 3], [0, 1, 2, 3]])


if __name__ == '__main__':
    unittest.main()
