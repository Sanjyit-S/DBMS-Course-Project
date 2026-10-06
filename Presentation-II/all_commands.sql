-- ============================================================================
-- AIRLINE RESERVATION & FLIGHT OPERATIONS MANAGEMENT SYSTEM (ARFOM-DB)
-- Course: Database Management Systems (DBMS) - Review 2 Implementation
-- Standards: ANSI SQL / PostgreSQL 15+ (Strict 3NF Decomposition)
-- ============================================================================

-- Drop existing tables in reverse dependency order if rebuilding
DROP TABLE IF EXISTS cancellations CASCADE;
DROP TABLE IF EXISTS baggage CASCADE;
DROP TABLE IF EXISTS checkins CASCADE;
DROP TABLE IF EXISTS payments CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS bookings CASCADE;
DROP TABLE IF EXISTS passengers CASCADE;
DROP TABLE IF EXISTS flights CASCADE;
DROP TABLE IF EXISTS seats CASCADE;
DROP TABLE IF EXISTS aircraft CASCADE;
DROP TABLE IF EXISTS routes CASCADE;
DROP TABLE IF EXISTS airports CASCADE;

-- ----------------------------------------------------------------------------
-- 1. BASE AIRPORT & ROUTE REGISTRY
-- ----------------------------------------------------------------------------
CREATE TABLE airports (
    airport_code CHAR(3) PRIMARY KEY,
    airport_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL
);

CREATE TABLE routes (
    route_id SERIAL PRIMARY KEY,
    origin_airport CHAR(3) NOT NULL,
    dest_airport CHAR(3) NOT NULL,
    distance_km NUMERIC(7,2) NOT NULL CHECK (distance_km > 0.00),
    CONSTRAINT fk_route_origin FOREIGN KEY (origin_airport) REFERENCES airports(airport_code) ON DELETE RESTRICT,
    CONSTRAINT fk_route_dest FOREIGN KEY (dest_airport) REFERENCES airports(airport_code) ON DELETE RESTRICT,
    CONSTRAINT chk_distinct_airports CHECK (origin_airport <> dest_airport)
);

-- ----------------------------------------------------------------------------
-- 2. AIRFRAME & PHYSICAL TOPOLOGY (AIRCRAFT CAPACITY ENFORCEMENT)
-- ----------------------------------------------------------------------------
CREATE TABLE aircraft (
    aircraft_id SERIAL PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    total_capacity INT NOT NULL CHECK (total_capacity > 0)
);

CREATE TABLE seats (
    seat_id SERIAL PRIMARY KEY,
    aircraft_id INT NOT NULL,
    seat_number VARCHAR(4) NOT NULL,
    seat_class VARCHAR(15) NOT NULL CHECK (seat_class IN ('ECONOMY', 'BUSINESS', 'FIRST')),
    CONSTRAINT fk_seat_aircraft FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id) ON DELETE CASCADE,
    CONSTRAINT uq_aircraft_seat UNIQUE (aircraft_id, seat_number)
);

-- ----------------------------------------------------------------------------
-- 3. FLIGHT INVENTORY & OPERATIONAL SEGMENTS
-- ----------------------------------------------------------------------------
CREATE TABLE flights (
    flight_id SERIAL PRIMARY KEY,
    route_id INT NOT NULL,
    aircraft_id INT NOT NULL,
    scheduled_departure TIMESTAMP NOT NULL,
    scheduled_arrival TIMESTAMP NOT NULL,
    flight_status VARCHAR(15) NOT NULL DEFAULT 'SCHEDULED' 
        CHECK (flight_status IN ('SCHEDULED', 'BOARDING', 'DEPARTED', 'ARRIVED', 'CANCELLED', 'DELAYED')),
    CONSTRAINT fk_flight_route FOREIGN KEY (route_id) REFERENCES routes(route_id),
    CONSTRAINT fk_flight_aircraft FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id),
    CONSTRAINT chk_flight_temporal_order CHECK (scheduled_arrival > scheduled_departure)
);

-- ----------------------------------------------------------------------------
-- 4. CUSTOMER PROFILE & COMMERCIAL ORDERS
-- ----------------------------------------------------------------------------
CREATE TABLE passengers (
    passenger_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    passport_number VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    booking_ref CHAR(6) NOT NULL UNIQUE,
    passenger_id INT NOT NULL,
    booking_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    booking_status VARCHAR(15) NOT NULL DEFAULT 'CONFIRMED' 
        CHECK (booking_status IN ('CONFIRMED', 'PENDING', 'CANCELLED')),
    CONSTRAINT fk_booking_passenger FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
);

-- ----------------------------------------------------------------------------
-- 5. TICKETING & SEAT ALLOCATION INVARIANTS
-- ----------------------------------------------------------------------------
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    booking_id INT NOT NULL,
    flight_id INT NOT NULL,
    seat_id INT NOT NULL,
    fare_amount NUMERIC(10,2) NOT NULL CHECK (fare_amount >= 0.00),
    ticket_status VARCHAR(15) NOT NULL DEFAULT 'ISSUED' 
        CHECK (ticket_status IN ('ISSUED', 'CHECKED_IN', 'CANCELLED')),
    CONSTRAINT fk_ticket_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_flight FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    CONSTRAINT fk_ticket_seat FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
    -- BUSINESS RULE: Exactly one passenger per physical seat on any flight
    CONSTRAINT uq_flight_seat UNIQUE (flight_id, seat_id)
);

-- ----------------------------------------------------------------------------
-- 6. SETTLEMENT & REVENUE LEDGER
-- ----------------------------------------------------------------------------
CREATE TABLE payments (
    payment_id SERIAL PRIMARY KEY,
    booking_id INT NOT NULL,
    amount_paid NUMERIC(10,2) NOT NULL CHECK (amount_paid > 0.00),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING')),
    payment_status VARCHAR(15) NOT NULL DEFAULT 'SUCCESS' CHECK (payment_status IN ('SUCCESS', 'FAILED', 'REFUNDED')),
    payment_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
);

-- ----------------------------------------------------------------------------
-- 7. AIRPORT DEPARTURE CONTROL & BAGGAGE CUSTODY
-- ----------------------------------------------------------------------------
CREATE TABLE checkins (
    checkin_id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    checkin_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    boarding_pass VARCHAR(20) NOT NULL UNIQUE,
    CONSTRAINT fk_checkin_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

CREATE TABLE baggage (
    baggage_id SERIAL PRIMARY KEY,
    checkin_id INT NOT NULL,
    weight_kg NUMERIC(5,2) NOT NULL CHECK (weight_kg >= 0.00),
    excess_fee NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (excess_fee >= 0.00),
    CONSTRAINT fk_baggage_checkin FOREIGN KEY (checkin_id) REFERENCES checkins(checkin_id) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 8. CANCELLATION & AUDIT LEDGER
-- ----------------------------------------------------------------------------
CREATE TABLE cancellations (
    cancellation_id SERIAL PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    cancellation_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    refund_amount NUMERIC(10,2) NOT NULL CHECK (refund_amount >= 0.00),
    CONSTRAINT fk_cancellation_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);

-- ----------------------------------------------------------------------------
-- 9. PERFORMANCE INDEXING
-- ----------------------------------------------------------------------------
CREATE INDEX idx_flights_search ON flights(route_id, scheduled_departure, flight_status);
CREATE INDEX idx_tickets_booking ON tickets(booking_id);
CREATE INDEX idx_bookings_pnr ON bookings(booking_ref);
CREATE INDEX idx_seats_aircraft ON seats(aircraft_id);
CREATE INDEX idx_tickets_flight ON tickets(flight_id);

-- ============================================================================
-- COMPLEX BUSINESS RULE ENFORCEMENT VIA PROCEDURAL TRIGGERS
-- ============================================================================

-- RULE 1: Ensure allocated seat physically belongs to the aircraft deployed on that flight
CREATE OR REPLACE FUNCTION trg_verify_seat_compatibility()
RETURNS TRIGGER AS $$
DECLARE
    v_flight_aircraft INT;
    v_seat_aircraft INT;
BEGIN
    SELECT aircraft_id INTO v_flight_aircraft FROM flights WHERE flight_id = NEW.flight_id;
    SELECT aircraft_id INTO v_seat_aircraft FROM seats WHERE seat_id = NEW.seat_id;

    IF v_flight_aircraft IS NULL OR v_seat_aircraft IS NULL THEN
        RAISE EXCEPTION 'Referential Error: Flight % or Seat % does not exist.', NEW.flight_id, NEW.seat_id;
    END IF;

    IF v_flight_aircraft <> v_seat_aircraft THEN
        RAISE EXCEPTION 'Integrity Violation: Seat ID % belongs to Aircraft %, but Flight % is operated by Aircraft %.',
            NEW.seat_id, v_seat_aircraft, NEW.flight_id, v_flight_aircraft;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS check_seat_compatibility ON tickets;
CREATE TRIGGER check_seat_compatibility
BEFORE INSERT OR UPDATE ON tickets
FOR EACH ROW EXECUTE FUNCTION trg_verify_seat_compatibility();

-- RULE 2: Aircraft-Capacity Enforcement (Overbooking Prevention)
CREATE OR REPLACE FUNCTION trg_verify_aircraft_capacity()
RETURNS TRIGGER AS $$
DECLARE
    v_capacity INT;
    v_current_bookings INT;
BEGIN
    SELECT a.total_capacity INTO v_capacity
    FROM flights f
    JOIN aircraft a ON f.aircraft_id = a.aircraft_id
    WHERE f.flight_id = NEW.flight_id;

    SELECT COUNT(*) INTO v_current_bookings
    FROM tickets
    WHERE flight_id = NEW.flight_id AND ticket_status <> 'CANCELLED';

    IF v_current_bookings >= v_capacity THEN
        RAISE EXCEPTION 'Capacity Overrun: Flight % has reached maximum airframe capacity of % seats.',
            NEW.flight_id, v_capacity;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS check_capacity_limits ON tickets;
CREATE TRIGGER check_capacity_limits
BEFORE INSERT ON tickets
FOR EACH ROW EXECUTE FUNCTION trg_verify_aircraft_capacity();

-- RULE 3: Check-in Allowed ONLY for Confirmed Bookings with Active Tickets
CREATE OR REPLACE FUNCTION trg_verify_checkin_eligibility()
RETURNS TRIGGER AS $$
DECLARE
    v_b_status VARCHAR(15);
    v_t_status VARCHAR(15);
BEGIN
    SELECT b.booking_status, t.ticket_status 
    INTO v_b_status, v_t_status
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    WHERE t.ticket_id = NEW.ticket_id;

    IF v_b_status IS NULL THEN
        RAISE EXCEPTION 'Check-in Denied: Invalid ticket or booking linkage for Ticket ID %.', NEW.ticket_id;
    END IF;

    IF v_b_status <> 'CONFIRMED' THEN
        RAISE EXCEPTION 'Check-in Denied: Booking status is "%", expected "CONFIRMED".', v_b_status;
    END IF;

    IF v_t_status <> 'ISSUED' THEN
        RAISE EXCEPTION 'Check-in Denied: Ticket status is "%", expected "ISSUED".', v_t_status;
    END IF;

    -- Automatically transition ticket state to CHECKED_IN
    UPDATE tickets SET ticket_status = 'CHECKED_IN' WHERE ticket_id = NEW.ticket_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_checkin_eligibility ON checkins;
CREATE TRIGGER enforce_checkin_eligibility
BEFORE INSERT ON checkins
FOR EACH ROW EXECUTE FUNCTION trg_verify_checkin_eligibility();

-- RULE 4: Strict Refund Rule (Refund Amount cannot exceed original paid fare)
CREATE OR REPLACE FUNCTION trg_enforce_refund_bounds()
RETURNS TRIGGER AS $$
DECLARE
    v_fare NUMERIC(10,2);
    v_t_status VARCHAR(15);
BEGIN
    SELECT fare_amount, ticket_status 
    INTO v_fare, v_t_status 
    FROM tickets 
    WHERE ticket_id = NEW.ticket_id;

    IF v_fare IS NULL THEN
        RAISE EXCEPTION 'Cancellation Denied: Ticket ID % does not exist.', NEW.ticket_id;
    END IF;

    IF v_t_status = 'CANCELLED' THEN
        RAISE EXCEPTION 'Cancellation Denied: Ticket ID % is already marked CANCELLED.', NEW.ticket_id;
    END IF;

    IF NEW.refund_amount > v_fare THEN
        RAISE EXCEPTION 'Accounting Anomaly: Refund amount (₹%) cannot exceed ticket base fare (₹%).',
            NEW.refund_amount, v_fare;
    END IF;

    -- Automatically transition ticket state to CANCELLED
    UPDATE tickets SET ticket_status = 'CANCELLED' WHERE ticket_id = NEW.ticket_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS enforce_refund_policy ON cancellations;
CREATE TRIGGER enforce_refund_policy
BEFORE INSERT ON cancellations
FOR EACH ROW EXECUTE FUNCTION trg_enforce_refund_bounds();
-- ============================================================================
-- SEED DATA GENERATION (DML) - AIRLINE RESERVATION & FLIGHT OPERATIONS
-- ============================================================================

-- Clean out existing data safely
TRUNCATE TABLE cancellations, baggage, checkins, payments, tickets, 
               bookings, passengers, flights, seats, aircraft, routes, airports 
RESTART IDENTITY CASCADE;

-- ----------------------------------------------------------------------------
-- 1. Airports Registry (IATA Standards)
-- ----------------------------------------------------------------------------
INSERT INTO airports (airport_code, airport_name, city, country) VALUES
('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India'),
('BOM', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India'),
('BLR', 'Kempegowda International Airport', 'Bengaluru', 'India'),
('DXB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates');

-- ----------------------------------------------------------------------------
-- 2. Aircraft Fleet (Scaled for clean classroom demonstration)
-- ----------------------------------------------------------------------------
INSERT INTO aircraft (aircraft_id, model, total_capacity) VALUES
(1, 'Airbus A320neo', 6),
(2, 'Boeing 737-800', 4);

-- ----------------------------------------------------------------------------
-- 3. Physical Seat Inventory & Cabin Tiers
-- ----------------------------------------------------------------------------
INSERT INTO seats (seat_id, aircraft_id, seat_number, seat_class) VALUES
-- Aircraft 1 (Airbus A320neo - Capacity 6)
(1, 1, '1A', 'BUSINESS'),
(2, 1, '1B', 'BUSINESS'),
(3, 1, '2A', 'ECONOMY'),
(4, 1, '2B', 'ECONOMY'),
(5, 1, '3A', 'ECONOMY'),
(6, 1, '3B', 'ECONOMY'),
-- Aircraft 2 (Boeing 737-800 - Capacity 4)
(7, 2, '1A', 'BUSINESS'),
(8, 2, '1B', 'BUSINESS'),
(9, 2, '2A', 'ECONOMY'),
(10, 2, '2B', 'ECONOMY');

-- ----------------------------------------------------------------------------
-- 4. Routes (Origin-Destination Corridors)
-- ----------------------------------------------------------------------------
INSERT INTO routes (route_id, origin_airport, dest_airport, distance_km) VALUES
(1, 'DEL', 'BOM', 1148.00),
(2, 'BOM', 'BLR', 842.00),
(3, 'DEL', 'DXB', 2185.00);

-- ----------------------------------------------------------------------------
-- 5. Scheduled Flight Operations
-- ----------------------------------------------------------------------------
INSERT INTO flights (flight_id, route_id, aircraft_id, scheduled_departure, scheduled_arrival, flight_status) VALUES
(101, 1, 1, '2026-10-15 06:00:00', '2026-10-15 08:15:00', 'SCHEDULED'),
(102, 1, 1, '2026-10-15 18:00:00', '2026-10-15 20:15:00', 'ARRIVED'),
(103, 2, 2, '2026-10-16 09:30:00', '2026-10-16 11:15:00', 'SCHEDULED'),
(104, 3, 1, '2026-10-17 14:00:00', '2026-10-17 16:30:00', 'DELAYED');

-- ----------------------------------------------------------------------------
-- 6. Passenger Profiles
-- ----------------------------------------------------------------------------
INSERT INTO passengers (passenger_id, first_name, last_name, email, passport_number) VALUES
(1, 'Arjun', 'Mehta', 'arjun.m@example.com', 'A12345678'),
(2, 'Neha', 'Sharma', 'neha.s@example.com', 'B98765432'),
(3, 'Rohan', 'Verma', 'rohan.v@example.com', 'C54321987'),
(4, 'Priya', 'Nair', 'priya.n@example.com', 'D76543210'),
(5, 'Vikram', 'Rathore', 'vikram.r@example.com', 'E11223344'),
(6, 'Ananya', 'Iyer', 'ananya.i@example.com', 'F99887766');

-- ----------------------------------------------------------------------------
-- 7. Commercial Bookings
-- ----------------------------------------------------------------------------
INSERT INTO bookings (booking_id, booking_ref, passenger_id, booking_date, booking_status) VALUES
(1, 'PNR001', 1, '2026-10-01 10:15:00', 'CONFIRMED'),
(2, 'PNR002', 2, '2026-10-01 11:30:00', 'CONFIRMED'),
(3, 'PNR003', 3, '2026-10-02 09:00:00', 'CONFIRMED'),
(4, 'PNR004', 4, '2026-10-02 14:20:00', 'CONFIRMED'),
(5, 'PNR005', 5, '2026-10-03 16:45:00', 'CANCELLED'),
(6, 'PNR006', 6, '2026-10-04 11:00:00', 'CONFIRMED');

-- ----------------------------------------------------------------------------
-- 8. Payment Settlement Records
-- ----------------------------------------------------------------------------
INSERT INTO payments (payment_id, booking_id, amount_paid, payment_method, payment_status, payment_timestamp) VALUES
(1, 1, 8500.00, 'CREDIT_CARD', 'SUCCESS', '2026-10-01 10:16:00'),
(2, 2, 5200.00, 'UPI', 'SUCCESS', '2026-10-01 11:31:00'),
(3, 3, 5200.00, 'NET_BANKING', 'SUCCESS', '2026-10-02 09:02:00'),
(4, 4, 12000.00, 'CREDIT_CARD', 'SUCCESS', '2026-10-02 14:22:00'),
(5, 5, 8500.00, 'UPI', 'REFUNDED', '2026-10-03 16:46:00'),
(6, 6, 5200.00, 'UPI', 'SUCCESS', '2026-10-04 11:02:00');

-- ----------------------------------------------------------------------------
-- 9. Issued Tickets (Enforces Compatibility & Capacity Triggers)
-- ----------------------------------------------------------------------------
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) VALUES
(1, 1, 101, 1, 8500.00, 'ISSUED'),   -- Flight 101, Seat 1A (Business, Aircraft 1)
(2, 2, 101, 3, 5200.00, 'ISSUED'),   -- Flight 101, Seat 2A (Economy, Aircraft 1)
(3, 3, 101, 4, 5200.00, 'ISSUED'),   -- Flight 101, Seat 2B (Economy, Aircraft 1)
(4, 4, 104, 2, 12000.00, 'ISSUED'),  -- Flight 104, Seat 1B (Business, Aircraft 1)
(5, 5, 101, 5, 8500.00, 'ISSUED'),   -- Flight 101, Seat 3A (Economy, Aircraft 1) -> To be cancelled
(6, 6, 103, 9, 5200.00, 'ISSUED');   -- Flight 103, Seat 2A (Economy, Aircraft 2)

-- ----------------------------------------------------------------------------
-- 10. Check-ins & Gate Manifest Tokens (Trigger auto-updates ticket to CHECKED_IN)
-- ----------------------------------------------------------------------------
INSERT INTO checkins (checkin_id, ticket_id, checkin_time, boarding_pass) VALUES
(1, 1, '2026-10-15 04:30:00', 'BP-DELBOM-1A'),
(2, 2, '2026-10-15 04:45:00', 'BP-DELBOM-2A');

-- ----------------------------------------------------------------------------
-- 11. Baggage Custody Records (Weight & Excess Surcharge)
-- ----------------------------------------------------------------------------
INSERT INTO baggage (baggage_id, checkin_id, weight_kg, excess_fee) VALUES
(1, 1, 24.50, 1500.00), -- Excess over 15kg limit
(2, 1, 8.00, 0.00),     -- Second bag within limit
(3, 2, 14.20, 0.00);    -- Single bag within limit

-- ----------------------------------------------------------------------------
-- 12. Cancellations & Ledger Balancing (Trigger auto-updates ticket to CANCELLED)
-- ----------------------------------------------------------------------------
INSERT INTO cancellations (cancellation_id, ticket_id, cancellation_timestamp, refund_amount) VALUES
(1, 5, '2026-10-04 12:00:00', 6800.00); -- ₹1700 cancellation fee deducted from ₹8500 fare
-- ============================================================================
-- ANALYTICAL QUERIES, OPERATIONAL VIEWS & BUSINESS INTELLIGENCE REPORTS
-- Course Project: Airline Reservation and Flight Operations Management System
-- Review 2 Deliverable: Joins, Nested Queries, Aggregations, Window Functions & Views
-- ============================================================================

-- ----------------------------------------------------------------------------
-- REPORT 1: Real-Time Flight Manifest (Operational Dispatch View)
-- Joins: flights, routes, tickets, seats, bookings, passengers, checkins
-- Purpose: Complete passenger gate manifest for boarding & ground dispatch
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_flight_manifest AS
SELECT 
    f.flight_id,
    r.origin_airport || ' -> ' || r.dest_airport AS flight_corridor,
    f.scheduled_departure,
    s.seat_number,
    s.seat_class,
    p.first_name || ' ' || p.last_name AS passenger_name,
    p.passport_number,
    b.booking_ref,
    t.ticket_status,
    COALESCE(c.boarding_pass, 'NOT CHECKED-IN') AS boarding_pass_token
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN tickets t ON f.flight_id = t.flight_id
JOIN seats s ON t.seat_id = s.seat_id
JOIN bookings b ON t.booking_id = b.booking_id
JOIN passengers p ON b.passenger_id = p.passenger_id
LEFT JOIN checkins c ON t.ticket_id = c.ticket_id
WHERE t.ticket_status <> 'CANCELLED';

-- Execution Query for Flight 101:
-- SELECT * FROM view_flight_manifest WHERE flight_id = 101 ORDER BY seat_number;


-- ----------------------------------------------------------------------------
-- REPORT 2: Flight Occupancy & Yield Analytics (Capacity Utilization View)
-- Joins: flights, aircraft, tickets
-- Techniques: GROUP BY, COUNT, TYPE CASTING, CASE WHEN categorization
-- Purpose: Detect oversold, profitable, or low-yield under-performing flights
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW view_flight_occupancy AS
SELECT 
    f.flight_id,
    a.model AS airframe_type,
    a.total_capacity,
    COUNT(t.ticket_id) AS confirmed_passengers,
    ROUND((COUNT(t.ticket_id)::NUMERIC / a.total_capacity::NUMERIC) * 100, 2) AS occupancy_rate_pct,
    CASE 
        WHEN (COUNT(t.ticket_id)::NUMERIC / a.total_capacity::NUMERIC) >= 0.80 THEN 'OPTIMAL'
        WHEN (COUNT(t.ticket_id)::NUMERIC / a.total_capacity::NUMERIC) >= 0.50 THEN 'MODERATE'
        ELSE 'LOW_YIELD'
    END AS operational_efficiency
FROM flights f
JOIN aircraft a ON f.aircraft_id = a.aircraft_id
LEFT JOIN tickets t ON f.flight_id = t.flight_id AND t.ticket_status <> 'CANCELLED'
GROUP BY f.flight_id, a.model, a.total_capacity;

-- Execution Query:
-- SELECT * FROM view_flight_occupancy ORDER BY occupancy_rate_pct DESC;


-- ----------------------------------------------------------------------------
-- REPORT 3: Route Demand & High-Density Corridors (Revenue & Frequency Analysis)
-- Joins: routes, flights, tickets
-- Techniques: Multi-table outer joins, COUNT(DISTINCT), SUM, NULLIF, ORDER BY
-- Purpose: Evaluate passenger density and financial yield per flight corridor
-- ----------------------------------------------------------------------------
SELECT 
    r.route_id,
    r.origin_airport || ' -> ' || r.dest_airport AS corridor,
    r.distance_km,
    COUNT(DISTINCT f.flight_id) AS total_flights_operated,
    COUNT(t.ticket_id) AS total_passengers_carried,
    COALESCE(SUM(t.fare_amount), 0.00) AS total_gross_revenue,
    ROUND(COALESCE(SUM(t.fare_amount), 0.00) / NULLIF(COUNT(t.ticket_id), 0), 2) AS average_ticket_yield
FROM routes r
LEFT JOIN flights f ON r.route_id = f.route_id
LEFT JOIN tickets t ON f.flight_id = t.flight_id AND t.ticket_status <> 'CANCELLED'
GROUP BY r.route_id, r.origin_airport, r.dest_airport, r.distance_km
ORDER BY total_gross_revenue DESC;


-- ----------------------------------------------------------------------------
-- REPORT 4: Baggage Logistics & Excess Surcharge Audit (Payload Analysis)
-- Joins: flights, routes, tickets, checkins, baggage
-- Techniques: 5-table relational chain, SUM, AVG, COALESCE
-- Purpose: Monitor airframe cargo displacement and auxiliary baggage fees
-- ----------------------------------------------------------------------------
SELECT 
    f.flight_id,
    r.origin_airport || ' -> ' || r.dest_airport AS route,
    COUNT(b.baggage_id) AS total_checked_bags,
    COALESCE(SUM(b.weight_kg), 0.00) AS total_cargo_weight_kg,
    ROUND(COALESCE(AVG(b.weight_kg), 0.00), 2) AS avg_bag_weight_kg,
    COALESCE(SUM(b.excess_fee), 0.00) AS total_excess_baggage_revenue
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN tickets t ON f.flight_id = t.flight_id
JOIN checkins c ON t.ticket_id = c.ticket_id
JOIN baggage b ON c.checkin_id = b.checkin_id
GROUP BY f.flight_id, r.origin_airport, r.dest_airport
ORDER BY total_cargo_weight_kg DESC;


-- ----------------------------------------------------------------------------
-- REPORT 5: Cancellation, Attrition & Net Retention Metrics (Financial Audit)
-- Joins: cancellations, tickets
-- Techniques: Arithmetic aggregation, NULLIF, percentage calculation
-- Purpose: Track gross forfeited fares, refund leakages, and net retained penalty
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(c.cancellation_id) AS total_cancellations,
    SUM(t.fare_amount) AS gross_forfeited_fare,
    SUM(c.refund_amount) AS total_refunded_capital,
    SUM(t.fare_amount - c.refund_amount) AS net_cancellation_penalty_retained,
    ROUND((SUM(c.refund_amount) / NULLIF(SUM(t.fare_amount), 0)) * 100, 2) AS refund_ratio_pct
FROM cancellations c
JOIN tickets t ON c.ticket_id = t.ticket_id;


-- ----------------------------------------------------------------------------
-- REPORT 6: Flight Status & On-Time Performance (OTP) Audit (Subquery Analysis)
-- Techniques: Scalar nested subquery for population total percentage
-- Purpose: Audit operational schedule compliance and identify disruptions
-- ----------------------------------------------------------------------------
SELECT 
    flight_status,
    COUNT(*) AS total_segments,
    ROUND((COUNT(*)::NUMERIC / (SELECT COUNT(*) FROM flights)::NUMERIC) * 100, 2) AS pct_of_total_operations
FROM flights
GROUP BY flight_status
ORDER BY total_segments DESC;


-- ----------------------------------------------------------------------------
-- REPORT 7: Revenue Segmentation by Cabin Tier & Yield (Window Functions)
-- Joins: tickets, seats
-- Techniques: Analytic Window Function SUM(SUM(...)) OVER (), Pareto share
-- Purpose: Measure cabin class commercial performance & % contribution
-- ----------------------------------------------------------------------------
SELECT 
    s.seat_class,
    COUNT(t.ticket_id) AS tickets_sold,
    SUM(t.fare_amount) AS class_revenue,
    ROUND(AVG(t.fare_amount), 2) AS average_fare_per_class,
    ROUND(
        (SUM(t.fare_amount) / SUM(SUM(t.fare_amount)) OVER ()) * 100, 
        2
    ) AS contribution_percentage
FROM tickets t
JOIN seats s ON t.seat_id = s.seat_id
WHERE t.ticket_status <> 'CANCELLED'
GROUP BY s.seat_class
ORDER BY class_revenue DESC;
