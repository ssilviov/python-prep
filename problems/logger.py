import threading
import enum
import time
import sys


class Severity(enum.Enum):
    ERROR = enum.auto()
    WARNING = enum.auto()
    INFO = enum.auto()


class Buffer:
    def __init__(self, capacity):
        self.capacity = capacity
        self.data = []

    def is_full(self):
        return len(self.data) >= self.capacity

    def append(self, item):
        self.data.append(item)

    def reset(self):
        self.data.clear()

    def __iter__(self):
        return iter(self.data)

    def __len__(self):
        return len(self.data)


class Logger:
    def __init__(self, buffer_len: int, timeout: float):
        self.buffer_len = buffer_len
        self.timeout = timeout

        self.active_buffer = Buffer(buffer_len)
        self.flush_buffer_ref = Buffer(buffer_len)

        self.is_running = False
        self.lock = threading.Lock()
        self.has_data_cond = threading.Condition(self.lock)
        self.slot_avail_cond = threading.Condition(self.lock)

        self.write_thread = threading.Thread(target=self._flush_buffer_loop)

    def log(self, severity: Severity, msg: str):
        with self.lock:
            # Backpressure: Block if active buffer is full
            while self.active_buffer.is_full() and self.is_running:
                self.slot_avail_cond.wait()

            if not self.is_running:
                return

            self.active_buffer.append((severity, msg))

            if self.active_buffer.is_full():
                self.has_data_cond.notify()

    def _flush_buffer_loop(self):
        while True:
            with self.lock:
                start_time = time.time()
                
                while len(self.active_buffer) == 0 and self.is_running:
                    elapsed = time.time() - start_time
                    remaining = self.timeout - elapsed
                    if remaining <= 0:
                        break
                    self.has_data_cond.wait(timeout=remaining)

                if not self.is_running and len(self.active_buffer) == 0:
                    break

                # Pointer Swap
                self.active_buffer, self.flush_buffer_ref = (
                    self.flush_buffer_ref,
                    self.active_buffer,
                )

            # --- FLUSH OUTSIDE LOCK ---
            if len(self.flush_buffer_ref) > 0:
                try:
                    for sev, msg in self.flush_buffer_ref:
                        self.write(f"[{sev.name}] {msg}")
                    self.fsync()
                except Exception as e:
                    sys.stderr.write(f"Flush Error: {e}\n")
                finally:
                    with self.lock:
                        self.flush_buffer_ref.reset()
                        self.slot_avail_cond.notify_all() # Unblock producers
