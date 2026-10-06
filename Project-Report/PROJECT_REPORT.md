# COURSE PROJECT REPORT
## Airline Reservation and Flight Operations Management System (ARFOM-DB)

**Course:** Database Management Systems (DBMS)  
**Learner Name:** Sanjyit Suresh Kumar  
**Roll Number:** 25WU0102243  
**Section:** AIML Whales (Merged with AIML Panthers &bull; Project Title #18)  
**Faculty In-Charge:** Department of Computer Science & Engineering / Artificial Intelligence & Machine Learning  
**Academic Year:** 2026&ndash;2027  

---

## 1. Cover Page Details
* **Project Title:** Design and Implementation of a Database Management System for Airline Reservation and Flight Operations Management (ARFOM-DB)
* **Candidate:** Sanjyit Suresh Kumar (Roll No. 25WU0102243)
* **Co-Learner (Title Peer):** Konduru Sharva Teja (Roll No. 25WU0102128 - AIML Panthers)
* **Course Code:** DBMS-2026
* **Submission Date:** October 2026

---

## 2. Abstract
Airline flight operations and reservation networks demand zero-downtime, ACID-compliant relational architectures capable of guaranteeing seat exclusivity, customer itinerary tracking, and baggage reconciliation across complex route networks. **ARFOM-DB** is a normalized relational database management system engineered to manage the complete lifecycle of airline operations. Built upon strict Third Normal Form (3NF) relational decomposition, the database models 10 core tables and analytical views encompassing airport hubs, aircraft configurations, seat maps, scheduled flight legs, customer profiles, booking transactions, e-tickets, payments, check-in custody, baggage manifests, and cancellation penalty ledgers. The system features engine-enforced domain, entity, and referential constraints—including a composite unique invariant preventing physical double-booking. A multi-tier web application and Python REST dispatch API interface directly with the relational engine, enabling live record viewing, atomic insertions, and referential-safe deletions with sub-millisecond database reflection.

---

## 3. Introduction & Problem Statement
Commercial aviation operates under narrow financial margins where seat allocation errors, uncollected baggage surcharges, or untracked cancellations directly impact profitability and regulatory compliance. Legacy reservation approaches often rely on decentralized or partially normalized flat files, leading to three critical database failure modes:
1. **Concurrency Contention & Double-Booking:** Simultaneous reservations writing to identical flight-seat pairs.
2. **Relational Redundancy:** Repeated entry of passenger profiles, route distances, and airframe capacities leading to update and deletion anomalies.
3. **Domain Integrity Violations:** Negative baggage masses, invalid chronological departure-arrival times, or route loops where origin and destination airports are identical.

ARFOM-DB resolves these challenges by formalizing enterprise airline operations into an ANSI SQL relational framework with guaranteed transaction isolation and strict constraint enforcement.

---

## 4. Objectives and Scope
### Objectives:
* Design a comprehensive relational schema representing complete flight reservation workflows.
* Achieve strict Third Normal Form (3NF) across all relational entities, eliminating transitive dependencies.
* Enforce declarative integrity constraints (`PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, and `UNIQUE`) at the database engine level.
* Build an operational web dashboard supporting live record viewing, insertion, and deletion.
* Provide analytical views for load factor reporting, corridor demand analysis, and baggage weight logistics.

### Scope:
* Fleet management (Airbus A320, Boeing 737, Boeing 787, ATR-72).
* Multi-class cabin topology (Economy, Business, First).
* Route network spanning 10 domestic and international hubs.
* Commercial ticketing with booking references (PNRs).
* Airport departure control: check-in processing, boarding passes, and baggage weighing.
* Financial settlement and cancellation fee reconciliation.

---

## 5. Software and Hardware Requirements
* **Operating System:** macOS Sonoma 14+ / Linux Ubuntu 22.04 LTS / Windows 11
* **Relational Storage Engine:** SQLite 3.40+ (Enforced Foreign Keys) / MySQL 8.0+ (InnoDB)
* **Application Backend:** Python 3.10+ (Native `http.server`, `sqlite3`, `json`)
* **Client Presentation Layer:** Modern Web Browser (Google Chrome 120+, Safari 17+, Firefox 120+)
* **Hardware:** Minimal requirements: 1.5 GHz Dual-Core CPU, 4 GB RAM, 100 MB available storage.

---

## 6. Entity-Relationship (ER) Diagram
The relational model captures entities, attributes, primary keys, and cardinalities:
* `airports` (1) &mdash; (N) `routes` [Origin & Destination]
* `aircraft` (1) &mdash; (N) `seats` [Cabin Physical Topology]
* `aircraft` (1) &mdash; (N) `flights` [Airframe Allocation]
* `routes` (1) &mdash; (N) `flights` [Flight Trajectory]
* `passengers` (1) &mdash; (N) `bookings` [Customer Orders]
* `bookings` (1) &mdash; (N) `tickets` [Commercial Order Decomposition]
* `flights` (1) &mdash; (N) `tickets` [Flight Leg Allocation]
* `seats` (1) &mdash; (N) `tickets` [Physical Seat Assignment]
* `bookings` (1) &mdash; (N) `payments` [Financial Ledger]
* `tickets` (1) &mdash; (1) `checkins` [Airport Departure Control - Strict 1:1 via UNIQUE]
* `checkins` (1) &mdash; (N) `baggage` [Baggage Custody]
* `tickets` (1) &mdash; (1) `cancellations` [Refund & Penalty Ledger]

*(Refer to `Presentation-II/ER_diagram.png` for the complete visual diagram).*

---

## 7. Relational Schema & Normalization
### 1NF Verification:
All column attributes contain atomic, indivisible values. Multi-valued attributes (such as passenger phone numbers or baggage items) are decomposed into separate tuples with independent primary keys.

### 2NF Verification:
All non-key attributes are fully functionally dependent on the primary key. In entities with composite keys (such as `seats` with `aircraft_id + seat_number`), class attributes pertain strictly to the entire composite identifier.

### 3NF Verification:
Every non-key attribute is non-transitively dependent on the candidate key ($X \to A$ holds where $X$ is a superkey or $A$ is prime). Calculated columns (such as ticket occupancy percentage, excess luggage fees, and net retained cancellation penalties) are derived dynamically via SQL analytical views rather than stored redundantly.

---

## 8. Data Dictionary
*(Summary of core tables)*

| Table Name | Primary Key | Foreign Keys | Key Constraints & Invariants |
| :--- | :--- | :--- | :--- |
| **airports** | `airport_code` (CHAR 3) | None | Country, city mandatory |
| **routes** | `route_id` (INT) | `origin_airport`, `dest_airport` | `CHECK (origin_airport <> dest_airport)`, `CHECK (distance_km > 0)` |
| **aircraft** | `aircraft_id` (INT) | None | `CHECK (total_capacity > 0)` |
| **seats** | `seat_id` (INT) | `aircraft_id` (CASCADE) | `UNIQUE (aircraft_id, seat_number)`, `CHECK (seat_class IN ('ECONOMY', 'BUSINESS', 'FIRST'))` |
| **flights** | `flight_id` (INT) | `route_id`, `aircraft_id` | `CHECK (scheduled_arrival > scheduled_departure)` |
| **passengers**| `passenger_id` (INT) | None | `UNIQUE (email)`, `UNIQUE (passport_number)` |
| **bookings** | `booking_id` (INT) | `passenger_id` | `UNIQUE (booking_ref)` |
| **tickets** | `ticket_id` (INT) | `booking_id`, `flight_id`, `seat_id` | **`UNIQUE (flight_id, seat_id)`** (Double booking prevention) |
| **payments** | `payment_id` (INT) | `booking_id` | `CHECK (amount_paid > 0.00)` |
| **checkins** | `checkin_id` (INT) | `ticket_id` | `UNIQUE (ticket_id)` (Strict 1:1), `UNIQUE (boarding_pass)` |
| **baggage** | `baggage_id` (INT) | `checkin_id` (CASCADE) | `CHECK (weight_kg >= 0.00)`, `CHECK (excess_fee >= 0.00)` |
| **cancellations** | `cancellation_id` (INT) | `ticket_id` | `UNIQUE (ticket_id)`, `CHECK (refund_amount >= 0.00)` |

---

## 9. SQL Commands Used (DDL & DML)
Refer to:
* `Presentation-II/all_commands.sql` (Comprehensive SQLite / ANSI SQL Script)
* `sql/mysql_schema.sql` (MySQL 8.0 InnoDB Production Script)

---

## 10. Analytical Queries & Views
The system implements 7 analytical reports:
1. **Master Manifest:** 6-table join across `tickets`, `bookings`, `passengers`, `flights`, `routes`, `seats`.
2. **Occupancy & Load Factor:** Evaluates capacity utilization with `ROUND((COUNT(t.ticket_id) * 100.0 / a.total_capacity), 1)`.
3. **Route Corridor Density:** Identifies top-grossing corridors via `GROUP BY r.route_id`.
4. **Baggage Logistics & Surcharges:** Analyzes average cargo load and excess weight fee retention.
5. **Net Cancellation Penalty Retention:** Quantifies retained fee margin.
6. **On-Time Performance Ratio:** Computes status distribution using scalar subqueries.
7. **Cabin Class Yield:** Revenue segmentation across Economy, Business, and First tiers.

---

## 11. User Interface Design & Screenshots
The user interface is structured as an interactive operations center:
* **Record Explorer (Viewing):** Live data grid with search, sorting, and multi-table navigation.
* **Record Insertion:** Dynamic forms with 1-click viva presets and live database reflection.
* **Record Deletion:** Target selection with referential safety alerts and execution logs.
* **Before & After Comparator:** Side-by-side split view capturing storage engine state transitions.

*(Refer to screenshots in `Presentation-III/screenshots/`)*.

---

## 12. Implementation Details
* **Frontend:** HTML5, CSS3 Custom Properties (Dark glassmorphic styling), Vanilla Asynchronous JS.
* **Backend:** Python `http.server` dispatching REST requests to `arfom.db`.
* **Zero Dependency Architecture:** Operates immediately without third-party package managers.

---

## 13. Testing (Test Cases & Results)
| Test Case ID | Test Description | Input Data | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Negative baggage weight | `weight_kg = -5.50` | `CHECK (weight_kg >= 0)` violation | Engine aborts write in 0.8ms | **PASS** |
| **TC-02** | Duplicate seat allocation | Flight 1, Seat 1 twice | `UNIQUE (flight_id, seat_id)` violation | Engine rejects duplicate key | **PASS** |
| **TC-03** | Route departure = arrival | Origin: DEL, Dest: DEL | `CHECK (origin <> dest)` violation | Write rejected | **PASS** |
| **TC-04** | Restricted deletion | `DELETE FROM airports WHERE 'DEL'` | `ON DELETE RESTRICT` failure | Deletion blocked | **PASS** |
| **TC-05** | Valid passenger insert | Vikram Malhotra | Tuple committed | Row ID 61 allocated | **PASS** |

---

## 14. Conclusion & Future Enhancements
ARFOM-DB provides a scalable, 3NF-compliant relational foundation for airline operations. Future expansions will include:
* Stored procedures for automated boarding group calculations.
* Real-time GPS flight telematics integration.
* Automated loyalty miles accrual triggers.

---

## 15. References
1. Elmasri, R., & Navathe, S. B. *Fundamentals of Database Systems*, 7th Edition, Pearson.
2. Silberschatz, A., Korth, H. F., & Sudarshan, S. *Database System Concepts*, 7th Edition, McGraw-Hill.
3. Codd, E. F. *A Relational Model of Data for Large Shared Data Banks*, Communications of the ACM.

---

## 16. Appendix: GitHub Repository
**Repository Link:** `https://github.com/sanjyit-sureshkumar/DBMS-Course-Project`  
*(Includes Presentation-I, Presentation-II, Presentation-III, and Project-Report directories).*
