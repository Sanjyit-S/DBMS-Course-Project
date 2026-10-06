# ARFOM-DB: PRESENTATION-III MASTER PLAYBOOK & VIVA CHEATSHEET
**Course:** Database Management Systems (DBMS)  
**Deliverable:** Review 3 / Presentation-III (User Interface Live Demonstration)  
**Learner:** Sanjyit Suresh Kumar (Roll No. **25WU0102243**)  
**Section:** AIML Whales &bull; **Serial No.:** 18  
**Presentation Slot:** **Tuesday, 6 October 2026 | 11:50 am &ndash; 12:00 pm (10 Minutes Sharp)**  
**Evaluation Weightage:** 10 Marks (Presentation-III UI Demo: 5 Marks &bull; Project Report: 5 Marks)

---

##  1. QUICK LAUNCH COMMANDS (INSTANT ACCESS)

### Option A: One-Command Master Launcher (Recommended)
Open Terminal in the repository root and run:
```bash
python3 "3rd presentation/start_presentation.py"
```
*This starts the Python backend server, checks all 12 database tables, and automatically opens Google Chrome to the UI dashboard!*

### Option B: Direct Browser Open (Offline / Zero-Dependency Fallback)
If you are presenting on a projector or without running a terminal server, simply double-click or open either URL in Google Chrome:
* **Interactive UI Portal:** [`3rd presentation/app/index.html`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/app/index.html)
* **Presentation Slide Deck:** [`3rd presentation/slides/presentation_iii_slides.html`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/slides/presentation_iii_slides.html)

---

##  2. EXACT 10-MINUTE TIMELINE & PRESENTATION SCRIPT

> [!IMPORTANT]
> You have strictly **10 minutes** allotted (11:50 AM to 12:00 PM). Stick to this minute-by-minute rhythm so you don't get cut off before showing the live database reflection!

```
[00:00 - 01:30] Slide Deck Introduction (Slides 1 to 4)
[01:30 - 03:30] Live Demo 1: Viewing of Records & Master Manifest
[03:30 - 05:30] Live Demo 2: Insertion of Records & Live DB Reflection
[05:30 - 07:30] Live Demo 3: Deletion of Records & Constraint Integrity
[07:30 - 08:45] Live Demo 4: Before & After Comparator + Negative Tests
[08:45 - 10:00] Conclusion & Faculty Viva Defense Q&A
```

---

### Step 1: Slide Deck Introduction (00:00 &ndash; 01:30 | 90 Seconds)
* **Open:** [`presentation_iii_slides.html`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/slides/presentation_iii_slides.html) in Fullscreen (Press **`F`**).
* **Slide 1 (Title):**
  > *"Good morning, respected faculty. I am Sanjyit Suresh Kumar, Roll No. 25WU0102243 from AIML Whales, presenting Serial #18: The Airline Reservation and Flight Operations Management System (ARFOM-DB)."*
* **Slide 2 (Architecture) & Slide 3 (Normalized Schema):**
  > *"Our system is designed as a 3-tier architecture: a responsive web presentation layer, a Python REST query dispatcher, and a relational storage engine with engine-level constraint enforcement. Our schema is strictly decomposed into 3NF across 10 tables, with composite keys preventing double-booking and foreign keys preserving referential integrity."*
* **Slide 4 (Rubric Alignment):**
  > *"Today, I will directly demonstrate the four required capabilities for Presentation-III: live record viewing, record insertion, record deletion, and real-time database state reflection. Let's switch directly to the live system."*

---

### Step 2: Live Demo 1 &mdash; Viewing of Records (01:30 &ndash; 03:30 | 2 Minutes)
* **Switch to:** UI Dashboard ([`index.html`](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/app/index.html)).
* **Click Tab:** ` 1. Record Explorer`.
* **Action:**
  1. Show the default **` Master Manifest`** table.
  2. Point out the top metrics: **60 Passengers**, **15 Flights**, **60 Bookings**, and **₹4,38,200 Gross Revenue**.
  3. In the search box, type `AI-101` or `Delhi` to demonstrate instant debounced search across 73 joined records.
  4. Click the table switcher pills:
     * Click `passengers (60)` &rarr; show customer profiles.
     * Click `flights (15)` &rarr; show aircraft and departure timings.
     * Click `tickets (60)` &rarr; show individual seat allocations.
* **What to say:**
  > *"Here is our Master Flight Manifest view. This is a live 6-table relational join connecting tickets, bookings, passengers, flights, routes, and seats, queried in just 0.8 milliseconds. As you can see, every table in our database can be searched, sorted, and inspected live."*

---

### Step 3: Live Demo 2 &mdash; Insertion of Records (03:30 &ndash; 05:30 | 2 Minutes)
* **Click Tab:** ` 2. Record Insertion`.
* **Action:**
  1. Under **1-Click Quick Demo Presets**, click:  
     `VIP Passenger: Dr. Vikram Malhotra`.
  2. Notice the form fields instantly populate:
     * First Name: `Vikram`
     * Last Name: `Malhotra`
     * Email: `vikram.malhotra@skywings.org`
     * Passport: `Z...` (Unique)
  3. Click **` Execute INSERT & Commit to Database`**.
* **Observe & Point to the Live Reflection Panel:**
  * Status Badge turns **EMERALD GREEN**: `SUCCESS (ID: 61)`
  * Terminal Log shows the exact SQL:
    ```sql
    INSERT INTO passengers (first_name, last_name, email, passport_number) 
    VALUES ('Vikram', 'Malhotra', 'vikram.malhotra@skywings.org', 'Z8921475');
    ```
  * Point out:
    * **Before Count:** `60`
    * **After Count:** `61`
    * **Net Delta:** `+1`
    * **Latency:** `1.2 ms`
  4. Click the button **`View in Table`** &rarr; The UI jumps to the table and highlights the new row in **glowing green**!
* **What to say:**
  > *"Notice how the insertion was committed as an ACID transaction. The database immediately allocated primary key #61, updated the table count from 60 to 61, and our Live Reflection Panel shows the exact SQL executed and latency in real time."*

---

### Step 4: Live Demo 3 &mdash; Deletion of Records (05:30 &ndash; 07:30 | 2 Minutes)
* **Click Tab:** ` 3. Record Deletion`.
* **Action:**
  1. Under Target Table, select `passengers`.
  2. Under Select Target Record ID, select `ID #61 — Vikram Malhotra`.
  3. Point to the **Candidate Details Preview** box.
  4. Click **` Execute DELETE & Commit Change`**.
* **Observe & Point to the Live Reflection Panel:**
  * Status Badge turns **GREEN**: `DELETED (passenger_id = 61)`
  * Terminal Log shows:
    ```sql
    DELETE FROM passengers WHERE passenger_id = 61;
    ```
  * Point out:
    * **Before Count:** `61`
    * **After Count:** `60`
    * **Net Delta:** `-1`
  * The deleted tuple details appear in the audit ledger box below.
* **What to say:**
  > *"When we execute the delete, the storage engine executes `DELETE FROM passengers WHERE passenger_id = 61;`, verifies referential integrity, and atomically commits. The row count drops from 61 back to 60, and the tuple is permanently expunged."*

---

### Step 5: Live Demo 4 &mdash; Before & After Comparator + Negative Tests (07:30 &ndash; 08:45 | 75 Seconds)
* **Click Tab:** ` 4. Before & After Comparator`.
  * Click **` Demo 1: Run Insert & Compare`**.
  * Point out the 3-column split view:
    * **[LEFT COLUMN]:** Before state (Row count: 60)
    * **[CENTER COLUMN]:** Transaction transition (`INSERT INTO passengers...`)
    * **[RIGHT COLUMN]:** After state (Row count: 61, newly committed row glowing in green).
  * *Say:* *"Ma'am, this comparator provides direct visual proof of the database state change before and after the operation on a single screen."*
* **Click Tab:** ` 5. Negative Testing & Constraints`.
  * Click **` Run Negative Test Live`** under **Negative Baggage Weight**.
  * The engine immediately rejects the query with a red badge:
    ```
    BLOCKED BY DATABASE ENGINE: CHECK constraint failed: weight_kg >= 0.00
    ```
  * *Say:* *"Our database actively guards against corrupt states at the engine level with CHECK, UNIQUE, and FOREIGN KEY RESTRICT constraints."*

---

### Step 6: Conclusion & Viva Handover (08:45 &ndash; 10:00 | 75 Seconds)
* Switch back to **Slide 10** in the presentation deck.
* **Closing Statement:**
  > *"To summarize, ARFOM-DB delivers a fully normalized 3NF relational model, zero update anomalies, atomic ACID transaction guarantees, and sub-millisecond query execution with live database reflection. Thank you faculty, I am now ready for your viva questions."*

---

##  3. TOP 10 VIVA QUESTIONS & WORD-FOR-WORD ANSWERS

### Q1: "Is this connected to MySQL or SQLite?"
> **Your Answer:**  
> *"Ma'am/Sir, our schema is written in 100% ANSI SQL standard and is fully compatible with MySQL 8.0 with InnoDB tables. In our repository, `sql/mysql_schema.sql` contains the complete MySQL 8.0 DDL script. For fast local demonstration with zero external dependencies, our Python backend connects to an embedded relational SQLite storage engine with foreign keys explicitly enabled via `PRAGMA foreign_keys = ON`."*

### Q2: "How do you prevent two passengers from booking the same seat on a flight?"
> **Your Answer:**  
> *"Through a table-level composite UNIQUE constraint in the `tickets` table:  
> `CONSTRAINT uq_flight_seat UNIQUE (flight_id, seat_id)`.  
> If an insert is attempted for a seat that is already booked on that flight, the relational storage engine aborts the transaction at the B-Tree index level before any row write commits."*

### Q3: "Why did you separate bookings and tickets into two different tables?"
> **Your Answer:**  
> *"Because a single commercial booking order can contain multiple passenger tickets or round-trip flight legs. Keeping `bookings` as the commercial parent entity and `tickets` as the physical seat allocation entity satisfies Second and Third Normal Form (2NF & 3NF) and prevents update anomalies."*

### Q4: "What is the relationship between passengers and flights?"
> **Your Answer:**  
> *"Logically, passengers and flights share a Many-to-Many (M:N) relationship. To normalize this into 3NF, we decomposed M:N into two 1:N relationships using the junction entity `tickets`."*

### Q5: "What happens if someone deletes an airport that has active flights?"
> **Your Answer:**  
> *"We enforced `ON DELETE RESTRICT` on `origin_airport` and `dest_airport` foreign keys in the `routes` table. If someone tries to delete 'DEL', the storage engine detects dependent child routes and immediately raises an integrity violation error, protecting referential consistency."*

### Q6: "What check constraints exist in your database?"
> **Your Answer:**  
> *"We defined four critical domain CHECK constraints:  
> 1. `CHECK (origin_airport <> dest_airport)` in `routes` (flight cannot land where it departs)  
> 2. `CHECK (distance_km > 0.00)` in `routes`  
> 3. `CHECK (scheduled_arrival > scheduled_departure)` in `flights` (temporal consistency)  
> 4. `CHECK (weight_kg >= 0.00)` in `baggage` (negative baggage weight rejected)"*

### Q7: "How does the UI reflect database changes live?"
> **Your Answer:**  
> *"Every user operation triggers a POST request to our REST backend. The backend executes an atomic transaction with `conn.commit()`, immediately re-queries the row count and primary key, and streams back the before count, after count, and latency in the response payload. The UI then highlights the newly written row reactively."*

### Q8: "What normal form is your schema in?"
> **Your Answer:**  
> *"Our entire schema is in strict Third Normal Form (3NF). Every relation is in 1NF (atomic attributes), 2NF (no partial functional dependencies on candidate keys), and 3NF (no transitive dependencies where a non-prime attribute depends on another non-prime attribute)."*

### Q9: "Can you explain your 6-table join view?"
> **Your Answer:**  
> *"Yes, `view_master_manifest` joins `tickets` with `bookings` on `booking_id`, `passengers` on `passenger_id`, `flights` on `flight_id`, `routes` on `route_id`, and `seats` on `seat_id`. This produces a complete flight manifest showing passenger name, route, seat number, and fare in a single query."*

### Q10: "If we mess up the data during testing, how do you recover?"
> **Your Answer:**  
> *"We built an instant 'Reset Seed DB' button in the top navigation bar. Clicking it executes an atomic seed rebuild, restoring all 12 tables and 60+ pristine records in less than 1 second."*

---

##  4. GITHUB SUBMISSION CHECKLIST (BEFORE 10 OCTOBER 2026)

The evaluation instruction sheet specifies that your public repository named `DBMS-Course-Project` must contain four folders:

| Folder Name | Required Contents | Status in this Workspace |
| :--- | :--- | :--- |
| **`Presentation-I/`** | Problem Description PPT / PDF | Staged in `Presentation-I/` |
| **`Presentation-II/`** | Review 2 PPT/PDF, ER diagram image, `.sql` schema/seed/queries, Viva Playbook | Staged in `Presentation-II/` |
| **`Presentation-III/`** | UI source code (`app/`), Slides (`slides/`), and Screenshots of every screen (view, insert, delete, before/after) | Staged in `Presentation-III/` & `3rd presentation/` |
| **`Project-Report/`** | Complete 16-chapter PDF Project Report (due 10 Oct 2026) | Staged template & generator in `Project-Report/` |
| **`README.md`** | Name, Roll No., Project Title, and One-Line Description | Configured at root |

---
*Good luck with Presentation-III, Sanjyit! You are 100% prepared to ace the presentation!*
