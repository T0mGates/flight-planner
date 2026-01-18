import asyncio
import uuid
from fastapi                            import FastAPI, HTTPException, status
from datetime                           import datetime
from typing                             import Optional

import pandas as pd
from backend.models                     import Flight, FlightFilters
from backend.database                   import db
from fastapi.middleware.cors            import CORSMiddleware
from backend.sentry.error_monitoring    import init_fast_api_sentry
from backend.logging.logger             import get_logger
from backend.scheduler.optimization_worker import optimizer_worker
from backend.scheduler.work_queue       import queue, job_status
from backend.scheduler.resolver       import CostDriven4DResolver
from contextlib import asynccontextmanager


init_fast_api_sentry()
database    = db.Database
database.init()

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(optimizer_worker())
    yield

app         = FastAPI(lifespan=lifespan)


# Setup logger
log = get_logger()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,         # Allows the specified origins
    allow_credentials=True,        # Allows cookies/authorization headers to be sent
    allow_methods=["*"],           # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],           # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/flights")
async def get_flights(
    # These are (optional) query params
    start:          Optional[str] = None, 
    end:            Optional[str] = None,
    origin:         Optional[str] = None,
    destination:    Optional[str] = None
):
    start       = start.strip()                 if start        else None
    end         = end.strip()                   if end          else None
    origin      = origin.strip().upper()        if origin       else None
    destination = destination.strip().upper()   if destination  else None

    filters     = FlightFilters(start=start, end=end, origin=origin, destination=destination)
    log.debug(f"Received filters: start = {start}, end = {end}, origin = {origin}, destination = {destination}")
    return database.get_flights(filters=filters)

@app.post("/flights")
def create_flight(flight: Flight):
    if not database.add_flight(flight=flight):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create flight"
        )
    
    return {"message": "Success!"}

@app.get("/flights/{flight_acid}")
def get_flight_by_acid(flight_acid: str):
    flight_acid = flight_acid.upper()
    flight = database.get_flight_by_acid(acid=flight_acid)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with acid: {flight_acid} does not exist"
        )
    
    return {"flight": flight}

@app.get("/airports")
def get_all_airport_details():
    return database.get_all_airports_details()

@app.get("/airports/{iata_code}")
def get_airport_details_by_iata_code(iata_code: str):
    airport_details = database.get_airport_details(iata_code=iata_code)

    if not airport_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport with IATA code: {iata_code} does not exist"
        )
    
    return airport_details
    
@app.get("/start_worker")
async def optimize():
    job_id = str(uuid.uuid4())

    job_status[job_id] = {
        "status": "queued",
        "progress": 0,
        "result": None,
    }

    await queue.put((job_id, None))

    return {"job_id": job_id}

@app.get("/job_status/{job_id}")
def get_job_status(job_id: str):
    job = job_status.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id: {job_id} does not exist"
        )
        
    # Dont show job['result']
    job_copy = job.copy()
    if job_copy['status'] == 'completed':
        job_copy['result'] = 'Result available for download.'
    
    return job_copy

@app.get("/job_status/{job_id}/flight_results")
def get_job_flight_results(job_id: str):
    job = job_status.get(job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with id: {job_id} does not exist"
        )
    
    if job['status'] != 'completed':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Job with id: {job_id} is not yet completed"
        )
    
    return job['result']