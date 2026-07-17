from typing import Optional
import heapq

# Definition for singly-linked list.
class ListNode:

    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:

    def mergeKLists(self, lists: list[Optional["ListNode"]]) -> Optional["ListNode"]:
        head = ListNode(0)
        tail = head

        heap = []
        unique_id = 0
        for h in lists:
            if h:
                heapq.heappush(heap, (h.val, unique_id, h))
                unique_id += 1

        while heap:
            val, _, h = heapq.heappop(heap)

            tail.next = h
            tail = tail.next

            next = h.next
            tail.next = None

            if next:
                heapq.heappush(heap, (next.val, unique_id, next))
                unique_id += 1

        return head.next

       
