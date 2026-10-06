#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB LIVE WORKBENCH LOCAL SERVER
Ultra-fast, zero-dependency HTTP server with live SQLite query execution.
===============================================================================
"""

import http.server
import socketserver
import json
import sqlite3
import os
import time
import urllib.parse
import webbrowser

PORT = 8000
DB_PATH = os.path.join(os.path.dirname(__file__), "arfom.db")
STATIC_DIR = os.path.dirname(__file__)

class WorkbenchHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS for local cross-origin file:// access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            resp = {"status": "online", "database": "arfom.db", "engine": "SQLite 3.x"}
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return
        elif parsed.path == "/" or parsed.path == "":
            self.path = "/index.html"

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/query":
            content_length = int(self.headers.get('Content-Length', 0))
            post_body = self.rfile.read(content_length).decode('utf-8')
            
            try:
                data = json.loads(post_body)
                sql = data.get("sql", "").strip()
            except Exception as e:
                self._send_json({"status": "error", "error": f"Invalid JSON payload: {str(e)}"}, status_code=400)
                return

            if not sql:
                self._send_json({"status": "error", "error": "Empty SQL query provided."}, status_code=400)
                return

            # Execute Query against SQLite DB
            t0 = time.perf_counter()
            try:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("PRAGMA foreign_keys = ON;")
                cur = conn.cursor()
                cur.execute(sql)

                if cur.description:
                    columns = [d[0] for d in cur.description]
                    rows = cur.fetchall()
                    conn.commit()
                    conn.close()
                    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                    self._send_json({
                        "status": "success",
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows),
                        "execution_time_ms": elapsed_ms
                    })
                else:
                    # Non-SELECT statement (INSERT, UPDATE, DELETE)
                    affected = cur.rowcount
                    conn.commit()
                    conn.close()
                    elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                    self._send_json({
                        "status": "success",
                        "columns": ["message", "rows_affected"],
                        "rows": [["Command executed successfully.", affected]],
                        "row_count": 1,
                        "execution_time_ms": elapsed_ms
                    })
            except Exception as e:
                elapsed_ms = round((time.perf_counter() - t0) * 1000, 2)
                self._send_json({
                    "status": "error",
                    "error": str(e),
                    "execution_time_ms": elapsed_ms
                }, status_code=200) # send 200 with error payload for friendly UI handling
            return

        self.send_error(404, "API endpoint not found")

    def _send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

def run_server():
    global PORT
    # Verify DB exists
    if not os.path.exists(DB_PATH):
        print("Database not found. Building database first...")
        import subprocess
        subprocess.run(["python3", os.path.join(STATIC_DIR, "build_database.py")], check=True)

    socketserver.TCPServer.allow_reuse_address = True
    httpd = None

    for attempt_port in [8000, 8001, 8080]:
        try:
            httpd = socketserver.TCPServer(("", attempt_port), WorkbenchHTTPRequestHandler)
            PORT = attempt_port
            break
        except OSError as e:
            if e.errno == 48:
                if attempt_port == 8000:
                    print(f"\n[NOTE] Port 8000 is already running and active!")
                    print(f"You can open your browser directly to: http://localhost:8000")
                continue
            else:
                raise e

    if not httpd:
        print(f"\n==================================================================")
        print(f" ARFOM-DB LIVE QUERY WORKBENCH SERVER IS ALREADY RUNNING!")
        print(f" Open your browser: http://localhost:8000/index.html")
        print(f" Or open directly:  workbench/index.html")
        print(f"==================================================================\n")
        return

    url = f"http://localhost:{PORT}/index.html"
    print(f"\n==================================================================")
    print(f" ARFOM-DB LIVE QUERY WORKBENCH SERVER RUNNING")
    print(f" Access URL: {url}")
    print(f" Press Ctrl+C to stop.")
    print(f"==================================================================\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down cleanly.")

if __name__ == "__main__":
    run_server()
