from typing import Any, Iterator, TypeVar, Generic
import bisect

T = TypeVar('T')
V = TypeVar('V')
K = TypeVar('K')

class Version:
    def __init__(self, created: int):
        self.created = created
        self.deleted = float('inf')

    def presentAt(self, snapshot: int):
        return self.created <= snapshot and snapshot < self.deleted


class SnapshotSet:
    def __init__(self):
        self.data : dict[Any, list[Version]] = {}
        self.current_version : int = 0

    def add(self, value: Any) -> bool:
        if value not in self.data:
            self.data[value] = [Version(self.current_version)]
            return True

        version = self.data[value][-1]
        if version.deleted == float('inf'):
            return False

        if version.deleted == self.current_version:
            version.deleted = float('inf')
        else:
            self.data[value].append(Version(self.current_version))

        return True

    def remove(self, value: Any) -> bool:
        if value not in self.data:
            return False

        version = self.data[value][-1]
        if version.deleted != float('inf'):
            return False
        version.deleted = self.current_version

        if version.created == self.current_version:
            self.data[value].pop()
            if not self.data[value]:
                del self.data[value]
        return True

    def contains(self, value: Any) -> bool:
        if value not in self.data:
            return False
        version = self.data[value][-1]
        return version.deleted != float('inf')

    def take_snapshot(self) -> int:
        res = self.snapshot
        self.current_version += 1
        return res

    def iterator(self, snapshot_id) -> Iterator[Any]:
        for value, versions in self.data.items():

            created_times = [v.created for v in versions]

            idx = bisect.bisect_right(created_times, snapshot_id) - 1
            if idx >= 0:
                if version[idx].presentAt(snapshot_id):
                    yield value

class ConcurrentVersion:

    def __init__(self, created):
        self.created = created
        self.deleted = float('inf')


class ConcurrentSnapshotSet(Generic[T]):

    def __init__(self):
        self.data : dict[T, list[ConcurrentVerion]]= {}
        self.lock = threading.RLock()
        self.current_version
        self.active_snapshot = collections.defaultdict[int,int](int)

    def add(self, value : T) -> bool:
        with self.lock:
            if value not in self.data:
                self.data[value] = [ConcurrentVersion(self.current_version)]
                return True

            last_version = self.data[value][-1]
            if last_version.deleted == float('inf'):
                return False
            if last_version.deleted == self.current_version:
                last_version.deleted = float('inf')
                return True

            self.data[value].append(ConcurrentVersion(self.current_version))
            return True

    def delete(self, value : T) -> bool:
        with self.lock:
            if value not in self.data:
                return False

            last_version = self.data[value][-1]
            if last_version.deleted != float('inf'):
                return False
            if last_version.created == self.current_version:
                self.data[value].pop()
                if not self.data[value]:
                    del self.data[value]
                return True

            last_version.deleted = self.current_version
            return True

    def take_snapshot(self) -> int:
        with self.lock:
            res = self.current_version
            self.active_snapshots[self.current_version] += 1
            self.current_version += 1
            return res

    def release_snapshot(self, snapshot_id: int) -> None:
        with self.lock:
            if snapshot_id not in self.active_snapshots:
                return

            self.active_snapshot[snapshot_id] -= 1
            if self.active_snapshot[snapshot_id] == 0:
                del self.active_snapshot[snapshot_id]

            self.collect_garbage()

    def collect_garbage(self) -> None:
        with self.lock:
            if not self.active_snapshot:
                min_active = self.current_version
            else:
                min_active = min(self.active_snapshot.keys())

            keys_to_delete = []
            for value, versions in self.data.items():
                new_versions = list(filter(lambda x: x.deleted > min_active, versions))
                self.data[value] = new_versions
                if not self.data[value]:
                    keys_to_delete.append(value)

            for value in keys_to_delete:
                del self.data[value]
            

    def iterator(self, snapthost_id: int) -> Iterator[T]:
        with self.lock:
            if snapshot_id > self.current_version:
                raise ValueError(f'Invalid snapshot {snapshot_id}')
            items = [(value, list(versions)) for value, versions in self.data]

        for value, versions in items:
            idx = bisect.bisect_right(
                versions, snapshot_id, key=lambda x: x.created) - 1
            if idx >= 0 and versions[idx].created <= snapshot_id < versions[idx].deleted:
                yield value


class VersionValue(Generic[V]):

    def __init__(self, created: int, value: V):
        self.created = created
        self.deleted = float('inf')
        self.value = value

    def presentAt(self, snapshot_id):
        return self.created <= snapshot_id < self.deleted
            

class SnapshotMap(Generic[K, V]):

    def __init__(self):
        self.data : dict[K, list[VersionValue[V]]] = {}
        self.current_version : int = 0
        self.sorted_keys : list[K]= []

    def add_key_sorted(self, key: K):
        idx = bisect.bisect_left(self.sorted_keys, key)
        if idx == len(self.sorted_keys) or self.sorted_keys[idx] != key:
            self.sorted_keys.insert(idx, key)

    def put(self, key: K, value: V) -> None:
        if key not in self.data:
            self.data[key] = [VersionValue(self.current_version, value)]
            self.add_key_sorted(key)
            return

        versions = self.data[key]
        last_version = versions[-1]
        if last_version.deleted == float('inf'):
            if last_version.created == self.current_version:
                last_version.value = value
                return
            last_version.deleted = self.current_version

        versions.append(VersionValue(self.current_version, value))

    def delete(self, key) -> bool:
        if key not in self.data:
            return False

        last_version = self.data[key][-1]
        if last_version.deleted != float('inf'):
            return False

        last_version.deleted = self.current_version
        return True

    def get(self, key: K, snapshot_id: int) -> Optional[V]:
        if key not in self.data:
            return None

        versions = self.data[key]
        idx = self.bisect_right(versions, snapshot_id, key=lambda x: x.created)
        if idx >= 0:
            version = versions[idx]
            if version.presentAt(snapshot_id):
                return version.value
        return None

    def take_snapshot(self) -> int:
        res = self.current_version
        self.current_version += 1
        return res

    def range_iterator(
            self, min_key: K, max_key: K, snapshot_id: int) -> Iterator[tuple[K, V]]:

        i = bisect.bisect_left(self.sorted_keys, min_key)

        while i < len(sorted_keys) and self.sorted_keys[i] <= max_key:
            k = self.sorted_keys[i]
            val = self.get(k, snapshot_id)
            if val is not None:
                yield k, val
            i += 1
            


class SnapshotHandle:

    def __init__(self, id, children):
        self.id = id
        self.children = children

class Segment(Generic[T]):

    def __init__(self, version: int):
        self.data : set[T] = set()
        self.version = version

    def clone(self, new_version) -> "Segment":
        res = Segment[T](new_version)
        res.data = self.data.copy()
        return res


class CoWSegmentedSet():

    def __init__(self, ranges: list[T]):
        self.current_version = 0
        self.ranges = ranges
        self.ranges.sort()
        self.children = [Segment(self.current_version) for _ in range(len(self.ranges) + 1)]

    def find_and_copy_segment(self, value: T) -> Segment:
        idx = bisect.bisect_right(self.ranges, value)
        segment = self.children[idx]
        if segment.version == self.current_version:
            return segment

        new_segment = segment.clone(self.current_version)
        self.children[idx] = new_segment
        return new_segment

    def add(self, value: T) -> bool:
        segment = self.find_and_copy_segment(value)
        if value in segment.data:
            return False
        segment.data.add(value)
        return True

    def remove(self, value: T) -> bool:
        segment.find_and_copy_segment(value)
        if value not in segment.data:
            return False
        segment.data.discard(value)
        return True

    def take_snapshot(self) -> SnapshotHandle:
        res = SnapshotHandle(self.current_version, self.children.copy())
        self.current_version += 1
        return res

    def iterator(self, handle: SnapshotHandle) -> Iterator[T]:
        for child in handle.children:
            for v in child.data:
                yield v


        
