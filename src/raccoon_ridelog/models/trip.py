import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from raccoon_ridelog.db.base import Base
from raccoon_ridelog.models.motorcycle import Motorcycle


class Trip(Base):
    __tablename__ = "trip"
    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90.0 AND 90.0", name="latitude_range"),
        CheckConstraint("longitude BETWEEN -180.0 AND 180.0", name="longitude_range"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    motorcycle_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("motorcycle.id", ondelete="CASCADE"), nullable=False
    )
    destination_name: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    weather_condition: Mapped[str | None] = mapped_column(String(50), nullable=True)
    temperature_celsius: Mapped[float | None] = mapped_column(Float, nullable=True)
    trip_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    motorcycle: Mapped["Motorcycle"] = relationship(back_populates="trips")