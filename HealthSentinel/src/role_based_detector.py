"""
Role-Based Insider Threat Detection
===================================

Context-aware detection using role-specific behavioral models.

Doctor at 2 AM accessing patient records = NORMAL (emergency)
HR staff at 2 AM accessing patient records = SUSPICIOUS

Author: HealthSentinel Team
"""

import torch
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict

from insider_threat_detector import InsiderThreatAutoencoder


class RoleBasedDetector:
    """
    Maintains separate LSTM autoencoders and baselines per user role.
    
    Roles:
    - Doctor
    - Nurse
    - Admin
    - IT Staff
    - Researcher
    - HR
    """
    
    def __init__(self, model_config: Dict, device: str = None):
        """
        Initialize role-based detector.
        
        Args:
            model_config: Model architecture config
            device: 'cuda' or 'cpu'
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.config = model_config
        
        # Role models
        self.roles = ['doctor', 'nurse', 'admin', 'it_staff', 'researcher', 'hr', 'default']
        self.role_models = {}
        self.role_baselines = {role: {} for role in self.roles}
        
        # User to role mapping
        self.user_roles = {}
        
        print(f"🔧 Initialized role-based detector")
        print(f"   Roles: {', '.join(self.roles)}")
    
    def load_role_model(self, role: str, model_path: str, baselines_path: str):
        """Load trained model for a specific role"""
        if role not in self.roles:
            raise ValueError(f"Unknown role: {role}")
        
        # Load model
        model = InsiderThreatAutoencoder(
            input_dim=self.config['input_dim'],
            hidden_dim=self.config['hidden_dim'],
            latent_dim=self.config['latent_dim'],
            num_layers=self.config.get('num_layers', 2),
            dropout=self.config.get('dropout', 0.2)
        ).to(self.device)
        
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        
        self.role_models[role] = model
        
        # Load baselines
        with open(baselines_path, 'r') as f:
            self.role_baselines[role] = json.load(f)
        
        print(f"✅ Loaded {role} model ({len(self.role_baselines[role])} user baselines)")
    
    def set_user_role(self, user_id: str, role: str):
        """Assign role to user"""
        if role not in self.roles:
            raise ValueError(f"Unknown role: {role}")
        self.user_roles[user_id] = role
    
    def load_user_roles(self, mapping_path: str):
        """
        Load user-to-role mapping from JSON file.
        
        Format: {"user_id": "role", ...}
        """
        with open(mapping_path, 'r') as f:
            self.user_roles = json.load(f)
        print(f"✅ Loaded {len(self.user_roles)} user role mappings")
    
    def get_user_role(self, user_id: str) -> str:
        """Get role for user (default if unknown)"""
        return self.user_roles.get(user_id, 'default')
    
    def detect(self, user_id: str, sequence: np.ndarray,
               threshold_multiplier: float = 2.0) -> Dict:
        """
        Detect anomaly using role-specific model.
        
        Args:
            user_id: User identifier
            sequence: Behavioral sequence [seq_len, n_features]
            threshold_multiplier: Threshold multiplier
        
        Returns:
            Detection result with role context
        """
        # Get user's role
        role = self.get_user_role(user_id)
        
        # Use role-specific model or default
        if role in self.role_models:
            model = self.role_models[role]
            baselines = self.role_baselines[role]
        elif 'default' in self.role_models:
            model = self.role_models['default']
            baselines = self.role_baselines['default']
        else:
            raise ValueError("No models loaded. Load at least a default model.")
        
        # Compute reconstruction error
        sequence_tensor = torch.FloatTensor(sequence).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            reconstructed = model(sequence_tensor)
            error = torch.mean((sequence_tensor - reconstructed) ** 2).item()
        
        # Get baseline
        baseline = baselines.get(user_id)
        
        if baseline:
            threshold = baseline['mean_error'] + threshold_multiplier * baseline['std_error']
            confidence = 'HIGH'
        else:
            # Use role average baseline
            role_mean = np.mean([b['mean_error'] for b in baselines.values()])
            role_std = np.mean([b['std_error'] for b in baselines.values()])
            threshold = role_mean + threshold_multiplier * role_std
            confidence = 'MEDIUM'
        
        is_anomaly = error > threshold
        
        # Risk score
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
            'role': role,
            'has_user_baseline': baseline is not None,
            'deviation_factor': error / baseline['mean_error'] if baseline else None
        }
    
    def train_role_model(self, role: str, sequences: np.ndarray, user_ids: List[str],
                        epochs: int = 30, batch_size: int = 64) -> Dict:
        """
        Train autoencoder for a specific role.
        
        Args:
            role: Role name
            sequences: Training sequences [n_sequences, seq_len, n_features]
            user_ids: User IDs for each sequence
            epochs: Training epochs
            batch_size: Batch size
        
        Returns:
            Training history
        """
        from torch.utils.data import Dataset, DataLoader
        import torch.optim as optim
        import torch.nn as nn
        
        print(f"\n🔧 Training {role} model...")
        print(f"   Sequences: {len(sequences):,}")
        print(f"   Users: {len(set(user_ids))}")
        
        # Create model
        model = InsiderThreatAutoencoder(
            input_dim=self.config['input_dim'],
            hidden_dim=self.config['hidden_dim'],
            latent_dim=self.config['latent_dim'],
            num_layers=self.config.get('num_layers', 2),
            dropout=self.config.get('dropout', 0.2)
        ).to(self.device)
        
        # Dataset
        class SeqDataset(Dataset):
            def __init__(self, seqs):
                self.seqs = torch.FloatTensor(seqs)
            def __len__(self):
                return len(self.seqs)
            def __getitem__(self, idx):
                return self.seqs[idx], self.seqs[idx]
        
        dataloader = DataLoader(SeqDataset(sequences), batch_size=batch_size, shuffle=True)
        
        # Train
        criterion = nn.MSELoss()
        optimizer = optim.Adam(model.parameters(), lr=0.001)
        
        history = []
        for epoch in range(epochs):
            model.train()
            epoch_loss = 0
            
            for seqs, targets in dataloader:
                seqs, targets = seqs.to(self.device), targets.to(self.device)
                
                optimizer.zero_grad()
                reconstructed = model(seqs)
                loss = criterion(reconstructed, targets)
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
            
            epoch_loss /= len(dataloader)
            history.append(epoch_loss)
            
            if (epoch + 1) % 5 == 0:
                print(f"   Epoch {epoch+1}/{epochs} | Loss: {epoch_loss:.6f}")
        
        # Save model
        self.role_models[role] = model
        
        # Compute baselines
        print(f"   Computing baselines...")
        baselines = {}
        unique_users = sorted(set(user_ids))
        
        model.eval()
        with torch.no_grad():
            for user in unique_users:
                user_indices = [i for i, u in enumerate(user_ids) if u == user]
                user_seqs = torch.FloatTensor(sequences[user_indices]).to(self.device)
                
                reconstructed = model(user_seqs)
                errors = torch.mean((user_seqs - reconstructed) ** 2, dim=(1, 2)).cpu().numpy()
                
                baselines[user] = {
                    'mean_error': float(np.mean(errors)),
                    'std_error': float(np.std(errors)),
                    'p95_error': float(np.percentile(errors, 95)),
                    'p99_error': float(np.percentile(errors, 99)),
                }
        
        self.role_baselines[role] = baselines
        
        print(f"✅ {role} model trained")
        
        return {'history': history, 'final_loss': history[-1]}
    
    def save_role_model(self, role: str, model_path: str, baselines_path: str):
        """Save role-specific model and baselines"""
        if role not in self.role_models:
            raise ValueError(f"No model loaded for role: {role}")
        
        torch.save(self.role_models[role].state_dict(), model_path)
        
        with open(baselines_path, 'w') as f:
            json.dump(self.role_baselines[role], f, indent=2)
        
        print(f"💾 Saved {role} model to {model_path}")
        print(f"💾 Saved {role} baselines to {baselines_path}")


# ============================================================================
# ROLE ASSIGNMENT UTILITIES
# ============================================================================

def assign_roles_by_heuristics(df) -> Dict[str, str]:
    """
    Auto-assign roles based on behavioral heuristics.
    
    Args:
        df: DataFrame with user activity data
    
    Returns:
        Dictionary mapping user_id -> role
    """
    user_roles = {}
    
    for user in df['user'].unique():
        user_data = df[df['user'] == user]
        
        # Heuristics
        has_phi_access = user_data['resource'].str.contains('patient|ehr|medical', case=False, na=False).any()
        has_admin_access = user_data['action'].str.contains('admin|sudo', case=False, na=False).any()
        has_it_access = user_data['action'].str.contains('ssh|network|server', case=False, na=False).any()
        
        # Assign role
        if has_phi_access and not has_admin_access:
            role = 'doctor'  # or nurse
        elif has_admin_access and has_it_access:
            role = 'it_staff'
        elif has_admin_access:
            role = 'admin'
        else:
            role = 'default'
        
        user_roles[user] = role
    
    print(f"📋 Auto-assigned roles for {len(user_roles)} users")
    role_counts = {}
    for role in user_roles.values():
        role_counts[role] = role_counts.get(role, 0) + 1
    
    for role, count in role_counts.items():
        print(f"   {role}: {count} users")
    
    return user_roles


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print("ROLE-BASED INSIDER THREAT DETECTOR - DEMO")
    print("="*80)
    
    # Example config
    config = {
        'input_dim': 12,
        'hidden_dim': 128,
        'latent_dim': 64,
        'num_layers': 2,
        'dropout': 0.2
    }
    
    detector = RoleBasedDetector(config)
    
    # Load default model
    MODEL_DIR = r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_autoencoder'
    
    detector.load_role_model(
        'default',
        f'{MODEL_DIR}/best_autoencoder.pt',
        f'{MODEL_DIR}/user_baselines.json'
    )
    
    print("\n✅ Role-based detector ready!")
    print("   To train role-specific models, use train_role_model()")
    print("   To assign users to roles, use set_user_role() or load_user_roles()")
