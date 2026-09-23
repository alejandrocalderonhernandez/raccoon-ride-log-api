import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TripCreate(BaseModel):
    destination_name: str = Field(max_length=100)
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)


class TripRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    motorcycle_id: uuid.UUID
    destination_name: str
    latitude: float
    longitude: float
    weather_condition: str | None
    temperature_celsius: float | None
    trip_date: datetime