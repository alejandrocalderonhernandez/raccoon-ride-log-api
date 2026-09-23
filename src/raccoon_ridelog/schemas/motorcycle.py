import uuid

from pydantic import BaseModel, ConfigDict, Field

from raccoon_ridelog.models.enums import MotorcycleBrand


class MotorcycleCreate(BaseModel):
    brand: MotorcycleBrand
    model_name: str = Field(min_length=2, max_length=50)
    engine_cc: int = Field(gt=125, lt=2500)


class MotorcycleUpdate(BaseModel):
    model_name: str = Field(min_length=2, max_length=50)
    engine_cc: int = Field(gt=125, lt=2500)


class MotorcycleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    rider_id: uuid.UUID
    brand: MotorcycleBrand
    model_name: str
    engine_cc: int