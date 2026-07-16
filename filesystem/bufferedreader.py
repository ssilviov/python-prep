"""A Buffered reader around a slow filesystem."""
import collections

class File:
    """Simulate a file that can be read in blocks."""

    def __init__(self, name: str, size: int):
        self.name = name
        self.size = size

    def read(self, offset: int, num_bytes: int) -> bytes:
        if offset > self.size:
            return b""

        to_return = min(self.size - offset, num_bytes)
        return bytearray(x % 256 for x in range(to_return))


class BufferedReader:
    """Buffer the reads with an LRU cache with blocks."""

    BLOCK_SIZE = 100

    def __init__(self, file: File, max_blocks: int):
        self.cache = collections.OrderedDict()
        self.max_blocks = max_blocks
        self.file = file

    def get_block(self, block: int) -> bytes:
        if block in self.cache:
            self.cache.move_to_end(block)
            return self.cache[block]
        
        if len(self.cache) >= self.max_blocks:
            self.cache.popitem(last=False)

        self.cache[block] = self.file.read(block * BLOCK_SIZE, BLOCK_SIZE)
        return self.cache[block]

    def read(self, num_bytes: int, offset: int=0) -> bytes:
        if offset < 0:
            raise ValueError(f"cannot read from negative offset {offset}")
        if num_bytes < 0:
            raise ValueError(f"cannot read negative bytes {offset}")

        if offset >= self.file.size or num_bytes == 0:
            return b""


        bytes_to_read = min(self.file.size - offset, num_bytes)
        res = bytearray()
        current_offset = offset

        while len(res) < bytes_to_read:
            block_id = current_offset // self.BLOCK_SIZE
            block_of = current_offset % self.BLOCK_SIZE

            block = self.get_block(block_id)
            if not block:
                break

            bytes_available = len(block) - block_of
            bytes_needed = bytes_to_read - len(res)
            bytes_to_copy = min(bytes_available, bytes_needed)

            res.extend(block[block_of: block_of + bytes_to_copy])
            current_offset += bytes_to_copy

        return bytes(res)

