import requests
import json
import time
import argparse
from datetime import datetime

def print_banner():
    print("="*60)
    print("  🔥 MEDGUARD LIVE ATTACK SIMULATOR 🔥")
    print("="*60)
    print("WARNING: This script will send malicious payloads to the target.")
    print("The MedGuard system should detect and block these attempts.\n")

def simulate_sql_injection(target_ip):
    print("[*] Launching SQL Injection Attack against AI Server...")
    url = f"http://{target_ip}:5000/api/ai/sql-injection"
    payload = {
        "query": "SELECT * FROM users WHERE username = 'admin' OR '1'='1' --"
    }
    try:
        start_time = time.time()
        print(f"    Target: {url}")
        print(f"    Payload: {payload['query']}")
        response = requests.post(url, json=payload, timeout=5)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            res_data = response.json()
            is_detected = res_data.get('is_injection', False)
            risk = res_data.get('risk_level', 'UNKNOWN')
            conf = res_data.get('confidence', 0)
            
            if is_detected:
                print(f"    [+] SHIELD ACTIVATED! AI detected injection in {elapsed*1000:.1f}ms")
                print(f"        Risk: {risk} | Confidence: {conf*100:.1f}%")
            else:
                print("    [-] Attack bypassed detection! (Warning)")
        else:
            print(f"    [!] Error: Server returned {response.status_code}")
    except Exception as e:
        print(f"    [!] Connection Failed: {e}")

def simulate_insider_exfiltration(target_ip):
    print("\n[*] Launching Insider Data Exfiltration (OSQuery Log Spoofing)...")
    url = f"http://{target_ip}:8085/logs"
    
    # We will spoof a highly suspicious log event to trigger the log aggregator's alerts
    # This will show up LIVE on the React Dashboard!
    fake_time = int(datetime.now().replace(hour=3).timestamp()) # 3 AM
    
    malicious_log = {
        "name": "file_events",
        "hostIdentifier": "friend-pc-001",
        "calendarTime": datetime.now().isoformat(),
        "unixTime": fake_time,
        "epoch": 0,
        "counter": 1,
        "columns": {
            "username": "Administrator",
            "target_path": "/data/patient_records_dump.csv",
            "action": "ACCESSED",
            "remote_address": "203.0.113.55"  # External IP
        }
    }
    
    payload = {
        "logs": [malicious_log]
    }
    
    try:
        print(f"    Target: {url}")
        print("    Injecting malicious log sequence (Mass patient data access at 3AM from external IP)...")
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            res_data = response.json()
            alerts = res_data.get('alerts_generated', 0)
            
            if alerts > 0:
                print(f"    [+] BLOCKED! Aggregator generated {alerts} critical alert(s).")
                print("        Check the MedGuard Dashboard Live Feed!")
            else:
                print("    [-] Log accepted, but no alert generated. Tuning might be needed.")
        else:
            print(f"    [!] Error: Server returned {response.status_code}")
    except Exception as e:
        print(f"    [!] Connection Failed: {e}")


def main():
    parser = argparse.ArgumentParser(description="MedGuard Live Attack Script")
    parser.add_argument("target_ip", help="IP address of the MedGuard server (e.g. 192.168.1.5)")
    args = parser.parse_args()
    
    print_banner()
    
    print(f"Targeting MedGuard System at: {args.target_ip}\n")
    
    simulate_sql_injection(args.target_ip)
    time.sleep(2)
    simulate_insider_exfiltration(args.target_ip)
    
    print("\n[*] Attack sequence complete. Check the MedGuard SOC dashboard for alerts.")

if __name__ == "__main__":
    main()
