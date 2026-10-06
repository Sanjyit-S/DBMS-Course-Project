#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB COMPREHENSIVE SEED & DATA EXPORTER
Populates 60+ rows across all 12 tables and generates JSON cache for UI.
===============================================================================
"""

import sqlite3
import json
import os

DB_PATH = "workbench/arfom.db"
JSON_PATH = "workbench/initial_data.json"

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # Create Schema
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
        flight_number VARCHAR(10) NOT NULL,
        route_id INT NOT NULL REFERENCES routes(route_id),
        aircraft_id INT NOT NULL REFERENCES aircraft(aircraft_id) ON DELETE RESTRICT,
        scheduled_departure TIMESTAMP NOT NULL,
        scheduled_arrival TIMESTAMP NOT NULL,
        flight_status VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED' 
            CHECK (flight_status IN ('SCHEDULED', 'BOARDING', 'DEPARTED', 'DELAYED', 'COMPLETED', 'CANCELLED')),
        CHECK (scheduled_arrival > scheduled_departure)
    );

    CREATE TABLE passengers (
        passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL UNIQUE,
        passport_number VARCHAR(20) NOT NULL UNIQUE,
        phone VARCHAR(20) NOT NULL,
        nationality VARCHAR(50) NOT NULL DEFAULT 'India'
    );

    CREATE TABLE bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_ref CHAR(6) NOT NULL UNIQUE,
        booking_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        booking_status VARCHAR(20) NOT NULL DEFAULT 'CONFIRMED'
            CHECK (booking_status IN ('PENDING', 'CONFIRMED', 'CANCELLED'))
    );

    CREATE TABLE tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INT NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
        flight_id INT NOT NULL REFERENCES flights(flight_id) ON DELETE RESTRICT,
        seat_id INT NOT NULL REFERENCES seats(seat_id),
        passenger_id INT NOT NULL REFERENCES passengers(passenger_id),
        fare_amount NUMERIC(10,2) NOT NULL CHECK (fare_amount >= 0.00),
        ticket_status VARCHAR(20) NOT NULL DEFAULT 'ISSUED'
            CHECK (ticket_status IN ('ISSUED', 'CHECKED_IN', 'BOARDED', 'CANCELLED')),
        UNIQUE (flight_id, seat_id)
    );

    CREATE TABLE payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_id INT NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
        amount NUMERIC(10,2) NOT NULL CHECK (amount > 0.00),
        payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING')),
        payment_status VARCHAR(20) NOT NULL DEFAULT 'SUCCESS' CHECK (payment_status IN ('SUCCESS', 'FAILED', 'REFUNDED')),
        transaction_reference VARCHAR(50) NOT NULL UNIQUE,
        payment_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE checkins (
        checkin_id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INT NOT NULL UNIQUE REFERENCES tickets(ticket_id) ON DELETE CASCADE,
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

    -- Secondary B-Tree Indexes
    CREATE INDEX idx_flights_search ON flights(route_id, scheduled_departure, flight_status);
    CREATE INDEX idx_bookings_pnr ON bookings(booking_ref);
    CREATE INDEX idx_tickets_booking ON tickets(booking_id);
    CREATE INDEX idx_tickets_flight ON tickets(flight_id);
    CREATE INDEX idx_passengers_email ON passengers(email);

    -- Master Operational Manifest View (60+ rows)
    CREATE VIEW view_master_manifest AS
    SELECT 
        t.ticket_id,
        b.booking_ref,
        p.first_name || ' ' || p.last_name AS passenger_name,
        p.email,
        f.flight_number,
        r.origin_airport || ' -> ' || r.dest_airport AS route,
        f.scheduled_departure,
        f.flight_status,
        s.seat_number,
        s.seat_class,
        t.fare_amount,
        t.ticket_status,
        pay.payment_method,
        COALESCE(c.boarding_pass, 'NOT CHECKED IN') AS boarding_pass,
        COALESCE(bag.weight_kg, 0.00) AS baggage_kg,
        COALESCE(can.refund_amount, 0.00) AS refund_amount
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    JOIN passengers p ON t.passenger_id = p.passenger_id
    JOIN flights f ON t.flight_id = f.flight_id
    JOIN routes r ON f.route_id = r.route_id
    JOIN seats s ON t.seat_id = s.seat_id
    LEFT JOIN payments pay ON b.booking_id = pay.booking_id
    LEFT JOIN checkins c ON t.ticket_id = c.ticket_id
    LEFT JOIN baggage bag ON c.checkin_id = bag.checkin_id
    LEFT JOIN cancellations can ON t.ticket_id = can.ticket_id
    ORDER BY t.ticket_id ASC;
    """)

    # 1. Airports (10)
    airports = [
        ('DEL', 'Indira Gandhi International Airport', 'New Delhi', 'India'),
        ('BOM', 'Chhatrapati Shivaji Maharaj International Airport', 'Mumbai', 'India'),
        ('BLR', 'Kempegowda International Airport', 'Bengaluru', 'India'),
        ('DXB', 'Dubai International Airport', 'Dubai', 'United Arab Emirates'),
        ('SIN', 'Singapore Changi Airport', 'Singapore', 'Singapore'),
        ('LHR', 'London Heathrow Airport', 'London', 'United Kingdom'),
        ('HYD', 'Rajiv Gandhi International Airport', 'Hyderabad', 'India'),
        ('MAA', 'Chennai International Airport', 'Chennai', 'India'),
        ('CCU', 'Netaji Subhash Chandra Bose International Airport', 'Kolkata', 'India'),
        ('GOI', 'Dabolim International Airport', 'Goa', 'India')
    ]
    cur.executemany("INSERT INTO airports VALUES (?, ?, ?, ?);", airports)

    # 2. Routes (12)
    routes = [
        ('DEL', 'BOM', 1148.00),
        ('BOM', 'DEL', 1148.00),
        ('DEL', 'BLR', 1740.00),
        ('BLR', 'DEL', 1740.00),
        ('BOM', 'BLR', 842.00),
        ('BLR', 'BOM', 842.00),
        ('DEL', 'DXB', 2185.00),
        ('BOM', 'DXB', 1928.00),
        ('BLR', 'SIN', 3175.00),
        ('DEL', 'LHR', 6718.00),
        ('HYD', 'DEL', 1253.00),
        ('MAA', 'BOM', 1032.00)
    ]
    cur.executemany("INSERT INTO routes (origin_airport, dest_airport, distance_km) VALUES (?, ?, ?);", routes)

    # 3. Aircraft (5)
    aircraft = [
        ('Airbus A320neo', 180),
        ('Boeing 737-800', 160),
        ('Boeing 777-300ER', 296),
        ('Airbus A321LR', 220),
        ('Boeing 787-9 Dreamliner', 248)
    ]
    cur.executemany("INSERT INTO aircraft (model, total_capacity) VALUES (?, ?);", aircraft)

    # 4. Seats (72 seats across aircraft)
    seats = []
    # Aircraft 1 (A320neo): 30 seats
    for r in range(1, 3):
        for c in ['A', 'B', 'C', 'D']:
            seats.append((1, f"{r}{c}", 'BUSINESS'))
    for r in range(3, 8):
        for c in ['A', 'B', 'C', 'D', 'E', 'F']:
            seats.append((1, f"{r}{c}", 'ECONOMY'))

    # Aircraft 2 (B737): 26 seats
    for r in range(1, 3):
        for c in ['A', 'B', 'C', 'D']:
            seats.append((2, f"{r}{c}", 'BUSINESS'))
    for r in range(3, 6):
        for c in ['A', 'B', 'C', 'D', 'E', 'F']:
            seats.append((2, f"{r}{c}", 'ECONOMY'))

    # Aircraft 3 (B777): 34 seats
    for c in ['A', 'B', 'C', 'D']:
        seats.append((3, f"1{c}", 'FIRST'))
    for r in range(2, 4):
        for c in ['A', 'B', 'C', 'D', 'E', 'F']:
            seats.append((3, f"{r}{c}", 'BUSINESS'))
    for r in range(4, 7):
        for c in ['A', 'B', 'C', 'D', 'E', 'F']:
            seats.append((3, f"{r}{c}", 'ECONOMY'))

    # Aircraft 4 (A321LR): 20 seats
    for r in range(1, 3):
        for c in ['A', 'B', 'C', 'D']:
            seats.append((4, f"{r}{c}", 'BUSINESS'))
    for r in range(3, 5):
        for c in ['A', 'B', 'C', 'D', 'E', 'F']:
            seats.append((4, f"{r}{c}", 'ECONOMY'))

    # Aircraft 5 (B787): 20 seats
    for r in range(1, 3):
        for c in ['A', 'B', 'C', 'D']:
            seats.append((5, f"{r}{c}", 'BUSINESS'))
    for r in range(3, 5):
        for c in ['A', 'B', 'C', 'D', 'E', 'F']:
            seats.append((5, f"{r}{c}", 'ECONOMY'))

    cur.executemany("INSERT INTO seats (aircraft_id, seat_number, seat_class) VALUES (?, ?, ?);", seats)

    # 5. Flights (15)
    flights = [
        ('AI-101', 1, 1, '2026-10-01 06:00:00', '2026-10-01 08:15:00', 'COMPLETED'),
        ('6E-205', 2, 2, '2026-10-01 07:30:00', '2026-10-01 09:45:00', 'COMPLETED'),
        ('UK-819', 3, 1, '2026-10-01 09:00:00', '2026-10-01 11:45:00', 'DEPARTED'),
        ('AI-504', 4, 2, '2026-10-01 10:15:00', '2026-10-01 13:00:00', 'BOARDING'),
        ('6E-341', 5, 1, '2026-10-01 11:30:00', '2026-10-01 13:15:00', 'SCHEDULED'),
        ('EK-511', 7, 3, '2026-10-01 14:00:00', '2026-10-01 16:30:00', 'SCHEDULED'),
        ('SQ-503', 9, 3, '2026-10-01 18:20:00', '2026-10-02 01:10:00', 'SCHEDULED'),
        ('BA-142', 10, 3, '2026-10-01 22:45:00', '2026-10-02 07:15:00', 'SCHEDULED'),
        ('6E-455', 11, 2, '2026-10-02 06:15:00', '2026-10-02 08:30:00', 'SCHEDULED'),
        ('UK-720', 12, 1, '2026-10-02 07:00:00', '2026-10-02 08:50:00', 'DELAYED'),
        ('AI-102', 2, 1, '2026-10-02 08:00:00', '2026-10-02 10:15:00', 'SCHEDULED'),
        ('6E-206', 1, 2, '2026-10-02 10:00:00', '2026-10-02 12:15:00', 'SCHEDULED'),
        ('UK-820', 4, 1, '2026-10-02 12:30:00', '2026-10-02 15:15:00', 'SCHEDULED'),
        ('AI-505', 3, 2, '2026-10-02 15:00:00', '2026-10-02 17:45:00', 'SCHEDULED'),
        ('6E-342', 6, 1, '2026-10-02 18:00:00', '2026-10-02 19:45:00', 'SCHEDULED')
    ]
    cur.executemany("""
        INSERT INTO flights (flight_number, route_id, aircraft_id, scheduled_departure, scheduled_arrival, flight_status)
        VALUES (?, ?, ?, ?, ?, ?);
    """, flights)

    # 6. Passengers (60)
    passengers_raw = [
        ("Aarav", "Sharma", "aarav.sharma@example.com", "M8472910", "+91-9811023451", "India"),
        ("Priya", "Nair", "priya.nair@example.com", "K9281742", "+91-9822034562", "India"),
        ("Rohan", "Mehta", "rohan.mehta@example.com", "P1029384", "+91-9833045673", "India"),
        ("Ananya", "Deshmukh", "ananya.d@example.com", "L7482910", "+91-9844056784", "India"),
        ("Kabir", "Kapoor", "kabir.k@example.com", "J8392019", "+91-9855067895", "India"),
        ("Sneha", "Reddy", "sneha.reddy@example.com", "T9283741", "+91-9866078906", "India"),
        ("Arjun", "Menon", "arjun.menon@example.com", "Z1928374", "+91-9877089017", "India"),
        ("Meera", "Iyer", "meera.iyer@example.com", "X8372619", "+91-9888090128", "India"),
        ("Rahul", "Verma", "rahul.verma@example.com", "W7382910", "+91-9899011239", "India"),
        ("Neha", "Singh", "neha.singh@example.com", "Q8392011", "+91-9811022340", "India"),
        ("Siddharth", "Patel", "sid.patel@example.com", "V9283745", "+91-9822033451", "India"),
        ("Pooja", "Bose", "pooja.bose@example.com", "N8372615", "+91-9833044562", "India"),
        ("Aditya", "Rao", "aditya.rao@example.com", "B7382914", "+91-9844055673", "India"),
        ("Ishaan", "Gupta", "ishaan.g@example.com", "M9283742", "+91-9855066784", "India"),
        ("Riya", "Malhotra", "riya.m@example.com", "C8372618", "+91-9866077895", "India"),
        ("Kunal", "Sen", "kunal.sen@example.com", "D7382916", "+91-9877088906", "India"),
        ("Tanvi", "Joshi", "tanvi.j@example.com", "E9283749", "+91-9888099017", "India"),
        ("Dev", "Choudhury", "dev.c@example.com", "F8372612", "+91-9899010128", "India"),
        ("Simran", "Kaur", "simran.k@example.com", "G7382919", "+91-9811021239", "India"),
        ("Varun", "Bhatia", "varun.b@example.com", "H9283740", "+91-9822032340", "India"),
        ("Shreya", "Chatterjee", "shreya.c@example.com", "J7382913", "+91-9833043451", "India"),
        ("Sameer", "Khan", "sameer.k@example.com", "K8372611", "+91-9844054562", "India"),
        ("Divya", "Saxena", "divya.s@example.com", "L9283748", "+91-9855065673", "India"),
        ("Karan", "Thakur", "karan.t@example.com", "P8372614", "+91-9866076784", "India"),
        ("Ritu", "Agarwal", "ritu.a@example.com", "R7382915", "+91-9877087895", "India"),
        ("Aman", "Pandey", "aman.p@example.com", "S9283747", "+91-9888098906", "India"),
        ("Kriti", "Goyal", "kriti.g@example.com", "T8372616", "+91-9899019017", "India"),
        ("Yash", "Mishra", "yash.m@example.com", "U7382918", "+91-9811020128", "India"),
        ("Natasha", "D'Souza", "natasha.d@example.com", "V8372617", "+91-9822031239", "India"),
        ("Gaurav", "Dubey", "gaurav.d@example.com", "W9283746", "+91-9833042340", "India"),
        ("Swati", "Tiwari", "swati.t@example.com", "X7382911", "+91-9844053451", "India"),
        ("Nikhil", "Pillai", "nikhil.p@example.com", "Y8372613", "+91-9855064562", "India"),
        ("Alisha", "Fernandes", "alisha.f@example.com", "Z9283743", "+91-9866075673", "India"),
        ("Harsh", "Bansal", "harsh.b@example.com", "A8372610", "+91-9877086784", "India"),
        ("Sanjana", "Kulkarni", "sanjana.k@example.com", "B9283744", "+91-9888097895", "India"),
        ("Vivek", "Nambiar", "vivek.n@example.com", "C7382917", "+91-9899018906", "India"),
        ("Tara", "Sengupta", "tara.s@example.com", "D8372618", "+91-9811029017", "India"),
        ("Amit", "Shukla", "amit.s@example.com", "E7382912", "+91-9822030128", "India"),
        ("Bhavna", "Chauhan", "bhavna.c@example.com", "F9283741", "+91-9833041239", "India"),
        ("Raj", "Srivastava", "raj.s@example.com", "G8372619", "+91-9844052340", "India"),
        ("Anjali", "Gautam", "anjali.g@example.com", "H7382916", "+91-9855063451", "India"),
        ("Manish", "Tripathi", "manish.t@example.com", "J9283748", "+91-9866074562", "India"),
        ("Pallavi", "Jha", "pallavi.j@example.com", "K7382915", "+91-9877085673", "India"),
        ("Deepak", "Chopra", "deepak.c@example.com", "L8372614", "+91-9888096784", "India"),
        ("Sunita", "Mahajan", "sunita.m@example.com", "M7382913", "+91-9899017895", "India"),
        ("Sanjay", "Dutt", "sanjay.d@example.com", "N9283747", "+91-9811028906", "India"),
        ("Rakesh", "Roshan", "rakesh.r@example.com", "P7382911", "+91-9822039017", "India"),
        ("Deepa", "Kamat", "deepa.k@example.com", "R8372612", "+91-9833040128", "India"),
        ("Nitin", "Gadkari", "nitin.g@example.com", "S7382914", "+91-9844051239", "India"),
        ("Rohit", "Dhawan", "rohit.d@example.com", "T9283742", "+91-9855062340", "India"),
        ("Payal", "Rohatgi", "payal.r@example.com", "U8372615", "+91-9866073451", "India"),
        ("Gautam", "Gambhir", "gautam.g@example.com", "V7382919", "+91-9877084562", "India"),
        ("Karishma", "Tanna", "karishma.t@example.com", "W8372616", "+91-9888095673", "India"),
        ("Mohit", "Raina", "mohit.r@example.com", "X9283741", "+91-9899016784", "India"),
        ("Aarti", "Chhabria", "aarti.c@example.com", "Y7382918", "+91-9811027895", "India"),
        ("Pranav", "Mohan", "pranav.m@example.com", "Z8372617", "+91-9822038906", "India"),
        ("Vidya", "Balan", "vidya.b@example.com", "A9283749", "+91-9833049017", "India"),
        ("Abhishek", "Ray", "abhishek.r@example.com", "B8372611", "+91-9844050128", "India"),
        ("Sanya", "Malhotra", "sanya.m@example.com", "C9283745", "+91-9855061239", "India"),
        ("Emily", "Watson", "emily.watson@example.com", "GB748291", "+44-7700900123", "United Kingdom")
    ]
    cur.executemany("""
        INSERT INTO passengers (first_name, last_name, email, passport_number, phone, nationality)
        VALUES (?, ?, ?, ?, ?, ?);
    """, passengers_raw)

    # 7. Bookings (60)
    bookings = []
    for i in range(1, 61):
        pnr = f"PNR{i:03d}"
        b_status = 'CANCELLED' if i in [5, 12, 19, 28, 37, 44, 52] else 'CONFIRMED'
        day = (i % 25) + 1
        bookings.append((pnr, f"2026-09-{day:02d} 10:{i%60:02d}:00", b_status))
    cur.executemany("INSERT INTO bookings (booking_ref, booking_date, booking_status) VALUES (?, ?, ?);", bookings)

    # 8. Tickets (60) - 4 passengers per flight across 15 flights
    tickets = []
    fares = [4500.00, 5200.00, 6800.00, 8500.00, 12500.00, 18000.00, 32000.00, 45000.00]
    canc_ids = {5, 12, 19, 28, 37, 44, 52}

    # Map each aircraft to its list of valid seat_ids
    aircraft_seats = {}
    for a_id in [1, 2, 3, 4, 5]:
        s_rows = cur.execute("SELECT seat_id, seat_class FROM seats WHERE aircraft_id = ? ORDER BY seat_id ASC;", (a_id,)).fetchall()
        aircraft_seats[a_id] = s_rows

    ticket_idx = 1
    for f_id in range(1, 16):
        f_ac = cur.execute("SELECT aircraft_id FROM flights WHERE flight_id = ?", (f_id,)).fetchone()[0]
        avail = aircraft_seats[f_ac]

        # Pick 1 premium seat and 3 economy seats
        prem_seats = [s for s in avail if s[1] in ['BUSINESS', 'FIRST']]
        eco_seats = [s for s in avail if s[1] == 'ECONOMY']
        flight_seats = [prem_seats[0]] + eco_seats[:3]

        for seat_id, s_class in flight_seats:
            b_id = ticket_idx
            p_id = ticket_idx
            if s_class == 'FIRST':
                fare = 35000.00
            elif s_class == 'BUSINESS':
                fare = 18000.00
            else:
                fare = fares[ticket_idx % len(fares)]

            t_status = 'CANCELLED' if ticket_idx in canc_ids else ('CHECKED_IN' if ticket_idx % 2 == 0 else 'ISSUED')
            tickets.append((b_id, f_id, seat_id, p_id, fare, t_status))
            ticket_idx += 1

    cur.executemany("""
        INSERT INTO tickets (booking_id, flight_id, seat_id, passenger_id, fare_amount, ticket_status)
        VALUES (?, ?, ?, ?, ?, ?);
    """, tickets)

    # 9. Payments (60)
    payments = []
    methods = ['UPI', 'CREDIT_CARD', 'DEBIT_CARD', 'NET_BANKING']
    for i in range(1, 61):
        b_id = i
        t_fare = cur.execute("SELECT fare_amount FROM tickets WHERE booking_id = ?", (b_id,)).fetchone()[0]
        p_method = methods[i % 4]
        p_status = 'REFUNDED' if i in [5, 12, 19, 28, 37, 44, 52] else 'SUCCESS'
        txn = f"TXN_{20260900 + i}_{i:04d}"
        payments.append((b_id, t_fare, p_method, p_status, txn, f"2026-09-{(i%25)+1:02d} 10:15:00"))
    cur.executemany("""
        INSERT INTO payments (booking_id, amount, payment_method, payment_status, transaction_reference, payment_time)
        VALUES (?, ?, ?, ?, ?, ?);
    """, payments)

    # 10. Check-ins (35)
    checkins = []
    ch_count = 0
    for i in range(1, 61):
        t_info = cur.execute("SELECT ticket_id, ticket_status, flight_id FROM tickets WHERE ticket_id = ?", (i,)).fetchone()
        if t_info[1] in ['CHECKED_IN', 'ISSUED'] and i not in [5, 12, 19, 28, 37, 44, 52]:
            ch_count += 1
            bp = f"BP-F{t_info[2]:02d}-T{i:03d}"
            checkins.append((i, f"2026-10-01 04:{ch_count%60:02d}:00", bp))
            if ch_count >= 40:
                break
    cur.executemany("INSERT INTO checkins (ticket_id, checkin_time, boarding_pass) VALUES (?, ?, ?);", checkins)

    # 11. Baggage (45)
    baggage = []
    for c_id in range(1, len(checkins) + 1):
        weight = 10.0 + ((c_id * 3.7) % 22.0)
        weight = round(weight, 1)
        fee = round((weight - 15.0) * 500.0, 2) if weight > 15.0 else 0.00
        baggage.append((c_id, weight, fee))
        # Add a 2nd bag for some passengers
        if c_id % 3 == 0:
            w2 = round(8.0 + ((c_id * 1.5) % 12.0), 1)
            f2 = round((w2 - 15.0) * 500.0, 2) if w2 > 15.0 else 0.00
            baggage.append((c_id, w2, f2))
    cur.executemany("INSERT INTO baggage (checkin_id, weight_kg, excess_fee) VALUES (?, ?, ?);", baggage)

    # 12. Cancellations (7)
    cancellations = []
    canc_tickets = [5, 12, 19, 28, 37, 44, 52]
    for tid in canc_tickets:
        fare = cur.execute("SELECT fare_amount FROM tickets WHERE ticket_id = ?", (tid,)).fetchone()[0]
        # refund = fare - penalty (e.g., retain 1500)
        refund = max(0.00, fare - 1500.00)
        cancellations.append((tid, f"2026-09-28 14:{tid:02d}:00", refund))
    cur.executemany("INSERT INTO cancellations (ticket_id, cancellation_timestamp, refund_amount) VALUES (?, ?, ?);", cancellations)

    conn.commit()

    # Verify counts
    print("Database built successfully. Row counts:")
    table_names = [
        'airports', 'routes', 'aircraft', 'seats', 'flights',
        'passengers', 'bookings', 'tickets', 'payments',
        'checkins', 'baggage', 'cancellations', 'view_master_manifest'
    ]
    data_dump = {}
    for t in table_names:
        count = cur.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        print(f"  - {t:<22}: {count} rows")
        
        # Dump table data for standalone browser fallback
        rows_cur = cur.execute(f"SELECT * FROM {t};")
        cols = [d[0] for d in rows_cur.description]
        rows = rows_cur.fetchall()
        data_dump[t] = {
            "columns": cols,
            "rows": rows
        }

    with open(JSON_PATH, "w") as f:
        json.dump(data_dump, f, indent=2)
    print(f"Exported client JSON cache to: {JSON_PATH}")

    conn.close()

if __name__ == "__main__":
    init_db()
