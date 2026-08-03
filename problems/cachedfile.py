import collections
import threading

class StorageClient:

    def __init__(self, filename: str, size: int):
        self.filename = filename
        self.size = size

    def get_size(self) -> int:
        return self.size

    def readBlock(self, offset: int, size: int, buffer: bytearray):
        for i in range(size):
            buffer[i] = i % 256

class CacheBlock:

    BLOCK_SIZE = 1024 # just for our exercise let's do 1kb

    def __init__(self):
        self.size = 0
        self.buffer = bytearray(self.BLOCK_SIZE)
        self.block_num = -1

    def reset(self):
        self.size = 0

    def read(self, client: StorageClient, block_num: int):
        offset = block_num * self.BLOCK_SIZE
        bytes_to_read = min(self.BLOCK_SIZE, client.get_size() - offset)
        client.readBlock(offset, bytes_to_read, self.buffer)
        self.size = bytes_to_read
        self.block_num = block_num


class CachedFile:
    
    EMPTY = 0
    PENDING = 1
    READY = 2

    def __init__(self, client: StorageClient, max_cache_size: int):
        self.client = client
        self.max_cache_size = max_cache_size

        # TODO: check that max_cache_size is multiple of BLOCK_SIZE
        if max_cache_size % CacheBlock.BLOCK_SIZE != 0:
            raise ValueError(
                f'max_cache_size {max_cache_size} should be a'
                ' multiple of {self.BLOCK_SIZE}')
        self.blocks_num = max_cache_size // CacheBlock.BLOCK_SIZE

        self.cache = [CacheBlock() for i in range(self.blocks_num)]
        self.lock = threading.Lock()
        self.block_map = collections.OrderedDict()

        self.block_lock = [threading.Lock() for i in range(self.blocks_num)]
        self.block_cond = [threading.Condition(l) for l in self.block_lock]
        self.block_status = [self.EMPTY for i in range.blocks_num]
        self.reader_counts = [0] * range.blocks_num

        self.free_slots = [i for i in range(self.blocks_num)]

    def _find_idx_and_pin(self, block_num: int) -> tuple(int, bool):
        idx = -1

        with self.lock:

            # block is already in map
            if block_num in self.block_map:
                self.block_map.move_to_end(block_num, last=True)

                idx = self.block_map[block_num]
                self.reader_counts[idx] += 1 # pin
                return idx, False # already being fetched.

            # Find a new block
            if len(self.block_map) == self.blocks_num:
                # no empty slots.
                key = -1
                for key, old_idx in self.block_map.items():
                    if self.reader_counts[cache_idx] == 0:
                        idx = old_idx
                        key = block_idx
                        break
                if key == -1:
                    raise RuntimeError("All slots are being read.")
                self.block_map.pop(key)
            else:
                idx = self.free_slots.pop()
            self.reader_counts[idx] = 1
            self.block_map[block_num] = idx
            with self.block_lock[idx]:
                self.block_status[idx] = self.PENDING
            return idx, True

    def get_block(self, block_num: int) -> tuple[CacheBlock, int]:
        idx, need_fetch = self._find_idx_and_pin(block_num)

        if not need_fetch:
            with self.block_lock[idx]:
                while self.block_status != self.READY:
                    self.block_cond[idx].wait()
            return self.cache[idx], idx

        block = self.cache[idx]
        block.read(self.client, block_num)
        with self.block_lock[idx]:
            self.block_status[idx] = self.READY
            self.block_cond[idx].notify_all()

        return block, idx

    def read(self, offset: int, size: int, buffer: bytearray) -> int:

        file_size = self.client.get_size()

        if size == 0 or offset == file_size:
            return 0

        if offset > file_size:
            raise ValueError(
                f"offset {offset} is greater than file size {file_size}")

        if offset + size > file_size:
            size = file_size - offset

        bytes_left = size
        current_offset = offset
        buffer_idx = 0

        while bytes_left > 0:
            block_idx = current_offset // CacheBlock.BLOCK_SIZE
            block_offset = current_offset % CacheBlock.BLOCK_SIZE

            block, idx = self.get_block(block_idx)

            bytes_to_read = min(block.size - block_offset, bytes_left)
            if bytes_to_read <= 0:
                break
            
            try:
                buffer[buffer_idx : buffer_idx + bytes_to_read] = (
                    block.buffer[block_offset : block_offset + bytes_to_read])

            finally:
                with self.lock:
                    self.reader_counts[idx] -= 1
            buffer_idx += bytes_to_read
            bytes_left -= bytes_to_read
            current_offset += bytes_to_read

        return buffer_idx


