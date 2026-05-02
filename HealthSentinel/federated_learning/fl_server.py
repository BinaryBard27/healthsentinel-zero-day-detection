"""
HealthSentinel FL Server (Day 12)
=================================
Aggregates model weights from multiple hospital nodes without seeing 1 byte 
of their actual patient data.
"""

import flwr as fl
import sys

def main():
    # Define strategy (FedAvg is the standard federated averaging algorithm)
    strategy = fl.server.strategy.FedAvg(
        fraction_fit=1.0,      # Sample 100% of available clients for training
        fraction_evaluate=0.5, # Sample 50% for evaluation
        min_fit_clients=2,     # Never train until at least 2 hospitals are online
        min_evaluate_clients=2,
        min_available_clients=2,
    )

    print("🌐 [FL SERVER] Starting HealthSentinel Global Aggregator...")
    print("📍 Location: localhost:8088")
    
    # Start Flower server
    fl.server.start_server(
        server_address="0.0.0.0:8088",
        config=fl.server.ServerConfig(num_rounds=3),
        strategy=strategy,
    )

if __name__ == "__main__":
    main()
