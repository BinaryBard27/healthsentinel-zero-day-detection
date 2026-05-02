"""
Quick LSTM Model Test
"""
import torch
import json
import numpy as np

print("=" * 80)
print("LSTM MODEL VERIFICATION")
print("=" * 80)

# Test 1: Load model
print("\n[1/3] Loading model...")
try:
    model = torch.load(r'models\insider_threat_lstm\insider_threat_lstm.pt', map_location='cpu')
    print("✅ Model loaded successfully")
    print(f"   Type: {type(model)}")
    
    # Try to get parameters
    if hasattr(model, 'parameters'):
        total_params = sum(p.numel() for p in model.parameters())
        print(f"   Parameters: {total_params:,}")
    
    # Try inference
    print("\n[2/3] Testing inference...")
    if hasattr(model, 'eval'):
        model.eval()
        dummy_input = torch.randn(1, 30, 12)
        with torch.no_grad():
            output = model(dummy_input)
        print(f"✅ Inference successful")
        print(f"   Input: {list(dummy_input.shape)}")
        print(f"   Output: {list(output.shape)}")
    else:
        print("⚠️ Model doesn't have eval() method")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Load baselines
print("\n[3/3] Analyzing user baselines...")
try:
    with open(r'user_baselines.json', 'r') as f:
        baselines = json.load(f)
    
    print(f"✅ Loaded baselines for {len(baselines)} users")
    
    means = [b['mean'] for b in baselines.values()]
    thresholds = [b['thresh'] for b in baselines.values()]
    
    print(f"\n   Reconstruction Error Statistics:")
    print(f"   Mean: {np.mean(means):.6f}")
    print(f("   Threshold (avg): {np.mean(thresholds):.6f}")
    print(f"   Threshold (min): {np.min(thresholds):.6f}")
    print(f"   Threshold (max): {np.max(thresholds):.6f}")
    
except Exception as e:
    print(f"❌ Error loading baselines: {e}")

print("\n" + "=" * 80)
print("VERIFICATION COMPLETE")
print("=" * 80)
