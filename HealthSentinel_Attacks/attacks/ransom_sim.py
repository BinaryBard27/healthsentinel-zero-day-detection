import os
import time

DATA_DIR = "../data"

def run_attack():
    # 1. Ensure dummy data exists
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    for i in range(10):
        with open(f"{DATA_DIR}/record_{i}.pdf", "w") as f:
            f.write("Encrypted Medical Record Content Simulation")

    print(f"[!] Starting Ransomware File Encryption Simulation in {DATA_DIR}...")
    
    # 2. Simulate rapid renaming/encryption
    files = [f for f in os.listdir(DATA_DIR) if not f.endswith(".locked")]
    
    for filename in files:
        old_path = os.path.join(DATA_DIR, filename)
        new_path = os.path.join(DATA_DIR, filename + ".locked")
        os.rename(old_path, new_path)
        print(f"[*] Encrypting: {filename} -> {filename}.locked")
        
        # Notify AI Backend for detection
        try:
            import requests
            requests.post("http://localhost:8000/api/ai/ransomware", json={
                "file_features": [0.95, 0.8, 0.7, 0.9], # entropy, suspicious_api, etc
                "file_name": filename
            }, timeout=1)
        except: pass
        
        time.sleep(0.2)

    print("[!] Encryption complete. System compromised.")

if __name__ == "__main__":
    run_attack()