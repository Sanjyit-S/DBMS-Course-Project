# Formal Relational Data Dictionary

The data dictionary below outlines all 12 normalized relational entities, column specifications, physical data types, constraint rules, referential integrity actions, and operational business logic.

---

## 1. `airports`
*Master registry of international and domestic civil airports.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `airport_code` | `CHAR(3)` | **PK**, NOT NULL | - | Standard IATA 3-letter uppercase identifier (e.g., 'DEL', 'BOM'). |
| `airport_name` | `VARCHAR(100)` | NOT NULL | - | Official aerodrome facility name. |
| `city` | `VARCHAR(50)` | NOT NULL | - | Metropolitan area served by the airport. |
| `country` | `VARCHAR(50)` | NOT NULL | - | Sovereign nation of airport jurisdiction. |

---

## 2. `routes`
*Master catalog of authorized point-to-point flight corridors.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `route_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Immutable surrogate sequence identifier for flight corridor. |
| `origin_airport` | `CHAR(3)` | **FK**, NOT NULL | `REFERENCES airports(airport_code) ON DELETE RESTRICT` | Departure terminal code. |
| `dest_airport` | `CHAR(3)` | **FK**, NOT NULL | `REFERENCES airports(airport_code) ON DELETE RESTRICT` | Destination terminal code. |
| `distance_km` | `NUMERIC(7,2)` | NOT NULL, CHECK (`> 0.00`) | - | Great-circle flight corridor distance in kilometers. |
| *Table Check* | - | `CHECK (origin_airport <> dest_airport)` | - | Self-loop prevention: Flight must connect distinct stations. |

---

## 3. `aircraft`
*Airframe registry defining physical fleet units and macro capacities.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `aircraft_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Unique system airframe hardware identifier. |
| `model` | `VARCHAR(50)` | NOT NULL | - | Manufacturer equipment designation (e.g., 'Airbus A320neo'). |
| `total_capacity` | `INT` | NOT NULL, CHECK (`> 0`) | - | Maximum physical certified seat configuration limit. |

---

## 4. `seats`
*Physical airframe topology and cabin class segmentation.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `seat_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Unique physical seat hardware identifier. |
| `aircraft_id` | `INT` | **FK**, NOT NULL | `REFERENCES aircraft(aircraft_id) ON DELETE CASCADE` | Physical airframe ownership. |
| `seat_number` | `VARCHAR(4)` | NOT NULL | - | Row and letter label (e.g., '12A', '1B'). |
| `seat_class` | `VARCHAR(15)` | NOT NULL, CHECK (`IN ('ECONOMY', 'BUSINESS', 'FIRST')`) | - | Service cabin tier determining tariff and amenities. |
| *Table Unique* | `(aircraft_id, seat_number)` | **UNIQUE** | - | Airframe seat uniqueness: An airframe cannot duplicate a seat label. |

---

## 5. `flights`
*Scheduled operational flight segments executed by deployed airframes.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `flight_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Operational segment identifier. |
| `route_id` | `INT` | **FK**, NOT NULL | `REFERENCES routes(route_id)` | Route profile assigned to this flight leg. |
| `aircraft_id` | `INT` | **FK**, NOT NULL | `REFERENCES aircraft(aircraft_id)` | Physical airframe deployed on this segment. |
| `scheduled_departure` | `TIMESTAMP` | NOT NULL | - | Scheduled off-block departure time. |
| `scheduled_arrival` | `TIMESTAMP` | NOT NULL | - | Scheduled in-block arrival time. |
| `flight_status` | `VARCHAR(15)` | NOT NULL, DEFAULT `'SCHEDULED'` | CHECK (`IN ('SCHEDULED', 'BOARDING', 'DEPARTED', 'ARRIVED', 'CANCELLED', 'DELAYED')`) | Operational flight state machine token. |
| *Table Check* | - | `CHECK (scheduled_arrival > scheduled_departure)` | - | Temporal integrity: Flight arrival must succeed departure. |

---

## 6. `passengers`
*Identity ledger and contact endpoints for customers.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `passenger_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Unique customer identity record sequence. |
| `first_name` | `VARCHAR(50)` | NOT NULL | - | Customer legal given name. |
| `last_name` | `VARCHAR(50)` | NOT NULL | - | Customer legal family name. |
| `email` | `VARCHAR(100)` | **UNIQUE**, NOT NULL | - | Primary communication & digital ticketing handle. |
| `passport_number` | `VARCHAR(20)` | **UNIQUE**, NOT NULL | - | Government-issued identification travel credential. |

---

## 7. `bookings`
*Commercial transaction orders placed by primary account holders.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `booking_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Internal order ledger identifier. |
| `booking_ref` | `CHAR(6)` | **UNIQUE**, NOT NULL | - | Passenger Name Record (PNR) token (e.g., 'PNR001'). |
| `passenger_id` | `INT` | **FK**, NOT NULL | `REFERENCES passengers(passenger_id)` | Primary account holder placing commercial order. |
| `booking_date` | `TIMESTAMP` | NOT NULL, DEFAULT `CURRENT_TIMESTAMP` | - | Audit timestamp of reservation creation. |
| `booking_status` | `VARCHAR(15)` | NOT NULL, DEFAULT `'CONFIRMED'` | CHECK (`IN ('CONFIRMED', 'PENDING', 'CANCELLED')`) | Commercial lifecycle state. |

---

## 8. `tickets`
*Coupons issued for physical seat allocation on operational segments.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `ticket_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Unique electronic ticket coupon identifier. |
| `booking_id` | `INT` | **FK**, NOT NULL | `REFERENCES bookings(booking_id) ON DELETE CASCADE` | Parent commercial booking transaction. |
| `flight_id` | `INT` | **FK**, NOT NULL | `REFERENCES flights(flight_id)` | Scheduled flight segment allocated. |
| `seat_id` | `INT` | **FK**, NOT NULL | `REFERENCES seats(seat_id)` | Physical seat hardware unit allocated. |
| `fare_amount` | `NUMERIC(10,2)` | NOT NULL, CHECK (`>= 0.00`) | - | Point-in-time contracted tariff paid. |
| `ticket_status` | `VARCHAR(15)` | NOT NULL, DEFAULT `'ISSUED'` | CHECK (`IN ('ISSUED', 'CHECKED_IN', 'CANCELLED')`) | Flight segment ticket lifecycle state. |
| *Table Unique* | `(flight_id, seat_id)` | **UNIQUE** | - | **Core Invariant**: Exactly one passenger per seat per flight. |

---

## 9. `payments`
*Financial settlement ledger auditing monetary transactions.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `payment_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Financial settlement journal sequence identifier. |
| `booking_id` | `INT` | **FK**, NOT NULL | `REFERENCES bookings(booking_id)` | Associated commercial booking order. |
| `amount_paid` | `NUMERIC(10,2)` | NOT NULL, CHECK (`> 0.00`) | - | Monetary value settled in Indian Rupees (₹). |
| `payment_method` | `VARCHAR(20)` | NOT NULL | CHECK (`IN ('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING')`) | Transaction clearance gateway channel. |
| `payment_status` | `VARCHAR(15)` | NOT NULL, DEFAULT `'SUCCESS'` | CHECK (`IN ('SUCCESS', 'FAILED', 'REFUNDED')`) | Financial settlement clearance status. |
| `payment_timestamp` | `TIMESTAMP` | NOT NULL, DEFAULT `CURRENT_TIMESTAMP` | - | Point-in-time timestamp of payment transaction. |

---

## 10. `checkins`
*Airport departure control system (DCS) custody and gate tokens.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `checkin_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Unique airport departure control sequence. |
| `ticket_id` | `INT` | **FK**, **UNIQUE**, NOT NULL | `REFERENCES tickets(ticket_id)` | 1:1 Linkage: Exactly one check-in allowed per issued ticket. |
| `checkin_time` | `TIMESTAMP` | NOT NULL, DEFAULT `CURRENT_TIMESTAMP` | - | Security gate clearance timestamp. |
| `boarding_pass` | `VARCHAR(20)` | **UNIQUE**, NOT NULL | - | Optical barcode token for automated boarding gate access. |

---

## 11. `baggage`
*Hold cargo weight verification and excess baggage surcharges.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `baggage_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Unique IATA luggage bag-tag custody sequence. |
| `checkin_id` | `INT` | **FK**, NOT NULL | `REFERENCES checkins(checkin_id) ON DELETE CASCADE` | Owning departure check-in record. |
| `weight_kg` | `NUMERIC(5,2)` | NOT NULL, CHECK (`>= 0.00`) | - | Scale weight reading; strictly non-negative. |
| `excess_fee` | `NUMERIC(8,2)` | NOT NULL, DEFAULT `0.00`, CHECK (`>= 0.00`) | - | Tariff penalty applied for payload over baseline allowance. |

---

## 12. `cancellations`
*Ticket revocation audit ledger and audited refund return capital.*

| Column Name | Data Type | Constraint | Referential Action | Description & Invariant Rule |
| :--- | :--- | :--- | :--- | :--- |
| `cancellation_id` | `INT` / `SERIAL` | **PK**, AUTO_INCREMENT | - | Audit trail sequence for segment revocation. |
| `ticket_id` | `INT` | **FK**, **UNIQUE**, NOT NULL | `REFERENCES tickets(ticket_id)` | 1:1 Linkage: At most one cancellation audit per ticket. |
| `cancellation_timestamp` | `TIMESTAMP` | NOT NULL, DEFAULT `CURRENT_TIMESTAMP` | - | Timestamp of passenger revocation request. |
| `refund_amount` | `NUMERIC(10,2)` | NOT NULL, CHECK (`>= 0.00`) | - | Value disbursed back; must not exceed original base fare. |
