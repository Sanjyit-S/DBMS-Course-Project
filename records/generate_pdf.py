#!/usr/bin/env python3
"""
DBMS Lab Record Outputs PDF Generator (Compact Edition)
Generates a clean, ready-to-print PDF containing only output tables with cut-out scissor guides
and sticky instructions. Formatted as compact micro-strips so that 3 to 5 outputs can easily
fit vertically on a single blank record book page. Includes complete Experiment 5 Venn Diagram graph.
"""

import sys, os

class PDFCanvas:
    def __init__(self):
        self.pages = []  # list of byte streams
        self.width = 595   # A4 width in pt
        self.height = 842  # A4 height in pt
        self.images = []   # list of (img_bytes, width, height)

    def new_page(self):
        self.current_stream = []
        self.pages.append(self.current_stream)

    def add_image(self, file_path, w, h):
        with open(file_path, 'rb') as f:
            data = f.read()
        self.images.append((data, w, h))
        return len(self.images)  # 1-indexed

    def escape_text(self, s):
        replacements = {
            '\u2014': '--',
            '\u2013': '-',
            '\u2018': "'",
            '\u2019': "'",
            '\u201c': '"',
            '\u201d': '"',
            '': '[CUT]',
            '': '[CUT]',
            '': '[NOTE]',
            '': '[STICK]',
            '': '->',
            '': '*',
            '≥': '>=',
            '≤': '<='
        }
        for k, v in replacements.items():
            s = s.replace(k, v)
        s = s.encode('ascii', 'replace').decode('ascii')
        return s.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

    def draw_text(self, x, y, text, font='F1', size=10, r=0, g=0, b=0):
        self.current_stream.append(f"{r:.2f} {g:.2f} {b:.2f} rg")
        self.current_stream.append(f"BT /{font} {size} Tf {x:.1f} {y:.1f} Td ({self.escape_text(text)}) Tj ET")

    def draw_rect(self, x, y, w, h, stroke_rgb=(0,0,0), fill_rgb=None, line_width=1, dashed=False):
        self.current_stream.append(f"{line_width} w")
        if dashed:
            self.current_stream.append("[3 2] 0 d")
        else:
            self.current_stream.append("[] 0 d")
        
        self.current_stream.append(f"{stroke_rgb[0]:.2f} {stroke_rgb[1]:.2f} {stroke_rgb[2]:.2f} RG")
        if fill_rgb:
            self.current_stream.append(f"{fill_rgb[0]:.2f} {fill_rgb[1]:.2f} {fill_rgb[2]:.2f} rg")
            self.current_stream.append(f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re B")
        else:
            self.current_stream.append(f"{x:.1f} {y:.1f} {w:.1f} {h:.1f} re S")
        self.current_stream.append("[] 0 d")

    def draw_cutout_strip(self, x, y_top, w, exp_label, title, query, output_lines, stick_text):
        """
        Draws a compact micro-strip (~35mm to 55mm tall) designed to fit 3-5 on a single record page.
        """
        line_height = 8.5
        terminal_height = len(output_lines) * line_height + 8
        header_height = 28
        footer_height = 18
        card_h = header_height + terminal_height + footer_height
        y_bottom = y_top - card_h

        # Outer dashed boundary
        self.draw_rect(x, y_bottom, w, card_h, stroke_rgb=(0.35, 0.45, 0.55), fill_rgb=(1, 1, 1), line_width=1.0, dashed=True)

        # Scissor label at top-left
        self.draw_rect(x + 12, y_top - 5, 120, 10, stroke_rgb=(0.85, 0.85, 0.85), fill_rgb=(1, 1, 1), line_width=0.4)
        self.draw_text(x + 16, y_top - 3, "[CUT] CUT HERE [CUT]", font="F2", size=6, r=0.4, g=0.4, b=0.4)

        # Title bar
        self.draw_text(x + 12, y_top - 15, f"{exp_label}: {title}", font="F2", size=8.5, r=0.08, g=0.2, b=0.55)
        self.draw_text(x + 12, y_top - 24, f"Query/Cmd: {query}", font="F3", size=6.8, r=0.2, g=0.2, b=0.2)

        # Terminal Box (dark background)
        term_y = y_bottom + footer_height + 3
        self.draw_rect(x + 8, term_y, w - 16, terminal_height, stroke_rgb=(0.1, 0.15, 0.25), fill_rgb=(0.04, 0.06, 0.1), line_width=0.6)

        # Terminal text lines
        cur_ty = term_y + terminal_height - 9
        for line in output_lines:
            if line.startswith("+") or line.startswith("|") or "ObjectId" in line:
                r, g, b = 0.2, 0.85, 0.6  # green
            elif "mysql>" in line or "CollegeDB>" in line or "sampleDB>" in line:
                r, g, b = 0.25, 0.75, 1.0  # cyan
            elif "row in set" in line or "acknowledged" in line or "Query OK" in line:
                r, g, b = 0.75, 0.75, 0.75 # gray
            else:
                r, g, b = 0.95, 0.95, 0.95 # white
            self.draw_text(x + 12, cur_ty, line, font="F3", size=6.6, r=r, g=g, b=b)
            cur_ty -= line_height

        # Sticky instruction banner (bottom)
        self.draw_rect(x + 8, y_bottom + 3, w - 16, 12, stroke_rgb=(0.95, 0.75, 0.2), fill_rgb=(1.0, 0.97, 0.88), line_width=0.6)
        self.draw_text(x + 12, y_bottom + 6, f"[STICK] WHERE TO STICK: {stick_text}", font="F2", size=6.5, r=0.5, g=0.25, b=0.05)

        return card_h + 8  # consumed height + small spacing

    def draw_image_strip(self, x, y_top, w, exp_label, title, query, img_w, img_h, stick_text):
        """
        Draws a cutout strip containing an embedded graphical image (e.g. Venn Diagram).
        """
        header_height = 28
        footer_height = 18
        card_h = header_height + img_h + 8 + footer_height
        y_bottom = y_top - card_h

        # Outer dashed boundary
        self.draw_rect(x, y_bottom, w, card_h, stroke_rgb=(0.2, 0.4, 0.8), fill_rgb=(1, 1, 1), line_width=1.2, dashed=True)

        # Scissor label
        self.draw_rect(x + 12, y_top - 5, 120, 10, stroke_rgb=(0.85, 0.85, 0.85), fill_rgb=(1, 1, 1), line_width=0.4)
        self.draw_text(x + 16, y_top - 3, "[CUT] CUT HERE [CUT]", font="F2", size=6, r=0.4, g=0.4, b=0.4)

        # Title bar
        self.draw_text(x + 12, y_top - 15, f"{exp_label}: {title}", font="F2", size=9, r=0.08, g=0.2, b=0.65)
        self.draw_text(x + 12, y_top - 24, f"{query}", font="F3", size=7, r=0.2, g=0.2, b=0.2)

        # Image box container
        img_x = x + (w - img_w) / 2
        img_y = y_bottom + footer_height + 4
        self.draw_rect(img_x - 2, img_y - 2, img_w + 4, img_h + 4, stroke_rgb=(0.8, 0.85, 0.9), fill_rgb=(1, 1, 1), line_width=0.5)

        # Draw Image using PDF Do operator
        self.current_stream.append("q")
        self.current_stream.append(f"{img_w:.1f} 0 0 {img_h:.1f} {img_x:.1f} {img_y:.1f} cm")
        self.current_stream.append("/Im1 Do")
        self.current_stream.append("Q")

        # Sticky instruction banner (bottom)
        self.draw_rect(x + 8, y_bottom + 3, w - 16, 12, stroke_rgb=(0.95, 0.75, 0.2), fill_rgb=(1.0, 0.97, 0.88), line_width=0.6)
        self.draw_text(x + 12, y_bottom + 6, f"[STICK] WHERE TO STICK: {stick_text}", font="F2", size=6.5, r=0.5, g=0.25, b=0.05)

        return card_h + 8

    def build_pdf(self, output_path):
        num_pages = len(self.pages)
        kids_refs = []
        page_obj_nums = []
        cur_obj = 3
        for i in range(num_pages):
            page_obj_nums.append(cur_obj)
            kids_refs.append(f"{cur_obj} 0 R")
            cur_obj += 1

        font1_num = cur_obj; cur_obj += 1
        font2_num = cur_obj; cur_obj += 1
        font3_num = cur_obj; cur_obj += 1
        font4_num = cur_obj; cur_obj += 1

        img_obj_nums = []
        for i in range(len(self.images)):
            img_obj_nums.append(cur_obj)
            cur_obj += 1

        stream_obj_nums = []
        for i in range(num_pages):
            stream_obj_nums.append(cur_obj)
            cur_obj += 1

        obj_offsets = {}
        out = bytearray()

        def add_obj(obj_num, content):
            obj_offsets[obj_num] = len(out)
            out.extend(f"{obj_num} 0 obj\n".encode('latin1'))
            if isinstance(content, str):
                out.extend(content.encode('latin1'))
            else:
                out.extend(content)
            out.extend(b"\nendobj\n")

        # PDF Header
        out.extend(b"%PDF-1.4\n")

        # 1: Catalog & 2: Pages
        add_obj(1, "<< /Type /Catalog /Pages 2 0 R >>")
        add_obj(2, f"<< /Type /Pages /Kids [{' '.join(kids_refs)}] /Count {num_pages} >>")

        # Page Objects
        for i in range(num_pages):
            p_num = page_obj_nums[i]
            s_num = stream_obj_nums[i]
            xobj_str = ""
            if len(self.images) > 0:
                xobj_str = f"/XObject << /Im1 {img_obj_nums[0]} 0 R >>"

            page_dict = f"""<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842]
/Resources << /Font <<
  /F1 {font1_num} 0 R
  /F2 {font2_num} 0 R
  /F3 {font3_num} 0 R
  /F4 {font4_num} 0 R
>> {xobj_str} >>
/Contents {s_num} 0 R >>"""
            add_obj(p_num, page_dict)

        # Fonts
        add_obj(font1_num, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        add_obj(font2_num, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
        add_obj(font3_num, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>")
        add_obj(font4_num, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier-Bold >>")

        # Images (XObjects)
        for idx, (img_bytes, w, h) in enumerate(self.images):
            img_obj = img_obj_nums[idx]
            img_hdr = f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(img_bytes)} >>\nstream\n"
            data = bytearray(img_hdr.encode('latin1')) + img_bytes + b"\nendstream"
            add_obj(img_obj, data)

        # Content Streams
        for i in range(num_pages):
            s_num = stream_obj_nums[i]
            stream_text = "\n".join(self.pages[i])
            stream_bytes = stream_text.encode('latin1')
            stream_obj = f"<< /Length {len(stream_bytes)} >>\nstream\n{stream_text}\nendstream"
            add_obj(s_num, stream_obj)

        # XRef table
        xref_offset = len(out)
        total_objs = cur_obj
        out.extend(f"xref\n0 {total_objs}\n".encode('latin1'))
        out.extend(b"0000000000 65535 f \n")
        for i in range(1, total_objs):
            off = obj_offsets[i]
            out.extend(f"{off:010d} 00000 n \n".encode('latin1'))

        # Trailer
        trailer = f"""trailer
<< /Size {total_objs}
   /Root 1 0 R
>>
startxref
{xref_offset}
%%EOF"""
        out.extend(trailer.encode('latin1'))

        with open(output_path, "wb") as f:
            f.write(out)
        print(f"Successfully generated {output_path} ({len(out)} bytes, {num_pages} pages).")


def build_compact_records_pdf():
    canvas = PDFCanvas()
    # Add Venn Diagram Image (1011x478)
    canvas.add_image("records/joins_venn_diagram.jpg", 1011, 478)

    w = 540 # width of each strip
    x = 28  # left margin

    # ==================== PAGE 1: COVER & INSTRUCTIONS ====================
    canvas.new_page()
    canvas.draw_rect(20, 20, 555, 802, stroke_rgb=(0.2, 0.4, 0.7), fill_rgb=(0.97, 0.98, 1.0), line_width=1.5)
    
    canvas.draw_text(40, 775, "WOXSEN UNIVERSITY -- SCHOOL OF TECHNOLOGY", font="F2", size=13, r=0.1, g=0.25, b=0.6)
    canvas.draw_text(40, 755, "DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING", font="F1", size=10, r=0.3, g=0.35, b=0.45)
    canvas.draw_text(40, 725, "DBMS LAB RECORD: COMPACT OUTPUT STRIPS (EXP 1 - 13)", font="F2", size=13.5, r=0.05, g=0.15, b=0.4)
    canvas.draw_text(40, 705, "Course Code: 25TU03MJM0  |  10-Mark Record Book Submission Pack", font="F1", size=9, r=0.4, g=0.4, b=0.4)

    # Instructions Box
    canvas.draw_rect(40, 555, 515, 130, stroke_rgb=(0.8, 0.6, 0.1), fill_rgb=(1.0, 0.98, 0.9), line_width=1.2)
    canvas.draw_text(55, 665, "[NOTE] HOW TO PASTE 3 TO 5 OUTPUTS ON ONE RECORD PAGE:", font="F2", size=10, r=0.6, g=0.3, b=0.0)
    canvas.draw_text(55, 645, "1. Print this PDF on single-sided A4 paper.", font="F1", size=8.5, r=0.2, g=0.2, b=0.2)
    canvas.draw_text(55, 628, "2. Cut each experiment strip along the dashed boundary line [CUT].", font="F1", size=8.5, r=0.2, g=0.2, b=0.2)
    canvas.draw_text(55, 611, "3. Strips are made micro-sized (~35mm-50mm high) so 3 to 5 strips stack neatly vertically.", font="F1", size=8.5, r=0.2, g=0.2, b=0.2)
    canvas.draw_text(55, 594, "4. Experiment 5 includes ALL Joins (Venn Graph, Single/Multi Aliases, Inner/Left/Right Joins & Union).", font="F2", size=8.5, r=0.1, g=0.25, b=0.6)
    canvas.draw_text(55, 577, "5. Paste them vertically onto the blank left page facing each experiment in your record book.", font="F1", size=8.5, r=0.1, g=0.4, b=0.1)

    # Index Table
    canvas.draw_text(40, 530, "EXPERIMENT STRIP CHECKLIST & PAGE GUIDE", font="F2", size=10.5, r=0.1, g=0.25, b=0.6)
    index_lines = [
        "+--------+--------------------------------------------------------------+---------------+",
        "| Exp No | Experiment Title                                             | Strips Count  |",
        "+--------+--------------------------------------------------------------+---------------+",
        "| EXP 01 | Hotel Booking System Attribute Matrix                        | 1 Strip       |",
        "| EXP 02 | Basic SQL CRUD Operations (Table, SELECT, UPDATE)            | 3 Strips      |",
        "| EXP 03 | More SQL Queries (DISTINCT, BETWEEN, ORDER BY, LIMIT)        | 3 Strips      |",
        "| EXP 04 | Table Constraints & Aggregates (MIN, MAX, AVG, SUM, COUNT)   | 3 Strips      |",
        "| EXP 05 | ALL Joins (Venn Graph, Aliases, Inner, Left/Right, Union)    | 5 Strips      |",
        "| EXP 06 | LIKE Wildcards (% and _), GROUP BY & HAVING                  | 3 Strips      |",
        "| EXP 07 | SQL Views (HighEarning) & Stored Procedures (CALL AddNew)    | 2 Strips      |",
        "| EXP 08 | Scenario-Based Practice (12 Tasks: LIKE, AVG, EXISTS, ALL)   | 3 Strips      |",
        "| EXP 09 | MongoDB CRUD Operations (createCollection, find, updateOne)  | 3 Strips      |",
        "| EXP 10 | MongoDB Query Operators ($gt, $or, $regex)                   | 3 Strips      |",
        "| EXP 11 | MongoDB Update Operations ($inc, $currentDate, $push)        | 2 Strips      |",
        "| EXP 12 | MongoDB Aggregations ($group sum, $match & sort pipeline)    | 2 Strips      |",
        "| EXP 13 | MongoDB Search and Indexing (Text Search, dropIndex)         | 2 Strips      |",
        "+--------+--------------------------------------------------------------+---------------+"
    ]
    cur_y = 510
    for l in index_lines:
        canvas.draw_text(40, cur_y, l, font="F3", size=7.8, r=0.15, g=0.2, b=0.25)
        cur_y -= 11.5

    canvas.draw_text(40, 50, "Woxsen University DBMS Lab Record Book Evaluation (10 Marks Internal Component)", font="F1", size=8, r=0.5, g=0.5, b=0.5)

    # ==================== PAGE 2: EXP 1, EXP 2 (3 Strips) & EXP 3 (Strip 1) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 1
    exp1_lines = [
        "+---------------+-------------------------------------------------------------------------------+",
        "| Entity Name   | Identified Attributes & Constraints                                           |",
        "+---------------+-------------------------------------------------------------------------------+",
        "| GUEST         | GuestID (PK), FirstName, LastName, Phone, Email, Address, IdProof             |",
        "| ROOM          | RoomID (PK), RoomNumber (UNIQUE), RoomType (Single/Double/Suite), Rate, Status|",
        "| RESERVATION   | ReservationID (PK), GuestID (FK), RoomID (FK), CheckInDate, CheckOutDate      |",
        "| PAYMENT       | PaymentID (PK), ReservationID (FK), PaymentDate, Amount, Method (Card/UPI)   |",
        "+---------------+-------------------------------------------------------------------------------+"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 01 [1/1]", "Hotel Booking System Attribute Matrix",
                                "Entity Identification & Normalization", exp1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Experiment 1 Aim.")
    y_pos -= h

    # Exp 2 [1/3]
    exp2_1_lines = [
        "+-----------+------+----------+--------+--------+------------+",
        "| Name      | ID   | Course   | DOB    | Gender | BloodGroup |",
        "+-----------+------+----------+--------+--------+------------+",
        "| Abhiram   | 1001 | CSE-AIML | 101003 | M      | O+ve       |",
        "| Abhimanyu | 1002 | CSE      | 010303 | M      | B+ve       |",
        "| Rudra     | 1003 | CSE-DS   | 210503 | M      | O+ve       |",
        "| Nandani   | 1004 | CSE      | 280303 | F      | B+ve       |",
        "| Ridhima   | 1005 | CSE-BIC  | 031003 | F      | O+ve       |",
        "+-----------+------+----------+--------+--------+------------+ (10 rows in set)"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 02 [1/3]", "Basic CRUD Operations -- 10 Records Inserted",
                                "SELECT * FROM Students;", exp2_1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 2 (Top - Strip 1 of 3).")
    y_pos -= h

    # Exp 2 [2/3]
    exp2_2_lines = [
        "+---------+------+---------+--------+--------+------------+",
        "| Name    | ID   | Course  | DOB    | Gender | BloodGroup |",
        "+---------+------+---------+--------+--------+------------+",
        "| Ridhima | 1005 | CSE-BIC | 031003 | F      | O+ve       |",
        "+---------+------+---------+--------+--------+------------+",
        "1 row in set (0.00 sec)"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 02 [2/3]", "Conditional Selection with WHERE Clause",
                                "SELECT * FROM Students WHERE ID = 1005;", exp2_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 2 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 2 [3/3]
    exp2_3_lines = [
        "Query OK, 1 row affected (0.01 sec)  Rows matched: 1  Changed: 1",
        "mysql> SELECT * FROM Students WHERE ID = 1005;  -- [AFTER UPDATE]",
        "+---------+------+--------+--------+--------+------------+",
        "| Name    | ID   | Course | DOB    | Gender | BloodGroup |",
        "+---------+------+--------+--------+--------+------------+",
        "| Ridhima | 1005 | CSE    | 031003 | F      | B+ve       |",
        "+---------+------+--------+--------+--------+------------+"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 02 [3/3]", "Record Update & Verification",
                                "UPDATE Students SET Course='CSE', BloodGroup='B+ve' WHERE ID=1005;", exp2_3_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 2 (Bottom - Strip 3 of 3).")
    y_pos -= h

    # Exp 3 [1/3]
    exp3_1_lines = [
        "+-------------+",
        "| Course_Name |",
        "+-------------+",
        "| CSE         |",
        "| CSE-AIML    |",
        "| CSE-DS      |",
        "| CSE-BIC     |",
        "+-------------+",
        "4 rows in set (0.00 sec) -- Duplicates eliminated"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 03 [1/3]", "DISTINCT Clause Output",
                            "SELECT DISTINCT Course_Name FROM Student;", exp3_1_lines,
                            "Paste on LEFT (BLANK) PAGE facing Exp 3 (Top - Strip 1 of 3).")

    # ==================== PAGE 3: EXP 3 (Strips 2-3) & EXP 4 (Strips 1-3) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 3 [2/3]
    exp3_2_lines = [
        "+------+---------+-------------+--------------+-------+",
        "| sID  | sName   | Course_Name | Address      | email |",
        "+------+---------+-------------+--------------+-------+",
        "| 1002 | Raj     | CSE-AIML    | Hyderabad    | NULL  |",
        "| 1003 | Ajay    | CSE-DS      | Sadashivapet | NULL  |",
        "| 1004 | Sandhya | CSE-BIC     | Kurnool      | NULL  |",
        "+------+---------+-------------+--------------+-------+",
        "3 rows in set (0.00 sec)"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 03 [2/3]", "WHERE Clause with BETWEEN Operator",
                                "SELECT * FROM Student WHERE sID BETWEEN 1002 AND 1004;", exp3_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 3 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 3 [3/3]
    exp3_3_lines = [
        "+------+----------+-------------+--------------+-------+",
        "| sID  | sName    | Course_Name | Address      | email |",
        "+------+----------+-------------+--------------+-------+",
        "| 1005 | Ruhanika | CSE-BIC     | Nandyal      | NULL  |",
        "| 1004 | Sandhya  | CSE-BIC     | Kurnool      | NULL  |",
        "| 1003 | Ajay     | CSE-DS      | Sadashivapet | NULL  |",
        "+------+----------+-------------+--------------+-------+",
        "3 rows in set (0.00 sec)"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 03 [3/3]", "ORDER BY DESC & LIMIT 3 (Select TOP)",
                                "SELECT * FROM Student ORDER BY sID DESC LIMIT 3;", exp3_3_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 3 (Bottom - Strip 3 of 3).")
    y_pos -= h

    # Exp 4 [1/3]
    exp4_1_lines = [
        "+--------+----------+---------+--------+---------+",
        "| emp_no | emp_name | job     | salary | dept_no |",
        "+--------+----------+---------+--------+---------+",
        "| 201001 | Anand    | Manager |  50000 |       1 |",
        "| 201002 | Vamsi    | Manager |  50000 |       2 |",
        "| 201003 | Sanjana  | Clerk   |  20000 |       4 |",
        "| 201004 | Nanditha | Clerk   |  20000 |       4 |",
        "| 221001 | Jaya     | Manager |  50000 |       1 |",
        "| 221005 | Sita     | Manager |  50000 |       2 |",
        "+--------+----------+---------+--------+---------+",
        "6 rows in set (0.00 sec)"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 04 [1/3]", "Table Constraints & Filter (Employee)",
                                "SELECT emp_no, emp_name, job, salary FROM Employee WHERE job IN ('Manager', 'Clerk');",
                                exp4_1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 4 (Top - Strip 1 of 3).")
    y_pos -= h

    # Exp 4 [2/3]
    exp4_2_lines = [
        "+---------+---------+----------+---------------+-----------------+",
        "| min_sal | max_sal | avg_sal  | total_payroll | total_employees |",
        "+---------+---------+----------+---------------+-----------------+",
        "|   20000 |   50000 | 36333.33 |        545000 |              15 |",
        "+---------+---------+----------+---------------+-----------------+",
        "1 row in set (0.00 sec)"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 04 [2/3]", "Aggregate Functions (MIN, MAX, AVG, SUM, COUNT)",
                                "SELECT MIN(salary), MAX(salary), AVG(salary), SUM(salary), COUNT(*) FROM Employee;",
                                exp4_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 4 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 4 [3/3]
    exp4_3_lines = [
        "+----------+--------+",
        "| emp_name | salary |",
        "+----------+--------+",
        "| Anand    |  50000 |",
        "+----------+--------+",
        "1 row in set (0.00 sec) (Top earner matching MAX constraint)"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 04 [3/3]", "Top Salary & String Concatenation",
                            "SELECT emp_name, salary FROM Employee ORDER BY salary DESC LIMIT 1;",
                            exp4_3_lines,
                            "Paste on LEFT (BLANK) PAGE facing Exp 4 (Bottom - Strip 3 of 3).")

    # ==================== PAGE 4: EXP 5 (COMPLETE: 5 STRIPS FIT ON ONE BLANK PAGE!) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 5 [1/5]: VENN DIAGRAM GRAPH
    h = canvas.draw_image_strip(x, y_pos, w, "EXP 05 [GRAPH 1/5]", "SQL JOINS GRAPHICAL VENN DIAGRAM",
                               "INNER JOIN | LEFT JOIN | RIGHT JOIN | FULL OUTER JOIN",
                               310, 146,
                               "Paste at TOP of LEFT (BLANK) PAGE facing Exp 5 (Strip 1 of 5).")
    y_pos -= h

    # Exp 5 [2/5]: ALIASES
    exp5_2_lines = [
        "mysql> SELECT Name AS Student_Name FROM Students LIMIT 3;",
        "+--------------+",
        "| Student_Name |",
        "+--------------+",
        "| Abhiram      |",
        "| Abhimanyu    |",
        "| Rudra        |",
        "+--------------+",
        "mysql> SELECT ID AS Student_ID, BloodGroup AS [Blood Group] FROM Students LIMIT 2;",
        "+------------+-------------+",
        "| Student_ID | Blood Group |",
        "+------------+-------------+",
        "|       1001 | O+ve        |",
        "|       1002 | B+ve        |",
        "+------------+-------------+"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 05 [2/5]", "SQL Aliases ('AS' Keyword & Bracketed Space)",
                                "SELECT Name AS Student_Name...; SELECT ID AS Student_ID, BloodGroup AS [Blood Group]...",
                                exp5_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 5 (Strip 2 of 5 - Aliases).")
    y_pos -= h

    # Exp 5 [3/5]: INNER JOIN
    exp5_3_lines = [
        "+---------+--------------------+------------+",
        "| OrderID | CustomerName       | OrderDate  |",
        "+---------+--------------------+------------+",
        "|   10308 | Ana Trujillo       | 2023-09-18 |",
        "|   10309 | Antonio Moreno     | 2023-09-19 |",
        "|   10310 | Around the Horn    | 2023-09-20 |",
        "|   10311 | Berglunds snabbkop | 2023-09-21 |",
        "+---------+--------------------+------------+",
        "4 rows in set (0.00 sec) -- Only matching records from both tables"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 05 [3/5]", "INNER JOIN (Orders & Customers)",
                                "SELECT Orders.OrderID, Customers.CustomerName FROM Orders INNER JOIN Customers...",
                                exp5_3_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 5 (Strip 3 of 5 - Inner Join).")
    y_pos -= h

    # Exp 5 [4/5]: LEFT & RIGHT JOIN
    exp5_4_lines = [
        "+--------------------+---------+",
        "| CustomerName       | OrderID |",
        "+--------------------+---------+",
        "| Alfreds Futterkiste|    NULL |  <-- Customer with 0 orders",
        "| Ana Trujillo       |   10308 |",
        "| Antonio Moreno     |   10309 |",
        "| Around the Horn    |   10310 |",
        "+--------------------+---------+",
        "4 rows in set (0.00 sec) -- Preserves unmatched rows with NULL"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 05 [4/5]", "LEFT & RIGHT OUTER JOIN (Preserving NULLs)",
                                "SELECT Customers.CustomerName, Orders.OrderID FROM Customers LEFT JOIN Orders...",
                                exp5_4_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 5 (Strip 4 of 5 - Outer Joins).")
    y_pos -= h

    # Exp 5 [5/5]: UNION vs UNION ALL
    exp5_5_lines = [
        "mysql> -- [UNION: Distinct 4 rows]   mysql> -- [UNION ALL: 15 rows with duplicates]",
        "+----------+                         +----------+",
        "| Course   |                         | Course   | (CSE-AIML, CSE, CSE-DS, CSE,",
        "+----------+                         +----------+  CSE-BIC, CSE-DS, CSE-BIC...)",
        "| CSE-AIML |                         15 rows in set (0.00 sec)",
        "| CSE      |",
        "| CSE-DS   |",
        "| CSE-BIC  |",
        "+----------+ (4 rows in set)"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 05 [5/5]", "UNION vs UNION ALL (Distinct vs All Rows)",
                            "SELECT Course FROM Students UNION [ALL] SELECT Course_Name FROM Student;",
                            exp5_5_lines,
                            "Paste at BOTTOM of LEFT (BLANK) PAGE facing Exp 5 (Strip 5 of 5).")

    # ==================== PAGE 5: EXP 6 (3 Strips) & EXP 7 (2 Strips) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 6 [1/3]
    exp6_1_lines = [
        "+-----------+----------+",
        "| Name      | Course   |",
        "+-----------+----------+",
        "| Abhiram   | CSE-AIML | (Matches 'Ab%' and '%AIML%')",
        "| Abhimanyu | CSE      | (Matches 'Ab%')",
        "| Veer      | CSE-AIML | (Matches '%AIML%')",
        "+-----------+----------+",
        "Pattern search with % (any chars) and _ (single char) verified"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 06 [1/3]", "LIKE Pattern Search (% and _ Wildcards)",
                                "SELECT Name, Course FROM Students WHERE Course LIKE '%AIML%';",
                                exp6_1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 6 (Top - Strip 1 of 3).")
    y_pos -= h

    # Exp 6 [2/3]
    exp6_2_lines = [
        "+-----------+-----------+",
        "| job       | count_emp |",
        "+-----------+-----------+",
        "| Manager   |         4 |",
        "| Assistant |         3 |",
        "| Engineer  |         3 |",
        "| Clerk     |         2 |",
        "| Analyst   |         2 |",
        "+-----------+-----------+"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 06 [2/3]", "GROUP BY Job & Headcount",
                                "SELECT job, COUNT(emp_no) AS count_emp FROM Employee GROUP BY job;",
                                exp6_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 6 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 6 [3/3]
    exp6_3_lines = [
        "+-----------+-------+------------+",
        "| job       | total | avg_salary |",
        "+-----------+-------+------------+",
        "| Manager   |     4 |   50000.00 |",
        "| Assistant |     3 |   25000.00 |",
        "| Engineer  |     3 |   40000.00 |",
        "| Clerk     |     2 |   20000.00 |",
        "| Analyst   |     2 |   35000.00 |",
        "+-----------+-------+------------+",
        "5 rows in set (0.00 sec) -- Filtered out job roles where count < 2"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 06 [3/3]", "HAVING Group Filter & ORDER BY",
                                "SELECT job, COUNT(emp_no) AS total, AVG(salary) GROUP BY job HAVING total >= 2;",
                                exp6_3_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 6 (Bottom - Strip 3 of 3).")
    y_pos -= h

    # Exp 7 [1/2]
    exp7_1_lines = [
        "+------------+---------------+--------+----------------+    +----------------+--------------+",
        "| EmployeeID | Name          | Salary | DepartmentName |    | DepartmentName | TotalExpense |",
        "+------------+---------------+--------+----------------+    +----------------+--------------+",
        "|          4 | Michael Brown |   7000 | IT             |    | Sales          |        15700 |",
        "|          5 | Sarah Johnson |   7500 | Marketing      |    | Marketing      |        13500 |",
        "+------------+---------------+--------+----------------+    | IT             |         7000 |",
        "                                                            +----------------+--------------+"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 07 [1/2]", "Database VIEWs Execution",
                                "SELECT * FROM HighEarningEmployees; SELECT * FROM DepartmentSalaryExpenses;",
                                exp7_1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 7 (Top - Strip 1 of 2 - Views).")
    y_pos -= h

    # Exp 7 [2/2]
    exp7_2_lines = [
        "Query OK, 1 row affected (0.01 sec)",
        "mysql> SELECT EmployeeID, Name, DepartmentID, Salary FROM Employees WHERE Name = 'Anna Taylor';",
        "+------------+-------------+--------------+--------+",
        "| EmployeeID | Name        | DepartmentID | Salary |",
        "+------------+-------------+--------------+--------+",
        "|          7 | Anna Taylor |          103 |   6800 |",
        "+------------+-------------+--------------+--------+",
        "1 row in set (0.00 sec) -- Stored procedure executed successfully"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 07 [2/2]", "Stored Procedure Execution (CALL AddNewEmployee)",
                            "CALL AddNewEmployee('Anna Taylor', 103, 6800);",
                            exp7_2_lines,
                            "Paste on LEFT (BLANK) PAGE facing Exp 7 (Bottom - Strip 2 of 2 - Procedures).")

    # ==================== PAGE 6: EXP 8 (3 Strips) & EXP 9 (3 Strips) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 8 [1/3]
    exp8_1_lines = [
        "+-------+     +------------+---------------+-----------+",
        "| Name  |     | Department | EmployeeCount | AvgSalary |",
        "+-------+     +------------+---------------+-----------+",
        "| Alice |     | IT         |             3 |  67333.33 |",
        "| Eve   |     | HR         |             2 |  51500.00 |",
        "| Grace |     | Marketing  |             2 |  72500.00 |",
        "+-------+     +------------+---------------+-----------+"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 08 [1/3]", "Name Filter ('%e') & Department Statistics",
                                "SELECT Name WHERE Name LIKE '%e'; SELECT Department, COUNT(*), AVG(Salary)...",
                                exp8_1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 8 (Top - Strip 1 of 3).")
    y_pos -= h

    # Exp 8 [2/3]
    exp8_2_lines = [
        "+-------+",
        "| Name  |",
        "+-------+",
        "| Frank |",
        "| Grace |",
        "+-------+",
        "2 rows in set (0.00 sec) -- Employees on projects with budget > $50,000"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 08 [2/3]", "Correlated Subquery with EXISTS",
                                "SELECT Name FROM Employees e WHERE EXISTS (SELECT 1 FROM Projects p WHERE p.Budget > 50000);",
                                exp8_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 8 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 8 [3/3]
    exp8_3_lines = [
        "+-------+-------+-------+-------+-------+",
        "| Alice | Bob   | Eve   | Frank | Grace |",
        "+-------+-------+-------+-------+-------+",
        "5 rows in set (0.00 sec) -- All employees with Salary > $55,000"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 08 [3/3]", "Set Comparison Subquery (Salary > ALL in HR)",
                                "SELECT Name FROM Employees WHERE Salary > ALL (SELECT Salary FROM Employees WHERE Department='HR');",
                                exp8_3_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 8 (Bottom - Strip 3 of 3).")
    y_pos -= h

    # Exp 9 [1/3]
    exp9_1_lines = [
        "CollegeDB> db.createCollection('Lab9')",
        "{ ok: 1 }",
        "CollegeDB> db.Lab9.insertMany([ { id: 1001, name: 'Abhiram', course: 'CSE-AIML', marks: 88 }, ... ])",
        "{ acknowledged: true, insertedIds: [ ObjectId('672c4101a88246916737a101'), ... ] }"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 09 [1/3]", "MongoDB Collection Creation & insertMany",
                                "db.createCollection('Lab9'); db.Lab9.insertMany([...]);", exp9_1_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 9 (Top - Strip 1 of 3).")
    y_pos -= h

    # Exp 9 [2/3]
    exp9_2_lines = [
        "[ { _id: ObjectId('...'), id: 1005, name: 'Ridhima', course: 'CSE-BIC', marks: 92 } ]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 09 [2/3]", "MongoDB find() Document Retrieval",
                                "db.Lab9.find({ id: 1005 });", exp9_2_lines,
                                "Paste on LEFT (BLANK) PAGE facing Exp 9 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 9 [3/3]
    exp9_3_lines = [
        "{ acknowledged: true, matchedCount: 1, modifiedCount: 1 }",
        "Document with id: 1005 updated with marks: 96"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 09 [3/3]", "MongoDB updateOne & deleteOne Operations",
                            "db.Lab9.updateOne({ id: 1005 }, { $set: { marks: 96 } });", exp9_3_lines,
                            "Paste on LEFT (BLANK) PAGE facing Exp 9 (Bottom - Strip 3 of 3).")

    # ==================== PAGE 7: EXP 10 (3 Strips), EXP 11 (2 Strips) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 10 [1/3]
    exp10_1_lines = [
        "[",
        "  { id: 1001, name: 'Abhiram', marks: 88 },",
        "  { id: 1003, name: 'Rudra', marks: 91 },",
        "  { id: 1005, name: 'Ridhima', marks: 96 },",
        "  { id: 1008, name: 'Kshithija', marks: 89 }",
        "]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 10 [1/3]", "Comparison Operators ($gt & $gte)",
                                 "db.Lab9.find({ marks: { $gt: 85 } }, { _id: 0, id: 1, name: 1, marks: 1 });",
                                 exp10_1_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 10 (Top - Strip 1 of 3).")
    y_pos -= h

    # Exp 10 [2/3]
    exp10_2_lines = [
        "[",
        "  { id: 1001, name: 'Abhiram', course: 'CSE-AIML' },",
        "  { id: 1005, name: 'Ridhima', course: 'CSE-BIC' },",
        "  { id: 1009, name: 'Veer', course: 'CSE-AIML' }",
        "]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 10 [2/3]", "Logical Disjunction ($or Operator)",
                                 "db.Lab9.find({ $or: [{ course: 'CSE-AIML' }, { marks: { $gte: 95 } }] });",
                                 exp10_2_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 10 (Middle - Strip 2 of 3).")
    y_pos -= h

    # Exp 10 [3/3]
    exp10_3_lines = [
        "[ { id: 1001, name: 'Abhiram' }, { id: 1002, name: 'Abhimanyu' } ]",
        "2 documents matched regex condition /^A/i"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 10 [3/3]", "Regex Pattern Search ($regex: /^A/i)",
                                 "db.Lab9.find({ name: { $regex: /^A/i } });",
                                 exp10_3_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 10 (Bottom - Strip 3 of 3).")
    y_pos -= h

    # Exp 11 [1/2]
    exp11_1_lines = [
        "{ acknowledged: true, matchedCount: 1, modifiedCount: 1 }",
        "sampleDB> db.sampledata.find({ name: 'Emily Davis' })",
        "[ { name: 'Emily Davis', age: 30, salary: 75000, lastUpdated: ISODate('2026-10-02T08:00:00Z') } ]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 11 [1/2]", "Field Update Modifiers ($inc, $currentDate)",
                                 "db.sampledata.updateOne({ name: 'Emily Davis' }, { $inc: { age: 1, salary: 5000 }, $currentDate... });",
                                 exp11_1_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 11 (Top - Strip 1 of 2).")
    y_pos -= h

    # Exp 11 [2/2]
    exp11_2_lines = [
        "{ acknowledged: true, matchedCount: 1, modifiedCount: 1 }",
        "Resulting Skills Array: [ 'Python', 'SQL', 'MongoDB' ]"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 11 [2/2]", "Array Modifiers ($push & $pull)",
                            "db.sampledata.updateOne({ name: 'Emily Davis' }, { $push: { skills: 'MongoDB' } });",
                            exp11_2_lines,
                            "Paste on LEFT (BLANK) PAGE facing Exp 11 (Bottom - Strip 2 of 2).")

    # ==================== PAGE 8: EXP 12 (2 Strips) & EXP 13 (2 Strips) ====================
    canvas.new_page()
    y_pos = 818

    # Exp 12 [1/2]
    exp12_1_lines = [
        "[",
        "  { _id: 'apple',  totalQty: 80,  totalRevenue: 96.0 },",
        "  { _id: 'banana', totalQty: 150, totalRevenue: 120.0 },",
        "  { _id: 'orange', totalQty: 75,  totalRevenue: 112.5 }",
        "]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 12 [1/2]", "Aggregation Pipeline ($group & $sum)",
                                 "db.sales.aggregate([{ $group: { _id: '$item', totalQty: { $sum: '$quantity' }, totalRevenue... } }]);",
                                 exp12_1_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 12 (Top - Strip 1 of 2).")
    y_pos -= h

    # Exp 12 [2/2]
    exp12_2_lines = [
        "[",
        "  { item: 'banana', price: 0.8, quantity: 100, status: 'A' },",
        "  { item: 'apple',  price: 1.2, quantity: 50,  status: 'A' }",
        "]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 12 [2/2]", "Filtered Pipeline ($match, $sort, $limit)",
                                 "db.sales.aggregate([{ $match: { status: 'A' } }, { $sort: { quantity: -1 } }, { $limit: 2 }]);",
                                 exp12_2_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 12 (Bottom - Strip 2 of 2).")
    y_pos -= h

    # Exp 13 [1/2]
    exp13_1_lines = [
        "companyDB> db.articles.createIndex({ content: 'text' })",
        "{ createdCollectionAutomatically: false, numIndexesBefore: 1, numIndexesAfter: 2, ok: 1 }",
        "companyDB> db.articles.find({ $text: { $search: 'database' } })",
        "[",
        "  { content: 'MongoDB is a NoSQL database.' },",
        "  { content: 'Databases like MongoDB are popular for modern web applications.' }",
        "]"
    ]
    h = canvas.draw_cutout_strip(x, y_pos, w, "EXP 13 [1/2]", "Full-Text Indexing & $text Search",
                                 "db.articles.createIndex({ content: 'text' }); db.articles.find({ $text: { $search: 'database' } });",
                                 exp13_1_lines,
                                 "Paste on LEFT (BLANK) PAGE facing Exp 13 (Top - Strip 1 of 2).")
    y_pos -= h

    # Exp 13 [2/2]
    exp13_2_lines = [
        "companyDB> db.employees.createIndex({ last_name: 1, date_of_birth: 1 })",
        "{ numIndexesBefore: 2, numIndexesAfter: 3, ok: 1 }",
        "companyDB> db.employees.dropIndex('first_name_1')",
        "{ nIndexesWas: 3, ok: 1 }"
    ]
    canvas.draw_cutout_strip(x, y_pos, w, "EXP 13 [2/2]", "Compound Index Creation & dropIndex",
                            "db.employees.createIndex({ last_name: 1, date_of_birth: 1 }); db.employees.dropIndex('first_name_1');",
                            exp13_2_lines,
                            "Paste on LEFT (BLANK) PAGE facing Exp 13 (Bottom - Strip 2 of 2).")

    # Output file
    output_pdf = "records/DBMS_LAB_RECORD_OUTPUTS.pdf"
    canvas.build_pdf(output_pdf)

if __name__ == "__main__":
    build_compact_records_pdf()
