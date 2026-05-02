import requests
import time
import random

def run_attack():
    print("[!] Simulating Insider Threat: Bulk Data Exfiltration...")
    for i in range(5):
        try:
            # Simulate high-risk behavioral sequence (anomalous data access)
            # 12 features per action, 10 actions in a sequence
            sequence = [[random.uniform(0.6, 1.0) for _ in range(12)] for _ in range(10)]
            response = requests.post("http://localhost:8000/api/ai/insider-threat", json={
                "user_id": "employee_04",
                "sequence_data": sequence
            }, timeout=2)
            print(f"[*] Analyzing user behavior {i+1}/5 - Status: {response.status_code}")
            if response.status_code == 200:
                res = response.json()
                print(f"[*] AI Anomaly Detected: {res.get('is_anomaly')} (Score: {res.get('risk_score'):.4f})")
            time.sleep(0.5)
        except Exception as e:
            print(f"[ERROR] Request failed: {e}")
            break

if __name__ == "__main__":
    run_attack()