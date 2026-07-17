import unittest
import solution

def make_list(l: list[int]) -> solution.ListNode:
    head = None
    tail = None

    for v in l:
        if not head:
            head = solution.ListNode(v)
            tail = head
        else:
            tail.next = solution.ListNode(v)
            tail = tail.next
    return head


def expand_list(l: solution.ListNode) -> list[int]:
    res = []
    while l:
        res.append(l.val)
        l = l.next
    return res


class SolutionTest(unittest.TestCase):

    def test1(self):
        sol = solution.Solution()
        lists = [ make_list(l) for l in [[1,4,5],[1,3,4],[2,6]] ]
        output = [1,1,2,3,4,4,5,6]
        self.assertListEqual(expand_list(sol.mergeKLists(lists)), output)

    def testEmpty(self):
        sol = solution.Solution()
        self.assertListEqual(expand_list(sol.mergeKLists([])), [])

    def testListofEmpty(self):
        sol = solution.Solution()
        self.assertListEqual(expand_list(sol.mergeKLists([[]])), [])


if __name__ == '__main__':
    unittest.main()
