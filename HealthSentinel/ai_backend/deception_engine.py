import random
from datetime import datetime

class DeceptionEngine:
    def __init__(self):
        self.assets = [
            {"id": "h-db-01", "name": "Patient Records (Old)", "type": "Database", "status": "idle", "ip": "10.0.0.42"},
            {"id": "h-srv-01", "name": "Legacy Admin Portal", "type": "Web Server", "status": "idle", "ip": "10.0.0.43"},
            {"id": "h-ssh-01", "name": "Backdoor SSH", "type": "Management", "status": "idle", "ip": "10.0.0.44"},
            {"id": "h-s3-01", "name": "Backup-Vault-2022", "type": "Cloud Storage", "status": "idle", "ip": "N/A"}
        ]
        self.triggers = []

    def get_assets(self):
        return self.assets

    def trigger_honeypot(self, asset_id, user_id="attacker"):
        for asset in self.assets:
            if asset["id"] == asset_id:
                asset["status"] = "triggered"
                event = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "asset_id": asset_id,
                    "asset_name": asset["name"],
                    "asset_type": asset["type"],
                    "trigger_ip": asset["ip"],
                    "user_id": user_id,
                    "alert_level": "CRITICAL",
                    "risk_boost": 0.25 # Direct interaction with honeypot is a strong indicator
                }
                self.triggers.append(event)
                return event
        return None

    def reset(self):
        for asset in self.assets:
            asset["status"] = "idle"
        self.triggers = []

    def generate_honey_record(self):
        """Generate a fake patient record to be used as a honey-token."""
        first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Diana"]
        last_names = ["Smith", "Doe", "Brown", "Wilson", "Taylor", "Miller"]
        conditions = ["Hypertension", "Type 2 Diabetes", "Asthma", "Arrhythmia"]
        
        record = {
            "patient_id": f"PAT-HONEY-{random.randint(1000, 9999)}",
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "dob": f"{random.randint(1,12)}/{random.randint(1,28)}/{random.randint(1950, 2010)}",
            "ssn": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}",
            "diagnosis": random.choice(conditions),
            "is_honeytoken": True,
            "canary_hash": hashlib.sha256(str(time.time()).encode()).hexdigest()[:10]
        }
        return record

import hashlib
import time

if __name__ == "__main__":
    engine = DeceptionEngine()
    print("Assets:")
    for a in engine.get_assets():
        print(a)
    print("\nTriggering h-db-01...")
    print(engine.trigger_honeypot("h-db-01"))
