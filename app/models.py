from pydantic import BaseModel, Field
from typing import Optional

class Location(BaseModel):
    city: str 
    state: str 
    lat: Optional[float] = None 
    lng: Optional[float] = None 

Class Load(BaseModel):
    id: str 
    posted_at: str 
    origin: Location 
    destination: Location 
    pickup_date: str 
    delivery_date: Optional[str] = None 
    equipment_type: Optional[str] = None 
    weight: Optional[float] = None 
    price_usd: Optional[float] = None 
    status: str = Field(default="available")
    notes: Optional[str] = None 

    