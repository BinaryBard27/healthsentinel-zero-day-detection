"""
LSTM Autoencoder for Insider Threat Detection - Production Training Script
===========================================================================

This trains a proper LSTM autoencoder that detects insider threats through
behavioral sequence reconstruction, NOT classification.

Architecture:
- Trains ONLY on normal behavior
- Uses reconstruction error for anomaly detection
- Per-user behavioral baselines
- Sliding window sequences

Author: HealthSentinel Team
Usage:
    python train_lstm_autoencoder.py
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import json
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from behavioral_feature_aggregator import BehavioralFeatureAggregator, load_and_prepare_data

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Data paths
    'data_path': r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs_complete.csv',
    'output_dir': r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_autoencoder',
    
    # Data preprocessing
    'sample_size': None,  # None = use all data, or set to e.g., 100000 for testing
    'window_minutes': 5,  # Time window for aggregation
    'sequence_length': 30,  # Number of time-steps per sequence
    'stride': 5,  # Sliding window stride
    
    # Model architecture
    'input_dim': 12,  # Number of features per time-step
    'hidden_dim': 128,
    'latent_dim': 64,
    'num_layers': 2,
    'dropout': 0.2,
    
    # Training
    'batch_size': 64,
    'epochs': 50,
    'learning_rate': 0.001,
    'weight_decay': 1e-5,
    'train_split': 0.7,
    'val_split': 0.15,
    'test_split': 0.15,
    
    # Device
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    
    # Anomaly detection thresholds
    'anomaly_threshold_percentile': 95,  # 95th percentile of training errors
}

print("="*80)
print(" " * 20 + "LSTM AUTOENCODER TRAINING")
print(" " * 15 + "Insider Threat Detection via Reconstruction")
print("="*80)
print(f"\n🔥 Device: {CONFIG['device']}")
print(f"📂 Data: {CONFIG['data_path']}")
print(f"💾 Output: {CONFIG['output_dir']}\n")

# Create output directory
os.makedirs(CONFIG['output_dir'], exist_ok=True)


# ============================================================================
# LSTM AUTOENCODER MODEL
# ============================================================================

class InsiderThreatAutoencoder(nn.Module):
    """
    LSTM Autoencoder for behavioral sequence reconstruction.
    
    Architecture:
    - Encoder: Compresses behavioral sequence into latent representation
    - Decoder: Reconstructs original sequence from latent vector
    - Loss: Reconstruction error (MSE)
    - Anomaly: High reconstruction error = behavioral deviation
    """
    
    def __init__(self, input_dim, hidden_dim, latent_dim, num_layers=2, dropout=0.2):
        super(InsiderThreatAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.num_layers = num_layers
        
        # Encoder: Compresses sequence to latent vector
        self.encoder_lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.encoder_fc = nn.Sequential(
            nn.Linear(hidden_dim, latent_dim),
            nn.Tanh()
        )
        
        # Decoder: Reconstructs sequence from latent vector
        self.decoder_fc = nn.Linear(latent_dim, hidden_dim)
        
        self.decoder_lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.output_fc = nn.Linear(hidden_dim, input_dim)
    
    def encode(self, x):
        """
        Encode sequence to latent representation.
        
        Args:
            x: [batch_size, seq_len, input_dim]
        
        Returns:
            latent: [batch_size, latent_dim]
        """
        # LSTM forward pass
        lstm_out, (hidden, cell) = self.encoder_lstm(x)
        
        # Use final hidden state
        latent = self.encoder_fc(hidden[-1])
        
        return latent
    
    def decode(self, latent, seq_len):
        """
        Decode latent vector to sequence.
        
        Args:
            latent: [batch_size, latent_dim]
            seq_len: sequence length to generate
        
        Returns:
            reconstructed: [batch_size, seq_len, input_dim]
        """
        batch_size = latent.size(0)
        
        # Expand latent to sequence
        decoder_input = self.decoder_fc(latent)  # [batch, hidden_dim]
        decoder_input = decoder_input.unsqueeze(1).repeat(1, seq_len, 1)  # [batch, seq_len, hidden_dim]
        
        # LSTM decode
        lstm_out, _ = self.decoder_lstm(decoder_input)
        
        # Reconstruct features
        reconstructed = self.output_fc(lstm_out)
        
        return reconstructed
    
    def forward(self, x):
        """
        Full autoencoder forward pass.
        
        Args:
            x: [batch_size, seq_len, input_dim]
        
        Returns:
            reconstructed: [batch_size, seq_len, input_dim]
        """
        seq_len = x.size(1)
        latent = self.encode(x)
        reconstructed = self.decode(latent, seq_len)
        return reconstructed
    
    def get_reconstruction_error(self, x, reduction='mean'):
        """
        Compute reconstruction error.
        
        Args:
            x: Original sequence
            reduction: 'mean', 'sum', or 'none'
        
        Returns:
            Reconstruction error
        """
        with torch.no_grad():
            reconstructed = self.forward(x)
            
            if reduction == 'none':
                # Per-sample error
                error = torch.mean((x - reconstructed) ** 2, dim=(1, 2))
            elif reduction == 'mean':
                error = torch.mean((x - reconstructed) ** 2)
            elif reduction == 'sum':
                error = torch.sum((x - reconstructed) ** 2)
            
            return error


# ============================================================================
# DATASET
# ============================================================================

class BehavioralSequenceDataset(Dataset):
    """Dataset of behavioral sequences for autoencoder training"""
    
    def __init__(self, sequences):
        """
        Args:
            sequences: numpy array [num_sequences, seq_len, num_features]
        """
        self.sequences = torch.FloatTensor(sequences)
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        # Return same sequence as input and target (autoencoder)
        return self.sequences[idx], self.sequences[idx]


# ============================================================================
# TRAINING
# ============================================================================

def train_epoch(model, dataloader, criterion, optimizer, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    for batch_idx, (sequences, targets) in enumerate(dataloader):
        sequences = sequences.to(device)
        targets = targets.to(device)
        
        # Forward pass
        optimizer.zero_grad()
        reconstructed = model(sequences)
        
        # Reconstruction loss
        loss = criterion(reconstructed, targets)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def validate(model, dataloader, criterion, device):
    """Validate model"""
    model.eval()
    total_loss = 0
    
    with torch.no_grad():
        for sequences, targets in dataloader:
            sequences = sequences.to(device)
            targets = targets.to(device)
            
            reconstructed = model(sequences)
            loss = criterion(reconstructed, targets)
            
            total_loss += loss.item()
    
    return total_loss / len(dataloader)


def compute_user_baselines(model, sequences, user_ids, device):
    """
    Compute per-user reconstruction error baselines.
    
    Args:
        model: Trained autoencoder
        sequences: All sequences
        user_ids: User ID for each sequence
        device: torch device
    
    Returns:
        Dictionary of user baselines
    """
    print("\n📊 Computing per-user baselines...")
    
    model.eval()
    baselines = {}
    
    unique_users = sorted(set(user_ids))
    
    with torch.no_grad():
        for user in unique_users:
            # Get user's sequences
            user_indices = [i for i, u in enumerate(user_ids) if u == user]
            user_seqs = torch.FloatTensor(sequences[user_indices]).to(device)
            
            # Compute reconstruction errors
            errors = model.get_reconstruction_error(user_seqs, reduction='none')
            errors = errors.cpu().numpy()
            
            # Store baseline statistics
            baselines[user] = {
                'mean_error': float(np.mean(errors)),
                'std_error': float(np.std(errors)),
                'median_error': float(np.median(errors)),
                'p95_error': float(np.percentile(errors, 95)),
                'p99_error': float(np.percentile(errors, 99)),
                'num_sequences': len(errors)
            }
            
            if len(baselines) % 100 == 0:
                print(f"  Processed {len(baselines)}/{len(unique_users)} users...")
    
    print(f"✅ Computed baselines for {len(baselines)} users")
    
    return baselines


# ============================================================================
# MAIN TRAINING PIPELINE
# ============================================================================

def main():
    # Step 1: Load and prepare data
    print("\n" + "="*80)
    print("STEP 1: LOADING DATA")
    print("="*80)
    
    df = load_and_prepare_data(CONFIG['data_path'], CONFIG['sample_size'])
    
    # Step 2: Filter to normal behavior only
    print("\n" + "="*80)
    print("STEP 2: FILTERING TO NORMAL BEHAVIOR")
    print("="*80)
    
    aggregator = BehavioralFeatureAggregator(window_minutes=CONFIG['window_minutes'])
    df_normal = aggregator.filter_normal_behavior(df)
    
    # Step 3: Aggregate to time-steps
    print("\n" + "="*80)
    print("STEP 3: FEATURE AGGREGATION")
    print("="*80)
    
    timestep_df = aggregator.aggregate_events_to_timesteps(df_normal)
    
    # Step 4: Create sequences
    print("\n" + "="*80)
    print("STEP 4: SEQUENCE CREATION")
    print("="*80)
    
    user_sequences, sequences_array, user_ids = aggregator.create_user_sequences(
        timestep_df,
        sequence_length=CONFIG['sequence_length'],
        stride=CONFIG['stride']
    )
    
    # Step 5: Split data by users (prevent data leakage)
    print("\n" + "="*80)
    print("STEP 5: SPLITTING DATA BY USERS")
    print("="*80)
    
    unique_users = list(set(user_ids))
    np.random.shuffle(unique_users)
    
    n_train = int(len(unique_users) * CONFIG['train_split'])
    n_val = int(len(unique_users) * CONFIG['val_split'])
    
    train_users = set(unique_users[:n_train])
    val_users = set(unique_users[n_train:n_train + n_val])
    test_users = set(unique_users[n_train + n_val:])
    
    train_indices = [i for i, u in enumerate(user_ids) if u in train_users]
    val_indices = [i for i, u in enumerate(user_ids) if u in val_users]
    test_indices = [i for i, u in enumerate(user_ids) if u in test_users]
    
    train_sequences = sequences_array[train_indices]
    val_sequences = sequences_array[val_indices]
    test_sequences = sequences_array[test_indices]
    
    print(f"Train: {len(train_users)} users, {len(train_sequences):,} sequences")
    print(f"Val:   {len(val_users)} users, {len(val_sequences):,} sequences")
    print(f"Test:  {len(test_users)} users, {len(test_sequences):,} sequences")
    
    # Step 6: Create datasets and loaders
    train_dataset = BehavioralSequenceDataset(train_sequences)
    val_dataset = BehavioralSequenceDataset(val_sequences)
    test_dataset = BehavioralSequenceDataset(test_sequences)
    
    train_loader = DataLoader(train_dataset, batch_size=CONFIG['batch_size'], shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=CONFIG['batch_size'], shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=CONFIG['batch_size'], shuffle=False)
    
    # Step 7: Build model
    print("\n" + "="*80)
    print("STEP 6: BUILDING MODEL")
    print("="*80)
    
    model = InsiderThreatAutoencoder(
        input_dim=CONFIG['input_dim'],
        hidden_dim=CONFIG['hidden_dim'],
        latent_dim=CONFIG['latent_dim'],
        num_layers=CONFIG['num_layers'],
        dropout=CONFIG['dropout']
    ).to(CONFIG['device'])
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"🧠 Model: LSTM Autoencoder")
    print(f"   Parameters: {total_params:,}")
    print(f"   Input dim: {CONFIG['input_dim']}")
    print(f"   Hidden dim: {CONFIG['hidden_dim']}")
    print(f"   Latent dim: {CONFIG['latent_dim']}")
    
    # Loss and optimizer
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=CONFIG['learning_rate'], weight_decay=CONFIG['weight_decay'])
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5, factor=0.5)
    
    # Step 8: Train
    print("\n" + "="*80)
    print("STEP 7: TRAINING")
    print("="*80 + "\n")
    
    history = {'train_loss': [], 'val_loss': []}
    best_val_loss = float('inf')
    
    for epoch in range(CONFIG['epochs']):
        train_loss = train_epoch(model, train_loader, criterion, optimizer, CONFIG['device'])
        val_loss = validate(model, val_loader, criterion, CONFIG['device'])
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        
        scheduler.step(val_loss)
        
        print(f"Epoch {epoch+1:3d}/{CONFIG['epochs']} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")
        
        # Save best model
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), os.path.join(CONFIG['output_dir'], 'best_autoencoder.pt'))
            print("  ✅ Saved best model")
    
    # Step 9: Compute baselines
    print("\n" + "="*80)
    print("STEP 8: COMPUTING USER BASELINES")
    print("="*80)
    
    model.load_state_dict(torch.load(os.path.join(CONFIG['output_dir'], 'best_autoencoder.pt']))
    
    baselines = compute_user_baselines(model, sequences_array, user_ids, CONFIG['device'])
    
    # Save baselines
    with open(os.path.join(CONFIG['output_dir'], 'user_baselines.json'), 'w') as f:
        json.dump(baselines, f, indent=2)
    
    # Step 10: Evaluate
    print("\n" + "="*80)
    print("STEP 9: EVALUATION")
    print("="*80)
    
    test_loss = validate(model, test_loader, criterion, CONFIG['device'])
    print(f"\n📊 Test Reconstruction Loss: {test_loss:.6f}")
    
    # Compute test reconstruction errors
    model.eval()
    test_errors = []
    with torch.no_grad():
        for sequences, _ in test_loader:
            sequences = sequences.to(CONFIG['device'])
            errors = model.get_reconstruction_error(sequences, reduction='none')
            test_errors.extend(errors.cpu().numpy())
    
    test_errors = np.array(test_errors)
    
    print(f"\n📈 Test Reconstruction Error Statistics:")
    print(f"   Mean: {np.mean(test_errors):.6f}")
    print(f"   Median: {np.median(test_errors):.6f}")
    print(f"   Std: {np.std(test_errors):.6f}")
    print(f"   95th percentile: {np.percentile(test_errors, 95):.6f}")
    print(f"   99th percentile: {np.percentile(test_errors, 99):.6f}")
    
    # Save config and results
    results = {
        'config': CONFIG,
        'training_history': history,
        'test_metrics': {
            'loss': float(test_loss),
            'mean_error': float(np.mean(test_errors)),
            'std_error': float(np.std(test_errors)),
            'p95_error': float(np.percentile(test_errors, 95)),
            'p99_error': float(np.percentile(test_errors, 99))
        },
        'num_users': len(unique_users),
        'num_sequences': len(sequences_array),
        'timestamp': datetime.now().isoformat()
    }
    
    with open(os.path.join(CONFIG['output_dir'], 'training_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Plot training curves
    plt.figure(figsize=(10, 5))
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Reconstruction Loss (MSE)')
    plt.title('LSTM Autoencoder Training')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(CONFIG['output_dir'], 'training_curve.png'), dpi=150, bbox_inches='tight')
    print(f"\n✅ Saved training curve")
    
    # Plot error distribution
    plt.figure(figsize=(10, 5))
    plt.hist(test_errors, bins=50, edgecolor='black', alpha=0.7)
    plt.axvline(np.percentile(test_errors, 95), color='r', linestyle='--', label='95th percentile')
    plt.xlabel('Reconstruction Error')
    plt.ylabel('Frequency')
    plt.title('Test Set Reconstruction Error Distribution')
    plt.legend()
    plt.grid(alpha=0.3)
    plt.savefig(os.path.join(CONFIG['output_dir'], 'error_distribution.png'), dpi=150, bbox_inches='tight')
    print(f"✅ Saved error distribution")
    
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETE!")
    print("="*80)
    print(f"\n📁 Output directory: {CONFIG['output_dir']}")
    print(f"   - best_autoencoder.pt (model weights)")
    print(f"   - user_baselines.json (per-user baselines)")
    print(f"   - training_results.json (metrics)")
    print(f"   - training_curve.png")
    print(f"   - error_distribution.png")


if __name__ == '__main__':
    main()
