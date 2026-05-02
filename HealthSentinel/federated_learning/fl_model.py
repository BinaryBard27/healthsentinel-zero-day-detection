"""
HealthSentinel Federated Learning Model
=======================================
Shared architecture for Global and Local training.
Predicts Medical Diagnosis Anomalies or Traffic Patterns.
"""

import torch
import torch.nn as nn

class FLModel(nn.Module):
    def __init__(self, input_dim=10, hidden_dim=32, output_dim=1):
        super(FLModel, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.fc(x)

def get_parameters(model):
    return [val.cpu().numpy() for _, val in model.state_dict().items()]

def set_parameters(model, parameters):
    params_dict = zip(model.state_dict().keys(), parameters)
    state_dict = {k: torch.tensor(v) for k, v in params_dict}
    model.load_state_dict(state_dict, strict=True)
