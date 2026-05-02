import sys
import numpy as np
import traceback
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')
from ai_server import model_manager

model_manager.load_all_models()

payload_features = [0.55, 0.6, 0.40, 0.70, 0.45, 0.35, 0.55, 0.42, 0.5, 0.58]
try:
    features = np.array(payload_features, dtype=np.float64)
    n_expected = model_manager.ransomware_models['scaler'].n_features_in_
    
    if len(features) < n_expected:
        padded = np.zeros(n_expected)
        padded[:len(features)] = features
        features = padded
        
    features = features.reshape(1, -1)
    print("Features shape:", features.shape)
    
    features_scaled = model_manager.ransomware_models['scaler'].transform(features)
    
    predictions = []
    
    for name in ['rf', 'xgb', 'lgb', 'svm']:
        print(f"Predicting {name}...")
        pred = model_manager.ransomware_models[name].predict(features_scaled)[0]
        prob = model_manager.ransomware_models[name].predict_proba(features_scaled)[0]
        predictions.append(pred)
        
    for name in ['voting_ensemble', 'stacking_ensemble']:
        print(f"Predicting {name}...")
        pred = model_manager.ransomware_models[name].predict(features_scaled)[0]
        predictions.append(pred)
        
    print("Predictions:", predictions)
    
except Exception as e:
    traceback.print_exc()
