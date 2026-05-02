"""
Zero-Day Detector Service
=========================
Simulates a network monitor that captures traffic features and uses the 
1D-CNN model to detect novel attacks (DoS, BruteForce, etc.)
"""

import torch
import torch.nn as nn
import numpy as np
import pickle
import time
import os
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_PATH = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\zeroday\zeroday_cnn.pt"
SCALER_PATH = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\zeroday\network_scaler.pkl"
AGGREGATOR_URL = "http://localhost:8080/logs"

# ═══════════════════════════════════════════════════════════════════════════════
# MODEL DEFINITION
# ═══════════════════════════════════════════════════════════════════════════════

class ZeroDayCNN(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.conv1 = nn.Sequential(nn.Conv1d(1, 32, kernel_size=3, padding=1), nn.BatchNorm1d(32), nn.ReLU(), nn.MaxPool1d(2))
        self.conv2 = nn.Sequential(nn.Conv1d(32, 64, kernel_size=3, padding=1), nn.BatchNorm1d(64), nn.ReLU(), nn.MaxPool1d(2))
        self.flatten = nn.Flatten()
        self.fc = nn.Sequential(nn.Linear(64 * 5, 128), nn.ReLU(), nn.Dropout(0.4), nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, num_classes))
    def forward(self, x):
        x = self.conv1(x)
        x = self.conv2(x)
        x = self.flatten(x)
        return self.fc(x)

# ═══════════════════════════════════════════════════════════════════════════════
# DETECTOR CORE
# ═══════════════════════════════════════════════════════════════════════════════

class NetworkMonitor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.labels = ["Normal", "DoS", "BruteForce", "Injection"]
        self.load_model()
        
    def load_model(self):
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            try:
                self.model = ZeroDayCNN()
                self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device))
                self.model.to(self.device).eval()
                with open(SCALER_PATH, 'rb') as f:
                    self.scaler = pickle.load(f)
                print("✅ [ZeroDay] CNN Model and Scaler loaded")
            except Exception as e:
                print(f"❌ [ZeroDay] Error loading model: {e}")
        else:
            print("⚠️ [ZeroDay] Waiting for models/zeroday/ files...")

    def predict(self, features):
        """
        features: list of 20 network flow metrics
        """
        if self.model is None or self.scaler is None:
            return "UNKNOWN", 0.0
            
        # Scale and reshape
        X = np.array(features).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        X_tensor = torch.FloatTensor(X_scaled.reshape(1, 1, -1)).to(self.device)
        
        with torch.no_grad():
            output = self.model(X_tensor)
            prob = torch.softmax(output, dim=1)
            pred_idx = output.argmax(1).item()
            confidence = prob[0][pred_idx].item()
            
        return self.labels[pred_idx], confidence

    def report_attack(self, attack_type, confidence, raw_features):
        """Send alert to aggregator."""
        if attack_type == "Normal":
            return
            
        alert_log = {
            "logs": [{
                "name": "zero_day_detection",
                "hostIdentifier": "network-gateway-01",
                "calendarTime": datetime.now().isoformat(),
                "unixTime": int(time.time()),
                "epoch": 0, "counter": 0,
                "columns": {
                    "attack_type": attack_type,
                    "confidence": f"{confidence:.2f}",
                    "severity": "high" if confidence > 0.8 else "medium",
                    "source": "1D-CNN-Monitor"
                }
            }]
        }
        
        try:
            requests.post(AGGREGATOR_URL, json=alert_log)
            print(f"🚨 [ALERT] Sent: {attack_type} ({confidence:.2f}%)")
        except:
            print("⚠️ Failed to send alert to aggregator")

    def run_simulated_monitor(self):
        """Simulate live traffic monitoring with random flows."""
        print("🔍 [ZeroDay] Monitoring network traffic...")
        
        # Simulate local flow capture
        while True:
            # Generate a "Normal" flow mostly
            if random.random() < 0.95:
                features = self._generate_sim_flow("normal")
            else:
                features = self._generate_sim_flow(random.choice(["dos", "bruteforce", "injection"]))
                
            attack_type, confidence = self.predict(features)
            if attack_type != "Normal":
                self.report_attack(attack_type, confidence, features)
            
            time.sleep(2)

    def _generate_sim_flow(self, flow_type):
        # Implementation of same logic from notebook for demo purposes
        # In real life, this would read from a pcap/log file
        import random
        feat = np.zeros(20)
        # simplified simulation
        if flow_type == "normal": feat[0] = 1000; feat[18] = 500
        elif flow_type == "dos": feat[0] = 50; feat[9] = 10000; feat[18] = 60
        return feat

if __name__ == "__main__":
    monitor = NetworkMonitor()
    # For now, just wait for files. Integration will happen in Phase 4.
    if monitor.model:
        # monitor.run_simulated_monitor() # Uncomment to start live sim
        pass
