"""
HealthSentinel IoMT Device Monitor (Day 10)
==========================================
Simulates an edge agent running on or alongside medical devices.
Monitors protocol commands (e.g., HL7, DICOM, Proprietary PUMP commands).

Detects:
1. Critical Command Spikes (e.g., Bolus dose frequency)
2. Unauthorized Remote Tuning
3. Firmware Integrity Fluctuations
"""

import time
import random
import requests
import json
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
AGGREGATOR_URL = "http://localhost:8080/logs"
ZT_URL = "http://localhost:8081/authorize"

DEVICE_ID = "PUMP-001"
DEVICE_TYPE = "Infusion Pump"

class IoMTMonitor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.risk_threshold = 0.15
        self.fingerprint = self.fingerprint_device()
        
    def fingerprint_device(self):
        """Analyze hardware and network signatures to create a device fingerprint."""
        # Simulated deep packet inspection / hardware signature
        return {
            "mac_vendor": "Baxter Healthcare",
            "protocol_stack": ["TCP/IP", "Proprietary_Pump_v2", "HL7"],
            "packet_timing_profile": "constant_interval_300ms",
            "os_signature": "Embedded_RTOS_v6.4",
            "trust_hash": hashlib.sha256(f"{self.device_id}_HARDWARE_SECRET".encode()).hexdigest()[:12]
        }

    def verify_fingerprint(self):
        """Verify the current device state against the stored fingerprint."""
        current = self.fingerprint_device()
        if current["trust_hash"] != self.fingerprint["trust_hash"]:
            self.log_anomaly("DEVICE_SPOOFING", "Device fingerprint mismatch - potential rogue device!")
            return False
        return True

import hashlib
        
    def check_authorization(self, user_id, action):
        """Verify with Zero Trust before allowing a command."""
        payload = {
            "user_id": user_id,
            "target_zone": "medical_devices",
            "action": action,
            "device_id": self.device_id,
            "mfa_verified": True # Assume medical staff use hardware keys
        }
        try:
            resp = requests.post(ZT_URL, json=payload, timeout=2)
            return resp.json().get("allowed", False)
        except:
            return False

    def log_anomaly(self, event_type, details, severity="critical"):
        """Report anomalies to the dashboard aggregator."""
        log = {
            "logs": [{
                "name": "iomt_anomaly",
                "hostIdentifier": f"IOT-{self.device_id}",
                "calendarTime": datetime.now().isoformat(),
                "unixTime": int(time.time()),
                "columns": {
                    "device_id": self.device_id,
                    "event_type": event_type,
                    "details": details,
                    "severity": severity
                }
            }]
        }
        try:
            requests.post(AGGREGATOR_URL, json=log)
            print(f"🚨 [IoMT ALERT] {event_type}: {details}")
        except:
            print(f"⚠️ Aggregator down. Locally logged: {event_type}")

    def monitor_loop(self):
        """Simulate command monitoring."""
        print(f"🏥 Monitoring {DEVICE_TYPE} ({self.device_id})...")
        
        while True:
            # Simulate a command coming in
            # Most commands are normal
            if random.random() < 0.95:
                # Normal drip rate adjustment by authorized nurse
                if self.check_authorization("nurse_authorized", "write"):
                    # print(f"  ✓ Command: Authorized set_rate")
                    pass
            else:
                # SIMULATE ATTACK 1: Unauthorized user tries to increase Dose
                print(f"⚠️ [IoMT] Intercepting suspicious command: set_bolus_high")
                if not self.check_authorization("attacker_001", "write"):
                    self.log_anomaly("UNAUTHORIZED_CONTROL", "Attacker attempted to set high bolus dose")
                
                # SIMULATE ATTACK 2: Unusual frequency of heartbeat commands
                # (Would be caught by CNN in Day 11)
                if random.random() < 0.3:
                    self.log_anomaly("ANOMALOUS_TRAFFIC_PATTERN", "Frequent small packet bursts detected from pump")
            
            time.sleep(3)

if __name__ == "__main__":
    monitor = IoMTMonitor(DEVICE_ID)
    monitor.monitor_loop()
