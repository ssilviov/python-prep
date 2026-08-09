import bisect
import heapq

class Job:

    def __init__(self, id: int, start: int, end: int, units: int):
        self.id = id
        self.start = start
        self.end = end
        self.units = units

class ResourceTracker:

    def __init__(self):
       self.events: dict[int, int] = {}
       self.jobs: dict[int, Job] = {}
       self.timeline: list[int] = []

    def record_event(self, time, units):
        new_val = self.events.get(time, 0) + units
        if new_val == 0:
            del self.events[time]
            idx = bisect.bisect_left(self.timeline, time)
            if idx < len(self.timeline) and self.timeline[idx] == time:
                self.timeline.pop(idx)
        else:
            if time not in self.events:
                idx = bisect.bisect_left(self.timeline, time)
                self.timeline.insert(idx, time)
            self.events[time] = new_val

    def add_job(self, job_id: str, start_time: int, end_time: int, units: int) -> None:
        if start_time >= end_time or units < 0:
           return
        if job_id in self.jobs:
            self.cancel_job(job_id)

        job = Job(job_id, start_time, end_time, units)
        self.jobs[job_id] = job
        self.record_event(start_time, units)
        self.record_event(end_time, -units)

    def cancel_job(self, job_id: str) -> None:
        """Cancels an active or future job by ID."""
        if job_id not in self.jobs:
            return
        job = self.jobs[job_id]
        self.record_event(job.start, -job.units)
        self.record_event(job.end, job.units)
        del self.jobs[job_id]

    def get_peak_occupancy(self, query_start: int, query_end: int) -> int:
        peak = -1
        current = 0
        for t in self.timeline:
            if t >= query_end:
                break

            units = self.events[t]

            if t >= query_start:
                if peak == -1:
                    peak = current
                current += units
                peak = max(peak, current)
            else:
                current += units
        if peak == -1 and current > 0:
            peak = current

        return max(0, peak)

    def get_total_active_duration(self, min_units: int) -> int:
        """Returns the total cumulative time across history where total utilization

        was >= min_units.
        """
        if not self.timeline:
            return 0

        current = 0
        counter = 0
        prev_time = self.timeline[0]
        for t in self.timeline:
            elapsed = t - prev_time
            if current >= min_units:
                counter += elapsed
            current += self.events[t]
            prev_time = t

        return counter
