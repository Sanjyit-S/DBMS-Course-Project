-- ============================================================================
-- INTEGRITY CONSTRAINT & TRIGGER VALIDATION SUITE (NEGATIVE TESTS)
-- Designed to demonstrate live error interception during Review 2 Viva
-- Every statement below is intentionally invalid and MUST be rejected by the RDBMS.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- TEST 1: Rule 1 - "One seat per passenger per flight"
-- Attempt: Insert a second ticket allocating the already-booked Seat 1 on Flight 101.
-- Expected Result: Database rejects with Unique Constraint Violation on (flight_id, seat_id).
-- ----------------------------------------------------------------------------
-- EXPECTED ERROR: duplicate key value violates unique constraint "uq_flight_seat"
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) 
VALUES (999, 2, 101, 1, 8500.00, 'ISSUED');


-- ----------------------------------------------------------------------------
-- TEST 2: Rule 2 - "Aircraft-Capacity Enforcement"
-- Context: Flight 103 operates Boeing 737-800 with total_capacity = 4.
-- Flight 103 already has Ticket 6 booked.
-- Attempt: Book 4 more tickets to exceed the 4-seat physical capacity limit.
-- Expected Result: Trigger trg_verify_aircraft_capacity throws Capacity Overrun exception.
-- ----------------------------------------------------------------------------
-- Booking remaining available seats (Seats 8, 10 on Aircraft 2):
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) VALUES (701, 1, 103, 7, 5000.00, 'ISSUED');
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) VALUES (702, 2, 103, 8, 5000.00, 'ISSUED');
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) VALUES (703, 3, 103, 10, 5000.00, 'ISSUED');

-- Now Flight 103 has 4 active tickets (capacity reached).
-- This 5th insert MUST FAIL:
-- EXPECTED ERROR: Capacity Overrun: Flight 103 has reached maximum airframe capacity of 4 seats.
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) 
VALUES (704, 4, 103, 7, 5000.00, 'ISSUED');


-- ----------------------------------------------------------------------------
-- TEST 3: Rule 3 - "Non-negative baggage"
-- Attempt: Insert baggage with a negative weight (-5.50 kg).
-- Expected Result: Check constraint violation on check (weight_kg >= 0.00).
-- ----------------------------------------------------------------------------
-- EXPECTED ERROR: new row for relation "baggage" violates check constraint "baggage_weight_kg_check"
INSERT INTO baggage (baggage_id, checkin_id, weight_kg, excess_fee) 
VALUES (999, 1, -5.50, 0.00);


-- ----------------------------------------------------------------------------
-- TEST 4: Rule 4 - "Check-in Allowed ONLY for Confirmed Bookings with Active Tickets"
-- Attempt: Attempt to generate a check-in for Ticket 5 (which is CANCELLED).
-- Expected Result: Trigger trg_verify_checkin_eligibility throws Check-in Denied exception.
-- ----------------------------------------------------------------------------
-- EXPECTED ERROR: Check-in Denied: Ticket status is "CANCELLED", expected "ISSUED".
INSERT INTO checkins (checkin_id, ticket_id, boarding_pass) 
VALUES (999, 5, 'BP-ILLEGAL-99');


-- ----------------------------------------------------------------------------
-- TEST 5: Rule 5 - "Refund Rules (Refund Amount <= Ticket Base Fare)"
-- Attempt: Ticket 1 was purchased for ₹8,500.00. Attempt to issue a refund of ₹10,000.00.
-- Expected Result: Trigger trg_enforce_refund_bounds throws Accounting Anomaly exception.
-- ----------------------------------------------------------------------------
-- EXPECTED ERROR: Accounting Anomaly: Refund amount (₹10000.00) cannot exceed ticket base fare (₹8500.00).
INSERT INTO cancellations (cancellation_id, ticket_id, refund_amount) 
VALUES (999, 1, 10000.00);


-- ----------------------------------------------------------------------------
-- BONUS TEST 6: Physical Airframe Topology Compatibility
-- Attempt: Assign Seat 7 (which belongs to Aircraft 2) to Flight 101 (operated by Aircraft 1).
-- Expected Result: Trigger trg_verify_seat_compatibility throws Integrity Violation.
-- ----------------------------------------------------------------------------
-- EXPECTED ERROR: Integrity Violation: Seat ID 7 belongs to Aircraft 2, but Flight 101 is operated by Aircraft 1.
INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) 
VALUES (998, 1, 101, 7, 8500.00, 'ISSUED');
