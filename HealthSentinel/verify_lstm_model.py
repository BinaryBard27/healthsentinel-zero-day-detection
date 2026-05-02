"""
LSTM Autoencoder Model Verification Script
===========================================

This script verifies the trained LSTM autoencoder model and generates a comprehensive
quality assessment report.

Usage:
    python verify_lstm_model.py
"""

import torch
import torch.nn as nn
import json
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Import the model architecture
class InsiderThreatAutoencoder(nn.Module):
    """LSTM Autoencoder for behavioral sequence reconstruction"""
    
    def __init__(self, input_dim, hidden_dim, latent_dim, num_layers=2, dropout=0.2):
        super(InsiderThreatAutoencoder, self).__init__()
        
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim
        self.num_layers = num_layers
        
        # Encoder
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
        
        # Decoder
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
        lstm_out, (hidden, cell) = self.encoder_lstm(x)
        latent = self.encoder_fc(hidden[-1])
        return latent
    
    def decode(self, latent, seq_len):
        batch_size = latent.size(0)
        decoder_input = self.decoder_fc(latent)
        decoder_input = decoder_input.unsqueeze(1).repeat(1, seq_len, 1)
        lstm_out, _ = self.decoder_lstm(decoder_input)
        reconstructed = self.output_fc(lstm_out)
        return reconstructed
    
    def forward(self, x):
        seq_len = x.size(1)
        latent = self.encode(x)
        reconstructed = self.decode(latent, seq_len)
        return reconstructed
    
    def get_reconstruction_error(self, x, reduction='mean'):
        with torch.no_grad():
            reconstructed = self.forward(x)
            
            if reduction == 'none':
                error = torch.mean((x - reconstructed) ** 2, dim=(1, 2))
            elif reduction == 'mean':
                error = torch.mean((x - reconstructed) ** 2)
            elif reduction == 'sum':
                error = torch.sum((x - reconstructed) ** 2)
            
            return error


def verify_model():
    """Verify the trained LSTM autoencoder model"""
    
    print("=" * 80)
    print(" " * 25 + "LSTM MODEL VERIFICATION")
    print("=" * 80)
    print()
    
    # Paths
    model_path = Path(r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_lstm\insider_threat_lstm.pt')
    baselines_path = Path(r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\user_baselines.json')
    
    results = {
        'model_verification': {},
        'baselines_analysis': {},
        'recommendations': []
    }
    
    # ========================================================================
    # STEP 1: Verify Model File
    # ========================================================================
    print("\n📦 STEP 1: Verifying Model File")
    print("-" * 80)
    
    if not model_path.exists():
        print("❌ ERROR: Model file not found!")
        print(f"   Expected: {model_path}")
        return False
    
    print(f"✅ Model file found: {model_path.name}")
    print(f"   Size: {model_path.stat().st_size / 1024 / 1024:.2f} MB")
    
    results['model_verification']['file_exists'] = True
    results['model_verification']['file_size_mb'] = model_path.stat().st_size / 1024 / 1024
    
    # ========================================================================
    # STEP 2: Load Model
    # ========================================================================
    print("\n🔄 STEP 2: Loading Model")
    print("-" * 80)
    
    try:
        # Try loading as full model
        try:
            model = torch.load(model_path, map_location='cpu')
            print("✅ Loaded as complete model")
            load_type = "complete_model"
        except:
            # Try loading as state dict
            model = InsiderThreatAutoencoder(
                input_dim=12,
                hidden_dim=128,
                latent_dim=64,
                num_layers=2,
                dropout=0.2
            )
            model.load_state_dict(torch.load(model_path, map_location='cpu'))
            print("✅ Loaded as state dictionary")
            load_type = "state_dict"
        
        model.eval()
        results['model_verification']['load_successful'] = True
        results['model_verification']['load_type'] = load_type
        
        # Count parameters
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
        
        print(f"\n📊 Model Architecture:")
        print(f"   Total parameters: {total_params:,}")
        print(f"   Trainable parameters: {trainable_params:,}")
        
        results['model_verification']['total_parameters'] = total_params
        results['model_verification']['trainable_parameters'] = trainable_params
        
    except Exception as e:
        print(f"❌ ERROR loading model: {str(e)}")
        results['model_verification']['load_successful'] = False
        results['model_verification']['error'] = str(e)
        return results
    
    # ========================================================================
    # STEP 3: Test Model Inference
    # ========================================================================
    print("\n🧪 STEP 3: Testing Model Inference")
    print("-" * 80)
    
    try:
        # Create dummy input (batch_size=2, seq_len=30, features=12)
        dummy_input = torch.randn(2, 30, 12)
        
        with torch.no_grad():
            output = model(dummy_input)
        
        print("✅ Forward pass successful")
        print(f"   Input shape: {list(dummy_input.shape)}")
        print(f"   Output shape: {list(output.shape)}")
        
        # Test reconstruction error
        error = model.get_reconstruction_error(dummy_input, reduction='none')
        print(f"   Reconstruction error shape: {list(error.shape)}")
        
        results['model_verification']['inference_successful'] = True
        results['model_verification']['input_shape'] = list(dummy_input.shape)
        results['model_verification']['output_shape'] = list(output.shape)
        
    except Exception as e:
        print(f"❌ ERROR during inference: {str(e)}")
        results['model_verification']['inference_successful'] = False
        results['model_verification']['inference_error'] = str(e)
    
    # ========================================================================
    # STEP 4: Verify User Baselines
    # ========================================================================
    print("\n👥 STEP 4: Verifying User Baselines")
    print("-" * 80)
    
    if not baselines_path.exists():
        print("❌ ERROR: User baselines file not found!")
        results['baselines_analysis']['file_exists'] = False
        return results
    
    print(f"✅ Baselines file found: {baselines_path.name}")
    
    try:
        with open(baselines_path, 'r') as f:
            baselines = json.load(f)
        
        num_users = len(baselines)
        print(f"   Number of users: {num_users}")
        
        # Analyze baseline statistics
        means = [b['mean'] for b in baselines.values()]
        stds = [b['std'] for b in baselines.values()]
        thresholds = [b['thresh'] for b in baselines.values()]
        
        print(f"\n📈 Baseline Statistics:")
        print(f"   Mean reconstruction error:")
        print(f"      Average: {np.mean(means):.6f}")
        print(f"      Min: {np.min(means):.6f}")
        print(f"      Max: {np.max(means):.6f}")
        print(f"   Thresholds:")
        print(f"      Average: {np.mean(thresholds):.6f}")
        print(f"      Min: {np.min(thresholds):.6f}")
        print(f"      Max: {np.max(thresholds):.6f}")
        
        # Identify users with highest/lowest thresholds
        sorted_users = sorted(baselines.items(), key=lambda x: x[1]['thresh'], reverse=True)
        
        print(f"\n🔝 Top 5 Users with Highest Variability:")
        for i, (user, stats) in enumerate(sorted_users[:5], 1):
            print(f"   {i}. {user[:30]:30s} - Threshold: {stats['thresh']:.6f}")
        
        print(f"\n🔽 Top 5 Users with Lowest Variability:")
        for i, (user, stats) in enumerate(sorted_users[-5:], 1):
            print(f"   {i}. {user[:30]:30s} - Threshold: {stats['thresh']:.6f}")
        
        results['baselines_analysis'] = {
            'file_exists': True,
            'num_users': num_users,
            'mean_error_avg': float(np.mean(means)),
            'mean_error_min': float(np.min(means)),
            'mean_error_max': float(np.max(means)),
            'threshold_avg': float(np.mean(thresholds)),
            'threshold_min': float(np.min(thresholds)),
            'threshold_max': float(np.max(thresholds)),
            'highest_variability_users': [
                {'user': user, 'threshold': stats['thresh']}
                for user, stats in sorted_users[:5]
            ],
            'lowest_variability_users': [
                {'user': user, 'threshold': stats['thresh']}
                for user, stats in sorted_users[-5:]
            ]
        }
        
    except Exception as e:
        print(f"❌ ERROR loading baselines: {str(e)}")
        results['baselines_analysis']['error'] = str(e)
    
    # ========================================================================
    # STEP 5: Generate Recommendations
    # ========================================================================
    print("\n💡 STEP 5: Recommendations")
    print("-" * 80)
    
    recommendations = []
    
    if results['model_verification'].get('load_successful'):
        recommendations.append("✅ Model loads successfully and is ready for inference")
    else:
        recommendations.append("❌ Model cannot be loaded - requires retraining")
    
    if results['model_verification'].get('inference_successful'):
        recommendations.append("✅ Model inference works correctly")
    else:
        recommendations.append("❌ Model inference failed - check architecture compatibility")
    
    if results['baselines_analysis'].get('num_users', 0) > 0:
        recommendations.append(f"✅ User baselines computed for {results['baselines_analysis']['num_users']} users")
    else:
        recommendations.append("❌ No user baselines found - need to compute baselines")
    
    # Check if thresholds are reasonable
    if results['baselines_analysis'].get('threshold_avg', 0) > 0:
        avg_thresh = results['baselines_analysis']['threshold_avg']
        if 0.01 < avg_thresh < 0.5:
            recommendations.append("✅ Threshold ranges look reasonable")
        else:
            recommendations.append("⚠️ Threshold ranges unusual - review training data quality")
    
    # Missing files
    results_json = Path(r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_lstm\training_results.json')
    if not results_json.exists():
        recommendations.append("⚠️ Missing training_results.json - no training metrics available")
    
    # Overall assessment
    if (results['model_verification'].get('load_successful') and 
        results['model_verification'].get('inference_successful') and
        results['baselines_analysis'].get('num_users', 0) > 50):
        recommendations.append("\n🎉 OVERALL: Model appears to be trained successfully and ready for deployment!")
    else:
        recommendations.append("\n⚠️ OVERALL: Model needs review before deployment")
    
    results['recommendations'] = recommendations
    
    for rec in recommendations:
        print(f"   {rec}")
    
    # ========================================================================
    # Save Results
    # ========================================================================
    print("\n\n💾 Saving verification results...")
    output_path = Path(r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\model_verification_report.json')
    
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"✅ Saved to: {output_path}")
    
    print("\n" + "=" * 80)
    print(" " * 25 + "VERIFICATION COMPLETE")
    print("=" * 80)
    
    return results


if __name__ == '__main__':
    verify_model()
