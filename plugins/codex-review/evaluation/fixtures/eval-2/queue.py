import threading
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class Job:
    id: int
    status: str  # "pending", "running", "completed", "failed"
    payload: dict
    result: Optional[str] = None


class JobQueue:
    def __init__(self):
        self.jobs: list[Job] = []
        self.lock = threading.Lock()

    def add_job(self, payload: dict) -> int:
        job = Job(id=len(self.jobs), status="pending", payload=payload)
        self.jobs.append(job)
        return job.id

    def claim_next_job(self) -> Optional[Job]:
        """Claim the next pending job for processing."""
        # Find a pending job
        for job in self.jobs:
            if job.status == "pending":
                # Mark it as running
                job.status = "running"
                return job
        return None

    def complete_job(self, job_id: int, result: str):
        job = self.jobs[job_id]
        job.status = "completed"
        job.result = result

    def fail_job(self, job_id: int, error: str):
        job = self.jobs[job_id]
        job.status = "failed"
        job.result = f"Error: {error}"


def worker(queue: JobQueue, worker_id: int):
    while True:
        job = queue.claim_next_job()
        if job is None:
            time.sleep(0.1)
            continue

        print(f"Worker {worker_id} processing job {job.id}")
        try:
            # Simulate work
            time.sleep(0.5)
            result = f"Processed: {job.payload}"
            queue.complete_job(job.id, result)
        except Exception as e:
            queue.fail_job(job.id, str(e))


if __name__ == "__main__":
    queue = JobQueue()

    # Add some jobs
    for i in range(10):
        queue.add_job({"task": f"task_{i}"})

    # Start workers
    workers = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(queue, i), daemon=True)
        t.start()
        workers.append(t)

    time.sleep(5)
    for job in queue.jobs:
        print(f"Job {job.id}: {job.status} - {job.result}")
