# ARFOM-DB: PRESENTATION-II ON-THE-SPOT QUERY SOLUTIONS
**Course:** Database Management Systems (DBMS) &bull; Review 2  
**Learner:** Sanjyit Suresh Kumar (Roll No. **25WU0102243**) &bull; Section: **AIML Whales** (Serial #18)

> [!TIP]
> During Presentation-II, faculty typically asks the student to write an on-the-spot SQL query to test relational join concepts, aggregate functions (`GROUP BY`, `HAVING`), subqueries, and set operations. Below are the **12 most common viva query challenges** with verified solutions and explanations.

---

### Query 1: Top 3 Highest-Spending Passengers
**Question:** *"Write a query to find the top 3 passengers who spent the maximum total amount on confirmed flight tickets."*
```sql
SELECT 
    p.passenger_id, 
    p.first_name || ' ' || p.last_name AS passenger_name, 
    p.email, 
    SUM(t.fare_amount) AS total_spent
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
WHERE t.ticket_status != 'CANCELLED'
GROUP BY p.passenger_id
ORDER BY total_spent DESC
LIMIT 3;
```
* **Concepts Demonstrated:** Multi-table join, `WHERE` status filter, `SUM()` aggregate, `GROUP BY`, `ORDER BY DESC`, `LIMIT`.

---

### Query 2: Unoccupied / Available Seats on a Specific Flight
**Question:** *"Find the count and seat numbers of all physical seats that remain unbooked on flight 'AI-101'."*
```sql
SELECT s.seat_id, s.seat_number, s.seat_class
FROM seats s
JOIN flights f ON s.aircraft_id = f.aircraft_id
WHERE f.flight_number = 'AI-101'
  AND s.seat_id NOT IN (
      SELECT t.seat_id 
      FROM tickets t 
      WHERE t.flight_id = f.flight_id AND t.ticket_status != 'CANCELLED'
  )
ORDER BY s.seat_number;
```
* **Concepts Demonstrated:** Correlated Subquery / `NOT IN`, physical seat topology check.

---

### Query 3: Cargo Logistics & Surcharge Revenue per Flight
**Question:** *"Calculate the total baggage pieces, total baggage weight in kg, and total excess baggage fees collected per flight."*
```sql
SELECT 
    f.flight_number, 
    r.origin_airport || ' -> ' || r.dest_airport AS route,
    COUNT(b.baggage_id) AS total_bags, 
    COALESCE(SUM(b.weight_kg), 0) AS total_cargo_weight_kg, 
    COALESCE(SUM(b.excess_fee), 0) AS total_excess_collected
FROM flights f
JOIN routes r ON f.route_id = r.route_id
LEFT JOIN tickets t ON f.flight_id = t.flight_id
LEFT JOIN checkins c ON t.ticket_id = c.ticket_id
LEFT JOIN baggage b ON c.checkin_id = b.checkin_id
GROUP BY f.flight_id
ORDER BY total_cargo_weight_kg DESC;
```
* **Concepts Demonstrated:** 5-table `LEFT JOIN`, `COALESCE` for NULL safety, multi-metric aggregation.

---

### Query 4: Highest Grossing Route Corridor
**Question:** *"Which flight route generates the highest total commercial revenue from confirmed tickets?"*
```sql
SELECT 
    r.route_id, 
    r.origin_airport || ' -> ' || r.dest_airport AS corridor, 
    r.distance_km,
    COUNT(t.ticket_id) AS tickets_sold, 
    SUM(t.fare_amount) AS total_route_revenue,
    ROUND(AVG(t.fare_amount), 2) AS avg_ticket_price
FROM routes r
JOIN flights f ON r.route_id = f.route_id
JOIN tickets t ON f.flight_id = t.flight_id
WHERE t.ticket_status != 'CANCELLED'
GROUP BY r.route_id
ORDER BY total_route_revenue DESC
LIMIT 1;
```
* **Concepts Demonstrated:** Route aggregation, revenue ranking, arithmetic averaging.

---

### Query 5: Passengers with Business Class Bookings & Checked Luggage
**Question:** *"List all passengers who booked Business or First class and have checked in baggage exceeding 15 kg."*
```sql
SELECT DISTINCT 
    p.passenger_id, 
    p.first_name || ' ' || p.last_name AS passenger_name, 
    f.flight_number,
    s.seat_number,
    s.seat_class, 
    b.weight_kg
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
JOIN flights f ON t.flight_id = f.flight_id
JOIN seats s ON t.seat_id = s.seat_id
JOIN checkins c ON t.ticket_id = c.ticket_id
JOIN baggage b ON c.checkin_id = b.checkin_id
WHERE s.seat_class IN ('BUSINESS', 'FIRST') 
  AND b.weight_kg > 15.0
ORDER BY b.weight_kg DESC;
```
* **Concepts Demonstrated:** Complex 6-table join, `DISTINCT`, domain condition filtering.

---

### Query 6: Cancellation Margin & Retained Penalties
**Question:** *"Calculate the net penalty retained by the airline from cancelled tickets (gross fare minus refunded amount)."*
```sql
SELECT 
    COUNT(c.cancellation_id) AS total_cancelled_tickets,
    SUM(t.fare_amount) AS gross_fare_collected,
    SUM(c.refund_amount) AS total_refunded_to_passengers,
    SUM(t.fare_amount - c.refund_amount) AS net_retained_airline_penalty,
    ROUND(SUM(c.refund_amount) * 100.0 / SUM(t.fare_amount), 1) || '%' AS refund_payout_ratio
FROM cancellations c
JOIN tickets t ON c.ticket_id = t.ticket_id;
```
* **Concepts Demonstrated:** Relational arithmetic expressions, ratio formatting, financial ledger audit.

---

### Query 7: On-Time Performance (OTP) Status Distribution
**Question:** *"Display the flight status breakdown (SCHEDULED, DEPARTED, ARRIVED, DELAYED) with the percentage of total flights."*
```sql
SELECT 
    flight_status, 
    COUNT(*) AS total_flights, 
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM flights), 1) || '%' AS percentage_of_fleet
FROM flights 
GROUP BY flight_status 
ORDER BY total_flights DESC;
```
* **Concepts Demonstrated:** Scalar subquery inside SELECT projection, categorical grouping.

---

### Query 8: Dual-Hub Airports (Origin & Destination Connectivity)
**Question:** *"Find all airports that serve as BOTH the origin for at least 2 routes AND the destination for at least 2 routes."*
```sql
SELECT 
    a.airport_code, 
    a.airport_name, 
    a.city,
    (SELECT COUNT(*) FROM routes WHERE origin_airport = a.airport_code) AS outbound_route_count,
    (SELECT COUNT(*) FROM routes WHERE dest_airport = a.airport_code) AS inbound_route_count
FROM airports a
WHERE (SELECT COUNT(*) FROM routes WHERE origin_airport = a.airport_code) >= 2
  AND (SELECT COUNT(*) FROM routes WHERE dest_airport = a.airport_code) >= 2;
```
* **Concepts Demonstrated:** Correlated scalar subqueries in `SELECT` and `WHERE`, hub connectivity analysis.

---

### Query 9: Cabin Class Revenue & Yield Analysis
**Question:** *"Show the total revenue generated and average ticket price grouped by cabin class (ECONOMY, BUSINESS, FIRST)."*
```sql
SELECT 
    s.seat_class, 
    COUNT(t.ticket_id) AS tickets_sold, 
    SUM(t.fare_amount) AS total_revenue, 
    ROUND(AVG(t.fare_amount), 2) AS avg_fare
FROM tickets t 
JOIN seats s ON t.seat_id = s.seat_id 
WHERE t.ticket_status != 'CANCELLED' 
GROUP BY s.seat_class 
ORDER BY total_revenue DESC;
```
* **Concepts Demonstrated:** Dimensional grouping, cabin yield reporting.

---

### Query 10: Passengers on Delayed Flights
**Question:** *"Find the names and email addresses of all passengers scheduled on flights that are currently marked as 'DELAYED'."*
```sql
SELECT 
    p.passenger_id,
    p.first_name || ' ' || p.last_name AS passenger_name,
    p.email,
    f.flight_number,
    f.scheduled_departure
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
JOIN flights f ON t.flight_id = f.flight_id
WHERE f.flight_status = 'DELAYED' AND t.ticket_status != 'CANCELLED';
```
* **Concepts Demonstrated:** Operational notification projection, join with temporal filter.

---

### Query 11: Aircraft Utilization & Fleet Seat Capacity
**Question:** *"List all aircraft models with their total physical capacity and the number of active flight segments assigned to each."*
```sql
SELECT 
    a.aircraft_id,
    a.model,
    a.total_capacity,
    COUNT(f.flight_id) AS scheduled_flight_legs
FROM aircraft a
LEFT JOIN flights f ON a.aircraft_id = f.aircraft_id
GROUP BY a.aircraft_id
ORDER BY scheduled_flight_legs DESC;
```
* **Concepts Demonstrated:** Asset utilization, `LEFT JOIN` handling unassigned aircraft.

---

### Query 12: Finding Multi-Leg Bookings (PNRs with >1 Ticket)
**Question:** *"Find all booking orders (booking_ref) that contain more than 1 issued ticket."*
```sql
SELECT 
    b.booking_id,
    b.booking_ref,
    b.booking_date,
    COUNT(t.ticket_id) AS total_tickets_in_pnr
FROM bookings b
JOIN tickets t ON b.booking_id = t.booking_id
GROUP BY b.booking_id
HAVING COUNT(t.ticket_id) > 1
ORDER BY total_tickets_in_pnr DESC;
```
* **Concepts Demonstrated:** `HAVING` clause filtering on aggregate count.
