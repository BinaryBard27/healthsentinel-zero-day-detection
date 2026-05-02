"""
HealthSentinel Insider Threat LSTM Training - Google Colab
===========================================================
Upload 'merged_all_logs.csv' to Colab before running!

This script:
1. Loads raw system logs (Windows, Linux, SSH, etc.)
2. Extracts features and creates sequences
3. Generates synthetic threat labels
4. Trains BiLSTM with anti-overfitting measures
5. Outputs: insider_threat_lstm_v2.pt
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 1: Install Dependencies & Setup
# ═══════════════════════════════════════════════════════════════════════════════
!pip install torch pandas numpy scikit-learn matplotlib seaborn -q

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import random

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Device: {device}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 2: Load & Preprocess Raw Logs
# ═══════════════════════════════════════════════════════════════════════════════
print("📂 Loading merged logs...")
df = pd.read_csv('merged_all_logs.csv', on_bad_lines='skip')
print(f"📊 Original shape: {df.shape}")
print(f"📋 Columns: {list(df.columns)[:10]}")

# Sample if too large (for faster training)
if len(df) > 50000:
    df = df.sample(50000, random_state=42)
    print(f"⚡ Sampled to {len(df)} rows for faster training")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 3: Feature Engineering
# ═══════════════════════════════════════════════════════════════════════════════
def extract_features(row):
    """Convert log row to 64-dim feature vector"""
    features = np.zeros(64)
    
    # Event type encoding (indices 0-9)
    content = str(row.get('Content', '')).lower()
    if 'login' in content or 'session' in content:
        features[0] = 1.0  # user_login
    elif 'file' in content:
        features[1] = 1.0  # file_access
    elif 'network' in content or 'connection' in content:
        features[2] = 1.0  # network
    else:
        features[4] = 1.0  # process (default)
    
    # Time features (index 10)
    try:
        hour = random.randint(0, 23)  # Simulate hour
        features[10] = hour / 24.0
    except:
        features[10] = 0.5
    
    # Add random noise to prevent overfitting
    features += np.random.normal(0, 0.03, 64)
    
    return features

print("🔧 Extracting features from logs...")
feature_vectors = []
for idx, row in df.iterrows():
    feature_vectors.append(extract_features(row))
    if idx % 10000 == 0:
        print(f"  Processed {idx}/{len(df)} rows")

features_array = np.array(feature_vectors)
print(f"✅ Features shape: {features_array.shape}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 4: Generate Labels (Synthetic Threat Detection)
# ═══════════════════════════════════════════════════════════════════════════════
print("🏷️ Generating labels...")

# 90% Normal, 10% Threat
labels = np.zeros(len(features_array))
threat_indices = np.random.choice(len(labels), size=int(len(labels)*0.1), replace=False)
labels[threat_indices] = 1

# Inject attack patterns into threat samples
for idx in threat_indices:
    if idx < len(features_array):
        # Off-hours activity
        features_array[idx, 10] = random.choice([0.08, 0.12, 0.95, 0.99])  # 2am, 3am, 11pm, midnight
        # Sensitive access marker
        features_array[idx, 18] = 1.0
        # External connection
        features_array[idx, 22] = 1.0

print(f"✅ Labels: {(labels==0).sum()} normal, {(labels==1).sum()} threats")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 5: Create Dataset
# ═══════════════════════════════════════════════════════════════════════════════
class LogSequenceDataset(Dataset):
    def __init__(self, features, labels, seq_len=20):
        self.seq_len = seq_len
        self.features = features
        self.labels = labels
        
    def __len__(self):
        return len(self.features) // self.seq_len
    
    def __getitem__(self, idx):
        start = idx * self.seq_len
        end = start + self.seq_len
        
        seq = self.features[start:end]
        label = int(self.labels[start:end].mean() > 0.5)  # Majority vote
        
        return torch.FloatTensor(seq), torch.FloatTensor([label])

dataset = LogSequenceDataset(features_array, labels, seq_len=20)
print(f"🔢 Total sequences: {len(dataset)}")

# Split: 70% train, 15% val, 15% test
train_size = int(0.7 * len(dataset))
val_size = int(0.15 * len(dataset))
test_size = len(dataset) - train_size - val_size

train_ds, val_ds, test_ds = random_split(dataset, [train_size, val_size, test_size])

train_loader = DataLoader(train_ds, batch_size=32, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=32, shuffle=False)
test_loader = DataLoader(test_ds, batch_size=32, shuffle=False)

print(f"✅ Train: {len(train_ds)} | Val: {len(val_ds)} | Test: {len(test_ds)}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 6: Model Architecture
# ═══════════════════════════════════════════════════════════════════════════════
class InsiderThreatLSTM(nn.Module):
    def __init__(self, input_dim=64, hidden_dim=64, num_layers=2, dropout=0.4):
        super().__init__()
        
        self.embedding = nn.Linear(input_dim, 128)
        self.bn1 = nn.BatchNorm1d(128)
        
        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0,
            bidirectional=True
        )
        
        self.dropout = nn.Dropout(dropout)
        
        # Attention
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        
        # Classifier
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        batch_size, seq_len, _ = x.size()
        
        # Embedding
        x = x.view(-1, x.size(-1))
        x = self.embedding(x)
        x = self.bn1(x)
        x = x.view(batch_size, seq_len, -1)
        
        # BiLSTM
        lstm_out, _ = self.lstm(x)
        lstm_out = self.dropout(lstm_out)
        
        # Attention
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)
        context = torch.sum(lstm_out * attn_weights, dim=1)
        
        # Classify
        return self.classifier(context)

model = InsiderThreatLSTM().to(device)
print(f"🧠 Parameters: {sum(p.numel() for p in model.parameters()):,}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 7: Training Setup
# ═══════════════════════════════════════════════════════════════════════════════
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)

def train_epoch(model, loader, criterion, optimizer):
    model.train()
    total_loss = 0
    all_preds, all_labels = [], []
    
    for seqs, labels in loader:
        seqs, labels = seqs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(seqs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        all_preds.extend((outputs > 0.5).cpu().numpy())
        all_labels.extend(labels.cpu().numpy())
    
    acc = accuracy_score(all_labels, all_preds)
    return total_loss / len(loader), acc

def validate(model, loader, criterion):
    model.eval()
    total_loss = 0
    all_preds, all_labels = [], []
    
    with torch.no_grad():
        for seqs, labels in loader:
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            all_preds.extend((outputs > 0.5).cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    acc = accuracy_score(all_labels, all_preds)
    prec, rec, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='binary', zero_division=0)
    
    return total_loss / len(loader), acc, prec, rec, f1

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 8: Train!
# ═══════════════════════════════════════════════════════════════════════════════
NUM_EPOCHS = 20
best_val_loss = float('inf')
history = {'train_loss': [], 'val_loss': [], 'val_acc': []}

print("🚀 Starting training...\n")
for epoch in range(NUM_EPOCHS):
    train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
    val_loss, val_acc, val_prec, val_rec, val_f1 = validate(model, val_loader, criterion)
    
    history['train_loss'].append(train_loss)
    history['val_loss'].append(val_loss)
    history['val_acc'].append(val_acc)
    
    scheduler.step(val_loss)
    
    print(f"Epoch {epoch+1:02d}/{NUM_EPOCHS} | TrLoss: {train_loss:.4f} | ValLoss: {val_loss:.4f} | ValAcc: {val_acc:.4f} | F1: {val_f1:.4f}")
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'insider_threat_lstm_v2.pt')
        print("  ✅ Saved!")

print("\n🎯 Training complete!")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 9: Evaluate
# ═══════════════════════════════════════════════════════════════════════════════
model.load_state_dict(torch.load('insider_threat_lstm_v2.pt'))
test_loss, test_acc, test_prec, test_rec, test_f1 = validate(model, test_loader, criterion)

print(f"\n📊 TEST RESULTS:")
print(f"  Accuracy:  {test_acc:.4f}")
print(f"  Precision: {test_prec:.4f}")
print(f"  Recall:    {test_rec:.4f}")
print(f"  F1-Score:  {test_f1:.4f}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 10: Visualizations
# ═══════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))

ax1.plot(history['train_loss'], label='Train Loss', color='blue')
ax1.plot(history['val_loss'], label='Val Loss', color='orange')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.set_title('Training Progress')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.plot(history['val_acc'], label='Val Accuracy', color='green')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.set_title('Validation Accuracy')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()

# Confusion Matrix
model.eval()
all_preds, all_labels = [], []
with torch.no_grad():
    for seqs, labels in test_loader:
        seqs = seqs.to(device)
        outputs = model(seqs)
        all_preds.extend((outputs > 0.5).cpu().numpy())
        all_labels.extend(labels.cpu().numpy())

cm = confusion_matrix(all_labels, all_preds)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Normal', 'Threat'], 
            yticklabels=['Normal', 'Threat'])
plt.title('Confusion Matrix')
plt.ylabel('True')
plt.xlabel('Predicted')
plt.show()

print("\n✅ Model saved as 'insider_threat_lstm_v2.pt'")
print("📥 Download it and place in: HealthSentinel/models/insider_threat_lstm/")
