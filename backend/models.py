from pydantic import BaseModel

class Flight(BaseModel):
    origin: str
    destination: str