# Airline Reservation & Flight Operations Management System (ARFOM-DB)

* **Learner Name:** Sanjyit Suresh Kumar  
* **Roll Number:** 25WU0102243  
* **Section:** AIML Whales (Serial #18)  
* **Presentation Slot:** Tuesday, 6 October 2026 | 11:50 am &ndash; 12:00 pm  
* **Project Title:** Design and Implementation of a Database Management System for Airline Reservation and Flight Operations Management  
* **Description:** A strict 3NF-normalized relational database system managing fleet scheduling, customer ticketing, airport check-in logistics, and live transactional CRUD operations with real-time database state reflection.

---

## 🚀 Quick Launch (Presentation-III Live UI)
```bash
python3 "3rd presentation/start_presentation.py"
```
* **Interactive UI Portal:** [`3rd presentation/app/index.html`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/app/index.html)
* **Presentation Slide Deck:** [`3rd presentation/slides/presentation_iii_slides.html`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/slides/presentation_iii_slides.html)
* **10-Minute Presentation Playbook:** [`3rd presentation/PRESENTATION_III_PLAYBOOK.md`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/PRESENTATION_III_PLAYBOOK.md)

---

## 📁 Repository Submission Folders
* **[`Presentation-I/`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-I/):** Problem Description & System Scope
* **[`Presentation-II/`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-II/):** ER Diagram, Normalized DDL/DML, and Analytical Queries
* **[`Presentation-III/`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-III/):** User Interface (Source Code, Slides, Playbook, and UI Screenshots)
* **[`Project-Report/`](file:///Users/sanjyitsureshkumar/dbms_18/Project-Report/):** Complete 16-chapter Project Report draft

```text
dbms_18/
├── README.md                           # Master project guide & presentation manual
├── demo_runner.py                      # Zero-dependency interactive CLI runner & test harness
├── sql/
│   ├── 01_schema.sql                   # PostgreSQL DDL with PK/FK, CHECKs, Indexes & Triggers
│   ├── 02_seed.sql                     # Realistic Indian & International flight seed dataset
│   ├── 03_queries_and_views.sql        # 7 Analytical Reports & Operational Views
│   ├── 04_negative_tests.sql           # Intentional violation statements for live constraint tests
│   └── mysql_schema.sql                # MySQL 8.0+ compatible InnoDB schema with SIGNAL triggers
└── docs/
    ├── ER_DIAGRAM.md                   # Complete Mermaid ER Diagram & Cardinality analysis
    ├── NORMALIZATION_AND_FD.md         # Mathematical Normalization Proof (UNF -> 3NF) & FDs
    ├── DATA_DICTIONARY.md              # 12-table comprehensive relational data dictionary
    └── VIVA_DEFENSE_MATRIX.md          # Word-for-word tactical answers for hostile viva questions
```

---

## 2. Quickstart: 10-Second Live Demonstration

You can run the complete presentation demonstration on any laptop using the built-in Python CLI runner:

```bash
# Automated live run (Executes Negative Constraint Tests + 7 Analytical Reports)
python3 demo_runner.py --demo

# Or interactive menu
python3 demo_runner.py
```

### Running in PostgreSQL (`psql`)
```bash
# 1. Build Schema & Triggers
psql -U postgres -d your_database -f sql/01_schema.sql

# 2. Populate Seed Data
psql -U postgres -d your_database -f sql/02_seed.sql

# 3. Run Analytical Views & Queries
psql -U postgres -d your_database -f sql/03_queries_and_views.sql

# 4. Run Negative Constraint Verification
psql -U postgres -d your_database -f sql/04_negative_tests.sql
```

---

## 3. The 5 Mandatory Business Rules (Enforced & Verified)

| # | Business Rule | Relational Mechanism | Live Negative Test |
| :---: | :--- | :--- | :--- |
| **1** | **One seat per passenger per flight** | Declarative `CONSTRAINT uq_flight_seat UNIQUE (flight_id, seat_id)` | Duplicate seat booking rejected with `UNIQUE constraint failed`. |
| **2** | **Aircraft-capacity enforcement** | Procedural Trigger `trg_verify_aircraft_capacity` | Exceeding airframe total capacity throws `Capacity Overrun` exception. |
| **3** | **Non-negative baggage** | Declarative `CHECK (weight_kg >= 0.00)` & `CHECK (excess_fee >= 0.00)` | Negative weight entry rejected with `CHECK constraint failed`. |
| **4** | **Check-in for confirmed bookings only** | Procedural Trigger `trg_verify_checkin_eligibility` | Checking in a cancelled ticket throws `Check-in Denied` exception. |
| **5** | **Strict refund rules** | Procedural Trigger `trg_enforce_refund_bounds` | Refunding more than the original fare throws `Accounting Anomaly` exception. |

---

## 4. The 7 Analytical Reports & Operational Views

1. **Real-Time Flight Manifest**: Passenger gate manifest showing allocated seat, class, and boarding readiness token for ground dispatch.
2. **Flight Occupancy & Yield Analytics**: Percentage capacity utilization per airframe classified as `OPTIMAL`, `MODERATE`, or `LOW_YIELD`.
3. **Route Demand & High-Density Corridors**: Passenger volume, frequency, and aggregate revenue per origin-destination pair.
4. **Baggage Logistics & Excess Surcharge Audit**: Multi-table cargo payload weight analysis and fee extraction per flight segment.
5. **Cancellation, Attrition & Net Retention Metrics**: Audited cancellation penalty retention, gross forfeited fares, and refund leakages.
6. **Flight Status & On-Time Performance (OTP)**: Schedule distribution and operational disruption counts via scalar subqueries.
7. **Revenue Segmentation by Cabin Tier & Yield**: Analytic window aggregation (`SUM(...) OVER()`) measuring revenue contribution by travel class.

---

## 5. Theoretical Documentation Quicklinks

- **[ER Diagram & Cardinality Topology](docs/ER_DIAGRAM.md)**
- **[Mathematical Normalization & Functional Dependencies](docs/NORMALIZATION_AND_FD.md)**
- **[Formal Data Dictionary](docs/DATA_DICTIONARY.md)**
- **[Viva Defense Playbook](docs/VIVA_DEFENSE_MATRIX.md)**
