import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from raccoon_ridelog.models.enums import RiderRole


class RiderCreate(BaseModel):
    
    username: str = Field(min_length=5, max_length=20, pattern=r"^[a-zA-Z0-9]+$")
    email: EmailStr
    password: str = Field(min_length=8)
    
    @field_validator("password")
    @classmethod
    def password_must_be_strong(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError("la contraseña debe tener al menos una mayúscula")
        if not any(c.isdigit() for c in value):
            raise ValueError("la contraseña debe tener al menos un número")
        return value


class RiderUpdate(BaseModel):
    username: str = Field(min_length=5, max_length=20, pattern=r"^[a-zA-Z0-9]+$")


class RiderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    email: EmailStr
    role: RiderRole
    is_active: bool