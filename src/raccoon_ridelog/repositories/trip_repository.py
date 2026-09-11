import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.models.trip import Trip


async def create_trip(session: AsyncSession, trip: Trip) -> Trip:
    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip


async def get_trip_by_id(session: AsyncSession, trip_id: uuid.UUID) -> Trip | None:
    return await session.get(Trip, trip_id)


async def list_trips_by_motorcycle(session: AsyncSession, motorcycle_id: uuid.UUID) -> list[Trip]:
    result = await session.execute(
        select(Trip).where(Trip.motorcycle_id == motorcycle_id)
    )
    return list(result.scalars().all())


async def list_trips_since(session: AsyncSession, since: datetime) -> list[Trip]:
    result = await session.execute(select(Trip).where(Trip.trip_date >= since))
    return list(result.scalars().all())


async def update_trip(session: AsyncSession, trip: Trip) -> Trip:
    await session.commit()
    await session.refresh(trip)
    return trip


async def delete_trip(session: AsyncSession, trip: Trip) -> None:
    await session.delete(trip)
    await session.commit()