"""
HealthSentinel USB/DLP Monitor (Day 14)
=======================================
Simulates Data Loss Prevention (DLP) by monitoring for unauthorized 
USB insertion and blocking large file transfers from the EHR zone.
"""

import time
import requests
import os
from datetime import datetime

AGGREGATOR_URL = "http://localhost:8080/logs"

class DLPServer:
    def __init__(self):
        self.blocked_ips = set()
        self.sensitive_files_accessed = 0

    def log_dlp_incident(self, event_type, details, severity="high"):
        now = datetime.now().isoformat()
        log = {
            "logs": [{
                "name": "dlp_incident",
                "hostIdentifier": "DLP-AGENT-01",
                "calendarTime": now,
                "unixTime": int(time.time()),
                "columns": {
                    "event_type": event_type,
                    "details": details,
                    "severity": severity
                }
            }]
        }
        try:
            requests.post(AGGREGATOR_URL, json=log, timeout=1)
            print(f"🛑 [DLP ALERT] {event_type}: {details}")
        except:
            pass

    def simulate_monitor(self):
        print("🛡️ HealthSentinel DLP Agent is active and monitoring USB/File activity...")
        
        # Simulation Logic
        try:
            while True:
                # Simulate a random USB insertion event
                import random
                if random.random() < 0.1:
                    self.log_dlp_incident("UNAUTHORIZED_USB", "Non-Whitelisted USB Drive Detected (ID: 0x5544)")
                
                # Simulate a large file transfer attempts
                if random.random() < 0.05:
                    self.log_dlp_incident("MASS_DATA_EXFIL", "User attempted to copy 2GB of .phi files to external storage")
                
                time.sleep(5)
        except KeyboardInterrupt:
            print("🛑 DLP Monitor stopped.")

if __name__ == "__main__":
    dlp = DLPServer()
    dlp.simulate_monitor()
