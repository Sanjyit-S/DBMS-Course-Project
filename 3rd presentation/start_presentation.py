#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB PRESENTATION-III MASTER ONE-CLICK LAUNCHER (LOCALHOST:8000)
Starts the unified backend server and opens Chrome directly to the UI Portal.
===============================================================================
Author: Sanjyit Suresh Kumar (Roll No. 25WU0102243)
Project Title: Airline Reservation & Flight Operations Management System
Course: Database Management Systems (AIML Whales - Serial #18)
===============================================================================
"""

import os
import sys
import time
import subprocess
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
APP_DIR = os.path.join(BASE_DIR, "app")
SERVER_PY = os.path.join(ROOT_DIR, "server.py")

SLIDES_URL = "http://localhost:8000/3rd%20presentation/slides/presentation_iii_slides.html"
UI_URL = "http://localhost:8000/3rd%20presentation/app/index.html"

print("\n" + "="*75)
print("  ARFOM-DB | PRESENTATION-III LIVE LAUNCHER")
print("  Learner: Sanjyit Suresh Kumar (Roll No. 25WU0102243) - AIML Whales")
print("  Presentation Slot: Tuesday, Oct 6, 2026 | 11:50 am - 12:00 pm")
print("  Host: http://localhost:8000")
print("="*75)

# Verify database exists
db_file = os.path.join(APP_DIR, "arfom.db")
if not os.path.exists(db_file):
    print("[*] Preparing local database from seed...")
    source_db = os.path.join(ROOT_DIR, "workbench", "arfom.db")
    if os.path.exists(source_db):
        import shutil
        shutil.copy2(source_db, db_file)
        print("    [✓] Database copied successfully.")
    else:
        build_script = os.path.join(ROOT_DIR, "workbench", "build_database.py")
        subprocess.run([sys.executable, build_script], check=True)
        if os.path.exists(source_db):
            import shutil
            shutil.copy2(source_db, db_file)

# Ensure server is running
server_proc = None
import urllib.request
is_running = False
try:
    with urllib.request.urlopen("http://localhost:8000/api/status", timeout=1.0) as res:
        if res.status == 200:
            is_running = True
except Exception:
    is_running = False

if not is_running:
    print("[*] Starting Unified Master Server on port 8000...")
    server_proc = subprocess.Popen([sys.executable, SERVER_PY, "8000"])
    time.sleep(1.0)
else:
    print("[✓] Master Server is already running on http://localhost:8000")

# Launch Chrome to Slides and UI
print("[*] Opening Presentation Slides and Live UI Portal in Google Chrome...")
time.sleep(0.5)

try:
    subprocess.run(["open", "-a", "Google Chrome", SLIDES_URL])
    time.sleep(0.8)
    subprocess.run(["open", "-a", "Google Chrome", UI_URL])
except Exception:
    webbrowser.open(SLIDES_URL)
    webbrowser.open(UI_URL)

print("\n[✓] Browser launched with:")
print(f"    1. Slide Deck: {SLIDES_URL}")
print(f"    2. Live UI:    {UI_URL}")
print("\n" + "-"*75)
print("  BACKEND REST API SERVER RUNNING ON PORT 8000")
print("  Press Ctrl+C to stop the session when finished.")
print("-"*75 + "\n")

if server_proc:
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[ARFOM-DB] Server stopped cleanly. Good luck on your presentation!")
