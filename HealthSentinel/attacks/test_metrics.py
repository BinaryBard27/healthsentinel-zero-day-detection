import sys
import pandas as pd
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')
from ai_server import model_manager

# Load models
print("Loading models...")
model_manager.load_all_models()

# Load test data
print("Loading simulation datasets...")
X = pd.read_csv('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/Datasets/preprocessed data/Ransomware/Simulation/model/simulation_features.csv')
y = pd.read_csv('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/Datasets/preprocessed data/Ransomware/Simulation/model/simulation_labels.csv')

# The labels might be a DataFrame, convert to 1D array
y = y.values.ravel()

print(f"Dataset shape: X={X.shape}, y={y.shape}")

# Scale features
scaler = model_manager.ransomware_models['scaler']
X_scaled = scaler.transform(X)

# Evaluate Voting Ensemble
print("Generating predictions using Voting Ensemble...")
voting_model = model_manager.ransomware_models['voting_ensemble']
y_pred = voting_model.predict(X_scaled)

print("\n" + "="*50)
print("             RANSOMWARE ENSEMBLE METRICS            ")
print("="*50)
print(f"Accuracy: {accuracy_score(y, y_pred):.4f}")
print("\nClassification Report:")
print(classification_report(y, y_pred, target_names=["Benign", "Ransomware"]))
print("\nConfusion Matrix:")
cm = confusion_matrix(y, y_pred)
print("                 Predicted Benign   Predicted Malware")
print(f"Actual Benign    {cm[0,0]:<17} {cm[0,1]}")
print(f"Actual Malware   {cm[1,0]:<17} {cm[1,1]}")
print("==================================================\n")
