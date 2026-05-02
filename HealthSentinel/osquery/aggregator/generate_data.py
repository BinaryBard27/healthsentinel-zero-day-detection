"""
Quick synthetic data generator - run this to generate training data.
"""
import json
import random
from datetime import datetime, timedelta

output_path = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\osquery\sample_data\insider_threat_training_data.json"

EVENT_TYPES = ["user_login_events", "file_access_events", "network_connections", "usb_devices", "process_events", "off_hours_activity", "sensitive_directory_access"]

SENSITIVE_PATHS = ["/data/patients/records", "/data/billing/claims", "/data/phi/ssn_list"]
NORMAL_PATHS = ["/home/user/documents", "/var/log/system", "/opt/applications"]

def generate_sequence(user, is_suspicious, seq_length=60):
    base_time = datetime.now() - timedelta(hours=random.randint(1, 72))
    events = []
    
    for i in range(seq_length):
        timestamp = int((base_time + timedelta(minutes=i*2)).timestamp())
        hour = (base_time + timedelta(minutes=i*2)).hour
        
        if is_suspicious:
            event_type = random.choice(["off_hours_activity", "sensitive_directory_access", "external_network", "usb_devices"])
            columns = {"username": user, "time": timestamp}
            
            if event_type == "sensitive_directory_access":
                columns["target_path"] = random.choice(SENSITIVE_PATHS)
                columns["size"] = random.randint(5000000, 50000000)
            elif event_type == "external_network":
                columns["remote_address"] = f"{random.randint(50,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
            elif event_type == "usb_devices":
                columns["removable"] = "1"
        else:
            event_type = random.choice(["user_login_events", "file_access_events", "process_events"])
            columns = {"username": user, "time": timestamp}
            if event_type == "file_access_events":
                columns["target_path"] = random.choice(NORMAL_PATHS)
                columns["size"] = random.randint(100, 1000000)
        
        events.append({"name": event_type, "host": f"ws-{random.randint(100,999)}", "unixTime": timestamp, "columns": columns})
    
    return {"user": user, "events": events, "label": 1 if is_suspicious else 0}

print("Generating 500 normal + 200 suspicious sequences...")
sequences = []

for i in range(500):
    user = f"user_{random.randint(100,999)}"
    sequences.append(generate_sequence(user, False))
    if (i+1) % 100 == 0:
        print(f"  Normal: {i+1}/500")

for i in range(200):
    user = f"user_{random.randint(100,999)}"
    sequences.append(generate_sequence(user, True))
    if (i+1) % 50 == 0:
        print(f"  Suspicious: {i+1}/200")

random.shuffle(sequences)

dataset = {
    "metadata": {"total": 700, "normal": 500, "suspicious": 200, "seq_length": 60},
    "sequences": sequences
}

with open(output_path, 'w') as f:
    json.dump(dataset, f)

print(f"Saved to {output_path}")
print(f"File size: {len(json.dumps(dataset))/1024:.1f} KB")
