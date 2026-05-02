import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_simulation():
    print("Testing Simulation Start...")
    try:
        res = requests.post(f"{BASE_URL}/api/simulate/start")
        print(f"Start Res: {res.json()}")
    except Exception as e:
        print(f"Failed to start simulation: {e}")
        return

    print("\nPolling Simulation Status...")
    for i in range(5):
        try:
            res = requests.get(f"{BASE_URL}/api/simulate/status")
            data = res.json()
            print(f"Stage: {data.get('stage')} | Risk: {data.get('combined_risk'):.4f} | Action: {data.get('action')}")
            if data.get('stage') == "Complete":
                break
        except Exception as e:
            print(f"Polling failed: {e}")
        time.sleep(1)

def test_risk_decision():
    print("\nTesting Risk Fusion Engine...")
    payload = {
        "lstm_score": 0.8,
        "isolation_score": 0.7,
        "honeypot_boost": 0.1
    }
    try:
        res = requests.post(f"{BASE_URL}/api/risk/decision", json=payload)
        print(f"Decision Res: {res.json()}")
    except Exception as e:
        print(f"Decision test failed: {e}")

if __name__ == "__main__":
    # Note: AI Server must be running for this to work
    print("HealthSentinel Simulation Test Runner")
    print("="*40)
    test_simulation()
    test_risk_decision()
