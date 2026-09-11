import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.models.motorcycle import Motorcycle


async def create_motorcycle(session: AsyncSession, motorcycle: Motorcycle) -> Motorcycle:
    session.add(motorcycle)
    await session.commit()
    await session.refresh(motorcycle)
    return motorcycle


async def get_motorcycle_by_id(session: AsyncSession, motorcycle_id: uuid.UUID) -> Motorcycle | None:
    return await session.get(Motorcycle, motorcycle_id)


async def list_motorcycles_by_rider(session: AsyncSession, rider_id: uuid.UUID) -> list[Motorcycle]:
    result = await session.execute(
        select(Motorcycle).where(Motorcycle.rider_id == rider_id)
    )
    return list(result.scalars().all())


async def update_motorcycle(session: AsyncSession, motorcycle: Motorcycle) -> Motorcycle:
    await session.commit()
    await session.refresh(motorcycle)
    return motorcycle


async def delete_motorcycle(session: AsyncSession, motorcycle: Motorcycle) -> None:
    await session.delete(motorcycle)
    await session.commit()