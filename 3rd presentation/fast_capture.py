#!/usr/bin/env python3
"""
Fast Chrome Headless Screenshot Capture for ARFOM-DB Presentation-III
Kills Chrome immediately after the PNG file is written to avoid macOS Mach port hang.
"""

import os
import sys
import subprocess
import time

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
APP_HTML = os.path.join(BASE_DIR, "app", "index.html")
PROFILE_DIR = os.path.join(BASE_DIR, ".chrome_fast_profile")

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(PROFILE_DIR, exist_ok=True)

TARGETS = [
    ("01_view_master_manifest.png", f"file://{APP_HTML}"),
    ("02_view_passengers_table.png", f"file://{APP_HTML}?table=passengers"),
    ("03_insert_form_presets.png", f"file://{APP_HTML}#tab-insert"),
    ("04_insert_live_db_reflection.png", f"file://{APP_HTML}#tab-insert-after"),
    ("05_delete_table_view.png", f"file://{APP_HTML}#tab-delete"),
    ("06_delete_live_db_reflection.png", f"file://{APP_HTML}#tab-delete-after"),
    ("07_before_after_comparison.png", f"file://{APP_HTML}#tab-compare"),
    ("08_negative_test_constraint_error.png", f"file://{APP_HTML}#tab-constraints"),
]

def capture_one(name, url):
    out_file = os.path.join(SCREENSHOTS_DIR, name)
    if os.path.exists(out_file):
        os.remove(out_file)

    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--user-data-dir={PROFILE_DIR}",
        "--window-size=1440,900",
        f"--screenshot={out_file}",
        url
    ]

    p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t0 = time.time()
    success = False

    while time.time() - t0 < 10.0:
        if os.path.exists(out_file) and os.path.getsize(out_file) > 50000:
            success = True
            time.sleep(0.8)
            break
        time.sleep(0.3)

    try:
        p.kill()
        p.wait(timeout=1.0)
    except Exception:
        pass

    if success:
        size_kb = os.path.getsize(out_file) // 1024
        print(f"  [✓] Captured {name} ({size_kb} KB)")
    else:
        print(f"  [!] Timeout or failed: {name}")

if __name__ == "__main__":
    print(f"\n==================================================================")
    print(f" FAST CAPTURE OF ALL 8 PRESENTATION-III SCREENSHOTS")
    print(f" Output Folder: {SCREENSHOTS_DIR}")
    print(f"==================================================================")

    for name, url in TARGETS:
        capture_one(name, url)

    print("\n[✓] Capture process complete!\n")
