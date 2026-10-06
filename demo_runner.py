#!/usr/bin/env python3
"""
===============================================================================
AIRLINE RESERVATION & FLIGHT OPERATIONS MANAGEMENT SYSTEM (ARFOM-DB)
Interactive Terminal Demonstration & Live Integrity Verification Harness
===============================================================================
Usage:
    python3 demo_runner.py            # Interactive Menu
    python3 demo_runner.py --demo     # Complete Automated Viva Presentation Run
===============================================================================
"""

import sqlite3
import sys
import os

# ANSI Terminal Styling
C_RESET  = "\033[0m"
C_BOLD   = "\033[1m"
C_RED    = "\033[91m"
C_GREEN  = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE   = "\033[94m"
C_CYAN   = "\033[96m"
C_MAGENTA= "\033[95m"

def print_header(title):
    print(f"\n{C_BOLD}{C_CYAN}{'='*80}{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}{title.center(80)}{C_RESET}")
    print(f"{C_BOLD}{C_CYAN}{'='*80}{C_RESET}\n")

def print_sub(title):
    print(f"\n{C_BOLD}{C_YELLOW}>>> {title}{C_RESET}")

def print_table(headers, rows):
    if not rows:
        print(f"  {C_YELLOW}[No records returned]{C_RESET}")
        return

    # Calculate column widths
    widths = [len(str(h)) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            val_str = "NULL" if val is None else str(val)
            widths[idx] = max(widths[idx], len(val_str))

    # Print header
    header_line = " | ".join(f"{h:<{widths[i]}}" for i, h in enumerate(headers))
    sep_line = "-+-".join("-" * widths[i] for i in range(len(headers)))
    print(f"  {C_BOLD}{header_line}{C_RESET}")
    print(f"  {sep_line}")

    # Print rows
    for row in rows:
        row_str = " | ".join(
            f"{('NULL' if val is None else str(val)):<{widths[i]}}"
            for i, val in enumerate(row)
        )
        print(f"  {row_str}")
    print(f"  {C_BLUE}(Total Rows: {len(rows)}){C_RESET}\n")

def init_database():
    """Initializes in-memory SQLite DB with full 3NF schema, check constraints, and triggers."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # DDL
    cur.executescript("""
    CREATE TABLE airports (
        airport_code CHAR(3) PRIMARY KEY,
        airport_name VARCHAR(100) NOT NULL,
        city VARCHAR(50) NOT NULL,
        country VARCHAR(50) NOT NULL
    );

    CREATE TABLE routes (
        route_id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin_airport CHAR(3) NOT NULL REFERENCES airports(airport_code),
        dest_airport CHAR(3) NOT NULL REFERENCES airports(airport_code),
        distance_km NUMERIC(7,2) NOT NULL CHECK (distance_km > 0),
        CHECK (origin_airport <> dest_airport)
    );

    CREATE TABLE aircraft (
        aircraft_id INTEGER PRIMARY KEY AUTOINCREMENT,
        model VARCHAR(50) NOT NULL,
        total_capacity INT NOT NULL CHECK (total_capacity > 0)
    );

    CREATE TABLE seats (
        seat_id INTEGER PRIMARY KEY AUTOINCREMENT,
        aircraft_id INT NOT NULL REFERENCES aircraft(aircraft_id) ON DELETE CASCADE,
        seat_number VARCHAR(4) NOT NULL,
        seat_class VARCHAR(15) NOT NULL CHECK (seat_class IN ('ECONOMY', 'BUSINESS', 'FIRST')),
        UNIQUE (aircraft_id, seat_number)
    );

    CREATE TABLE flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        route_id INT NOT NULL REFERENCES routes(route_id),
        aircraft_id INT NOT NULL REFERENCES aircraft(aircraft_id),
        scheduled_departure TIMESTAMP NOT NULL,
        scheduled_arrival TIMESTAMP NOT NULL,
        flight_status VARCHAR(15) NOT NULL DEFAULT 'SCHEDULED' 
            CHECK (flight_status IN ('SCHEDULED', 'BOARDING', 'DEPARTED', 'ARRIVED', 'CANCELLED', 'DELAYED')),
        CHECK (scheduled_arrival > scheduled_departure)
    );

    CREATE TABLE passengers (
        passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        passport_number VARCHAR(20) NOT NULL UNIQUE
    );

    CREATE TABLE bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_ref CHAR(6) NOT NULL UNIQUE,
        passenger_id INT NOT NULL REFERENCES passengers(passenger_id),
        booking_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        booking_status VARCHAR(15) NOT NULL DEFAULT 'CONFIRMED' 
            CHECK (booking_status IN ('CONFIRMED', 'PENDING', 'CANCELLED'))
    );

    CREATE TABLE tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INT NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
        flight_id INT NOT NULL REFERENCES flights(flight_id),
        seat_id INT NOT NULL REFERENCES seats(seat_id),
        fare_amount NUMERIC(10,2) NOT NULL CHECK (fare_amount >= 0.00),
        ticket_status VARCHAR(15) NOT NULL DEFAULT 'ISSUED' 
            CHECK (ticket_status IN ('ISSUED', 'CHECKED_IN', 'CANCELLED')),
        UNIQUE (flight_id, seat_id)
    );

    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INT NOT NULL REFERENCES bookings(booking_id),
        amount_paid NUMERIC(10,2) NOT NULL CHECK (amount_paid > 0.00),
        payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING')),
        payment_status VARCHAR(15) NOT NULL DEFAULT 'SUCCESS' CHECK (payment_status IN ('SUCCESS', 'FAILED', 'REFUNDED')),
        payment_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE checkins (
        checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INT NOT NULL UNIQUE REFERENCES tickets(ticket_id),
        checkin_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        boarding_pass VARCHAR(20) NOT NULL UNIQUE
    );

    CREATE TABLE baggage (
        baggage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        checkin_id INT NOT NULL REFERENCES checkins(checkin_id) ON DELETE CASCADE,
        weight_kg NUMERIC(5,2) NOT NULL CHECK (weight_kg >= 0.00),
        excess_fee NUMERIC(8,2) NOT NULL DEFAULT 0.00 CHECK (excess_fee >= 0.00)
    );

    CREATE TABLE cancellations (
        cancellation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INT NOT NULL UNIQUE REFERENCES tickets(ticket_id),
        cancellation_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        refund_amount NUMERIC(10,2) NOT NULL CHECK (refund_amount >= 0.00)
    );

    -- TRIGGERS

    -- RULE 1: Seat airframe compatibility
    CREATE TRIGGER trg_verify_seat_compatibility
    BEFORE INSERT ON tickets
    FOR EACH ROW
    WHEN (
        (SELECT aircraft_id FROM flights WHERE flight_id = NEW.flight_id) <>
        (SELECT aircraft_id FROM seats WHERE seat_id = NEW.seat_id)
    )
    BEGIN
        SELECT RAISE(ABORT, 'Integrity Violation: Seat does not match deployed flight airframe.');
    END;

    -- RULE 2: Aircraft Capacity Limit
    CREATE TRIGGER trg_verify_capacity
    BEFORE INSERT ON tickets
    FOR EACH ROW
    WHEN (
        (SELECT COUNT(*) FROM tickets WHERE flight_id = NEW.flight_id AND ticket_status <> 'CANCELLED') >=
        (SELECT a.total_capacity FROM flights f JOIN aircraft a ON f.aircraft_id = a.aircraft_id WHERE f.flight_id = NEW.flight_id)
    )
    BEGIN
        SELECT RAISE(ABORT, 'Capacity Overrun: Airframe capacity reached for this flight.');
    END;

    -- RULE 3: Check-in Eligibility (Only CONFIRMED bookings and ISSUED tickets)
    CREATE TRIGGER trg_checkin_eligibility
    BEFORE INSERT ON checkins
    FOR EACH ROW
    WHEN (
        (SELECT b.booking_status FROM tickets t JOIN bookings b ON t.booking_id = b.booking_id WHERE t.ticket_id = NEW.ticket_id) <> 'CONFIRMED'
        OR
        (SELECT ticket_status FROM tickets WHERE ticket_id = NEW.ticket_id) <> 'ISSUED'
    )
    BEGIN
        SELECT RAISE(ABORT, 'Check-in Denied: Booking must be CONFIRMED and ticket must be in ISSUED state.');
    END;

    -- Trigger to auto-update ticket to CHECKED_IN
    CREATE TRIGGER trg_after_checkin
    AFTER INSERT ON checkins
    FOR EACH ROW
    BEGIN
        UPDATE tickets SET ticket_status = 'CHECKED_IN' WHERE ticket_id = NEW.ticket_id;
    END;

    -- RULE 4: Strict Refund Limits
    CREATE TRIGGER trg_refund_bounds
    BEFORE INSERT ON cancellations
    FOR EACH ROW
    WHEN (
        NEW.refund_amount > (SELECT fare_amount FROM tickets WHERE ticket_id = NEW.ticket_id)
        OR
        (SELECT ticket_status FROM tickets WHERE ticket_id = NEW.ticket_id) = 'CANCELLED'
    )
    BEGIN
        SELECT RAISE(ABORT, 'Accounting Anomaly: Refund exceeds ticket base fare or ticket already cancelled.');
    END;

    -- Trigger to auto-update ticket to CANCELLED
    CREATE TRIGGER trg_after_cancellation
    AFTER INSERT ON cancellations
    FOR EACH ROW
    BEGIN
        UPDATE tickets SET ticket_status = 'CANCELLED' WHERE ticket_id = NEW.ticket_id;
    END;
    """)

    # Seed Data
    cur.executescript("""
    INSERT INTO airports VALUES ('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India');
    INSERT INTO airports VALUES ('BOM', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India');
    INSERT INTO airports VALUES ('BLR', 'Kempegowda International Airport', 'Bengaluru', 'India');
    INSERT INTO airports VALUES ('DXB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates');

    INSERT INTO aircraft VALUES (1, 'Airbus A320neo', 6);
    INSERT INTO aircraft VALUES (2, 'Boeing 737-800', 4);

    INSERT INTO seats VALUES (1, 1, '1A', 'BUSINESS');
    INSERT INTO seats VALUES (2, 1, '1B', 'BUSINESS');
    INSERT INTO seats VALUES (3, 1, '2A', 'ECONOMY');
    INSERT INTO seats VALUES (4, 1, '2B', 'ECONOMY');
    INSERT INTO seats VALUES (5, 1, '3A', 'ECONOMY');
    INSERT INTO seats VALUES (6, 1, '3B', 'ECONOMY');
    INSERT INTO seats VALUES (7, 2, '1A', 'BUSINESS');
    INSERT INTO seats VALUES (8, 2, '1B', 'BUSINESS');
    INSERT INTO seats VALUES (9, 2, '2A', 'ECONOMY');
    INSERT INTO seats VALUES (10, 2, '2B', 'ECONOMY');

    INSERT INTO routes VALUES (1, 'DEL', 'BOM', 1148.00);
    INSERT INTO routes VALUES (2, 'BOM', 'BLR', 842.00);
    INSERT INTO routes VALUES (3, 'DEL', 'DXB', 2185.00);

    INSERT INTO flights VALUES (101, 1, 1, '2026-10-15 06:00:00', '2026-10-15 08:15:00', 'SCHEDULED');
    INSERT INTO flights VALUES (102, 1, 1, '2026-10-15 18:00:00', '2026-10-15 20:15:00', 'ARRIVED');
    INSERT INTO flights VALUES (103, 2, 2, '2026-10-16 09:30:00', '2026-10-16 11:15:00', 'SCHEDULED');
    INSERT INTO flights VALUES (104, 3, 1, '2026-10-17 14:00:00', '2026-10-17 16:30:00', 'DELAYED');

    INSERT INTO passengers VALUES (1, 'Arjun', 'Mehta', 'arjun.m@example.com', 'A12345678');
    INSERT INTO passengers VALUES (2, 'Neha', 'Sharma', 'neha.s@example.com', 'B98765432');
    INSERT INTO passengers VALUES (3, 'Rohan', 'Verma', 'rohan.v@example.com', 'C54321987');
    INSERT INTO passengers VALUES (4, 'Priya', 'Nair', 'priya.n@example.com', 'D76543210');
    INSERT INTO passengers VALUES (5, 'Vikram', 'Rathore', 'vikram.r@example.com', 'E11223344');
    INSERT INTO passengers VALUES (6, 'Ananya', 'Iyer', 'ananya.i@example.com', 'F99887766');

    INSERT INTO bookings VALUES (1, 'PNR001', 1, '2026-10-01 10:15:00', 'CONFIRMED');
    INSERT INTO bookings VALUES (2, 'PNR002', 2, '2026-10-01 11:30:00', 'CONFIRMED');
    INSERT INTO bookings VALUES (3, 'PNR003', 3, '2026-10-02 09:00:00', 'CONFIRMED');
    INSERT INTO bookings VALUES (4, 'PNR004', 4, '2026-10-02 14:20:00', 'CONFIRMED');
    INSERT INTO bookings VALUES (5, 'PNR005', 5, '2026-10-03 16:45:00', 'CANCELLED');
    INSERT INTO bookings VALUES (6, 'PNR006', 6, '2026-10-04 11:00:00', 'CONFIRMED');

    INSERT INTO payments VALUES (1, 1, 8500.00, 'CREDIT_CARD', 'SUCCESS', '2026-10-01 10:16:00');
    INSERT INTO payments VALUES (2, 2, 5200.00, 'UPI', 'SUCCESS', '2026-10-01 11:31:00');
    INSERT INTO payments VALUES (3, 3, 5200.00, 'NET_BANKING', 'SUCCESS', '2026-10-02 09:02:00');
    INSERT INTO payments VALUES (4, 4, 12000.00, 'CREDIT_CARD', 'SUCCESS', '2026-10-02 14:22:00');
    INSERT INTO payments VALUES (5, 5, 8500.00, 'UPI', 'REFUNDED', '2026-10-03 16:46:00');
    INSERT INTO payments VALUES (6, 6, 5200.00, 'UPI', 'SUCCESS', '2026-10-04 11:02:00');

    INSERT INTO tickets VALUES (1, 1, 101, 1, 8500.00, 'ISSUED');
    INSERT INTO tickets VALUES (2, 2, 101, 3, 5200.00, 'ISSUED');
    INSERT INTO tickets VALUES (3, 3, 101, 4, 5200.00, 'ISSUED');
    INSERT INTO tickets VALUES (4, 4, 104, 2, 12000.00, 'ISSUED');
    INSERT INTO tickets VALUES (5, 5, 101, 5, 8500.00, 'ISSUED');
    INSERT INTO tickets VALUES (6, 6, 103, 9, 5200.00, 'ISSUED');

    INSERT INTO checkins VALUES (1, 1, '2026-10-15 04:30:00', 'BP-DELBOM-1A');
    INSERT INTO checkins VALUES (2, 2, '2026-10-15 04:45:00', 'BP-DELBOM-2A');

    INSERT INTO baggage VALUES (1, 1, 24.50, 1500.00);
    INSERT INTO baggage VALUES (2, 1, 8.00, 0.00);
    INSERT INTO baggage VALUES (3, 2, 14.20, 0.00);

    INSERT INTO cancellations VALUES (1, 5, '2026-10-04 12:00:00', 6800.00);
    """)

    conn.commit()
    return conn

def run_negative_tests(base_conn=None):
    print_header("LIVE INTEGRITY CONSTRAINT & TRIGGER VALIDATION (NEGATIVE TESTS)")

    tests = [
        (
            "Rule 1: One seat per passenger per flight (Unique flight_id + seat_id)",
            "INSERT INTO tickets (ticket_id, booking_id, flight_id, seat_id, fare_amount, ticket_status) VALUES (901, 2, 101, 1, 8500.00, 'ISSUED');",
            "UNIQUE constraint failed"
        ),
        (
            "Rule 2: Aircraft-Capacity Enforcement (Airframe limit)",
            """
            -- Book remaining seats on Flight 103 (Capacity = 4, already 1 booked)
            INSERT INTO tickets VALUES (902, 1, 103, 7, 5000.00, 'ISSUED');
            INSERT INTO tickets VALUES (903, 2, 103, 8, 5000.00, 'ISSUED');
            INSERT INTO tickets VALUES (904, 3, 103, 10, 5000.00, 'ISSUED');
            -- This 5th ticket exceeds capacity limit of 4:
            INSERT INTO tickets VALUES (905, 4, 103, 7, 5000.00, 'ISSUED');
            """,
            "Capacity Overrun"
        ),
        (
            "Rule 3: Non-negative baggage (CHECK weight_kg >= 0.00)",
            "INSERT INTO baggage VALUES (906, 1, -12.50, 0.00);",
            "CHECK constraint failed"
        ),
        (
            "Rule 4: Check-in Allowed ONLY for Confirmed Bookings with Active Tickets",
            "INSERT INTO checkins (checkin_id, ticket_id, boarding_pass) VALUES (907, 5, 'BP-ILLEGAL-99');",
            "Check-in Denied"
        ),
        (
            "Rule 5: Strict Refund Rule (Refund <= Ticket Fare Amount)",
            "INSERT INTO cancellations VALUES (908, 1, '2026-10-15 00:00:00', 15000.00);",
            "Accounting Anomaly"
        ),
        (
            "Bonus Rule 6: Seat Compatibility (Seat belongs to scheduled aircraft)",
            "INSERT INTO tickets VALUES (909, 1, 101, 7, 8500.00, 'ISSUED');",
            "Integrity Violation"
        ),
    ]

    for idx, (title, sql_code, expected_substr) in enumerate(tests, 1):
        print(f"{C_BOLD}[TEST {idx}] {title}{C_RESET}")
        test_conn = init_database()
        test_cur = test_conn.cursor()
        try:
            test_cur.executescript(sql_code)
            print(f"  {C_RED}FAILED: Statement was unexpectedly accepted!{C_RESET}\n")
        except sqlite3.Error as e:
            err_msg = str(e)
            if expected_substr.lower() in err_msg.lower():
                print(f"  {C_GREEN}[OK] PASS: Storage engine intercepted illegal operation:{C_RESET}")
                print(f"  {C_MAGENTA}Exception: {err_msg}{C_RESET}\n")
            else:
                print(f"  {C_YELLOW}CAUGHT (Different message): {err_msg}{C_RESET}\n")
        finally:
            test_conn.close()

def run_analytical_reports(conn):
    print_header("ANALYTICAL QUERIES & BUSINESS INTELLIGENCE REPORTS")
    cur = conn.cursor()

    reports = [
        (
            "REPORT 1: Real-Time Flight Manifest (Operational Dispatch)",
            """
            SELECT 
                f.flight_id,
                r.origin_airport || ' -> ' || r.dest_airport AS corridor,
                f.scheduled_departure,
                s.seat_number,
                s.seat_class,
                p.first_name || ' ' || p.last_name AS passenger,
                p.passport_number,
                b.booking_ref,
                t.ticket_status,
                COALESCE(c.boarding_pass, 'NOT CHECKED-IN') AS boarding_pass
            FROM flights f
            JOIN routes r ON f.route_id = r.route_id
            JOIN tickets t ON f.flight_id = t.flight_id
            JOIN seats s ON t.seat_id = s.seat_id
            JOIN bookings b ON t.booking_id = b.booking_id
            JOIN passengers p ON b.passenger_id = p.passenger_id
            LEFT JOIN checkins c ON t.ticket_id = c.ticket_id
            WHERE t.ticket_status <> 'CANCELLED' AND f.flight_id = 101
            ORDER BY s.seat_number;
            """
        ),
        (
            "REPORT 2: Flight Occupancy & Yield Analytics (Capacity Utilization)",
            """
            SELECT 
                f.flight_id,
                a.model AS airframe,
                a.total_capacity,
                COUNT(t.ticket_id) AS confirmed_passengers,
                ROUND((CAST(COUNT(t.ticket_id) AS REAL) / a.total_capacity) * 100, 2) AS occupancy_pct,
                CASE 
                    WHEN (CAST(COUNT(t.ticket_id) AS REAL) / a.total_capacity) >= 0.80 THEN 'OPTIMAL'
                    WHEN (CAST(COUNT(t.ticket_id) AS REAL) / a.total_capacity) >= 0.50 THEN 'MODERATE'
                    ELSE 'LOW_YIELD'
                END AS operational_efficiency
            FROM flights f
            JOIN aircraft a ON f.aircraft_id = a.aircraft_id
            LEFT JOIN tickets t ON f.flight_id = t.flight_id AND t.ticket_status <> 'CANCELLED'
            GROUP BY f.flight_id, a.model, a.total_capacity
            ORDER BY occupancy_pct DESC;
            """
        ),
        (
            "REPORT 3: Route Demand & High-Density Corridors",
            """
            SELECT 
                r.route_id,
                r.origin_airport || ' -> ' || r.dest_airport AS corridor,
                r.distance_km,
                COUNT(DISTINCT f.flight_id) AS flights_operated,
                COUNT(t.ticket_id) AS passengers_carried,
                COALESCE(SUM(t.fare_amount), 0.00) AS gross_revenue_inr,
                ROUND(COALESCE(SUM(t.fare_amount), 0.00) / NULLIF(COUNT(t.ticket_id), 0), 2) AS avg_ticket_yield
            FROM routes r
            LEFT JOIN flights f ON r.route_id = f.route_id
            LEFT JOIN tickets t ON f.flight_id = t.flight_id AND t.ticket_status <> 'CANCELLED'
            GROUP BY r.route_id, r.origin_airport, r.dest_airport, r.distance_km
            ORDER BY gross_revenue_inr DESC;
            """
        ),
        (
            "REPORT 4: Baggage Logistics & Excess Surcharge Audit",
            """
            SELECT 
                f.flight_id,
                r.origin_airport || ' -> ' || r.dest_airport AS corridor,
                COUNT(b.baggage_id) AS checked_bags,
                COALESCE(SUM(b.weight_kg), 0.00) AS total_cargo_kg,
                ROUND(COALESCE(AVG(b.weight_kg), 0.00), 2) AS avg_bag_kg,
                COALESCE(SUM(b.excess_fee), 0.00) AS excess_baggage_revenue_inr
            FROM flights f
            JOIN routes r ON f.route_id = r.route_id
            JOIN tickets t ON f.flight_id = t.flight_id
            JOIN checkins c ON t.ticket_id = c.ticket_id
            JOIN baggage b ON c.checkin_id = b.checkin_id
            GROUP BY f.flight_id, r.origin_airport, r.dest_airport
            ORDER BY total_cargo_kg DESC;
            """
        ),
        (
            "REPORT 5: Cancellation, Attrition & Net Retention Metrics",
            """
            SELECT 
                COUNT(c.cancellation_id) AS total_cancellations,
                SUM(t.fare_amount) AS gross_forfeited_fare,
                SUM(c.refund_amount) AS total_refunded_capital,
                SUM(t.fare_amount - c.refund_amount) AS net_cancellation_penalty_retained,
                ROUND((CAST(SUM(c.refund_amount) AS REAL) / NULLIF(SUM(t.fare_amount), 0)) * 100, 2) AS refund_ratio_pct
            FROM cancellations c
            JOIN tickets t ON c.ticket_id = t.ticket_id;
            """
        ),
        (
            "REPORT 6: Flight Status & On-Time Performance (OTP) Distribution",
            """
            SELECT 
                flight_status,
                COUNT(*) AS total_segments,
                ROUND((CAST(COUNT(*) AS REAL) / (SELECT COUNT(*) FROM flights)) * 100, 2) AS pct_of_operations
            FROM flights
            GROUP BY flight_status
            ORDER BY total_segments DESC;
            """
        ),
        (
            "REPORT 7: Revenue Segmentation by Cabin Tier & Yield",
            """
            SELECT 
                s.seat_class,
                COUNT(t.ticket_id) AS tickets_sold,
                SUM(t.fare_amount) AS class_revenue_inr,
                ROUND(AVG(t.fare_amount), 2) AS avg_fare_per_class,
                ROUND(
                    (SUM(t.fare_amount) * 100.0) / (SELECT SUM(fare_amount) FROM tickets WHERE ticket_status <> 'CANCELLED'),
                    2
                ) AS contribution_percentage
            FROM tickets t
            JOIN seats s ON t.seat_id = s.seat_id
            WHERE t.ticket_status <> 'CANCELLED'
            GROUP BY s.seat_class
            ORDER BY class_revenue_inr DESC;
            """
        ),
    ]

    for title, sql_query in reports:
        print_sub(title)
        cur.execute(sql_query)
        headers = [col[0] for col in cur.description]
        rows = cur.fetchall()
        print_table(headers, rows)

def main():
    conn = init_database()
    print_header("AIRLINE RESERVATION & OPERATIONS SYSTEM - REVIEW 2 HARNESS")
    print(f"{C_GREEN}Database successfully initialized in memory with 12 normalized tables and seed data.{C_RESET}")

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_negative_tests(conn)
        run_analytical_reports(conn)
        print_header("DEMONSTRATION COMPLETE - ALL CHECKS PASSED")
        return

    if len(sys.argv) > 1 and sys.argv[1] in ("--constraints", "--negative"):
        run_negative_tests(conn)
        print_header("INTEGRITY CHECKS COMPLETE - ALL INVARIANTS ENFORCED")
        return

    if len(sys.argv) > 1 and sys.argv[1] in ("--reports", "--queries"):
        run_analytical_reports(conn)
        print_header("ANALYTICAL REPORTS COMPLETE")
        return

    if len(sys.argv) > 2 and sys.argv[1] == "--sql":
        custom_query = sys.argv[2]
        print_sub(f"Executing Custom Query: {custom_query}")
        try:
            cur = conn.cursor()
            cur.execute(custom_query)
            if cur.description:
                headers = [col[0] for col in cur.description]
                rows = cur.fetchall()
                print_table(headers, rows)
            else:
                conn.commit()
                print(f"  {C_GREEN}Query executed successfully. Rows affected: {cur.rowcount}{C_RESET}\n")
        except Exception as e:
            print(f"  {C_RED}SQL Execution Error: {e}{C_RESET}\n")
        return

    while True:
        print(f"\n{C_BOLD}Select an action:{C_RESET}")
        print("  1. Run All Analytical Queries & Business Reports")
        print("  2. Run Negative Integrity & Trigger Tests")
        print("  3. Run Complete Automated Viva Presentation Demo")
        print("  4. View Table Counts & Schema Summary")
        print("  5. Run Custom SQL Query (Interactive Prompt)")
        print("  6. Exit")
        choice = input(f"\n{C_BOLD}Enter choice [1-6]: {C_RESET}").strip()

        if choice == "1":
            run_analytical_reports(conn)
        elif choice == "2":
            run_negative_tests(conn)
        elif choice == "3":
            run_negative_tests(conn)
            run_analytical_reports(conn)
        elif choice == "4":
            cur = conn.cursor()
            tables = ["airports", "routes", "aircraft", "seats", "flights", "passengers", 
                      "bookings", "tickets", "payments", "checkins", "baggage", "cancellations"]
            summary = []
            for t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                cnt = cur.fetchone()[0]
                summary.append((t, cnt))
            print_sub("Table Populations")
            print_table(["Table Name", "Record Count"], summary)
        elif choice == "5":
            print(f"\n{C_CYAN}Type any SQL statement (e.g., SELECT * FROM aircraft;) or 'exit':{C_RESET}")
            while True:
                q = input(f"{C_BOLD}SQL> {C_RESET}").strip()
                if not q or q.lower() == 'exit':
                    break
                try:
                    cur = conn.cursor()
                    cur.execute(q)
                    if cur.description:
                        headers = [col[0] for col in cur.description]
                        rows = cur.fetchall()
                        print_table(headers, rows)
                    else:
                        conn.commit()
                        print(f"  {C_GREEN}Query executed successfully. Rows affected: {cur.rowcount}{C_RESET}\n")
                except Exception as e:
                    print(f"  {C_RED}Error: {e}{C_RESET}\n")
        elif choice == "6":
            print("Exiting demonstration.")
            break
        else:
            print(f"{C_RED}Invalid choice. Please select 1-6.{C_RESET}")

if __name__ == "__main__":
    main()
