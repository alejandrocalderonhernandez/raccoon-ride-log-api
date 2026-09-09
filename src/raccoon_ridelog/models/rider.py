import uuid

from sqlalchemy import Boolean, CheckConstraint, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from raccoon_ridelog.db.base import Base
from raccoon_ridelog.models.enums import RiderRole
from raccoon_ridelog.models.motorcycle import Motorcycle


class Rider(Base):
    __tablename__ = "rider"
    __table_args__ = (
        CheckConstraint("char_length(username) BETWEEN 5 AND 20", name="username_length")
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True);
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    role: Mapped[RiderRole] = mapped_column(default=RiderRole.STANDARD_RIDER, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
 
    motorcycles: Mapped[list["Motorcycle"]] = relationship(back_populates="rider")
    

