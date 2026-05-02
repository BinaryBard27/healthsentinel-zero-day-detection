import requests

TARGET_IP = "192.168.1.XX"
URL = "http://localhost:8000/api/ai/phishing"

# Spoofing the Referer header to look like a phishing site
headers = {
    "User-Agent": "Mozilla/5.0",
    "Referer": "http://hospital-staff-update-verify.com/login-secure"
}

def run_attack():
    print(f"[!] Simulating Phishing Link Click from suspicious domain...")
    # Phishing detection expects subject, message, sender
    payload = {
        "sender": "security@payroll-verify.xyz",
        "subject": "URGENT: Your payroll account will be suspended",
        "message": "Click here http://bit.ly/payroll-urgent123 to verify your account and prevent suspension. Enter your hospital ID and password.",
        "urls": ["http://bit.ly/payroll-urgent123"]
    }
    try:
        response = requests.post(URL, json=payload, headers=headers, timeout=5)
        print(f"[*] Request sent. Status: {response.status_code}")
        if response.status_code == 200:
            res = response.json()
            print(f"[*] AI Verdict: {res.get('action')} - {res.get('user_message')}")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")

if __name__ == "__main__":
    run_attack()