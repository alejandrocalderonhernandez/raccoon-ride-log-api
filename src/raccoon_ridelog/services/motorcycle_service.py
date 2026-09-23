import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from raccoon_ridelog.models.enums import MotorcycleBrand
from raccoon_ridelog.models.motorcycle import Motorcycle
from raccoon_ridelog.repositories import motorcycle_repository


async def register_motorcycle(
    session: AsyncSession,
    rider_id: uuid.UUID,
    brand: MotorcycleBrand,
    model_name: str,
    engine_cc: int,
) -> Motorcycle:
    new_motorcycle = Motorcycle(
        id=uuid.uuid4(),
        rider_id=rider_id,
        brand=brand,
        model_name=model_name,
        engine_cc=engine_cc,
    )
    return await motorcycle_repository.create_motorcycle(session, new_motorcycle)


async def get_motorcycle(session: AsyncSession, motorcycle_id: uuid.UUID) -> Motorcycle | None:
    return await motorcycle_repository.get_motorcycle_by_id(session, motorcycle_id)


async def list_rider_garage(session: AsyncSession, rider_id: uuid.UUID) -> list[Motorcycle]:
    return await motorcycle_repository.list_motorcycles_by_rider(session, rider_id)


async def remove_motorcycle(session: AsyncSession, motorcycle_id: uuid.UUID) -> bool:
    motorcycle = await motorcycle_repository.get_motorcycle_by_id(session, motorcycle_id)
    if motorcycle is None:
        return False
    await motorcycle_repository.delete_motorcycle(session, motorcycle)
    return True