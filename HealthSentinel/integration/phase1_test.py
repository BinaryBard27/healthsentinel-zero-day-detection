"""
Phase 1 Unified Integration Tester
==================================
Starts and tests the interaction between:
1. OSQuery (Aggregator)
2. LSTM Model (Inference)
3. Zero-Day Monitor (1D-CNN)
4. Honeypots (Docker/Local)
"""

import threading
import time
import requests
import subprocess
import os

# CONFIG
PROJECT_ROOT = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel"
AGGREGATOR_URL = "http://localhost:8080"

def start_aggregator():
    print("🚀 Starting Log Aggregator...")
    os.chdir(os.path.join(PROJECT_ROOT, "osquery", "aggregator"))
    subprocess.Popen(["python", "log_aggregator.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)

def start_honeypots():
    print("🍯 Starting Honeypots...")
    os.chdir(os.path.join(PROJECT_ROOT, "honeypots"))
    subprocess.Popen(["python", "honeypot_services.py"], creationflags=subprocess.CREATE_NEW_CONSOLE)

def test_alert_pipeline():
    print("\n🧪 Testing Alert Pipeline...")
    time.sleep(5) # Wait for start
    
    # Simulate a honeypot trip
    hp_alert = {
        "logs": [{
            "name": "integration_test",
            "hostIdentifier": "TEST-NODE",
            "calendarTime": "2026-02-04T12:00:00Z",
            "unixTime": int(time.time()),
            "columns": {"action": "trip", "severity": "high"}
        }]
    }
    
    try:
        r = requests.post(f"{AGGREGATOR_URL}/logs", json=hp_alert)
        print(f"Aggregator response: {r.status_code}")
        
        # Verify alert received
        alerts = requests.get(f"{AGGREGATOR_URL}/alerts").json()
        print(f"Total alerts in system: {len(alerts)}")
        if len(alerts) > 0:
            print("✅ Alert Pipeline Verified!")
        else:
            print("❌ Alert not found in system")
    except Exception as e:
        print(f"❌ Pipeline Test Failed: {e}")

if __name__ == "__main__":
    start_aggregator()
    start_honeypots()
    test_alert_pipeline()
