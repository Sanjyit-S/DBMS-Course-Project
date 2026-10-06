# ARFOM-DB: PRESENTATION-II MASTER DEFENSE PLAYBOOK
**Course:** Database Management Systems (DBMS) &bull; Review 2 Evaluation  
**Learner:** Sanjyit Suresh Kumar (Roll No. **25WU0102243**) &bull; Section: **AIML Whales** (Serial #18)  
**Evaluation Weightage:** 10 Marks (ER Modeling, 3NF Normalization, SQL DDL/DML, Analytical Queries)

---

## ⚡ 1. QUICK LAUNCH COMMANDS FOR PRESENTATION-II

### Terminal One-Liner (Automated Live Demo Run)
```bash
python3 demo_runner.py --demo
```
*Executes all 5 negative constraint tests live (showing engine rejection) + all 7 analytical reports!*

### Individual Terminal Demos
* **Show all Integrity Constraints passing negative tests:**
  ```bash
  python3 demo_runner.py --constraints
  ```
* **Show all 7 Analytical Reports (Joins, Views, Aggregations):**
  ```bash
  python3 demo_runner.py --reports
  ```
* **Interactive SQL Query Prompt (to run any query faculty asks):**
  ```bash
  python3 demo_runner.py
  # Select option 5: Interactive SQL Query Console
  ```

### Visual Slide Deck & ER Diagram
* **Interactive Presentation Deck:** [`Presentation-II/Presentation-II.html`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-II/Presentation-II.html) &bull; [http://localhost:8000/Presentation-II/Presentation-II.html](http://localhost:8000/Presentation-II/Presentation-II.html)
* **Interactive Drag & Zoom ER Studio:** [`Presentation-II/er_diagram_arfom.html`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-II/er_diagram_arfom.html) &bull; [http://localhost:8000/visuals/er_diagram_arfom.html](http://localhost:8000/visuals/er_diagram_arfom.html)
* **Visuals Command Center:** [http://localhost:8000/visuals/index.html](http://localhost:8000/visuals/index.html)
* **Printable Slides PDF:** [`Presentation-II/Presentation-II.pdf`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-II/Presentation-II.pdf)

---

## 🎙️ 2. PRESENTATION-II DEFENSE WALKTHROUGH (WHAT TO SAY)

### Part 1: The ER Diagram & Cardinality (Slide 2 & 3)
* **Open:** [`Presentation-II/Presentation-II.html`](file:///Users/sanjyitsureshkumar/dbms_18/Presentation-II/Presentation-II.html)
* **What to say:**
  > *"Good morning, faculty. Today I am presenting Review 2 for the Airline Reservation & Flight Operations Management System (ARFOM-DB).  
  > In our ER model, we have 10 core entities.  
  > 1. `airports` to `routes` is 1:N because one airport serves as origin or destination for many routes.  
  > 2. `aircraft` to `seats` is 1:N with ON DELETE CASCADE, representing physical cabin layout.  
  > 3. Most importantly, `passengers` and `flights` share a Many-to-Many relationship. To avoid insertion and deletion anomalies, we decomposed M:N into two 1:N relationships via the junction entity `tickets`."*

### Part 2: Normalization Proof (Slide 7)
* **What to say:**
  > *"Our relational schema satisfies strict Third Normal Form (3NF) and BCNF:  
  > - **1NF:** Every attribute is atomic; composite phone numbers or baggage items are fully unnested into independent tuples.  
  > - **2NF:** In tables with composite keys—such as `seats (aircraft_id, seat_number)`—all non-prime attributes depend on the full composite key, eliminating partial dependencies.  
  > - **3NF:** No non-key attribute depends transitively on another non-key attribute ($X \to Y$ holds only where $X$ is a superkey). Calculated values such as excess fees and load factors are dynamically computed via SQL views rather than redundantly stored."*

### Part 3: Live Negative Constraint Demonstration (Terminal Run)
* **Switch to Terminal:**
  ```bash
  python3 demo_runner.py --constraints
  ```
* **Point out the 4 live constraint failures:**
  1. **Negative Baggage Weight (`-5.50 kg`):**
     * Output: `CHECK constraint failed: weight_kg >= 0.00`
     * *Say:* *"Our domain constraint immediately rejects negative cargo masses."*
  2. **Double-Booking Seat (Seat 1 on Flight 1 twice):**
     * Output: `UNIQUE constraint failed: tickets.flight_id, tickets.seat_id`
     * *Say:* *"Composite unique constraint `(flight_id, seat_id)` prevents overbooking at the storage engine level."*
  3. **Same Origin & Destination (`DEL -> DEL`):**
     * Output: `CHECK constraint failed: origin_airport <> dest_airport`
     * *Say:* *"A flight cannot depart and arrive at the same airport."*
  4. **Negative Refund Amount (`-500.00`):**
     * Output: `CHECK constraint failed: refund_amount >= 0.00`
     * *Say:* *"Financial ledger rejects illegal negative refund values."*

### Part 4: The 7 Analytical Queries (Terminal Run)
* **Run:**
  ```bash
  python3 demo_runner.py --reports
  ```
* **Highlight key reports:**
  * **Report 1:** Master Flight Manifest &mdash; 6-table join across `tickets`, `bookings`, `passengers`, `flights`, `routes`, `seats`.
  * **Report 2:** Aircraft Occupancy & Load Factor &mdash; Evaluates percentage occupancy with `CASE WHEN` efficiency tiering.
  * **Report 3:** Route Corridor Density & Revenue &mdash; Identifies top corridors by gross ticket earnings.
  * **Report 4:** Cargo Logistics & Excess Fees &mdash; 5-table join computing average baggage weight per flight.

---

## 🔄 3. THE SEAMLESS TRANSITION FROM REVIEW 2 TO REVIEW 3

Once faculty finishes examining your Presentation-II queries, say:

> *"Ma'am/Sir, this concludes our database schema, normalization, and analytical query verification for Review 2.  
> As required for Presentation-III, I have also developed a full-stack, responsive User Interface that connects live to this relational database to demonstrate record viewing, insertion, and deletion with real-time ACID database reflection.  
> May I switch over to demonstrate the Presentation-III live UI now?"*

Then launch:
```bash
python3 "3rd presentation/start_presentation.py"
```
And proceed with the [Presentation-III Playbook](file:///Users/sanjyitsureshkumar/dbms_18/3rd%20presentation/PRESENTATION_III_PLAYBOOK.md)!
