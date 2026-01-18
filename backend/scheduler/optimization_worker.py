import asyncio
from concurrent.futures import ThreadPoolExecutor

from backend.scheduler.work_queue import queue, job_status
from backend.scheduler.resolver import CostDriven4DResolver
from backend.scheduler.data_loader import generate_flight_schedule

executor = ThreadPoolExecutor(max_workers=2)

def run_optimizer_sync(job_id: str, payload: dict):
    """
    This runs in a separate thread.
    MUST be synchronous.
    """
    return CostDriven4DResolver().resolve(
        generate_flight_schedule("canadian_flights_1000.json"),
        iterations=10,
        status=job_status[job_id]
    )

async def optimizer_worker():
    # Use the loop associated with this specific thread
    loop = asyncio.get_event_loop()

    while True:
        # This will wait here until a job enters the queue
        job_id, payload = await queue.get()

        try:
            job_status[job_id]["status"] = "running"

            # Offload the math to the ThreadPoolExecutor
            result = await loop.run_in_executor(
                executor,
                run_optimizer_sync,
                job_id,
                payload,
            )

            job_status[job_id]["status"] = "completed"
            job_status[job_id].update({"result": result.to_dict(orient="records")})

        except Exception as e:
            job_status[job_id]["status"] = "failed"
            job_status[job_id]["error"] = str(e)
        finally:
            queue.task_done()