import unittest
import solution


class SolutionTest(unittest.TestCase):

    def testMedian(self):
        medianFinder = solution.MedianFinder()
        medianFinder.addNum(1)    # arr = [1]
        medianFinder.addNum(2)    # arr = [1, 2]
        # return 1.5 (i.e., (1 + 2) / 2)
        self.assertEqual(medianFinder.findMedian(), 1.5)
        medianFinder.addNum(3)    # arr[1, 2, 3]
        self.assertEqual(medianFinder.findMedian(), 2)


if __name__ == '__main__':
    unittest.main()
