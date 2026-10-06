-- ============================================================================
-- MYSQL 8.0+ COMPATIBLE DDL & CONSTRAINT ARCHITECTURE (ARFOM-DB)
-- Fully compatible with MySQL 8.0 (InnoDB Engine with enforced CHECK & Triggers)
-- ============================================================================

DROP DATABASE IF EXISTS airline_db;
CREATE DATABASE airline_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE airline_db;

-- 1. AIRPORTS
CREATE TABLE airports (
    airport_code CHAR(3) PRIMARY KEY,
    airport_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- 2. ROUTES
CREATE TABLE routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    origin_airport CHAR(3) NOT NULL,
    dest_airport CHAR(3) NOT NULL,
    distance_km DECIMAL(7,2) NOT NULL CHECK (distance_km > 0.00),
    CONSTRAINT fk_route_origin FOREIGN KEY (origin_airport) REFERENCES airports(airport_code) ON DELETE RESTRICT,
    CONSTRAINT fk_route_dest FOREIGN KEY (dest_airport) REFERENCES airports(airport_code) ON DELETE RESTRICT,
    CONSTRAINT chk_distinct_airports CHECK (origin_airport <> dest_airport)
) ENGINE=InnoDB;

-- 3. AIRCRAFT
CREATE TABLE aircraft (
    aircraft_id INT AUTO_INCREMENT PRIMARY KEY,
    model VARCHAR(50) NOT NULL,
    total_capacity INT NOT NULL CHECK (total_capacity > 0)
) ENGINE=InnoDB;

-- 4. SEATS
CREATE TABLE seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    aircraft_id INT NOT NULL,
    seat_number VARCHAR(4) NOT NULL,
    seat_class VARCHAR(15) NOT NULL CHECK (seat_class IN ('ECONOMY', 'BUSINESS', 'FIRST')),
    CONSTRAINT fk_seat_aircraft FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id) ON DELETE CASCADE,
    CONSTRAINT uq_aircraft_seat UNIQUE (aircraft_id, seat_number)
) ENGINE=InnoDB;

-- 5. FLIGHTS
CREATE TABLE flights (
    flight_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    aircraft_id INT NOT NULL,
    scheduled_departure DATETIME NOT NULL,
    scheduled_arrival DATETIME NOT NULL,
    flight_status VARCHAR(15) NOT NULL DEFAULT 'SCHEDULED' 
        CHECK (flight_status IN ('SCHEDULED', 'BOARDING', 'DEPARTED', 'ARRIVED', 'CANCELLED', 'DELAYED')),
    CONSTRAINT fk_flight_route FOREIGN KEY (route_id) REFERENCES routes(route_id),
    CONSTRAINT fk_flight_aircraft FOREIGN KEY (aircraft_id) REFERENCES aircraft(aircraft_id),
    CONSTRAINT chk_flight_temporal_order CHECK (scheduled_arrival > scheduled_departure)
) ENGINE=InnoDB;

-- 6. PASSENGERS
CREATE TABLE passengers (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    passport_number VARCHAR(20) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- 7. BOOKINGS
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_ref CHAR(6) NOT NULL UNIQUE,
    passenger_id INT NOT NULL,
    booking_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    booking_status VARCHAR(15) NOT NULL DEFAULT 'CONFIRMED' 
        CHECK (booking_status IN ('CONFIRMED', 'PENDING', 'CANCELLED')),
    CONSTRAINT fk_booking_passenger FOREIGN KEY (passenger_id) REFERENCES passengers(passenger_id)
) ENGINE=InnoDB;

-- 8. TICKETS
CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    flight_id INT NOT NULL,
    seat_id INT NOT NULL,
    fare_amount DECIMAL(10,2) NOT NULL CHECK (fare_amount >= 0.00),
    ticket_status VARCHAR(15) NOT NULL DEFAULT 'ISSUED' 
        CHECK (ticket_status IN ('ISSUED', 'CHECKED_IN', 'CANCELLED')),
    CONSTRAINT fk_ticket_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT fk_ticket_flight FOREIGN KEY (flight_id) REFERENCES flights(flight_id),
    CONSTRAINT fk_ticket_seat FOREIGN KEY (seat_id) REFERENCES seats(seat_id),
    CONSTRAINT uq_flight_seat UNIQUE (flight_id, seat_id)
) ENGINE=InnoDB;

-- 9. PAYMENTS
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount_paid DECIMAL(10,2) NOT NULL CHECK (amount_paid > 0.00),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING')),
    payment_status VARCHAR(15) NOT NULL DEFAULT 'SUCCESS' CHECK (payment_status IN ('SUCCESS', 'FAILED', 'REFUNDED')),
    payment_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payment_booking FOREIGN KEY (booking_id) REFERENCES bookings(booking_id)
) ENGINE=InnoDB;

-- 10. CHECK-INS
CREATE TABLE checkins (
    checkin_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    checkin_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    boarding_pass VARCHAR(20) NOT NULL UNIQUE,
    CONSTRAINT fk_checkin_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
) ENGINE=InnoDB;

-- 11. BAGGAGE
CREATE TABLE baggage (
    baggage_id INT AUTO_INCREMENT PRIMARY KEY,
    checkin_id INT NOT NULL,
    weight_kg DECIMAL(5,2) NOT NULL CHECK (weight_kg >= 0.00),
    excess_fee DECIMAL(8,2) NOT NULL DEFAULT 0.00 CHECK (excess_fee >= 0.00),
    CONSTRAINT fk_baggage_checkin FOREIGN KEY (checkin_id) REFERENCES checkins(checkin_id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 12. CANCELLATIONS
CREATE TABLE cancellations (
    cancellation_id INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id INT NOT NULL UNIQUE,
    cancellation_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    refund_amount DECIMAL(10,2) NOT NULL CHECK (refund_amount >= 0.00),
    CONSTRAINT fk_cancellation_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
) ENGINE=InnoDB;

-- Performance Indexes
CREATE INDEX idx_flights_search ON flights(route_id, scheduled_departure, flight_status);
CREATE INDEX idx_tickets_booking ON tickets(booking_id);
CREATE INDEX idx_bookings_pnr ON bookings(booking_ref);

-- ============================================================================
-- MYSQL TRIGGERS (SIGNAL SQLSTATE '45000')
-- ============================================================================

DELIMITER $$

-- RULE 1: Seat Compatibility
CREATE TRIGGER trg_verify_seat_compatibility_mysql
BEFORE INSERT ON tickets
FOR EACH ROW
BEGIN
    DECLARE v_flight_aircraft INT;
    DECLARE v_seat_aircraft INT;

    SELECT aircraft_id INTO v_flight_aircraft FROM flights WHERE flight_id = NEW.flight_id;
    SELECT aircraft_id INTO v_seat_aircraft FROM seats WHERE seat_id = NEW.seat_id;

    IF v_flight_aircraft <> v_seat_aircraft THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Violation: Seat does not match flight airframe deployment.';
    END IF;
END $$

-- RULE 2: Aircraft-Capacity Limits
CREATE TRIGGER trg_verify_aircraft_capacity_mysql
BEFORE INSERT ON tickets
FOR EACH ROW
BEGIN
    DECLARE v_capacity INT;
    DECLARE v_current_bookings INT;

    SELECT a.total_capacity INTO v_capacity
    FROM flights f
    JOIN aircraft a ON f.aircraft_id = a.aircraft_id
    WHERE f.flight_id = NEW.flight_id;

    SELECT COUNT(*) INTO v_current_bookings
    FROM tickets
    WHERE flight_id = NEW.flight_id AND ticket_status <> 'CANCELLED';

    IF v_current_bookings >= v_capacity THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Capacity Overrun: Airframe capacity reached for this flight.';
    END IF;
END $$

-- RULE 3: Check-in Eligibility
CREATE TRIGGER trg_verify_checkin_eligibility_mysql
BEFORE INSERT ON checkins
FOR EACH ROW
BEGIN
    DECLARE v_b_status VARCHAR(15);
    DECLARE v_t_status VARCHAR(15);

    SELECT b.booking_status, t.ticket_status 
    INTO v_b_status, v_t_status
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    WHERE t.ticket_id = NEW.ticket_id;

    IF v_b_status <> 'CONFIRMED' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Check-in Denied: Booking status is not CONFIRMED.';
    END IF;

    IF v_t_status <> 'ISSUED' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Check-in Denied: Ticket is not in ISSUED state.';
    END IF;

    UPDATE tickets SET ticket_status = 'CHECKED_IN' WHERE ticket_id = NEW.ticket_id;
END $$

-- RULE 4: Strict Refund Limits
CREATE TRIGGER trg_enforce_refund_bounds_mysql
BEFORE INSERT ON cancellations
FOR EACH ROW
BEGIN
    DECLARE v_fare DECIMAL(10,2);

    SELECT fare_amount INTO v_fare FROM tickets WHERE ticket_id = NEW.ticket_id;

    IF NEW.refund_amount > v_fare THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Accounting Anomaly: Refund amount exceeds ticket base fare.';
    END IF;

    UPDATE tickets SET ticket_status = 'CANCELLED' WHERE ticket_id = NEW.ticket_id;
END $$

DELIMITER ;
