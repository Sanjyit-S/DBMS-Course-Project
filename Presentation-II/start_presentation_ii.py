#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB PRESENTATION-II MASTER ONE-CLICK LAUNCHER (LOCALHOST:8000)
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

SLIDES_URL = "http://localhost:8000/Presentation-II/Presentation-II.html"
VISUALS_URL = "http://localhost:8000/visuals/index.html"

print("\n" + "="*75)
print("  ARFOM-DB | PRESENTATION-II (REVIEW 2) MASTER LAUNCHER")
print("  Learner: Sanjyit Suresh Kumar (Roll No. 25WU0102243) - AIML Whales")
print("  Scope: Relational Architecture, 3NF Normalization, Integrity & SQL")
print("  Host: http://localhost:8000 (All Visuals & Schema Diagrams Active)")
print("="*75)

# Ensure server is running
server_script = os.path.join(ROOT_DIR, "server.py")
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
    server_proc = subprocess.Popen([sys.executable, server_script, "8000"])
    time.sleep(1.0)
else:
    print("[✓] Master Server is already running on http://localhost:8000")

print("\n[*] Opening Review 2 Artifacts in Google Chrome on localhost:8000...")
try:
    subprocess.run(["open", "-a", "Google Chrome", SLIDES_URL])
    time.sleep(0.5)
    subprocess.run(["open", "-a", "Google Chrome", VISUALS_URL])
except Exception:
    webbrowser.open(SLIDES_URL)
    webbrowser.open(VISUALS_URL)

print("\n[✓] Review 2 Launched Successfully on localhost:8000!")
print(f"    1. Slide Deck (16:9): {SLIDES_URL}")
print(f"    2. Visuals Hub:       {VISUALS_URL}")
print(f"    3. PDF Deck:          {os.path.join(BASE_DIR, 'Presentation-II.pdf')}")
print(f"    4. Playbook Guide:    {os.path.join(BASE_DIR, 'PRESENTATION_II_PLAYBOOK.md')}")
print("\n[Tip] For on-the-spot terminal query execution, run:")
print("      python3 demo_runner.py --demo\n")

if server_proc:
    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[ARFOM-DB] Server stopped cleanly.")
