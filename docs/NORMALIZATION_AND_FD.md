# Mathematical Normalization, Functional Dependencies & Relational Decomposition

## 1. Formal Theoretical Definitions

### Third Normal Form (3NF)
A relation schema $R$ is in **Third Normal Form (3NF)** with respect to a set of functional dependencies $F$ if, for every non-trivial functional dependency $X \rightarrow A \in F^+$:
1. $X$ is a **superkey** of $R$, OR
2. $A$ is a **prime attribute** of $R$ (i.e., $A$ is a constituent member of some candidate key of $R$).

### Boyce-Codd Normal Form (BCNF)
A relation schema $R$ is in **BCNF** if, for every non-trivial functional dependency $X \rightarrow A \in F^+$, $X$ is a **superkey** of $R$.
*(Note: As proven below, our decomposed schema strictly satisfies BCNF across all relations because every determinant is a superkey, while guaranteeing 100% dependency preservation).*

---

## 2. Normalization Process: UNF $\rightarrow$ 1NF $\rightarrow$ 2NF $\rightarrow$ 3NF

### Stage 0: Universal Unnormalized Relation ($UNF$)

$$R_{\text{univ}} = \{ \text{booking\_ref}, \text{booking\_date}, \text{passenger\_id}, \text{first\_name}, \text{last\_name}, \text{email}, \text{passport\_no}, \text{flight\_no}, \text{dep\_airport}, \text{arr\_airport}, \text{sched\_dep}, \text{sched\_arr}, \text{aircraft\_id}, \text{model}, \text{capacity}, \text{seat\_no}, \text{seat\_class}, \text{fare\_amt}, \text{payment\_id}, \text{amount\_paid}, \text{pay\_method}, \text{pay\_status}, \text{checkin\_id}, \text{boarding\_pass}, \text{baggage\_id}, \text{bag\_weight}, \text{excess\_fee}, \text{cancellation\_id}, \text{refund\_amt} \}$$

**Anomalies in $UNF$:**
- **Repeating Groups**: A single commercial booking contains multiple passengers; a passenger itinerary contains multiple flights; a check-in contains multiple baggage items.
- **Redundancy & Inconsistency**: Airport names, aircraft models, and route distances are repeated across every booked passenger ticket.
- **Insertion Anomaly**: An airport or aircraft cannot exist in the database unless an active booking is made on it.
- **Deletion Anomaly**: Deleting a passenger's booking deletes the physical flight schedule and aircraft definition from the system.

---

### Stage 1: First Normal Form (1NF)

> **Definition:** A relation $R$ is in 1NF if and only if all attribute domains are atomic (indivisible) and there are no repeating groups or multivalued attributes.

* **Resolution**: Flatten multivalued arrays (passengers, flight segments, baggage) into distinct rows.
* **Composite Candidate Key for flattened $R_{\text{1NF}}$**:
  $$K_{\text{1NF}} = \{ \text{booking\_ref}, \text{passenger\_id}, \text{flight\_no}, \text{seat\_no}, \text{baggage\_id} \}$$

* **Identified Functional Dependencies in 1NF**:
  - $K_{\text{1NF}} \rightarrow \text{All non-key attributes}$
  - $\{\text{booking\_ref}\} \rightarrow \text{booking\_date}$ *(Depends only on part of key)*
  - $\{\text{passenger\_id}\} \rightarrow \text{first\_name}, \text{last\_name}, \text{email}, \text{passport\_no}$ *(Depends only on part of key)*
  - $\{\text{flight\_no}, \text{sched\_dep}\} \rightarrow \text{dep\_airport}, \text{arr\_airport}, \text{aircraft\_id}$ *(Depends only on part of key)*
  - $\{\text{aircraft\_id}, \text{seat\_no}\} \rightarrow \text{seat\_class}$ *(Depends only on part of key)*

---

### Stage 2: Second Normal Form (2NF)

> **Definition:** A relation $R$ is in 2NF if it is in 1NF and **no non-prime attribute is partially dependent on any candidate key** of $R$ (i.e., every non-prime attribute is fully functionally dependent on the primary key).

* **Violation in 1NF**: The dependencies above show non-prime attributes depending on proper subsets of $K_{\text{1NF}}$.
* **2NF Decomposition**: Project the relation into independent relational entities:
  - `PASSENGER` ($\underline{\text{passenger\_id}}, \text{first\_name}, \text{last\_name}, \text{email}, \text{passport\_no}$)
  - `BOOKING` ($\underline{\text{booking\_id}}, \text{booking\_ref}, \text{passenger\_id}, \text{booking\_date}, \text{booking\_status}$)
  - `AIRCRAFT` ($\underline{\text{aircraft\_id}}, \text{model}, \text{total\_capacity}$)
  - `SEATS` ($\underline{\text{seat\_id}}, \text{aircraft\_id}, \text{seat\_number}, \text{seat\_class}$)
  - `FLIGHTS` ($\underline{\text{flight\_id}}, \text{dep\_airport}, \text{arr\_airport}, \text{aircraft\_id}, \text{sched\_dep}, \text{sched\_arr}, \text{status}$)
  - `TICKETS` ($\underline{\text{ticket\_id}}, \text{booking\_id}, \text{flight\_id}, \text{seat\_id}, \text{fare\_amount}, \text{status}$)
  - `PAYMENTS` ($\underline{\text{payment\_id}}, \text{booking\_id}, \text{amount\_paid}, \text{payment\_method}, \text{status}$)
  - `CHECKINS` ($\underline{\text{checkin\_id}}, \text{ticket\_id}, \text{checkin\_time}, \text{boarding\_pass}$)
  - `BAGGAGE` ($\underline{\text{baggage\_id}}, \text{checkin\_id}, \text{weight\_kg}, \text{excess\_fee}$)
  - `CANCELLATIONS` ($\underline{\text{cancellation\_id}}, \text{ticket\_id}, \text{cancel\_time}, \text{refund\_amount}$)

---

### Stage 3: Third Normal Form (3NF)

> **Definition:** A relation $R$ is in 3NF if it is in 2NF and **no non-prime attribute is transitively dependent on any candidate key** (i.e., $X \rightarrow Y$ and $Y \rightarrow Z$, where $Z$ is non-prime and $Y$ is not a superkey).

* **Violations Identified in 2NF Schemas**:
  1. **In `FLIGHTS`**:
     $$\text{flight\_id} \rightarrow (\text{dep\_airport}, \text{arr\_airport}) \rightarrow \text{distance\_km}$$
     The flight corridor distance depends on the pair of airports, not on individual scheduled flight instances. Furthermore, airport codes determine city, airport name, and country:
     $$\text{flight\_id} \rightarrow \text{dep\_airport} \rightarrow (\text{city}, \text{country}, \text{airport\_name})$$
     *Resolution*: Extract `AIRPORTS` and `ROUTES` tables.
     - `AIRPORTS` ($\underline{\text{airport\_code}}, \text{airport\_name}, \text{city}, \text{country}$)
     - `ROUTES` ($\underline{\text{route\_id}}, \text{origin\_airport}, \text{dest\_airport}, \text{distance\_km}$)
     - `FLIGHTS` retains only $\text{route\_id}$ as a foreign key: ($\underline{\text{flight\_id}}, \text{route\_id}, \text{aircraft\_id}, \dots$).

  2. **In `CHECKINS` & `BAGGAGE`**:
     $$\text{baggage\_id} \rightarrow \text{checkin\_id} \rightarrow \text{ticket\_id} \rightarrow \text{flight\_id}$$
     *Resolution*: Maintain strict parent-child hierarchies. `BAGGAGE` determines check-in custody, `CHECKINS` determines ticket authority, and `TICKETS` links directly to commercial bookings and operational flights.

---

## 3. Formal Functional Dependency Set ($F$)

The complete set of minimal, non-trivial functional dependencies governing the universe of discourse:

$$FD_1: \text{airport\_code} \rightarrow \text{airport\_name}, \text{city}, \text{country}$$
$$FD_2: \text{aircraft\_id} \rightarrow \text{model}, \text{total\_capacity}$$
$$FD_3: (\text{aircraft\_id}, \text{seat\_number}) \rightarrow \text{seat\_class}, \text{seat\_id}$$
$$FD_4: \text{route\_id} \rightarrow \text{origin\_airport}, \text{dest\_airport}, \text{distance\_km}$$
$$FD_5: (\text{origin\_airport}, \text{dest\_airport}) \rightarrow \text{route\_id}, \text{distance\_km}$$
$$FD_6: \text{flight\_id} \rightarrow \text{route\_id}, \text{aircraft\_id}, \text{scheduled\_departure}, \text{scheduled\_arrival}, \text{flight\_status}$$
$$FD_7: \text{passenger\_id} \rightarrow \text{first\_name}, \text{last\_name}, \text{email}, \text{passport\_number}$$
$$FD_8: \text{email} \rightarrow \text{passenger\_id}, \text{first\_name}, \text{last\_name}, \text{passport\_number}$$
$$FD_9: \text{passport\_number} \rightarrow \text{passenger\_id}, \text{first\_name}, \text{last\_name}, \text{email}$$
$$FD_{10}: \text{booking\_id} \rightarrow \text{booking\_ref}, \text{passenger\_id}, \text{booking\_date}, \text{booking\_status}$$
$$FD_{11}: \text{booking\_ref} \rightarrow \text{booking\_id}, \text{passenger\_id}, \text{booking\_date}, \text{booking\_status}$$
$$FD_{12}: \text{ticket\_id} \rightarrow \text{booking\_id}, \text{flight\_id}, \text{seat\_id}, \text{fare\_amount}, \text{ticket\_status}$$
$$FD_{13}: (\text{flight\_id}, \text{seat\_id}) \rightarrow \text{ticket\_id}, \text{booking\_id}, \text{fare\_amount}, \text{ticket\_status}$$
$$FD_{14}: \text{payment\_id} \rightarrow \text{booking\_id}, \text{amount\_paid}, \text{payment\_method}, \text{payment\_status}, \text{payment\_timestamp}$$
$$FD_{15}: \text{checkin\_id} \rightarrow \text{ticket\_id}, \text{checkin\_time}, \text{boarding\_pass}$$
$$FD_{16}: \text{boarding\_pass} \rightarrow \text{checkin\_id}, \text{ticket\_id}, \text{checkin\_time}$$
$$FD_{17}: \text{baggage\_id} \rightarrow \text{checkin\_id}, \text{weight\_kg}, \text{excess\_fee}$$
$$FD_{18}: \text{cancellation\_id} \rightarrow \text{ticket\_id}, \text{cancellation\_timestamp}, \text{refund\_amount}$$

---

## 4. Formal Proof of Properties

### Theorem 1: Lossless Join Decomposition
A decomposition of relation $R$ into $D = \{R_1, R_2\}$ is **lossless** with respect to functional dependency set $F$ if and only if the common attributes form a superkey of at least one of the decomposed relations:

$$R_1 \cap R_2 \rightarrow R_1 \quad \text{OR} \quad R_1 \cap R_2 \rightarrow R_2 \in F^+$$

**Inductive Verification on Schema:**
1. $\text{airports} \cap \text{routes} = \{\text{origin\_airport}\} \equiv \text{airport\_code}$.
   Since $\text{airport\_code} \rightarrow \text{airports}$ ($FD_1$), the join is **lossless**.
2. $\text{aircraft} \cap \text{seats} = \{\text{aircraft\_id}\}$.
   Since $\text{aircraft\_id} \rightarrow \text{aircraft}$ ($FD_2$), the join is **lossless**.
3. $\text{routes} \cap \text{flights} = \{\text{route\_id}\}$.
   Since $\text{route\_id} \rightarrow \text{routes}$ ($FD_4$), the join is **lossless**.
4. $\text{bookings} \cap \text{tickets} = \{\text{booking\_id}\}$.
   Since $\text{booking\_id} \rightarrow \text{bookings}$ ($FD_{10}$), the join is **lossless**.
5. $\text{tickets} \cap \text{checkins} = \{\text{ticket\_id}\}$.
   Since $\text{ticket\_id} \rightarrow \text{tickets}$ ($FD_{12}$), the join is **lossless**.

By induction, for every decomposition step, $R_i \cap R_j$ contains a candidate key of either $R_i$ or $R_j$. Thus, the universal relation can be reconstructed via natural join without generating spurious tuples.

---

### Theorem 2: Dependency Preservation
A decomposition $D = \{R_1, R_2, \dots, R_k\}$ is **dependency-preserving** if:

$$F^+ = \left( \bigcup_{i=1}^k \pi_{R_i}(F) \right)^+$$

Every functional dependency $X \rightarrow Y \in F$ is enforced locally within a single projected table $R_i$ through primary keys or unique index constraints:
- $FD_1 \in \pi_{\text{airports}}$ (Enforced by `PRIMARY KEY (airport_code)`)
- $FD_2 \in \pi_{\text{aircraft}}$ (Enforced by `PRIMARY KEY (aircraft_id)`)
- $FD_3 \in \pi_{\text{seats}}$ (Enforced by `UNIQUE (aircraft_id, seat_number)`)
- $FD_4 \in \pi_{\text{routes}}$ (Enforced by `PRIMARY KEY (route_id)`)
- $FD_6 \in \pi_{\text{flights}}$ (Enforced by `PRIMARY KEY (flight_id)`)
- $FD_7, FD_8, FD_9 \in \pi_{\text{passengers}}$ (Enforced by `PK` and `UNIQUE` constraints)
- $FD_{10}, FD_{11} \in \pi_{\text{bookings}}$ (Enforced by `PK` and `UNIQUE (booking_ref)`)
- $FD_{12}, FD_{13} \in \pi_{\text{tickets}}$ (Enforced by `PK` and `UNIQUE (flight_id, seat_id)`)
- $FD_{14} \in \pi_{\text{payments}}$ (Enforced by `PRIMARY KEY (payment_id)`)
- $FD_{15}, FD_{16} \in \pi_{\text{checkins}}$ (Enforced by `PK` and `UNIQUE (ticket_id)`)
- $FD_{17} \in \pi_{\text{baggage}}$ (Enforced by `PRIMARY KEY (baggage_id)`)
- $FD_{18} \in \pi_{\text{cancellations}}$ (Enforced by `PK` and `UNIQUE (ticket_id)`)

Since every $FD \in F$ is directly projected and preserved within its respective table, the decomposition is **100% dependency-preserving**.

---

### Theorem 3: Strict BCNF Compliance
In our projected schema:
- For every table $R_i$ and for every non-trivial functional dependency $X \rightarrow Y$ in $\pi_{R_i}(F)$, $X$ is a **superkey** of $R_i$.
- Therefore, the schema not only satisfies 3NF, but also satisfies **Boyce-Codd Normal Form (BCNF)** without suffering from any dependency loss.
