# ARFOM-DB: PROBLEM DESCRIPTION & SYSTEM SCOPE
**Course:** Database Management Systems (DBMS) &bull; Presentation-I  
**Project Title:** Airline Reservation and Flight Operations Management System  
**Learner:** Sanjyit Suresh Kumar (Roll No. **25WU0102243**) &bull; Section: **AIML Whales** (Serial #18)

---

## 1. Executive Summary & Problem Statement
Modern airline operators manage complex, highly concurrent transactional environments spanning flight scheduling, fleet allocation, seat inventory, customer reservations, electronic ticketing, baggage handling, and financial settlements. 

Traditional spreadsheet-driven and legacy file-based reservation mechanisms suffer from critical structural deficiencies:
1. **Double-Booking & Seat Contention:** Inability to enforce strict concurrency and multi-attribute uniqueness, leading to simultaneous booking of identical physical aircraft seats.
2. **Data Redundancy & Anomalies:** Redundant storage of flight routes, passenger identities, and aircraft capacities across disparate logs leads to update, insertion, and deletion anomalies.
3. **Lack of Referential Integrity:** Orphaned baggage items, inconsistent cancellation refunds, and untracked itinerary changes.
4. **Weak Domain Constraints:** Unchecked domain values (e.g., negative luggage weights, flights departing and arriving at identical hubs, or chronological departure/arrival inversions).

**ARFOM-DB** resolves these operational challenges by designing and implementing an enterprise-grade, normalized relational database management system with rigorous integrity constraints, zero-loss 3NF decomposition, and high-performance transactional query interfaces.

---

## 2. Project Objectives
* **Comprehensive Relational Modeling:** Engineer an end-to-end database architecture encompassing 10+ core entities covering passenger lifecycles from booking to baggage claim.
* **Strict Normalization (3NF/BCNF):** Eliminate data redundancy and eliminate anomalies by decomposing Many-to-Many relationships via dedicated junction entities.
* **Declarative Constraint Architecture:** Enforce physical, temporal, and financial invariants at the storage engine level (`PRIMARY KEY`, `FOREIGN KEY`, `CHECK`, and `UNIQUE`).
* **High-Concurrency Operational Performance:** Support sub-millisecond multi-table analytical joins and real-time flight manifest projections.
* **Interactive Management UI:** Provide an intuitive, real-time web portal supporting CRUD operations with live database state reflection.

---

## 3. Scope of the System
The system encompasses four functional operational domains:
1. **Fleet & Flight Infrastructure:** Aircraft topology (airframe models, cabin seat classes: Economy, Business, First), airport registries, route networks with geographic distance validation, and operational flight segment schedules.
2. **Customer Reservation & Commercial Ticketing:** Passenger demographic registration, multi-passenger booking orders (PNRs), individual flight leg ticket issuance, and double-booking prevention.
3. **Settlement & Audit Ledger:** Multi-mode payment tracking (Credit Card, Debit Card, UPI, Net Banking), transaction verification, and cancellation fee/refund processing.
4. **Departure Control & Logistics:** Airport check-in management, electronic boarding pass generation, baggage allowance tracking, and excess weight surcharge accounting.
