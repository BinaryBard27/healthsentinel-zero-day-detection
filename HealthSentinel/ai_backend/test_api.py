"""
Quick Test Script for AI Backend
=================================
Tests all four model endpoints, SHAP explain endpoints, and rate limiting.
"""

import requests
import json
import random

API_BASE = "http://localhost:8000"

print("\n" + "="*80)
print(" " * 25 + "AI Backend Test Suite")
print("="*80)

# Test 1: Health Check
print("\n[1/8] Testing health endpoint...")
try:
    r = requests.get(f"{API_BASE}/api/health")
    data = r.json()
    print(f"✅ Server Status: {data['status']}")
    print(f"   Models Loaded: {data['models_loaded']}")
    for model, loaded in data['models'].items():
        status = "✅" if loaded else "❌"
        print(f"   {status} {model}")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Ransomware Detection
print("\n[2/8] Testing ransomware detection...")
try:
    payload = {
        "file_features": [0.5, 0.3, 0.8, 0.1, 0.9, 0.2, 0.7, 0.4, 0.6, 0.3],
        "file_name": "test_file.exe"
    }
    r = requests.post(f"{API_BASE}/api/detect/ransomware", json=payload)
    data = r.json()
    print(f"✅ Prediction: {data['prediction']}")
    print(f"   Confidence: {data['confidence']:.2%}")
    print(f"   Risk Level: {data['risk_level']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Phishing Detection
print("\n[3/8] Testing phishing detection...")
try:
    payload = {
        "sender": "urgent@suspicious-domain.xyz",
        "subject": "URGENT: Verify Your Account NOW!",
        "message": "Your account will be suspended! Click here: http://bit.ly/verify123",
        "urls": ["http://bit.ly/verify123"]
    }
    r = requests.post(f"{API_BASE}/api/detect/phishing", json=payload)
    data = r.json()
    print(f"✅ Action: {data['action']}")
    print(f"   Risk Level: {data['risk_level']}")
    print(f"   Confidence: {data['confidence']:.2%}")
    print(f"   Reasons: {', '.join(data['reasons'][:2])}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: SQL Injection Detection
print("\n[4/8] Testing SQL injection detection...")
try:
    payload = {
        "query": "SELECT * FROM users WHERE id = '1' OR '1'='1'"
    }
    r = requests.post(f"{API_BASE}/api/detect/sql-injection", json=payload)
    data = r.json()
    print(f"✅ Is Injection: {data['is_injection']}")
    print(f"   Confidence: {data['confidence']:.2%}")
    print(f"   Risk Level: {data['risk_level']}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Insider Threat Detection
print("\n[5/8] Testing insider threat detection...")
try:
    sequence = [[random.random() for _ in range(12)] for _ in range(30)]
    payload = {
        "user_id": "test_user",
        "sequence_data": sequence
    }
    r = requests.post(f"{API_BASE}/api/detect/insider-threat", json=payload)
    data = r.json()
    print(f"✅ Is Anomaly: {data['is_anomaly']}")
    print(f"   Risk Score: {data['risk_score']:.2%}")
    print(f"   Risk Level: {data['risk_level']}")
    print(f"   Reconstruction Error: {data['reconstruction_error']:.6f}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: SHAP Explain - Ransomware
print("\n[6/8] Testing SHAP explanation for ransomware...")
try:
    payload = {
        "file_features": [0.5, 0.3, 0.8, 0.1, 0.9, 0.2, 0.7, 0.4, 0.6, 0.3],
        "file_name": "test_file.exe"
    }
    r = requests.post(f"{API_BASE}/api/explain/ransomware", json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"✅ SHAP values: {len(data['shap_values'])} features")
        print(f"   Base value: {data['base_value']:.4f}")
        print(f"   Prediction: {data['prediction']}")
        print(f"   Top feature: {data['top_features'][0]['name']} "
              f"(impact={data['top_features'][0]['impact']}, value={data['top_features'][0]['value']:.4f})")
    else:
        print(f"⚠️  Status {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 7: SHAP Explain - SQL Injection
print("\n[7/8] Testing SHAP explanation for SQL injection...")
try:
    payload = {"query": "SELECT * FROM users WHERE id = '1' OR '1'='1'"}
    r = requests.post(f"{API_BASE}/api/explain/sql-injection", json=payload)
    if r.status_code == 200:
        data = r.json()
        print(f"✅ Token-level SHAP: {len(data['shap_values'])} tokens analyzed")
        print(f"   Prediction: {data['prediction']}")
        if data['top_features']:
            top = data['top_features'][0]
            print(f"   Most influential token: '{top['name']}' ({top['impact']}, {top['value']:.4f})")
    else:
        print(f"⚠️  Status {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 8: Rate Limiter
print("\n[8/8] Testing rate limiter (sending 35 requests to /api/detect/ransomware)...")
try:
    payload = {
        "file_features": [0.5, 0.3, 0.8, 0.1, 0.9, 0.2, 0.7, 0.4, 0.6, 0.3],
        "file_name": "rate_test.exe"
    }
    throttled = False
    for i in range(1, 36):
        r = requests.post(f"{API_BASE}/api/detect/ransomware", json=payload)
        if r.status_code == 429:
            print(f"✅ Rate limit triggered at request #{i} → HTTP 429 Too Many Requests")
            throttled = True
            break
    if not throttled:
        print("⚠️  Rate limit was NOT triggered in 35 requests (limit may be > 30/min or IP-based windowing differs)")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)
print(" " * 25 + "All Tests Complete!")
print("="*80 + "\n")
