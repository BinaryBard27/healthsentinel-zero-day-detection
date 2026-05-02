"""
Verification Script for Day 9: Third-Party Security
=================================================
Tests:
1. Static Analysis of a suspicious script
2. API Gateway with Zero Trust & SQLi Guarding
"""

import os
import requests
import json
import time

# ═══════════════════════════════════════════════════════════════════════════════
# 1. TEST STATIC ANALYZER
# ═══════════════════════════════════════════════════════════════════════════════
print("🔍 Testing Static Analyzer...")
from static_analyzer import StaticAnalyzer

malicious_code = """
import os
import subprocess
import socket

# Suspicious IP
remote_server = "185.123.45.67"

def exploit():
    # Dangerous eval
    eval("print('system compromised')")
    # Subprocess call
    subprocess.run(["rm", "-rf", "/"])
"""

with open("dangerous_app.py", "w") as f:
    f.write(malicious_code)

analyzer = StaticAnalyzer()
report = analyzer.analyze_file("dangerous_app.py")
print(f"Report Status: {report['status']}")
print(f"Risk Score: {report['risk_score']:.2f}")
print(f"Issues Found: {len(report['issues'])}")
for issue in report['issues']:
    print(f"  - [{issue['severity'].upper()}] {issue['detail']}")

os.remove("dangerous_app.py")
print("-" * 30)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. TEST API GATEWAY
# ═══════════════════════════════════════════════════════════════════════════════
print("\n🛡️ Testing API Gateway Guarding...")

GATEWAY_URL = "http://localhost:8082/v1/ehr/patient"

def test_gateway_call(app_id, patient_id, query_params=""):
    payload = {
        "app_id": app_id,
        "patient_id": patient_id,
        "query_params": query_params
    }
    print(f"Accessing {patient_id} with query: '{query_params}'...")
    try:
        resp = requests.post(GATEWAY_URL, json=payload, timeout=3)
        if resp.status_code == 200:
            print(f"  ✅ SUCCESS: {resp.json().get('status')}")
            print(f"  Message: {resp.json().get('guarded_by')}")
        else:
            print(f"  ❌ DENIED ({resp.status_code}): {resp.json().get('detail')}")
    except Exception as e:
        print(f"  ❌ Connection Error: {e}")
    print("-" * 30)

# Wait for gateway to start
time.sleep(2)

# Case A: Legitimate Request (Assuming ZT Controller is running)
test_gateway_call("valid_partner_app", "PAT-12345")

# Case B: SQL Injection Attack
test_gateway_call("valid_partner_app", "PAT-12345", query_params="' OR '1'='1")

# Case C: Zero Trust Block (App not authorized)
test_gateway_call("unknown_malicious_app", "PAT-99999")
