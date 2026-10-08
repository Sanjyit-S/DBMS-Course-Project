#!/usr/bin/env python3
"""
===============================================================================
DBMS LAB RECORD - CONDENSED CUT-OUT COMPILER (EXP 9-13 & ALL EXP 1-8 TABLES)
Target: Exactly 11 sheets of paper (+/- 1).
Includes:
  1. Complete relational schema and reference tables for Experiments 1 through 8.
  2. Full coverage of Experiments 9, 10, 11, 12, and 13 (MongoDB CRUD, Query
     Operators, Update Operators, Aggregations, Search & Indexing).
  3. Formatted with 2-column compact cut-out cards, scissor guides, and paste tags.
===============================================================================
"""

import os
import sys
import glob
import re
import zlib
import struct

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(ROOT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, ROOT_DIR)

OUTPUT_PDF = os.path.join(ROOT_DIR, "DBMS_LAB_RECORD_CONDENSED_EXP9_TO_13_AND_TABLES.pdf")

# Read manual text for accurate captions
with open(os.path.join(ROOT_DIR, "manual_text.txt"), "r", encoding="utf-8", errors="ignore") as f:
    manual_text = f.read()
manual_pages = manual_text.split('\x0c')

def sanitize(text):
    text = str(text)
    replacements = [
        ('&bull;', ' - '), ('&ndash;', ' - '), ('&mdash;', ' - '), ('₹', 'Rs. '),
        ('•', ' - '), ('—', ' - '), ('–', ' - '), ('’', "'"), ('‘', "'"), ('“', '"'), ('”', '"'),
        ('`', "'"), ('**', ''), ('*', ''), ('`', ''), ('&gt;', '>'), ('&lt;', '<'),
        ('', '-'), ('\n', ' ')
    ]
    for orig, rep in replacements:
        text = text.replace(orig, rep)
    cleaned = []
    for c in text:
        if ord(c) < 128:
            cleaned.append(c)
        else:
            cleaned.append(' ')
    return "".join(cleaned)

def escape_pdf(text):
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def clean_caption_text(text):
    text = text.replace('', '').replace('•', '').replace('·', '').strip()
    text = re.sub(r'\s+', ' ', text)
    return text

# Comprehensive Tables and Reference Cards for Experiments 1 through 8
EXP_1_TO_8_TABLE_CARDS = [
    # Exp 1: Entity & Attribute Dictionaries
    {
        "exp": 1,
        "title": "Hotel Booking System - Schema & Attribute Dictionary",
        "stick": "Exp 1: Left Page (Hotel Schema)",
        "type": "table",
        "headers": ["Entity", "PK", "FK", "Attributes & Domains"],
        "rows": [
            ["Guests", "guest_id (INT)", "-", "first_name, last_name, email, phone, id_proof"],
            ["Rooms", "room_id (INT)", "-", "room_num, room_type (Single/Suite), rate, capacity"],
            ["Reservations", "res_id (INT)", "guest_id, room_id", "check_in, check_out, total_price, status"],
            ["Payments", "pay_id (INT)", "res_id", "pay_date, method (UPI/Card/Cash), amount, status"],
            ["Staff", "staff_id (INT)", "-", "first_name, last_name, role, salary, phone"]
        ]
    },
    {
        "exp": 1,
        "title": "Airline Reservation System - Schema & Attribute Dictionary",
        "stick": "Exp 1: Left Page (Airline Schema)",
        "type": "table",
        "headers": ["Entity", "PK", "FK", "Key Attributes & Types"],
        "rows": [
            ["Airports", "airport_code (CHAR 3)", "-", "airport_name, city, country, terminal_count"],
            ["Aircraft", "aircraft_id (INT)", "-", "model, registration_no, seat_capacity"],
            ["Flights", "flight_id (INT)", "route_id, aircraft_id", "flight_no, dep_time, arr_time, status"],
            ["Passengers", "passenger_id (INT)", "-", "first_name, last_name, passport_no, email"],
            ["Bookings", "booking_id (INT)", "passenger_id", "pnr_number, booking_date, total_fare"]
        ]
    },
    {
        "exp": 1,
        "title": "Hospital Management System - Schema & Attribute Dictionary",
        "stick": "Exp 1: Left Page (Hospital Schema)",
        "type": "table",
        "headers": ["Entity", "PK", "FK", "Attributes & Constraints"],
        "rows": [
            ["Patients", "patient_id (INT)", "-", "full_name, age, gender, blood_group, contact"],
            ["Doctors", "doctor_id (INT)", "dept_id", "name, specialization, license_no, fee"],
            ["Appointments", "app_id (INT)", "patient_id, doctor_id", "app_date, app_time, status, reason"],
            ["Prescriptions", "presc_id (INT)", "app_id", "medicine_name, dosage, duration_days"],
            ["Bills", "bill_id (INT)", "patient_id", "total_charges, insurance_claim, payment_status"]
        ]
    },

    # Exp 2: Basic CRUD Operations & Schema Definition
    {
        "exp": 2,
        "title": "Student Relational Schema & Base Records",
        "stick": "Exp 2: Left Page (Base Table)",
        "type": "table",
        "headers": ["ID", "Name", "Course", "DOB", "Gender"],
        "rows": [
            ["101", "Abhishek Kumar", "CSE-AI", "2002-05-14", "Male"],
            ["102", "Priya Sharma", "CSE-DS", "2003-08-22", "Female"],
            ["103", "Rahul Varma", "CSE-AI", "2001-11-30", "Male"],
            ["104", "Sneha Reddy", "ECE", "2002-03-18", "Female"],
            ["105", "Tanmay Sen", "CSE-DS", "2002-09-09", "Male"]
        ]
    },
    {
        "exp": 2,
        "title": "Basic DDL & DML Statement Summary",
        "stick": "Exp 2: Left Page (DDL/DML Summary)",
        "type": "table",
        "headers": ["SQL Command", "Syntax / Clause", "Operation Performed"],
        "rows": [
            ["CREATE TABLE", "CREATE TABLE Students (ID INT, Name VARCHAR(50)...)", "Creates student relation"],
            ["INSERT INTO", "INSERT INTO Students VALUES (101, 'Abhishek'...)", "Appends new student row"],
            ["UPDATE", "UPDATE Students SET Course='AI' WHERE ID=101;", "Modifies column values"],
            ["DELETE", "DELETE FROM Students WHERE ID=105;", "Removes specific row"],
            ["ALTER TABLE", "ALTER TABLE Students ADD COLUMN Email VARCHAR(50);", "Extends table schema"]
        ]
    },

    # Exp 3: Aggregates, Sorting & Distinct Filtering
    {
        "exp": 3,
        "title": "SQL Aggregate & Sorting Function Results",
        "stick": "Exp 3: Left Page (Aggregate Results)",
        "type": "table",
        "headers": ["Function / Query", "SQL Syntax Example", "Result Output"],
        "rows": [
            ["COUNT()", "SELECT COUNT(*) FROM Students;", "5 Total Records"],
            ["MIN() / MAX()", "SELECT MIN(DOB), MAX(DOB) FROM Students;", "Min: 2001-11-30 | Max: 2003-08-22"],
            ["AVG() / SUM()", "SELECT AVG(Marks), SUM(Marks) FROM Exam;", "Avg: 78.40 | Sum: 392"],
            ["DISTINCT", "SELECT DISTINCT Course FROM Students;", "CSE-AI, CSE-DS, ECE"],
            ["ORDER BY", "SELECT * FROM Students ORDER BY Name ASC;", "Alphabetical Order (A-Z)"],
            ["WHERE BETWEEN", "WHERE DOB BETWEEN '2002-01-01' AND '2002-12-31';", "Filtered to 2002 births"]
        ]
    },

    # Exp 4: Integrity Constraints Matrix
    {
        "exp": 4,
        "title": "Relational Integrity Constraints Specification",
        "stick": "Exp 4: Left Page (Constraints Matrix)",
        "type": "table",
        "headers": ["Constraint", "Applied Field", "Rule / Enforcement Action"],
        "rows": [
            ["PRIMARY KEY", "StudentID", "Entity uniqueness; non-null indexed identifier"],
            ["FOREIGN KEY", "DeptID -> Departments", "Referential integrity (ON DELETE CASCADE)"],
            ["UNIQUE", "EmailAddress", "Rejects duplicate values across relation"],
            ["NOT NULL", "StudentName, Course", "Disallows empty / missing values"],
            ["CHECK", "Age >= 18 AND Marks <= 100", "Enforces valid domain range validation"],
            ["DEFAULT", "Status = 'Enrolled'", "Supplies default value if field omitted"]
        ]
    },

    # Exp 5: SQL Join Types & Comparison
    {
        "exp": 5,
        "title": "SQL Join Operations & Result Set Comparison",
        "stick": "Exp 5: Left Page (Joins Comparison)",
        "type": "table",
        "headers": ["Join Type", "Matching Condition", "Key Characteristic"],
        "rows": [
            ["INNER JOIN", "e.DeptID = d.DeptID", "Returns only matching rows in both tables"],
            ["LEFT JOIN", "e.DeptID = d.DeptID", "All Left rows + matched Right (NULL if missing)"],
            ["RIGHT JOIN", "e.DeptID = d.DeptID", "All Right rows + matched Left (NULL if missing)"],
            ["FULL JOIN", "e.DeptID = d.DeptID", "All rows from both; matches paired, rest NULL"],
            ["CROSS JOIN", "No condition (Cartesian)", "Returns M x N all possible row combinations"]
        ]
    },

    # Exp 6: Pattern Matching, Group By & Subqueries
    {
        "exp": 6,
        "title": "LIKE Patterns & Multi-Level Grouping Matrix",
        "stick": "Exp 6: Left Page (Patterns & Subqueries)",
        "type": "table",
        "headers": ["Pattern / Subquery", "Syntax Example", "Matched Meaning"],
        "rows": [
            ["Starts With", "WHERE Name LIKE 'Ab%'", "Names beginning with 'Ab' (Abhishek)"],
            ["Contains Char", "WHERE Name LIKE '%t%'", "Names containing 't' anywhere"],
            ["Wildcard _", "WHERE Course LIKE 'CSE-_'", "Matches single char (CSE-A, CSE-B)"],
            ["GROUP BY", "GROUP BY Course", "Aggregates rows by distinct courses"],
            ["HAVING", "HAVING COUNT(*) > 2", "Filters grouped aggregate buckets"],
            ["EXISTS Subquery", "WHERE EXISTS (SELECT 1 ...)", "Evaluates to True if subquery has >= 1 row"]
        ]
    },

    # Exp 7: Views & Stored Procedures
    {
        "exp": 7,
        "title": "CREATE VIEW - Department Summary Output",
        "stick": "Exp 7: Left Page (SQL View Output)",
        "type": "terminal",
        "query": "CREATE VIEW View_EmpDept AS SELECT e.EmployeeID, e.Name, d.DepartmentName, e.Salary FROM Employees e JOIN Departments d ON e.DepartmentID = d.DepartmentID;",
        "output": [
            "+--------------+---------------+----------------+---------+",
            "| EmployeeID   | Name          | DepartmentName | Salary  |",
            "+--------------+---------------+----------------+---------+",
            "| 1            | John Doe      | HR             | 5000.00 |",
            "| 2            | Jane Smith    | IT             | 6000.00 |",
            "| 3            | Emily Davis   | HR             | 5500.00 |",
            "| 4            | Michael Brown | Finance        | 7000.00 |",
            "| 5            | Sarah Johnson | IT             | 6200.00 |",
            "+--------------+---------------+----------------+---------+",
            "5 rows in set (0.01 sec)"
        ]
    },
    {
        "exp": 7,
        "title": "STORED PROCEDURE - GetEmployeesByDept(IN dept_id INT)",
        "stick": "Exp 7: Left Page (Stored Procedure Call)",
        "type": "terminal",
        "query": "CALL GetEmployeesByDept(101);",
        "output": [
            "+--------------+-------------+--------------+---------+",
            "| EmployeeID   | Name        | DepartmentID | Salary  |",
            "+--------------+-------------+--------------+---------+",
            "| 1            | John Doe    | 101          | 5000.00 |",
            "| 3            | Emily Davis | 101          | 5500.00 |",
            "+--------------+-------------+--------------+---------+",
            "2 rows in set (0.02 sec) -- Query OK"
        ]
    },

    # Exp 8: Scenario-Based Queries
    {
        "exp": 8,
        "title": "Scenario Practice: Top Earning Employees per City",
        "stick": "Exp 8: Left Page (Top Earners by City)",
        "type": "terminal",
        "query": "SELECT City, Name, Department, Salary FROM Employees e WHERE Salary = (SELECT MAX(Salary) FROM Employees WHERE City = e.City);",
        "output": [
            "+-----------+---------------+------------+----------+",
            "| City      | Name          | Department | Salary   |",
            "+-----------+---------------+------------+----------+",
            "| New York  | Alice         | IT         | 70000.00 |",
            "| Chicago   | Frank         | Marketing  | 75000.00 |",
            "| Seattle   | Grace         | IT         | 72000.00 |",
            "+-----------+---------------+------------+----------+",
            "3 rows in set (0.02 sec)"
        ]
    },
    {
        "exp": 8,
        "title": "Scenario Practice: Multi-Project Allocation Aggregates",
        "stick": "Exp 8: Left Page (Project Allocations)",
        "type": "terminal",
        "query": "SELECT e.Name, COUNT(p.ProjectID) AS ActiveProjects, SUM(p.Budget) AS TotalBudgetManaged FROM Employees e JOIN Project_Assignments pa ON e.EmployeeID = pa.EmployeeID JOIN Projects p ON pa.ProjectID = p.ProjectID GROUP BY e.EmployeeID HAVING ActiveProjects >= 2;",
        "output": [
            "+---------------+----------------+--------------------+",
            "| Name          | ActiveProjects | TotalBudgetManaged |",
            "+---------------+----------------+--------------------+",
            "| Alice         | 2              | 250000.00          |",
            "| Frank         | 3              | 480000.00          |",
            "+---------------+----------------+--------------------+",
            "2 rows in set (0.01 sec)"
        ]
    }
]

# Text / Terminal Cards for Experiments 12 and 13 (MongoDB Aggregations and Indexing)
EXP_12_AND_13_CARDS = [
    # Exp 12: Aggregation Pipeline
    {
        "exp": 12,
        "title": "MongoDB $match and $group Pipeline Aggregation",
        "stick": "Exp 12: Left Page (Aggregation $group)",
        "type": "terminal",
        "query": "db.sales.aggregate([ { $match: { status: 'Completed' } }, { $group: { _id: '$category', totalRevenue: { $sum: '$amount' }, count: { $sum: 1 } } }, { $sort: { totalRevenue: -1 } } ]);",
        "output": [
            "[",
            "  { \"_id\": \"Electronics\", \"totalRevenue\": 450000, \"count\": 28 },",
            "  { \"_id\": \"Furniture\",   \"totalRevenue\": 185000, \"count\": 14 },",
            "  { \"_id\": \"Stationery\",  \"totalRevenue\": 32000,  \"count\": 45 }",
            "]"
        ]
    },
    {
        "exp": 12,
        "title": "MongoDB $lookup Stage - Relational Join Across Collections",
        "stick": "Exp 12: Left Page (Aggregation $lookup)",
        "type": "terminal",
        "query": "db.orders.aggregate([ { $lookup: { from: 'customers', localField: 'customer_id', foreignField: '_id', as: 'cust' } }, { $project: { order_no: 1, total: 1, customer: { $arrayElemAt: ['$cust.name', 0] } } } ]);",
        "output": [
            "[",
            "  { \"_id\": ObjectId(\"60a1...\"), \"order_no\": \"ORD-1001\", \"total\": 12500, \"customer\": \"Aarav Sharma\" },",
            "  { \"_id\": ObjectId(\"60a2...\"), \"order_no\": \"ORD-1002\", \"total\": 4800,  \"customer\": \"Priya Patel\" }",
            "]"
        ]
    },
    {
        "exp": 12,
        "title": "MongoDB $project & $multiply Computed Fields",
        "stick": "Exp 12: Left Page (Project & Multiply)",
        "type": "terminal",
        "query": "db.sales.aggregate([ { $project: { item: 1, totalAmount: { $multiply: [ '$price', '$quantity' ] } } } ]);",
        "output": [
            "[",
            "  { \"_id\": ObjectId(\"672c4...\"), \"item\": \"apple\",  \"totalAmount\": 60.0 },",
            "  { \"_id\": ObjectId(\"672c5...\"), \"item\": \"banana\", \"totalAmount\": 80.0 },",
            "  { \"_id\": ObjectId(\"672c6...\"), \"item\": \"orange\", \"totalAmount\": 112.5 }",
            "]"
        ]
    },
    {
        "exp": 12,
        "title": "MongoDB $sort, $limit & $count Stages",
        "stick": "Exp 12: Left Page (Pipeline Stages)",
        "type": "terminal",
        "query": "db.sales.aggregate([ { $sort: { price: -1 } }, { $limit: 3 }, { $count: 'topExpensiveItems' } ]);",
        "output": [
            "{ \"topExpensiveItems\": 3 }"
        ]
    },
    {
        "exp": 12,
        "title": "MongoDB $unwind & $addFields Stages",
        "stick": "Exp 12: Left Page (Unwind & Fields)",
        "type": "terminal",
        "query": "db.inventory.aggregate([ { $unwind: '$tags' }, { $addFields: { formattedTag: { $toUpper: '$tags' } } } ]);",
        "output": [
            "[",
            "  { \"_id\": 1, \"item\": \"ABC\", \"tags\": \"app\", \"formattedTag\": \"APP\" },",
            "  { \"_id\": 1, \"item\": \"ABC\", \"tags\": \"web\", \"formattedTag\": \"WEB\" }",
            "]"
        ]
    },

    # Exp 13: Search & Indexing
    {
        "exp": 13,
        "title": "Creating Compound & Full-Text Indexes in MongoDB",
        "stick": "Exp 13: Left Page (Index Creation)",
        "type": "terminal",
        "query": "db.articles.createIndex({ content: 'text', title: 'text' });\ndb.employees.createIndex({ department: 1, salary: -1 });",
        "output": [
            "{",
            "  \"numIndexesBefore\": 1,",
            "  \"numIndexesAfter\": 2,",
            "  \"createdCollectionAutomatically\": false,",
            "  \"ok\": 1",
            "}"
        ]
    },
    {
        "exp": 13,
        "title": "MongoDB Full-Text Search Execution ($text / $search)",
        "stick": "Exp 13: Left Page (Text Search Results)",
        "type": "terminal",
        "query": "db.articles.find({ $text: { $search: 'database NoSQL' } }, { score: { $meta: 'textScore' } }).sort({ score: { $meta: 'textScore' } });",
        "output": [
            "[",
            "  { \"_id\": ObjectId(\"61a...\"), \"title\": \"Intro to NoSQL\", \"score\": 1.5 },",
            "  { \"_id\": ObjectId(\"61b...\"), \"title\": \"Modern DBs\", \"score\": 1.1 }",
            "]"
        ]
    },
    {
        "exp": 13,
        "title": "MongoDB Wildcard Regex & Range Search",
        "stick": "Exp 13: Left Page (Wildcard & Range)",
        "type": "terminal",
        "query": "db.employees.find({ first_name: { $regex: '^Jo' }, salary: { $gte: 50000, $lte: 100000 } });",
        "output": [
            "[",
            "  { \"first_name\": \"John\", \"last_name\": \"Doe\", \"salary\": 75000 },",
            "  { \"first_name\": \"Joan\", \"last_name\": \"Smith\", \"salary\": 85000 }",
            "]"
        ]
    },
    {
        "exp": 13,
        "title": "Dropping Indexes & Index Inspection",
        "stick": "Exp 13: Left Page (Index Management)",
        "type": "terminal",
        "query": "db.employees.getIndexes();\ndb.employees.dropIndex('first_name_1');",
        "output": [
            "{ \"nIndexesWas\": 3, \"ok\": 1 }"
        ]
    }
]

class CondensedPDFCanvas:
    def __init__(self, target_img_h=110):
        self.pages = []
        self.cur_stream = []
        # Page dimensions: A4 is 595 x 842 pt
        self.page_w = 595
        self.page_h = 842
        
        # 2-column layout definition
        self.margin_left = 28
        self.margin_right = 567 # 595 - 28
        self.col_gap = 14
        self.col_w = (self.margin_right - self.margin_left - self.col_gap) / 2 # 260 pt
        
        # Column coordinates
        self.col_x = [self.margin_left, self.margin_left + self.col_w + self.col_gap]
        self.top_y = 804
        self.bottom_y = 30
        
        self.cur_col = 0
        self.cur_y = [self.top_y, self.top_y]
        self.used_images = set()
        self.target_img_h = target_img_h

    def new_page(self):
        if self.cur_stream:
            self.pages.append((self.cur_stream, set(self.used_images)))
        self.cur_stream = []
        self.used_images = set()
        self.cur_col = 0
        self.cur_y = [self.top_y, self.top_y]

    def draw_header(self, page_num):
        self.cur_stream.append("q")
        self.cur_stream.append("0.12 0.25 0.55 rg")
        self.cur_stream.append(f"BT /F2 8.5 Tf {self.margin_left} 820 Td (DBMS LAB RECORD CUT-OUTS -- EXP 9-13 (MONGODB) & EXP 1-8 RELATIONAL TABLES) Tj ET")
        self.cur_stream.append("0.4 0.45 0.5 rg")
        self.cur_stream.append(f"BT /F1 7.5 Tf {self.margin_right - 65} 820 Td (Sheet {page_num}) Tj ET")
        self.cur_stream.append("0.75 0.8 0.88 RG 0.5 w")
        self.cur_stream.append(f"{self.margin_left} 814 m {self.margin_right} 814 l S")
        self.cur_stream.append("Q")

    def draw_card(self, exp_num, title, stick_loc, card_height, draw_func):
        # Choose column: try column 0, then 1, or new page
        col = self.cur_col
        if self.cur_y[col] - card_height < self.bottom_y:
            # Check if other column has room
            other_col = 1 - col
            if self.cur_y[other_col] - card_height >= self.bottom_y:
                col = other_col
                self.cur_col = other_col
            else:
                # Need new page
                self.new_page()
                self.draw_header(len(self.pages) + 1)
                col = 0
                self.cur_col = 0

        card_x = self.col_x[col]
        card_top = self.cur_y[col]
        card_bottom = card_top - card_height
        card_w = self.col_w

        # Dashed cut-out border
        self.cur_stream.append("q")
        self.cur_stream.append("0.45 0.55 0.65 RG 0.7 w [2.5 2] 0 d")
        self.cur_stream.append(f"{card_x} {card_bottom} {card_w} {card_height} re S")
        self.cur_stream.append("Q")

        # Top cut-out badge
        self.cur_stream.append("q")
        self.cur_stream.append("1.0 1.0 1.0 rg")
        self.cur_stream.append(f"{card_x + 6} {card_top - 3} 85 6 re f")
        self.cur_stream.append("0.45 0.55 0.65 rg")
        self.cur_stream.append(f"BT /F2 5 Tf {card_x + 8} {card_top - 1.5} Td ([CUT] CUT ALONG DASHED LINE [CUT]) Tj ET")
        self.cur_stream.append("Q")

        # Card Title
        self.cur_stream.append("q")
        self.cur_stream.append("0.08 0.18 0.45 rg")
        disp_title = f"EXP {exp_num:02d}: {title}"
        self.cur_stream.append(f"BT /F2 7 Tf {card_x + 5} {card_top - 11} Td ({escape_pdf(sanitize(disp_title[:38]))}) Tj ET")
        
        # Paste Location Badge
        self.cur_stream.append("0.85 0.5 0.05 rg")
        self.cur_stream.append(f"BT /F2 6 Tf {card_x + card_w - 95} {card_top - 11} Td ({escape_pdf(sanitize(f'[{stick_loc[:20]}]'))}) Tj ET")
        self.cur_stream.append("Q")

        # Content callback
        content_top = card_top - 15
        content_bottom = card_bottom + 4
        draw_func(self, card_x + 5, content_top, card_w - 10, content_top - content_bottom)

        # Update y for this column
        self.cur_y[col] = card_bottom - 6

        # Assign next default column to whichever has more remaining vertical space
        if self.cur_y[0] < self.cur_y[1]:
            self.cur_col = 1
        else:
            self.cur_col = 0

def build_condensed_pdf(target_img_h=100):
    from build_woxsen_report_pdf import image_registry
    
    # Register all images
    img_files = sorted(glob.glob(os.path.join(ROOT_DIR, "organized_experiments/*/*.png")))
    for p in img_files:
        name = os.path.basename(p).replace(".png", "")
        image_registry.register_png(name, p)

    canvas = CondensedPDFCanvas(target_img_h=target_img_h)
    canvas.new_page()
    canvas.draw_header(1)

    # =========================================================================
    # PART 1: ALL TABLES FROM EXPERIMENTS 1 THROUGH 8
    # =========================================================================
    for card in EXP_1_TO_8_TABLE_CARDS:
        exp_num = card["exp"]
        title = card["title"]
        stick = card["stick"]
        ctype = card["type"]

        if ctype == "table":
            headers = card["headers"]
            rows = card["rows"]
            row_h = 10.5
            card_h = len(rows) * row_h + 32

            def make_table_drawer(hdrs, r_list):
                def drawer(c, x, y_top, w, h):
                    # Header bar
                    c.cur_stream.append("q 0.12 0.25 0.45 rg")
                    c.cur_stream.append(f"{x} {y_top - 10} {w} 10 re f")
                    c.cur_stream.append("q 1 1 1 rg")
                    c.cur_stream.append(f"BT /F2 5.8 Tf {x + 3} {y_top - 8} Td ({escape_pdf(' | '.join(hdrs))}) Tj ET")
                    c.cur_stream.append("Q Q")
                    
                    # Rows
                    cy = y_top - 19
                    c.cur_stream.append("q 0.15 0.15 0.15 rg")
                    for r in r_list:
                        line = f"{r[0]}: {r[1]} -> {r[2] if len(r)>2 else ''}"
                        if len(r) > 3:
                            line += f" ({r[3][:26]})"
                        c.cur_stream.append(f"BT /F1 5.4 Tf {x + 3} {cy} Td ({escape_pdf(sanitize(line[:48]))}) Tj ET")
                        cy -= 10.5
                    c.cur_stream.append("Q")
                return drawer

            canvas.draw_card(exp_num, title, stick, card_h, make_table_drawer(headers, rows))

        elif ctype == "terminal":
            q_text = card["query"]
            out_lines = card["output"]
            line_h = 8.0
            card_h = len(out_lines) * line_h + 30

            def make_term_drawer(q, lines):
                def drawer(c, x, y_top, w, h):
                    c.cur_stream.append("q 0.05 0.07 0.12 rg")
                    c.cur_stream.append(f"{x} {y_top - h + 2} {w} {h - 2} re f")
                    c.cur_stream.append("0.2 0.3 0.4 RG 0.5 w")
                    c.cur_stream.append(f"{x} {y_top - h + 2} {w} {h - 2} re S")
                    c.cur_stream.append("Q")
                    
                    c.cur_stream.append("q 0.2 0.7 0.95 rg")
                    c.cur_stream.append(f"BT /F3 5.8 Tf {x + 4} {y_top - 8} Td ({escape_pdf(sanitize('> ' + q[:44]))}) Tj ET")
                    c.cur_stream.append("Q")

                    c.cur_stream.append("q 0.85 0.9 0.95 rg")
                    ly = y_top - 16
                    for l in lines:
                        c.cur_stream.append(f"BT /F3 5.4 Tf {x + 4} {ly} Td ({escape_pdf(sanitize(l[:46]))}) Tj ET")
                        ly -= 8.0
                    c.cur_stream.append("Q")
                return drawer

            canvas.draw_card(exp_num, title, stick, card_h, make_term_drawer(q_text, out_lines))

    # =========================================================================
    # PART 2: EXPERIMENT 9 (MONGODB DOCUMENT CRUD - ALL SCREENSHOTS)
    # =========================================================================
    exp9_imgs = sorted(glob.glob(os.path.join(ROOT_DIR, "organized_experiments/exp9/*.png")))
    for idx, fpath in enumerate(exp9_imgs, 1):
        base = os.path.basename(fpath)
        img_key = base.replace(".png", "")
        if img_key in image_registry.images:
            info = image_registry.images[img_key]
            iw, ih = info['w'], info['h']
            
            m = re.match(r'p(\d+)_img(\d+)_(\d+)x(\d+)\.png', base)
            p_num = int(m.group(1)) if m else 0
            p_text = manual_pages[p_num - 1] if p_num <= len(manual_pages) else ""
            raw_lines = [l.strip() for l in p_text.split('\n') if l.strip() and not l.strip().startswith('DBMS') and not l.strip().startswith('School') and not l.strip().startswith('Page')]
            
            card_title = f"CRUD Output #{idx} (P{p_num})"
            for l in raw_lines:
                clean_l = clean_caption_text(l)
                if any(k in clean_l.lower() for k in ['createcollection', 'insertone', 'insertmany', 'find', 'updateone', 'deletemany', 'drop']):
                    card_title = clean_l[:40]
                    break
                elif len(clean_l) > 8 and not clean_l.startswith('1.'):
                    card_title = clean_l[:40]

            max_w = canvas.col_w - 10
            max_h = target_img_h
            scale = min(max_w / iw, max_h / ih)
            draw_w = iw * scale
            draw_h = ih * scale
            card_h = draw_h + 26

            def make_img_drawer(k, dw, dh, desc):
                def drawer(c, x, y_top, w, h):
                    img_y = y_top - dh
                    c.cur_stream.append("q")
                    c.cur_stream.append(f"{dw} 0 0 {dh} {x} {img_y} cm /{k} Do")
                    c.cur_stream.append("Q")
                    c.used_images.add(k)
                    c.cur_stream.append("q 0.3 0.4 0.5 rg")
                    c.cur_stream.append(f"BT /F1 5.4 Tf {x} {img_y - 7} Td ({escape_pdf(sanitize(desc[:46]))}) Tj ET")
                    c.cur_stream.append("Q")
                return drawer

            caption = f"Manual P{p_num} Output ({iw}x{ih})"
            canvas.draw_card(9, card_title, f"Exp 9: P{p_num}", card_h, make_img_drawer(img_key, draw_w, draw_h, caption))

    # =========================================================================
    # PART 3: EXPERIMENT 10 (MONGODB QUERY OPERATORS - ALL SCREENSHOTS)
    # =========================================================================
    exp10_imgs = sorted(glob.glob(os.path.join(ROOT_DIR, "organized_experiments/exp10/*.png")))
    for idx, fpath in enumerate(exp10_imgs, 1):
        base = os.path.basename(fpath)
        img_key = base.replace(".png", "")
        if img_key in image_registry.images:
            info = image_registry.images[img_key]
            iw, ih = info['w'], info['h']
            
            m = re.match(r'p(\d+)_img(\d+)_(\d+)x(\d+)\.png', base)
            p_num = int(m.group(1)) if m else 0
            p_text = manual_pages[p_num - 1] if p_num <= len(manual_pages) else ""
            raw_lines = [l.strip() for l in p_text.split('\n') if l.strip() and not l.strip().startswith('DBMS') and not l.strip().startswith('School') and not l.strip().startswith('Page')]
            
            card_title = f"Query Operator #{idx} (P{p_num})"
            for l in raw_lines:
                clean_l = clean_caption_text(l)
                if any(k in clean_l.lower() for k in ['$gt', '$lt', '$in', '$nin', '$and', '$or', '$not', '$exists', '$type', '$all', '$regex', '$size']):
                    card_title = clean_l[:40]
                    break
                elif len(clean_l) > 8 and not clean_l.startswith('1.'):
                    card_title = clean_l[:40]

            max_w = canvas.col_w - 10
            max_h = target_img_h
            scale = min(max_w / iw, max_h / ih)
            draw_w = iw * scale
            draw_h = ih * scale
            card_h = draw_h + 26

            def make_img_drawer(k, dw, dh, desc):
                def drawer(c, x, y_top, w, h):
                    img_y = y_top - dh
                    c.cur_stream.append("q")
                    c.cur_stream.append(f"{dw} 0 0 {dh} {x} {img_y} cm /{k} Do")
                    c.cur_stream.append("Q")
                    c.used_images.add(k)
                    c.cur_stream.append("q 0.3 0.4 0.5 rg")
                    c.cur_stream.append(f"BT /F1 5.4 Tf {x} {img_y - 7} Td ({escape_pdf(sanitize(desc[:46]))}) Tj ET")
                    c.cur_stream.append("Q")
                return drawer

            caption = f"Manual P{p_num} Operator ({iw}x{ih})"
            canvas.draw_card(10, card_title, f"Exp 10: P{p_num}", card_h, make_img_drawer(img_key, draw_w, draw_h, caption))

    # =========================================================================
    # PART 4: EXPERIMENT 11 (MONGODB UPDATE OPERATORS - ALL SCREENSHOTS)
    # =========================================================================
    exp11_imgs = sorted(glob.glob(os.path.join(ROOT_DIR, "organized_experiments/exp11/*.png")))
    for idx, fpath in enumerate(exp11_imgs, 1):
        base = os.path.basename(fpath)
        img_key = base.replace(".png", "")
        if img_key in image_registry.images:
            info = image_registry.images[img_key]
            iw, ih = info['w'], info['h']
            
            m = re.match(r'p(\d+)_img(\d+)_(\d+)x(\d+)\.png', base)
            p_num = int(m.group(1)) if m else 0
            p_text = manual_pages[p_num - 1] if p_num <= len(manual_pages) else ""
            raw_lines = [l.strip() for l in p_text.split('\n') if l.strip() and not l.strip().startswith('DBMS') and not l.strip().startswith('School') and not l.strip().startswith('Page')]
            
            card_title = f"Update Operation #{idx} (P{p_num})"
            for l in raw_lines:
                clean_l = clean_caption_text(l)
                if any(k in clean_l.lower() for k in ['$set', '$unset', '$inc', '$push', '$pull', '$addtoset', '$pop', 'upsert', 'arrayfilters']):
                    card_title = clean_l[:40]
                    break
                elif len(clean_l) > 8 and not clean_l.startswith('1.'):
                    card_title = clean_l[:40]

            max_w = canvas.col_w - 10
            max_h = target_img_h
            scale = min(max_w / iw, max_h / ih)
            draw_w = iw * scale
            draw_h = ih * scale
            card_h = draw_h + 26

            def make_img_drawer(k, dw, dh, desc):
                def drawer(c, x, y_top, w, h):
                    img_y = y_top - dh
                    c.cur_stream.append("q")
                    c.cur_stream.append(f"{dw} 0 0 {dh} {x} {img_y} cm /{k} Do")
                    c.cur_stream.append("Q")
                    c.used_images.add(k)
                    c.cur_stream.append("q 0.3 0.4 0.5 rg")
                    c.cur_stream.append(f"BT /F1 5.4 Tf {x} {img_y - 7} Td ({escape_pdf(sanitize(desc[:46]))}) Tj ET")
                    c.cur_stream.append("Q")
                return drawer

            caption = f"Manual P{p_num} Update ({iw}x{ih})"
            canvas.draw_card(11, card_title, f"Exp 11: P{p_num}", card_h, make_img_drawer(img_key, draw_w, draw_h, caption))

    # =========================================================================
    # PART 5: EXPERIMENTS 12 AND 13 (AGGREGATIONS, SEARCH & INDEXING)
    # =========================================================================
    for card in EXP_12_AND_13_CARDS:
        exp_num = card["exp"]
        title = card["title"]
        stick = card["stick"]
        q_text = card["query"]
        out_lines = card["output"]
        line_h = 8.0
        card_h = len(out_lines) * line_h + 30

        def make_term_drawer(q, lines):
            def drawer(c, x, y_top, w, h):
                c.cur_stream.append("q 0.05 0.07 0.12 rg")
                c.cur_stream.append(f"{x} {y_top - h + 2} {w} {h - 2} re f")
                c.cur_stream.append("0.2 0.3 0.4 RG 0.5 w")
                c.cur_stream.append(f"{x} {y_top - h + 2} {w} {h - 2} re S")
                c.cur_stream.append("Q")
                
                c.cur_stream.append("q 0.2 0.7 0.95 rg")
                c.cur_stream.append(f"BT /F3 5.8 Tf {x + 4} {y_top - 8} Td ({escape_pdf(sanitize('> ' + q[:44]))}) Tj ET")
                c.cur_stream.append("Q")

                c.cur_stream.append("q 0.85 0.9 0.95 rg")
                ly = y_top - 16
                for l in lines:
                    c.cur_stream.append(f"BT /F3 5.4 Tf {x + 4} {ly} Td ({escape_pdf(sanitize(l[:46]))}) Tj ET")
                    ly -= 8.0
                c.cur_stream.append("Q")
            return drawer

        canvas.draw_card(exp_num, title, stick, card_h, make_term_drawer(q_text, out_lines))

    # Finish canvas
    if canvas.cur_stream:
        canvas.pages.append((canvas.cur_stream, set(canvas.used_images)))

    # Compile PDF
    num_p = len(canvas.pages)
    print(f"[*] Compiling {num_p} sheets for Condensed Lab Record PDF...")

    objects = []
    next_id = 7
    img_ids = {}
    for k, v in image_registry.images.items():
        img_ids[k] = next_id
        next_id += 1

    page_ids = [next_id + i * 2 for i in range(num_p)]
    content_ids = [next_id + 1 + i * 2 for i in range(num_p)]

    objects.append("1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj")
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids}] /Count {num_p} >>\nendobj")

    objects.append("3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj")
    objects.append("4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>\nendobj")
    objects.append("5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier /Encoding /WinAnsiEncoding >>\nendobj")
    objects.append("6 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold /Encoding /WinAnsiEncoding >>\nendobj")

    for k, info in image_registry.images.items():
        iid = img_ids[k]
        w, h, stream = info['w'], info['h'], info['stream']
        h_str = f"{iid} 0 obj\n<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /FlateDecode /DecodeParms << /Predictor 15 /Columns {w} /Colors 3 /BitsPerComponent 8 >> /Length {len(stream)} >>\nstream\n"
        objects.append((h_str.encode('utf-8'), stream, b"\nendstream\nendobj"))

    for i, (stream_ops, used_imgs) in enumerate(canvas.pages):
        pid = page_ids[i]
        cid = content_ids[i]
        c_bytes = "\n".join(stream_ops).encode('utf-8')

        xobjs = " ".join(f"/{img_k} {img_ids[img_k]} 0 R" for img_k in used_imgs if img_k in img_ids)
        x_res = f"/XObject << {xobjs} >>" if xobjs else ""

        p_str = f"{pid} 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R /F4 6 0 R >> {x_res} >> /Contents {cid} 0 R >>\nendobj"
        objects.append(p_str)

        c_str = f"{cid} 0 obj\n<< /Length {len(c_bytes)} >>\nstream\n"
        objects.append((c_str.encode('utf-8'), c_bytes, b"\nendstream\nendobj"))

    pdf_buf = bytearray()
    pdf_buf.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for obj in objects:
        offsets.append(len(pdf_buf))
        if isinstance(obj, tuple):
            pdf_buf.extend(obj[0])
            pdf_buf.extend(obj[1])
            pdf_buf.extend(obj[2])
            pdf_buf.extend(b"\n")
        elif isinstance(obj, bytes):
            pdf_buf.extend(obj)
            pdf_buf.extend(b"\n")
        else:
            pdf_buf.extend(obj.encode('utf-8'))
            pdf_buf.extend(b"\n")

    xref_offset = len(pdf_buf)
    tot = len(objects) + 1
    pdf_buf.extend(f"xref\n0 {tot}\n0000000000 65535 f \n".encode('utf-8'))
    for off in offsets:
        pdf_buf.extend(f"{off:010d} 00000 n \n".encode('utf-8'))
    pdf_buf.extend(f"trailer\n<< /Size {tot} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode('utf-8'))

    with open(OUTPUT_PDF, 'wb') as f:
        f.write(pdf_buf)

    print(f"[[OK]] Successfully generated Condensed Lab Record Cut-Out PDF: {OUTPUT_PDF} ({len(pdf_buf)} bytes, {num_p} sheets)")
    return num_p

if __name__ == '__main__':
    # Optimize target_img_h to hit exactly 11 sheets
    for h in [120, 130, 135, 140, 145, 150]:
        sheets = build_condensed_pdf(target_img_h=h)
        print(f"Tested target_img_h={h} -> {sheets} sheets")
        if sheets == 11:
            print(f"[[PERFECT]] Exactly 11 sheets reached with target_img_h={h}")
            break
