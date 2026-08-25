# Product Requirements Document (PRD)
## Product: Raccoon Ride-Log API

**Product Vision:** A centralized backend system for riders to register their motorcycle garage, plan road trips, and automatically retrieve weather conditions at the destination using basic telemetry. The system will provide daily automated analytics based on the completed trips.

---

### 1. Business Objects and Validation Rules
These are our core models and the constraints that must be validated at the entry layer (Data Transfer Objects / Schemas).

**A. Object: `Rider` (User)**
*   `id`: UUID (Auto-generated).
*   `username`: Alphanumeric string, length between 5 and 20 characters. No spaces.
*   `email`: Valid email format (Regex: `^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$`).
*   `password_hash`: String (Hashed using BCrypt on the backend; the endpoint receives plain text with a minimum of 8 characters, at least 1 uppercase letter, and 1 number).
*   `is_active`: Boolean (Default: `true`).

**B. Object: `Motorcycle` (Vehicle)**
*   `id`: UUID.
*   `rider_id`: Foreign Key (FK) relating to `Rider`.
*   `brand`: Enumerator (See Section 2).
*   `model_name`: String, length between 2 and 50 (e.g., "Tiger Sport 800", "GSX-8S").
*   `engine_cc`: Integer, must be greater than 125 and less than 2500.

**C. Object: `Trip` (Ride / Journey)**
*   `id`: UUID.
*   `motorcycle_id`: Foreign Key (FK) relating to `Motorcycle`.
*   `destination_name`: String, max 100 characters.
*   `latitude`: Float (Range: -90.0 to 90.0).
*   `longitude`: Float (Range: -180.0 to 180.0).
*   `weather_condition`: String, injected via external API (Max 50 characters).
*   `temperature_celsius`: Float, injected via external API.
*   `trip_date`: ISO 8601 format (e.g., `2026-09-15T10:00:00Z`).

---

### 2. Catalogs and Enumerators (Enums)
In Python, we will use the native `Enum` class to strictly restrict these inputs:

*   **`MotorcycleBrand`**: `TRIUMPH`, `KAWASAKI`, `SUZUKI`, `YAMAHA`, `OTHER`.
*   **`RiderRole`**: `ADMIN`, `STANDARD_RIDER`.

---

### 3. External API Integration (Core Logic)
*   **Target API:** **Open-Meteo API** (100% free, no tokens or registration required).
*   **External Endpoint:** `GET https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true`
*   **Execution Trigger:** Triggered when the user calls `POST /trips`. 
*   **Data Flow:** The client sends the destination's latitude and longitude. Before persisting the record in the SQL database, the Python service makes an asynchronous HTTP request to Open-Meteo. It extracts `temperature` and `weathercode`, maps the weather condition (e.g., "Clear sky", "Heavy rain"), and saves the complete `Trip` object enriched with this meteorological data.

---

### 4. Reporting Engine (Pandas & Scheduler)
*   **Execution Trigger:** A scheduled Cron Job running strictly every day at **12:00 AM (Midnight)**.
*   **Analytical Process:**
    1. The engine executes an SQL `JOIN` query between the `Motorcycle` and `Trip` tables to retrieve data from the last 24 hours.
    2. The result set is loaded into a Pandas `DataFrame`.
    3. Using Pandas, the data is grouped by motorcycle brand (`brand`) to calculate the average temperature experienced during the rides.
    4. The engine exports a physical file named `daily_telemetry_YYYY_MM_DD.csv` to a secure folder on the server.

---

### 5. REST API Endpoints Table

| Verb | Endpoint | Description | Requires Auth (JWT) | Specific Headers |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/auth/token` | Receives `email` and `password`. Returns JWT. | ❌ No | `Content-Type: application/json` |
| **POST** | `/api/v1/riders` | New user registration (Signup). | ❌ No | `Content-Type: application/json` |
| **GET** | `/api/v1/motorcycles` | Lists motorcycles owned by the authenticated rider. | ✅ Yes | `Authorization: Bearer <token>` |
| **POST** | `/api/v1/motorcycles` | Registers a new motorcycle in the garage. | ✅ Yes | `Authorization: Bearer <token>` |
| **POST** | `/api/v1/trips` | Registers a trip and fetches external weather data. | ✅ Yes | `Authorization: Bearer <token>` |
| **GET** | `/api/v1/reports/latest` | Downloads the CSV file of the most recently generated report. | ✅ Yes (Only `ADMIN`) | `Authorization: Bearer <token>` |

---

### 6. Security and Authentication (OAuth2)
We will implement the **OAuth2 flow with JWT (JSON Web Tokens)**. Validation will occur at the middleware/dependency level for all protected endpoints.

*   **Signature Algorithm:** `HS256` (HMAC using SHA-256). Ideal, fast, and symmetric (only the server knows the `SECRET_KEY`).
*   **JWT Payload Structure:**
    ```json
    {
      "sub": "550e8400-e29b-41d4-a716-446655440000",
      "email": "rider@debuggeando.com",
      "role": "STANDARD_RIDER",
      "iat": 1724578000, 
      "exp": 1724581600  
    }
    ```
    *(Note: `iat` stands for Issued At, and `exp` is the Expiration time, e.g., 1 hour).*

---

### 7. Documentation and Database
*   **Relational Database:** `PostgreSQL` or `SQLite` (SQLite recommended for the first local iteration).
*   **API Documentation:** The project must auto-generate its own interactive interface using the **OpenAPI 3.0** standard. It will be exposed at the `/docs` route using **Swagger UI**.