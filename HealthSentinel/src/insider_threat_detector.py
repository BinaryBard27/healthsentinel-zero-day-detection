"""
Insider Threat Detector - Real-time Inference Module
====================================================

Uses trained LSTM autoencoder to detect insider threats in real-time
through behavioral sequence reconstruction error analysis.

Author: HealthSentinel Team
"""

import torch
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import deque
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from behavioral_feature_aggregator import BehavioralFeatureAggregator


class InsiderThreatAutoencoder(torch.nn.Module):
    """LSTM Autoencoder - same architecture as training"""
    
    def __init__(self, input_dim, hidden_dim, latent_dim, num_layers=2, dropout=0.2):
        super(InsiderThreatAutoencoder, self).__init__()
        
        self.encoder_lstm = torch.nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.encoder_fc = torch.nn.Sequential(
            torch.nn.Linear(hidden_dim, latent_dim),
            torch.nn.Tanh()
        )
        
        self.decoder_fc = torch.nn.Linear(latent_dim, hidden_dim)
        
        self.decoder_lstm = torch.nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.output_fc = torch.nn.Linear(hidden_dim, input_dim)
    
    def encode(self, x):
        lstm_out, (hidden, cell) = self.encoder_lstm(x)
        latent = self.encoder_fc(hidden[-1])
        return latent
    
    def decode(self, latent, seq_len):
        batch_size = latent.size(0)
        decoder_input = self.decoder_fc(latent).unsqueeze(1).repeat(1, seq_len, 1)
        lstm_out, _ = self.decoder_lstm(decoder_input)
        reconstructed = self.output_fc(lstm_out)
        return reconstructed
    
    def forward(self, x):
        seq_len = x.size(1)
        latent = self.encode(x)
        reconstructed = self.decode(latent, seq_len)
        return reconstructed


class InsiderThreatDetector:
    """
    Real-time insider threat detector using LSTM autoencoder.
    
    Detects behavioral deviations through sequence reconstruction error.
    """
    
    def __init__(self, model_path: str, baselines_path: str, 
                 config_path: str, device: str = None):
        """
        Initialize detector.
        
        Args:
            model_path: Path to trained autoencoder weights
            baselines_path: Path to user baselines JSON
            config_path: Path to training config JSON
            device: 'cuda' or 'cpu' (auto-detect if None)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load config
        with open(config_path, 'r') as f:
            results = json.load(f)
            self.config = results['config']
        
        # Load user baselines
        with open(baselines_path, 'r') as f:
            self.baselines = json.load(f)
        
        # Load model
        self.model = InsiderThreatAutoencoder(
            input_dim=self.config['input_dim'],
            hidden_dim=self.config['hidden_dim'],
            latent_dim=self.config['latent_dim'],
            num_layers=self.config['num_layers'],
            dropout=self.config['dropout']
        ).to(self.device)
        
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.eval()
        
        # Feature aggregator
        self.aggregator = BehavioralFeatureAggregator(
            window_minutes=self.config['window_minutes']
        )
        
        # Sequence buffer per user
        self.user_buffers = {}
        self.sequence_length = self.config['sequence_length']
        
        print(f"✅ Insider Threat Detector Initialized")
        print(f"   Device: {self.device}")
        print(f"   Users with baselines: {len(self.baselines)}")
        print(f"   Sequence length: {self.sequence_length}")
    
    def detect(self, user_id: str, time_step_vector: np.ndarray, 
               threshold_multiplier: float = 2.0) -> Dict:
        """
        Detect if a new time-step is anomalous for the user.
        
        Args:
            user_id: User identifier
            time_step_vector: Feature vector for this time-step [12 features]
            threshold_multiplier: How many std deviations above mean = anomaly
        
        Returns:
            Detection result dictionary
        """
        # Initialize buffer for new user
        if user_id not in self.user_buffers:
            self.user_buffers[user_id] = deque(maxlen=self.sequence_length)
        
        # Add time-step to buffer
        self.user_buffers[user_id].append(time_step_vector)
        
        # Need full sequence for detection
        if len(self.user_buffers[user_id]) < self.sequence_length:
            return {
                'is_anomaly': False,
                'confidence': 'INSUFFICIENT_DATA',
                'reconstruction_error': None,
                'threshold': None,
                'buffer_fill': len(self.user_buffers[user_id]) / self.sequence_length
            }
        
        # Create sequence tensor
        sequence = np.array(list(self.user_buffers[user_id]))
        sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)
        
        # Compute reconstruction error
        with torch.no_grad():
            reconstructed = self.model(sequence_tensor)
            error = torch.mean((sequence_tensor - reconstructed) ** 2).item()
        
        # Get user baseline
        baseline = self.baselines.get(user_id)
        
        if baseline is None:
            # No baseline for this user - use global baseline
            global_mean = np.mean([b['mean_error'] for b in self.baselines.values()])
            global_std = np.mean([b['std_error'] for b in self.baselines.values()])
            threshold = global_mean + threshold_multiplier * global_std
            confidence = 'MEDIUM'  # Less confident without user-specific baseline
        else:
            threshold = baseline['mean_error'] + threshold_multiplier * baseline['std_error']
            confidence = 'HIGH'
        
        is_anomaly = error > threshold
        
        # Risk score (0-1)
        if baseline:
            risk_score = min(1.0, error / baseline['p99_error'])
        else:
            risk_score = 0.5 if not is_anomaly else 0.8
        
        return {
            'is_anomaly': bool(is_anomaly),
            'confidence': confidence,
            'risk_score': float(risk_score),
            'reconstruction_error': float(error),
            'threshold': float(threshold),
            'baseline_mean': baseline['mean_error'] if baseline else None,
            'baseline_p95': baseline['p95_error'] if baseline else None,
            'deviation_factor': error / baseline['mean_error'] if baseline else None
        }
    
    def detect_batch(self, user_id: str, sequences: np.ndarray, 
                    threshold_multiplier: float = 2.0) -> List[Dict]:
        """
        Detect anomalies in a batch of sequences.
        
        Args:
            user_id: User identifier
            sequences: Array of shape [num_sequences, seq_len, num_features]
            threshold_multiplier: Threshold multiplier
        
        Returns:
            List of detection results
        """
        sequences_tensor = torch.FloatTensor(sequences).to(self.device)
        
        with torch.no_grad():
            reconstructed = self.model(sequences_tensor)
            errors = torch.mean((sequences_tensor - reconstructed) ** 2, dim=(1, 2))
            errors = errors.cpu().numpy()
        
        baseline = self.baselines.get(user_id)
        
        if baseline:
            threshold = baseline['mean_error'] + threshold_multiplier * baseline['std_error']
        else:
            global_mean = np.mean([b['mean_error'] for b in self.baselines.values()])
            global_std = np.mean([b['std_error'] for b in self.baselines.values()])
            threshold = global_mean + threshold_multiplier * global_std
        
        results = []
        for error in errors:
            is_anomaly = error > threshold
            risk_score = min(1.0, error / baseline['p99_error']) if baseline else 0.5
            
            results.append({
                'is_anomaly': bool(is_anomaly),
                'risk_score': float(risk_score),
                'reconstruction_error': float(error),
                'threshold': float(threshold)
            })
        
        return results
    
    def get_user_baseline(self, user_id: str) -> Optional[Dict]:
        """Get baseline for a user"""
        return self.baselines.get(user_id)
    
    def update_baseline(self, user_id: str, new_sequences: np.ndarray):
        """
        Update user baseline with new normal behavior data.
        
        Args:
            user_id: User identifier
            new_sequences: New normal sequences to include in baseline
        """
        sequences_tensor = torch.FloatTensor(new_sequences).to(self.device)
        
        with torch.no_grad():
            reconstructed = self.model(sequences_tensor)
            errors = torch.mean((sequences_tensor - reconstructed) ** 2, dim=(1, 2))
            errors = errors.cpu().numpy()
        
        self.baselines[user_id] = {
            'mean_error': float(np.mean(errors)),
            'std_error': float(np.std(errors)),
            'median_error': float(np.median(errors)),
            'p95_error': float(np.percentile(errors, 95)),
            'p99_error': float(np.percentile(errors, 99)),
            'num_sequences': len(errors)
        }
        
        print(f"✅ Updated baseline for user: {user_id}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    import pandas as pd
    from behavioral_feature_aggregator import load_and_prepare_data
    
    # Paths
    MODEL_DIR = r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_autoencoder'
    
    print("="*80)
    print("INSIDER THREAT DETECTOR - INFERENCE DEMO")
    print("="*80)
    
    # Initialize detector
    detector = InsiderThreatDetector(
        model_path=f'{MODEL_DIR}/best_autoencoder.pt',
        baselines_path=f'{MODEL_DIR}/user_baselines.json',
        config_path=f'{MODEL_DIR}/training_results.json'
    )
    
    # Load some test data
    print("\n📂 Loading test data...")
    df = load_and_prepare_data(
        r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs_complete.csv',
        sample_size=10000
    )
    
    # Aggregate to time-steps
    print("\n🔧 Aggregating to time-steps...")
    timestep_df = detector.aggregator.aggregate_events_to_timesteps(df)
    
    # Test detection on first user
    test_user = timestep_df['user'].iloc[0]
    user_data = timestep_df[timestep_df['user'] == test_user]
    
    print(f"\n🔍 Testing detection on user: {test_user}")
    print(f"   Time-steps: {len(user_data)}")
    
    # Simulate real-time detection
    anomalies_found = 0
    for idx, row in user_data.iterrows():
        time_step = row[detector.aggregator.feature_names].values
        
        result = detector.detect(test_user, time_step, threshold_multiplier=2.0)
        
        if result['is_anomaly']:
            anomalies_found += 1
            print(f"\n🚨 ANOMALY DETECTED!")
            print(f"   Time: {row['timestamp']}")
            print(f"   Reconstruction Error: {result['reconstruction_error']:.6f}")
            print(f"   Threshold: {result['threshold']:.6f}")
            print(f"   Risk Score: {result['risk_score']:.2f}")
            print(f"   Deviation Factor: {result['deviation_factor']:.2f}x")
    
    print(f"\n📊 Detection Summary:")
    print(f"   Total time-steps analyzed: {len(user_data)}")
    print(f"   Anomalies detected: {anomalies_found}")
    print(f"   Anomaly rate: {anomalies_found/len(user_data)*100:.2f}%")
