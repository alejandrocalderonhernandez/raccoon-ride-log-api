import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from raccoon_ridelog.db.session import AsyncSessionLocal
from raccoon_ridelog.models.enums import MotorcycleBrand
from raccoon_ridelog.models.motorcycle import Motorcycle
from raccoon_ridelog.models.rider import Rider
from raccoon_ridelog.models.trip import Trip
from raccoon_ridelog.repositories import (
    motorcycle_repository,
    rider_repository,
    trip_repository,
)


async def main() -> None:
    async with AsyncSessionLocal() as session:
        # --- Rider ---
        new_rider = Rider(
            id=uuid.uuid4(),
            username="smoketest01",
            email="smoketest01@raccoon.dev",
            password_hash="placeholder-not-hashed-yet",  # el hashing real llega en Fase 2
        )
        rider = await rider_repository.create_rider(session, new_rider)
        print(f"[rider] creado: {rider.id} ({rider.username})")

        fetched = await rider_repository.get_rider_by_id(session, rider.id)
        assert fetched is not None
        print(f"[rider] get_by_id OK: {fetched.username}")

        by_email = await rider_repository.get_rider_by_email(session, rider.email)
        assert by_email is not None and by_email.id == rider.id
        print("[rider] get_by_email OK")

        rider.username = "smoketest02"
        updated = await rider_repository.update_rider(session, rider)
        assert updated.username == "smoketest02"
        print(f"[rider] update OK: nuevo username = {updated.username}")

        # --- Motorcycle (depende del rider recién creado) ---
        new_motorcycle = Motorcycle(
            id=uuid.uuid4(),
            rider_id=rider.id,
            brand=MotorcycleBrand.TRIUMPH,
            model_name="Tiger Sport 800",
            engine_cc=798,
        )
        motorcycle = await motorcycle_repository.create_motorcycle(session, new_motorcycle)
        print(f"[motorcycle] creada: {motorcycle.id}")

        by_rider = await motorcycle_repository.list_motorcycles_by_rider(session, rider.id)
        assert len(by_rider) == 1 and by_rider[0].id == motorcycle.id
        print("[motorcycle] list_by_rider OK")

        # --- Trip (depende de la moto recién creada) ---
        new_trip = Trip(
            id=uuid.uuid4(),
            motorcycle_id=motorcycle.id,
            destination_name="Valle de Bravo",
            latitude=19.1947,
            longitude=-100.1339,
        )
        trip = await trip_repository.create_trip(session, new_trip)
        print(f"[trip] creado: {trip.id}, trip_date (server_default) = {trip.trip_date}")

        by_motorcycle = await trip_repository.list_trips_by_motorcycle(session, motorcycle.id)
        assert len(by_motorcycle) == 1 and by_motorcycle[0].id == trip.id
        print("[trip] list_by_motorcycle OK")

        since = datetime.now(timezone.utc) - timedelta(hours=1)
        recent = await trip_repository.list_trips_since(session, since)
        assert any(t.id == trip.id for t in recent)
        print("[trip] list_since OK")

        # --- Limpieza: borramos en orden inverso a las FKs ---
        await trip_repository.delete_trip(session, trip)
        await motorcycle_repository.delete_motorcycle(session, motorcycle)
        await rider_repository.delete_rider(session, rider)
        print("[cleanup] registros de prueba eliminados")

        gone = await rider_repository.get_rider_by_id(session, rider.id)
        assert gone is None
        print("[cleanup] verificado: rider ya no existe")

    print("\n✅ Todos los checks de repositorios pasaron.")


if __name__ == "__main__":
    asyncio.run(main())