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
