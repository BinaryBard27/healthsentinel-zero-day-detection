import sys
import numpy as np
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')
from ai_server import model_manager

model_manager.load_all_models()

scenarios = {
    "Safe": [0.1, 0.2, 0.05, 0.3, 0.1, 0.0, 0.0, 0.05, 0.9, 0.1],
    "WannaCry": [0.95, 0.88, 0.92, 0.85, 0.72, 1.0, 0.95, 0.78, 0.08, 0.91],
    "LockBit": [0.92, 0.95, 0.88, 0.90, 0.65, 0.97, 0.88, 0.82, 0.05, 0.88],
    "Suspicious": [0.55, 0.6, 0.40, 0.70, 0.45, 0.35, 0.55, 0.42, 0.5, 0.58]
}

n_expected = model_manager.ransomware_models['scaler'].n_features_in_

for name, payload in scenarios.items():
    feats = np.array(payload, dtype=np.float64)
    # Cyclic padding
    padded = np.zeros(n_expected)
    for i in range(n_expected):
        padded[i] = feats[i % len(feats)]
        
    scaled = model_manager.ransomware_models['scaler'].transform(padded.reshape(1, -1))
    preds = []
    for model_name in ['rf', 'xgb', 'lgb', 'svm', 'voting_ensemble']:
        preds.append(int(model_manager.ransomware_models[model_name].predict(scaled)[0]))
        
    print(f"{name} -> Sum={sum(preds)}/5 -> {preds}")

