import pickle
import torch
import numpy as np
from pathlib import Path
import sys
import os

def test_loading():
    project_root = Path(os.getcwd()).parent
    
    # 1. Test Ransomware
    print("Testing Ransomware models...")
    base_path = project_root / "Datasets" / "preprocessed data" / "Ransomware" / "Simulation" / "model" / "RansomwareModels_Complete"
    if base_path.exists():
        try:
            rf = pickle.load(open(base_path / 'rf_model.pkl', 'rb'))
            print("✅ RF Loaded")
        except Exception as e:
            print(f"❌ RF Failed: {e}")
    else:
        print(f"❌ base_path {base_path} not found")

    # 2. Test Phishing
    print("\nTesting Phishing...")
    simulation_dir = project_root / "Datasets" / "preprocessed data" / "phising attack" / "simulation"
    phishing_path = simulation_dir / "two_tier_phishing_system.pkl"
    if phishing_path.exists():
        print(f"✅ Phishing path exists: {phishing_path}")
    else:
        print(f"❌ Phishing path not found")

    # 3. Test LSTM
    print("\nTesting LSTM...")
    model_path = project_root / "models" / "insider_threat_lstm" / "insider_threat_lstm.pt"
    if model_path.exists():
        try:
            loaded = torch.load(model_path, map_location='cpu', weights_only=False)
            print(f"✅ LSTM Loaded (type: {type(loaded)})")
        except Exception as e:
            print(f"❌ LSTM Failed: {e}")
    else:
        print(f"❌ LSTM path {model_path} not found")

if __name__ == "__main__":
    test_loading()
