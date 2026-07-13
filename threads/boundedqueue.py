"""
A queue where multiple producers can write and
multiple writers can read, but has a max size.
Producers block until one slot is empty and readers
block until one slot is filled. 

Uses 2 Conditions with the same lock to block the readers
and the writers separately.
"""
import threading
import collections

class BoundedQueue:

    def __init__(self, n):
        self.n = n
        self.queue = [None] * n
        self.end = 0
        self.start = 0
        self.size = 0
        lock = threading.Lock()
        self.not_empty = threading.Condition(lock)
        self.not_full = threading.Condition(lock)

    def push(self, item):
        with self.not_full:
            self.not_full.wait_for(lambda: self.size < self.n)
            self.queue[self.end] = item
            self.end += 1
            self.size += 1
            self.end %= self.n
            self.not_empty.notify()

    def pop(self): 
        with self.not_empty:
            self.not_empty.wait_for(lambda: self.size > 0)
            res = self.queue[self.start]
            self.start += 1
            self.start %= self.n
            self.size -= 1
            self.not_full.notify()
        return res
