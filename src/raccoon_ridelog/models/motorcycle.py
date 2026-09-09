import uuid

from sqlalchemy import CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from raccoon_ridelog.db.base import Base
from raccoon_ridelog.models.enums import MotorcycleBrand
from raccoon_ridelog.models.rider import Rider
from raccoon_ridelog.models.trip import Trip


class Motorcycle(Base):
    __tablename__ = "motorcycle"
    __table_args__ = (
        CheckConstraint("char_length(model_name) BETWEEN 2 AND 50", name="model_name_length"),
        CheckConstraint("engine_cc > 125 AND engine_cc < 2500", name="engine_cc_range"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    rider_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rider.id", ondelete="CASCADE"), nullable=False
    )
    brand: Mapped[MotorcycleBrand] = mapped_column(nullable=False)
    model_name: Mapped[str] = mapped_column(String(50), nullable=False)
    engine_cc: Mapped[int] = mapped_column(Integer, nullable=False)

    rider: Mapped["Rider"] = relationship(back_populates="motorcycles")
    trips: Mapped[list["Trip"]] = relationship(back_populates="motorcycle")