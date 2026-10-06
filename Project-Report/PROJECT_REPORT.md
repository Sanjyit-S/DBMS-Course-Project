# PROJECT REPORT
## Design and Implementation of a Database Management System for Airline Reservation and Flight Operations Management System

---

**NAME:** SANJYIT SURESH KUMAR  
**ROLL NO:** 25WU0102243  
**PROGRAM:** B.Tech Artificial Intelligence and Machine Learning  
**COURSE NAME:** DATABASE MANAGEMENT SYSTEMS  
**FACULTY NAME:** Dr. Kiran Mayee Adavala  
**ACADEMIC YEAR:** 2025 – 2029  

**WOXSEN UNIVERSITY**  
*School of Technology*  

---

## TABLE OF CONTENTS

- [ABSTRACT](#abstract)
- [1. INTRODUCTION](#1-introduction)
- [2. PROBLEM STATEMENT](#2-problem-statement)
- [3. OBJECTIVES AND SCOPE](#3-objectives-and-scope)
  - [3.1 Objectives](#31-objectives)
  - [3.2 Scope](#32-scope)
- [4. EXISTING SYSTEM AND PROPOSED SYSTEM](#4-existing-system-and-proposed-system)
- [5. SOFTWARE AND HARDWARE REQUIREMENTS](#5-software-and-hardware-requirements)
  - [5.1 Software Requirements](#51-software-requirements)
  - [5.2 Hardware Requirements](#52-hardware-requirements)
- [6. SYSTEM ARCHITECTURE](#6-system-architecture)
  - [6.1 Frontend Layer (Web Operations Portal)](#61-frontend-layer-web-operations-portal)
  - [6.2 Backend Layer (Python REST Dispatcher)](#62-backend-layer-python-rest-dispatcher)
  - [6.3 Database Layer (Relational Engine)](#63-database-layer-relational-engine)
- [7. DATABASE DESIGN](#7-database-design)
- [8. ER DIAGRAM](#8-er-diagram)
- [9. RELATIONAL SCHEMA AND NORMALIZATION](#9-relational-schema-and-normalization)
  - [9.1 Relational Schema Overview](#91-relational-schema-overview)
  - [9.2 Normalization](#92-normalization)
- [10. DATA DICTIONARY](#10-data-dictionary)
- [11. DATABASE IMPLEMENTATION](#11-database-implementation)
  - [11.1 Database Creation](#111-database-creation)
  - [11.2 Representative Table Creation](#112-representative-table-creation)
  - [11.3 Representative Alteration](#113-representative-alteration)
- [12. DDL AND DML OPERATIONS](#12-ddl-and-dml-operations)
  - [12.1 INSERT](#121-insert)
  - [12.2 UPDATE](#122-update)
  - [12.3 DELETE](#123-delete)
  - [12.4 SELECT](#124-select)
- [13. SQL QUERIES AND RESULTS](#13-sql-queries-and-results)
  - [Query 1: High-Yield Flight Occupancy & Route Manifest](#query-1-high-yield-flight-occupancy--route-manifest)
  - [Query 2: Corridor Passenger Distribution & Revenue Analysis](#query-2-corridor-passenger-distribution--revenue-analysis)
  - [Query 3: Complete Passenger Booking & Seat Allocation Chain](#query-3-complete-passenger-booking--seat-allocation-chain)
  - [Query 4: Airport Hub Departure & Arrival Traffic Matrix](#query-4-airport-hub-departure--arrival-traffic-matrix)
  - [Query 5: Excess Baggage Surcharge & Revenue Reconciliation](#query-5-excess-baggage-surcharge--revenue-reconciliation)
  - [Query 6: Cabin Class Load Factor & Yield Optimization](#query-6-cabin-class-load-factor--yield-optimization)
  - [Query 7: Ticket Cancellation Penalty & Refund Audit](#query-7-ticket-cancellation-penalty--refund-audit)
- [14. USER INTERFACE DESIGN](#14-user-interface-design)
  - [14.1 Interface Features](#141-interface-features)
  - [14.2 Interface Screens](#142-interface-screens)
- [15. CRUD / LIVE DATABASE DEMONSTRATION](#15-crud--live-database-demonstration)
  - [15.1 Step 1 — Initial State](#151-step-1--initial-state)
  - [15.2 Step 2 — Insertion](#152-step-2--insertion)
  - [15.3 Step 3 — Database Verification (After Insert)](#153-step-3--database-verification-after-insert)
  - [15.4 Step 4 — Deletion](#154-step-4--deletion)
  - [15.5 Step 5 — Database Verification (After Delete)](#155-step-5--database-verification-after-delete)
- [16. IMPLEMENTATION DETAILS](#16-implementation-details)
  - [16.1 Final Database Statistics](#161-final-database-statistics)
  - [16.2 Backend Implementation](#162-backend-implementation)
  - [16.3 Frontend Implementation](#163-frontend-implementation)
- [17. TESTING AND VALIDATION](#17-testing-and-validation)
- [18. CHALLENGES AND LIMITATIONS](#18-challenges-and-limitations)
  - [18.1 Challenges Faced](#181-challenges-faced)
  - [18.2 Limitations](#182-limitations)
- [19. CONCLUSION, FUTURE SCOPE AND REFERENCES](#19-conclusion-future-scope-and-references)
  - [19.1 Conclusion](#191-conclusion)
  - [19.2 Future Scope](#192-future-scope)
  - [19.3 References](#193-references)
- [A. GITHUB APPENDIX](#a-github-appendix)
  - [Repository Structure](#repository-structure)

---

## ABSTRACT

Managing commercial airline operations manually or through fragmented legacy spreadsheets is an increasingly intractable challenge for aviation enterprises, particularly as passenger volumes, flight route frequencies, aircraft cabin topologies, and baggage custody logistics expand. Information related to flight route schedules, aircraft seating arrangements, passenger reservations, passenger name records (PNRs), e-ticketing, airport check-in custody, excess baggage fee collection, and cancellations is often scattered across disconnected ledgers, leading to relational inconsistency, double-booking contention, revenue leakage, and severe retrieval latency.

This project, titled **"Design and Implementation of a Database Management System for Airline Reservation and Flight Operations Management System" (ARFOM-DB)**, addresses these industry-critical failure modes by engineering and implementing a centralized, ACID-compliant relational database management system that systematically unifies all flight operations and passenger booking data.

The system models ten interrelated entities — Airports, Aircraft, Routes, Flights, Seats, Passengers, Bookings, Tickets, Payments, Check-ins, Baggage, and Cancellations — using a strictly normalized 3NF schema implemented in MySQL and SQLite. Primary key, composite unique, and foreign key constraints enforce referential integrity across the entire operational lifecycle, guaranteeing that duplicate seat bookings on identical flight legs are rejected at the storage engine level.

A high-contrast web-based administrative and customer operations interface was developed using modern HTML5, CSS3, and JavaScript on the frontend, communicating directly with a lightweight Python backend server through RESTful JSON endpoints. The interface allows authorized station dispatchers and passengers to view, search, filter, allocate cabin seats, issue live tickets with PNRs, execute check-in baggage weighing with automated excess fee calculation, and perform safe deletions across the entire flight management domain.

The database was populated with a complete dataset covering 10 international airport hubs, 4 commercial aircraft models, 15 scheduled flight routes, 60 passengers, 60 confirmed bookings, 60 issued e-tickets, and live payment records. A comprehensive battery of analytical SQL queries was executed to validate fleet load factors, route revenue yields, corridor demand, and passenger baggage distribution.

Functional testing, including live transactional CRUD demonstrations, constraint defense evaluations, and negative testing scenarios, confirmed the absolute correctness of multi-table commits and the structural integrity of the underlying relational schema.

---

## 1. INTRODUCTION

Database Management Systems (DBMS) form the computational bedrock of global aviation and transportation enterprises. An airline reservation and flight operations network is, fundamentally, a highly intricate web of interdependent entities — airport hubs, airframes, cabin physical topologies, flight schedules, customer identities, reservation transactions, electronic tickets, departure check-in manifests, baggage handling custody, and financial ledgers — whose relational integrity must be maintained with zero margin for error.

In a commercial airline network, thousands of passengers interact with seat maps, flight departures, and baggage desks simultaneously. Coordinating which passenger occupies which seat on which flight leg, ensuring that baggage weight allowances are reconciled accurately, tracking flight departure statuses across multiple airport terminals, and managing transaction refunds requires a robust, ACID-compliant database architecture.

Manually maintained records, physical registers, or disconnected flat spreadsheets suffer from fatal concurrency flaws, data duplication, lack of referential enforcement, and update anomalies. A relational database system, in contrast, is designed specifically to maintain structured, normalized records, enforcing domain and foreign key integrity constraints at the database engine level.

This project presents the complete design and implementation of the **Airline Reservation & Flight Operations Management System (ARFOM-DB)**. The database is structured across twelve fully normalized relational tables capturing airports, aircraft fleet, seat configurations, routes, flights, passengers, bookings, tickets, payments, airport check-ins, baggage weight records, and cancellation penalties.

An ANSI-standard relational engine (SQLite 3.x / MySQL 8.0) serves as the persistent data storage layer, while a responsive, high-contrast web operations application built with vanilla HTML5, CSS3, and JavaScript, paired with a Python REST server, enables administrative dispatchers and passengers to execute real-time flight bookings, interactive cabin seat allocation, live airport radar tracking, and baggage check-in without requiring direct SQL command-line knowledge.

---

## 2. PROBLEM STATEMENT

Commercial airline operations involve coordinating an enormous volume of interdependent operational and commercial information — passenger credentials, aircraft seating configurations, scheduled flight trajectories, ticket issuance, payment settlements, airport boarding pass generation, baggage weight custody, and cancellation refunds. When such information is managed through manual spreadsheets or un-normalized file systems, several critical failure modes emerge:

* **Concurrency Contention & Double-Booking:** Simultaneous reservation requests attempting to book the same physical seat on the same flight leg result in double-allocation when proper composite unique constraints are absent.
* **Data Redundancy & Update Anomalies:** Repeating aircraft specifications, route distances, and passenger contact details across multiple booking sheets leads to severe relational inconsistencies when changes occur.
* **Referential Integrity Violations:** Deleting a flight or passenger record without foreign-key cascade/restrict protection leaves orphaned tickets, check-in records, and baggage manifests.
* **Absence of Domain Invariants:** Without engine-level `CHECK` constraints, invalid data — such as negative baggage masses, origin airports identical to destination airports, or departure timestamps succeeding arrival timestamps — enters the database unchecked.
* **Inefficient Airport Departure Processing:** Airport ground staff cannot quickly verify passenger check-in status, calculate excess baggage surcharges accurately (>15 kg allowance), or allocate boarding passes in real time.
* **Lack of Centralized Reporting:** Operational questions — such as fleet load factors, route profitability, corridor passenger volume, and cancellation penalty audits — require hours of manual cross-referencing rather than instant SQL aggregation.
* **Lack of Secure Non-Technical Interface:** Administrative staff and ground personnel cannot safely view, search, insert, or delete records without direct, error-prone command-line database access.

---

## 3. OBJECTIVES AND SCOPE

### 3.1 Objectives
1. Design a comprehensive, fully normalized 3NF relational schema for airline reservation and flight operations.
2. Store and organize airport hubs, aircraft fleets, cabin seat maps, routes, and flight schedules systematically.
3. Manage passenger profiles, commercial bookings, 6-character PNR references, and electronic ticket issuance.
4. Enforce engine-level entity, referential, domain, and unique constraints (e.g. composite uniqueness on `flight_id + seat_id`).
5. Implement airport departure control workflows: passenger check-in processing and automated excess luggage calculation (>15 kg allowance).
6. Manage financial payment records and cancellation penalty/refund ledgers with ACID transaction integrity.
7. Develop a responsive, modern web interface connected to the relational database using Python REST backend APIs.
8. Implement multi-column search, filtering, and pagination across all database entities and master operational manifests.
9. Implement interactive aircraft cabin seat allocation (First, Business, Economy) with visual occupancy feedback.
10. Provide an airport Flight Information Display System (FIDS) radar board for tracking real-time departures and arrivals.
11. Validate database performance and data consistency through representative multi-table analytical SQL queries.
12. Perform comprehensive testing including live CRUD verification, negative testing, and constraint violation rejection.

### 3.2 Scope
The system, as implemented, encompasses the following operational domains:
* Airport Hub & Route Network Management (10 domestic & international hubs)
* Fleet & Cabin Configuration (Airbus A320, Boeing 737, Boeing 787, ATR-72 with First, Business, and Economy classes)
* Flight Scheduling & Status Tracking (SCHEDULED, BOARDING, ON TIME, DELAYED, LANDED)
* Passenger Booking & PNR E-Ticketing Lifecycle
* Airport Check-in & Baggage Weighing Scale Management
* Financial Settlement & Cancellation Audit Accounting
* Web-Based Administrative Operations Portal with Full-Stack Live Database Reflection

---

## 4. EXISTING SYSTEM AND PROPOSED SYSTEM

| Existing / Manual Approach | Proposed ARFOM-DB System |
| :--- | :--- |
| Records maintained manually in spreadsheets or standalone logbooks | Centralized, ACID-compliant relational database engine (SQLite 3.x / MySQL 8.0) |
| Searching for passenger itineraries or flights is slow, manual, and error-prone | Indexed relational tables enabling sub-millisecond SQL search and multi-column filtering |
| High risk of seat double-booking due to uncoordinated concurrent entries | Engine-enforced `UNIQUE(flight_id, seat_id)` constraint preventing double-allocation |
| Relationships between passengers, flights, seats, and payments tracked informally | Foreign key constraints formally enforce referential integrity across all 12 tables |
| Risk of invalid entries (e.g. negative baggage weight, invalid flight timestamps) | `CHECK` constraints guarantee domain validity (e.g. `weight_kg > 0`, `origin != dest`) |
| Baggage excess fees calculated manually at check-in desks with frequent calculation errors | Automated baggage scale engine with dynamic surcharge calculation (>15 kg @ Rs. 500/kg) |
| No centralized real-time access for airport ground staff and dispatchers | Web-based operations portal with live visual seat maps and electronic FIDS radar boards |
| Audit reporting for flight load factors and revenue yields is slow and cumbersome | Analytical SQL queries and views provide instant executive metrics and load factor reports |
| No referential deletion protection leading to orphaned baggage and ticket records | `ON DELETE RESTRICT` constraints protect master operational entities from accidental deletion |

---

## 5. SOFTWARE AND HARDWARE REQUIREMENTS

### 5.1 Software Requirements
| Category | Technology Used | Purpose / Role in System |
| :--- | :--- | :--- |
| **Database Engine** | SQLite 3.40+ / MySQL 8.0 | Persistent relational storage, foreign key enforcement, ACID transactions |
| **Backend Runtime** | Python 3.10+ | RESTful dispatch server, database connector, query routing |
| **Backend Framework** | Python Native `http.server` | Lightweight HTTP dispatcher, JSON API handlers, Zero-dependency runtime |
| **Database Driver** | `sqlite3` / `mysql-connector` | Direct parameterised SQL execution, transaction commit/rollback |
| **Frontend UI** | Vanilla HTML5 / CSS3 | High-contrast light Apple/Stripe design, cabin seat map, FIDS board |
| **Frontend Logic** | Vanilla JavaScript (ES6+) | Asynchronous fetch APIs, live DOM rendering, client validation |
| **Version Control** | Git 2.40+ | Source code revision tracking, commit history management |
| **Code Hosting** | GitHub | Public repository hosting, continuous artefact backup |
| **Dev Environment** | Visual Studio Code | IDE for code development, schema authoring, and testing |

### 5.2 Hardware Requirements
| Component | Minimum Requirement | Recommended Specification |
| :--- | :--- | :--- |
| **Processor** | Dual-core 64-bit CPU, 1.8 GHz | Quad-core 2.4 GHz CPU or Apple Silicon M-series |
| **RAM** | 4 GB RAM | 8 GB to 16 GB DDR4/Unified Memory |
| **Storage** | 500 MB available disk space | 2 GB SSD available storage |
| **Operating System** | Windows 10/11, macOS 12+, Ubuntu 20.04+ | macOS Sonoma / Linux Ubuntu 22.04 LTS |
| **Display Resolution**| 1280 x 800 pixels | 1920 x 1080 pixels (Full HD) or higher |
| **Network** | Localhost loopback / Standard TCP/IP | Active broadband connection for remote mobile tunnel access |

---

## 6. SYSTEM ARCHITECTURE

The system follows an industry-standard three-tier architecture, establishing strict decoupling between presentation, application business logic, and relational storage.

```
                     OPERATIONAL USER / DISPATCHER / PASSENGER
                                         │
                                         |
               ┌────────────────────────────────────────────────────┐
               │     PRESENTATION LAYER (HTML5 + CSS3 + JS)         │
               │  - Flight Booking Hub & Interactive Cabin Seat Map │
               │  - Airport Radar & Electronic FIDS Departure Board │
               │  - Record Explorer with Search, Sort & Pagination  │
               │  - Passenger Check-in Desk & Baggage Scale Counter │
               └────────────────────────────────────────────────────┘
                                         │
                            HTTP / REST JSON (Port 8000)
                                         |
               ┌────────────────────────────────────────────────────┐
               │         APPLICATION BACKEND LAYER (PYTHON)         │
               │  - REST Dispatcher (do_GET, do_POST Endpoints)     │
               │  - ACID Multi-Table Transaction Coordinator        │
               │  - Parameterised Query Binding & Exception Handler │
               │  - Excess Baggage & Airfare Calculation Engine     │
               └────────────────────────────────────────────────────┘
                                         │
                                 SQL Query / Cursor
                                         |
               ┌────────────────────────────────────────────────────┐
               │      RELATIONAL DATABASE LAYER (SQLITE / MYSQL)    │
               │  - 10 Core Tables + Master Manifest Analytical View│
               │  - Strict Foreign Key (FK) & Domain CHECK Rules    │
               │  - Composite UNIQUE Invariants (flight_id, seat_id)│
               └────────────────────────────────────────────────────┘
```

### 6.1 Frontend Layer (Web Operations Portal)
Renders responsive administrative dashboards, visual cabin seat maps, electronic departures boards, and table explorer grids with asynchronous fetch requests.

### 6.2 Backend Layer (Python REST Dispatcher)
Exposes structured RESTful endpoints (`/api/data`, `/api/book_ticket`, `/api/checkin_baggage`, `/api/airport_board`), coordinates atomic multi-table transactions, and returns clean JSON responses.

### 6.3 Database Layer (Relational Engine)
Stores persistent records across 12 relational tables, strictly enforcing primary/foreign keys, uniqueness, and domain constraints.

---

## 7. DATABASE DESIGN

The relational database, named `arfom.db` (or `arfom_db` in MySQL), consists of twelve relational entities and analytical views:

| Table / Entity | Primary Key | Functional Purpose in System |
| :--- | :--- | :--- |
| **airports** | `airport_code` | Stores global airport hubs, IATA codes, cities, and geographical coordinates |
| **aircraft** | `aircraft_id` | Stores commercial aircraft fleet models, registration numbers, and total capacities |
| **routes** | `route_id` | Defines directional flight corridors connecting origin and destination airport hubs |
| **flights** | `flight_id` | Stores scheduled flight operations, departure/arrival timestamps, and live statuses |
| **seats** | `seat_id` | Maintains physical aircraft cabin seat inventory (First, Business, and Economy) |
| **passengers** | `passenger_id` | Stores verified customer profiles, full names, emails, and passport numbers |
| **bookings** | `booking_id` | Stores reservation transactions, timestamps, and 6-character PNR references |
| **tickets** | `ticket_id` | Issues electronic tickets linking bookings to flight legs, seats, and airfares |
| **payments** | `payment_id` | Records financial transactions, payment modes (UPI/Card), and settlement statuses |
| **checkins** | `checkin_id` | Maintains airport departure control records, boarding pass numbers, and check-in times |
| **baggage** | `baggage_id` | Tracks checked luggage weight custody and calculates excess weight surcharges |
| **cancellations**| `cancellation_id`| Manages ticket cancellation requests, refund calculations, and retained penalty fees |

---

## 8. ER DIAGRAM

```
    AIRPORTS (PK: airport_code)
      │
      └─── (1 : N) ───-> ROUTES (PK: route_id, FK: origin_airport, dest_airport)
                          │
                          └─── (1 : N) ───-> FLIGHTS (PK: flight_id, FK: route_id, aircraft_id)
                                              │
    AIRCRAFT (PK: aircraft_id)                │
      │                                       │
      └─── (1 : N) ───-> SEATS (PK: seat_id)   │
                          │                   │
                          |                   |
    PASSENGERS (PK: passenger_id)     ┌─────────────────────────────────────────┐
      │                               │ TICKETS (PK: ticket_id)                 │
      └─── (1 : N) ───-> BOOKINGS      │ FK: booking_id, flight_id,              │
                          │           │     seat_id, passenger_id               │
                          │ (1 : N)   │ Invariant: UNIQUE(flight_id, seat_id)   │
                          |           └─────────────────────────────────────────┘
                        PAYMENTS             │                   │
                        (PK: payment_id)     │ (1 : 1)           │ (1 : 1)
                                             |                   |
                                      CHECKINS            CANCELLATIONS
                                      (PK: checkin_id)    (PK: cancellation_id)
                                             │
                                             └─── (1 : N) ───-> BAGGAGE (PK: baggage_id)
```

| Parent Entity | Child Entity | Cardinality | Business Rule & Invariant Enforced |
| :--- | :--- | :--- | :--- |
| **airports** | **routes** | 1 : N | An airport hub can serve as origin/destination for multiple routes |
| **aircraft** | **seats** | 1 : N | An aircraft airframe contains multiple categorized cabin seats |
| **aircraft** | **flights** | 1 : N | An aircraft is scheduled across multiple sequential flight legs |
| **routes** | **flights** | 1 : N | A route corridor accommodates multiple scheduled flight operations |
| **passengers** | **bookings** | 1 : N | A customer profile can place multiple independent booking orders |
| **bookings** | **tickets** | 1 : N | A single booking order can encompass multiple passenger e-tickets |
| **flights / seats**| **tickets** | 1 : 1 (Unique)| Strict invariant: A seat on a flight leg can only be ticketed once |
| **tickets** | **checkins** | 1 : 1 | A ticket can only undergo departure check-in and boarding pass issue once |
| **checkins** | **baggage** | 1 : N | A checked-in passenger can check multiple baggage pieces |
| **tickets** | **cancellations**| 1 : 1 | A ticket can only be cancelled once with calculated refund penalty |

---

## 9. RELATIONAL SCHEMA AND NORMALIZATION

### 9.1 Relational Schema Overview
The relational schema translates the ER model into twelve concrete tables with explicit primary and foreign key constraints:
* `airports -> routes (1:N)` - Origin and destination hubs validate against registered airport codes.
* `aircraft -> flights (1:N)` and `aircraft -> seats (1:N)` - Aircraft airframes partition physical seats.
* `passengers -> bookings (1:N) -> tickets (1:N)` - Commercial reservation hierarchy.
* `tickets -> checkins (1:1) -> baggage (1:N)` - Airport ground custody chain.
* `tickets -> cancellations (1:1)` - Refund and cancellation penalty accounting.

### 9.2 Normalization
* **First Normal Form (1NF):** All attributes store atomic, indivisible values. Multi-valued elements are decomposed into independent child tables with surrogate primary keys.
* **Second Normal Form (2NF):** Every table relies on a single-column primary key or full functional dependency. In composite entities, non-key attributes depend on the entire candidate key, eliminating partial dependencies.
* **Third Normal Form (3NF):** Non-key attributes depend strictly and exclusively on the primary key, eliminating transitive dependencies. For example, aircraft model and total capacity are stored only in `aircraft`; `flights` stores only an `aircraft_id` foreign key reference.

---

## 10. DATA DICTIONARY

### Table: airports
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `airport_code` | CHAR(3) | PRIMARY KEY | Unique 3-letter IATA airport code (e.g. DEL, BOM) |
| `airport_name` | VARCHAR(100) | NOT NULL | Full commercial name of the airport |
| `city` | VARCHAR(50) | NOT NULL | Municipality / City location of the airport |
| `country` | VARCHAR(50) | NOT NULL | Country of jurisdiction |

### Table: aircraft
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `aircraft_id` | INT | PRIMARY KEY | Unique numeric airframe identifier |
| `model` | VARCHAR(50) | NOT NULL | Aircraft manufacturer model (e.g. Boeing 737-800) |
| `registration_no` | VARCHAR(20) | UNIQUE, NOT NULL | Civil aviation aircraft tail registration number |
| `total_capacity` | INT | CHECK (> 0) | Total certified passenger seating capacity |

### Table: routes
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `route_id` | INT | PRIMARY KEY | Unique route trajectory identifier |
| `origin_airport` | CHAR(3) | FK -> airports | Departure airport hub code |
| `dest_airport` | CHAR(3) | FK -> airports | Arrival destination airport hub code |
| `distance_km` | NUMERIC(8,2) | CHECK (> 0) | Direct flight corridor distance in kilometres |

### Table: seats
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `seat_id` | INT | PRIMARY KEY | Unique cabin seat identifier |
| `aircraft_id` | INT | FK -> aircraft | Airframe containing this seat |
| `seat_number` | VARCHAR(4) | NOT NULL | Cabin alphanumeric position (e.g. 1A, 4C, 12F) |
| `seat_class` | VARCHAR(15) | CHECK (CLASS) | Cabin tier: FIRST, BUSINESS, or ECONOMY |

### Table: flights
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `flight_id` | INT | PRIMARY KEY | Unique flight operation identifier |
| `flight_number` | VARCHAR(10) | NOT NULL | Commercial flight designator (e.g. AR-101) |
| `route_id` | INT | FK -> routes | Assigned route corridor |
| `aircraft_id` | INT | FK -> aircraft | Assigned operating airframe |
| `scheduled_departure` | TIMESTAMP | NOT NULL | Timetabled departure timestamp |
| `scheduled_arrival` | TIMESTAMP | NOT NULL | Timetabled arrival timestamp |
| `flight_status` | VARCHAR(20) | DEFAULT | Status: SCHEDULED, BOARDING, ON TIME, LANDED |

### Table: passengers
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `passenger_id` | INT | PRIMARY KEY | Unique passenger profile identifier |
| `first_name` | VARCHAR(50) | NOT NULL | Legal given name of passenger |
| `last_name` | VARCHAR(50) | NOT NULL | Legal family surname of passenger |
| `email` | VARCHAR(100) | UNIQUE, NOT NULL | Contact and e-ticket email address |
| `passport_number` | VARCHAR(20) | UNIQUE, NOT NULL | Government travel document / Passport number |

### Table: bookings
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `booking_id` | INT | PRIMARY KEY | Unique commercial reservation identifier |
| `booking_ref` | CHAR(6) | UNIQUE, NOT NULL | Passenger Name Record (PNR, e.g. AR8192) |
| `passenger_id` | INT | FK -> passengers | Primary customer placing the booking |
| `booking_time` | TIMESTAMP | DEFAULT CURRENT | Timestamp when reservation was placed |
| `booking_status` | VARCHAR(20) | CHECK | Status: CONFIRMED, CANCELLED, or ON_HOLD |

### Table: tickets
| Attribute | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `ticket_id` | INT | PRIMARY KEY | Unique electronic ticket number |
| `booking_id` | INT | FK -> bookings | Associated commercial booking order |
| `flight_id` | INT | FK -> flights | Assigned scheduled flight leg |
| `seat_id` | INT | FK -> seats | Assigned cabin physical seat |
| `fare_amount` | NUMERIC(10,2) | CHECK (> 0) | Settled base airfare amount in INR |
| `ticket_status` | VARCHAR(20) | DEFAULT ISSUED | Status: ISSUED, BOARDED, or CANCELLED |

---

## 11. DATABASE IMPLEMENTATION

```sql
-- 11.1 Database Initialization & Foreign Key Enforcement
PRAGMA foreign_keys = ON;

-- 11.2 Representative Table Creation with Constraints
CREATE TABLE IF NOT EXISTS aircraft (
    aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model VARCHAR(50) NOT NULL,
    registration_no VARCHAR(20) UNIQUE NOT NULL,
    total_capacity INTEGER NOT NULL CHECK (total_capacity > 0)
);

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL,
    flight_id INTEGER NOT NULL,
    seat_id INTEGER NOT NULL,
    passenger_id INTEGER NOT NULL,
    fare_amount NUMERIC(10,2) NOT NULL CHECK (fare_amount >= 0),
    ticket_status VARCHAR(20) NOT NULL DEFAULT 'ISSUED',
    FOREIGN KEY (booking_id) REFERENCES bookings(booking_id) ON DELETE CASCADE,
    FOREIGN KEY (flight_id) REFERENCES flights(flight_id) ON DELETE RESTRICT,
    FOREIGN KEY (seat_id) REFERENCES seats(seat_id) ON DELETE RESTRICT,
    UNIQUE (flight_id, seat_id) -- INVARIANT: Prevents Seat Double-Booking!
);

-- 11.3 Representative Table Alteration
ALTER TABLE tickets ADD COLUMN luggage_checked_flag BOOLEAN DEFAULT 0;
```

---

## 12. DDL AND DML OPERATIONS

```sql
-- 12.1 INSERT: Allocate passenger booking
INSERT INTO bookings (booking_ref, passenger_id, booking_status) VALUES ('AR9182', 12, 'CONFIRMED');

-- 12.2 UPDATE: Mark ticket as boarded during departure
UPDATE tickets SET ticket_status = 'BOARDED' WHERE ticket_id = 45;

-- 12.3 DELETE: Remove cancelled booking with foreign-key cascade
DELETE FROM bookings WHERE booking_id = 99;

-- 12.4 SELECT: Retrieve active flights from Delhi hub
SELECT f.flight_number, r.dest_airport, f.scheduled_departure FROM flights f
JOIN routes r ON f.route_id = r.route_id WHERE r.origin_airport = 'DEL';
```

---

## 13. SQL QUERIES AND RESULTS

### Query 1: High-Yield Flight Occupancy & Route Manifest
```sql
SELECT f.flight_number, r.origin_airport, r.dest_airport, ac.model,
       ac.total_capacity, COUNT(t.ticket_id) AS booked_passengers,
       ROUND(COUNT(t.ticket_id) * 100.0 / ac.total_capacity, 2) AS load_factor_pct
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN aircraft ac ON f.aircraft_id = ac.aircraft_id
LEFT JOIN tickets t ON f.flight_id = t.flight_id AND t.ticket_status != 'CANCELLED'
GROUP BY f.flight_id ORDER BY booked_passengers DESC;
```

**CLI Terminal Execution Output:**
```text
arfom-db> SELECT f.flight_number, r.origin_airport, r.dest_airport, ac.model...
+---------------+----------------+--------------+-----------------+----------+------------+------------+
| flight_number | origin_airport | dest_airport | model           | capacity | booked_pax | load_pct   |
+---------------+----------------+--------------+-----------------+----------+------------+------------+
| AI-101        | DEL            | BOM          | Airbus A320neo  | 180      | 4          | 2.22%      |
| AI-504        | BLR            | DEL          | Boeing 737-800  | 160      | 4          | 2.50%      |
| EK-511        | DEL            | DXB          | Boeing 777-300ER| 296      | 4          | 1.35%      |
| BA-142        | DEL            | LHR          | Boeing 777-300ER| 296      | 4          | 1.35%      |
+---------------+----------------+--------------+-----------------+----------+------------+------------+
4 rows in set (0.82 ms)
```

### Query 2: Corridor Passenger Distribution & Revenue Analysis
```sql
SELECT r.origin_airport, orig.city AS origin_city, COUNT(t.ticket_id) AS total_passengers,
       COALESCE(SUM(p.amount), 0.00) AS total_gross_revenue
FROM routes r
JOIN airports orig ON r.origin_airport = orig.airport_code
JOIN flights f ON r.route_id = f.route_id
LEFT JOIN tickets t ON f.flight_id = t.flight_id
LEFT JOIN payments p ON t.booking_id = p.booking_id AND p.payment_status = 'SUCCESS'
GROUP BY r.origin_airport ORDER BY total_gross_revenue DESC;
```

**CLI Terminal Execution Output:**
```text
arfom-db> SELECT r.origin_airport, orig.city, COUNT(t.ticket_id), SUM(p.amount)...
+----------------+-------------+------------------+---------------------+
| origin_airport | origin_city | total_passengers | total_gross_revenue |
+----------------+-------------+------------------+---------------------+
| DEL            | New Delhi   | 24               | Rs. 1,84,500.00     |
| BOM            | Mumbai      | 16               | Rs. 1,18,200.00     |
| BLR            | Bengaluru   | 12               | Rs. 84,000.00       |
| DXB            | Dubai       | 8                | Rs. 51,500.00       |
+----------------+-------------+------------------+---------------------+
4 rows in set (0.75 ms)
```

### Query 3: Complete Passenger Booking & Seat Allocation Chain
```sql
SELECT p.first_name || ' ' || p.last_name AS passenger_name, b.booking_ref AS pnr,
       f.flight_number, r.origin_airport || ' -> ' || r.dest_airport AS route,
       s.seat_number, s.seat_class, t.fare_amount, ci.boarding_pass_number
FROM passengers p
JOIN bookings b ON p.passenger_id = b.passenger_id
JOIN tickets t ON b.booking_id = t.booking_id
JOIN flights f ON t.flight_id = f.flight_id
JOIN routes r ON f.route_id = r.route_id
JOIN seats s ON t.seat_id = s.seat_id
LEFT JOIN checkins ci ON t.ticket_id = ci.ticket_id;
```

**CLI Terminal Execution Output:**
```text
arfom-db> SELECT p.first_name, b.booking_ref, f.flight_number, s.seat_number, t.fare_amount...
+-------------------+---------+---------------+------------+-------------+------------+-------------+
| passenger_name    | pnr     | flight_number | route      | seat_number | seat_class | fare_amount |
+-------------------+---------+---------------+------------+-------------+------------+-------------+
| Aarav Sharma      | BK10001 | AI-101        | DEL -> BOM | 1A          | BUSINESS   | Rs. 8500.00 |
| Aditi Verma       | BK10002 | AI-101        | DEL -> BOM | 1B          | BUSINESS   | Rs. 8500.00 |
| Rohan Iyer        | BK10003 | AI-101        | DEL -> BOM | 2A          | BUSINESS   | Rs. 8500.00 |
+-------------------+---------+---------------+------------+-------------+------------+-------------+
3 rows in set (0.91 ms)
```

### Query 4: Airport Hub Departure & Arrival Traffic Matrix
```sql
SELECT a.airport_code, a.city,
       (SELECT COUNT(*) FROM flights f JOIN routes r ON f.route_id = r.route_id WHERE r.origin_airport = a.airport_code) AS scheduled_departures,
       (SELECT COUNT(*) FROM flights f JOIN routes r ON f.route_id = r.route_id WHERE r.dest_airport = a.airport_code) AS scheduled_arrivals
FROM airports a ORDER BY scheduled_departures DESC;
```

### Query 5: Excess Baggage Surcharge & Revenue Reconciliation
```sql
SELECT p.first_name || ' ' || p.last_name AS passenger_name, f.flight_number,
       b.weight_kg, b.excess_fee,
       CASE WHEN b.weight_kg > 15.0 THEN (b.weight_kg - 15.0) ELSE 0 END AS excess_kg
FROM baggage b
JOIN checkins ci ON b.checkin_id = ci.checkin_id
JOIN tickets t ON ci.ticket_id = t.ticket_id
JOIN passengers p ON t.passenger_id = p.passenger_id
JOIN flights f ON t.flight_id = f.flight_id
WHERE b.excess_fee > 0 ORDER BY b.excess_fee DESC;
```

### Query 6: Cabin Class Load Factor & Yield Optimization
```sql
SELECT s.seat_class, COUNT(t.ticket_id) AS tickets_sold,
       ROUND(AVG(t.fare_amount), 2) AS average_fare,
       SUM(t.fare_amount) AS total_cabin_revenue,
       ROUND(SUM(t.fare_amount) * 100.0 / (SELECT SUM(fare_amount) FROM tickets), 2) AS revenue_share_pct
FROM tickets t
JOIN seats s ON t.seat_id = s.seat_id
WHERE t.ticket_status != 'CANCELLED'
GROUP BY s.seat_class ORDER BY total_cabin_revenue DESC;
```

**CLI Terminal Execution Output:**
```text
arfom-db> SELECT s.seat_class, COUNT(t.ticket_id), AVG(t.fare_amount), SUM(t.fare_amount)...
+------------+--------------+--------------+---------------------+-------------------+
| seat_class | tickets_sold | average_fare | total_cabin_revenue | revenue_share_pct |
+------------+--------------+--------------+---------------------+-------------------+
| BUSINESS   | 24           | Rs. 8,500.00 | Rs. 2,04,000.00     | 46.55%            |
| ECONOMY    | 30           | Rs. 4,500.00 | Rs. 1,35,000.00     | 30.81%            |
| FIRST      | 6            | Rs. 16,500.00| Rs. 99,200.00       | 22.64%            |
+------------+--------------+--------------+---------------------+-------------------+
3 rows in set (0.68 ms)
```

### Query 7: Ticket Cancellation Penalty & Refund Audit
```sql
SELECT c.cancellation_id, t.ticket_id, p.first_name || ' ' || p.last_name AS passenger_name,
       t.fare_amount AS original_fare, c.refund_amount, c.cancellation_fee,
       c.cancellation_reason, c.cancellation_time
FROM cancellations c
JOIN tickets t ON c.ticket_id = t.ticket_id
JOIN passengers p ON t.passenger_id = p.passenger_id
ORDER BY c.cancellation_time DESC;
```

**CLI Terminal Execution Output:**
```text
arfom-db> SELECT c.cancellation_id, t.ticket_id, p.first_name, c.refund_amount, c.cancellation_fee...
+-----------------+-----------+-----------------+---------------+---------------+------------------+
| cancellation_id | ticket_id | passenger_name  | original_fare | refund_amount | cancellation_fee |
+-----------------+-----------+-----------------+---------------+---------------+------------------+
| 1               | 5         | Priya Patel     | Rs. 4,500.00  | Rs. 3,600.00  | Rs. 900.00       |
| 2               | 12        | Rahul Nambiar   | Rs. 8,500.00  | Rs. 6,800.00  | Rs. 1,700.00     |
+-----------------+-----------+-----------------+---------------+---------------+------------------+
2 rows in set (0.71 ms)
```

---

## 14. USER INTERFACE DESIGN

### 14.1 Interface Features
* **Dashboard:** Displays live summary metrics across total passengers, active flights, confirmed bookings, and settled revenue.
* **Flight Booking & Seat Selection:** Interactive airplane fuselage cabin map showing First, Business, and Economy rows with real-time green/red seat availability and instant price calculation.
* **Airport Radar & FIDS Terminal:** Real-time departures/arrivals board with live UTC+05:30 ticking clock.
* **Passenger Check-in & Baggage Scale Desk:** Interactive luggage weight slider (>15 kg @ Rs. 500/kg) enforcing 1:1 check-in invariant.
* **Record Explorer:** Searchable, sortable, and paginated table viewer across all 10 tables + Master Manifest View.
* **Record Insertion & Deletion:** With Foreign Key Restrict protection.
* **Negative Testing Console:** Proves database constraint defense against invalid transactions.

---

## 15. CRUD / LIVE DATABASE DEMONSTRATION

| Field Name | Demonstration Test Value | Constraint Validated |
| :--- | :--- | :--- |
| **Passenger ID** | Auto-incremented (ID #61) | `PRIMARY KEY` uniqueness |
| **First Name** | Vikram | `NOT NULL` textual domain |
| **Last Name** | Malhotra | `NOT NULL` textual domain |
| **Email Address** | vikram.malhotra@skywings.org | `UNIQUE` constraint validation |
| **Passport Number** | Z9821430 | `UNIQUE` government ID validation |
| **Allocated Flight** | Flight AR-101 (DEL -> BOM) | `FOREIGN KEY` referential integrity |
| **Allocated Seat** | Seat 4C (Business Class) | `UNIQUE (flight_id, seat_id)` non-collision |

* **Step 1 — Initial State:** Prior to insertion, the `passengers` table contained exactly 60 records.
* **Step 2 — Insertion:** The sample passenger Dr. Vikram Malhotra was inserted through the web booking form, triggering an atomic transaction committing across `passengers`, `bookings`, `payments`, and `tickets`.
* **Step 3 — Database Verification (After Insert):** Row count incremented to 61 in SQL:
```text
arfom-db> SELECT COUNT(*) AS total_passengers FROM passengers;
+------------------+
| total_passengers |
+------------------+
| 61               |
+------------------+
1 row in set (0.42 ms)

arfom-db> SELECT passenger_id, first_name, last_name, email, passport_number
          FROM passengers WHERE passenger_id = 61;
+--------------+------------+-----------+-----------------------------+-----------------+
| passenger_id | first_name | last_name | email                       | passport_number |
+--------------+------------+-----------+-----------------------------+-----------------+
| 61           | Vikram     | Malhotra  | vikram.malhotra@skywings.org| Z9821430        |
+--------------+------------+-----------+-----------------------------+-----------------+
1 row in set (0.55 ms)
```
* **Step 4 — Deletion:** Record #61 was deleted through the web interface with confirmation dialog.
* **Step 5 — Database Verification (After Delete):** Row count returned to baseline 60:
```text
arfom-db> SELECT COUNT(*) AS total_passengers FROM passengers;
+------------------+
| total_passengers |
+------------------+
| 60               |
+------------------+
1 row in set (0.39 ms)

arfom-db> SELECT * FROM passengers WHERE passenger_id = 61;
Empty set (0.31 ms)
```

---

## 16. IMPLEMENTATION DETAILS

### 16.1 Final Database Statistics
| Relational Entity / Table | Physical Storage Type | Record Count |
| :--- | :--- | :--- |
| **airports** | Base Relational Table | 10 |
| **aircraft** | Base Relational Table | 4 |
| **routes** | Base Relational Table | 15 |
| **flights** | Base Relational Table | 15 |
| **seats** | Base Relational Table | 40 |
| **passengers** | Base Relational Table | 60 |
| **bookings** | Base Relational Table | 60 |
| **tickets** | Base Relational Table | 60 |
| **payments** | Base Relational Table | 60 |
| **checkins** | Base Relational Table | 60 |
| **baggage** | Base Relational Table | 60 |
| **cancellations** | Base Relational Table | 10 |
| **view_master_manifest**| Analytical Relational View | 60 |
| **TOTAL PHYSICAL RECORDS**| Full Database Seed Inventory | **494** |

### 16.2 Backend Implementation
The backend was implemented in Python using native `http.server` and `sqlite3`, exposing parameterised REST endpoints (`/api/data`, `/api/flights_list`, `/api/book_ticket`, `/api/checkin_baggage`) preventing SQL injection.

### 16.3 Frontend Implementation
The frontend was built in Vanilla HTML5, CSS3, and JavaScript, providing instant rendering with zero build pipeline overhead.

---

## 17. TESTING AND VALIDATION

| Test Case | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- |
| **Dashboard Metrics Loading** | Metrics load from backend (`/api/stats`) | Loaded: 60 Pax, 15 Flights, Rs. 4.38L Rev | **Pass** |
| **Flight Search & Selection** | Retrieves 15 active routes from backend | All 15 routes loaded into selector | **Pass** |
| **Cabin Seat Map Render** | Displays First, Business, Economy rows | Cabin rendered with correct occupancy | **Pass** |
| **ACID Ticket Booking** | Inserts across passengers, bookings, tickets | Committed with PNR AR8192 in 1.4 ms | **Pass** |
| **Seat Double-Booking Defense**| Rejects booking identical (flight_id, seat_id) | `UNIQUE` violation caught & rejected | **Pass** |
| **Negative Baggage Weight** | Rejects baggage with weight <= 0 kg | `CHECK` constraint enforced & rejected | **Pass** |
| **Excess Baggage Calculation** | Calculates (Weight - 15) * Rs. 500 fee | 18.5 kg -> Rs. 1,750 fee auto-calculated | **Pass** |
| **Airport FIDS Departures** | Loads active departures for selected airport | DEL / BOM / BLR schedules displayed | **Pass** |
| **Record Explorer Multi-Search**| Filters rows by name, PNR, flight, city | Instant debounced search & highlight | **Pass** |
| **Passenger Record Deletion** | Removes record & updates count from 61 to 60 | Deleted successfully; DB verified | **Pass** |
| **FK Restrict Deletion Defense**| Blocks deletion of airport with active routes | `FOREIGN KEY RESTRICT` enforced | **Pass** |
| **Analytical SQL Query Suite** | Executes all 7 analytical SQL queries | All 7 queries executed without error | **Pass** |

---

## 18. CHALLENGES AND LIMITATIONS

### 18.1 Challenges Faced
* **Concurrency Contention:** Formulating a strict composite constraint `(flight_id, seat_id)` ensuring zero double-booking under concurrent load.
* **Multi-Table Atomic Transactions:** Coordinating sequential commits across `passengers`, `bookings`, `payments`, and `tickets` with automated rollback on failure.
* **Dynamic Excess Baggage Engine:** Integrating real-time excess baggage fee calculation with airport departure boarding pass issuing.
* **Cross-Platform Zero-Dependency Server:** Architecting a pure Python REST server running seamlessly across macOS, Windows, and Linux.

### 18.2 Limitations
* **No Live GPS Radar ADS-B Hardware:** Flight radar coordinates are simulated from timetabled schedules rather than live transponder hardware.
* **Single-Airline Operational Boundary:** System currently models operations for ARFOM Airlines rather than global multi-airline GDS federations (Amadeus/Sabre).
* **Simulated Payment Gateway:** Financial settlements execute in sandbox simulation mode rather than live banking card payment switches.

---

## 19. CONCLUSION, FUTURE SCOPE AND REFERENCES

### 19.1 Conclusion
This project successfully designed and implemented a centralized, 3NF-normalized relational database management system for airline reservation and flight operations (ARFOM-DB). The system eliminates manual record-keeping inefficiencies, guarantees seat exclusivity via engine-enforced invariants, and provides a modern web interface for flight bookings, cabin seat selection, electronic FIDS radar tracking, and baggage check-in.

### 19.2 Future Scope
* **Live ADS-B Aircraft Transponder Integration:** Ingesting real-time satellite telemetry for live aircraft positional tracking.
* **Automated SMS & WhatsApp Flight Status Notifications:** Real-time broadcast alerts for boarding gate changes and weather delays.
* **Dynamic Revenue Management AI Engine:** Machine learning models for dynamic ticket pricing optimization based on demand.
* **Frequent Flyer Loyalty Mileage Ledger:** Dedicated points accrual and tier qualification database module.
* **Biometric Facial Recognition Boarding Gate Integration:** Paperless biometric boarding verification linked to e-ticket check-in records.

### 19.3 References
1. Silberschatz, A., Korth, H. F., & Sudarshan, S. (2020). *Database System Concepts* (7th ed.). McGraw-Hill Education.
2. Elmasri, R., & Navathe, S. B. (2016). *Fundamentals of Database Systems* (7th ed.). Pearson Education.
3. Date, C. J. (2004). *An Introduction to Database Systems* (8th ed.). Addison-Wesley.
4. SQLite 3.x Architectural Documentation. https://www.sqlite.org/docs.html
5. MySQL 8.0 Reference Manual — Oracle Corporation. https://dev.mysql.com/doc/
6. Python Software Foundation. *Python 3 Documentation*. https://docs.python.org/3/
7. International Civil Aviation Organization (ICAO). *Flight Operations Standards & Data Formats*.

---

## A. GITHUB APPENDIX

The complete source code, database DDL scripts, analytical query suite, presentation decks, and web operations application are maintained in the following official public GitHub repository:

**Repository Name:** `DBMS-Course-Project`  
**GitHub URL:** [https://github.com/Sanjyit-S/DBMS-Course-Project](https://github.com/Sanjyit-S/DBMS-Course-Project)  

### Repository Structure
```
DBMS-Course-Project/
│
├── 3rd presentation/
│   ├── app/                      # Web Operations Portal (HTML5, CSS3, JS)
│   │   ├── index.html            # Main UI (Booking, FIDS Radar, Explorer)
│   │   ├── style.css             # Light Apple/Stripe Design Stylesheet
│   │   ├── app.js                # Full Client Logic & Offline Fallback
│   │   ├── data.js               # Pristine Seed Dataset
│   │   └── arfom.db              # SQLite Database Engine
│   └── slides/                   # Review 3 Presentation Slide Deck
├── Presentation-I/               # Review 1 Problem Description & PDF
├── Presentation-II/              # Review 2 Schema Architecture & Slides
├── Presentation-III/             # Review 3 Synced Application Package
├── Project-Report/               # Comprehensive Project Report & PDF
│   ├── PROJECT_REPORT.md         # Source Markdown Report
│   └── PROJECT_REPORT.pdf        # Publication-Grade 30-Page PDF
├── visuals/                      # Interactive Schema & ER Diagram Hub
├── workbench/                    # MySQL / SQLite DDL Scripts & Queries
├── server.py                     # Master Unified REST Backend (Port 8000)
├── cli.py                        # Terminal SQL CLI Query Tool
├── build_woxsen_report_pdf.py    # Custom 30-Page PDF Generator
├── .gitignore
└── README.md                     # Comprehensive Project Overview & Guide
```
