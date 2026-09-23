import asyncio
from datetime import datetime, timedelta, timezone

from raccoon_ridelog.db.session import AsyncSessionLocal
from raccoon_ridelog.models.enums import MotorcycleBrand
from raccoon_ridelog.services import motorcycle_service, rider_service, trip_service


async def main() -> None:
    async with AsyncSessionLocal() as session:
        rider = None
        motorcycle = None
        trip = None
        try:
            # --- Rider ---
            rider = await rider_service.register_rider(
                session,
                username="svctest01",
                email="svctest01@raccoon.dev",
                password_hash="placeholder-not-hashed-yet",
            )
            print(f"[rider] registrado: {rider.id} ({rider.username})")

            fetched = await rider_service.get_rider(session, rider.id)
            assert fetched is not None and fetched.username == "svctest01"
            print("[rider] get OK")

            renamed = await rider_service.rename_rider(session, rider.id, "svctest01_renamed")
            assert renamed is not None and renamed.username == "svctest01_renamed"
            print(f"[rider] rename OK: {renamed.username}")

            # --- Motorcycle ---
            motorcycle = await motorcycle_service.register_motorcycle(
                session,
                rider_id=rider.id,
                brand=MotorcycleBrand.KAWASAKI,
                model_name="Ninja 650",
                engine_cc=649,
            )
            print(f"[motorcycle] registrada: {motorcycle.id}")

            garage = await motorcycle_service.list_rider_garage(session, rider.id)
            assert len(garage) == 1 and garage[0].id == motorcycle.id
            print("[motorcycle] list_rider_garage OK")

            # --- Trip ---
            trip = await trip_service.register_trip(
                session,
                motorcycle_id=motorcycle.id,
                destination_name="Tepoztlán",
                latitude=18.9847,
                longitude=-99.0938,
            )
            print(f"[trip] registrado: {trip.id}")

            trips = await trip_service.list_motorcycle_trips(session, motorcycle.id)
            assert len(trips) == 1 and trips[0].id == trip.id
            print("[trip] list_motorcycle_trips OK")

            since = datetime.now(timezone.utc) - timedelta(hours=1)
            recent = await trip_service.list_recent_trips(session, since)
            assert any(t.id == trip.id for t in recent)
            print("[trip] list_recent_trips OK")

            print("\n✅ Todos los checks de servicios pasaron.")

        finally:
            # cleanup garantizado, corra o no corra bien el bloque de arriba
            if trip is not None:
                from raccoon_ridelog.repositories import trip_repository
                await trip_repository.delete_trip(session, trip)
            if motorcycle is not None:
                removed = await motorcycle_service.remove_motorcycle(session, motorcycle.id)
                print(f"[cleanup] motorcycle eliminada: {removed}")
            if rider is not None:
                removed = await rider_service.remove_rider(session, rider.id)
                print(f"[cleanup] rider eliminado: {removed}")


if __name__ == "__main__":
    asyncio.run(main())