"""
LSTM Autoencoder Training - Google Colab Version
===============================================

Upload 'merged_all_logs_complete.csv' to Colab before running!

This is the PROPER insider threat detection architecture:
- LSTM Autoencoder (NOT classification)
- Trains ONLY on normal behavior
- Detects threats via reconstruction error
- Per-user behavioral baselines

Author: HealthSentinel Team
"""

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 1: Install Dependencies & Upload Data
# ═══════════════════════════════════════════════════════════════════════════════

!pip install torch pandas numpy scikit-learn matplotlib seaborn -q

from google.colab import files
import io

print("📤 Please upload 'merged_all_logs_complete.csv'")
uploaded = files.upload()

# Save uploaded file
for filename in uploaded.keys():
    print(f"✅ Uploaded: {filename} ({len(uploaded[filename])/1024/1024:.1f} MB)")

DATA_FILE = list(uploaded.keys())[0]

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 2: Imports & Setup
# ═══════════════════════════════════════════════════════════════════════════════

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from collections import defaultdict, deque
import warnings
warnings.filterwarnings('ignore')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 Device: {device}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 3: Configuration
# ═══════════════════════════════════════════════════════════════════════════════

CONFIG = {
    'sample_size': 100000,  # Faster training for Colab
    'window_minutes': 5,
    'sequence_length': 30,
    'stride': 5,
    'input_dim': 12,
    'hidden_dim': 128,
    'latent_dim': 64,
    'num_layers': 2,
    'dropout': 0.2,
    'batch_size': 64,
    'epochs': 30,  # Reduced for Colab
    'learning_rate': 0.001,
}

print("⚙️  Configuration:")
for k, v in CONFIG.items():
    print(f"   {k}: {v}")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 4: Feature Aggregator (Inline)
# ═══════════════════════════════════════════════════════════════════════════════

class BehavioralFeatureAggregator:
    def __init__(self, window_minutes=5):
        self.window_minutes = window_minutes
        self.feature_names = [
            'login_hour_normalized', 'file_access_count', 'sensitive_file_flag',
            'new_process_flag', 'network_entropy', 'privilege_level',
            'usb_event_flag', 'data_transfer_size_log', 'unique_files_accessed',
            'command_diversity', 'afterhours_flag', 'weekend_flag'
        ]
    
    def aggregate_events_to_timesteps(self, df):
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp']).sort_values(['user', 'timestamp'])
        df['time_window'] = df['timestamp'].dt.floor(f'{self.window_minutes}T')
        
        aggregated = []
        for (user, window), group in df.groupby(['user', 'time_window']):
            features = self._extract_window_features(group, window)
            features['user'] = user
            features['timestamp'] = window
            aggregated.append(features)
        
        return pd.DataFrame(aggregated)
    
    def _extract_window_features(self, group, window_time):
        hour = group.iloc[0]['timestamp'].hour
        day_of_week = group.iloc[0]['timestamp'].dayofweek
        
        phi_keywords = ['patient', 'ehr', 'medical', 'lab', 'imaging', 'pacs']
        content_str = ' '.join(group.get('Content', group.get('action', '')).fillna('').astype(str).str.lower())
        resource_str = ' '.join(group.get('resource', group.get('Resource', '')).fillna('').astype(str).str.lower())
        
        return {
            'login_hour_normalized': hour / 24.0,
            'afterhours_flag': 1 if (hour < 7 or hour > 19) else 0,
            'weekend_flag': 1 if day_of_week >= 5 else 0,
            'file_access_count': len(group),
            'unique_files_accessed': group.get('resource', group.get('Resource', pd.Series([]))).nunique(),
            'sensitive_file_flag': 1 if any(kw in resource_str for kw in phi_keywords) else 0,
            'new_process_flag': 1 if 'process' in content_str else 0,
            'command_diversity': group.get('action', group.get('Action', pd.Series([]))).nunique(),
            'network_entropy': self._calculate_entropy(group.get('source_ip', pd.Series([]))),
            'privilege_level': 1 if 'admin' in content_str or 'sudo' in content_str else 0,
            'usb_event_flag': 1 if 'usb' in content_str else 0,
            'data_transfer_size_log': np.log1p(group.get('bytes_transferred', pd.Series([0])).sum()),
        }
    
    def _calculate_entropy(self, series):
        if len(series) == 0:
            return 0.0
        value_counts = series.value_counts()
        probabilities = value_counts / len(series)
        return float(-np.sum(probabilities * np.log2(probabilities + 1e-10)))
    
    def create_user_sequences(self, timestep_df, sequence_length=30, stride=1):
        sequences = []
        user_ids = []
        
        for user in timestep_df['user'].unique():
            user_data = timestep_df[timestep_df['user'] == user].sort_values('timestamp')
            user_features = user_data[self.feature_names].values
            
            for i in range(0, len(user_features) - sequence_length + 1, stride):
                seq = user_features[i:i + sequence_length]
                sequences.append(seq)
                user_ids.append(user)
        
        return np.array(sequences, dtype=np.float32), user_ids

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 5: LSTM Autoencoder Model
# ═══════════════════════════════════════════════════════════════════════════════

class InsiderThreatAutoencoder(nn.Module):
    def __init__(self, input_dim, hidden_dim, latent_dim, num_layers=2, dropout=0.2):
        super().__init__()
        
        self.encoder_lstm = nn.LSTM(
            input_size=input_dim, hidden_size=hidden_dim, num_layers=num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0
        )
        self.encoder_fc = nn.Sequential(nn.Linear(hidden_dim, latent_dim), nn.Tanh())
        
        self.decoder_fc = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(
            input_size=hidden_dim, hidden_size=hidden_dim, num_layers=num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0
        )
        self.output_fc = nn.Linear(hidden_dim, input_dim)
    
    def encode(self, x):
        lstm_out, (hidden, cell) = self.encoder_lstm(x)
        return self.encoder_fc(hidden[-1])
    
    def decode(self, latent, seq_len):
        decoder_input = self.decoder_fc(latent).unsqueeze(1).repeat(1, seq_len, 1)
        lstm_out, _ = self.decoder_lstm(decoder_input)
        return self.output_fc(lstm_out)
    
    def forward(self, x):
        latent = self.encode(x)
        return self.decode(latent, x.size(1))

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 6: Load & Preprocess Data
# ═══════════════════════════════════════════════════════════════════════════════

print("📂 Loading data...")
df = pd.read_csv(DATA_FILE, on_bad_lines='skip')
print(f"   Loaded: {len(df):,} rows")

# Sample for faster training
if CONFIG['sample_size'] and len(df) > CONFIG['sample_size']:
    df = df.sample(CONFIG['sample_size'], random_state=42)
    print(f"   Sampled: {len(df):,} rows")

# Normalize columns
column_mapping = {
    'User': 'user', 'Username': 'user', 'Action': 'action', 'Event': 'action',
    'Resource': 'resource', 'Target': 'resource', 'Timestamp': 'timestamp',
    'Time': 'timestamp', 'Source': 'source_ip', 'Bytes': 'bytes_transferred',
    'Label': 'label', 'is_threat': 'label'
}
for old, new in column_mapping.items():
    if old in df.columns and new not in df.columns:
        df[new] = df[old]

# Fill missing
if 'resource' not in df.columns:
    df['resource'] = 'unknown'
if 'source_ip' not in df.columns:
    df['source_ip'] = 'unknown'
if 'bytes_transferred' not in df.columns:
    df['bytes_transferred'] = 0

# Filter to normal behavior
if 'label' in df.columns:
    df_normal = df[df['label'] == 0].copy()
    print(f"   Normal behavior: {len(df_normal):,} ({len(df_normal)/len(df)*100:.1f}%)")
else:
    df_normal = df.copy()
    print("   No labels found, using all data")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 7: Feature Aggregation
# ═══════════════════════════════════════════════════════════════════════════════

aggregator = BehavioralFeatureAggregator(window_minutes=CONFIG['window_minutes'])

print("\n🔧 Aggregating to time-steps...")
timestep_df = aggregator.aggregate_events_to_timesteps(df_normal)
print(f"✅ Created {len(timestep_df):,} time-steps")

print("\n🔧 Creating sequences...")
sequences, user_ids = aggregator.create_user_sequences(
    timestep_df, CONFIG['sequence_length'], CONFIG['stride']
)
print(f"✅ Created {len(sequences):,} sequences from {len(set(user_ids))} users")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 8: Split Data by Users
# ═══════════════════════════════════════════════════════════════════════════════

unique_users = list(set(user_ids))
np.random.shuffle(unique_users)

n_train = int(len(unique_users) * 0.7)
n_val = int(len(unique_users) * 0.15)

train_users = set(unique_users[:n_train])
val_users = set(unique_users[n_train:n_train + n_val])
test_users = set(unique_users[n_train + n_val:])

train_indices = [i for i, u in enumerate(user_ids) if u in train_users]
val_indices = [i for i, u in enumerate(user_ids) if u in val_users]
test_indices = [i for i, u in enumerate(user_ids) if u in test_users]

train_seqs = sequences[train_indices]
val_seqs = sequences[val_indices]
test_seqs = sequences[test_indices]

print(f"Train: {len(train_users)} users, {len(train_seqs):,} sequences")
print(f"Val:   {len(val_users)} users, {len(val_seqs):,} sequences")
print(f"Test:  {len(test_users)} users, {len(test_seqs):,} sequences")

# DataLoaders
class SeqDataset(Dataset):
    def __init__(self, seqs):
        self.seqs = torch.FloatTensor(seqs)
    def __len__(self):
        return len(self.seqs)
    def __getitem__(self, idx):
        return self.seqs[idx], self.seqs[idx]

train_loader = DataLoader(SeqDataset(train_seqs), batch_size=CONFIG['batch_size'], shuffle=True)
val_loader = DataLoader(SeqDataset(val_seqs), batch_size=CONFIG['batch_size'], shuffle=False)
test_loader = DataLoader(SeqDataset(test_seqs), batch_size=CONFIG['batch_size'], shuffle=False)

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 9: Build Model & Train
# ═══════════════════════════════════════════════════════════════════════════════

model = InsiderThreatAutoencoder(
    CONFIG['input_dim'], CONFIG['hidden_dim'], CONFIG['latent_dim'],
    CONFIG['num_layers'], CONFIG['dropout']
).to(device)

print(f"🧠 Model parameters: {sum(p.numel() for p in model.parameters()):,}")

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=CONFIG['learning_rate'])
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)

# Training loop
history = {'train_loss': [], 'val_loss': []}
best_val_loss = float('inf')

print("\n🚀 Training...\n")
for epoch in range(CONFIG['epochs']):
    # Train
    model.train()
    train_loss = 0
    for seqs, targets in train_loader:
        seqs, targets = seqs.to(device), targets.to(device)
        optimizer.zero_grad()
        reconstructed = model(seqs)
        loss = criterion(reconstructed, targets)
        loss.backward()
        optimizer.step()
        train_loss += loss.item()
    train_loss /= len(train_loader)
    
    # Validate
    model.eval()
    val_loss = 0
    with torch.no_grad():
        for seqs, targets in val_loader:
            seqs, targets = seqs.to(device), targets.to(device)
            reconstructed = model(seqs)
            loss = criterion(reconstructed, targets)
            val_loss += loss.item()
    val_loss /= len(val_loader)
    
    history['train_loss'].append(train_loss)
    history['val_loss'].append(val_loss)
    scheduler.step(val_loss)
    
    print(f"Epoch {epoch+1:2d}/{CONFIG['epochs']} | Train: {train_loss:.6f} | Val: {val_loss:.6f}")
    
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'insider_threat_autoencoder.pt')
        print("  ✅ Saved!")

print("\n✅ Training complete!")

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 10: Compute User Baselines
# ═══════════════════════════════════════════════════════════════════════════════

print("\n📊 Computing per-user baselines...")

model.load_state_dict(torch.load('insider_threat_autoencoder.pt'))
model.eval()

baselines = {}
unique_users_list = sorted(set(user_ids))

with torch.no_grad():
    for user in unique_users_list:
        user_indices = [i for i, u in enumerate(user_ids) if u == user]
        user_seqs = torch.FloatTensor(sequences[user_indices]).to(device)
        
        reconstructed = model(user_seqs)
        errors = torch.mean((user_seqs - reconstructed) ** 2, dim=(1, 2)).cpu().numpy()
        
        baselines[user] = {
            'mean_error': float(np.mean(errors)),
            'std_error': float(np.std(errors)),
            'p95_error': float(np.percentile(errors, 95)),
            'p99_error': float(np.percentile(errors, 99)),
        }

print(f"✅ Computed baselines for {len(baselines)} users")

# Save baselines
import json
with open('user_baselines.json', 'w') as f:
    json.dump(baselines, f, indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 11: Evaluate & Visualize
# ═══════════════════════════════════════════════════════════════════════════════

print("\n📊 Evaluation...")

test_errors = []
with torch.no_grad():
    for seqs, _ in test_loader:
        seqs = seqs.to(device)
        reconstructed = model(seqs)
        errors = torch.mean((seqs - reconstructed) ** 2, dim=(1, 2))
        test_errors.extend(errors.cpu().numpy())

test_errors = np.array(test_errors)

print(f"\nTest Reconstruction Error:")
print(f"  Mean: {np.mean(test_errors):.6f}")
print(f"  Median: {np.median(test_errors):.6f}")
print(f"  P95: {np.percentile(test_errors, 95):.6f}")
print(f"  P99: {np.percentile(test_errors, 99):.6f}")

# Plot training curve
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history['train_loss'], label='Train Loss')
ax1.plot(history['val_loss'], label='Val Loss')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Reconstruction Loss (MSE)')
ax1.set_title('Training Progress')
ax1.legend()
ax1.grid(alpha=0.3)

ax2.hist(test_errors, bins=50, edgecolor='black', alpha=0.7)
ax2.axvline(np.percentile(test_errors, 95), color='r', linestyle='--', label='95th percentile')
ax2.set_xlabel('Reconstruction Error')
ax2.set_ylabel('Frequency')
ax2.set_title('Error Distribution')
ax2.legend()
ax2.grid(alpha=0.3)

plt.tight_layout()
plt.show()

# ═══════════════════════════════════════════════════════════════════════════════
# CELL 12: Download Model Files
# ═══════════════════════════════════════════════════════════════════════════════

print("\n📥 Download these files:")
print("   1. insider_threat_autoencoder.pt")
print("   2. user_baselines.json")
print("\nPlace in: HealthSentinel/models/insider_threat_autoencoder/")

files.download('insider_threat_autoencoder.pt')
files.download('user_baselines.json')

print("\n✅ LSTM Autoencoder training complete!")
print("This model detects insider threats through behavioral sequence reconstruction.")
print("High reconstruction error = behavioral deviation = potential threat.")
