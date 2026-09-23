import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.models.trip import Trip
from raccoon_ridelog.repositories import trip_repository


async def register_trip(
    session: AsyncSession,
    motorcycle_id: uuid.UUID,
    destination_name: str,
    latitude: float,
    longitude: float,
) -> Trip:
    new_trip = Trip(
        id=uuid.uuid4(),
        motorcycle_id=motorcycle_id,
        destination_name=destination_name,
        latitude=latitude,
        longitude=longitude,
    )
    return await trip_repository.create_trip(session, new_trip)


async def get_trip(session: AsyncSession, trip_id: uuid.UUID) -> Trip | None:
    return await trip_repository.get_trip_by_id(session, trip_id)


async def list_motorcycle_trips(session: AsyncSession, motorcycle_id: uuid.UUID) -> list[Trip]:
    return await trip_repository.list_trips_by_motorcycle(session, motorcycle_id)


async def list_recent_trips(session: AsyncSession, since: datetime) -> list[Trip]:
    return await trip_repository.list_trips_since(session, since)