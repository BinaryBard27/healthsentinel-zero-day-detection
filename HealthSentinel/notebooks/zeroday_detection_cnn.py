# HealthSentinel Zero-Day Threat Detection - Google Colab Notebook
# =====================================================================
# This notebook trains a 1D-CNN classifier to detect novel/zero-day network attacks.
# It uses a simplified synthetic dataset generator to simulate network traffic features.

# %% [markdown]
# # 🛡️ HealthSentinel - Zero-Day Threat Detection (1D-CNN)
# 
# This notebook implements a 1D-CNN classifier to detect network-based attacks.
# We simulate network traffic features (packet length, flow duration, flags, etc.)
# and train the model to distinguish between normal traffic and various attack types.
# 
# **Runtime**: T4 GPU (free tier)
# **Technique**: 1D-CNN for spatial-temporal feature learning in network flows.

# %% [code]
# Cell 1: Setup
!pip install torch pandas numpy scikit-learn matplotlib seaborn --quiet

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import drive, files

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"✅ Using device: {device}")

# %% [code]
# Cell 2: Synthetic Network Attack Generator
# Simulates features similar to CICIDS but simplified for faster training

NETWORK_FEATURES = [
    "flow_duration", "tot_fwd_pkts", "tot_bwd_pkts", "tot_len_fwd_pkts", 
    "tot_len_bwd_pkts", "fwd_pkt_len_max", "fwd_pkt_len_min", "fwd_pkt_len_mean",
    "flow_byts_s", "flow_pkts_s", "fwd_iat_mean", "bwd_iat_mean",
    "fwd_header_len", "bwd_header_len", "fwd_pkts_s", "bwd_pkts_s",
    "pkt_len_min", "pkt_len_max", "pkt_len_mean", "avg_pkt_size"
]
NUM_FEATURES = len(NETWORK_FEATURES)

def generate_network_flow(label_type="normal"):
    """
    Generate synthetic network flow features.
    label_type: "normal", "dos", "bruteforce", "injection"
    """
    features = np.zeros(NUM_FEATURES)
    
    if label_type == "normal":
        # Normal traffic patterns
        features[0] = np.random.uniform(100, 5000) # Duration
        features[1] = np.random.randint(1, 10)     # Fwd pkts
        features[2] = np.random.randint(1, 10)     # Bwd pkts
        features[3] = features[1] * np.random.uniform(40, 1000)
        features[18] = np.random.uniform(40, 1500) # Pkt len mean
        
    elif label_type == "dos":
        # DoS: High volume, small packets, high rate
        features[0] = np.random.uniform(10, 500)
        features[1] = np.random.randint(100, 1000)
        features[9] = 10000 # High pkts/s
        features[18] = np.random.uniform(40, 60) # Small packets
        
    elif label_type == "bruteforce":
        # Brute Force: Repetitive small flows
        features[0] = np.random.uniform(500, 2000)
        features[1] = np.random.randint(5, 20)
        features[2] = np.random.randint(5, 20)
        features[10] = np.random.uniform(1, 5) # Low IAT
        
    elif label_type == "injection":
        # Injection: Large packets, medium duration
        features[0] = np.random.uniform(1000, 10000)
        features[1] = np.random.randint(20, 100)
        features[3] = np.random.uniform(5000, 50000) # Large length
        features[18] = np.random.uniform(800, 1500) # Large packets
    
    # Add noise
    features += np.random.normal(0, 0.05 * features)
    return np.clip(features, 0, None)

# %% [code]
# Cell 3: Create Dataset

NUM_SAMPLES = 5000
print(f"Generating {NUM_SAMPLES} network samples...")

X = []
y = []

# Class distribution: 70% Normal, 10% DoS, 10% BruteForce, 10% Injection
labels = ["normal"] * 3500 + ["dos"] * 500 + ["bruteforce"] * 500 + ["injection"] * 500
label_map = {"normal": 0, "dos": 1, "bruteforce": 2, "injection": 3}

for label_name in labels:
    X.append(generate_network_flow(label_name))
    y.append(label_map[label_name])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int64)

# Normalize data
from sklearn.preprocessing import StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Reshape for 1D-CNN (samples, channels, features)
# We treat the features as a 1D sequence
X = X.reshape(X.shape[0], 1, X.shape[1])

print(f"✅ Dataset ready: X={X.shape}, y={y.shape}")

# %% [code]
# Cell 4: 1D-CNN Model Architecture

class ZeroDayCNN(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        
        self.conv1 = nn.Sequential(
            nn.Conv1d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv1d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.MaxPool1d(2)
        )
        
        self.flatten = nn.Flatten()
        
        # Calculate flatten size: NUM_FEATURES / 2 / 2 = 20 / 4 = 5
        self.fc = nn.Sequential(
            nn.Linear(64 * 5, 128),
            nn.ReLU(),
            nn.Dropout(0.4),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.flatten(x)
        x = self.fc(x)
        return x

model = ZeroDayCNN().to(device)
print(f"✅ 1D-CNN Model ready. Params: {sum(p.numel() for p in model.parameters()):,}")

# %% [code]
# Cell 5: Training

class NetworkDataset(Dataset):
    def __init__(self, X, y): self.X, self.y = torch.FloatTensor(X), torch.LongTensor(y)
    def __len__(self): return len(self.y)
    def __getitem__(self, i): return self.X[i], self.y[i]

ds = NetworkDataset(X, y)
train_ds, val_ds, test_ds = random_split(ds, [3500, 750, 750])

train_dl = DataLoader(train_ds, batch_size=64, shuffle=True)
val_dl = DataLoader(val_ds, batch_size=64)
test_dl = DataLoader(test_ds, batch_size=64)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("Training...")
for epoch in range(30):
    model.train()
    for bx, by in train_dl:
        bx, by = bx.to(device), by.to(device)
        optimizer.zero_grad()
        out = model(bx)
        loss = criterion(out, by)
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 5 == 0:
        model.eval()
        val_loss = 0
        correct = 0
        with torch.no_grad():
            for bx, by in val_dl:
                bx, by = bx.to(device), by.to(device)
                out = model(bx)
                val_loss += criterion(out, by).item()
                correct += (out.argmax(1) == by).sum().item()
        print(f"Epoch {epoch+1:02d} | Val Loss: {val_loss/len(val_dl):.4f} | Acc: {correct/len(val_ds):.4f}")

print("✅ Training complete!")

# %% [code]
# Cell 6: Evaluation

model.eval()
preds, true = [], []
with torch.no_grad():
    for bx, by in test_dl:
        out = model(bx.to(device))
        preds.extend(out.argmax(1).cpu().numpy())
        true.extend(by.numpy())

print("\n📊 ZERO-DAY DETECTION RESULTS")
print(classification_report(true, preds, target_names=["Normal", "DoS", "BruteForce", "Injection"]))

# %% [code]
# Cell 7: Save & Download

# Save scaler and model
import pickle
with open('network_scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)

torch.save(model.state_dict(), 'zeroday_cnn.pt')
files.download('network_scaler.pkl')
files.download('zeroday_cnn.pt')
print("✅ Files downloaded. Place 'zeroday_cnn.pt' and 'network_scaler.pkl' in models/zeroday/")
