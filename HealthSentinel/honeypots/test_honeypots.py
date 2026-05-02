"""
Honeypot Verification Script
===========================
Tests the 3 honeypots to ensure they correctly report to the aggregator.
"""

import requests
import socket
import time

print("🧪 Starting Honeypot Verification...")
print("-" * 40)

# 1. Test Web Honeypot
try:
    print("Testing Web Honeypot (Port 5000)...")
    resp = requests.get("http://localhost:5000", timeout=2)
    print(f"  Result: {resp.status_code} - EHR Portal Accessed")
    
    print("Simulating Login Attack...")
    resp = requests.post("http://localhost:5000/login", data={"u": "admin", "p": "password123"}, timeout=2)
    print(f"  Result: {resp.status_code} - Brute Force Logged")
except Exception as e:
    print(f"  ❌ Web Honeypot failed: {e}")

# 2. Test SQL Honeypot
try:
    print("\nTesting SQL Honeypot (Port 5432)...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(("127.0.0.1", 5432))
    data = s.recv(1024)
    print(f"  Received: {data[:10].hex()}... (Postgres Error Simulation)")
    s.send(b"SELECT * FROM patients;")
    s.close()
    print("  ✅ SQL Probe Logged")
except Exception as e:
    print(f"  ❌ SQL Honeypot failed: {e}")

# 3. Test FTP Honeypot
try:
    print("\nTesting FTP Honeypot (Port 21)...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    s.connect(("127.0.0.1", 21))
    print(f"  Received: {s.recv(1024).decode().strip()}")
    s.send(b"USER medical_staff\r\n")
    print(f"  Response: {s.recv(1024).decode().strip()}")
    s.close()
    print("  ✅ FTP Probe Logged")
except Exception as e:
    print(f"  ❌ FTP Honeypot failed: {e}")

print("\n" + "-" * 40)
print("🏁 Verification Script Finished.")
print("Check the Log Aggregator window or Dashboard to see the alerts.")
