# HealthSentinel IoMT Anomaly Detection - Google Colab Notebook
# =====================================================================
# This notebook trains a 1D-CNN to detect anomalies in Medical Device communication.
# It focuses on command frequency, value ranges, and inter-arrival times.

# %% [markdown]
# # 🏥 HealthSentinel - IoMT Anomaly Detection (1D-CNN)
# 
# This notebook implements a 1D-CNN to monitor medical devices (like infusion pumps).
# We simulate features like command type, value (e.g., flow rate), and time since last command.
# 
# **Runtime**: T4 GPU
# **Goal**: Detect "command injection" or "dosage manipulation" that bypasses standard auth.

# %% [code]
# Cell 1: Setup
# !pip install torch pandas numpy scikit-learn matplotlib --quiet

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
from google.colab import drive, files

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"✅ Device: {device}")

# %% [code]
# Cell 2: IoMT Command Simulator
# Commands: 0=Pulse, 1=Read_Rate, 2=Set_Rate, 3=Set_Bolus (Critical), 4=Reset

def generate_iomt_seq(label_type="normal", length=10):
    """
    Generate a sequence of 10 commands.
    Features per command: [cmd_id, value, time_delta, error_flags]
    """
    seq = np.zeros((length, 4))
    
    if label_type == "normal":
        for i in range(length):
            cmd = np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1])
            val = np.random.uniform(1.0, 5.0) if cmd == 2 else 0.0
            dt = np.random.uniform(5.0, 60.0) # Normal slow drip
            seq[i] = [cmd, val, dt, 0]
            
    elif label_type == "dosage_overflow":
        # Sudden jump to dangerous dosage
        for i in range(length-1):
            seq[i] = [0, 0, 10, 0]
        seq[-1] = [3, 99.0, 1.0, 0] # Dangerous bolus dose
        
    elif label_type == "command_burst":
        # DoS/Bruteforce pattern
        for i in range(length):
            seq[i] = [random.randint(0,4), random.random(), 0.1, 0] # Very fast commands
            
    return seq

# %% [code]
# Cell 3: Dataset Creation
N = 2000
X = []
y = []

# labels: 0=normal, 1=anomaly
for _ in range(N // 2):
    X.append(generate_iomt_seq("normal"))
    y.append(0)
    
for _ in range(N // 4):
    X.append(generate_iomt_seq("dosage_overflow"))
    y.append(1)
    
for _ in range(N // 4):
    X.append(generate_iomt_seq("command_burst"))
    y.append(1)

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)

# Reshape for CNN (batch, features, sequence_length)
X = X.transpose(0, 2, 1) # (N, 4, 10)

print(f"✅ X shape: {X.shape}, y shape: {y.shape}")

# %% [code]
# Cell 4: 1D-CNN Architecture
class IoMTAnomalizer(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv1d(4, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Flatten()
        )
        self.fc = nn.Sequential(
            nn.Linear(64 * 10, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )
    def forward(self, x):
        return self.fc(self.conv(x)).squeeze()

model = IoMTAnomalizer().to(device)
print(f"✅ IoMT Model Ready")

# Cell 5: Train & Save
# (Training loop omitted for brevity in file creation, same as zeroday)
# ...
# torch.save(model.state_dict(), 'iomt_cnn.pt')
# files.download('iomt_cnn.pt')
