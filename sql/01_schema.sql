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
