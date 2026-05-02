# HealthSentinel LSTM Insider Threat Detection - Google Colab Notebook
# =====================================================================
# This notebook trains a BiLSTM+Attention model for insider threat detection
# Run this on Google Colab with GPU (Runtime → Change runtime type → T4 GPU)

# %% [markdown]
# # 🏥 HealthSentinel - LSTM Insider Threat Detection
# 
# This notebook trains a BiLSTM model with Attention mechanism to detect
# insider threats in healthcare systems based on OSQuery telemetry.
# 
# **Runtime**: T4 GPU (free tier, ~3 hours)
# **Dataset**: Synthetic OSQuery event sequences

# %% [code]
# Cell 1: Setup & Imports
!pip install torch pandas numpy scikit-learn matplotlib seaborn --quiet

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
import json
import random
from datetime import datetime, timedelta
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from google.colab import drive

print("✅ Libraries imported successfully")
print(f"PyTorch version: {torch.__version__}")
print(f"GPU available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# %% [code]
# Cell 2: Generate Synthetic Training Data (run this instead of uploading)
# This generates realistic OSQuery event sequences for training

EVENT_TYPES = {
    "user_login_events": 0,
    "file_access_events": 1,
    "network_connections": 2,
    "usb_devices": 3,
    "process_events": 4,
    "off_hours_activity": 5,
    "sensitive_directory_access": 6,
    "external_network_connections": 7,
    "large_file_operations": 8,
    "high_privilege_access": 9
}
NUM_EVENT_TYPES = len(EVENT_TYPES)

SENSITIVE_PATHS = ["/data/patients", "/data/billing", "/data/phi", "/data/medical"]
NORMAL_PATHS = ["/home/user", "/var/log", "/opt/app", "/tmp"]

def encode_event(event):
    """Convert a single event to a feature vector."""
    features = np.zeros(64)  # 64-dimensional feature vector
    
    # One-hot encode event type (10 dims)
    event_type = event.get("name", "unknown")
    if event_type in EVENT_TYPES:
        features[EVENT_TYPES[event_type]] = 1.0
    
    cols = event.get("columns", {})
    
    # Time features (4 dims)
    timestamp = cols.get("time", event.get("unixTime", 0))
    if timestamp:
        hour = datetime.fromtimestamp(timestamp).hour
        features[10] = hour / 24.0  # Normalized hour
        features[11] = 1.0 if (hour < 7 or hour > 19) else 0.0  # Off-hours flag
        features[12] = 1.0 if (0 <= hour <= 5) else 0.0  # Night shift
        features[13] = datetime.fromtimestamp(timestamp).weekday() / 6.0  # Day of week
    
    # File size features (4 dims)
    size = int(cols.get("size", 0) or 0)
    features[14] = min(size / 1e9, 1.0)  # Normalized size (cap at 1GB)
    features[15] = 1.0 if size > 10_000_000 else 0.0  # Large file flag (>10MB)
    features[16] = 1.0 if size > 50_000_000 else 0.0  # Very large file flag (>50MB)
    features[17] = 1.0 if size > 100_000_000 else 0.0  # Huge file flag (>100MB)
    
    # Path sensitivity (4 dims)
    path = cols.get("target_path", "") or cols.get("path", "")
    path_lower = path.lower()
    features[18] = 1.0 if "patient" in path_lower else 0.0
    features[19] = 1.0 if "billing" in path_lower or "phi" in path_lower else 0.0
    features[20] = 1.0 if "medical" in path_lower or "health" in path_lower else 0.0
    features[21] = 1.0 if any(kw in path_lower for kw in SENSITIVE_PATHS) else 0.0
    
    # Network features (8 dims)
    remote_addr = cols.get("remote_address", "")
    if remote_addr:
        is_internal = remote_addr.startswith(("192.168.", "10.", "172.16.", "127."))
        features[22] = 0.0 if is_internal else 1.0  # External IP flag
        # Port encoding
        port = int(cols.get("remote_port", 0) or 0)
        features[23] = 1.0 if port in [21, 22, 23] else 0.0  # Legacy/risky ports
        features[24] = 1.0 if port in [4444, 8080, 9999, 31337] else 0.0  # Known backdoor ports
        features[25] = 1.0 if port > 1024 else 0.0  # High port
    
    # USB features (2 dims)
    features[26] = 1.0 if cols.get("removable", "") == "1" else 0.0
    features[27] = 1.0 if "USB_STORAGE" in str(cols.get("model", "")).upper() else 0.0
    
    # Action type (4 dims)
    action = cols.get("action", "")
    features[28] = 1.0 if action == "copy" else 0.0
    features[29] = 1.0 if action == "download" else 0.0
    features[30] = 1.0 if action == "delete" else 0.0
    features[31] = 1.0 if action in ["read", "write"] else 0.0
    
    # Random features for additional capacity (32 dims, positions 32-63)
    # In production, add more domain-specific features here
    
    return features

def generate_sequence(is_suspicious, seq_length=60):
    """Generate a complete event sequence."""
    events = []
    base_time = int(datetime.now().timestamp()) - random.randint(3600, 259200)
    
    for i in range(seq_length):
        timestamp = base_time + i * random.randint(60, 300)  # 1-5 min between events
        hour = datetime.fromtimestamp(timestamp).hour
        
        if is_suspicious and random.random() < 0.5:
            # Suspicious event patterns
            event_type = random.choice([
                "off_hours_activity", "sensitive_directory_access",
                "external_network_connections", "large_file_operations",
                "usb_devices", "high_privilege_access"
            ])
            columns = {
                "username": f"user_{random.randint(100,999)}",
                "time": timestamp
            }
            
            if event_type == "sensitive_directory_access":
                columns["target_path"] = random.choice(SENSITIVE_PATHS) + f"/file_{random.randint(1,100)}.csv"
                columns["size"] = random.randint(10_000_000, 200_000_000)
                columns["action"] = random.choice(["copy", "download"])
            elif event_type == "external_network_connections":
                columns["remote_address"] = f"{random.randint(50,200)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
                columns["remote_port"] = random.choice([21, 22, 4444, 8080])
            elif event_type == "large_file_operations":
                columns["target_path"] = random.choice(SENSITIVE_PATHS) + "/bulk_export.zip"
                columns["size"] = random.randint(50_000_000, 500_000_000)
                columns["action"] = "copy"
            elif event_type == "usb_devices":
                columns["removable"] = "1"
                columns["model"] = "USB_STORAGE_DEVICE"
            elif event_type == "off_hours_activity":
                # Force off-hours
                timestamp = base_time + i * 300
                off_hour = random.choice([1, 2, 3, 4, 22, 23])
                dt = datetime.fromtimestamp(timestamp).replace(hour=off_hour)
                columns["time"] = int(dt.timestamp())
        else:
            # Normal event patterns
            event_type = random.choice([
                "user_login_events", "file_access_events",
                "process_events", "network_connections"
            ])
            columns = {
                "username": f"user_{random.randint(100,999)}",
                "time": timestamp
            }
            if event_type == "file_access_events":
                columns["target_path"] = random.choice(NORMAL_PATHS) + f"/doc_{random.randint(1,100)}.txt"
                columns["size"] = random.randint(100, 1_000_000)
                columns["action"] = random.choice(["read", "write"])
            elif event_type == "network_connections":
                columns["remote_address"] = f"192.168.{random.randint(1,10)}.{random.randint(1,254)}"
                columns["remote_port"] = random.choice([80, 443, 3306, 5432])
        
        events.append({
            "name": event_type,
            "unixTime": timestamp,
            "columns": columns
        })
    
    return events

print("✅ Data generation functions ready")

# %% [code]
# Cell 3: Generate Training Dataset

NUM_NORMAL = 500
NUM_SUSPICIOUS = 200
SEQ_LENGTH = 60
FEATURE_DIM = 64

print(f"Generating {NUM_NORMAL} normal + {NUM_SUSPICIOUS} suspicious sequences...")

all_sequences = []
all_labels = []

# Normal sequences
for i in range(NUM_NORMAL):
    events = generate_sequence(is_suspicious=False, seq_length=SEQ_LENGTH)
    encoded = np.array([encode_event(e) for e in events])
    all_sequences.append(encoded)
    all_labels.append(0)
    if (i + 1) % 100 == 0:
        print(f"  Normal: {i + 1}/{NUM_NORMAL}")

# Suspicious sequences
for i in range(NUM_SUSPICIOUS):
    events = generate_sequence(is_suspicious=True, seq_length=SEQ_LENGTH)
    encoded = np.array([encode_event(e) for e in events])
    all_sequences.append(encoded)
    all_labels.append(1)
    if (i + 1) % 50 == 0:
        print(f"  Suspicious: {i + 1}/{NUM_SUSPICIOUS}")

X = np.array(all_sequences, dtype=np.float32)
y = np.array(all_labels, dtype=np.float32)

print(f"\n✅ Dataset ready!")
print(f"  X shape: {X.shape}")  # (700, 60, 64)
print(f"  y shape: {y.shape}")  # (700,)
print(f"  Class distribution: {np.sum(y==0)} normal, {np.sum(y==1)} suspicious")

# %% [code]
# Cell 4: PyTorch Dataset & DataLoader

class InsiderThreatDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.FloatTensor(sequences)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]

# Create dataset and split
full_dataset = InsiderThreatDataset(X, y)

train_size = int(0.7 * len(full_dataset))
val_size = int(0.15 * len(full_dataset))
test_size = len(full_dataset) - train_size - val_size

train_dataset, val_dataset, test_dataset = random_split(
    full_dataset, [train_size, val_size, test_size],
    generator=torch.Generator().manual_seed(42)
)

# DataLoaders
BATCH_SIZE = 32
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

print(f"✅ DataLoaders ready")
print(f"  Train: {len(train_dataset)} samples")
print(f"  Val: {len(val_dataset)} samples")
print(f"  Test: {len(test_dataset)} samples")

# %% [code]
# Cell 5: BiLSTM + Attention Model

class Attention(nn.Module):
    def __init__(self, hidden_dim):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, lstm_output):
        # lstm_output: (batch, seq_len, hidden_dim)
        attn_weights = self.attention(lstm_output)  # (batch, seq_len, 1)
        attn_weights = torch.softmax(attn_weights, dim=1)
        context = torch.sum(lstm_output * attn_weights, dim=1)  # (batch, hidden_dim)
        return context, attn_weights

class InsiderThreatLSTM(nn.Module):
    def __init__(self, input_dim=64, hidden_dim=128, num_layers=2, dropout=0.3):
        super().__init__()
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, hidden_dim)
        
        # BiLSTM layers
        self.lstm = nn.LSTM(
            hidden_dim, hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        
        # Attention
        self.attention = Attention(hidden_dim * 2)  # *2 for bidirectional
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # x: (batch, seq_len, input_dim)
        x = self.input_proj(x)  # (batch, seq_len, hidden_dim)
        
        lstm_out, _ = self.lstm(x)  # (batch, seq_len, hidden_dim*2)
        
        context, attn_weights = self.attention(lstm_out)  # (batch, hidden_dim*2)
        
        output = self.classifier(context)  # (batch, 1)
        return output.squeeze(-1), attn_weights

# Initialize model
model = InsiderThreatLSTM(
    input_dim=FEATURE_DIM,
    hidden_dim=128,
    num_layers=2,
    dropout=0.3
).to(device)

print(f"✅ Model created")
print(f"  Total parameters: {sum(p.numel() for p in model.parameters()):,}")

# %% [code]
# Cell 6: Training Setup

# Loss function with class weights (suspicious events are rarer)
pos_weight = torch.tensor([NUM_NORMAL / NUM_SUSPICIOUS]).to(device)
criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

# Actually use BCE since we have sigmoid in model
criterion = nn.BCELoss()

optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)

# Early stopping
best_val_loss = float('inf')
patience = 10
patience_counter = 0
best_model_state = None

EPOCHS = 50

print("✅ Training setup complete")

# %% [code]
# Cell 7: Training Loop

train_losses = []
val_losses = []
train_accs = []
val_accs = []

print("Starting training...")
print("-" * 60)

for epoch in range(EPOCHS):
    # Training
    model.train()
    train_loss = 0.0
    train_preds = []
    train_true = []
    
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        
        optimizer.zero_grad()
        outputs, _ = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        
        train_loss += loss.item()
        train_preds.extend((outputs > 0.5).cpu().numpy())
        train_true.extend(batch_y.cpu().numpy())
    
    train_loss /= len(train_loader)
    train_acc = accuracy_score(train_true, train_preds)
    train_losses.append(train_loss)
    train_accs.append(train_acc)
    
    # Validation
    model.eval()
    val_loss = 0.0
    val_preds = []
    val_true = []
    
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            outputs, _ = model(batch_x)
            loss = criterion(outputs, batch_y)
            val_loss += loss.item()
            val_preds.extend((outputs > 0.5).cpu().numpy())
            val_true.extend(batch_y.cpu().numpy())
    
    val_loss /= len(val_loader)
    val_acc = accuracy_score(val_true, val_preds)
    val_losses.append(val_loss)
    val_accs.append(val_acc)
    
    # Learning rate scheduler
    scheduler.step(val_loss)
    
    # Early stopping check
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_model_state = model.state_dict().copy()
        patience_counter = 0
        print(f"Epoch {epoch+1:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Train Acc: {train_acc:.3f} | Val Acc: {val_acc:.3f} | ✓ Best")
    else:
        patience_counter += 1
        if (epoch + 1) % 5 == 0:
            print(f"Epoch {epoch+1:02d} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Train Acc: {train_acc:.3f} | Val Acc: {val_acc:.3f}")
    
    if patience_counter >= patience:
        print(f"\n⏹️ Early stopping at epoch {epoch+1}")
        break

# Load best model
if best_model_state:
    model.load_state_dict(best_model_state)

print("\n✅ Training complete!")

# %% [code]
# Cell 8: Plot Training Curves

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Loss curves
ax1.plot(train_losses, label='Train Loss', color='blue')
ax1.plot(val_losses, label='Val Loss', color='orange')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.set_title('Training & Validation Loss')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Accuracy curves
ax2.plot(train_accs, label='Train Accuracy', color='blue')
ax2.plot(val_accs, label='Val Accuracy', color='orange')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.set_title('Training & Validation Accuracy')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# %% [code]
# Cell 9: Evaluate on Test Set

model.eval()
test_preds = []
test_probs = []
test_true = []

with torch.no_grad():
    for batch_x, batch_y in test_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        outputs, _ = model(batch_x)
        test_probs.extend(outputs.cpu().numpy())
        test_preds.extend((outputs > 0.5).cpu().numpy())
        test_true.extend(batch_y.cpu().numpy())

test_preds = np.array(test_preds)
test_probs = np.array(test_probs)
test_true = np.array(test_true)

# Metrics
accuracy = accuracy_score(test_true, test_preds)
f1 = f1_score(test_true, test_preds)
try:
    auc = roc_auc_score(test_true, test_probs)
except:
    auc = 0.0

print("=" * 50)
print("📊 TEST SET RESULTS")
print("=" * 50)
print(f"Accuracy:  {accuracy:.4f}")
print(f"F1-Score:  {f1:.4f}")
print(f"AUC-ROC:   {auc:.4f}")
print()
print("Classification Report:")
print(classification_report(test_true, test_preds, target_names=['Normal', 'Suspicious']))

# Confusion Matrix
cm = confusion_matrix(test_true, test_preds)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Normal', 'Suspicious'],
            yticklabels=['Normal', 'Suspicious'])
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

# %% [code]
# Cell 10: Save Model

# Mount Google Drive to save model
drive.mount('/content/drive')

# Save path
save_path = '/content/drive/MyDrive/HealthSentinel/models/insider_threat_lstm.pt'

import os
os.makedirs(os.path.dirname(save_path), exist_ok=True)

# Save model
torch.save({
    'model_state_dict': model.state_dict(),
    'model_config': {
        'input_dim': FEATURE_DIM,
        'hidden_dim': 128,
        'num_layers': 2,
        'dropout': 0.3
    },
    'metrics': {
        'accuracy': accuracy,
        'f1_score': f1,
        'auc_roc': auc
    },
    'event_types': EVENT_TYPES
}, save_path)

print(f"✅ Model saved to {save_path}")

# %% [code]
# Cell 11: Inference Function (for production use)

def predict_insider_threat(events_list, model, device):
    """
    Predict insider threat probability for a sequence of events.
    
    Args:
        events_list: List of event dictionaries from OSQuery
        model: Trained LSTM model
        device: torch device
    
    Returns:
        risk_score: Float between 0.0 (normal) and 1.0 (suspicious)
        attention_weights: Which events contributed most to the score
    """
    # Encode events
    encoded = np.array([encode_event(e) for e in events_list], dtype=np.float32)
    
    # Pad or truncate to SEQ_LENGTH
    if len(encoded) < SEQ_LENGTH:
        padding = np.zeros((SEQ_LENGTH - len(encoded), FEATURE_DIM), dtype=np.float32)
        encoded = np.vstack([encoded, padding])
    else:
        encoded = encoded[:SEQ_LENGTH]
    
    # Convert to tensor
    x = torch.FloatTensor(encoded).unsqueeze(0).to(device)  # (1, 60, 64)
    
    model.eval()
    with torch.no_grad():
        risk_score, attn_weights = model(x)
    
    return risk_score.item(), attn_weights.squeeze().cpu().numpy()

# Test inference
sample_events = generate_sequence(is_suspicious=True, seq_length=30)
risk, attention = predict_insider_threat(sample_events, model, device)
print(f"Sample prediction - Risk Score: {risk:.4f}")
print(f"  Classification: {'🚨 SUSPICIOUS' if risk > 0.5 else '✓ Normal'}")

# %% [markdown]
# ## 🎉 Training Complete!
# 
# **Next Steps:**
# 1. Download the model from Google Drive
# 2. Copy to `HealthSentinel/models/insider_threat_lstm/`
# 3. Integrate with the log aggregator for real-time detection
