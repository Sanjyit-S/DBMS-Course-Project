# Review 2 Viva Defense Playbook: Complete Survival & Master Dossier

> **Purpose:** This document is designed for zero-DBMS-background rapid mastery. It arms you with word-for-word answers, plain-English conceptual breakdowns, and defense mechanisms against aggressive or hostile questioning from the evaluation committee / Vice Dean.

---

## Part 1: Fast-Recall Core Cheat Sheet (The 5 Golden Rules)

If your professor asks: *"Show me where you implemented my 5 mandatory business rules,"* immediately quote these lines:

| # | Mandatory Business Rule | Relational Mechanism | The Exact File & Line | The 10-Second Explanation |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **One seat per passenger per flight** | Declarative `CONSTRAINT uq_flight_seat UNIQUE (flight_id, seat_id)` | [`sql/01_schema.sql`](file:///Users/sanjyitsureshkumar/dbms_18/sql/01_schema.sql) in table `tickets` | "Enforced at the B-Tree storage engine index level. No two tickets can ever share the same `flight_id` and `seat_id` combination." |
| **2** | **Aircraft-capacity limits** | Trigger `trg_verify_aircraft_capacity` (`BEFORE INSERT ON tickets`) | [`sql/01_schema.sql`](file:///Users/sanjyitsureshkumar/dbms_18/sql/01_schema.sql) | "Counts active uncancelled tickets for that flight. If count $\ge$ airframe `total_capacity`, it throws a `Capacity Overrun` exception and aborts." |
| **3** | **Non-negative baggage** | Declarative `CHECK (weight_kg >= 0.00)` and `CHECK (excess_fee >= 0.00)` | [`sql/01_schema.sql`](file:///Users/sanjyitsureshkumar/dbms_18/sql/01_schema.sql) in table `baggage` | "Pure domain constraint. Rejects negative weight measurements or negative fee penalties at input time." |
| **4** | **Check-in for confirmed bookings only** | Trigger `trg_verify_checkin_eligibility` (`BEFORE INSERT ON checkins`) | [`sql/01_schema.sql`](file:///Users/sanjyitsureshkumar/dbms_18/sql/01_schema.sql) | "Verifies that the parent booking is `CONFIRMED` and ticket is `ISSUED`. Automatically transitions `ticket_status` to `CHECKED_IN`." |
| **5** | **Strict refund rules** | Trigger `trg_enforce_refund_bounds` (`BEFORE INSERT ON cancellations`) | [`sql/01_schema.sql`](file:///Users/sanjyitsureshkumar/dbms_18/sql/01_schema.sql) | "Enforces that `refund_amount <= fare_amount`. Rejects any refund exceeding paid fare as an `Accounting Anomaly` and sets ticket to `CANCELLED`." |

---

## Part 2: Crash Course — DBMS Fundamentals Explained Simply

### 1. What is a Primary Key (PK)?
* **Plain English:** A column (or set of columns) that uniquely identifies every single row in a table. It cannot be `NULL` and cannot have duplicates.
* *Example:* `airport_code` ('DEL') in `airports`, or `passenger_id` (1) in `passengers`.

### 2. What is a Foreign Key (FK)?
* **Plain English:** A column in a child table that points directly to a Primary Key in a parent table. It guarantees you can't have "orphan records."
* *Example:* `booking_id` in `tickets` points to `bookings(booking_id)`. You can't issue a ticket for a booking that doesn't exist.

### 3. What is a Superkey and Candidate Key?
* **Superkey:** Any combination of columns that uniquely identifies a row (even if it has extra unnecessary columns).
* **Candidate Key:** A *minimal* superkey (a unique identifier with no redundant attributes). The Primary Key is simply the Candidate Key you chose as primary.

### 4. What are Functional Dependencies ($X \rightarrow Y$)?
* **Plain English:** "If I know $X$, there is only one possible value for $Y$."
* *Example:* `passport_number -> passenger_name`. If I have your passport number, your name is uniquely determined.

### 5. What are the Normal Forms?
* **UNF (Unnormalized Form):** One giant messy table containing repeating lists (e.g., multiple passengers or bags shoved inside one booking row).
* **1NF (First Normal Form):** Every cell has only **one single atomic value** (no arrays or lists). A unique composite key is chosen.
* **2NF (Second Normal Form):** In 1NF + **No Partial Dependencies**. If your primary key is composite `(A, B)`, every other column must depend on **both A and B**, not just A alone.
* **3NF (Third Normal Form):** In 2NF + **No Transitive Dependencies**. Non-key columns cannot depend on other non-key columns ($A \rightarrow B \rightarrow C$). If column $C$ depends on $B$, $B$ must be moved to its own table.
* **BCNF (Boyce-Codd Normal Form):** A slightly stricter version of 3NF where in *every* functional dependency $X \rightarrow Y$, $X$ must be a superkey.

---

## Part 3: The 16 Lethal Viva Defense Questions & Exact Answers

---

### Q1. *"Why did you normalize to 3NF instead of BCNF? Did you fail to reach BCNF?"*

* **What She's Testing:** Does this student understand the difference between 3NF and BCNF, or did they just copy a syllabus heading?
* **The 15-Second Recital:**
  > *"Our schema actually **satisfies BCNF across all 12 tables** because every determinant in every functional dependency is a superkey. We framed it as 3NF in our presentation to match the exact wording of the syllabus rubric ('up to 3NF'). In classical database theory, standard 3NF synthesis guarantees both Lossless Join and 100% Dependency Preservation, whereas some BCNF decompositions can sacrifice dependencies. Fortunately, our domain allowed us to achieve full BCNF compliance while preserving 100% of dependencies locally."*
* **The Concept:** In 3NF, $X \rightarrow A$ is allowed if $X$ is a superkey OR $A$ is prime. In BCNF, $X$ *must* always be a superkey. In our schema, every single determinant ($X$) is a primary key, so we hit BCNF anyway!
* **Trap Avoidance:** NEVER say *"BCNF was too hard"* or *"We didn't need BCNF."* Say *"We strictly satisfy BCNF."*

---

### Q2. *"Why do you have BOTH a UNIQUE constraint on `(flight_id, seat_id)` AND an aircraft capacity trigger? Isn't that redundant?"*

* **What She's Testing:** Can you distinguish between micro-level relational constraints and macro-level business invariants?
* **The 15-Second Recital:**
  > *"That is layered defensive database engineering. `UNIQUE(flight_id, seat_id)` enforces **Micro-Level Uniqueness**—guaranteeing that two passengers cannot be assigned the same physical seat on a flight. 
  > 
  > The trigger `trg_verify_aircraft_capacity` enforces **Macro-Level Airframe Payload Limits**. For example, if an airline dynamically swaps an aircraft from an Airbus A321 (220 seats) down to an A320 (180 seats), previously booked seat IDs might all be unique, but would violate physical airframe capacity. The trigger acts as an active constraint barrier preventing overbooking beyond certified equipment limits."*
* **The Concept:** Think of a concert hall: having unique seat numbers stops two people from sitting on seat #5, but the fire marshal's maximum room capacity rule is a separate check!
* **Trap Avoidance:** Do NOT say *"I just added it to be safe."* Use the words **Micro-Invariant Uniqueness** and **Macro-Invariant Capacity Limits**.

---

### Q3. *"Why use surrogate integer keys (`booking_id`, `ticket_id`) instead of natural keys (`booking_ref`, `passport_number`)?"*

* **What She's Testing:** Do you know how database storage engines (B-Trees) and RAM memory buffers actually work?
* **The 15-Second Recital:**
  > *"We used natural keys where domain standards are globally immutable—specifically `CHAR(3)` for IATA airport codes. 
  > 
  > However, for high-write transactional tables like `bookings`, `tickets`, and `payments`, we deliberately used monotonic integer surrogate keys (`SERIAL`/`AUTO_INCREMENT`) for three enterprise reasons:
  > 1. **B-Tree Index Performance:** Sequential integers append cleanly to the right of B-Tree index pages, preventing page splits and fragmentation caused by random alphanumeric hashes.
  > 2. **Memory Efficiency:** Joining 4-byte integers across 6 downstream tables consumes significantly less buffer cache memory than joining 20-character strings.
  > 3. **Business Logic Isolation:** If customer support ever updates a customer's PNR or email, zero foreign keys break across downstream operational ledgers."*
* **The Concept:** B-Trees love numbers like 1, 2, 3, 4. If you insert random text like "X9B7A" and "A1Z4C", the database has to constantly tear open disk pages to insert in the middle.
* **Trap Avoidance:** Do NOT say *"Auto-increment is just easier."* Say **B-Tree page fill factors and index leaf fragmentation**.

---

### Q4. *"Why is `aircraft_id` in `seats` set to `ON DELETE CASCADE`, but in `flights` it is set to `ON DELETE RESTRICT`?"*

* **What She's Testing:** Do you understand referential integrity actions, composition (weak entities), and cascading safety?
* **The 15-Second Recital:**
  > *"Because `seats` represents an **existence-dependent physical component** of an airframe (a weak composition entity). A physical seat cannot exist without the plane it is bolted into; when a retired plane is scrapped, its physical seat layout cascades cleanly.
  > 
  > In contrast, `flights` represents an **operational commercial commitment**. If an aircraft has active scheduled flights with booked passengers, deleting the aircraft must be strictly **BLOCKED (`RESTRICT`)**. This creates a defensive safety net: an in-service aircraft can never be deleted while assigned to flights, while decommissioned aircraft can safely purge their seat maps."*
* **The Concept:** If you trash an old laptop, its internal keys get trashed with it (`CASCADE`). But you cannot trash a company laptop if an employee is currently using it to run client meetings (`RESTRICT`).
* **Trap Avoidance:** Do NOT say *"I didn't notice that."* Emphasize the **safety barrier** of `RESTRICT` on `flights`.

---

### Q5. *"Why is `fare_amount` stored inside `tickets` when you could calculate it from a `fares` table? Isn't that redundant data?"*

* **What She's Testing:** Financial database auditability and point-in-time immutability vs naive normalization.
* **The 15-Second Recital:**
  > *"Storing `fare_amount` directly on the `tickets` table is a deliberate architectural decision required for **Temporal Immutability and Financial Accounting Standards (GAAP)**.
  > 
  > Airline fares fluctuate dynamically due to yield management and demand algorithms. If we calculated ticket prices dynamically via a join to a live fare matrix, every time the airline adjusted prices, the calculated historical revenue of flights flown three months ago would retroactively change, corrupting financial ledgers. Storing the transacted fare at the instant of issuance maintains immutable point-in-time audit integrity."*
* **The Concept:** When you buy groceries with a receipt showing milk for ₹50, and next week milk price rises to ₹60, your old receipt shouldn't magically change to ₹60!
* **Trap Avoidance:** Never apologize for storing `fare_amount`. Proudly call it **"Temporal point-in-time auditing."**

---

### Q6. *"What happens under heavy concurrent booking traffic? Won't two users booking the same seat cause a race condition in your trigger?"*

* **What She's Testing:** Transaction isolation, ACID properties, and concurrency control.
* **The 15-Second Recital:**
  > *"In an enterprise production environment, concurrency is resolved through two defensive tiers:
  > 
  > 1. **Transaction Isolation & Row-Level Locking:** Booking transactions execute under `ISOLATION LEVEL REPEATABLE READ` or acquire pessimistic row locks via `SELECT aircraft_id FROM flights WHERE flight_id = ? FOR UPDATE`. This serializes concurrent booking requests against that flight leg.
  > 2. **Atomic Storage Engine Barrier:** Even if two concurrent threads bypassed the application trigger simultaneously, the database's declarative constraint `UNIQUE (flight_id, seat_id)` is enforced atomically at the storage engine's B-Tree leaf level. The B-Tree page latch guarantees that one thread commits and the second thread is immediately rejected with a duplicate key exception."*
* **The Concept:** Even if two people click "Book" at the exact same millisecond, only one can grab the lock on the index leaf. The second is rejected.
* **Trap Avoidance:** Don't say *"Concurrency is handled by the front-end."* Concurrency in DBMS is handled by **transaction isolation and unique index latches**.

---

### Q7. *"Why did you write triggers instead of declarative `CHECK` constraints for capacity and check-in eligibility?"*

* **What She's Testing:** SQL standard constraints vs procedural extensions.
* **The 15-Second Recital:**
  > *"Because ANSI SQL standards strictly limit declarative `CHECK` constraints to **single-row, single-table attribute evaluations**.
  > 
  > A `CHECK` constraint cannot execute subqueries or inspect parent table states across foreign tables—for instance, checking `bookings.booking_status` from inside a `checkins` insert, or calculating `COUNT(tickets)` against `aircraft.total_capacity`. In relational database engines like PostgreSQL and MySQL, cross-table invariant assertions must be enforced via **Procedural Triggers (`BEFORE INSERT`)**, which execute with indexed $O(1)$ lookups."*
* **The Concept:** A `CHECK` constraint can only see the columns on the row currently being typed in (like `weight_kg >= 0`). It is blind to other tables. Triggers have eyes on the whole database.
* **Trap Avoidance:** Don't say *"I like triggers better."* Say **"Declarative CHECK constraints cannot execute subqueries across foreign tables in the SQL standard."**

---

### Q8. *"Why is `cancellations` a separate table with `ticket_id UNIQUE` instead of just setting `ticket_status = 'CANCELLED'` in `tickets`?"*

* **What She's Testing:** Sparse tables, null handling, and 3NF normalization.
* **The 15-Second Recital:**
  > *"That directly satisfies **Third Normal Form (3NF)** and **Financial Audit Separation**:
  > 
  > 1. **Elimination of Null Anomalies:** Cancellation metadata (`cancellation_timestamp`, `refund_amount`) applies *only* to cancelled tickets. Adding these columns directly into `tickets` would force 95% of active issued tickets to store `NULL` values, resulting in sparse, inefficient tables.
  > 2. **Audit Ledger Integrity:** A cancellation is a distinct financial accounting event involving refund capital disbursement. A dedicated ledger with `ticket_id UNIQUE` preserves an unalterable audit trail and links cleanly to payment reconciliation."*
* **The Concept:** You don't put a "Date of Death" column on a live employee badge table; you keep mortality or termination records in a dedicated audit log.

---

### Q9. *"What index structures did you create and why?"*

* **What She's Testing:** Indexing strategy, query optimization, and B-Tree selectivity.
* **The 15-Second Recital:**
  > *"We created secondary B-Tree composite indexes targeted at high-frequency query access paths:
  > 1. `idx_flights_search` on `flights(route_id, scheduled_departure, flight_status)`: Optimizes customer flight searches using an index-only range scan without full-table table scans.
  > 2. `idx_bookings_pnr` on `bookings(booking_ref)`: Guarantees $O(\log N)$ hash-like lookup speed when ground staff query a 6-character PNR.
  > 3. `idx_tickets_booking` on `tickets(booking_id)` and `idx_tickets_flight` on `tickets(flight_id)`: Accelerates multi-table joins when assembling real-time flight manifests and calculating occupancy yield."*
* **The Concept:** An index is like the index at the back of a textbook. Instead of reading all 500 pages to find "Delhi flight", you jump directly to page 42.

---

### Q10. *"Prove that your schema decomposition has no insertion, deletion, or update anomalies."*

* **What She's Testing:** The practical purpose of normalization.
* **The 15-Second Recital:**
  > *"We can prove this by inspecting our decoupled entities:
  > 1. **No Insertion Anomaly:** We can add a newly commissioned airport into `airports` or a new plane into `aircraft` without requiring any flights, bookings, or passengers to exist. In the unnormalized relation ($UNF$), an airport could not exist without a booking reference.
  > 2. **No Deletion Anomaly:** If a passenger cancels their booking, or if old booking records are archived, the physical flight corridor, schedule, and aircraft definitions remain intact.
  > 3. **No Update Anomaly:** If Indira Gandhi International Airport changes its name, we update a single row in `airports`. All downstream routes and flights instantly reflect the update via foreign key reference without inconsistent duplicates."*

---

### Q11. *"What is a Weak Entity in your schema, and how is it identified?"*

* **What She's Testing:** Relational terminology and ER modeling semantics.
* **The 15-Second Recital:**
  > *"In our schema, `seats` and `baggage` function as **Weak Entities**:
  > - `seats` has an existence dependency on `aircraft`. A seat label like '12A' has no unique physical meaning without knowing which `aircraft_id` it belongs to. That is why its physical uniqueness constraint is composite: `UNIQUE (aircraft_id, seat_number)`.
  > - `baggage` has an existence dependency on `checkins`. A checked bag cannot exist in the hold without an originating check-in event (`checkin_id`).
  > In both cases, the parent's removal cascades to the child (`ON DELETE CASCADE`)."*

---

### Q12. *"How do your triggers maintain state machine transitions automatically?"*

* **What She's Testing:** Active database automation and side effects.
* **The 15-Second Recital:**
  > *"Our procedural triggers don't just validate; they execute automated state machine transitions:
  > - When a check-in record is inserted into `checkins`, trigger `trg_verify_checkin_eligibility` automatically executes `UPDATE tickets SET ticket_status = 'CHECKED_IN' WHERE ticket_id = NEW.ticket_id`.
  > - When a cancellation record is inserted into `cancellations`, trigger `trg_enforce_refund_bounds` automatically executes `UPDATE tickets SET ticket_status = 'CANCELLED' WHERE ticket_id = NEW.ticket_id`.
  > This guarantees that application software cannot accidentally leave tickets in an inconsistent or out-of-sync state."*

---

### Q13. *"What is Lossless Join Decomposition, and how do you prove your schema has it?"*

* **What She's Testing:** Formal relational mathematical theorems.
* **The 15-Second Recital:**
  > *"A decomposition of relation $R$ into $R_1$ and $R_2$ is **Lossless** if and only if the intersection of their attribute sets forms a superkey of at least one of the relations:
  > $$R_1 \cap R_2 \rightarrow R_1 \quad \text{OR} \quad R_1 \cap R_2 \rightarrow R_2$$
  > In every single table join across our schema, the common attribute is a primary key:
  > - `airports` $\cap$ `routes` = `airport_code` (Primary Key of `airports`)
  > - `aircraft` $\cap$ `seats` = `aircraft_id` (Primary Key of `aircraft`)
  > - `bookings` $\cap$ `tickets` = `booking_id` (Primary Key of `bookings`)
  > Because the join column is always a candidate key, joining the tables reconstructs the original universal relation with zero spurious or false tuples."*

---

### Q14. *"What is Dependency Preservation, and why does it matter?"*

* **What She's Testing:** Bernstein's synthesis and functional dependency theory.
* **The 15-Second Recital:**
  > *"Dependency Preservation means that the union of all functional dependencies projected onto our individual tables contains every functional dependency present in the original global closure ($F^+$):
  > $$(F_1 \cup F_2 \cup \dots \cup F_k)^+ \equiv F^+$$
  > It matters because if dependencies are preserved, the database engine can enforce all business integrity constraints locally within individual tables via primary and unique keys, without needing expensive cross-table joins during every insert or update."*

---

### Q15. *"What is the difference between Logical and Physical Data Independence in your project?"*

* **What She's Testing:** ANSI/SPARC 3-schema database architecture.
* **The 15-Second Recital:**
  > *"1. **Logical Data Independence:** Demonstrated through our **Operational Views** (`view_flight_manifest`, `view_flight_occupancy`). If we add new columns or modify the internal structure of the `tickets` or `passengers` tables, the conceptual views consumed by ground dispatch applications remain completely unchanged.
  > 2. **Physical Data Independence:** Demonstrated through our **Secondary B-Tree Indexes**. We can create, drop, or rebuild indexes like `idx_flights_search` or change storage block sizing without modifying a single SQL application query or changing table schemas."*

---

### Q16. *"How does your database handle refund deductions? Why not just refund 100%?"*

* **What She's Testing:** Domain business rules and arithmetic check constraints.
* **The 15-Second Recital:**
  > *"Airlines enforce cancellation penalty tiers based on how close to departure a cancellation occurs. 
  > 
  > In our seed dataset, Ticket #5 had a base fare of ₹8,500.00. Upon cancellation, the cancellation record processed a refund of ₹6,800.00, retaining ₹1,700.00 as an audited cancellation penalty fee. 
  > 
  > Trigger `trg_enforce_refund_bounds` guarantees that the refund amount can never exceed ₹8,500.00. Our fifth analytical query audits this directly, computing gross forfeited fares, total refunded capital, and net retained penalty margin."*

---

## Part 4: Emergency Survival Protocol (The Poker Face)

### 1. If She Interrupts You Mid-Sentence
* **Do NOT:** Fidget, apologize, or argue emotionally.
* **Do THIS:** Stop speaking instantly. Look directly at her notepad or eyes. Nod once. Let her finish her sentence completely. Then respond calmly:  
  *"Yes, Vice Dean, that directly relates to our referential constraint in table X..."*

### 2. If She Asks a Term You Have Never Heard Of
* **Do NOT:** Say *"I don't know"* or make up a fake technical buzzword.
* **The Pivot Script:**
  > *"In our current operational design, we prioritized enforcing that constraint directly at the storage engine layer via triggers and B-Tree uniqueness. Could you specify which table's lifecycle you would like to see that applied to?"*
  *(This throws the ball back into her court and forces her to rephrase it in terms of the tables you already know!)*

### 3. The 3-Second Rule
* When she finishes asking a hostile question, **count 1... 2... 3... in your head before speaking.**
* Taking a deliberate 3-second pause makes you look like an executive analyzing architectural tradeoffs, rather than a nervous student reciting memorized notes.

---

## Part 5: One-Line Summary of Every Table (Instant Memory Trigger)

1. `airports`: The physical terminals (DEL, BOM). Primary Key = `airport_code`.
2. `routes`: Flight corridors between 2 airports with distance. Checks `origin != dest`.
3. `aircraft`: The physical airplanes with certified `total_capacity`.
4. `seats`: Physical chairs inside a plane. Cascades on aircraft delete.
5. `flights`: Scheduled trips on a route using an aircraft with departure/arrival times.
6. `passengers`: People with unique passports and emails.
7. `bookings`: Commercial orders with a 6-letter PNR token.
8. `tickets`: The golden table connecting a booking, a flight, and a seat. `UNIQUE(flight, seat)`.
9. `payments`: Money paid via UPI/Card. Strictly positive amount.
10. `checkins`: 1:1 gate clearance creating a barcode boarding pass.
11. `baggage`: Luggage checked under custody. Non-negative weight check.
12. `cancellations`: 1:1 revocation ledger enforcing `refund <= fare paid`.
