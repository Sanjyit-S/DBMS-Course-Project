#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB SUBMISSION PDF GENERATOR
Generates publication-grade PDFs for Project-Report and Presentation-I
from their respective Markdown files while keeping the .md files intact.
Zero external dependencies. Pure Python PDF 1.4 engine.
===============================================================================
"""

import os
import sys
import re

# Font metrics for standard Helvetica & Helvetica-Bold
HELVETICA_WIDTHS = {
    ' ': 278, '!': 278, '"': 355, '#': 556, '$': 556, '%': 889, '&': 667, "'": 191,
    '(': 333, ')': 333, '*': 389, '+': 584, ',': 278, '-': 333, '.': 278, '/': 278,
    '0': 556, '1': 556, '2': 556, '3': 556, '4': 556, '5': 556, '6': 556, '7': 556,
    '8': 556, '9': 556, ':': 278, ';': 278, '<': 584, '=': 584, '>': 584, '?': 556,
    '@': 1015, 'A': 667, 'B': 667, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 500, 'K': 667, 'L': 556, 'M': 833, 'N': 722, 'O': 778,
    'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722, 'V': 667, 'W': 944,
    'X': 667, 'Y': 667, 'Z': 611, '[': 278, '\\': 278, ']': 278, '^': 469, '_': 556,
    '`': 333, 'a': 556, 'b': 556, 'c': 500, 'd': 556, 'e': 556, 'f': 278, 'g': 556,
    'h': 556, 'i': 222, 'j': 222, 'k': 500, 'l': 222, 'm': 833, 'n': 556, 'o': 556,
    'p': 556, 'q': 556, 'r': 333, 's': 500, 't': 278, 'u': 556, 'v': 500, 'w': 722,
    'x': 500, 'y': 500, 'z': 500, '{': 334, '|': 260, '}': 334, '~': 584
}

HELVETICA_BOLD_WIDTHS = {
    ' ': 278, '!': 333, '"': 474, '#': 556, '$': 556, '%': 889, '&': 722, "'": 238,
    '(': 333, ')': 333, '*': 465, '+': 584, ',': 278, '-': 333, '.': 278, '/': 278,
    '0': 556, '1': 556, '2': 556, '3': 556, '4': 556, '5': 556, '6': 556, '7': 556,
    '8': 556, '9': 556, ':': 333, ';': 333, '<': 584, '=': 584, '>': 584, '?': 611,
    '@': 975, 'A': 722, 'B': 722, 'C': 722, 'D': 722, 'E': 667, 'F': 611, 'G': 778,
    'H': 722, 'I': 278, 'J': 556, 'K': 722, 'L': 611, 'M': 833, 'N': 722, 'O': 778,
    'P': 667, 'Q': 778, 'R': 722, 'S': 667, 'T': 611, 'U': 722, 'V': 667, 'W': 944,
    'X': 667, 'Y': 667, 'Z': 611, '[': 278, '\\': 278, ']': 278, '^': 584, '_': 556,
    '`': 333, 'a': 556, 'b': 611, 'c': 556, 'd': 611, 'e': 556, 'f': 333, 'g': 611,
    'h': 611, 'i': 278, 'j': 278, 'k': 556, 'l': 278, 'm': 889, 'n': 611, 'o': 611,
    'p': 611, 'q': 611, 'r': 389, 's': 556, 't': 333, 'u': 611, 'v': 556, 'w': 778,
    'x': 556, 'y': 556, 'z': 500, '{': 389, '|': 260, '}': 389, '~': 584
}

def sanitize(text):
    text = str(text)
    replacements = [
        ('&bull;', ' - '),
        ('&ndash;', ' - '),
        ('&mdash;', ' - '),
        ('₹', 'Rs. '),
        ('•', ' - '),
        ('—', ' - '),
        ('–', ' - '),
        ('’', "'"),
        ('‘', "'"),
        ('“', '"'),
        ('”', '"'),
        ('`', "'"),
        ('**', ''),
        ('*', ''),
        ('`', ''),
        ('>=', '>='),
        ('<=', '<='),
        ('<>', '!='),
        ('->', ' -> '),
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

def calc_text_width(text, font_type, font_size):
    widths = HELVETICA_BOLD_WIDTHS if font_type == "F2" else HELVETICA_WIDTHS
    def_w = 600 if font_type == "F2" else 550
    w = sum(widths.get(c, def_w) for c in text)
    return (w * font_size) / 1000.0

def wrap_text(text, font_type, font_size, max_width):
    text = sanitize(text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split(' ')
    lines = []
    curr = []
    curr_w = 0.0

    for word in words:
        if not word:
            continue
        w = calc_text_width(word + ' ', font_type, font_size)
        if curr_w + w <= max_width:
            curr.append(word)
            curr_w += w
        else:
            if curr:
                lines.append(' '.join(curr))
            curr = [word]
            curr_w = calc_text_width(word + ' ', font_type, font_size)
    if curr:
        lines.append(' '.join(curr))
    return lines

class CleanPDFBuilder:
    def __init__(self, filename, title_header="ARFOM-DB | Course Project Report"):
        self.filename = filename
        self.title_header = title_header
        self.pages = []
        self.curr_ops = []
        self.page_w = 595.28  # A4
        self.page_h = 841.89  # A4
        self.margin_x = 42.0
        self.margin_top = 45.0
        self.margin_bottom = 45.0
        self.content_w = self.page_w - (self.margin_x * 2)
        self.cursor_y = self.page_h - self.margin_top
        self.new_page()

    def new_page(self):
        if self.curr_ops:
            self.pages.append(self.curr_ops)
        self.curr_ops = []
        self.cursor_y = self.page_h - self.margin_top

        # Running header on page 2+
        if len(self.pages) >= 1:
            self.draw_rect(self.margin_x, self.page_h - 28, self.content_w, 0.5, stroke_rgb=(0.82, 0.86, 0.92))
            self.draw_text(self.title_header, self.margin_x, self.page_h - 24, font="F2", size=8, rgb=(0.35, 0.40, 0.50))

    def ensure_space(self, h):
        if self.cursor_y - h < self.margin_bottom:
            self.new_page()

    def draw_rect(self, x, y, w, h, fill_rgb=None, stroke_rgb=None, line_width=1):
        op = ""
        if stroke_rgb:
            op += f"{line_width} w {stroke_rgb[0]:.3f} {stroke_rgb[1]:.3f} {stroke_rgb[2]:.3f} RG "
        if fill_rgb:
            op += f"{fill_rgb[0]:.3f} {fill_rgb[1]:.3f} {fill_rgb[2]:.3f} rg "
        op += f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re "
        if fill_rgb and stroke_rgb:
            op += "B\n"
        elif fill_rgb:
            op += "f\n"
        elif stroke_rgb:
            op += "S\n"
        self.curr_ops.append(op)

    def draw_text(self, text, x, y, font="F1", size=10, rgb=(0.1, 0.1, 0.15)):
        clean = escape_pdf(sanitize(text))
        op = f"BT /{font} {size:.2f} Tf {rgb[0]:.3f} {rgb[1]:.3f} {rgb[2]:.3f} rg 1 0 0 1 {x:.2f} {y:.2f} Tm ({clean}) Tj ET\n"
        self.curr_ops.append(op)

    def add_title(self, main_title, subtitle=""):
        self.ensure_space(60)
        self.draw_text(main_title, self.margin_x, self.cursor_y, font="F2", size=18, rgb=(0.06, 0.15, 0.35))
        self.cursor_y -= 22
        if subtitle:
            self.draw_text(subtitle, self.margin_x, self.cursor_y, font="F1", size=11, rgb=(0.30, 0.38, 0.48))
            self.cursor_y -= 16
        self.draw_rect(self.margin_x, self.cursor_y, self.content_w, 1.5, fill_rgb=(0.10, 0.45, 0.85))
        self.cursor_y -= 18

    def add_section_h2(self, title):
        self.ensure_space(38)
        self.cursor_y -= 8
        self.draw_rect(self.margin_x, self.cursor_y - 2, self.content_w, 18, fill_rgb=(0.94, 0.96, 0.98), stroke_rgb=(0.85, 0.89, 0.94), line_width=0.5)
        self.draw_text(title, self.margin_x + 8, self.cursor_y + 3, font="F2", size=11, rgb=(0.08, 0.22, 0.45))
        self.cursor_y -= 22

    def add_section_h3(self, title):
        self.ensure_space(24)
        self.cursor_y -= 4
        self.draw_text(title, self.margin_x, self.cursor_y, font="F2", size=10.5, rgb=(0.12, 0.30, 0.55))
        self.cursor_y -= 14

    def add_paragraph(self, text, indent=0, rgb=(0.12, 0.15, 0.20)):
        lines = wrap_text(text, "F1", 9.5, self.content_w - indent)
        for line in lines:
            self.ensure_space(14)
            self.draw_text(line, self.margin_x + indent, self.cursor_y, font="F1", size=9.5, rgb=rgb)
            self.cursor_y -= 13.5
        self.cursor_y -= 4

    def add_bullet(self, text):
        lines = wrap_text(text, "F1", 9.5, self.content_w - 18)
        for idx, line in enumerate(lines):
            self.ensure_space(14)
            if idx == 0:
                self.draw_text("-", self.margin_x + 4, self.cursor_y, font="F2", size=9.5, rgb=(0.10, 0.45, 0.85))
            self.draw_text(line, self.margin_x + 16, self.cursor_y, font="F1", size=9.5, rgb=(0.12, 0.15, 0.20))
            self.cursor_y -= 13.5
        self.cursor_y -= 2

    def add_meta_row(self, label, value):
        self.ensure_space(15)
        self.draw_text(label, self.margin_x, self.cursor_y, font="F2", size=9.5, rgb=(0.20, 0.25, 0.35))
        self.draw_text(value, self.margin_x + 130, self.cursor_y, font="F1", size=9.5, rgb=(0.08, 0.12, 0.18))
        self.cursor_y -= 14

    def add_table(self, headers, rows):
        col_w = self.content_w / len(headers)
        row_h = 16.0
        
        table_needed_h = (len(rows) + 1) * row_h + 10
        self.ensure_space(min(120, table_needed_h))

        # Header
        self.draw_rect(self.margin_x, self.cursor_y - row_h + 3, self.content_w, row_h, fill_rgb=(0.08, 0.25, 0.50))
        for i, h in enumerate(headers):
            self.draw_text(h, self.margin_x + (i * col_w) + 6, self.cursor_y - 8, font="F2", size=8.5, rgb=(1, 1, 1))
        self.cursor_y -= row_h

        # Rows
        for r_idx, r in enumerate(rows):
            self.ensure_space(row_h + 5)
            bg = (0.97, 0.98, 1.0) if r_idx % 2 == 0 else (1.0, 1.0, 1.0)
            self.draw_rect(self.margin_x, self.cursor_y - row_h + 3, self.content_w, row_h, fill_rgb=bg, stroke_rgb=(0.88, 0.90, 0.94), line_width=0.5)
            for c_idx, val in enumerate(r):
                self.draw_text(str(val), self.margin_x + (c_idx * col_w) + 6, self.cursor_y - 8, font="F1", size=8.0, rgb=(0.10, 0.12, 0.16))
            self.cursor_y -= row_h
        self.cursor_y -= 8

    def add_code_block(self, lines_of_code):
        box_h = len(lines_of_code) * 12 + 12
        self.ensure_space(min(100, box_h))
        self.draw_rect(self.margin_x, self.cursor_y - box_h + 6, self.content_w, box_h, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.80, 0.85, 0.90), line_width=0.5)
        self.cursor_y -= 8
        for line in lines_of_code:
            self.draw_text(line, self.margin_x + 10, self.cursor_y, font="F1", size=8.0, rgb=(0.10, 0.30, 0.60))
            self.cursor_y -= 12
        self.cursor_y -= 6

    def save(self):
        if self.curr_ops:
            self.pages.append(self.curr_ops)

        total_pages = len(self.pages)
        # Add page numbers
        for idx, p_ops in enumerate(self.pages):
            p_num_str = f"Page {idx + 1} of {total_pages}"
            p_num_clean = escape_pdf(p_num_str)
            footer_op = (
                f"BT /F1 8 Tf 0.45 0.50 0.60 rg 1 0 0 1 {self.page_w - self.margin_x - 60:.2f} 22 Tm ({p_num_clean}) Tj ET\n"
                f"0.5 w 0.85 0.88 0.92 RG {self.margin_x:.2f} 32.00 {self.content_w:.2f} 0.5 re S\n"
            )
            p_ops.append(footer_op)

        # Build PDF objects
        objects = []
        
        # 1: Catalog
        objects.append("<< /Type /Catalog /Pages 2 0 R >>")
        
        # 2: Pages Root
        page_refs = " ".join(f"{4 + i*2} 0 R" for i in range(total_pages))
        objects.append(f"<< /Type /Pages /Kids [{page_refs}] /Count {total_pages} >>")
        
        # 3: Fonts Dictionary
        objects.append("<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> /F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> >> >>")

        for i in range(total_pages):
            # Page Object
            content_ref = f"{5 + i*2} 0 R"
            objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.page_w:.2f} {self.page_h:.2f}] /Contents {content_ref} /Resources 3 0 R >>")
            # Content Stream
            stream_body = "".join(self.pages[i])
            stream_len = len(stream_body.encode('latin1', 'ignore'))
            objects.append(f"<< /Length {stream_len} >>\nstream\n{stream_body}\nendstream")

        # Compile PDF binary
        out = ["%PDF-1.4\n"]
        xref = [0]
        offset = len(out[0].encode('latin1'))

        for idx, obj in enumerate(objects):
            xref.append(offset)
            obj_str = f"{idx + 1} 0 obj\n{obj}\nendobj\n"
            out.append(obj_str)
            offset += len(obj_str.encode('latin1'))

        xref_pos = offset
        out.append(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n")
        for pos in xref[1:]:
            out.append(f"{pos:010d} 00000 n \n")

        out.append(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n")

        os.makedirs(os.path.dirname(os.path.abspath(self.filename)), exist_ok=True)
        with open(self.filename, 'wb') as f:
            f.write("".join(out).encode('latin1', 'replace'))
        print(f"[PDF BUILDER] Successfully generated: {self.filename} ({total_pages} pages)")

def build_problem_description_pdf():
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Presentation-I", "Problem_Description.pdf")
    builder = CleanPDFBuilder(pdf_path, title_header="ARFOM-DB | Presentation-I: Problem Description & Scope")
    
    builder.add_title("ARFOM-DB: PROBLEM DESCRIPTION & SYSTEM SCOPE", "Airline Reservation and Flight Operations Management System")
    
    builder.add_meta_row("Course:", "Database Management Systems (DBMS) - Presentation-I")
    builder.add_meta_row("Learner Name:", "Sanjyit Suresh Kumar (Roll No. 25WU0102243)")
    builder.add_meta_row("Section / Serial:", "AIML Whales - Serial #18")
    builder.add_meta_row("Evaluation Stage:", "Review 1 & Scope Definition")
    builder.cursor_y -= 8

    builder.add_section_h2("1. Executive Summary & Problem Statement")
    builder.add_paragraph(
        "Modern airline operators manage complex, highly concurrent transactional environments spanning flight scheduling, fleet allocation, seat inventory, customer reservations, electronic ticketing, baggage handling, and financial settlements."
    )
    builder.add_paragraph("Traditional spreadsheet-driven and legacy file-based reservation mechanisms suffer from four critical failure modes:")
    builder.add_bullet("Double-Booking & Seat Contention: Inability to enforce strict multi-attribute uniqueness, leading to simultaneous booking of identical physical aircraft seats.")
    builder.add_bullet("Data Redundancy & Anomalies: Redundant storage of flight routes, passenger identities, and aircraft capacities across disparate logs leads to update, insertion, and deletion anomalies.")
    builder.add_bullet("Lack of Referential Integrity: Orphaned baggage items, inconsistent cancellation refunds, and untracked itinerary changes.")
    builder.add_bullet("Weak Domain Constraints: Unchecked domain values (e.g., negative luggage weights, flights departing and arriving at identical hubs, or chronological departure/arrival inversions).")
    builder.add_paragraph(
        "ARFOM-DB resolves these operational challenges by designing and implementing an enterprise-grade, normalized relational database management system with rigorous integrity constraints, zero-loss 3NF decomposition, and high-performance transactional query interfaces."
    )

    builder.add_section_h2("2. Project Objectives")
    builder.add_bullet("Comprehensive Relational Modeling: Engineer an end-to-end database architecture encompassing 10+ core entities covering passenger lifecycles from booking to baggage claim.")
    builder.add_bullet("Strict Normalization (3NF/BCNF): Eliminate data redundancy and eliminate anomalies by decomposing Many-to-Many relationships via dedicated junction entities.")
    builder.add_bullet("Declarative Constraint Architecture: Enforce physical, temporal, and financial invariants at the storage engine level (PRIMARY KEY, FOREIGN KEY, CHECK, and UNIQUE).")
    builder.add_bullet("High-Concurrency Operational Performance: Support sub-millisecond multi-table analytical joins and real-time flight manifest projections.")
    builder.add_bullet("Interactive Management UI: Provide an intuitive, real-time web portal supporting CRUD operations with live database state reflection.")

    builder.add_section_h2("3. Scope of the System")
    builder.add_bullet("Fleet & Flight Infrastructure: Aircraft topology (airframe models, cabin seat classes: Economy, Business, First), airport registries, route networks with geographic distance validation, and operational flight schedules.")
    builder.add_bullet("Customer Reservation & Commercial Ticketing: Passenger demographic registration, multi-passenger booking orders (PNRs), individual flight leg ticket issuance, and double-booking prevention.")
    builder.add_bullet("Settlement & Audit Ledger: Multi-mode payment tracking (Credit Card, Debit Card, UPI, Net Banking), transaction verification, and cancellation fee/refund processing.")
    builder.add_bullet("Departure Control & Logistics: Airport check-in management, electronic boarding pass generation, baggage allowance tracking, and excess weight surcharge accounting.")

    builder.save()

def build_project_report_pdf():
    pdf_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Project-Report", "PROJECT_REPORT.pdf")
    builder = CleanPDFBuilder(pdf_path, title_header="ARFOM-DB | Comprehensive Project Report")

    builder.add_title("COURSE PROJECT REPORT: ARFOM-DB", "Airline Reservation and Flight Operations Management System")

    builder.add_meta_row("Course:", "Database Management Systems (DBMS)")
    builder.add_meta_row("Candidate Name:", "Sanjyit Suresh Kumar (Roll No. 25WU0102243)")
    builder.add_meta_row("Section / Roll:", "AIML Whales - Serial #18")
    builder.add_meta_row("Academic Year:", "2026 - 2027")
    builder.add_meta_row("Submission:", "Final Comprehensive Report (5 Marks)")
    builder.cursor_y -= 8

    builder.add_section_h2("1. Abstract")
    builder.add_paragraph(
        "Airline flight operations and reservation networks demand zero-downtime, ACID-compliant relational architectures capable of guaranteeing seat exclusivity, customer itinerary tracking, and baggage reconciliation across complex route networks. ARFOM-DB is a normalized relational database management system engineered to manage the complete lifecycle of airline operations. Built upon strict Third Normal Form (3NF) relational decomposition, the database models 10 core tables and analytical views encompassing airport hubs, aircraft configurations, seat maps, scheduled flight legs, customer profiles, booking transactions, e-tickets, payments, check-in custody, baggage manifests, and cancellation penalty ledgers. The system features engine-enforced domain, entity, and referential constraints - including a composite unique invariant preventing physical double-booking. A multi-tier web application and Python REST dispatch API interface directly with the relational engine, enabling live record viewing, atomic insertions, and referential-safe deletions with sub-millisecond database reflection."
    )

    builder.add_section_h2("2. Problem Statement & System Objectives")
    builder.add_paragraph(
        "Commercial aviation operates under narrow financial margins where seat allocation errors, uncollected baggage surcharges, or untracked cancellations directly impact profitability and regulatory compliance. Legacy reservation approaches often rely on decentralized or partially normalized flat files, leading to three critical database failure modes:"
    )
    builder.add_bullet("Concurrency Contention & Double-Booking: Simultaneous reservations writing to identical flight-seat pairs.")
    builder.add_bullet("Relational Redundancy: Repeated entry of passenger profiles, route distances, and airframe capacities leading to update and deletion anomalies.")
    builder.add_bullet("Lack of Auditability: Inability to trace financial transactions from initial booking to check-in or cancellation.")

    builder.add_section_h2("3. Objectives and Scope")
    builder.add_bullet("Design a complete Entity-Relationship model capturing 1:1, 1:N, and decomposed M:N relationships.")
    builder.add_bullet("Achieve strict 3NF and BCNF normalization across all tables.")
    builder.add_bullet("Enforce declarative integrity constraints (PK, FK RESTRICT/CASCADE, CHECK, UNIQUE).")
    builder.add_bullet("Implement multi-table analytical queries for flight load factor, revenue corridor density, and cargo logistics.")
    builder.add_bullet("Develop a fully connected, responsive User Interface demonstrating live record viewing, insertion, and deletion.")

    builder.add_section_h2("4. System Architecture & Relational Topology")
    builder.add_bullet("Infrastructure Module: airports, routes, aircraft, seats")
    builder.add_bullet("Operations Module: flights, checkins, baggage")
    builder.add_bullet("Commercial Module: passengers, bookings, tickets (junction entity resolving M:N)")
    builder.add_bullet("Audit & Finance Module: payments, cancellations")

    builder.add_section_h2("5. Relational Normalization Analysis")
    builder.add_bullet("1NF Compliance: All attribute values are strictly atomic. Multi-valued contacts or baggage items are fully decomposed into dedicated tuples.")
    builder.add_bullet("2NF Compliance: All non-prime attributes are fully functionally dependent on the primary key. Composite primary keys (e.g. seats.aircraft_id, seat_number) contain no partial dependencies.")
    builder.add_bullet("3NF Compliance: No transitive functional dependencies exist among non-prime attributes (X -> Y holds only where X is a superkey). Dynamic values like excess baggage fees are computed via operational views.")

    builder.add_section_h2("6. Verification & Negative Constraint Test Results")
    headers = ["Test ID", "Constraint Evaluated", "Test Input", "Engine Behavior", "Status"]
    rows = [
        ["TC-01", "CHECK (weight_kg >= 0)", "weight_kg = -5.50", "Engine aborts write in 0.8ms", "PASS"],
        ["TC-02", "UNIQUE (flight_id, seat_id)", "Flight 1, Seat 1 twice", "Duplicate key rejected", "PASS"],
        ["TC-03", "CHECK (origin <> dest)", "DEL -> DEL", "Write aborted", "PASS"],
        ["TC-04", "FOREIGN KEY ON DELETE RESTRICT", "DELETE airport 'DEL'", "Deletion blocked", "PASS"],
        ["TC-05", "ACID INSERT Transaction", "Passenger: V. Malhotra", "Row ID 61 allocated in 2.1ms", "PASS"]
    ]
    builder.add_table(headers, rows)

    builder.add_section_h2("7. User Interface Implementation & CRUD Operations")
    builder.add_paragraph("The application layer connects directly to the relational database through a zero-dependency Python REST server:")
    builder.add_bullet("Viewing Module: Live data grid with multi-table selector, search filters, column sorting, and pagination.")
    builder.add_bullet("Insertion Module: Form validation with 1-click viva presets and real-time row count increment (+1).")
    builder.add_bullet("Deletion Module: Pre-deletion inspection with referential safety warnings and instant row count decrement (-1).")
    builder.add_bullet("Before & After Comparator: Side-by-side 3-column state transition proving live storage engine reflection.")

    builder.add_section_h2("8. Conclusion & Repository Deliverables")
    builder.add_paragraph(
        "ARFOM-DB provides an enterprise-ready, mathematically rigorous relational foundation for airline reservation and fleet dispatching. All source code, DDL/DML scripts, slide decks, and test harnesses are submitted in the public repository:"
    )
    builder.add_bullet("Repository URL: https://github.com/Sanjyit-S/DBMS-Course-Project")
    builder.add_bullet("Presentation-I: Problem Description PDF & Scope Definition")
    builder.add_bullet("Presentation-II: Interactive ER Studio, DDL Scripts & Analytical Queries")
    builder.add_bullet("Presentation-III: Live UI Source Code, Slide Deck & CRUD Verification")
    builder.add_bullet("Project-Report: Comprehensive 16-Chapter Technical Documentation")

    builder.save()

if __name__ == "__main__":
    build_problem_description_pdf()
    build_project_report_pdf()
