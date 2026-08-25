CREATE TYPE motorcycle_brand AS ENUM ('TRIUMPH', 'KAWASAKI', 'SUZUKI', 'YAMAHA', 'OTHER');
CREATE TYPE rider_role AS ENUM ('ADMIN', 'STANDARD_RIDER');

CREATE TABLE rider (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username        VARCHAR(20) NOT NULL UNIQUE,
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    role            rider_role NOT NULL DEFAULT 'STANDARD_RIDER',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT username_length CHECK (char_length(username) BETWEEN 5 AND 20)
);

CREATE TABLE motorcycle (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rider_id        UUID NOT NULL REFERENCES rider(id) ON DELETE CASCADE,
    brand           motorcycle_brand NOT NULL,
    model_name      VARCHAR(50) NOT NULL,
    engine_cc       INTEGER NOT NULL,
    CONSTRAINT model_name_length CHECK (char_length(model_name) BETWEEN 2 AND 50),
    CONSTRAINT engine_cc_range CHECK (engine_cc > 125 AND engine_cc < 2500)
);

CREATE TABLE trip (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    motorcycle_id        UUID NOT NULL REFERENCES motorcycle(id) ON DELETE CASCADE,
    destination_name     VARCHAR(100) NOT NULL,
    latitude             DOUBLE PRECISION NOT NULL CHECK (latitude BETWEEN -90.0 AND 90.0),
    longitude            DOUBLE PRECISION NOT NULL CHECK (longitude BETWEEN -180.0 AND 180.0),
    weather_condition    VARCHAR(50),
    temperature_celsius  DOUBLE PRECISION,
    trip_date            TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE EXTENSION IF NOT EXISTS pgcrypto;