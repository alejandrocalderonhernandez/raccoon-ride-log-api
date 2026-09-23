import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.models.rider import Rider
from raccoon_ridelog.repositories import rider_repository


async def register_rider(session: AsyncSession, username: str, email: str, 
                         password_hash: str) -> Rider:
    new_rider = Rider(
        id=uuid.uuid4(),
        username=username,
        email=email,
        password_hash=password_hash
    )
    
    return await rider_repository.create_rider(session, new_rider)

async def get_rider(session: AsyncSession, rider_id: uuid.UUID) -> Rider:
    return await rider_repository.get_rider_by_id(session, rider_id)

async def list_all_riders(session: AsyncSession) -> list[Rider]:
    return await rider_repository.list_riders(session)

async def rename_rider(session: AsyncSession, rider_id: uuid.UUID, new_username: str
                       ) -> Rider | None:
    rider = await rider_repository.get_rider_by_id(session, rider_id)
    if rider is None:
        return None
    
    rider.username = new_username
    return await rider_repository.update_rider(session, rider)

async def delete_rider(session: AsyncSession, rider_id: uuid.UUID) -> bool:
    rider = await rider_repository.get_rider_by_id(session, rider_id)
    if rider is None:
        return False
    
    await rider_repository.delete_rider(session, rider)
    return True