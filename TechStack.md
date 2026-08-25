# Technical Specifications: Modern Python Tech Stack
## Project: Raccoon Ride-Log API

*   **Package Management & Execution Engine**
    *   `uv`: An ultra-fast, Rust-based package and project manager. It replaces `pip` and handles virtual environments, dependencies (`pyproject.toml`, `uv.lock`), and Python versions perfectly. This is the modern equivalent to Maven.
    *   `Uvicorn`: An ASGI (Asynchronous Server Gateway Interface) web server implementation for Python. This is the engine that will serve the application (similar to embedded Tomcat).

*   **Core API Framework & Validation**
    *   `FastAPI`: A modern, fast, high-performance web framework for building APIs with Python based on standard Python type hints. It auto-generates Swagger/OpenAPI documentation.
    *   `Pydantic`: The most widely used data validation library for Python. It forces strict typing and data parsing (serving the exact role of Java DTOs with validation annotations).

*   **Database & Object-Relational Mapping (PostgreSQL)**
    *   `SQLAlchemy` (v2.0+): The enterprise-standard ORM for Python. It provides a full suite of persistence patterns (equivalent to Hibernate).
    *   `asyncpg`: A database interface library designed specifically for PostgreSQL and Python/asyncio. It is significantly faster than standard synchronous drivers.


*   **Security & Authentication**
    *   `PyJWT`: A Python library that allows you to encode and decode JSON Web Tokens (JWT) for the OAuth2 implementation.
    *   `passlib`: A password hashing library that provides cross-platform implementations of over 30 password hashing algorithms.
    *   `bcrypt`: The specific hashing algorithm backend used alongside `passlib` to encrypt rider passwords securely.

*   **Business Logic: External APIs & Tasks**
    *   **Target External API:** `Open-Meteo API` (`https://api.open-meteo.com/v1/forecast`). Free, no-token weather telemetry.
    *   `httpx`: A fully featured, next-generation HTTP client for Python with async support. Used to query the Open-Meteo API without blocking the main thread (equivalent to Spring's `WebClient`).
    *   `APScheduler`: Advanced Python Scheduler. A lightweight in-process task scheduler to trigger the midnight reporting job.

*   **Data Analysis & Reporting**
    *   `pandas`: A powerful data manipulation and analysis library. It will be used to ingest the SQL query results, aggregate the trip data by motorcycle brand, and export the daily CSV file.

*   **Testing Strategy & Quality Assurance**
    *   `pytest`: The standard, highly extensible testing framework for Python (equivalent to JUnit).
    *   `pytest-asyncio`: A plugin for `pytest` that allows testing of asynchronous functions and coroutines.