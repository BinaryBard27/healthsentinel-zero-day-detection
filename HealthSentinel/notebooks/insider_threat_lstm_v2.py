"""
HealthSentinel Insider Threat LSTM - Google Colab Training Script v2
====================================================================
PURPOSE: Fix overfitting by using realistic log data with proper regularization.

DATASET: realistic_insider_threat.csv (generated from Windows/Linux/SSH logs)
OUTPUT: insider_threat_lstm_v2.pt (trained model weights)

Upload 'realistic_insider_threat.csv' to Colab before running this!
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 1: Setup
# ═══════════════════════════════════════════════════════════════════════════════
# !pip install torch pandas numpy scikit-learn matplotlib seaborn -q

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Using device: {device}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 2: Load Dataset
# ═══════════════════════════════════════════════════════════════════════════════
# Upload 'realistic_insider_threat.csv' to Colab first!
df = pd.read_csv('realistic_insider_threat.csv')
print(f"📊 Dataset shape: {df.shape}")
print(f"🏷️ Label distribution:\n{df['label'].value_counts()}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 3: Dataset Class
# ═══════════════════════════════════════════════════════════════════════════════
class InsiderThreatDataset(Dataset):
    def __init__(self, df, seq_length=20):
        self.seq_length = seq_length
        self.features = df[[f"f{i}" for i in range(64)]].values
        self.labels = df['label'].values
        
    def __len__(self):
        return len(self.features) // self.seq_length
    
    def __getitem__(self, idx):
        start = idx * self.seq_length
        end = start + self.seq_length
        
        seq = self.features[start:end]
        label = int(self.labels[start:end].mean() > 0.5)  # Majority vote
        
        return torch.FloatTensor(seq), torch.FloatTensor([label])

dataset = InsiderThreatDataset(df, seq_length=20)
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
# CELL 4: Model Definition (Anti-Overfitting Architecture)
# ═══════════════════════════════════════════════════════════════════════════════
class InsiderThreatLSTM(nn.Module):
    def __init__(self, input_dim=64, hidden_dim=64, num_layers=2, dropout=0.4):
        super(InsiderThreatLSTM, self).__init__()
        
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
        
        # Attention mechanism
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.Tanh(),
            nn.Linear(64, 1)
        )
        
        # Classifier with L2 regularization (via optimizer)
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
        # x: (batch, seq_len, input_dim)
        batch_size, seq_len, _ = x.size()
        
        # Embedding
        x = x.view(-1, x.size(-1))
        x = self.embedding(x)
        x = self.bn1(x)
        x = x.view(batch_size, seq_len, -1)
        
        # LSTM
        lstm_out, _ = self.lstm(x)
        lstm_out = self.dropout(lstm_out)
        
        # Attention
        attn_weights = torch.softmax(self.attention(lstm_out), dim=1)
        context = torch.sum(lstm_out * attn_weights, dim=1)
        
        # Classifier
        out = self.classifier(context)
        return out

model = InsiderThreatLSTM().to(device)
print(f"🧠 Model parameters: {sum(p.numel() for p in model.parameters()):,}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 5: Training Setup
# ═══════════════════════════════════════════════════════════════════════════════
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001, weight_decay=1e-4)  # L2 regularization
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=3, factor=0.5)

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 6: Training Loop
# ═══════════════════════════════════════════════════════════════════════════════
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
    all_preds, all_labels, all_probs = [], [], []
    
    with torch.no_grad():
        for seqs, labels in loader:
            seqs, labels = seqs.to(device), labels.to(device)
            outputs = model(seqs)
            loss = criterion(outputs, labels)
            
            total_loss += loss.item()
            all_probs.extend(outputs.cpu().numpy())
            all_preds.extend((outputs > 0.5).cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
    
    acc = accuracy_score(all_labels, all_preds)
    prec, rec, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='binary', zero_division=0)
    
    return total_loss / len(loader), acc, prec, rec, f1

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 7: Train the Model
# ═══════════════════════════════════════════════════════════════════════════════
NUM_EPOCHS = 25
best_val_loss = float('inf')
history = {'train_loss': [], 'val_loss': [], 'val_acc': []}

print("🚀 Starting training...")
for epoch in range(NUM_EPOCHS):
    train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer)
    val_loss, val_acc, val_prec, val_rec, val_f1 = validate(model, val_loader, criterion)
    
    history['train_loss'].append(train_loss)
    history['val_loss'].append(val_loss)
    history['val_acc'].append(val_acc)
    
    scheduler.step(val_loss)
    
    print(f"Epoch {epoch+1}/{NUM_EPOCHS} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.4f} | F1: {val_f1:.4f}")
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'insider_threat_lstm_v2.pt')
        print("✅ Model saved!")

print("\n🎯 Training complete!")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 8: Final Test Evaluation
# ═══════════════════════════════════════════════════════════════════════════════
model.load_state_dict(torch.load('insider_threat_lstm_v2.pt'))
test_loss, test_acc, test_prec, test_rec, test_f1 = validate(model, test_loader, criterion)

print(f"\n📊 Test Results:")
print(f"Accuracy: {test_acc:.4f}")
print(f"Precision: {test_prec:.4f}")
print(f"Recall: {test_rec:.4f}")
print(f"F1-Score: {test_f1:.4f}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 9: Plot Training History
# ═══════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 4))

ax1.plot(history['train_loss'], label='Train Loss')
ax1.plot(history['val_loss'], label='Val Loss')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Loss')
ax1.set_title('Training vs Validation Loss')
ax1.legend()

ax2.plot(history['val_acc'], label='Val Accuracy', color='green')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Accuracy')
ax2.set_title('Validation Accuracy Over Time')
ax2.legend()

plt.tight_layout()
plt.show()

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 10: Confusion Matrix
# ═══════════════════════════════════════════════════════════════════════════════
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
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Normal', 'Threat'], yticklabels=['Normal', 'Threat'])
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.show()

print("\n✅ Download 'insider_threat_lstm_v2.pt' and use it in the HealthSentinel platform!")
