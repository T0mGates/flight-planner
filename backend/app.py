from fastapi                            import FastAPI, HTTPException, status
from backend.models                     import Flight
from backend.database                   import db
from fastapi.middleware.cors            import CORSMiddleware
from backend.sentry.error_monitoring    import init_fast_api_sentry
from backend.logging.logger             import get_logger

init_fast_api_sentry()
database    = db.Database
database.init()

app         = FastAPI()

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
def get_flights():
    return database.get_flights()

@app.post("/flights")
def create_flight(flight: Flight):
    if not database.add_flight(flight=flight):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not create flight"
        )
    
    return {"message": "Success!"}

@app.get("/flights/{flight_id}")
def get_flight_by_id(flight_id: int):
    flight = database.get_flight_by_id(id=flight_id)
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with id: {flight_id} does not exist"
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
    