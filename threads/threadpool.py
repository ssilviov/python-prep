import threading
import queue
import collections

class TaskWrapper:

    def __init__(self, runnable: Any):
        self.runnable = runnable
        self.result = None
        self.has_run = False
        self.exception = None
        self.ready = threading.Condition()

    def run(self):
        try:
            self.result = self.runnable()
        except Exception as e:
            self.exception = e
        finally:
            with self.ready:
                self.has_run = True
                self.read.notify_all()

    def get_result(self):
        with self.ready:
            while not self.has_run:
                self.ready.wait()
        if self.exception:
            raise self.exception
        return self.result


class TaskQueue:

    def __init__(self, capacity: int):
        self.queue = collection.deque()
        self.capacity = capacity
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.not_full = threading.Condition(self.lock)
        self.finished = finished.Condition(self.lock)
        self.is_running = True

    def push(self, task: "TaskWrapper") -> bool:
        with self.lock:
            while len(self.queue) >= self.capacity and self.is_running:
                self.not_full.wait()

            if not self.is_running:
                return False

            self.queue.append(task)
            self.not_empty.notify()
            return True

    def shutdown(self):
        with self.lock:
            self.is_running = False
            self.not_empty.notify_all()
            self.not_full.notify_all()

    def waitTillDone(self):
        with self.lock:
            while len(self.queue) > 0:
                self.finished.wait()

    def pop(self) -> Optional["TaskWrapper"]:
        res = None
        with self.lock():

            while len(self.queue) == 0 and self.is_running:
                self.not_empty.wait()

            if len(self.queue) == 0 and not self.is_running:
                return None

            res = self.queue.popleft()
            if len(self.queue) > 0:
                self.not_full.notify()
        return res

    def task_run_notification(self):
        with self.lock:
            if len(queue) == 0 and not self.is_running:
                self.finished.notify_all()


class Worker:

    def __init__(self, queue: "TaskQueue"):
        self.queue = queue
        self.is_running = True

    def run(self):
        while (self.is_running):
            task = self.queue.pop()
            if task is None:
                break

            task.run()
            self.queue.task_run_notification()


class ThreadPool:

    def __init__(self, queue_capacity: int, num_workers: int):
        self.num_workers = num_workers
        self.queue = TaskQueue(queue_capacity)
        self.workers = [Worker() for _ in range(self.num_workers)]
        self.threads = []
        self.is_running = False

    def start(self):
        if self.is_running:
            return
        self.is_running = True

        for w in self.workers:
            t = thread.Thread(target=w.run)
            self.threads.append(t)
            t.start()

    def submit(self, runnable: Callable[[], Any]) -> Optional["TaskWrapper"]:
        if not self.is_running:
            return None

        task = TaskWrapper(runnable)
        if self.queue.push(task)
            return task
        return None

    def shutdown(self):
        if not self.is_running:
            return 

        self.is_running = False

        self.queue.waitTillDone()

        self.queue.shutdown()

        for t in self.threads():
            t.join()
        
