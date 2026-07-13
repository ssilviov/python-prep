"""
A class that simulates a buffered file writer.

Multiple threads can write to an in memory buffer very quickly. One
background threads flushes the buffer to file when the buffer is full
or after a timeout.

To make writes fast, uses a double buffer, so a new buffer is already
allocated once one is full and writer threads don't have to wait for
the flush to be finished. 
"""
import threading

class BufferedDiskWriter:

    def __init__(self, size, timeout):
        self.size = size
        self.current = 0
        self.end = 0

        self.to_flush_idx = None
        self.to_flush_size = 0

        self.buffers = [[None] * size, [None] * size]]

        self.lock = threading.Lock()
        self.timeout = timeout

        self.cv = threading.Condition(self.lock)

        self.is_running = True

    def write(self, message):
        with self.cv:
            self.cv.wait_for(lambda: self.to_flush_idx is None)

            buffer = self.buffers[self.current]
            buffer[self.end] = message
            self.size += 1
            if self.size == self.n:
                self.to_flush_idx = self.current
                self.to_flush_size = self.size

                self.current = (self.current + 1) % 2
                self.size = 0
                self.end = 0
                self.cv.notify()

    def shutdown(self):
        with self.cv:
            self.is_running = False
            self.cv.notify_all()

    def flushBackground(self):
        to_flush = None
        size = 0
        with self.cv:
            expired = self.cv.wait_for(
                lambda: self.to_flush_idx is not None and self.is_running,
                self.timeout)

            
            if not expired:
                to_flush = self.current
                self.current = (self.current + 1) % 2
                self.size = 0
                self.end = 0
            else:
                to_flush = self.to_flush
                size = self.size
                self.to_flush = None

        self.write_to_disk(to_flush, size)
        
