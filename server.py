#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB UNIFIED MASTER HTTP & REST API SERVER (PORT 8000)
Serves the Entire Project Root with Live CRUD, Schema Visuals, and Slides
===============================================================================
Author: Sanjyit Suresh Kumar (Roll No. 25WU0102243)
Project Title: Airline Reservation & Flight Operations Management System
Course: Database Management Systems (AIML Whales - Serial #18)
===============================================================================
"""

import http.server
import socketserver
import json
import sqlite3
import os
import sys
import time
import urllib.parse

PORT = 8000
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(ROOT_DIR, "3rd presentation", "app")
DB_PATH = os.path.join(APP_DIR, "arfom.db")

# Ensure database exists
if not os.path.exists(DB_PATH):
    source_db = os.path.join(ROOT_DIR, "workbench", "arfom.db")
    if os.path.exists(source_db):
        import shutil
        shutil.copy2(source_db, DB_PATH)
        print(f"[ARFOM-DB] Seeded database from {source_db}")
    else:
        build_script = os.path.join(ROOT_DIR, "workbench", "build_database.py")
        if os.path.exists(build_script):
            import subprocess
            subprocess.run([sys.executable, build_script], check=True)
            if os.path.exists(source_db):
                import shutil
                shutil.copy2(source_db, DB_PATH)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

class UnifiedProjectHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Serve from the root directory so ALL directories (visuals, Presentation-II, 3rd presentation, workbench, records) are accessible
        super().__init__(*args, directory=ROOT_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query_params = urllib.parse.parse_qs(parsed.query)

        # REST API Endpoints
        if path == "/api/status":
            self.handle_status()
            return
        elif path == "/api/tables":
            self.handle_tables()
            return
        elif path == "/api/data":
            self.handle_get_data(query_params)
            return
        elif path == "/api/stats":
            self.handle_stats()
            return
        elif path == "/api/flights_list":
            self.handle_flights_list(query_params)
            return
        elif path == "/api/airport_board":
            self.handle_airport_board(query_params)
            return
        elif path == "/api/available_seats":
            self.handle_available_seats(query_params)
            return

        # Friendly URL Aliases & Redirects
        if path in ["/", "/index.html"]:
            self.path = "/visuals/index.html"
        elif path in ["/review2", "/presentation2", "/presentation-ii"]:
            self.send_response(302)
            self.send_header('Location', '/Presentation-II/Presentation-II.html')
            self.end_headers()
            return
        elif path in ["/review3", "/presentation3", "/presentation-iii", "/app"]:
            self.send_response(302)
            self.send_header('Location', '/3rd%20presentation/app/index.html')
            self.end_headers()
            return
        elif path in ["/slides2"]:
            self.send_response(302)
            self.send_header('Location', '/Presentation-II/Presentation-II.html')
            self.end_headers()
            return
        elif path in ["/slides3", "/slides"]:
            self.send_response(302)
            self.send_header('Location', '/3rd%20presentation/slides/presentation_iii_slides.html')
            self.end_headers()
            return
        elif path in ["/visuals", "/visuals/"]:
            self.send_response(302)
            self.send_header('Location', '/visuals/index.html')
            self.end_headers()
            return
        elif path in ["/workbench", "/workbench/"]:
            self.send_response(302)
            self.send_header('Location', '/workbench/index.html')
            self.end_headers()
            return
        elif path in ["/records", "/records/"]:
            self.send_response(302)
            self.send_header('Location', '/records/PRINTABLE_OUTPUTS.html')
            self.end_headers()
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        post_body = self.rfile.read(content_length).decode('utf-8')

        try:
            payload = json.loads(post_body) if post_body else {}
        except Exception as e:
            self._send_json({"status": "error", "error": f"Invalid JSON payload: {str(e)}"}, status_code=400)
            return

        if path == "/api/insert":
            self.handle_insert(payload)
        elif path == "/api/delete":
            self.handle_delete(payload)
        elif path == "/api/book_ticket":
            self.handle_book_ticket(payload)
        elif path == "/api/checkin_baggage":
            self.handle_checkin_baggage(payload)
        elif path == "/api/query":
            self.handle_raw_query(payload)
        elif path == "/api/reset":
            self.handle_reset()
        else:
            self.send_error(404, "Endpoint not found")

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, default=str).encode('utf-8'))

    def handle_status(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            t_count = cur.fetchone()[0]
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='view';")
            v_count = cur.fetchone()[0]
            conn.close()

            self._send_json({
                "status": "online",
                "database_name": "arfom.db",
                "engine": "SQLite 3.x with Strict FK & CHECK Enforcement",
                "mysql_compatibility": "Full (ANSI SQL 3NF Schema)",
                "table_count": t_count,
                "view_count": v_count,
                "project_title": "Airline Reservation & Flight Operations Management System",
                "student_name": "Sanjyit Suresh Kumar",
                "roll_no": "25WU0102243",
                "section": "AIML Whales (Review 3 - Serial #18)"
            })
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

    def handle_tables(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%' ORDER BY type DESC, name ASC;")
            entries = cur.fetchall()

            result = []
            for name, obj_type in entries:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM \"{name}\";")
                    row_count = cur.fetchone()[0]
                except Exception:
                    row_count = 0

                cur.execute(f"PRAGMA table_info(\"{name}\");")
                cols = cur.fetchall()
                col_defs = [{"cid": c[0], "name": c[1], "type": c[2], "notnull": c[3], "pk": c[5]} for c in cols]

                result.append({
                    "name": name,
                    "type": obj_type,
                    "row_count": row_count,
                    "columns": col_defs
                })
            conn.close()
            self._send_json({"status": "success", "tables": result})
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

    def handle_get_data(self, query_params):
        table_name = query_params.get("table", ["view_master_manifest"])[0]
        search = query_params.get("search", [""])[0].strip()
        sort_col = query_params.get("sortCol", [""])[0].strip()
        sort_dir = query_params.get("sortDir", ["ASC"])[0].upper()
        if sort_dir not in ["ASC", "DESC"]:
            sort_dir = "ASC"

        try:
            page = max(1, int(query_params.get("page", ["1"])[0]))
            page_size = max(5, min(200, int(query_params.get("pageSize", ["25"])[0])))
        except ValueError:
            page = 1
            page_size = 25

        offset = (page - 1) * page_size

        t0 = time.perf_counter()
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table', 'view') AND name = ?;", (table_name,))
            if not cur.fetchone():
                conn.close()
                self._send_json({"status": "error", "error": f"Table or View '{table_name}' does not exist."}, status_code=404)
                return

            cur.execute(f"PRAGMA table_info(\"{table_name}\");")
            col_info = cur.fetchall()
            columns = [c[1] for c in col_info]
            pk_col = next((c[1] for c in col_info if c[5] == 1), columns[0] if columns else None)

            where_clauses = []
            params = []
            if search:
                sub_clauses = []
                for c in columns:
                    sub_clauses.append(f"CAST(\"{c}\" AS TEXT) LIKE ?")
                    params.append(f"%{search}%")
                where_clauses.append(f"({' OR '.join(sub_clauses)})")

            where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            count_sql = f"SELECT COUNT(*) FROM \"{table_name}\"{where_str};"
            cur.execute(count_sql, params)
            total_records = cur.fetchone()[0]

            order_by_str = ""
            if sort_col and sort_col in columns:
                order_by_str = f" ORDER BY \"{sort_col}\" {sort_dir}"
            elif pk_col:
                order_by_str = f" ORDER BY \"{pk_col}\" DESC"

            data_sql = f"SELECT * FROM \"{table_name}\"{where_str}{order_by_str} LIMIT ? OFFSET ?;"
            exec_params = list(params) + [page_size, offset]
            cur.execute(data_sql, exec_params)
            rows = cur.fetchall()

            conn.close()
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

            self._send_json({
                "status": "success",
                "table": table_name,
                "columns": columns,
                "pk_col": pk_col,
                "rows": rows,
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": max(1, (total_records + page_size - 1) // page_size),
                "sql_executed": data_sql.replace("?", "%s") if params else data_sql,
                "execution_time_ms": elapsed_ms
            })
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({"status": "error", "error": str(e), "execution_time_ms": elapsed_ms}, status_code=500)

    def handle_insert(self, payload):
        table_name = payload.get("table", "").strip()
        data = payload.get("data", {})

        if not table_name or not data:
            self._send_json({"status": "error", "error": "Table name and record data required."}, status_code=400)
            return

        t0 = time.perf_counter()
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
            if not cur.fetchone():
                conn.close()
                self._send_json({"status": "error", "error": f"Table '{table_name}' does not exist."}, status_code=400)
                return

            cur.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
            before_count = cur.fetchone()[0]

            cols = list(data.keys())
            vals = list(data.values())
            placeholders = ", ".join(["?"] * len(vals))
            col_str = ", ".join([f"\"{c}\"" for c in cols])

            insert_sql = f"INSERT INTO \"{table_name}\" ({col_str}) VALUES ({placeholders});"

            cur.execute(insert_sql, vals)
            new_id = cur.lastrowid
            conn.commit()

            cur.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
            after_count = cur.fetchone()[0]

            cur.execute(f"PRAGMA table_info(\"{table_name}\");")
            col_info = cur.fetchall()
            pk_col = next((c[1] for c in col_info if c[5] == 1), None)

            inserted_record = None
            if pk_col and new_id:
                cur.execute(f"SELECT * FROM \"{table_name}\" WHERE \"{pk_col}\" = ?;", (new_id,))
                inserted_record = cur.fetchone()

            conn.close()
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

            rendered_vals = []
            for v in vals:
                if v is None:
                    rendered_vals.append("NULL")
                elif isinstance(v, (int, float)):
                    rendered_vals.append(str(v))
                else:
                    rendered_vals.append(f"'{v}'")
            human_sql = f"INSERT INTO {table_name} ({', '.join(cols)}) VALUES ({', '.join(rendered_vals)});"

            self._send_json({
                "status": "success",
                "action": "INSERT",
                "table": table_name,
                "new_id": new_id,
                "before_count": before_count,
                "after_count": after_count,
                "delta": after_count - before_count,
                "sql": human_sql,
                "inserted_record": inserted_record,
                "columns": [c[1] for c in col_info],
                "message": f"Successfully inserted new record into '{table_name}' (ID: {new_id}).",
                "execution_time_ms": elapsed_ms
            })
        except sqlite3.IntegrityError as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({
                "status": "error",
                "error_type": "INTEGRITY_CONSTRAINT_VIOLATION",
                "error": str(e),
                "table": table_name,
                "message": f"Database Constraint Enforced: {str(e)}",
                "execution_time_ms": elapsed_ms
            }, status_code=200)
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({
                "status": "error",
                "error_type": "DATABASE_ERROR",
                "error": str(e),
                "execution_time_ms": elapsed_ms
            }, status_code=200)

    def handle_delete(self, payload):
        table_name = payload.get("table", "").strip()
        id_col = payload.get("id_col", "").strip()
        id_val = payload.get("id_val", None)

        if not table_name or not id_col or id_val is None:
            self._send_json({"status": "error", "error": "Table, ID column, and ID value are required for deletion."}, status_code=400)
            return

        t0 = time.perf_counter()
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,))
            if not cur.fetchone():
                conn.close()
                self._send_json({"status": "error", "error": f"Table '{table_name}' does not exist."}, status_code=400)
                return

            cur.execute(f"SELECT * FROM \"{table_name}\" WHERE \"{id_col}\" = ?;", (id_val,))
            record_to_delete = cur.fetchone()

            if not record_to_delete:
                conn.close()
                self._send_json({"status": "error", "error": f"Record with {id_col} = {id_val} not found in '{table_name}'."}, status_code=404)
                return

            cur.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
            before_count = cur.fetchone()[0]

            delete_sql = f"DELETE FROM \"{table_name}\" WHERE \"{id_col}\" = ?;"
            cur.execute(delete_sql, (id_val,))
            affected = cur.rowcount
            conn.commit()

            cur.execute(f"SELECT COUNT(*) FROM \"{table_name}\";")
            after_count = cur.fetchone()[0]

            cur.execute(f"PRAGMA table_info(\"{table_name}\");")
            cols = [c[1] for c in cur.fetchall()]

            conn.close()
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

            human_sql = f"DELETE FROM {table_name} WHERE {id_col} = {id_val};"

            self._send_json({
                "status": "success",
                "action": "DELETE",
                "table": table_name,
                "id_col": id_col,
                "id_val": id_val,
                "deleted_record": record_to_delete,
                "columns": cols,
                "before_count": before_count,
                "after_count": after_count,
                "delta": after_count - before_count,
                "rows_affected": affected,
                "sql": human_sql,
                "message": f"Successfully deleted record ({id_col} = {id_val}) from '{table_name}'. Database row count updated from {before_count} to {after_count}.",
                "execution_time_ms": elapsed_ms
            })
        except sqlite3.IntegrityError as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({
                "status": "error",
                "error_type": "FOREIGN_KEY_RESTRICT_VIOLATION",
                "error": str(e),
                "table": table_name,
                "message": f"Cannot delete: Referential integrity protected by foreign key restriction ({str(e)}).",
                "execution_time_ms": elapsed_ms
            }, status_code=200)
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({
                "status": "error",
                "error_type": "DATABASE_ERROR",
                "error": str(e),
                "execution_time_ms": elapsed_ms
            }, status_code=200)

    def handle_raw_query(self, payload):
        sql = payload.get("sql", "").strip()
        if not sql:
            self._send_json({"status": "error", "error": "Query cannot be empty."}, status_code=400)
            return

        t0 = time.perf_counter()
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(sql)

            if cur.description:
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                conn.commit()
                conn.close()
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                self._send_json({
                    "status": "success",
                    "columns": cols,
                    "rows": rows,
                    "row_count": len(rows),
                    "sql": sql,
                    "execution_time_ms": elapsed_ms
                })
            else:
                affected = cur.rowcount
                conn.commit()
                conn.close()
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                self._send_json({
                    "status": "success",
                    "columns": ["message", "rows_affected"],
                    "rows": [["Query executed successfully.", affected]],
                    "row_count": 1,
                    "rows_affected": affected,
                    "sql": sql,
                    "execution_time_ms": elapsed_ms
                })
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({
                "status": "error",
                "error": str(e),
                "sql": sql,
                "execution_time_ms": elapsed_ms
            }, status_code=200)

    def handle_stats(self):
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            stats = {}
            for t in ['passengers', 'flights', 'bookings', 'tickets', 'baggage', 'checkins', 'cancellations', 'airports', 'aircraft', 'routes']:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM \"{t}\";")
                    stats[t] = cur.fetchone()[0]
                except Exception:
                    stats[t] = 0

            try:
                cur.execute("SELECT COALESCE(SUM(amount_paid), 0) FROM payments WHERE payment_status = 'SUCCESS';")
                stats['total_revenue'] = cur.fetchone()[0]
            except Exception:
                stats['total_revenue'] = 0

            conn.close()
            self._send_json({"status": "success", "stats": stats})
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

    def handle_flights_list(self, query_params):
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT 
                    f.flight_id,
                    f.flight_number,
                    r.origin_airport,
                    orig.city AS origin_city,
                    r.dest_airport,
                    dest.city AS dest_city,
                    r.distance_km,
                    ac.model AS aircraft_model,
                    ac.total_capacity,
                    f.scheduled_departure,
                    f.scheduled_arrival,
                    f.flight_status,
                    (SELECT COUNT(*) FROM tickets t WHERE t.flight_id = f.flight_id AND t.ticket_status != 'CANCELLED') AS booked_count
                FROM flights f
                JOIN routes r ON f.route_id = r.route_id
                JOIN airports orig ON r.origin_airport = orig.airport_code
                JOIN airports dest ON r.dest_airport = dest.airport_code
                JOIN aircraft ac ON f.aircraft_id = ac.aircraft_id
                ORDER BY f.flight_id ASC;
            """)
            cols = [c[0] for c in cur.description]
            rows = [dict(zip(cols, r)) for r in cur.fetchall()]
            conn.close()
            self._send_json({"status": "success", "flights": rows})
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

    def handle_airport_board(self, query_params):
        airport_code = query_params.get("airport", ["DEL"])[0].upper()
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            
            # Airport Info
            cur.execute("SELECT airport_code, airport_name, city, country FROM airports WHERE airport_code = ?;", (airport_code,))
            airport_info = cur.fetchone()
            
            # Departures from this airport
            cur.execute("""
                SELECT 
                    f.flight_id, f.flight_number, r.dest_airport, dest.city AS dest_city,
                    f.scheduled_departure, ac.model, f.flight_status,
                    (SELECT COUNT(*) FROM tickets t WHERE t.flight_id = f.flight_id) AS passenger_count
                FROM flights f
                JOIN routes r ON f.route_id = r.route_id
                JOIN airports dest ON r.dest_airport = dest.airport_code
                JOIN aircraft ac ON f.aircraft_id = ac.aircraft_id
                WHERE r.origin_airport = ?
                ORDER BY f.scheduled_departure ASC;
            """, (airport_code,))
            dep_cols = [c[0] for c in cur.description]
            departures = [dict(zip(dep_cols, r)) for r in cur.fetchall()]

            # Arrivals to this airport
            cur.execute("""
                SELECT 
                    f.flight_id, f.flight_number, r.origin_airport, orig.city AS origin_city,
                    f.scheduled_arrival, ac.model, f.flight_status,
                    (SELECT COUNT(*) FROM tickets t WHERE t.flight_id = f.flight_id) AS passenger_count
                FROM flights f
                JOIN routes r ON f.route_id = r.route_id
                JOIN airports orig ON r.origin_airport = orig.airport_code
                JOIN aircraft ac ON f.aircraft_id = ac.aircraft_id
                WHERE r.dest_airport = ?
                ORDER BY f.scheduled_arrival ASC;
            """, (airport_code,))
            arr_cols = [c[0] for c in cur.description]
            arrivals = [dict(zip(arr_cols, r)) for r in cur.fetchall()]

            # List of all airports for selector
            cur.execute("SELECT airport_code, airport_name, city, country FROM airports ORDER BY airport_code ASC;")
            all_airports = [{"code": r[0], "name": r[1], "city": r[2], "country": r[3]} for r in cur.fetchall()]

            conn.close()
            self._send_json({
                "status": "success",
                "airport": {
                    "code": airport_info[0] if airport_info else airport_code,
                    "name": airport_info[1] if airport_info else "",
                    "city": airport_info[2] if airport_info else "",
                    "country": airport_info[3] if airport_info else ""
                },
                "departures": departures,
                "arrivals": arrivals,
                "all_airports": all_airports
            })
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

    def handle_available_seats(self, query_params):
        try:
            flight_id = int(query_params.get("flight_id", ["1"])[0])
            conn = get_db_connection()
            cur = conn.cursor()
            
            cur.execute("SELECT aircraft_id FROM flights WHERE flight_id = ?;", (flight_id,))
            flight_row = cur.fetchone()
            if not flight_row:
                conn.close()
                self._send_json({"status": "error", "error": f"Flight {flight_id} not found."}, status_code=404)
                return

            aircraft_id = flight_row[0]

            # Get all seats for this aircraft
            cur.execute("SELECT seat_id, seat_number, seat_class FROM seats WHERE aircraft_id = ? ORDER BY seat_id ASC;", (aircraft_id,))
            seats = cur.fetchall()

            # Get occupied seat_ids for this specific flight
            cur.execute("SELECT seat_id, ticket_id, passenger_id FROM tickets WHERE flight_id = ? AND ticket_status != 'CANCELLED';", (flight_id,))
            occupied_map = {r[0]: {"ticket_id": r[1], "passenger_id": r[2]} for r in cur.fetchall()}

            result = []
            for s_id, s_num, s_cls in seats:
                is_occ = s_id in occupied_map
                base_fare = 15000.0 if s_cls == 'FIRST' else (8500.0 if s_cls == 'BUSINESS' else 4500.0)
                result.append({
                    "seat_id": s_id,
                    "seat_number": s_num,
                    "seat_class": s_cls,
                    "is_occupied": is_occ,
                    "fare": base_fare,
                    "ticket_id": occupied_map.get(s_id, {}).get("ticket_id") if is_occ else None
                })

            conn.close()
            self._send_json({"status": "success", "flight_id": flight_id, "seats": result})
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

    def handle_book_ticket(self, payload):
        first_name = payload.get("first_name", "").strip()
        last_name = payload.get("last_name", "").strip()
        email = payload.get("email", "").strip()
        passport = payload.get("passport_number", "").strip()
        flight_id = payload.get("flight_id")
        seat_id = payload.get("seat_id")
        fare_amount = payload.get("fare_amount", 5500.0)
        payment_method = payload.get("payment_method", "CREDIT_CARD")

        if not (first_name and last_name and email and passport and flight_id and seat_id):
            self._send_json({"status": "error", "error": "Missing required booking fields (passenger names, email, passport, flight, seat)."}, status_code=400)
            return

        t0 = time.perf_counter()
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # 1. Passenger
            cur.execute("SELECT passenger_id FROM passengers WHERE email = ? OR passport_number = ?;", (email, passport))
            p_row = cur.fetchone()
            if p_row:
                passenger_id = p_row[0]
            else:
                cur.execute("INSERT INTO passengers (first_name, last_name, email, passport_number) VALUES (?, ?, ?, ?);",
                            (first_name, last_name, email, passport))
                passenger_id = cur.lastrowid

            # 2. Check if seat is already occupied (Enforces UNIQUE constraint!)
            cur.execute("SELECT ticket_id FROM tickets WHERE flight_id = ? AND seat_id = ? AND ticket_status != 'CANCELLED';", (flight_id, seat_id))
            if cur.fetchone():
                conn.close()
                self._send_json({"status": "error", "error_type": "SEAT_ALREADY_OCCUPIED", "error": "This seat has already been booked by another passenger. Invariant UNIQUE (flight_id, seat_id) enforced!"}, status_code=200)
                return

            # 3. Create Booking (Random 6-character PNR)
            import random, string
            pnr = "AR" + ''.join(random.choices(string.digits, k=4))
            cur.execute("INSERT INTO bookings (booking_ref, passenger_id, booking_status) VALUES (?, ?, 'CONFIRMED');", (pnr, passenger_id))
            booking_id = cur.lastrowid

            # 4. Payment
            cur.execute("INSERT INTO payments (booking_id, amount_paid, payment_method, payment_status) VALUES (?, ?, ?, 'SUCCESS');",
                        (booking_id, float(fare_amount), payment_method))
            payment_id = cur.lastrowid

            # 5. Issue Ticket
            cur.execute("INSERT INTO tickets (booking_id, flight_id, seat_id, passenger_id, fare_amount, ticket_status) VALUES (?, ?, ?, ?, ?, 'ISSUED');",
                        (booking_id, int(flight_id), int(seat_id), int(passenger_id), float(fare_amount)))
            ticket_id = cur.lastrowid

            # Fetch seat number and flight number for confirmation
            cur.execute("SELECT seat_number, seat_class FROM seats WHERE seat_id = ?;", (seat_id,))
            seat_info = cur.fetchone()
            cur.execute("SELECT f.flight_number, r.origin_airport, r.dest_airport, f.scheduled_departure FROM flights f JOIN routes r ON f.route_id = r.route_id WHERE f.flight_id = ?;", (flight_id,))
            flight_info = cur.fetchone()

            conn.commit()
            conn.close()
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

            self._send_json({
                "status": "success",
                "message": f"Ticket #{ticket_id} booked successfully with PNR {pnr}!",
                "booking_ref": pnr,
                "ticket_id": ticket_id,
                "booking_id": booking_id,
                "payment_id": payment_id,
                "passenger": f"{first_name} {last_name}",
                "seat_number": seat_info[0] if seat_info else "",
                "seat_class": seat_info[1] if seat_info else "",
                "flight_number": flight_info[0] if flight_info else "",
                "route": f"{flight_info[1]} -> {flight_info[2]}" if flight_info else "",
                "departure": flight_info[3] if flight_info else "",
                "fare_paid": float(fare_amount),
                "execution_time_ms": elapsed_ms
            })
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({"status": "error", "error": str(e), "execution_time_ms": elapsed_ms}, status_code=500)

    def handle_checkin_baggage(self, payload):
        ticket_id = payload.get("ticket_id")
        weight_kg = float(payload.get("weight_kg", 0.0))

        if not ticket_id:
            self._send_json({"status": "error", "error": "Ticket ID is required for check-in."}, status_code=400)
            return

        t0 = time.perf_counter()
        try:
            conn = get_db_connection()
            cur = conn.cursor()

            # Check if ticket exists
            cur.execute("SELECT t.ticket_id, t.ticket_status, r.origin_airport FROM tickets t JOIN flights f ON t.flight_id = f.flight_id JOIN routes r ON f.route_id = r.route_id WHERE t.ticket_id = ?;", (ticket_id,))
            t_row = cur.fetchone()
            if not t_row:
                conn.close()
                self._send_json({"status": "error", "error": f"Ticket #{ticket_id} not found."}, status_code=404)
                return

            # Check if already checked in (Enforces 1:1 invariant!)
            cur.execute("SELECT checkin_id, boarding_pass FROM checkins WHERE ticket_id = ?;", (ticket_id,))
            existing_ci = cur.fetchone()
            if existing_ci:
                conn.close()
                self._send_json({"status": "error", "error_type": "CHECKIN_1_TO_1_VIOLATION", "error": f"Ticket #{ticket_id} has already been checked in (Boarding Pass: {existing_ci[1]}). 1:1 constraint UNIQUE(ticket_id) enforced!"}, status_code=200)
                return

            import random
            bp_code = f"BP-{t_row[2]}-{random.randint(1000, 9999)}"
            cur.execute("INSERT INTO checkins (ticket_id, boarding_pass) VALUES (?, ?);", (int(ticket_id), bp_code))
            checkin_id = cur.lastrowid

            # Baggage excess fee calculation: >15kg charged ₹500/kg
            excess_fee = 0.0
            baggage_id = None
            if weight_kg > 0:
                if weight_kg > 15.0:
                    excess_fee = round((weight_kg - 15.0) * 500.0, 2)
                cur.execute("INSERT INTO baggage (checkin_id, weight_kg, excess_fee) VALUES (?, ?, ?);",
                            (checkin_id, weight_kg, excess_fee))
                baggage_id = cur.lastrowid

            conn.commit()
            conn.close()
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)

            self._send_json({
                "status": "success",
                "message": f"Check-in complete! Boarding pass {bp_code} issued.",
                "checkin_id": checkin_id,
                "boarding_pass": bp_code,
                "ticket_id": ticket_id,
                "weight_kg": weight_kg,
                "excess_fee": excess_fee,
                "baggage_id": baggage_id,
                "execution_time_ms": elapsed_ms
            })
        except Exception as e:
            elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
            self._send_json({"status": "error", "error": str(e), "execution_time_ms": elapsed_ms}, status_code=500)

    def handle_reset(self):
        try:
            source_db = os.path.join(ROOT_DIR, "workbench", "arfom.db")
            if not os.path.exists(source_db):
                build_script = os.path.join(ROOT_DIR, "workbench", "build_database.py")
                import subprocess
                subprocess.run([sys.executable, build_script], check=True)

            import shutil
            shutil.copy2(source_db, DB_PATH)
            self._send_json({
                "status": "success",
                "message": "Database reset to pristine seed state with all 12 tables and 60+ sample records restored."
            })
        except Exception as e:
            self._send_json({"status": "error", "error": str(e)}, status_code=500)

def run_server(port=8000):
    socketserver.TCPServer.allow_reuse_address = True
    httpd = None

    try:
        httpd = socketserver.TCPServer(("", port), UnifiedProjectHandler)
        actual_port = port
    except OSError:
        for p in [8001, 8888, 3000]:
            try:
                httpd = socketserver.TCPServer(("", p), UnifiedProjectHandler)
                actual_port = p
                break
            except OSError:
                continue

    if not httpd:
        print(f"[!] Could not bind to port {port}. Please ensure no other process is using it.")
        return

    print(f"\n" + "="*75)
    print(f"  ARFOM-DB UNIFIED MASTER HTTP & REST SERVER RUNNING")
    print(f"  Student: Sanjyit Suresh Kumar (Roll No. 25WU0102243) • AIML Whales")
    print(f"  Root URL:        http://localhost:{actual_port}/")
    print(f"  Visuals Hub:     http://localhost:{actual_port}/visuals/index.html")
    print(f"  Review 2 Deck:   http://localhost:{actual_port}/Presentation-II/Presentation-II.html")
    print(f"  Review 3 App:    http://localhost:{actual_port}/3rd%20presentation/app/index.html")
    print(f"  Review 3 Slides: http://localhost:{actual_port}/3rd%20presentation/slides/presentation_iii_slides.html")
    print(f"  Workbench:       http://localhost:{actual_port}/workbench/index.html")
    print(f"  Lab Records:     http://localhost:{actual_port}/records/PRINTABLE_OUTPUTS.html")
    print(f"="*75 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[ARFOM-DB] Master server shut down cleanly.")

if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port_arg)
