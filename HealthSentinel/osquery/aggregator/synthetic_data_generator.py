"""
Synthetic Training Data Generator
=================================
Generates realistic OSQuery event sequences for LSTM training.
Creates both normal behavior patterns and suspicious insider threat patterns.

Output: JSON file with labeled sequences for Google Colab training.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import os

# Event types we simulate
EVENT_TYPES = [
    "user_login_events",
    "file_access_events", 
    "network_connections",
    "usb_devices",
    "process_events",
    "high_privilege_access",
    "large_file_operations",
    "off_hours_activity",
    "sensitive_directory_access",
    "external_network_connections"
]

# Departments in a hospital
DEPARTMENTS = ["Cardiology", "Radiology", "Emergency", "Pharmacy", "Billing", "IT", "Admin"]

# File paths
SENSITIVE_PATHS = [
    "/data/patients/records",
    "/data/billing/claims",
    "/data/phi/ssn_list",
    "/data/medical/prescriptions",
    "/data/insurance/policies"
]
NORMAL_PATHS = [
    "/home/user/documents",
    "/var/log/system",
    "/opt/applications",
    "/tmp/temp_files"
]


def generate_user_id() -> str:
    """Generate a realistic user ID."""
    prefixes = ["dr_", "nurse_", "admin_", "tech_", "billing_"]
    return random.choice(prefixes) + str(random.randint(100, 999))


def generate_timestamp(base_time: datetime, offset_minutes: int = 0) -> int:
    """Generate unix timestamp."""
    return int((base_time + timedelta(minutes=offset_minutes)).timestamp())


def is_work_hours(hour: int) -> bool:
    """Check if hour is within normal work hours (7 AM - 7 PM)."""
    return 7 <= hour <= 19


def generate_normal_event(user: str, base_time: datetime, offset: int) -> Dict[str, Any]:
    """Generate a single normal event."""
    timestamp = generate_timestamp(base_time, offset)
    hour = (base_time + timedelta(minutes=offset)).hour
    
    # Normal users mostly work during work hours
    if not is_work_hours(hour):
        return None  # Skip off-hours for normal behavior
    
    event_type = random.choice([
        "user_login_events",
        "file_access_events",
        "process_events"
    ])
    
    columns = {
        "username": user,
        "time": timestamp,
    }
    
    if event_type == "file_access_events":
        columns["target_path"] = random.choice(NORMAL_PATHS)
        columns["action"] = random.choice(["read", "write"])
        columns["size"] = random.randint(100, 1_000_000)  # Normal file sizes
    
    elif event_type == "network_connections":
        columns["remote_address"] = f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"
        columns["remote_port"] = random.choice([80, 443, 22, 3306])
    
    elif event_type == "process_events":
        columns["path"] = random.choice(["/usr/bin/python", "/usr/bin/bash", "/opt/app/start"])
        columns["cmdline"] = "normal_process_command"
    
    return {
        "name": event_type,
        "hostIdentifier": f"ws-{random.randint(100, 999)}",
        "unixTime": timestamp,
        "columns": columns
    }


def generate_suspicious_event(user: str, base_time: datetime, offset: int) -> Dict[str, Any]:
    """Generate a single suspicious event (insider threat pattern)."""
    timestamp = generate_timestamp(base_time, offset)
    hour = (base_time + timedelta(minutes=offset)).hour
    
    # Suspicious activities often happen off-hours
    suspicious_types = [
        ("off_hours_activity", 0.3),
        ("sensitive_directory_access", 0.25),
        ("large_file_operations", 0.2),
        ("external_network_connections", 0.15),
        ("usb_devices", 0.1)
    ]
    
    # Weighted random selection
    event_type = random.choices(
        [t[0] for t in suspicious_types],
        weights=[t[1] for t in suspicious_types]
    )[0]
    
    columns = {
        "username": user,
        "time": timestamp,
    }
    
    if event_type == "off_hours_activity":
        # Force off-hours
        off_hour = random.choice([1, 2, 3, 4, 5, 22, 23, 0])
        columns["time"] = int((base_time.replace(hour=off_hour) + timedelta(minutes=offset)).timestamp())
    
    elif event_type == "sensitive_directory_access":
        columns["target_path"] = random.choice(SENSITIVE_PATHS)
        columns["action"] = random.choice(["read", "copy", "download"])
    
    elif event_type == "large_file_operations":
        columns["target_path"] = random.choice(SENSITIVE_PATHS)
        columns["size"] = random.randint(50_000_000, 500_000_000)  # 50MB - 500MB
        columns["action"] = "copy"
    
    elif event_type == "external_network_connections":
        # External IP (not internal network)
        columns["remote_address"] = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        columns["remote_port"] = random.choice([21, 22, 4444, 8080, 9999])  # Suspicious ports
    
    elif event_type == "usb_devices":
        columns["vendor"] = "Unknown"
        columns["model"] = f"USB_STORAGE_{random.randint(1, 99)}"
        columns["removable"] = "1"
    
    return {
        "name": event_type,
        "hostIdentifier": f"ws-{random.randint(100, 999)}",
        "unixTime": timestamp,
        "columns": columns
    }


def generate_sequence(user: str, is_suspicious: bool, seq_length: int = 60) -> Dict[str, Any]:
    """
    Generate a complete event sequence for one user.
    
    Args:
        user: User identifier
        is_suspicious: True if this should be an insider threat pattern
        seq_length: Number of events in sequence
    
    Returns:
        Dict with events list and label (0=normal, 1=suspicious)
    """
    base_time = datetime.now() - timedelta(hours=random.randint(1, 72))
    events = []
    
    for i in range(seq_length):
        offset = i * random.randint(1, 5)  # 1-5 minutes between events
        
        if is_suspicious:
            # Mix of suspicious and some normal events
            if random.random() < 0.6:  # 60% suspicious events
                event = generate_suspicious_event(user, base_time, offset)
            else:
                event = generate_normal_event(user, base_time, offset)
        else:
            event = generate_normal_event(user, base_time, offset)
        
        if event:
            events.append(event)
    
    return {
        "user": user,
        "sequence_id": f"{user}_{int(base_time.timestamp())}",
        "events": events,
        "label": 1 if is_suspicious else 0,
        "label_name": "suspicious" if is_suspicious else "normal"
    }


def generate_dataset(
    num_normal: int = 500,
    num_suspicious: int = 200,
    seq_length: int = 60,
    output_path: str = None
) -> Dict[str, Any]:
    """
    Generate complete training dataset.
    
    Args:
        num_normal: Number of normal behavior sequences
        num_suspicious: Number of suspicious behavior sequences
        seq_length: Events per sequence
        output_path: Optional path to save JSON file
    
    Returns:
        Dataset dictionary
    """
    print(f"🔄 Generating {num_normal} normal + {num_suspicious} suspicious sequences...")
    
    sequences = []
    
    # Generate normal sequences
    for i in range(num_normal):
        user = generate_user_id()
        seq = generate_sequence(user, is_suspicious=False, seq_length=seq_length)
        sequences.append(seq)
        if (i + 1) % 100 == 0:
            print(f"  Normal: {i + 1}/{num_normal}")
    
    # Generate suspicious sequences
    for i in range(num_suspicious):
        user = generate_user_id()
        seq = generate_sequence(user, is_suspicious=True, seq_length=seq_length)
        sequences.append(seq)
        if (i + 1) % 50 == 0:
            print(f"  Suspicious: {i + 1}/{num_suspicious}")
    
    # Shuffle
    random.shuffle(sequences)
    
    dataset = {
        "metadata": {
            "total_sequences": len(sequences),
            "normal_count": num_normal,
            "suspicious_count": num_suspicious,
            "sequence_length": seq_length,
            "event_types": EVENT_TYPES,
            "generated_at": datetime.now().isoformat()
        },
        "sequences": sequences
    }
    
    if output_path:
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(dataset, f, indent=2)
        print(f"✅ Dataset saved to {output_path}")
    
    return dataset


if __name__ == "__main__":
    # Generate training dataset
    output_file = "../sample_data/insider_threat_training_data.json"
    generate_dataset(
        num_normal=500,
        num_suspicious=200,
        seq_length=60,
        output_path=output_file
    )
    
    print("\n📊 Dataset Statistics:")
    print(f"  - Total sequences: 700")
    print(f"  - Events per sequence: 60")
    print(f"  - Class ratio: 500 normal : 200 suspicious (71% : 29%)")
    print(f"\n🚀 Ready for training on Google Colab!")
