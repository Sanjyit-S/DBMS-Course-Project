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
