from fastapi    import FastAPI, HTTPException, status
from backend.models     import Flight
from backend.database   import db

database    = db.Database
database.init()

app         = FastAPI()


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