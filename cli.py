#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB LIVE INTERACTIVE SQL CLI FOR VIVA & FACULTY DEFENSE
Student: Sanjyit Suresh Kumar (Roll No. 25WU0102243) • AIML Whales (#18)
===============================================================================
Usage:
    python3 cli.py
===============================================================================
"""

import sqlite3
import os
import sys
import time

# Attempt to enable readline for command history and arrow key navigation
try:
    import readline
except ImportError:
    pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "3rd presentation", "app", "arfom.db")

if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(ROOT_DIR, "workbench", "arfom.db")

# ANSI Color Codes
C_RESET   = "\033[0m"
C_BOLD    = "\033[1m"
C_RED     = "\033[91m"
C_GREEN   = "\033[92m"
C_YELLOW  = "\033[93m"
C_BLUE    = "\033[94m"
C_MAGENTA = "\033[95m"
C_CYAN    = "\033[96m"
C_DIM     = "\033[90m"

def render_table(headers, rows):
    """Renders a pristine MySQL/PostgreSQL-style ASCII grid table."""
    if not headers and not rows:
        print(f"{C_DIM}(Empty set){C_RESET}\n")
        return

    # Determine string representation and column widths
    str_rows = []
    for r in rows:
        str_rows.append(["NULL" if v is None else str(v) for v in r])

    widths = [len(str(h)) for h in headers]
    for r in str_rows:
        for i, val in enumerate(r):
            if i < len(widths):
                widths[i] = max(widths[i], len(val))
            else:
                widths.append(len(val))

    # Borders
    top_border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    sep_border = "+" + "+".join("=" * (w + 2) for w in widths) + "+"

    print(f"{C_DIM}{top_border}{C_RESET}")
    
    # Header Row
    header_cells = [f" {headers[i]:<{widths[i]}} " for i in range(len(headers))]
    print(f"{C_DIM}|{C_RESET}" + f"{C_DIM}|{C_RESET}".join(f"{C_BOLD}{C_CYAN}{cell}{C_RESET}" for cell in header_cells) + f"{C_DIM}|{C_RESET}")
    print(f"{C_DIM}{sep_border}{C_RESET}")

    if not str_rows:
        print(f"{C_DIM}|{C_RESET} " + f"{C_YELLOW}Empty set (0 rows){C_RESET}".center(sum(widths) + len(widths)*3 - 3) + f" {C_DIM}|{C_RESET}")
    else:
        for r in str_rows:
            row_cells = []
            for i, val in enumerate(r):
                # Highlight NULLs differently
                if val == "NULL":
                    styled_val = f"{C_DIM}NULL{C_RESET}"
                    row_cells.append(f" {styled_val}{' ' * (widths[i] - 4)} ")
                else:
                    row_cells.append(f" {val:<{widths[i]}} ")
            print(f"{C_DIM}|{C_RESET}" + f"{C_DIM}|{C_RESET}".join(row_cells) + f"{C_DIM}|{C_RESET}")

    print(f"{C_DIM}{top_border}{C_RESET}")

def print_banner():
    banner = f"""{C_BOLD}{C_CYAN}
┌─────────────────────────────────────────────────────────────────────────────┐
│  ✈️  ARFOM-DB INTERACTIVE RELATIONAL SQL CONSOLE                           │
│  Candidate: Sanjyit Suresh Kumar (Roll No. 25WU0102243) • AIML Whales (#18) │
│  Engine: SQLite 3.x with Strict Foreign Keys & Invariants                   │
└─────────────────────────────────────────────────────────────────────────────┘{C_RESET}
{C_DIM}Commands: Type any SQL query ending with ';' | 'tables' to list | 'desc <table>' | 'clear' | 'exit'{C_RESET}
"""
    print(banner)

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def show_tables(conn):
    cur = conn.cursor()
    cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY type DESC, name ASC;")
    tables = cur.fetchall()
    
    rows = []
    for name, obj_type in tables:
        try:
            cur.execute(f"SELECT COUNT(*) FROM \"{name}\";")
            count = cur.fetchone()[0]
        except Exception:
            count = 0
        rows.append([name, obj_type.upper(), count])
    
    render_table(["Table / View Name", "Object Type", "Row Count"], rows)
    print(f"{C_GREEN}✓ {len(tables)} relational entities active in storage.{C_RESET}\n")

def desc_table(conn, table_name):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?;", (table_name,))
    if not cur.fetchone():
        print(f"{C_RED}Error: Table or view '{table_name}' does not exist.{C_RESET}\n")
        return

    cur.execute(f"PRAGMA table_info(\"{table_name}\");")
    cols = cur.fetchall()
    
    rows = []
    for c in cols:
        cid, name, col_type, notnull, dflt, pk = c
        key_badge = "PK" if pk else ""
        null_badge = "NO" if notnull else "YES"
        rows.append([name, col_type or "ANY", null_badge, key_badge, str(dflt) if dflt is not None else "NULL"])
    
    render_table(["Column Name", "Data Type", "Nullable", "Key", "Default"], rows)

def main():
    if not os.path.exists(DB_PATH):
        print(f"{C_RED}Database not found at {DB_PATH}. Building database...{C_RESET}")
        import subprocess
        subprocess.run([sys.executable, os.path.join(ROOT_DIR, "workbench", "build_database.py")])

    print_banner()

    conn = get_connection()
    buffer = ""

    while True:
        try:
            prompt = f"{C_BOLD}{C_GREEN}SQL>{C_RESET} " if not buffer else f"{C_BOLD}{C_YELLOW}   ->{C_RESET} "
            line = input(prompt).strip()

            if not buffer and not line:
                continue

            # Meta commands
            lower_line = line.lower().rstrip(';')
            if not buffer:
                if lower_line in ['exit', 'quit', 'q']:
                    print(f"\n{C_CYAN}Exiting ARFOM-DB Console. Good luck with your defense!{C_RESET}")
                    break
                elif lower_line in ['clear', 'cls']:
                    os.system('clear' if os.name != 'nt' else 'cls')
                    print_banner()
                    continue
                elif lower_line in ['tables', '\\dt', 'show tables']:
                    show_tables(conn)
                    continue
                elif lower_line.startswith('desc ') or lower_line.startswith('describe '):
                    parts = lower_line.split()
                    if len(parts) > 1:
                        desc_table(conn, parts[1])
                    continue
                elif lower_line in ['help', '?']:
                    print(f"""
{C_BOLD}Available Commands:{C_RESET}
  {C_CYAN}tables{C_RESET}                  - List all 12 tables and views with row counts
  {C_CYAN}desc <table_name>{C_RESET}        - Describe schema columns, types, and primary keys
  {C_CYAN}clear{C_RESET}                   - Clear terminal screen
  {C_CYAN}exit{C_RESET} / {C_CYAN}quit{C_RESET}             - Exit console
  {C_CYAN}<any SQL statement>;{C_RESET}    - Execute raw SQL (e.g. SELECT * FROM flights;)
""")
                    continue

            buffer += (" " + line) if buffer else line

            if buffer.endswith(";"):
                sql = buffer.strip()
                buffer = ""
                
                t0 = time.perf_counter()
                try:
                    cur = conn.cursor()
                    cur.execute(sql)
                    elapsed_ms = (time.perf_counter() - t0) * 1000

                    if cur.description:
                        headers = [col[0] for col in cur.description]
                        rows = cur.fetchall()
                        render_table(headers, rows)
                        print(f"{C_GREEN}✓ {len(rows)} row(s) in set ({elapsed_ms:.2f} ms){C_RESET}\n")
                    else:
                        conn.commit()
                        affected = cur.rowcount
                        print(f"{C_GREEN}✓ Query OK, {affected} row(s) affected ({elapsed_ms:.2f} ms){C_RESET}\n")

                except sqlite3.IntegrityError as e:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    print(f"{C_RED}❌ Integrity Constraint Violation ({elapsed_ms:.2f} ms):{C_RESET}")
                    print(f"   {C_RED}{str(e)}{C_RESET}\n")
                except Exception as e:
                    elapsed_ms = (time.perf_counter() - t0) * 1000
                    print(f"{C_RED}❌ SQL Error ({elapsed_ms:.2f} ms):{C_RESET}")
                    print(f"   {C_RED}{str(e)}{C_RESET}\n")

        except KeyboardInterrupt:
            buffer = ""
            print(f"\n{C_YELLOW}(Query cancelled){C_RESET}")
        except EOFError:
            print(f"\n{C_CYAN}Exiting ARFOM-DB Console.{C_RESET}")
            break

if __name__ == "__main__":
    main()
