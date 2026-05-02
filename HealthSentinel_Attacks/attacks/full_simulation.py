import os
import subprocess
import time
import random

try:
    import requests
except ImportError:
    requests = None  # type: ignore

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    attacks = [
        ("sqli_attack.py", "SQL Injection"),
        ("phishing_link.py", "Phishing Campaign"),
        ("ransom_sim.py", "Ransomware Execution"),
        ("insider_threat.py", "Insider Data Leak")
    ]

    print("==========================================")
    print("   HEALTH SENTINEL: FULL BATTLE SIMULATION")
    print("==========================================")
    print(f"[*] Duration: 2-3 Minutes")
    print(f"[*] Mode: Multi-Vector Hybrid Attack")
    print("------------------------------------------")

    # 1. Start the simulation on the dashboard (notify server — battle mode for live report)
    try:
        if requests is None:
            raise RuntimeError("requests not installed")
        num_waves = 12
        requests.post(
            "http://localhost:8000/api/ai/simulate/start",
            json={"battle_mode": True, "expected_waves": num_waves},
            timeout=5,
        )
        print("[+] Dashboard Simulation Sync: ACTIVE (live battle mode)")
    except Exception as e:
        print(f"[!] Warning: Dashboard sync failed ({e}). Running local attacks only.")

    start_time = time.time()
    
    # 2. Run randomized attack waves
    for i in range(12): # 12 waves over ~2-3 mins
        attack_file, attack_name = random.choice(attacks)
        print(f"\n[{time.strftime('%H:%M:%S')}] 🚨 WAVE {i+1}: Launching {attack_name}...")
        
        script_path = os.path.join(base_path, attack_file)
        subprocess.run(["python", script_path])

        try:
            if requests:
                requests.post(
                    "http://localhost:8000/api/ai/simulate/wave",
                    json={"wave": i + 1, "attack_name": attack_name},
                    timeout=5,
                )
        except Exception:
            pass
        
        # Random delay between 10-20 seconds
        delay = random.uniform(10, 18)
        print(f"[*] Cooling down for {delay:.1f}s...")
        time.sleep(delay)

    print("\n------------------------------------------")
    print(f"[+] Simulation Complete. Total Duration: {time.time() - start_time:.1f}s")
    
    # Notify server to trigger report
    try:
        if requests:
            requests.post("http://localhost:8000/api/ai/simulate/complete", timeout=5)
        print("[+] Dashboard Sync: Triggering Final Report...")
    except Exception:
        pass

    print("[+] Check the dashboard for the Forensic Report.")
    print("==========================================")

if __name__ == "__main__":
    main()
