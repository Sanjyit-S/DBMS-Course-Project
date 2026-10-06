#!/usr/bin/env python3
"""
===============================================================================
ARFOM-DB UNIFIED PRESENTATION LAUNCHER (REVIEWS 2 & 3 • LOCALHOST:8000)
===============================================================================
Author: Sanjyit Suresh Kumar (Roll No. 25WU0102243)
Course: Database Management Systems (25TU03MJM0) • AIML Whales (Serial #18)
Presentation Slot: Tuesday, 6 October 2026 | 11:50 AM – 12:00 PM
===============================================================================
"""

import os
import sys
import time
import subprocess
import webbrowser

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVER_PY = os.path.join(BASE_DIR, "server.py")

R2_SLIDES = "http://localhost:8000/Presentation-II/Presentation-II.html"
VISUALS_HUB = "http://localhost:8000/visuals/index.html"
R3_SLIDES = "http://localhost:8000/3rd%20presentation/slides/presentation_iii_slides.html"
R3_UI = "http://localhost:8000/3rd%20presentation/app/index.html"

def ensure_server_running():
    import urllib.request
    try:
        with urllib.request.urlopen("http://localhost:8000/api/status", timeout=1.0) as res:
            if res.status == 200:
                return None
    except Exception:
        pass

    print("[*] Starting Master Server on port 8000 (localhost)...")
    proc = subprocess.Popen([sys.executable, SERVER_PY, "8000"])
    time.sleep(1.0)
    return proc

def print_banner():
    print("\n" + "="*75)
    print("  AIRLINE RESERVATION & FLIGHT OPERATIONS MANAGEMENT SYSTEM (ARFOM-DB)")
    print("  Unified Presentation Suite • Learner: Sanjyit Suresh Kumar (25WU0102243)")
    print("  Host: http://localhost:8000 (All Visuals, Iframes & Live DB Active)")
    print("  Tuesday, 6 October 2026 • Serial #18 (AIML Whales)")
    print("="*75)
    print("  [1] Review 2 Presentation (Relational Modeling, 3NF & SQL Queries)")
    print("  [2] Review 3 Presentation (Live UI, Viewing, Insert, Delete & Mobile QR)")
    print("  [3] Launch BOTH Back-to-Back (Full Tuesday Review Defense)")
    print("  [4] Run Terminal SQL Viva Demo Harness (demo_runner.py)")
    print("  [5] Exit")
    print("="*75)

def launch_review_2():
    proc = ensure_server_running()
    print("\n[*] Opening Review 2 on localhost:8000 in Google Chrome...")
    try:
        subprocess.run(["open", "-a", "Google Chrome", R2_SLIDES])
        time.sleep(0.5)
        subprocess.run(["open", "-a", "Google Chrome", VISUALS_HUB])
    except Exception:
        webbrowser.open(R2_SLIDES)
        webbrowser.open(VISUALS_HUB)

    print("\n[[OK]] Review 2 Launched Successfully on localhost:8000!")
    print(f"    1. Slide Deck: {R2_SLIDES}")
    print(f"    2. Visuals Hub: {VISUALS_HUB}")
    if proc:
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n[ARFOM-DB] Server stopped.")

def launch_review_3():
    proc = ensure_server_running()
    print("\n[*] Opening Review 3 on localhost:8000 in Google Chrome...")
    try:
        subprocess.run(["open", "-a", "Google Chrome", R3_SLIDES])
        time.sleep(0.8)
        subprocess.run(["open", "-a", "Google Chrome", R3_UI])
    except Exception:
        webbrowser.open(R3_SLIDES)
        webbrowser.open(R3_UI)

    print("\n[[OK]] Review 3 Launched Successfully on localhost:8000!")
    print(f"    1. Slide Deck: {R3_SLIDES}")
    print(f"    2. Live UI:    {R3_UI}")
    if proc:
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n[ARFOM-DB] Server stopped.")

def launch_both():
    proc = ensure_server_running()
    print("\n[*] Opening BOTH Reviews 2 & 3 on localhost:8000 in Google Chrome...")
    try:
        subprocess.run(["open", "-a", "Google Chrome", R2_SLIDES])
        time.sleep(0.4)
        subprocess.run(["open", "-a", "Google Chrome", VISUALS_HUB])
        time.sleep(0.4)
        subprocess.run(["open", "-a", "Google Chrome", R3_SLIDES])
        time.sleep(0.4)
        subprocess.run(["open", "-a", "Google Chrome", R3_UI])
    except Exception:
        webbrowser.open(R2_SLIDES)
        webbrowser.open(VISUALS_HUB)
        webbrowser.open(R3_SLIDES)
        webbrowser.open(R3_UI)

    print("\n[[OK]] Chrome opened with 4 localhost:8000 tabs:")
    print(f"    Tab 1: Review 2 Slides       ({R2_SLIDES})")
    print(f"    Tab 2: Review 2 Visuals Hub  ({VISUALS_HUB})")
    print(f"    Tab 3: Review 3 Slides       ({R3_SLIDES})")
    print(f"    Tab 4: Review 3 Live UI      ({R3_UI})")
    print("\n[*] Master Server running on port 8000. Press Ctrl+C when presentation is done.\n")
    if proc:
        try:
            proc.wait()
        except KeyboardInterrupt:
            print("\n[[OK]] Presentation session completed cleanly!")

def run_cli_demo():
    print("\n[*] Running Interactive Terminal Viva Harness...")
    demo_script = os.path.join(BASE_DIR, "demo_runner.py")
    subprocess.run([sys.executable, demo_script, "--demo"])

def main():
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["2", "review2", "r2"]:
            launch_review_2()
            return
        elif arg in ["3", "review3", "r3"]:
            launch_review_3()
            return
        elif arg in ["both", "all"]:
            launch_both()
            return
        elif arg in ["demo", "cli"]:
            run_cli_demo()
            return

    while True:
        print_banner()
        choice = input("Enter option [1-5]: ").strip()
        if choice == "1":
            launch_review_2()
            break
        elif choice == "2":
            launch_review_3()
            break
        elif choice == "3":
            launch_both()
            break
        elif choice == "4":
            run_cli_demo()
            break
        elif choice == "5":
            print("\nExiting. Good luck tomorrow!\n")
            break
        else:
            print("\n[!] Invalid choice. Please enter 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main()
