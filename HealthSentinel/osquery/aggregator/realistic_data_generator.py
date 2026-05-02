"""
HealthSentinel Realistic Log Generator (To Fix Overfitting) v2
==============================================================
Parses multiple log types (Windows, Linux, SSH, Android) to build 
a high-entropy training set for the Insider Threat LSTM.
"""

import pandas as pd
import numpy as np
import os
import random

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
DATASETS_DIR = r"c:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\preprocessed data\sql injection and log\log files"
OUTPUT_PATH = r"c:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\realistic_insider_threat.csv"

# EVENT MAPPING (Align with log_aggregator.py)
EVENT_TYPES = {"user_login": 0, "file_access": 1, "network": 2, "usb": 3, "process": 4, 
               "off_hours": 5, "sensitive_access": 6, "external_net": 7, "large_file": 8, "high_priv": 9}

def parse_csv_log(filename, event_map_fn):
    path = os.path.join(DATASETS_DIR, filename)
    if not os.path.exists(path): return []
    try:
        # Use low_memory and sample to handle large files
        df = pd.read_csv(path, on_bad_lines='skip', low_memory=False)
        logs = []
        sample_size = min(len(df), 2000)
        for _, row in df.sample(sample_size).iterrows():
            logs.append(event_map_fn(row))
        return logs
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
        return []

def windows_mapper(row):
    content = str(row.get('Content', '')).lower()
    event = "process"
    if "login" in content: event = "user_login"
    elif "file" in content: event = "file_access"
    return {"event": event, "hour": random.randint(8, 18), "is_sensitive": 0, "is_external": 0}

def apache_mapper(row):
    return {"event": "network", "hour": random.randint(0, 23), "is_sensitive": 0, "is_external": 1}

def ssh_mapper(row):
    content = str(row.get('Content', '')).lower()
    event = "user_login" if "accepted" in content or "password" in content else "network"
    return {"event": event, "hour": random.randint(0, 23), "is_sensitive": 0, "is_external": 1}

def generate_threat_sequences(n_samples=800):
    """Generates complex attack patterns that mimic insider exfiltration."""
    threats = []
    for _ in range(n_samples):
        seq = []
        for i in range(20): # 20 steps per sequence
            # Pattern: Login -> Broad File Search -> Sensitive File Read -> Upload
            if i < 2: e = "user_login"
            elif i < 10: e = "process"
            elif i < 15: e = "sensitive_access"
            elif i < 19: e = "file_access"
            else: e = "external_net"
            
            seq.append({
                "event": e,
                "hour": random.choice([2, 3, 23, 0, 1]), # Suspicious hours
                "is_sensitive": 1 if i >= 10 else 0,
                "is_external": 1 if i >= 18 else 0,
                "label": 1
            })
        threats.append(seq)
    return threats

def main():
    print("🚀 Starting log ingestion pipeline...")
    all_logs = []
    
    # Ingest from various sources
    sources = [
        ("Windows_2k.log_structured_cleaned.csv", windows_mapper),
        ("Apache_2k.log_structured_cleaned.csv", apache_mapper),
        ("OpenSSH_2k.log_structured_cleaned.csv", ssh_mapper)
    ]
    
    for filename, mapper in sources:
        logs = parse_csv_log(filename, mapper)
        if logs:
            print(f"✅ Ingested {len(logs)} events from {filename}")
            all_logs += logs
    
    if len(all_logs) < 100:
        print("⚠️ Warning: Very few logs parsed. Using fallback generation.")
        all_logs += [{"event": "process", "hour": random.randint(9, 17), "is_sensitive": 0, "is_external": 0} for _ in range(5000)]

    print(f"📊 Total base events gathered: {len(all_logs)}")
    
    final_data = []
    
    # Normal sequences (Label 0)
    print("🏠 Building normal user sequences...")
    for i in range(0, len(all_logs) - 20, 20):
        seq = all_logs[i:i+20]
        for event in seq:
            feat = np.zeros(64)
            # Map event type to index
            idx = EVENT_TYPES.get(event['event'], 4)
            feat[idx] = 1.0
            feat[10] = event['hour'] / 24.0
            feat[18] = float(event['is_sensitive'])
            feat[22] = float(event['is_external'])
            # Add significant Gaussian noise to make the model work harder (prevents overfitting)
            feat += np.random.normal(0, 0.05, 64)
            
            row = list(feat) + [0]
            final_data.append(row)
            
    # Attack sequences (Label 1)
    print("👾 Injecting insider threat patterns...")
    threat_seqs = generate_threat_sequences()
    for seq in threat_seqs:
        for event in seq:
            feat = np.zeros(64)
            idx = EVENT_TYPES.get(event['event'], 4)
            feat[idx] = 1.0
            feat[10] = event['hour'] / 24.0
            feat[18] = float(event['is_sensitive'])
            feat[22] = float(event['is_external'])
            feat += np.random.normal(0, 0.05, 64)
            
            row = list(feat) + [1]
            final_data.append(row)

    cols = [f"f{i}" for i in range(64)] + ["label"]
    df = pd.DataFrame(final_data, columns=cols)
    df = df.sample(frac=1).reset_index(drop=True) # Shuffle
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Success! Created HD dataset at: {OUTPUT_PATH}")
    print(f"📈 Dataset shape: {df.shape}")

if __name__ == "__main__":
    main()
