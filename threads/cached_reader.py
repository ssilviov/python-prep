"""
A file reader class with a cache because of slow storage.

Split a file in blocks of BLOCK SIZE and caches them in a cache of
a specified size. The cache is evicted with an LRU policy.

Multiple threads can read chunks from the cache at the same time but
a single thread does the reading.

Each cache line contains a Condition and a Lock so that multiple thread
trying to access a missing slot will wait for the read and be awaken
when it's finished.

Careful handling of indexes and evicting the cache.
"""
import threading
import collections
import enum

BLOCK_SIZE = 10

class Status(enum.Enum):
    NOTREAD = enum.auto()
    AVAILABLE = enum.auto()
    PENDING = enum.auto()

class CacheLine:
    def __init__(self):
        self.status = Status.NOTREAD
        self.lock = threading.Lock()
        self.cv = threading.Condition(self.lock)
        self.data = None
        self.id = None

class CachedReader:

    def __init__(self, name, cache_size, file_size):
        self.name = name
        self.file_size = file_size
        self.cache_size = cache_size
        self.cache = [CacheLine() for i in range(cache_size)]
        self.cache_map = {}
        self.lru = collections.deque(range(cache_size))
        self.cache_lock = threading.Lock()

    def ids_from_offsets(self, start_offset, end_offset):
        start = start_offset // BLOCK_SIZE
        end = end_offset // BLOCK_SIZE
        return range(start, end+1)

    def readFromFile(self, chunk_id):
        # slow read from file
        return f"data {chunk_id}"

    def read_chunk(self, i):
        with self.cache_lock:
            idx = self.cache_map.get(i, None)
            if idx is None:
                # remove the oldest cache location.
                idx = self.lru.popleft()
                line = self.cache[idx]

                if line.id is not None:
                    self.cache_map.pop(line.id, None)

                line.data = None
                line.status = Status.NOTREAD
                line.id = i

                self.cache_map[i] = idx
            else:
                self.lru.remove(idx)
            self.lru.append(idx)

        line = self.cache[idx]
        with line.cv:
            if line.status == Status.PENDING:
                line.cv.wait_for(lambda: self.cache[idx][0] == Status.AVAILABLE)

            if line.status == Status.NOTREAD:
                line.status = Status.PENDING

                line.lock.release()
                try:
                    data = self.readFromFile(i)
                finally:
                    line.lock.acquire()

                line.data = data
                line.status = Status.AVAILABLE
                line.cv.notify_all()
                return line.data

            if line.status == Status.AVAILABLE:
                return line.data
                
    def read(self, start_offset, end_offset):
        chunks = self.ids_from_offsets(start_offset, end_offset)

        for c in chunks():
            yield self.read_chunk(c)
                
