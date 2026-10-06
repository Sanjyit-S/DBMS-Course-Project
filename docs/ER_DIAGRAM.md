# Entity-Relationship (ER) Architecture & Relational Topology

## 1. System Overview & Conceptual Model

The **Airline Reservation and Flight Operations Management System (ARFOM-DB)** models the end-to-end operational and commercial lifecycle of an enterprise airline. It establishes relational integrity across flight planning, physical airframe topology, dynamic seat allocations, passenger identity, bookings, financial settlements, departure control (check-in/baggage), and cancellation audits.

The database model is strictly decomposed to **Third Normal Form (3NF)** and enforces all physical airframe and commercial business rules at the database engine level.

---

## 2. Complete Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    AIRPORTS ||--o{ ROUTES : "origin_for"
    AIRPORTS ||--o{ ROUTES : "destination_for"
    ROUTES ||--o{ FLIGHTS : "scheduled_on"
    AIRCRAFT ||--o{ SEATS : "configures"
    AIRCRAFT ||--o{ FLIGHTS : "deploys"

    PASSENGERS ||--o{ BOOKINGS : "places"
    BOOKINGS ||--o{ PAYMENTS : "settled_by"
    BOOKINGS ||--o{ TICKETS : "contains"

    FLIGHTS ||--o{ TICKETS : "allocates"
    SEATS ||--o{ TICKETS : "occupies"

    TICKETS ||--o| CHECKINS : "authorizes"
    CHECKINS ||--o{ BAGGAGE : "custody_of"
    TICKETS ||--o| CANCELLATIONS : "revoked_by"

    AIRPORTS {
        char(3) airport_code PK
        varchar(100) airport_name
        varchar(50) city
        varchar(50) country
    }

    ROUTES {
        int route_id PK
        char(3) origin_airport FK
        char(3) dest_airport FK
        numeric distance_km
    }

    AIRCRAFT {
        int aircraft_id PK
        varchar(50) model
        int total_capacity
    }

    SEATS {
        int seat_id PK
        int aircraft_id FK
        varchar(4) seat_number
        varchar(15) seat_class
    }

    FLIGHTS {
        int flight_id PK
        int route_id FK
        int aircraft_id FK
        timestamp scheduled_departure
        timestamp scheduled_arrival
        varchar(15) flight_status
    }

    PASSENGERS {
        int passenger_id PK
        varchar(50) first_name
        varchar(50) last_name
        varchar(100) email UK
        varchar(20) passport_number UK
    }

    BOOKINGS {
        int booking_id PK
        char(6) booking_ref UK
        int passenger_id FK
        timestamp booking_date
        varchar(15) booking_status
    }

    TICKETS {
        int ticket_id PK
        int booking_id FK
        int flight_id FK
        int seat_id FK
        numeric fare_amount
        varchar(15) ticket_status
    }

    PAYMENTS {
        int payment_id PK
        int booking_id FK
        numeric amount_paid
        varchar(20) payment_method
        varchar(15) payment_status
        timestamp payment_timestamp
    }

    CHECKINS {
        int checkin_id PK
        int ticket_id FK, UK
        timestamp checkin_time
        varchar(20) boarding_pass UK
    }

    BAGGAGE {
        int baggage_id PK
        int checkin_id FK
        numeric weight_kg
        numeric excess_fee
    }

    CANCELLATIONS {
        int cancellation_id PK
        int ticket_id FK, UK
        timestamp cancellation_timestamp
        numeric refund_amount
    }
```

---

## 3. Structural Cardinalities & Relationship Mechanics

| Parent Entity | Child Entity | Relationship Cardinality | Participation | Relational Integrity Rule |
| :--- | :--- | :--- | :--- | :--- |
| **`airports`** | **`routes`** (Origin) | $1 : N$ (One-to-Many) | Mandatory | An airport can originate many flight corridors; a route must have exactly 1 origin airport (`ON DELETE RESTRICT`). |
| **`airports`** | **`routes`** (Dest) | $1 : N$ (One-to-Many) | Mandatory | An airport can terminate many corridors; a route must have exactly 1 destination airport (`ON DELETE RESTRICT`). `CHECK (origin <> dest)`. |
| **`routes`** | **`flights`** | $1 : N$ (One-to-Many) | Mandatory | A route corridor hosts recurring flight instances; each flight maps to exactly 1 defined route. |
| **`aircraft`** | **`seats`** | $1 : N$ (One-to-Many) | Mandatory | An airframe physically holds multiple seats. If an airframe is decommissioned, its seat topography cascades (`ON DELETE CASCADE`). |
| **`aircraft`** | **`flights`** | $1 : N$ (One-to-Many) | Mandatory | An aircraft is deployed across multiple scheduled flight legs; each flight leg requires 1 active airframe. |
| **`passengers`** | **`bookings`** | $1 : N$ (One-to-Many) | Optional | A customer account can place multiple commercial bookings over time. |
| **`bookings`** | **`tickets`** | $1 : N$ (One-to-Many) | Mandatory | A commercial booking order contains 1 or more passenger flight segment tickets (`ON DELETE CASCADE`). |
| **`bookings`** | **`payments`** | $1 : N$ (One-to-Many) | Mandatory | A booking transaction can be settled across 1 or more payment attempts/methods. |
| **`flights`** | **`tickets`** | $1 : N$ (One-to-Many) | Mandatory | A flight inventory contains multiple issued tickets up to its airframe capacity limit. |
| **`seats`** | **`tickets`** | $1 : N$ (One-to-Many) | Mandatory | A physical seat is allocated across distinct flights. Enforced unique constraint: `UNIQUE (flight_id, seat_id)`. |
| **`tickets`** | **`checkins`** | $1 : 1$ (One-to-One) | Optional | An active issued ticket produces at most **one** airport check-in and boarding pass token (`ticket_id UNIQUE`). |
| **`checkins`** | **`baggage`** | $1 : N$ (One-to-Many) | Optional | A checked-in passenger can register 0, 1, or multiple checked baggage items. |
| **`tickets`** | **`cancellations`** | $1 : 1$ (One-to-One) | Optional | A ticket can be revoked at most **once** (`ticket_id UNIQUE`). |

---

## 4. Key Relational Invariants Enforced in Topology

1. **Airframe Topology Decoupling**: Seats are bound to physical airframes (`aircraft_id`), not directly to flights. This allows an airline to change the physical aircraft deployed on a flight without redesigning seat maps.
2. **Double-Booking Prevention**: The composite constraint `UNIQUE (flight_id, seat_id)` physically prevents any seat on a flight from having more than one valid ticket allocated.
3. **Audit Ledger Immutability**: `payments`, `checkins`, and `cancellations` preserve permanent transactional historical states, satisfying financial and regulatory auditability.
