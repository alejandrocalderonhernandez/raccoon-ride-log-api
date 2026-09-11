import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.models.rider import Rider


async def create_rider(session: AsyncSession, rider: Rider) -> Rider:
    session.add(rider)
    await session.commit()
    await session.refresh(rider)
    return rider

async def get_rider_by_id(session: AsyncSession, rider_id: uuid.UUID) -> Rider | None:
    return await session.get(Rider, rider_id)

async def get_rider_by_email(session: AsyncSession, email: str) -> Rider | None:
    result = await session.execute(select(Rider).where(Rider.email == email))
    return result.scalar_one_or_none

async def list_riders(session: AsyncSession) -> list[Rider]:
    result = await session.execute(select(Rider))
    return list(result.scalars().all)

async def update_rider(session: AsyncSession, rider: Rider) -> Rider:
   await session.commit()
   await session.refresh(rider)
   return rider

async def delete_rider(session: AsyncSession,  rider: Rider) -> None:
    await session.delete(rider)
    await session.commit()