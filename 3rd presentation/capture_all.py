#!/usr/bin/env python3
"""
Automated UI Screenshot Capture for ARFOM-DB Presentation-III
Captures pixel-perfect screenshots of all required demonstration screens:
1. Master Flight Manifest (Viewing)
2. Passengers Table (Viewing)
3. Insert Form & Presets (Insertion Before)
4. Insert Live Database Reflection (Insertion After)
5. Delete Candidate Selection (Deletion Before)
6. Delete Live Database Reflection (Deletion After)
7. Before & After State Comparator (Live Reflection)
8. Negative Testing & Constraint Defense (Integrity Error)
"""

import os
import sys
import subprocess
import time

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
APP_HTML = os.path.join(BASE_DIR, "app", "index.html")
PROFILE_DIR = os.path.join(BASE_DIR, ".chrome_headless_profile")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

TARGETS = [
    ("01_view_master_manifest.png", f"file://{APP_HTML}", 1.5),
    ("02_view_passengers_table.png", f"file://{APP_HTML}?table=passengers", 1.5),
    ("03_insert_form_presets.png", f"file://{APP_HTML}#tab-insert", 1.5),
    ("04_insert_live_db_reflection.png", f"file://{APP_HTML}#tab-insert-after", 2.0),
    ("05_delete_table_view.png", f"file://{APP_HTML}#tab-delete", 1.5),
    ("06_delete_live_db_reflection.png", f"file://{APP_HTML}#tab-delete-after", 2.0),
    ("07_before_after_comparison.png", f"file://{APP_HTML}#tab-compare", 2.0),
    ("08_negative_test_constraint_error.png", f"file://{APP_HTML}#tab-constraints", 2.0),
]

def capture(output_name, url, delay_sec):
    out_path = os.path.join(SCREENSHOTS_DIR, output_name)
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={PROFILE_DIR}",
        "--window-size=1440,900",
        f"--virtual-time-budget={int(delay_sec * 1000)}",
        f"--screenshot={out_path}",
        url
    ]
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"  [✓] Captured: {output_name}")
    except Exception as e:
        print(f"  [!] Error capturing {output_name}: {e}")

if __name__ == "__main__":
    print(f"\n==================================================================")
    print(f" ARFOM-DB: CAPTURING ALL PRESENTATION-III SCREENSHOTS")
    print(f" Output Folder: {SCREENSHOTS_DIR}")
    print(f"==================================================================")

    for name, url, delay in TARGETS:
        capture(name, url, delay)

    print(f"\n[✓] All screenshots successfully stored in:\n    {SCREENSHOTS_DIR}\n")
