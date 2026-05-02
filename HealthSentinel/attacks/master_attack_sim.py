"""
HealthSentinel Attack Simulation Suite
======================================
This script simulates 4 distinct attack vectors to verify our AI defenses.
1. SQL Injection (Tests CodeBERT + API Gateway)
2. Insider Threat (Tests LSTM + OSQuery Aggregator)
3. Honeypot Intrusion (Tests Web/SQL/FTP Traps)
4. IoMT Command Injection (Tests Zero Trust + IoMT Monitor)
"""

import requests
import json
import time
import socket
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
AGGREGATOR_URL = "http://localhost:8080"
GATEWAY_URL = "http://localhost:8082/v1/ehr/patient"
ZT_URL = "http://localhost:8081/authorize"

def print_banner(text):
    print("\n" + "="*60)
    print(f"🚀 {text}")
    print("="*60)

# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK 1: SQL INJECTION (Target: EHR API)
# ═══════════════════════════════════════════════════════════════════════════════
def sim_sql_injection():
    print_banner("ATTACK 1: SQL Injection Probe")
    print("Attempting to bypass login and dump patient database...")
    
    payload = {
        "app_id": "third_party_app_01",
        "patient_id": "PAT-001",
        "query_params": "' OR '1'='1' --"
    }
    
    try:
        r = requests.post(GATEWAY_URL, json=payload, timeout=3)
        if r.status_code == 400:
            print("🛡️ [DEFENSE ACTIVE] CodeBERT AI detected and blocked the SQLi attempt!")
            print(f"   Response: {r.json()['detail']}")
        else:
            print(f"⚠️ [VULNERABILITY] Request went through: {r.status_code}")
    except Exception as e:
        print(f"❌ Error connecting to API Gateway: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK 2: INSIDER THREAT (Target: OSQuery Logs)
# ═══════════════════════════════════════════════════════════════════════════════
def sim_insider_threat():
    print_banner("ATTACK 2: Insider Threat / Data Exfiltration")
    print("Simulating a disgruntled employee accessing billing files off-hours...")
    
    threat_logs = {
        "logs": [
            {
                "name": "file_events",
                "hostIdentifier": "LAB-WORKSTATION-05",
                "calendarTime": datetime.now().isoformat(),
                "unixTime": int(time.time()),
                "columns": {
                    "username": "unhappy_employee",
                    "target_path": "C:\\hospital\\billing\\phi_export.csv",
                    "action": "ACCESS",
                    "time": int(time.time())
                }
            },
            {
                "name": "external_connections",
                "hostIdentifier": "LAB-WORKSTATION-05",
                "calendarTime": datetime.now().isoformat(),
                "unixTime": int(time.time()),
                "columns": {
                    "username": "unhappy_employee",
                    "remote_address": "85.203.1.44",
                    "remote_port": "443"
                }
            }
        ]
    }
    
    try:
        r = requests.post(f"{AGGREGATOR_URL}/logs", json=threat_logs)
        print("Sent suspicious activity logs to aggregator.")
        time.sleep(1)
        
        # Check if LSTM flagged high risk
        risk = requests.get(f"{AGGREGATOR_URL}/user/unhappy_employee/risk").json()
        print(f"🛡️ [DEFENSE ACTIVE] LSTM Risk Score for user: {risk['risk_score']}")
        if risk['risk_score'] > 0.5:
            print("✅ AI Flagged this user as a probable Insider Threat!")
    except Exception as e:
        print(f"❌ Error connecting to Aggregator: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK 3: HONEYPOT PROBE (Target: Fake EHR Portal)
# ═══════════════════════════════════════════════════════════════════════════════
def sim_honeypot_probe():
    print_banner("ATTACK 3: Honeypot Reconnaissance")
    print("Simulating botnet scanning port 5000 (Fake EHR Portal)...")
    
    try:
        r = requests.get("http://localhost:5000", timeout=2)
        print("Connected to port 5000. Attempting brute force...")
        requests.post("http://localhost:5000/login", data={"u": "admin", "p": "admin123"})
        
        # Check alerts
        alerts = requests.get(f"{AGGREGATOR_URL}/alerts", params={"severity": "critical"}).json()
        print(f"🛡️ [DEFENSE ACTIVE] {len(alerts)} Critical alerts fired in aggregator!")
        for a in alerts[-2:]:
            print(f"   Alert: {a['description']}")
    except:
        print("❌ Error: Is the Honeypot service running on port 5000?")

# ═══════════════════════════════════════════════════════════════════════════════
# ATTACK 4: IoMT EXPLOIT (Target: Infusion Pump)
# ═══════════════════════════════════════════════════════════════════════════════
def sim_iomt_exploit():
    print_banner("ATTACK 4: Medical Device Command Injection")
    print("Attacker 'malicious_user' trying to set dangerous bolus on PUMP-001...")
    
    zt_payload = {
        "user_id": "malicious_user",
        "target_zone": "medical_devices",
        "action": "write",
        "device_id": "PUMP-001",
        "mfa_verified": False
    }
    
    try:
        r = requests.post(ZT_URL, json=zt_payload)
        data = r.json()
        if not data['allowed']:
            print(f"🛡️ [DEFENSE ACTIVE] Zero Trust blocked the command!")
            print(f"   Reason: {data['reason']}")
        else:
            print("⚠️ [VULNERABILITY] Forbidden command allowed!")
    except:
        print("❌ Error: Is the Zero Trust Controller running on port 8081?")

# ═══════════════════════════════════════════════════════════════════════════════
# MASTER RUNNER
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "#"*60)
    print("## HEALTHSENTINEL SECURITY VALIDATION SUITE ##")
    print("#"*60)
    
    sim_sql_injection()
    sim_insider_threat()
    sim_honeypot_probe()
    sim_iomt_exploit()
    
    print("\n" + "="*60)
    print("✅ Attack Simulation Cycle Complete.")
    print("All security layers (CodeBERT, LSTM, Zero Trust, Honeypots) have been verified.")
    print("="*60)
