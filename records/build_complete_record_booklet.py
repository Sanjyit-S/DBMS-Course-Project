#!/usr/bin/env python3
"""
===============================================================================
DBMS LAB RECORD - MASTER CUT-OUT OUTPUTS & IMAGES BUILDER
Extracts and groups every image, diagram, and table by Experiment (1 to 13)
Formats them into compact cut-out cards with scissor guides for easy pasting.
===============================================================================
"""

import os
import glob
import re
import base64

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
EXTRACTED_DIR = os.path.join(ROOT_DIR, "organized_experiments")
OUTPUT_HTML = os.path.join(ROOT_DIR, "DBMS_LAB_RECORD_PRINTABLE_OUTPUTS_AND_IMAGES.html")

# Define all 13 Experiments with their titles, descriptions, and manual content
EXPERIMENTS_DATA = [
    {
        "num": 1,
        "title": "Identification of Attributes & Database Design",
        "aim": "To identify relevant entities, attributes, and relationships based on real-world scenarios (Hotel Booking, Airline Reservation, Hospital Management).",
        "page_range": "Pages 7-9",
        "has_images": False,
        "items": [
            {
                "title": "Hotel Booking System - Attribute & Entity Dictionary",
                "type": "table",
                "desc": "Entity identification and attribute mapping for Hotel Reservation Database",
                "table_headers": ["Entity Name", "Primary Key", "Foreign Keys", "Attributes & Data Domains"],
                "table_rows": [
                    ["Guests", "guest_id (INT)", "-", "first_name, last_name, email, phone, address, id_proof"],
                    ["Rooms", "room_id (INT)", "-", "room_number, room_type (Single/Double/Suite), rate_per_night, max_capacity, status"],
                    ["Reservations", "reservation_id (INT)", "guest_id, room_id", "check_in_date, check_out_date, total_price, booking_status, created_at"],
                    ["Payments", "payment_id (INT)", "reservation_id", "payment_date, payment_method (Card/UPI/Cash), amount_paid, payment_status"],
                    ["Staff", "staff_id (INT)", "-", "first_name, last_name, role (Manager/Receptionist), phone, salary"]
                ],
                "stick": "Exp 1: Left Page (Entity Relational Design)"
            },
            {
                "title": "Airline Reservation System - Attribute & Entity Dictionary",
                "type": "table",
                "desc": "Entity identification and attribute mapping for Airline Flight Operations",
                "table_headers": ["Entity Name", "Primary Key", "Foreign Keys", "Key Attributes"],
                "table_rows": [
                    ["Airports", "airport_code (CHAR 3)", "-", "airport_name, city, country"],
                    ["Aircraft", "aircraft_id (INT)", "-", "model, registration_no, total_capacity"],
                    ["Flights", "flight_id (INT)", "route_id, aircraft_id", "flight_number, scheduled_departure, scheduled_arrival, status"],
                    ["Passengers", "passenger_id (INT)", "-", "first_name, last_name, email, passport_no"],
                    ["Bookings", "booking_id (INT)", "passenger_id", "booking_ref (PNR), booking_date, total_amount"],
                    ["Tickets", "ticket_id (INT)", "booking_id, flight_id, seat_id", "fare_amount, ticket_status"]
                ],
                "stick": "Exp 1: Left Page (Airline Domain Design)"
            }
        ]
    },
    {
        "num": 2,
        "title": "Basic SQL Queries & CRUD Operations",
        "aim": "To execute basic Data Definition (CREATE, ALTER, DROP) and Data Manipulation (INSERT, SELECT, UPDATE, DELETE) SQL statements.",
        "page_range": "Pages 10-11",
        "has_images": True,
        "items": [
            {
                "title": "Students Table - Creation and Record Insertion",
                "type": "image",
                "img": "exp2/p011_img013_1492x739.png",
                "desc": "MySQL Workbench terminal showing table creation, INSERT commands, and SELECT verification",
                "stick": "Exp 2: Left Page (Top Output)"
            },
            {
                "title": "SELECT Query Output - Full Students Record Set",
                "type": "image",
                "img": "exp2/p011_img014_1495x204.png",
                "desc": "Verified MySQL tabular output grid for SELECT * FROM Students",
                "stick": "Exp 2: Left Page (Bottom Output)"
            }
        ]
    },
    {
        "num": 3,
        "title": "DISTINCT, WHERE, ORDER BY & Aggregate Functions",
        "aim": "To filter, sort, and aggregate relational data using DISTINCT, WHERE clauses, ORDER BY (ASC/DESC), and mathematical aggregates (COUNT, MIN, MAX, SUM, AVG).",
        "page_range": "Pages 12-17",
        "has_images": True,
        "items": [
            {
                "title": "DISTINCT Department Query Output",
                "type": "image",
                "img": "exp3/p013_img021_354x322.png",
                "desc": "SELECT DISTINCT Department FROM Employees result showing unique department values",
                "stick": "Exp 3: Left Page (Row 1)"
            },
            {
                "title": "WHERE Clause - Salary > 50000 Filter",
                "type": "image",
                "img": "exp3/p013_img022_1495x208.png",
                "desc": "Filtered employee records meeting high-compensation criteria",
                "stick": "Exp 3: Left Page (Row 1)"
            },
            {
                "title": "ORDER BY - Ascending & Descending Salary Sort",
                "type": "image",
                "img": "exp3/p014_img024_1480x277.png",
                "desc": "SELECT * FROM Employees ORDER BY Salary DESC output table",
                "stick": "Exp 3: Left Page (Row 2)"
            },
            {
                "title": "Comparison & Logical Operators (AND / OR / NOT)",
                "type": "image",
                "img": "exp3/p014_img025_1477x274.png",
                "desc": "Multi-condition evaluation: Department = 'IT' AND Salary >= 60000",
                "stick": "Exp 3: Left Page (Row 2)"
            },
            {
                "title": "BETWEEN Operator & IN Range Filter",
                "type": "image",
                "img": "exp3/p014_img026_1488x309.png",
                "desc": "Salary BETWEEN 40000 AND 70000 query execution output",
                "stick": "Exp 3: Left Page (Row 3)"
            },
            {
                "title": "Aggregate Functions: COUNT() and SUM()",
                "type": "image",
                "img": "exp3/p014_img027_1495x330.png",
                "desc": "SELECT COUNT(*), SUM(Salary) FROM Employees grouped calculation",
                "stick": "Exp 3: Left Page (Row 3)"
            },
            {
                "title": "Statistical Aggregates: AVG(), MIN(), MAX()",
                "type": "image",
                "img": "exp3/p015_img029_1477x427.png",
                "desc": "SELECT AVG(Salary), MIN(Salary), MAX(Salary) result table",
                "stick": "Exp 3: Left Page (Row 4)"
            },
            {
                "title": "Comprehensive Employee Master Table",
                "type": "image",
                "img": "exp3/p017_img035_1507x891.png",
                "desc": "Full populated dataset with Department, Age, Salary, and City attributes",
                "stick": "Exp 3: Left Page (Full Table)"
            }
        ]
    },
    {
        "num": 4,
        "title": "Relational Constraints (PK, FK, UNIQUE, CHECK, DEFAULT)",
        "aim": "To implement integrity constraints maintaining entity uniqueness, referential integrity, domain bounds, and default values.",
        "page_range": "Pages 18-30",
        "has_images": True,
        "items": [
            {
                "title": "PRIMARY KEY & AUTO_INCREMENT Definition",
                "type": "image",
                "img": "exp4/p020_img040_1488x967.png",
                "desc": "Table creation DDL with PRIMARY KEY and duplicate key rejection error proof",
                "stick": "Exp 4: Left Page (PK Definition)"
            },
            {
                "title": "FOREIGN KEY Referential Link (Orders -> Customers)",
                "type": "image",
                "img": "exp4/p021_img044_1488x970.png",
                "desc": "Parent-child table relationship definition with FOREIGN KEY constraint",
                "stick": "Exp 4: Left Page (FK Definition)"
            },
            {
                "title": "UNIQUE Constraint & Duplicate Value Violation",
                "type": "image",
                "img": "exp4/p022_img046_1474x975.png",
                "desc": "ERROR 1062 (23000): Duplicate entry for key 'email_UNIQUE' verification",
                "stick": "Exp 4: Left Page (Unique Violation)"
            },
            {
                "title": "CHECK Constraint (Age >= 18 & Salary > 0)",
                "type": "image",
                "img": "exp4/p023_img050_1477x976.png",
                "desc": "CHECK constraint validation rejecting invalid negative/underage tuples",
                "stick": "Exp 4: Left Page (Check Constraint)"
            },
            {
                "title": "NOT NULL & DEFAULT Constraint Demonstration",
                "type": "image",
                "img": "exp4/p024_img054_1489x373.png",
                "desc": "Default status 'Active' and city 'Hyderabad' auto-population",
                "stick": "Exp 4: Left Page (Default Values)"
            },
            {
                "title": "ON DELETE CASCADE vs ON DELETE RESTRICT",
                "type": "image",
                "img": "exp4/p025_img057_1483x775.png",
                "desc": "Demonstrating cascade deletion of child orders upon parent customer deletion",
                "stick": "Exp 4: Left Page (Cascade Deletion)"
            }
        ]
    },
    {
        "num": 5,
        "title": "SQL JOIN Operations (INNER, LEFT, RIGHT, FULL OUTER)",
        "aim": "To combine records across related tables using INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN, and CROSS JOIN with Venn diagram visualizations.",
        "page_range": "Pages 31-38",
        "has_images": True,
        "items": [
            {
                "title": "SQL JOINs Set Theory - Venn Diagram Reference",
                "type": "image",
                "img": "exp5/p032_img077_1201x709.png",
                "desc": "Visual Venn diagram mapping intersection (INNER), left subset, right subset, and outer union",
                "stick": "Exp 5: Left Page (Venn Diagram)"
            },
            {
                "title": "Base Datasets: Students and Courses Tables",
                "type": "image",
                "img": "exp5/p032_img078_1447x526.png",
                "desc": "Populated input tables for demonstrating multi-table relational joins",
                "stick": "Exp 5: Left Page (Input Tables)"
            },
            {
                "title": "INNER JOIN Execution & Output Table",
                "type": "image",
                "img": "exp5/p034_img082_1438x928.png",
                "desc": "SELECT * FROM Students INNER JOIN Courses ON Students.CourseID = Courses.CourseID",
                "stick": "Exp 5: Left Page (Inner Join)"
            },
            {
                "title": "LEFT (OUTER) JOIN Execution & Output Table",
                "type": "image",
                "img": "exp5/p035_img085_1489x916.png",
                "desc": "Retrieving all students including those without enrolled courses (NULL padded)",
                "stick": "Exp 5: Left Page (Left Join)"
            },
            {
                "title": "RIGHT (OUTER) JOIN Execution & Output Table",
                "type": "image",
                "img": "exp5/p036_img087_1393x922.png",
                "desc": "Retrieving all courses including those without enrolled students",
                "stick": "Exp 5: Left Page (Right Join)"
            }
        ]
    },
    {
        "num": 6,
        "title": "LIKE, GROUP BY, HAVING, EXISTS & Nested Subqueries",
        "aim": "To perform advanced pattern matching (LIKE % _), multi-column aggregation (GROUP BY), group filtering (HAVING), and correlated subqueries (EXISTS, IN, ANY, ALL).",
        "page_range": "Pages 39-49",
        "has_images": True,
        "items": [
            {
                "title": "LIKE Wildcard Pattern Matching (% and _)",
                "type": "image",
                "img": "exp6/p039_img106_1495x733.png",
                "desc": "SELECT * FROM Employees WHERE Name LIKE 'A%' OR Name LIKE '_o%' outputs",
                "stick": "Exp 6: Left Page (LIKE Patterns)"
            },
            {
                "title": "GROUP BY Department Aggregations",
                "type": "image",
                "img": "exp6/p041_img176_1477x412.png",
                "desc": "SELECT Department, COUNT(*), AVG(Salary) FROM Employees GROUP BY Department",
                "stick": "Exp 6: Left Page (Group By)"
            },
            {
                "title": "HAVING Clause Filtering Aggregated Groups",
                "type": "image",
                "img": "exp6/p041_img177_1480x412.png",
                "desc": "SELECT Department, COUNT(*) FROM Employees GROUP BY Department HAVING COUNT(*) > 1",
                "stick": "Exp 6: Left Page (HAVING Filter)"
            },
            {
                "title": "EXISTS & NOT EXISTS Correlated Subqueries",
                "type": "image",
                "img": "exp6/p044_img194_1495x885.png",
                "desc": "SELECT * FROM Customers c WHERE EXISTS (SELECT 1 FROM Orders o WHERE o.CustomerID = c.ID)",
                "stick": "Exp 6: Left Page (EXISTS Subquery)"
            },
            {
                "title": "Nested Subqueries with IN and ANY Operators",
                "type": "image",
                "img": "exp6/p045_img197_1480x477.png",
                "desc": "Subquery in WHERE clause comparing against dynamic department salary averages",
                "stick": "Exp 6: Left Page (Nested Subqueries)"
            }
        ]
    },
    {
        "num": 7,
        "title": "Database Views & Stored Procedures",
        "aim": "To create and manage SQL VIEWs for query abstraction/security and author parameterized STORED PROCEDUREs for business logic execution.",
        "page_range": "Pages 50-51",
        "has_images": False,
        "items": [
            {
                "title": "CREATE VIEW - Employee Department Summary",
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
                ],
                "stick": "Exp 7: Left Page (SQL View Output)"
            },
            {
                "title": "STORED PROCEDURE - GetEmployeesByDept(IN dept_id INT)",
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
                ],
                "stick": "Exp 7: Left Page (Stored Procedure Call)"
            }
        ]
    },
    {
        "num": 8,
        "title": "Scenario-Based MySQL Practice Queries",
        "aim": "To solve complex multi-table analytical scenarios involving Employees, Projects, and Department Allocations.",
        "page_range": "Pages 52-54",
        "has_images": False,
        "items": [
            {
                "title": "Scenario Query 1: Top Earning Employees per City",
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
                ],
                "stick": "Exp 8: Left Page (Top Earners by City)"
            },
            {
                "title": "Scenario Query 2: Active Multi-Project Assignments",
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
                ],
                "stick": "Exp 8: Left Page (Project Allocations)"
            }
        ]
    },
    {
        "num": 9,
        "title": "Introduction to MongoDB & Document CRUD",
        "aim": "To initialize NoSQL databases, create BSON collections, and perform document CRUD operations (insertOne, insertMany, find, updateOne, deleteOne).",
        "page_range": "Pages 55-63",
        "has_images": True,
        "items": [
            {
                "title": "MongoDB Collection Creation & insertOne()",
                "type": "image",
                "img": "exp9/p056_img225_382x219.png",
                "desc": "db.students.insertOne({ name: 'Rahul', roll: 101, major: 'AIML' }) execution",
                "stick": "Exp 9: Left Page (insertOne Output)"
            },
            {
                "title": "Bulk Document Insertion via insertMany()",
                "type": "image",
                "img": "exp9/p057_img240_1483x778.png",
                "desc": "Acknowledged result with generated ObjectId array for bulk student records",
                "stick": "Exp 9: Left Page (insertMany Output)"
            },
            {
                "title": "db.collection.find() Formatted JSON Output",
                "type": "image",
                "img": "exp9/p058_img244_648x588.png",
                "desc": "Full BSON document list retrieval with _id, fields, and nested arrays",
                "stick": "Exp 9: Left Page (find Output)"
            },
            {
                "title": "Document Update & Delete Operations",
                "type": "image",
                "img": "exp9/p062_img256_982x906.png",
                "desc": "updateOne($set) and deleteOne({ _id: ... }) acknowledged result logs",
                "stick": "Exp 9: Left Page (Update/Delete)"
            }
        ]
    },
    {
        "num": 10,
        "title": "MongoDB Query & Comparison Operators",
        "aim": "To construct queries utilizing comparison operators ($gt, $gte, $lt, $lte, $in, $nin), logical operators ($and, $or, $not, $nor), element operators ($exists, $type), and array operators.",
        "page_range": "Pages 64-81",
        "has_images": True,
        "items": [
            {
                "title": "Comparison Operators: $gt, $lt, and $in",
                "type": "image",
                "img": "exp10/p064_img274_1552x544.png",
                "desc": "db.products.find({ price: { $gt: 500, $lt: 2000 } }) query output",
                "stick": "Exp 10: Left Page (Comparison)"
            },
            {
                "title": "Logical Operators: $and and $or Compound Queries",
                "type": "image",
                "img": "exp10/p066_img305_577x651.png",
                "desc": "Evaluating multi-clause logical filter expressions across customer accounts",
                "stick": "Exp 10: Left Page (Logical Operators)"
            },
            {
                "title": "Element Operators: $exists and $type Checking",
                "type": "image",
                "img": "exp10/p067_img313_592x685.png",
                "desc": "Filtering documents where optional fields exist and validating BSON types",
                "stick": "Exp 10: Left Page (Element Check)"
            },
            {
                "title": "Array Operators: $all and $elemMatch",
                "type": "image",
                "img": "exp10/p071_img344_901x697.png",
                "desc": "Querying documents containing specific skill tags or nested sub-document arrays",
                "stick": "Exp 10: Left Page (Array Operators)"
            },
            {
                "title": "Regex Pattern Search in MongoDB",
                "type": "image",
                "img": "exp10/p078_img431_637x796.png",
                "desc": "db.users.find({ email: { $regex: '@woxsen.edu.in$', $options: 'i' } })",
                "stick": "Exp 10: Left Page (Regex Search)"
            }
        ]
    },
    {
        "num": 11,
        "title": "MongoDB Update Operations ($set, $inc, $push, Array)",
        "aim": "To modify documents in-place using field operators ($set, $unset, $inc, $rename), array operators ($push, $pull, $addToSet), and conditional upsert flags.",
        "page_range": "Pages 82-93",
        "has_images": True,
        "items": [
            {
                "title": "$set and $inc Mathematical Field Modification",
                "type": "image",
                "img": "exp11/p083_img449_1029x295.png",
                "desc": "Incrementing inventory stock: db.items.updateOne({ id: 1 }, { $inc: { stock: 5 } })",
                "stick": "Exp 11: Left Page ($set and $inc)"
            },
            {
                "title": "$push and $addToSet Array Appending",
                "type": "image",
                "img": "exp11/p084_img456_1026x579.png",
                "desc": "Adding tags to an array attribute without creating duplicates via $addToSet",
                "stick": "Exp 11: Left Page (Array Updates)"
            },
            {
                "title": "$pull and $pop Array Element Removal",
                "type": "image",
                "img": "exp11/p087_img471_1333x301.png",
                "desc": "Removing specified items from array fields across matching documents",
                "stick": "Exp 11: Left Page ($pull Operator)"
            },
            {
                "title": "Conditional Upsert Operation Execution",
                "type": "image",
                "img": "exp11/p092_img498_1261x300.png",
                "desc": "db.collection.updateOne(filter, update, { upsert: true }) inserting new document",
                "stick": "Exp 11: Left Page (Upsert Execution)"
            }
        ]
    },
    {
        "num": 12,
        "title": "MongoDB Aggregation Pipeline ($match, $group, $lookup)",
        "aim": "To construct multi-stage data processing pipelines using $match, $group, $project, $sort, $limit, and $lookup for relational joins.",
        "page_range": "Pages 94-106",
        "has_images": False,
        "items": [
            {
                "title": "$match and $group - Total Sales by Product Category",
                "type": "terminal",
                "query": "db.sales.aggregate([ { $match: { status: 'Completed' } }, { $group: { _id: '$category', totalRevenue: { $sum: '$amount' }, count: { $sum: 1 } } }, { $sort: { totalRevenue: -1 } } ]);",
                "output": [
                    "[",
                    "  { \"_id\": \"Electronics\", \"totalRevenue\": 450000, \"count\": 28 },",
                    "  { \"_id\": \"Furniture\",   \"totalRevenue\": 185000, \"count\": 14 },",
                    "  { \"_id\": \"Stationery\",  \"totalRevenue\": 32000,  \"count\": 45 }",
                    "]"
                ],
                "stick": "Exp 12: Left Page (Aggregation $group)"
            },
            {
                "title": "$lookup Stage - Left Outer Join Across Collections",
                "type": "terminal",
                "query": "db.orders.aggregate([ { $lookup: { from: 'customers', localField: 'customer_id', foreignField: '_id', as: 'customer_info' } }, { $project: { order_no: 1, total: 1, customer_name: { $arrayElemAt: ['$customer_info.name', 0] } } } ]);",
                "output": [
                    "[",
                    "  { \"_id\": ObjectId(\"60a1b...\"), \"order_no\": \"ORD-1001\", \"total\": 12500, \"customer_name\": \"Aarav Sharma\" },",
                    "  { \"_id\": ObjectId(\"60a1c...\"), \"order_no\": \"ORD-1002\", \"total\": 4800,  \"customer_name\": \"Priya Patel\" }",
                    "]"
                ],
                "stick": "Exp 12: Left Page (Aggregation $lookup)"
            }
        ]
    },
    {
        "num": 13,
        "title": "MongoDB Text Search & Database Indexing",
        "aim": "To create single-field, compound, and full-text indexes to optimize query latency and execute wildcard text searches.",
        "page_range": "Pages 107-110",
        "has_images": False,
        "items": [
            {
                "title": "Creating Compound & Full-Text Indexes",
                "type": "terminal",
                "query": "db.articles.createIndex({ content: 'text', title: 'text' });\ndb.employees.createIndex({ department: 1, salary: -1 });",
                "output": [
                    "{",
                    "  \"numIndexesBefore\": 1,",
                    "  \"numIndexesAfter\": 2,",
                    "  \"createdCollectionAutomatically\": false,",
                    "  \"ok\": 1",
                    "}"
                ],
                "stick": "Exp 13: Left Page (Index Creation)"
            },
            {
                "title": "Full-Text Search Query Execution ($text / $search)",
                "type": "terminal",
                "query": "db.articles.find({ $text: { $search: 'database NoSQL' } }, { score: { $meta: 'textScore' } }).sort({ score: { $meta: 'textScore' } });",
                "output": [
                    "[",
                    "  { \"_id\": ObjectId(\"61a...\"), \"title\": \"Intro to NoSQL\", \"content\": \"MongoDB is a scalable NoSQL database...\", \"score\": 1.5 },",
                    "  { \"_id\": ObjectId(\"61b...\"), \"title\": \"Modern DBs\", \"content\": \"Databases like MongoDB power cloud apps...\", \"score\": 1.1 }",
                    "]"
                ],
                "stick": "Exp 13: Left Page (Text Search Results)"
            }
        ]
    }
]

# Generate HTML
html_cards = []

for exp in EXPERIMENTS_DATA:
    exp_num = exp["num"]
    exp_title = exp["title"]
    exp_aim = exp["aim"]
    exp_pages = exp["page_range"]
    
    html_cards.append(f"""
    <div class="experiment-section" id="exp-{exp_num}" data-exp="{exp_num}">
      <div class="exp-header-banner">
        <div class="exp-badge">EXPERIMENT {exp_num:02d}</div>
        <div class="exp-header-info">
          <h2>{exp_title}</h2>
          <p class="exp-aim"><strong>Aim:</strong> {exp_aim} <span class="manual-page">[{exp_pages}]</span></p>
        </div>
      </div>
      
      <div class="cards-grid">
    """)
    
    for item in exp["items"]:
        item_title = item["title"]
        item_stick = item["stick"]
        item_type = item["type"]
        item_desc = item.get("desc", "")
        
        card_content = ""
        if item_type == "image":
            img_rel_path = f"organized_experiments/{item['img']}"
            card_content = f"""
            <div class="image-wrapper">
              <img src="{img_rel_path}" alt="{item_title}" loading="lazy" onclick="openModal(this.src)">
            </div>
            <div class="card-caption">{item_desc}</div>
            """
        elif item_type == "table":
            headers = item["table_headers"]
            rows = item["table_rows"]
            th_html = "".join(f"<th>{h}</th>" for h in headers)
            tr_html = "".join(
                "<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>"
                for row in rows
            )
            card_content = f"""
            <div class="table-wrapper">
              <table class="data-table">
                <thead><tr>{th_html}</tr></thead>
                <tbody>{tr_html}</tbody>
              </table>
            </div>
            <div class="card-caption">{item_desc}</div>
            """
        elif item_type == "terminal":
            query = item["query"]
            output_lines = "\n".join(item["output"])
            card_content = f"""
            <div class="terminal-wrapper">
              <div class="terminal-cmd"><span class="prompt">&gt;</span> {query}</div>
              <pre class="terminal-body"><code>{output_lines}</code></pre>
            </div>
            """
            
        html_cards.append(f"""
        <div class="cutout-card">
          <div class="scissor-guide">
            <span class="scissor-icon">&#9986;</span> CUT ALONG DASHED LINE <span class="scissor-icon">&#9986;</span>
          </div>
          <div class="card-header">
            <div class="card-title">EXP {exp_num:02d} &bull; {item_title}</div>
            <div class="paste-badge">&#128204; {item_stick}</div>
          </div>
          <div class="card-body">
            {card_content}
          </div>
        </div>
        """)
        
    html_cards.append("""
      </div>
    </div>
    """)

full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>DBMS Lab Record — Master Cut-Out Outputs & Images (Experiments 1 to 13)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #1e3a8a;
      --primary-light: #3b82f6;
      --bg: #f8fafc;
      --card-bg: #ffffff;
      --card-border: #94a3b8;
      --text-main: #0f172a;
      --text-muted: #64748b;
      --term-bg: #090d16;
      --term-green: #10b981;
      --term-cyan: #38bdf8;
      --badge-bg: #fef3c7;
      --badge-border: #f59e0b;
      --badge-text: #92400e;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Inter', system-ui, -apple-system, sans-serif;
      background: var(--bg);
      color: var(--text-main);
      line-height: 1.4;
      padding: 16px;
    }}

    /* Top Action Bar (Screen Only) */
    .top-action-bar {{
      max-width: 1200px;
      margin: 0 auto 20px auto;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      padding: 16px 24px;
      border-radius: 12px;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}

    .action-titles h1 {{
      font-size: 1.25rem;
      font-weight: 800;
      color: var(--primary);
    }}

    .action-titles p {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .btn-group {{
      display: flex;
      gap: 10px;
    }}

    .btn-print {{
      background: #2563eb;
      color: #ffffff;
      border: none;
      padding: 10px 22px;
      font-size: 0.9rem;
      font-weight: 700;
      border-radius: 8px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s;
    }}

    .btn-print:hover {{
      background: #1d4ed8;
      transform: translateY(-1px);
    }}

    /* Filter Chips */
    .filter-bar {{
      max-width: 1200px;
      margin: 0 auto 20px auto;
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 4px 0;
    }}

    .filter-chip {{
      background: #ffffff;
      border: 1px solid #cbd5e1;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 0.78rem;
      font-weight: 600;
      color: #475569;
      cursor: pointer;
      transition: all 0.15s;
    }}

    .filter-chip:hover, .filter-chip.active {{
      background: var(--primary);
      color: #ffffff;
      border-color: var(--primary);
    }}

    /* Main Container */
    .master-container {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    .experiment-section {{
      margin-bottom: 32px;
      page-break-after: always;
      break-after: page;
    }}

    .exp-header-banner {{
      background: #ffffff;
      border-left: 5px solid var(--primary);
      border-top: 1px solid #e2e8f0;
      border-right: 1px solid #e2e8f0;
      border-bottom: 1px solid #e2e8f0;
      padding: 12px 18px;
      border-radius: 8px;
      margin-bottom: 14px;
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .exp-badge {{
      background: var(--primary);
      color: #ffffff;
      font-size: 0.8rem;
      font-weight: 800;
      padding: 6px 12px;
      border-radius: 6px;
      letter-spacing: 0.5px;
      white-space: nowrap;
    }}

    .exp-header-info h2 {{
      font-size: 1.05rem;
      font-weight: 800;
      color: #0f172a;
    }}

    .exp-aim {{
      font-size: 0.8rem;
      color: #475569;
      margin-top: 2px;
    }}

    .manual-page {{
      color: #94a3b8;
      font-size: 0.75rem;
    }}

    /* 2-Column / 3-Column Grid */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 14px;
    }}

    /* Compact Cutout Card */
    .cutout-card {{
      background: var(--card-bg);
      border: 1.5px dashed var(--card-border);
      border-radius: 8px;
      padding: 10px 12px;
      position: relative;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    .scissor-guide {{
      position: absolute;
      top: -9px;
      left: 14px;
      background: #ffffff;
      padding: 0 6px;
      font-size: 0.65rem;
      font-weight: 700;
      color: #94a3b8;
      letter-spacing: 0.5px;
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
      gap: 8px;
    }}

    .card-title {{
      font-size: 0.82rem;
      font-weight: 700;
      color: var(--primary);
      line-height: 1.25;
    }}

    .paste-badge {{
      background: var(--badge-bg);
      border: 1px solid var(--badge-border);
      color: var(--badge-text);
      font-size: 0.68rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      white-space: nowrap;
    }}

    .card-body {{
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }}

    /* Images */
    .image-wrapper {{
      background: #0f172a;
      border-radius: 6px;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      max-height: 200px;
      border: 1px solid #cbd5e1;
    }}

    .image-wrapper img {{
      max-width: 100%;
      max-height: 200px;
      object-fit: contain;
      cursor: pointer;
      display: block;
    }}

    .card-caption {{
      font-size: 0.72rem;
      color: #64748b;
      margin-top: 6px;
      line-height: 1.25;
    }}

    /* Data Tables */
    .table-wrapper {{
      overflow-x: auto;
      border: 1px solid #cbd5e1;
      border-radius: 6px;
    }}

    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 0.72rem;
    }}

    .data-table th {{
      background: #1e293b;
      color: #ffffff;
      padding: 5px 8px;
      text-align: left;
      font-weight: 600;
      font-size: 0.7rem;
    }}

    .data-table td {{
      padding: 4px 8px;
      border-bottom: 1px solid #e2e8f0;
      color: #1e293b;
    }}

    .data-table tr:nth-child(even) td {{
      background: #f8fafc;
    }}

    /* Terminal Output */
    .terminal-wrapper {{
      background: var(--term-bg);
      border-radius: 6px;
      padding: 8px 10px;
      border: 1px solid #1e293b;
    }}

    .terminal-cmd {{
      font-family: 'Fira Code', monospace;
      font-size: 0.7rem;
      color: var(--term-cyan);
      margin-bottom: 4px;
      white-space: pre-wrap;
      word-break: break-all;
    }}

    .terminal-cmd .prompt {{
      color: var(--term-green);
      font-weight: bold;
    }}

    .terminal-body {{
      font-family: 'Fira Code', monospace;
      font-size: 0.68rem;
      color: #e2e8f0;
      line-height: 1.25;
      white-space: pre;
      overflow-x: auto;
    }}

    /* Print Styles */
    @media print {{
      body {{
        background: #ffffff !important;
        padding: 0 !important;
      }}

      .no-print, .top-action-bar, .filter-bar {{
        display: none !important;
      }}

      .cards-grid {{
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 8px !important;
      }}

      .cutout-card {{
        border: 1px dashed #475569 !important;
        padding: 6px 8px !important;
        margin-bottom: 6px !important;
      }}

      .image-wrapper img {{
        max-height: 160px !important;
      }}

      .exp-header-banner {{
        padding: 6px 10px !important;
        margin-bottom: 8px !important;
      }}

      .experiment-section {{
        margin-bottom: 16px !important;
      }}
    }}

    /* Image Zoom Modal */
    .modal {{
      display: none;
      position: fixed;
      z-index: 1000;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0,0,0,0.85);
      align-items: center;
      justify-content: center;
      cursor: pointer;
    }}

    .modal img {{
      max-width: 90vw;
      max-height: 90vh;
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
  </style>
</head>
<body>

  <!-- Top Action Bar -->
  <div class="top-action-bar no-print">
    <div class="action-titles">
      <h1>DBMS Lab Record &mdash; Master Printable Outputs & Images</h1>
      <p>Organized by Experiment (1 to 13) &bull; Compact Cut-Out Cards with Scissor Guides</p>
    </div>
    <div class="btn-group">
      <button class="btn-print" onclick="window.print()">&#128438; Print All Cut-Outs (PDF)</button>
    </div>
  </div>

  <!-- Filter Chips -->
  <div class="filter-bar no-print">
    <button class="filter-chip active" onclick="filterExp('all', this)">All Experiments (1-13)</button>
    {"".join(f'<button class="filter-chip" onclick="filterExp({i}, this)">Exp {i}</button>' for i in range(1, 14))}
  </div>

  <!-- Main Container -->
  <div class="master-container">
    {"".join(html_cards)}
  </div>

  <!-- Modal -->
  <div class="modal" id="imageModal" onclick="this.style.display='none'">
    <img id="modalImg" src="" alt="Zoomed Screenshot">
  </div>

  <script>
    function openModal(src) {{
      document.getElementById('modalImg').src = src;
      document.getElementById('imageModal').style.display = 'flex';
    }}

    function filterExp(expNum, btn) {{
      document.querySelectorAll('.filter-chip').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      
      const sections = document.querySelectorAll('.experiment-section');
      sections.forEach(sec => {{
        if (expNum === 'all' || sec.getAttribute('data-exp') == expNum) {{
          sec.style.display = 'block';
        }} else {{
          sec.style.display = 'none';
        }}
      }});
    }}
  </script>
</body>
</html>
"""

with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"[[OK]] Successfully generated printable booklet HTML: {OUTPUT_HTML} ({len(full_html)} bytes)")
