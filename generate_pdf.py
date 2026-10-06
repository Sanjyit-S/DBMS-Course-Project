#!/usr/bin/env python3
"""
===============================================================================
PROFESSIONAL PDF GENERATOR FOR ARFOM-DB VIVA DEFENSE PLAYBOOK (REV 2)
Generates an executive, publication-grade A4 PDF from scratch in pure Python.
Zero external dependencies. Fully compliant with PDF 1.4 specification.
===============================================================================
"""

import sys
import os
import re

# Precise Character Widths (Adobe Helvetica & Helvetica-Bold at 1000 units)
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

def sanitize_text(text):
    """Replaces Unicode symbols with crystal-clear ASCII equivalents."""
    replacements = [
        ('₹', 'Rs. '),
        ('•', ' | '),
        ('—', ' - '),
        ('–', ' - '),
        ('’', "'"),
        ('‘', "'"),
        ('“', '"'),
        ('”', '"'),
        ('≥', '>='),
        ('≤', '<='),
        ('→', ' -> '),
        ('∩', ' INTERSECT '),
        ('∪', ' UNION '),
        ('≡', ' == '),
        ('\xa0', ' '),
        ('…', '...'),
        ('`', "'"),
        ('$', ''),
    ]
    for orig, rep in replacements:
        text = text.replace(orig, rep)
    
    # Strip any remaining non-ASCII characters cleanly
    cleaned = []
    for c in text:
        if ord(c) < 128:
            cleaned.append(c)
        else:
            cleaned.append(' ')
    return "".join(cleaned)

def calc_text_width(text, font_type, font_size):
    widths = HELVETICA_BOLD_WIDTHS if font_type == "F2" else HELVETICA_WIDTHS
    def_w = 600 if font_type == "F2" else 550
    w = sum(widths.get(c, def_w) for c in text)
    return (w * font_size) / 1000.0

def escape_pdf(text):
    return text.replace('\\', '\\\\').replace('(', '\\(').replace(')', '\\)')

def wrap_text_box(text, font_type, font_size, max_width):
    """
    Wraps text accurately to fit within max_width.
    Uses safety factor to guarantee text never touches the right edge.
    """
    text = sanitize_text(text)
    # Normalize multiple whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    words = text.split(' ')
    lines = []
    curr_words = []
    curr_width = 0.0
    effective_max = max_width * 0.96  # 4% safety margin

    for word in words:
        if not word:
            continue
        word_w = calc_text_width(word + ' ', font_type, font_size)
        if curr_width + word_w <= effective_max:
            curr_words.append(word)
            curr_width += word_w
        else:
            if curr_words:
                lines.append(' '.join(curr_words))
            curr_words = [word]
            curr_width = calc_text_width(word + ' ', font_type, font_size)
    if curr_words:
        lines.append(' '.join(curr_words))
    return lines

class PDFDoc:
    def __init__(self, filename="docs/VIVA_DEFENSE_PLAYBOOK.pdf"):
        self.filename = filename
        self.pages = []
        self.curr_ops = []
        self.page_w = 595.28  # A4
        self.page_h = 841.89  # A4
        self.margin_x = 36.0
        self.margin_top = 40.0
        self.margin_bottom = 44.0
        self.content_w = self.page_w - (self.margin_x * 2)  # 523.28 pt
        self.cursor_y = self.page_h - self.margin_top
        self.new_page()

    def new_page(self):
        if self.curr_ops:
            self.pages.append(self.curr_ops)
        self.curr_ops = []
        self.cursor_y = self.page_h - self.margin_top

        # Top running header for page 2 onwards
        if len(self.pages) >= 1:
            self.draw_rect(self.margin_x, self.page_h - 26, self.content_w, 0.5, stroke_rgb=(0.82, 0.86, 0.92))
            self.draw_text(
                "ARFOM-DB | AIRLINE RESERVATION & OPERATIONS SYSTEM | VIVA DEFENSE DOSSIER",
                self.margin_x, self.page_h - 22, font="F2", size=7.5, rgb=(0.40, 0.45, 0.55)
            )

    def check_space(self, height_needed):
        """If remaining vertical room is less than height_needed, triggers a page break."""
        if self.cursor_y - height_needed < self.margin_bottom:
            self.new_page()

    def draw_rect(self, x, y, w, h, fill_rgb=None, stroke_rgb=None, stroke_w=1.0):
        ops = []
        if fill_rgb:
            r, g, b = fill_rgb
            ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg")
        if stroke_rgb:
            r, g, b = stroke_rgb
            ops.append(f"{r:.3f} {g:.3f} {b:.3f} RG {stroke_w:.2f} w")
        mode = "B" if (fill_rgb and stroke_rgb) else ("f" if fill_rgb else "S")
        ops.append(f"{x:.2f} {y:.2f} {w:.2f} {h:.2f} re {mode}")
        self.curr_ops.append(" ".join(ops))

    def draw_text(self, text, x, y, font="F1", size=10, rgb=(0.1, 0.1, 0.1)):
        r, g, b = rgb
        clean = sanitize_text(text)
        esc = escape_pdf(clean)
        self.curr_ops.append(f"{r:.3f} {g:.3f} {b:.3f} rg BT /{font} {size:.2f} Tf {x:.2f} {y:.2f} Td ({esc}) Tj ET")

    def add_main_header(self, title, subtitle, meta_text):
        h = 62.0
        # Dark Midnight Executive Banner
        self.draw_rect(self.margin_x, self.cursor_y - h, self.content_w, h,
                       fill_rgb=(0.06, 0.09, 0.16), stroke_rgb=(0.20, 0.28, 0.45), stroke_w=1.0)
        
        # Red Alert Pill
        pill_w = 195.0
        self.draw_rect(self.margin_x + 12, self.cursor_y - 18, pill_w, 13, fill_rgb=(0.88, 0.15, 0.25))
        self.draw_text("HOSTILE VIVA DEFENSE DOSSIER | REVIEW 2", self.margin_x + 16, self.cursor_y - 15,
                       font="F2", size=7.5, rgb=(1, 1, 1))

        # Title & Subtitle
        self.draw_text(title, self.margin_x + 12, self.cursor_y - 34, font="F2", size=13.0, rgb=(1, 1, 1))
        self.draw_text(subtitle, self.margin_x + 12, self.cursor_y - 46, font="F1", size=8.0, rgb=(0.75, 0.82, 0.95))
        self.draw_text(meta_text, self.margin_x + 12, self.cursor_y - 56, font="F2", size=7.0, rgb=(0.55, 0.65, 0.80))

        self.cursor_y -= (h + 14.0)

    def add_section_title(self, title):
        self.check_space(32.0)
        h = 22.0
        # Indigo indicator bar + soft background
        self.draw_rect(self.margin_x, self.cursor_y - h, 4.0, h, fill_rgb=(0.25, 0.35, 0.85))
        self.draw_rect(self.margin_x + 6, self.cursor_y - h, self.content_w - 6, h,
                       fill_rgb=(0.94, 0.96, 0.99), stroke_rgb=(0.86, 0.90, 0.96), stroke_w=0.5)
        self.draw_text(title.upper(), self.margin_x + 14, self.cursor_y - 15,
                       font="F2", size=9.5, rgb=(0.10, 0.16, 0.35))
        self.cursor_y -= (h + 10.0)

    def add_table_cheat_sheet(self):
        headers = ["#", "Mandatory Business Rule", "Relational Mechanism", "File & Line", "10-Second Viva Speech"]
        col_w = [22.0, 112.0, 116.0, 78.0, 195.28]  # Sum = 523.28 = content_w
        
        rules = [
            ("1", "One seat per passenger", "UNIQUE(flight_id, seat_id)", "tickets table",
             "Storage-engine B-Tree uniqueness barrier. Rejects any duplicate seat allocation on the same flight leg."),
            ("2", "Aircraft-capacity limit", "trg_verify_aircraft_capacity", "BEFORE INSERT",
             "Trigger counts uncancelled tickets vs total_capacity. Throws Capacity Overrun exception on overrun."),
            ("3", "Non-negative baggage", "CHECK(weight_kg >= 0.00)", "baggage table",
             "Declarative domain check constraint. Rejects negative scale weight or fees at SQL parse level."),
            ("4", "Check-in eligibility", "trg_verify_checkin_eligibility", "BEFORE INSERT",
             "Verifies parent booking is CONFIRMED and ticket is ISSUED. Automatically sets ticket to CHECKED_IN."),
            ("5", "Strict refund bounds", "trg_enforce_refund_bounds", "BEFORE INSERT",
             "Enforces refund <= fare_amount. Blocks excessive refunds as accounting anomaly and sets ticket to CANCELLED.")
        ]

        # Calculate row heights dynamically
        row_heights = []
        prepared_rows = []
        for r_data in rules:
            rule_lines = wrap_text_box(r_data[1], "F2", 8.0, col_w[1] - 8)
            mech_lines = wrap_text_box(r_data[2], "F1", 7.5, col_w[2] - 8)
            loc_lines = wrap_text_box(r_data[3], "F1", 7.5, col_w[3] - 8)
            speech_lines = wrap_text_box(r_data[4], "F1", 7.5, col_w[4] - 8)
            max_lines = max(len(rule_lines), len(mech_lines), len(loc_lines), len(speech_lines))
            h = max(28.0, max_lines * 9.5 + 8.0)
            row_heights.append(h)
            prepared_rows.append((r_data[0], rule_lines, mech_lines, loc_lines, speech_lines, h))

        total_h = 20.0 + sum(row_heights)
        self.check_space(total_h)

        # Header Row
        header_y = self.cursor_y - 18.0
        self.draw_rect(self.margin_x, header_y, self.content_w, 18.0, fill_rgb=(0.10, 0.15, 0.28))
        x = self.margin_x
        for idx, h_text in enumerate(headers):
            self.draw_text(h_text, x + 4.0, header_y + 5.0, font="F2", size=8.0, rgb=(1, 1, 1))
            x += col_w[idx]
        self.cursor_y -= 18.0

        # Data Rows
        for idx, (num, r_lines, m_lines, l_lines, s_lines, r_h) in enumerate(prepared_rows):
            y = self.cursor_y - r_h
            bg = (0.97, 0.98, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0)
            self.draw_rect(self.margin_x, y, self.content_w, r_h, fill_rgb=bg, stroke_rgb=(0.85, 0.88, 0.93), stroke_w=0.5)

            # Col 0: Number
            self.draw_text(num, self.margin_x + 6.0, y + r_h - 13.0, font="F2", size=8.5, rgb=(0.20, 0.35, 0.75))
            
            # Col 1: Rule
            cy = y + r_h - 12.0
            for l in r_lines:
                self.draw_text(l, self.margin_x + col_w[0] + 4.0, cy, font="F2", size=7.5, rgb=(0.10, 0.15, 0.25))
                cy -= 9.0

            # Col 2: Mechanism
            cy = y + r_h - 12.0
            for l in m_lines:
                self.draw_text(l, self.margin_x + col_w[0] + col_w[1] + 4.0, cy, font="F1", size=7.5, rgb=(0.15, 0.35, 0.65))
                cy -= 9.0

            # Col 3: Location
            cy = y + r_h - 12.0
            for l in l_lines:
                self.draw_text(l, self.margin_x + col_w[0] + col_w[1] + col_w[2] + 4.0, cy, font="F1", size=7.5, rgb=(0.40, 0.45, 0.50))
                cy -= 9.0

            # Col 4: Speech
            cy = y + r_h - 12.0
            for l in s_lines:
                self.draw_text(l, self.margin_x + col_w[0] + col_w[1] + col_w[2] + col_w[3] + 4.0, cy, font="F1", size=7.5, rgb=(0.08, 0.12, 0.20))
                cy -= 9.0

            self.cursor_y -= r_h
        self.cursor_y -= 12.0

    def add_crash_course_card(self, title, def_text, example_text):
        """Adds a cleanly formatted crash course concept card with wrapped lines."""
        t_lines = wrap_text_box(title, "F2", 9.0, self.content_w - 20)
        d_lines = wrap_text_box(def_text, "F1", 8.0, self.content_w - 20)
        e_lines = wrap_text_box("Example: " + example_text, "F1", 7.5, self.content_w - 20)

        h_title = len(t_lines) * 11.0
        h_def = len(d_lines) * 10.0
        h_ex = len(e_lines) * 9.5
        box_h = h_title + h_def + h_ex + 14.0

        self.check_space(box_h + 8.0)

        box_y = self.cursor_y - box_h
        self.draw_rect(self.margin_x, box_y, self.content_w, box_h,
                       fill_rgb=(0.98, 0.99, 1.0), stroke_rgb=(0.82, 0.86, 0.92), stroke_w=0.6)
        
        # Blue accent line on left
        self.draw_rect(self.margin_x, box_y, 3.0, box_h, fill_rgb=(0.30, 0.45, 0.85))

        cy = self.cursor_y - 11.0
        for l in t_lines:
            self.draw_text(l, self.margin_x + 10.0, cy, font="F2", size=9.0, rgb=(0.12, 0.22, 0.45))
            cy -= 11.0

        cy -= 2.0
        for l in d_lines:
            self.draw_text(l, self.margin_x + 10.0, cy, font="F1", size=8.0, rgb=(0.15, 0.18, 0.22))
            cy -= 10.0

        cy -= 2.0
        for l in e_lines:
            self.draw_text(l, self.margin_x + 10.0, cy, font="F1", size=7.5, rgb=(0.35, 0.40, 0.50))
            cy -= 9.5

        self.cursor_y = box_y - 6.0

    def add_qa_card(self, q_num, question, testing_intent, recital, concept, trap=None):
        """
        Creates an executive, high-contrast, fully encapsulated Q&A Defense Card.
        Calculates exact vertical space so text NEVER clips or runs off margins.
        """
        usable_w = self.content_w - 24.0  # inner box width margin

        # Wrap all text blocks
        q_lines = wrap_text_box(f"Q{q_num}: {question}", "F2", 9.5, self.content_w - 20)
        intent_lines = wrap_text_box(f"Evaluator Intent: {testing_intent}", "F1", 7.5, usable_w) if testing_intent else []
        recital_lines = wrap_text_box(recital, "F1", 8.0, usable_w - 12.0)
        concept_lines = wrap_text_box(concept, "F1", 8.0, usable_w - 12.0)
        trap_lines = wrap_text_box(f"HOSTILE TRAP WARNING: {trap}", "F2", 7.5, usable_w - 12.0) if trap else []

        # Heights
        h_q = len(q_lines) * 12.5 + 8.0
        h_intent = (len(intent_lines) * 9.5 + 4.0) if intent_lines else 0.0
        h_rec = len(recital_lines) * 10.5 + 18.0
        h_con = len(concept_lines) * 10.0 + 16.0
        h_trp = (len(trap_lines) * 9.5 + 12.0) if trap else 0.0

        total_h = h_q + h_intent + h_rec + h_con + h_trp + 14.0

        # Page boundary check - never break a card across pages!
        self.check_space(total_h + 6.0)

        card_top = self.cursor_y
        card_bottom = card_top - total_h

        # Outer Card Border & White Background
        self.draw_rect(self.margin_x, card_bottom, self.content_w, total_h,
                       fill_rgb=(1.0, 1.0, 1.0), stroke_rgb=(0.80, 0.84, 0.90), stroke_w=0.8)

        # 1. Question Header Banner (Deep Navy)
        self.draw_rect(self.margin_x, card_top - h_q, self.content_w, h_q, fill_rgb=(0.11, 0.16, 0.28))
        qy = card_top - 11.0
        for ql in q_lines:
            self.draw_text(ql, self.margin_x + 10.0, qy, font="F2", size=9.5, rgb=(1.0, 1.0, 1.0))
            qy -= 12.5

        curr_y = card_top - h_q - 5.0

        # 2. Evaluator Intent (if provided)
        if intent_lines:
            iy = curr_y - 2.0
            for il in intent_lines:
                self.draw_text(il, self.margin_x + 12.0, iy, font="F1", size=7.5, rgb=(0.45, 0.50, 0.60))
                iy -= 9.5
            curr_y -= h_intent

        # 3. Recital Box (Soft Ice-Blue with Bold Royal Blue Indicator Bar)
        rec_box_h = h_rec - 4.0
        self.draw_rect(self.margin_x + 8.0, curr_y - rec_box_h, self.content_w - 16.0, rec_box_h,
                       fill_rgb=(0.94, 0.96, 1.0), stroke_rgb=(0.80, 0.86, 0.96), stroke_w=0.5)
        # Left accent bar
        self.draw_rect(self.margin_x + 8.0, curr_y - rec_box_h, 3.5, rec_box_h, fill_rgb=(0.25, 0.35, 0.85))
        
        self.draw_text("RECITE OUT LOUD (15 SECONDS):", self.margin_x + 16.0, curr_y - 9.0,
                       font="F2", size=7.5, rgb=(0.18, 0.25, 0.65))
        ry = curr_y - 20.0
        for rl in recital_lines:
            self.draw_text(rl, self.margin_x + 16.0, ry, font="F1", size=8.0, rgb=(0.08, 0.12, 0.22))
            ry -= 10.5

        curr_y -= (rec_box_h + 5.0)

        # 4. Plain-English Concept Box (Warm Slate Grey)
        con_box_h = h_con - 4.0
        self.draw_rect(self.margin_x + 8.0, curr_y - con_box_h, self.content_w - 16.0, con_box_h,
                       fill_rgb=(0.97, 0.98, 0.99), stroke_rgb=(0.88, 0.90, 0.94), stroke_w=0.5)
        self.draw_text("PLAIN-ENGLISH CONCEPT (ELI5):", self.margin_x + 16.0, curr_y - 8.5,
                       font="F2", size=7.0, rgb=(0.35, 0.40, 0.48))
        cy = curr_y - 18.5
        for cl in concept_lines:
            self.draw_text(cl, self.margin_x + 16.0, cy, font="F1", size=8.0, rgb=(0.20, 0.24, 0.30))
            cy -= 10.0

        curr_y -= (con_box_h + 5.0)

        # 5. Hostile Trap Box (Soft Crimson Warning)
        if trap:
            trp_box_h = h_trp - 4.0
            self.draw_rect(self.margin_x + 8.0, curr_y - trp_box_h, self.content_w - 16.0, trp_box_h,
                           fill_rgb=(1.0, 0.94, 0.95), stroke_rgb=(0.95, 0.65, 0.70), stroke_w=0.6)
            ty = curr_y - 9.0
            for tl in trap_lines:
                self.draw_text(tl, self.margin_x + 14.0, ty, font="F2", size=7.5, rgb=(0.75, 0.12, 0.20))
                ty -= 9.5

        self.cursor_y = card_bottom - 10.0

    def add_table_directory_section(self):
        """Adds Part 5: One-Line Summary of Every Table."""
        self.check_space(140.0)
        self.add_section_title("Part 5: 12-Table Rapid Mental Map (One-Line Memory Triggers)")
        
        tables = [
            ("airports", "Physical terminals (DEL, BOM). Primary Key = airport_code CHAR(3)."),
            ("routes", "Flight corridors between 2 airports with distance_km. Enforces origin != dest."),
            ("aircraft", "Physical airframes with certified total_capacity and model code."),
            ("seats", "Physical chairs bolted inside airframe. Cascades on aircraft delete."),
            ("flights", "Scheduled trips on a route using an aircraft with departure and arrival times."),
            ("passengers", "Customer identities with unique passport numbers and email addresses."),
            ("bookings", "Commercial order tokens containing 6-character alphanumeric PNR."),
            ("tickets", "Central junction table connecting booking, flight, and seat. UNIQUE(flight, seat)."),
            ("payments", "Monetary audit record (UPI/Card). Enforces positive transacted amount."),
            ("checkins", "1:1 gate clearance creating barcode boarding pass for confirmed tickets."),
            ("baggage", "Checked luggage custody tracking with non-negative weight constraint."),
            ("cancellations", "1:1 revocation ledger enforcing refund_amount <= ticket fare paid.")
        ]

        # Draw 12 compact rows
        for idx, (tname, tdesc) in enumerate(tables):
            y = self.cursor_y - 17.0
            bg = (0.96, 0.98, 1.0) if idx % 2 == 0 else (1.0, 1.0, 1.0)
            self.draw_rect(self.margin_x, y, self.content_w, 17.0, fill_rgb=bg, stroke_rgb=(0.88, 0.90, 0.94), stroke_w=0.4)
            
            # Badge
            self.draw_rect(self.margin_x + 4.0, y + 2.5, 76.0, 12.0, fill_rgb=(0.15, 0.25, 0.45))
            self.draw_text(tname, self.margin_x + 8.0, y + 4.5, font="F2", size=7.5, rgb=(1, 1, 1))

            # Description
            self.draw_text(tdesc, self.margin_x + 86.0, y + 4.5, font="F1", size=7.5, rgb=(0.15, 0.20, 0.30))
            self.cursor_y -= 17.0

        self.cursor_y -= 10.0

    def save(self):
        if self.curr_ops:
            self.pages.append(self.curr_ops)

        num_pages = len(self.pages)
        objects = []
        obj_id = 1

        # Catalog (Obj 1)
        cat_id = obj_id
        objects.append("<< /Type /Catalog /Pages 2 0 R >>")
        obj_id += 1

        # Pages parent (Obj 2)
        pages_id = obj_id
        kids_refs = [f"{i} 0 R" for i in range(pages_id + 1, pages_id + 1 + num_pages)]
        objects.append(f"<< /Type /Pages /Kids [{' '.join(kids_refs)}] /Count {num_pages} >>")
        obj_id += 1

        # Font F1 (Helvetica), F2 (Helvetica-Bold)
        f1_id = pages_id + 1 + num_pages
        f2_id = f1_id + 1

        page_ids = []
        content_ids = []
        for p_idx in range(num_pages):
            p_id = obj_id
            page_ids.append(p_id)
            c_id = p_id + num_pages + 2
            content_ids.append(c_id)
            obj_id += 1

        obj_f1 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
        obj_f2 = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"

        # Content streams
        page_streams = []
        for p_idx, p_ops in enumerate(self.pages):
            # Bottom running footer
            p_ops.append(f"0.80 0.84 0.90 RG 0.5 w {self.margin_x} 32 m {self.page_w - self.margin_x} 32 l S")
            p_ops.append(f"0.45 0.50 0.60 rg BT /F1 7.5 Tf {self.margin_x} 20 Td (DBMS Course Project | Review 2 | Hostile Viva Survival Playbook) Tj ET")
            p_ops.append(f"0.20 0.25 0.35 rg BT /F2 8.0 Tf {self.page_w - self.margin_x - 60} 20 Td (Page {p_idx+1} of {num_pages}) Tj ET")

            stream_data = "\n".join(p_ops)
            page_streams.append(stream_data)

        # Write Binary PDF-1.4
        pdf_out = bytearray()
        pdf_out.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = {}

        def add_obj(oid, data_bytes):
            offsets[oid] = len(pdf_out)
            pdf_out.extend(f"{oid} 0 obj\n".encode('ascii'))
            pdf_out.extend(data_bytes)
            pdf_out.extend(b"\nendobj\n")

        add_obj(cat_id, objects[0].encode('ascii'))
        add_obj(pages_id, objects[1].encode('ascii'))

        for p_idx in range(num_pages):
            p_dict = (
                f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 {self.page_w:.2f} {self.page_h:.2f}]\n"
                f"   /Resources << /Font << /F1 {f1_id} 0 R /F2 {f2_id} 0 R >> >>\n"
                f"   /Contents {content_ids[p_idx]} 0 R >>"
            )
            add_obj(page_ids[p_idx], p_dict.encode('ascii'))

        add_obj(f1_id, obj_f1.encode('ascii'))
        add_obj(f2_id, obj_f2.encode('ascii'))

        for p_idx in range(num_pages):
            s_bytes = page_streams[p_idx].encode('latin-1', 'replace')
            s_obj = f"<< /Length {len(s_bytes)} >>\nstream\n".encode('ascii') + s_bytes + b"\nendstream"
            add_obj(content_ids[p_idx], s_obj)

        # Xref
        xref_offset = len(pdf_out)
        total_objs = max(offsets.keys()) + 1
        pdf_out.extend(f"xref\n0 {total_objs}\n".encode('ascii'))
        pdf_out.extend(b"0000000000 65535 f \n")
        for i in range(1, total_objs):
            off = offsets.get(i, 0)
            pdf_out.extend(f"{off:010d} 00000 n \n".encode('ascii'))

        trailer = f"trailer\n<< /Size {total_objs} /Root {cat_id} 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n"
        pdf_out.extend(trailer.encode('ascii'))

        with open(self.filename, 'wb') as f:
            f.write(pdf_out)

        print(f"Successfully generated clean executive PDF: {self.filename} ({num_pages} pages, {len(pdf_out)} bytes)")


def build_playbook():
    pdf = PDFDoc("docs/VIVA_DEFENSE_PLAYBOOK.pdf")

    # Master Document Header
    pdf.add_main_header(
        "VIVA DEFENSE MASTER PLAYBOOK & ORAL DEFENSE DOSSIER",
        "Airtight Theoretical Proofs, Word-for-Word Recital Answers & Emergency Survival Protocols",
        "SYSTEM: ARFOM-DB (12 Tables, 4 Triggers, 5 B-Tree Indexes) | TARGET: HOSTILE VICE DEAN EVALUATION"
    )

    # Part 1: Fast-Recall Core Cheat Sheet
    pdf.add_section_title("Part 1: The 5 Mandatory Business Rules (The Teacher's Rubric)")
    pdf.add_table_cheat_sheet()

    # Part 2: Crash Course
    pdf.add_section_title("Part 2: DBMS Crash Course (ELI5 - Zero-Background Mastery)")
    pdf.add_crash_course_card(
        "1. Primary Key vs. Foreign Key",
        "A Primary Key uniquely identifies a row in a table. It cannot be NULL and cannot have duplicates. A Foreign Key is a column in a child table pointing to a PK in a parent table to stop orphan records.",
        "airport_code ('DEL') in airports is PK. In tickets, booking_id is an FK pointing to bookings(booking_id)."
    )
    pdf.add_crash_course_card(
        "2. Superkey vs. Candidate Key",
        "A Superkey is any set of columns that uniquely identifies a row (even if it has redundant extra columns). A Candidate Key is a minimal superkey with zero redundant columns. The Primary Key is simply whichever candidate key you choose as primary.",
        "In passengers, (passport_number, email) is a superkey, but passport_number alone is a candidate key."
    )
    pdf.add_crash_course_card(
        "3. Normal Forms: 1NF -> 2NF -> 3NF -> BCNF",
        "1NF: Atomic cells (no comma-separated lists/arrays). 2NF: In 1NF + No Partial Key Dependencies (every non-key attribute depends on the full composite PK). 3NF: In 2NF + No Transitive Dependencies (A -> B -> C). BCNF: Every determinant is a superkey.",
        "Splitting baggage items into a separate table reaches 1NF. Splitting routes from flights eliminates transitive chains and reaches 3NF."
    )
    pdf.add_crash_course_card(
        "4. Lossless Join & Dependency Preservation",
        "Lossless Join means joining decomposed tables via natural join reconstructs the exact original relation with zero fake/spurious rows. Dependency Preservation means all functional dependencies can be validated locally in individual tables without expensive cross-table joins.",
        "Common join column between related tables is always a Candidate Key (e.g., airport_code in routes, aircraft_id in seats)."
    )

    # Part 3: The 16 Questions
    pdf.add_section_title("Part 3: 16 Hostile Viva Questions & Exact Word-for-Word Recitals")

    pdf.add_qa_card(
        1,
        "Why did you normalize to 3NF instead of BCNF? Did you fail to reach BCNF?",
        "Does this student understand the theoretical difference between 3NF and BCNF, or did they blindly follow a syllabus prompt?",
        "Our schema strictly satisfies Boyce-Codd Normal Form (BCNF) across all 12 tables, because in every single table, every determinant in our functional dependency set is a superkey. We framed our presentation under 3NF strictly to align with the syllabus rubric ('up to 3NF'). In classical database theory (Bernstein's Synthesis), 3NF guarantees both Lossless Join and 100% Dependency Preservation. In our specific domain, we achieved full BCNF compliance while preserving 100% of functional dependencies locally without requiring expensive inter-table assertions.",
        "In 3NF, X -> Y allows Y to be a prime attribute even if X is not a superkey. In BCNF, X must ALWAYS be a superkey. In our tables, every single determinant X is already a Primary Key, so we hit BCNF automatically!",
        "NEVER say 'BCNF was too hard' or 'We didn't need BCNF.' Say 'Our schema strictly satisfies BCNF.'"
    )

    pdf.add_qa_card(
        2,
        "Why do you have BOTH a UNIQUE constraint on (flight_id, seat_id) AND an aircraft capacity trigger? Isn't that redundant?",
        "Can you distinguish between micro-level relational uniqueness and macro-level business capacity invariants?",
        "That is layered defensive database engineering addressing two fundamentally distinct invariants. UNIQUE(flight_id, seat_id) enforces Micro-Invariant Uniqueness -- preventing two passengers from being allocated the same physical seat on a flight leg. The trigger trg_verify_aircraft_capacity enforces Macro-Invariant Airframe Capacity. For example, if operational dispatch dynamically swaps an aircraft on a flight from an Airbus A321 (220 seats) down to an A320 (180 seats), previously booked seat IDs might all be unique, but would violate physical airframe capacity. The trigger acts as an active barrier preventing overbooking beyond certified equipment limits.",
        "Unique seat numbers stop two passengers sitting on seat 5A. The capacity trigger stops the airline selling 200 tickets on a plane that only has 180 seats.",
        "Do NOT say 'I added both just in case.' Use the exact terms Micro-Level Uniqueness and Macro-Level Airframe Capacity."
    )

    pdf.add_qa_card(
        3,
        "Why use surrogate integer keys (booking_id, ticket_id) instead of natural keys (booking_ref, passport_number)?",
        "Do you understand B-Tree index storage, leaf page fragmentation, and RAM buffer cache efficiency?",
        "We used natural keys where domain standards are globally immutable -- specifically CHAR(3) for IATA airport codes. However, for high-write transactional tables like bookings, tickets, and payments, we deliberately used monotonic integer surrogate keys for three enterprise reasons: 1) B-Tree Page Fill Factors: Sequential integers append cleanly to the right of B-Tree pages, eliminating index page fragmentation caused by random strings. 2) Memory Efficiency: Joining 4-byte integers across 6 downstream tables consumes significantly less buffer cache RAM than joining 20-character strings. 3) Business Logic Isolation: If a customer updates their PNR or email, zero foreign keys break across downstream operational ledgers.",
        "Computers compare integers in 1 CPU cycle. Comparing long strings takes many cycles and causes page splits on disk B-Trees.",
        "Do NOT say 'Auto-increment is just easier.' Emphasize B-Tree leaf page fragmentation and buffer cache efficiency."
    )

    pdf.add_qa_card(
        4,
        "Why is aircraft_id in seats ON DELETE CASCADE, but in flights it is ON DELETE RESTRICT?",
        "Do you understand referential integrity actions, weak composition entities, and commercial data safety?",
        "Because seats represents an existence-dependent physical component of an airframe (a weak composition entity). A physical seat cannot exist without the plane it is bolted into; when a retired plane is scrapped, its physical seat layout cascades cleanly. In contrast, flights represents an active commercial commitment. If an aircraft has active scheduled flights with booked passengers, deleting the aircraft must be strictly BLOCKED (RESTRICT). This creates a defensive safety net: an in-service aircraft can never be deleted while assigned to flights, while decommissioned aircraft can safely purge their seat maps.",
        "Scrapping a plane scraps its chairs (CASCADE). But you cannot delete a plane if it has passengers scheduled to fly on it tomorrow (RESTRICT).",
        "Point out that flights(aircraft_id) RESTRICT protects in-service planes and booked tickets from accidental deletion!"
    )

    pdf.add_qa_card(
        5,
        "Why is fare_amount stored inside tickets when you could calculate it from a fares table?",
        "Do you understand point-in-time financial auditability and GAAP compliance vs naive over-normalization?",
        "Storing fare_amount directly on the tickets table is a deliberate architectural decision required for Temporal Immutability and Financial Accounting Standards (GAAP). Airline fares fluctuate dynamically due to yield management and demand algorithms. If we calculated ticket prices dynamically via a join to a live fare matrix, every time the airline adjusted prices, the calculated historical revenue of flights flown three months ago would retroactively change, corrupting financial ledgers. Storing the transacted fare at the instant of issuance maintains immutable point-in-time audit integrity.",
        "If you buy milk for Rs. 50, and next week the store raises milk to Rs. 60, your old printed receipt shouldn't magically change to Rs. 60.",
        "Never apologize for storing fare_amount. Proudly call it 'Temporal point-in-time auditing under GAAP compliance.'"
    )

    pdf.add_qa_card(
        6,
        "What happens under heavy concurrent booking traffic? Won't two users booking the same seat cause a race condition in your trigger?",
        "Transaction isolation, row-level locking, and ACID storage engine guarantees under high concurrency.",
        "In an enterprise production environment, concurrency is resolved through two defensive tiers: 1) Transaction Isolation & Row-Level Locking: Booking transactions execute under ISOLATION LEVEL REPEATABLE READ or acquire pessimistic row locks via SELECT aircraft_id FROM flights WHERE flight_id = ? FOR UPDATE. This serializes concurrent booking requests against that flight leg. 2) Atomic Storage Engine Barrier: Even if two concurrent threads bypassed the application trigger simultaneously, the database's declarative constraint UNIQUE (flight_id, seat_id) is enforced atomically at the storage engine's B-Tree leaf level. The B-Tree page latch guarantees that one thread commits and the second thread is immediately rejected with a duplicate key exception.",
        "Even if two users click 'Buy' at the exact same millisecond, the database index physically only allows one row to be written. The second gets an instant error.",
        "Do NOT say 'Concurrency is handled by the front-end.' Concurrency in DBMS is handled by transaction isolation levels and B-Tree unique latches."
    )

    pdf.add_qa_card(
        7,
        "Why did you write triggers instead of declarative CHECK constraints for capacity and check-in eligibility?",
        "SQL standard declarative constraint boundaries vs procedural extensions.",
        "Because ANSI SQL standards strictly limit declarative CHECK constraints to single-row, single-table attribute evaluations. A CHECK constraint cannot execute subqueries or inspect parent table states across foreign tables -- for instance, checking bookings.booking_status from inside a checkins insert, or calculating COUNT(tickets) against aircraft.total_capacity. In relational database engines like PostgreSQL and MySQL, cross-table invariant assertions must be enforced via Procedural Triggers (BEFORE INSERT), which execute with indexed O(1) lookups.",
        "CHECK constraints only know what is in the row you are currently typing. They cannot look into other tables. Triggers can query any table.",
        "Do NOT say 'I like triggers better.' Say 'Declarative CHECK constraints cannot execute subqueries across foreign tables in the SQL standard.'"
    )

    pdf.add_qa_card(
        8,
        "Why is cancellations a separate table with ticket_id UNIQUE instead of just setting ticket_status = 'CANCELLED' in tickets?",
        "Sparse tables, null anomalies, and 3NF normalization vs audit ledgers.",
        "That directly satisfies Third Normal Form (3NF) and Financial Audit Separation: 1) Elimination of Null Anomalies: Cancellation metadata (cancellation_timestamp, refund_amount) applies only to cancelled tickets. Adding these columns directly into tickets would force 95% of active issued tickets to store NULL values, resulting in sparse, inefficient tables. 2) Audit Ledger Integrity: A cancellation is a distinct financial accounting event involving refund capital disbursement. A dedicated ledger with ticket_id UNIQUE preserves an unalterable audit trail and links cleanly to payment reconciliation.",
        "You don't put a 'Date of Death' column on a live employee badge table; you keep termination records in a dedicated audit log.",
        "Mention that it avoids 'Sparse Tables and Null Anomalies in dense relational pages.'"
    )

    pdf.add_qa_card(
        9,
        "What index structures did you create and why?",
        "Indexing strategy, B-Tree selectivity, and query optimization paths.",
        "We created secondary B-Tree composite indexes targeted at high-frequency query access paths: 1) idx_flights_search on flights(route_id, scheduled_departure, flight_status): Optimizes customer flight searches using an index-only range scan without full-table scans. 2) idx_bookings_pnr on bookings(booking_ref): Guarantees O(log N) hash-like lookup speed when ground staff query a 6-character PNR. 3) idx_tickets_booking on tickets(booking_id) and idx_tickets_flight on tickets(flight_id): Accelerates multi-table joins when assembling real-time flight manifests and calculating occupancy yield.",
        "An index is like the index at the back of a textbook. Instead of reading all 500 pages to find 'Delhi flight', you jump directly to page 42.",
        "Always specify that they are 'Secondary B-Tree Composite Indexes' with high selectivity."
    )

    pdf.add_qa_card(
        10,
        "Prove that your schema decomposition has no insertion, deletion, or update anomalies.",
        "Practical proof of 3NF normalization benefits across the data lifecycle.",
        "We can prove this by inspecting our decoupled entities: 1) No Insertion Anomaly: We can add a newly commissioned airport into airports or a new plane into aircraft without requiring any flights, bookings, or passengers to exist. In the unnormalized relation (UNF), an airport could not exist without a booking reference. 2) No Deletion Anomaly: If a passenger cancels their booking, or if old booking records are archived, the physical flight corridor, schedule, and aircraft definitions remain intact. 3) No Update Anomaly: If Indira Gandhi International Airport changes its name, we update a single row in airports. All downstream routes and flights instantly reflect the update via foreign key reference without inconsistent duplicates.",
        "Decoupling independent entities means updating an airport name in 1 place updates it everywhere without contradictory data.",
        "State all 3 anomalies clearly: Insertion, Deletion, and Update."
    )

    pdf.add_qa_card(
        11,
        "What is a Weak Entity in your schema, and how is it identified?",
        "Relational entity modeling semantics, existence dependency, and identifying composite keys.",
        "In our schema, seats and baggage function as Weak Entities. A seat cannot exist without an aircraft (composite key aircraft_id + seat_number). A bag cannot exist without an originating check-in event (checkin_id). Both cascade on parent deletion (ON DELETE CASCADE).",
        "A weak entity cannot be uniquely identified by its own attributes alone; it borrows part of its identity from a parent owner.",
        "Quote the composite unique constraint: UNIQUE (aircraft_id, seat_number)."
    )

    pdf.add_qa_card(
        12,
        "How do your triggers maintain state machine transitions automatically?",
        "Active database automation, automated side effects, and lifecycle integrity.",
        "Our triggers execute active state machine transitions: Inserting into checkins triggers an update setting tickets.ticket_status = 'CHECKED_IN'. Inserting into cancellations triggers an update setting tickets.ticket_status = 'CANCELLED'. This guarantees that application software cannot accidentally leave tickets in an inconsistent or out-of-sync state.",
        "The database acts as an active gatekeeper that guarantees lifecycle states remain valid without relying solely on client code.",
        "Call it 'Engine-enforced state machine automation.'"
    )

    pdf.add_qa_card(
        13,
        "Explain Lossless Join Decomposition and how your schema satisfies it.",
        "Formal mathematical relational theorem: R1 INTERSECT R2 -> R1 or R2 in F+.",
        "A decomposition of relation R into R1 and R2 is Lossless if and only if R1 INTERSECT R2 -> R1 or R1 INTERSECT R2 -> R2 in F+. In our schema, every single join condition between related tables is a Primary Key: airports INTERSECT routes = airport_code (PK of airports); aircraft INTERSECT seats = aircraft_id (PK of aircraft); bookings INTERSECT tickets = booking_id (PK of bookings). Because the common attribute is always a candidate key, joining tables reconstructs the universal relation with zero spurious or false tuples.",
        "Lossless join means when you stitch the tables back together with JOIN, you get the exact original data back -- no ghost rows.",
        "Quote the formula: R1 INTERSECT R2 -> R1 or R1 INTERSECT R2 -> R2."
    )

    pdf.add_qa_card(
        14,
        "Explain Dependency Preservation and why your schema preserves 100% of FDs.",
        "Bernstein's synthesis theorem: (F1 UNION F2 UNION ... UNION Fk)+ == F+.",
        "Dependency Preservation means the union of all functional dependencies projected onto our individual tables equals the global closure: (F1 UNION F2 UNION ... UNION Fk)+ == F+. In our schema, all 18 minimal functional dependencies are enforced locally inside their single projected table via Primary Keys and UNIQUE constraints without requiring expensive cross-table joins during every insert or update.",
        "Dependency preservation means you don't need to join 3 tables just to check if an insert is legal.",
        "State that all 18 functional dependencies are enforced locally via PK/UQ."
    )

    pdf.add_qa_card(
        15,
        "What is the difference between Logical and Physical Data Independence in your project?",
        "ANSI/SPARC 3-schema architecture in practical database deployment.",
        "1) Logical Data Independence is demonstrated through our Operational Views (view_flight_manifest, view_flight_occupancy). If internal tables change or columns are added, the conceptual views consumed by ground applications remain constant. 2) Physical Data Independence is demonstrated through our Secondary B-Tree Indexes; we can add, drop, or rebuild indexes like idx_flights_search without altering a single application SQL query or changing table schemas.",
        "Logical independence protects user queries from schema changes. Physical independence protects queries from storage/indexing changes.",
        "Use view_flight_manifest as the logical example and idx_flights_search as the physical example."
    )

    pdf.add_qa_card(
        16,
        "How does your database handle refund deductions? Why not just refund 100%?",
        "Financial domain rules, business check constraints, and revenue leakage prevention.",
        "Airlines deduct cancellation penalties based on booking cancellation windows. In our seed data, Ticket #5 had a fare of Rs. 8,500.00 and was refunded Rs. 6,800.00, retaining Rs. 1,700.00 as penalty profit. Trigger trg_enforce_refund_bounds guarantees refunds cannot exceed base fare. Query #5 tracks net retained cancellation penalties across the system.",
        "Cancellation fee = Paid Fare minus Refund Amount. The trigger guarantees refund <= fare so the airline never loses money.",
        "Refer to Query #5 in sql/03_queries_and_views.sql."
    )

    # Force Page Break to give Part 4, Part 5, and Part 6 a dedicated final tactical briefing page
    pdf.new_page()

    # Part 4: Emergency Survival Protocol
    pdf.add_section_title("Part 4: Emergency Survival Protocol (The Poker Face)")
    pdf.add_crash_course_card(
        "1. If She Interrupts Mid-Sentence",
        "Do not look defensive or flustered. Stop speaking instantly, nod once, let her finish, then respond calmly:",
        "'Yes, Vice Dean, that directly relates to our referential constraint in table...'"
    )
    pdf.add_crash_course_card(
        "2. If She Asks a Term You Don't Know (The Pivot Script)",
        "Do not guess or use fake buzzwords. Throw the ball back into her court calmly:",
        "'In our operational architecture, we enforced that directly at the storage engine layer via triggers. Could you specify which table's lifecycle you would like to see that applied to?'"
    )
    pdf.add_crash_course_card(
        "3. The 3-Second Rule (Executive Composure)",
        "When she finishes asking a hostile question, count 1... 2... 3... in your head before answering.",
        "A calm 3-second pause makes you look like an architect analyzing tradeoffs, not a panicked student reciting memorized notes."
    )

    # Part 5: Rapid Table Directory
    pdf.add_table_directory_section()

    # Part 6: Quick-Fire Verification Commands
    pdf.add_section_title("Part 6: Instant Demo Verification Commands (Live Execution)")
    pdf.add_crash_course_card(
        "Run Full Automated Test Suite (6 Negative Tests + Seed Verification)",
        "Execute in terminal to prove 100% database constraint and trigger enforcement in 3 seconds:",
        "python3 demo_runner.py --demo"
    )
    pdf.add_crash_course_card(
        "Open Vector Visual Dashboards in Browser (ER Diagram, Data Dictionary, 3NF Proofs)",
        "Opens the complete high-contrast visual portal for Review 2 visual presentation:",
        "open visuals/index.html"
    )

    pdf.save()

    # Also overwrite docs/VIVA_DEFENSE_MATRIX.pdf so both filenames have the elite version!
    matrix_pdf_path = "docs/VIVA_DEFENSE_MATRIX.pdf"
    import shutil
    shutil.copyfile("docs/VIVA_DEFENSE_PLAYBOOK.pdf", matrix_pdf_path)
    print(f"Also synchronized: {matrix_pdf_path}")

if __name__ == "__main__":
    build_playbook()
