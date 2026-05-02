"""
Zero Trust Verification Script
==============================
Tests the Zone Controller's ability to block access based on AI risk scores.
"""

import requests
import json

ZT_URL = "http://localhost:8081/authorize"

def test_access(user, zone, mfa=True):
    payload = {
        "user_id": user,
        "target_zone": zone,
        "action": "read",
        "device_id": "WS-LAPTOP-01",
        "mfa_verified": mfa
    }
    
    print(f"Checking access for {user} -> {zone}...")
    try:
        resp = requests.post(ZT_URL, json=payload)
        data = resp.json()
        status = "✅ ALLOWED" if data['allowed'] else "❌ BLOCKED"
        print(f"  Result: {status}")
        print(f"  AI risk: {data['risk_score']:.2f}")
        print(f"  Reason: {data['reason']}")
        print("-" * 30)
    except:
        print("❌ Error: Is the Zone Controller running on port 8081?")

if __name__ == "__main__":
    # Test cases
    print("🧪 Zero Trust Policy Testing\n")
    
    # Case 1: Low risk user accessing Public zone
    test_access("dr_smith", "public")
    
    # Case 2: User accessing EHR without MFA
    test_access("dr_smith", "ehr", mfa=False)
    
    # Case 3: High risk user (should be blocked by AI Score)
    # Note: For this to work live, the Log Aggregator must have high risk for this user
    test_access("suspicious_user_99", "ehr")
    
    # Case 4: Accessing Medical Devices ( IoMT Zone )
    test_access("nurse_joy", "medical_devices")
