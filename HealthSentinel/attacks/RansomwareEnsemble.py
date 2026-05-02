import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from xgboost import XGBClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, recall_score, confusion_matrix
import functools

def fail_safe_decorator(func):
    """Fail-Safe Decorator: if confidence < 0.40, output QUARANTINE with 1.0 confidence"""
    @functools.wraps(func)
    def wrapper(self, X, *args, **kwargs):
        preds, probs = func(self, X, *args, **kwargs)
        final_preds = []
        final_probs = []
        for i in range(len(preds)):
            if probs[i] < 0.40:
                final_preds.append('QUARANTINE')
                final_probs.append(1.0)
            else:
                final_preds.append('RANSOMWARE' if preds[i] == 1 else 'BENIGN')
                final_probs.append(probs[i])
        return np.array(final_preds), np.array(final_probs)
    return wrapper

class RansomwareEnsemble:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None

    def fit(self, X, y):
        # 2) Implement Cost-Sensitive Learning (class_weight='balanced')
        # Calculate ratio for XGBoost
        ratio = float(np.sum(y == 0)) / np.sum(y == 1) if np.sum(y == 1) > 0 else 1.0
        
        estimators = [
            ('rf', RandomForestClassifier(class_weight='balanced', random_state=42, n_jobs=-1)),
            ('xgb', XGBClassifier(scale_pos_weight=ratio, random_state=42, n_jobs=-1, use_label_encoder=False, eval_metric='logloss'))
        ]
        
        # 1) Replace 'Majority Vote' with StackingClassifier using Logistic Regression meta-learner
        self.model = StackingClassifier(
            estimators=estimators,
            final_estimator=LogisticRegression(class_weight='balanced'),
            cv=5,
            n_jobs=-1
        )
        
        X_scaled = self.scaler.fit_transform(X)
        print("Training Cost-Sensitive Stacking Classifier...")
        self.model.fit(X_scaled, y)
        print("Training complete.")
        return self

    @fail_safe_decorator
    def predict_with_failsafe(self, X):
        X_scaled = self.scaler.transform(X)
        preds = self.model.predict(X_scaled)
        # Getting confidence (max probability)
        probs = np.max(self.model.predict_proba(X_scaled), axis=1)
        return preds, probs
        
    def predict(self, X):
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)

if __name__ == "__main__":
    import warnings
    warnings.filterwarnings('ignore')
    
    print("Loading simulation datasets...")
    X = pd.read_csv('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/Datasets/preprocessed data/Ransomware/Simulation/model/simulation_features.csv')
    y_df = pd.read_csv('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/Datasets/preprocessed data/Ransomware/Simulation/model/simulation_labels.csv')
    y = y_df.values.ravel()
    
    print(f"Dataset Shape: X={X.shape}, y={y.shape}")
    
    # Train/Test Split (80/20) for fair evaluation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    ensemble = RansomwareEnsemble()
    ensemble.fit(X_train, y_train)
    
    # Predict without failsafe to get pure ML metrics
    y_pred = ensemble.predict(X_test)
    
    print("\n" + "="*50)
    print("          ANTIGRAVITY ANALYTICS REPORT          ")
    print("="*50)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    recall = recall_score(y_test, y_pred)
    print(f"Recall (Malware): {recall * 100:.2f}%")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Benign", "Ransomware"]))
    
    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    print("                 Predicted Benign   Predicted Malware")
    print(f"Actual Benign    {cm[0,0]:<17} {cm[0,1]}")
    print(f"Actual Malware   {cm[1,0]:<17} {cm[1,1]}")
    print("==================================================\n")
    
    # Test Fail-Safe Decorator
    print("Testing Fail-Safe Decorator...")
    sample_safe = np.array([[0.1, 0.2, 0.05, 0.3, 0.1, 0.0, 0.0, 0.05, 0.9, 0.1] * 6 + [0.1]]) # 61 features approx
    # Wait, simple test with a subset of test data
    test_subset = X_test.head(5).copy()
    preds, confs = ensemble.predict_with_failsafe(test_subset)
    print("Fail-Safe Predictions:")
    for i in range(5):
        print(f"Sample {i}: Pred={preds[i]:<12} Conf={confs[i]:.4f}")

