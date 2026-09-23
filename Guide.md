# Guía de estudio — Python moderno / SQLAlchemy async / FastAPI
### Basada en el desarrollo de Raccoon Ride-Log API

Esta guía cubre, en orden, todo lo que construimos: conexión y pool, modelado de entidades, relaciones, repositorios y servicios. Cada respuesta incluye la comparación con Java/Spring cuando ayuda a fijar el concepto.

---

## Bloque 1 — Conexión, sesión y pool

### 1. ¿Qué es `AsyncSessionLocal` y por qué no se usa directamente, sino que se "abre" con `async with`?

`AsyncSessionLocal` es una **fábrica de sesiones** (`async_sessionmaker`), no una sesión en sí. Cada vez que la llamas (`AsyncSessionLocal()`), te da una sesión nueva. Se usa con `async with` porque una `AsyncSession` mantiene recursos (una conexión del pool, un buffer de cambios pendientes) que deben cerrarse siempre, incluso si algo falla — `async with` garantiza ese cierre, equivalente a un `try/finally` implícito.

```python
async with AsyncSessionLocal() as session:
    ...  # la sesión se cierra sola al salir del bloque, incluso si hay excepción
```

**Java:** `AsyncSessionLocal` ≈ `SessionFactory`/`EntityManagerFactory`. `async with` ≈ el ciclo de vida de un `EntityManager` dentro de un `try-with-resources`, o lo que Spring maneja implícitamente con `@Transactional`.

---

### 2. ¿Qué es el *connection pool* y por qué no abrimos una conexión nueva por cada query?

Abrir una conexión TCP a Postgres es costoso (handshake, autenticación). El pool mantiene un conjunto de conexiones **ya abiertas y reutilizables** — cuando tu código pide una conexión, toma una prestada del pool; cuando termina, la devuelve (no la cierra). Esto evita pagar el costo de apertura en cada request.

```python
create_async_engine(
    settings.database_url,
    pool_size=settings.db_pool_size,        # conexiones que se mantienen abiertas
    max_overflow=settings.db_max_overflow,  # conexiones extra permitidas en picos
    pool_timeout=settings.db_pool_timeout,  # cuánto esperar si el pool está lleno
    pool_recycle=settings.db_pool_recycle,  # segundos antes de reciclar una conexión vieja
)
```

**Java:** exactamente el mismo concepto que **HikariCP** en Spring Boot (`spring.datasource.hikari.maximum-pool-size`, etc.) — mismo problema, mismo tipo de solución.

---

### 3. ¿Qué es `AsyncSession` en comparación con el `EntityManager` de Hibernate?

Ambos son el **"unit of work"**: mantienen un *identity map* (un objeto cargado no se vuelve a traer dos veces en la misma sesión), trackean qué objetos cambiaron (*dirty checking*), y agrupan operaciones dentro de una transacción. La diferencia principal es que en Spring casi nunca ves el `EntityManager` explícitamente (`@Transactional` lo esconde); aquí lo manejas tú mismo, a mano, en cada función.

---

### 4. ¿Por qué `Settings(BaseSettings)` explotó con `Extra inputs are not permitted` y cómo se resuelve?

Por defecto, `pydantic-settings` es **estricto**: si el `.env` tiene variables que la clase no declara (en nuestro caso, `POSTGRES_USER`/`PASSWORD`/`DB`, que solo las usa Docker Compose, no la app Python), rechaza toda la instancia. Se resuelve con `extra="ignore"` en `model_config`.

```python
model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```

**Java:** lo contrario a Spring Boot, donde `ignoreUnknownFields` es `true` por default — Pydantic prioriza "avísame si algo no cuadra" sobre "no rompas mi arranque".

---

## Bloque 2 — Modelado de entidades (ORM)

### 5. ¿Qué es `Mapped[...]` y en qué se diferencia de un simple type hint de Python?

`Mapped[tipo]` no es solo documentación — es parte de la definición real del ORM. Le dice a SQLAlchemy 2.0 qué tipo Python esperar para esa columna, y junto con `mapped_column(...)` define tanto el tipo Python como el tipo SQL de la columna.

```python
username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
```

**Java:** un campo `private String username;` en una `@Entity` — la diferencia es que en Java, el tipo Java y el tipo de columna SQL están más separados (el tipo de columna suele inferirse o declararse aparte con `@Column`).

---

### 6. ¿Por qué `__table_args__ = (CheckConstraint(...))` explotó con `ArgumentError`, y qué diferencia hay con `(CheckConstraint(...),)`?

En Python, los paréntesis solos **no crean una tupla** — solo agrupan una expresión. Lo que convierte algo en tupla es la **coma**, no los paréntesis. `(CheckConstraint(...))` es solo el objeto `CheckConstraint` "pelado"; `(CheckConstraint(...),)` sí es una tupla de un elemento — y SQLAlchemy exige que `__table_args__` sea tupla o dict.

```python
__table_args__ = (
    CheckConstraint("char_length(username) BETWEEN 5 AND 20", name="username_length"),
    # ^ esta coma es obligatoria si solo hay un elemento
)
```

---

### 7. ¿Cómo se mapea un `ENUM` nativo de Postgres que ya existe (creado por SQL crudo), sin que SQLAlchemy intente crearlo de nuevo?

Con `Enum(MiEnumPython, name="nombre_exacto_en_postgres", create_type=False)`. Sin el `name` explícito, SQLAlchemy infiere el nombre del tipo a partir del nombre de la clase Python en minúsculas (`RiderRole` → `riderrole`), lo cual puede no coincidir con el nombre real en la DB (`rider_role`). `create_type=False` evita que SQLAlchemy intente un `CREATE TYPE` que fallaría porque el tipo ya existe.

```python
role: Mapped[RiderRole] = mapped_column(
    Enum(RiderRole, name="rider_role", create_type=False),
    default=RiderRole.STANDARD_RIDER,
)
```

---

### 8. ¿Qué es un import circular en Python, y por qué en Java este problema casi no existe?

Python ejecuta los módulos de arriba hacia abajo, **una sola vez**, en el momento del import. Si `rider.py` importa `motorcycle.py` y `motorcycle.py` importa `rider.py` (imports reales, no strings), ninguno de los dos termina de "existir" completamente cuando el otro lo necesita → `ImportError`. Java no tiene este problema porque el compilador hace **dos pasadas**: primero resuelve todos los nombres de clase disponibles, luego los cuerpos — dos clases pueden referenciarse mutuamente sin fricción.

---

### 9. ¿Cómo se resuelve el import circular entre dos modelos que se referencian mutuamente (`Rider` ↔ `Motorcycle`)?

Con **strings** en las anotaciones de tipo (`Mapped["Motorcycle"]`, que SQLAlchemy resuelve en runtime, no en el momento de definir la clase) combinados con `TYPE_CHECKING`, para que el editor sí pueda tipar correctamente sin generar el import real:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from raccoon_ridelog.models.motorcycle import Motorcycle
    # este bloque NUNCA se ejecuta en runtime (TYPE_CHECKING es False)
    # pero Pylance/mypy sí lo "ve" para tipar correctamente

class Rider(Base):
    motorcycles: Mapped[list["Motorcycle"]] = relationship(back_populates="rider")
```

**Error común:** dejar el import real (`from ... import Motorcycle`) **además** del bloque `TYPE_CHECKING`, en vez de borrarlo — el bloque no reemplaza nada, solo se suma.

---

### 10. ¿Dónde vive realmente la Foreign Key: en `mapped_column(ForeignKey(...))` o en `relationship()`?

En `mapped_column(ForeignKey(...))`. Esa línea genera la columna real en Postgres con su constraint de integridad referencial. `relationship()` **no genera ninguna columna ni SQL** — es un atributo de conveniencia a nivel Python/ORM que le dice a SQLAlchemy: "cuando accedan a este atributo, resuelve el JOIN usando la FK que ya existe".

```python
rider_id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True), ForeignKey("rider.id", ondelete="CASCADE"), nullable=False
)  # <- la FK real

rider: Mapped["Rider"] = relationship(back_populates="motorcycles")  # <- solo navegación
```

**Java:** JPA fusiona ambas cosas en un solo campo (`@ManyToOne @JoinColumn(name="rider_id") private Rider rider;`); SQLAlchemy las separa en dos atributos independientes y **ambos coexisten**: `motorcycle.rider_id` (el UUID crudo) y `motorcycle.rider` (el objeto completo).

---

## Bloque 3 — Sesión, queries y resultados

### 11. ¿Qué diferencia hay entre `Result`, `Row` y un "escalar"?

- **`Result`**: el cursor completo que devuelve `session.execute(...)` — todavía no son objetos Python usables.
- **`Row`**: cada fila individual del cursor, empaquetada como tupla-con-nombre, aunque tenga un solo valor adentro.
- **Escalar**: el valor puro que está *dentro* de un `Row` — un `Rider`, un `int`, sin la envoltura de tupla.

`Row` envuelve → `.scalars()` desenvuelve → lo que obtienes es el escalar.

```python
result = await session.execute(select(Rider))
result.all()             # -> [(Rider(...),), (Rider(...),)]  ← tuplas de un elemento
result.scalars().all()   # -> [Rider(...), Rider(...)]        ← escalares planos
```

---

### 12. ¿Cuál es la diferencia entre `.first()`, `.one()`, `.one_or_none()` y `.scalar()`?

| Método | Comportamiento con 0 filas | Comportamiento con 2+ filas |
|---|---|---|
| `.first()` | devuelve `None` | devuelve la primera, sin quejarse |
| `.one()` | lanza excepción | lanza excepción |
| `.one_or_none()` | devuelve `None` | lanza excepción |
| `.scalar()` | devuelve `None` | devuelve el primero (aplanado) |

`scalar_one_or_none()` combina "aplanar a un solo valor" + "exigir que sea único o inexistente" — ideal para búsquedas por columna `unique=True` como `email`.

---

### 13. ¿Por qué `session.get(Rider, rider_id)` es distinto (y más simple) que `session.execute(select(Rider).where(Rider.id == rider_id))`?

`session.get()` es un atajo optimizado específicamente para búsqueda **por clave primaria** — no pasa por `execute()`/`select()`/`.scalars()`, y aprovecha el *identity map* de la sesión (si el objeto ya estaba cargado, ni siquiera va a la DB). Para cualquier otro filtro (por email, por fecha, etc.) sí necesitas `select().where()`.

---

### 14. ¿Cómo funciona el *dirty checking* y por qué `update_rider` casi no tiene código?

En cuanto un objeto sale de `session.get(...)` o de un `select()` ejecutado con esa sesión, queda **attached** (adjunto) a ella. Cualquier atributo que mutes en Python sobre ese objeto queda marcado internamente como "sucio". En el próximo `commit()`, SQLAlchemy compara el estado actual contra el original y genera el `UPDATE` solo con los campos que cambiaron — por eso no hace falta un método `.set(...)` explícito.

```python
rider = await rider_repository.get_rider_by_id(session, rider_id)
rider.username = "nuevo_nombre"          # <- aquí se marca "dirty", sin llamar a nada más
await rider_repository.update_rider(session, rider)  # <- solo hace commit() + refresh()
```

**Importante:** solo funciona si el objeto sigue *attached* a la misma sesión en la que se mutó.

**Java:** es el mismo mecanismo detrás de `@Transactional` en Spring — modificar una entidad "managed" la persiste sola al salir del método, sin `save()` explícito.

---

### 15. ¿Cuál es la diferencia entre borrar con `session.delete(objeto)` (ORM) y con `delete(Modelo).where(...)` (Core)?

`session.delete(objeto)` dispara el ciclo de vida completo del ORM: cascadas de `relationship()`, eventos, sincronización del *identity map*. Requiere cargar el objeto primero (un `SELECT` + un `DELETE`).

`delete(Modelo).where(...)` (Core) genera **un solo** `DELETE` directo, sin cargar nada a memoria — pero bypasea el ORM por completo: no dispara cascadas de `relationship()` ni eventos, y si el objeto ya estaba cargado en la sesión, esta no se entera del borrado.

```python
# ORM — dos roundtrips, dispara cascadas de relationship()
rider = await get_rider_by_email(session, email)
await session.delete(rider)

# Core — un roundtrip, bypasea el ORM
await session.execute(delete(Rider).where(Rider.email == email))
```

---

## Bloque 4 — Repositorios y servicios

### 16. ¿Por qué los repositorios son funciones sueltas en un módulo, y no una clase con métodos?

Porque no hay estado de instancia que mantener — nada equivalente a un `this.entityManager` guardado. Cada función recibe la `AsyncSession` como parámetro explícito. Es funcionalmente igual a que en Java todos los métodos fueran `static` en una clase final con constructor privado; Python simplemente no obliga a envolver eso en una clase.

```python
# no hay "instancia" de RiderRepository — solo funciones que reciben la sesión
async def get_rider_by_id(session: AsyncSession, rider_id: uuid.UUID) -> Rider | None:
    return await session.get(Rider, rider_id)
```

**Java:** `interface RiderRepository extends JpaRepository<Rider, UUID>` — Spring Data genera `save`/`findById`/`findAll`/`delete` automáticamente por convención; en Python, cada operación (incluso las triviales) se escribe explícitamente.

---

### 17. ¿Por qué la capa de servicios, en Fase 1, se ve casi idéntica a la de repositorios?

Porque todavía no hay lógica de negocio real que orquestar (eso llega en Fase 2: hash de contraseña, llamada a Open-Meteo antes de guardar un `Trip`, JWT). Hoy el servicio es un "passthrough": arma la entidad (`uuid.uuid4()`, construir el objeto) y delega al repositorio. La razón de ser de la capa aparecerá cuando un servicio necesite **coordinar más de un repositorio o una llamada externa** en una sola operación de negocio.

---

### 18. ¿Por qué `trip_service.py` no expone `update_trip`/`delete_trip`, aunque el repositorio sí los tenga?

Porque el servicio expone solo lo que el **negocio** necesita (lo que definen los endpoints del PRD), mientras que el repositorio se mantiene completo por convención/flexibilidad futura, independiente de qué use la API hoy. El PRD no define ningún `PUT`/`DELETE /trips`, así que el servicio no necesita exponer esas operaciones todavía, aunque técnicamente existan un nivel más abajo.

---

### 19. ¿Por qué la sesión se recibe "inyectada desde afuera" en vez de abrirse dentro de cada función de servicio?

Para que el mismo patrón funcione sin cambios cuando lleguemos a FastAPI: ahí la sesión llegará vía `Depends(get_db)`, gestionada por el framework en el ciclo de vida del request. Si el servicio abriera su propia sesión internamente, no podrías compartir una sola transacción entre varias llamadas de servicio dentro del mismo endpoint (por ejemplo, crear un `Trip` y actualizar estadísticas del `Motorcycle` en la misma transacción).

---

### 20. ¿Qué es `greenlet` y por qué SQLAlchemy async lo necesita aunque nunca lo importes en tu código?

Gran parte del motor interno de SQLAlchemy (ORM, eventos, manejo de sesión) fue escrito originalmente en código síncrono. `greenlet` le permite a SQLAlchemy "pausar y reanudar" ese código síncrono desde un contexto `async`/`await`, sin reescribir todo el ORM. Cualquier uso de `sqlalchemy[asyncio]` con un driver async (`asyncpg`) lo requiere como dependencia — normalmente viene incluido, pero si se declaró SQLAlchemy sin el extra `[asyncio]`, hay que agregarlo aparte con `uv add greenlet`.

---

### 21. ¿Cuál es la diferencia real entre `uv add paquete` y `pip install paquete`?

`pip install` solo toca el `.venv` — el paquete queda instalado en tu máquina, pero **no queda registrado en ningún archivo versionable**. Si otra persona clona el repo y corre `uv sync`, ese paquete no aparecería. `uv add` hace tres cosas en un solo comando: escribe la entrada en `pyproject.toml`, resuelve la versión y actualiza `uv.lock`, e instala en el `.venv` — deja rastro reproducible.

**Java:** la diferencia entre instalar un `.jar` a mano en el classpath vs. agregar la dependencia al `pom.xml` con Maven.

---

### 22. Sin volumen persistente en `docker-compose.yml`, ¿qué pasa exactamente al hacer `docker compose down` vs. `docker compose stop`?

- `stop`/`start`/`restart`: el contenedor sigue siendo el mismo, los datos **persisten** (viven en la capa de escritura del contenedor).
- `down`: **elimina** el contenedor. Al volver a `up`, Postgres arranca desde cero y **vuelve a correr** `01_schema.sql` y `02_seed.sql` automáticamente — útil para resetear rápido en desarrollo, pero significa que cualquier dato de prueba que no limpiaste a mano se pierde (o, si un script falló a medias, queda basura hasta el próximo `down`).

**Java:** equivalente a `spring.jpa.hibernate.ddl-auto=create-drop` con una base H2 en memoria — limpio en cada arranque, no apto para producción.

---

### 23. Si un `assert` de Python falla a la mitad de un script que ya hizo `commit()`, ¿hay rollback automático?

**No.** A diferencia de un test de Spring con `@Transactional` (que hace rollback automático al final de cada test), un `AssertionError` genérico en un script Python no revierte nada que ya se haya confirmado con `commit()`. Por eso conviene envolver el flujo en `try/finally`, garantizando que la limpieza corra pase lo que pase:

```python
try:
    rider = await rider_repository.create_rider(session, new_rider)  # ya hizo commit
    assert rider.username == "algo_que_puede_fallar"                 # si esto truena...
finally:
    await rider_repository.delete_rider(session, rider)  # ...esto igual se ejecuta
```

---

### 24. ¿Por qué `Rider.email == email` dentro de `.where(...)` no se evalúa como un `bool` normal de Python?

Porque `Rider.email` no es un string — es un `InstrumentedAttribute`, un objeto especial que SQLAlchemy pone en la clase mapeada. Ese objeto **sobrecarga el operador `==`** (vía `__eq__`) para que, en vez de comparar y devolver `True`/`False`, construya un objeto `BinaryExpression` — una representación en memoria de `email = :valor` en SQL. `select()` sabe traducir esa expresión al `WHERE` real.

**Java:** el mismo truco conceptual que la Criteria API (`cb.equal(root.get("email"), email)`), salvo que Java no permite sobrecargar `==` para tipos propios, así que ahí se ve más explícito.

---

### 25. En el flujo `get → mutar → update`, ¿por qué es necesario el `get` si de todos modos vas a sobrescribir el valor?

Porque el *dirty checking* solo funciona sobre un objeto **cargado y attached** a la sesión — SQLAlchemy necesita el estado "antes" en memoria para poder comparar contra el estado "después" y generar el `UPDATE` correcto. No existe forma de aprovechar ese mecanismo sin cargar la fila primero. (La alternativa que sí evita el roundtrip es un `update()` de Core explícito, tipo `UPDATE rider SET username = :val WHERE id = :id`, pero eso renuncia al dirty checking y se usa solo cuando el rendimiento lo justifica.)

---

## Tabla resumen rápida (para repaso de último minuto)

| Concepto | SQL | SQLAlchemy | Java / JPA |
|---|---|---|---|
| Clave primaria | `UUID PRIMARY KEY` | `mapped_column(primary_key=True)` | `@Id` |
| Valor único | `UNIQUE` | `unique=True` | `@Column(unique = true)` |
| Enum nativo | `CREATE TYPE ... AS ENUM` | `Enum(X, name=..., create_type=False)` | `@Enumerated(EnumType.STRING)` |
| FK + cascada | `REFERENCES t(id) ON DELETE CASCADE` | `ForeignKey("t.id", ondelete="CASCADE")` | `@JoinColumn` + cascade JPA |
| Lado "muchos" | — | `relationship(back_populates=...)` | `@ManyToOne` |
| Lado "uno" | — | `relationship(...)` con `list[...]` | `@OneToMany(mappedBy=...)` |
| Unidad de trabajo | — | `AsyncSession` | `EntityManager` |
| Pool de conexiones | — | `create_async_engine(pool_size=...)` | HikariCP |
| Referencia mutua entre clases | no aplica | `if TYPE_CHECKING: import ...` | no aplica (compilador de dos pasadas) |