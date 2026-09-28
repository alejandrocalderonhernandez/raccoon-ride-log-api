import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.core.security import hash_password
from raccoon_ridelog.models.rider import Rider
from raccoon_ridelog.repositories import rider_repository
from raccoon_ridelog.schemas.rider import RiderCreate, RiderUpdate  # NUEVO import


async def register_rider(session: AsyncSession, data: RiderCreate) -> Rider:
    new_rider = Rider(
        id=uuid.uuid4(),
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    return await rider_repository.create_rider(session, new_rider)

async def get_rider(session: AsyncSession, rider_id: uuid.UUID) -> Rider:
    return await rider_repository.get_rider_by_id(session, rider_id)

async def list_all_riders(session: AsyncSession) -> list[Rider]:
    return await rider_repository.list_riders(session)

async def rename_rider(
    session: AsyncSession, rider_id: uuid.UUID, data: RiderUpdate
) -> Rider | None:
    rider = await rider_repository.get_rider_by_id(session, rider_id)
    if rider is None:
        return None
    rider.username = data.username
    return await rider_repository.update_rider(session, rider)

async def delete_rider(session: AsyncSession, rider_id: uuid.UUID) -> bool:
    rider = await rider_repository.get_rider_by_id(session, rider_id)
    if rider is None:
        return False
    
    await rider_repository.delete_rider(session, rider)
    return True