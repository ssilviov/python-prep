import unittest
import solution


class SolutionTest(unittest.TestCase):

    def test1(self):
        s = solution.Solution()
        words = ["i","love","leetcode","i","love","coding"]
        self.assertEqual(s.topKFrequent(words, 2), ["i", "love"])

    def test2(self):
        s = solution.Solution()
        words =["the","day","is","sunny","the","the","the","sunny","is","is"]
        self.assertEqual(s.topKFrequent(words, 4), ["the","is","sunny","day"])


if __name__ == '__main__':
    unittest.main()
