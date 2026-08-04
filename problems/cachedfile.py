import collections
import threading
import enum

class StorageClient:

    def __init__(self, filename: str, size: int):
        self.filename = filename
        self.size = size

    def get_size(self) -> int:
        return self.size

    def readBlock(self, offset: int, size: int, buffer: bytearray):
        for i in range(size):
            buffer[i] = i % 256

class BlockStatus(enum.Enum):
    EMPTY = 0
    PENDING = 1
    READY = 2
    ERROR = 3


class CacheBlock:

    BLOCK_SIZE = 1024 # just for our exercise let's do 1kb

    def __init__(self, physical_index):
        self.valid_bytes = 0
        self.buffer = bytearray(CacheBlock.BLOCK_SIZE)
        self.block_num = -1
        self.physical_idx = physical_index
        self.logical_idx = -1
        self.lock = threading.Lock()
        self.cond = threading.Condition(self.lock)
        self.reader_count = 0
        self.status = BlockStatus.EMPTY


class CachedFile:
    
    def __init__(self, client: StorageClient, max_cache_size: int):
        self.client = client
        self.max_cache_size = max_cache_size

        # TODO: check that max_cache_size is multiple of BLOCK_SIZE
        if max_cache_size % CacheBlock.BLOCK_SIZE != 0:
            raise ValueError(
                f'max_cache_size {max_cache_size} should be a'
                ' multiple of {self.BLOCK_SIZE}')
        self.blocks_num = max_cache_size // CacheBlock.BLOCK_SIZE

        self.cache = [CacheBlock(i) for i in range(self.blocks_num)]
        self.lock = threading.Lock()
        self.block_map = collections.OrderedDict()
        self.free_slots = list(range(self.blocks_num))

    def get_block_and_pin(self, block_num: int) -> tuple[int, bool]:

        with self.lock:

            # block is already in map
            if block_num in self.block_map:
                self.block_map.move_to_end(block_num, last=True)

                idx = self.block_map[block_num]
                block = self.cache[idx]
                with block.lock:
                    block.reader_count += 1 # pin
                return idx, False # already being fetched.

            idx = -1
            # Find a new block
            if len(self.block_map) == self.blocks_num:
                # no empty slots.
                key_to_evict = -1
                for key, old_idx in self.block_map.items():
                    block = self.cache[old_idx]
                    with block.lock:
                        if block.reader_count == 0:
                            key_to_evict = key
                            idx = old_idx
                            break
                if key_to_evict == -1:
                    raise RuntimeError("All slots are being read.")
                self.block_map.pop(key_to_evict)
            else:
                idx = self.free_slots.pop()

            block = self.cache[idx]
            with block.lock:
                block.reader_count = 1
                block.status = BlockStatus.PENDING
                block.valid_bytes = 0
            self.block_map[block_num] = idx
            
            return idx, True

    def read(self, offset: int, size: int, buffer: bytearray) -> int:

        # validate input, that size and offset are valid.
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

            idx, needs_fetch = self.get_block_and_pin(block_idx)
            block = self.cache[idx]

            try:
                if needs_fetch:
                    offset_in_file = block_idx * CacheBlock.BLOCK_SIZE
                    fetch_bytes = min(file_size - offset_in_file, CacheBlock.BLOCK_SIZE)
                    try:
                        self.client.readBlock(offset_in_file, fetch_bytes, block.buffer)

                        with block.lock:
                            block.valid_bytes = fetch_bytes
                            block.status = BlockStatus.READY
                            block.cond.notify_all()

                    except Exception as e:
                        with block.lock:
                            block.valid_bytes = 0
                            block.status = BlockStatus.ERROR
                            block.cond.notify_all()

                        with self.lock:
                            if block_idx in self.block_map and self.block_map[block_idx] == idx:
                                self.block_map.pop(block_idx)
                                self.free_slots.append(block_idx)
                        raise IOError(f"Failed fetch of block {block_idx}") from e

                else:
                    with block.lock:
                        while block.status == BlockStatus.PENDING:
                            block.cond.wait()

                        if block.status == BlockStatus.ERROR:
                            raise IOError(f"Failed fetch of block {block_idx}")
                        

                bytes_to_read = min(block.valid_bytes - block_offset, bytes_left)
                if bytes_to_read <= 0:
                    break

                buffer[buffer_idx : buffer_idx + bytes_to_read] = (
                    block.buffer[block_offset : block_offset + bytes_to_read])

                with self.lock:
                    if block_idx in self.block_map:
                        self.block_map.move_to_end(block_idx)
            finally:
                # always unpin
                with block.lock:
                    block.reader_count -= 1

            buffer_idx += bytes_to_read
            bytes_left -= bytes_to_read
            current_offset += bytes_to_read

        return buffer_idx


