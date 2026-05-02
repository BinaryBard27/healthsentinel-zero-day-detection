"""
HealthSentinel FL Hospital Client (Day 12)
==========================================
Each hospital runs this locally. 
Trains on private medical data and only sends math (weights) to the server.
"""

import torch
import torch.nn as nn
import flwr as fl
import numpy as np
from fl_model import FLModel, get_parameters, set_parameters

# ═══════════════════════════════════════════════════════════════════════════════
# DATA SIMULATOR (Local Hospital Private Data)
# ═══════════════════════════════════════════════════════════════════════════════
def load_data():
    # Simulated 100 patient records (10 features each)
    X = torch.randn(100, 10)
    # Simple rule: if feature[0] > 0, it's 'suspicious'
    y = (X[:, 0] > 0).float().view(-1, 1)
    return X, y

class HospitalClient(fl.client.NumPyClient):
    def __init__(self, model, X, y):
        self.model = model
        self.X = X
        self.y = y
        self.optim = torch.optim.Adam(self.model.parameters(), lr=0.01)
        self.crit = nn.BCELoss()

    def get_parameters(self, config):
        return get_parameters(self.model)

    def fit(self, parameters, config):
        set_parameters(self.model, parameters)
        self.model.train()
        
        # Train for 5 epochs locally
        for _ in range(5):
            self.optim.zero_grad()
            out = self.model(self.X)
            loss = self.crit(out, self.y)
            loss.backward()
            self.optim.step()
            
        print(f"🏥 [LOCAL TRAIN] Completed round. Loss: {loss.item():.4f}")
        return get_parameters(self.model), len(self.X), {}

    def evaluate(self, parameters, config):
        set_parameters(self.model, parameters)
        self.model.eval()
        with torch.no_grad():
            out = self.model(self.X)
            loss = self.crit(out, self.y)
            acc = ((out > 0.5).float() == self.y).float().mean()
        
        print(f"📊 [LOCAL EVAL] Accuracy: {acc.item():.2%}")
        return float(loss), len(self.X), {"accuracy": float(acc)}

def main():
    model = FLModel()
    X, y = load_data()
    
    print("🔌 [FL CLIENT] Connecting to HealthSentinel Global Server...")
    fl.client.start_numpy_client(
        server_address="127.0.0.1:8088",
        client=HospitalClient(model, X, y)
    )

if __name__ == "__main__":
    main()
