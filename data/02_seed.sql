-- Riders de prueba
INSERT INTO rider (id, username, email, password_hash, role, is_active) VALUES
    ('11111111-1111-1111-1111-111111111111', 'alecalde', 'alejandro@example.com',
     '$2b$12$abcdefghijklmnopqrstuvKQ7X8yYVYVYVYVYVYVYVYVYVYVYVYVe', 'ADMIN', true),
    ('22222222-2222-2222-2222-222222222222', 'racoonrider', 'rider2@example.com',
     '$2b$12$abcdefghijklmnopqrstuvKQ7X8yYVYVYVYVYVYVYVYVYVYVYVYVe', 'STANDARD_RIDER', true),
    ('33333333-3333-3333-3333-333333333333', 'veloz_gaby', 'gaby@example.com',
     '$2b$12$abcdefghijklmnopqrstuvKQ7X8yYVYVYVYVYVYVYVYVYVYVYVYVe', 'STANDARD_RIDER', true),
    ('44444444-4444-4444-4444-444444444444', 'moto_hector', 'hector@example.com',
     '$2b$12$abcdefghijklmnopqrstuvKQ7X8yYVYVYVYVYVYVYVYVYVYVYVYVe', 'STANDARD_RIDER', true),
    ('55555555-5555-5555-5555-555555555555', 'admin_paola', 'paola@example.com',
     '$2b$12$abcdefghijklmnopqrstuvKQ7X8yYVYVYVYVYVYVYVYVYVYVYVYVe', 'ADMIN', true);

-- 10 motocicletas: 2 por cada marca del enum, repartidas entre los riders
INSERT INTO motorcycle (id, rider_id, brand, model_name, engine_cc) VALUES
    ('a0000000-0000-0000-0000-000000000001', '11111111-1111-1111-1111-111111111111', 'TRIUMPH', 'Tiger Sport 800', 798),
    ('a0000000-0000-0000-0000-000000000002', '33333333-3333-3333-3333-333333333333', 'TRIUMPH', 'Trident 660', 660),
    ('a0000000-0000-0000-0000-000000000003', '22222222-2222-2222-2222-222222222222', 'KAWASAKI', 'Versys 650', 649),
    ('a0000000-0000-0000-0000-000000000004', '44444444-4444-4444-4444-444444444444', 'KAWASAKI', 'Ninja 400', 399),
    ('a0000000-0000-0000-0000-000000000005', '22222222-2222-2222-2222-222222222222', 'SUZUKI', 'GSX-8S', 776),
    ('a0000000-0000-0000-0000-000000000006', '55555555-5555-5555-5555-555555555555', 'SUZUKI', 'V-Strom 650', 645),
    ('a0000000-0000-0000-0000-000000000007', '33333333-3333-3333-3333-333333333333', 'YAMAHA', 'MT-07', 689),
    ('a0000000-0000-0000-0000-000000000008', '44444444-4444-4444-4444-444444444444', 'YAMAHA', 'Tenere 700', 689),
    ('a0000000-0000-0000-0000-000000000009', '55555555-5555-5555-5555-555555555555', 'OTHER', 'Royal Enfield Himalayan', 411),
    ('a0000000-0000-0000-0000-000000000010', '11111111-1111-1111-1111-111111111111', 'OTHER', 'Benelli TRK 502', 500);

-- 42 trips repartidos entre las 10 motocicletas, con fechas variadas
-- (18 dentro de las ultimas 24h, el resto entre 2 y 10 dias atras) para que
-- el reporte de Pandas agrupado por marca tenga variacion real y para que
-- puedas probar que el filtro "ultimas 24 horas" del reporte SI filtra.
INSERT INTO trip (motorcycle_id, destination_name, latitude, longitude, weather_condition, temperature_celsius, trip_date) VALUES
    ('a0000000-0000-0000-0000-000000000001', 'Valle de Bravo', 19.1947, -100.1319, 'Clear sky', 25.7, now() - interval '1.08 hours'),
    ('a0000000-0000-0000-0000-000000000002', 'Tepoztlan', 18.9847, -99.0937, 'Partly cloudy', 18.0, now() - interval '5.63 hours'),
    ('a0000000-0000-0000-0000-000000000003', 'Malinalco', 18.9483, -99.4917, 'Clear sky', 26.8, now() - interval '16.06 hours'),
    ('a0000000-0000-0000-0000-000000000004', 'Real de Catorce', 23.6858, -100.8792, 'Mainly clear', 18.9, now() - interval '2.50 hours'),
    ('a0000000-0000-0000-0000-000000000005', 'Bernal, Queretaro', 20.7458, -99.9483, 'Sunny', 25.1, now() - interval '1.19 hours'),
    ('a0000000-0000-0000-0000-000000000006', 'Taxco', 18.5561, -99.6036, 'Partly cloudy', 17.4, now() - interval '12.12 hours'),
    ('a0000000-0000-0000-0000-000000000007', 'Puerto Vallarta', 20.6534, -105.2253, 'Heavy rain', 22.2, now() - interval '5.07 hours'),
    ('a0000000-0000-0000-0000-000000000008', 'Creel, Chihuahua', 27.7539, -107.6314, 'Overcast', 14.5, now() - interval '13.03 hours'),
    ('a0000000-0000-0000-0000-000000000009', 'Ensenada', 31.8667, -116.5964, 'Foggy', 13.3, now() - interval '14.05 hours'),
    ('a0000000-0000-0000-0000-000000000010', 'Bacalar', 18.6786, -88.3961, 'Thunderstorm', 29.7, now() - interval '0.65 hours'),
    ('a0000000-0000-0000-0000-000000000001', 'Xilitla', 21.3833, -98.9989, 'Light rain', 20.4, now() - interval '16.56 hours'),
    ('a0000000-0000-0000-0000-000000000002', 'Cholula', 19.0639, -98.3061, 'Clear sky', 22.1, now() - interval '4.08 hours'),
    ('a0000000-0000-0000-0000-000000000003', 'Metepec', 19.2603, -99.6058, 'Overcast', 17.6, now() - interval '8.24 hours'),
    ('a0000000-0000-0000-0000-000000000004', 'Guanajuato', 21.019, -101.2574, 'Sunny', 21.1, now() - interval '2.72 hours'),
    ('a0000000-0000-0000-0000-000000000005', 'San Miguel de Allende', 20.9153, -100.7436, 'Clear sky', 28.2, now() - interval '14.39 hours'),
    ('a0000000-0000-0000-0000-000000000006', 'Valle de Bravo', 19.1947, -100.1319, 'Clear sky', 27.7, now() - interval '17.28 hours'),
    ('a0000000-0000-0000-0000-000000000007', 'Tepoztlan', 18.9847, -99.0937, 'Partly cloudy', 20.9, now() - interval '22.88 hours'),
    ('a0000000-0000-0000-0000-000000000008', 'Malinalco', 18.9483, -99.4917, 'Clear sky', 22.5, now() - interval '13.20 hours'),
    ('a0000000-0000-0000-0000-000000000009', 'Real de Catorce', 23.6858, -100.8792, 'Mainly clear', 18.3, now() - interval '7 days 13.28 hours'),
    ('a0000000-0000-0000-0000-000000000010', 'Bernal, Queretaro', 20.7458, -99.9483, 'Sunny', 28.5, now() - interval '2 days 15.21 hours'),
    ('a0000000-0000-0000-0000-000000000001', 'Taxco', 18.5561, -99.6036, 'Partly cloudy', 23.5, now() - interval '3 days 19.67 hours'),
    ('a0000000-0000-0000-0000-000000000002', 'Puerto Vallarta', 20.6534, -105.2253, 'Heavy rain', 28.9, now() - interval '8 days 6.39 hours'),
    ('a0000000-0000-0000-0000-000000000003', 'Creel, Chihuahua', 27.7539, -107.6314, 'Overcast', 14.4, now() - interval '7 days 3.74 hours'),
    ('a0000000-0000-0000-0000-000000000004', 'Ensenada', 31.8667, -116.5964, 'Foggy', 14.1, now() - interval '6 days 16.14 hours'),
    ('a0000000-0000-0000-0000-000000000005', 'Bacalar', 18.6786, -88.3961, 'Thunderstorm', 28.8, now() - interval '3 days 14.01 hours'),
    ('a0000000-0000-0000-0000-000000000006', 'Xilitla', 21.3833, -98.9989, 'Light rain', 15.4, now() - interval '5 days 3.76 hours'),
    ('a0000000-0000-0000-0000-000000000007', 'Cholula', 19.0639, -98.3061, 'Clear sky', 22.6, now() - interval '10 days 5.05 hours'),
    ('a0000000-0000-0000-0000-000000000008', 'Metepec', 19.2603, -99.6058, 'Overcast', 11.2, now() - interval '2 days 5.27 hours'),
    ('a0000000-0000-0000-0000-000000000009', 'Guanajuato', 21.019, -101.2574, 'Sunny', 20.4, now() - interval '7 days 9.23 hours'),
    ('a0000000-0000-0000-0000-000000000010', 'San Miguel de Allende', 20.9153, -100.7436, 'Clear sky', 18.8, now() - interval '7 days 4.89 hours'),
    ('a0000000-0000-0000-0000-000000000001', 'Valle de Bravo', 19.1947, -100.1319, 'Clear sky', 24.0, now() - interval '9 days 3.29 hours'),
    ('a0000000-0000-0000-0000-000000000002', 'Tepoztlan', 18.9847, -99.0937, 'Partly cloudy', 16.5, now() - interval '10 days 12.40 hours'),
    ('a0000000-0000-0000-0000-000000000003', 'Malinalco', 18.9483, -99.4917, 'Clear sky', 27.0, now() - interval '8 days 20.65 hours'),
    ('a0000000-0000-0000-0000-000000000004', 'Real de Catorce', 23.6858, -100.8792, 'Mainly clear', 14.0, now() - interval '5 days 22.94 hours'),
    ('a0000000-0000-0000-0000-000000000005', 'Bernal, Queretaro', 20.7458, -99.9483, 'Sunny', 21.7, now() - interval '9 days 2.09 hours'),
    ('a0000000-0000-0000-0000-000000000006', 'Taxco', 18.5561, -99.6036, 'Partly cloudy', 15.5, now() - interval '3 days 3.52 hours'),
    ('a0000000-0000-0000-0000-000000000007', 'Puerto Vallarta', 20.6534, -105.2253, 'Heavy rain', 23.3, now() - interval '8 days 13.72 hours'),
    ('a0000000-0000-0000-0000-000000000008', 'Creel, Chihuahua', 27.7539, -107.6314, 'Overcast', 11.8, now() - interval '9 days 12.17 hours'),
    ('a0000000-0000-0000-0000-000000000009', 'Ensenada', 31.8667, -116.5964, 'Foggy', 17.8, now() - interval '2 days 15.65 hours'),
    ('a0000000-0000-0000-0000-000000000010', 'Bacalar', 18.6786, -88.3961, 'Thunderstorm', 24.8, now() - interval '10 days 17.27 hours'),
    ('a0000000-0000-0000-0000-000000000001', 'Xilitla', 21.3833, -98.9989, 'Light rain', 20.1, now() - interval '7 days 2.57 hours'),
    ('a0000000-0000-0000-0000-000000000002', 'Cholula', 19.0639, -98.3061, 'Clear sky', 23.2, now() - interval '9 days 0.07 hours');