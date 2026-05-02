import pandas as pd
import numpy as np
from scipy.stats import ks_2samp
import time
import datetime
import json
import os

class DriftMonitor:
    def __init__(self, baseline_path, logs_path):
        self.baseline_path = baseline_path
        self.logs_path = logs_path
        print(f"[{datetime.datetime.now()}] Initializing DriftMonitor Service...")
        try:
            self.baseline_df = pd.read_csv(self.baseline_path)
            # Ensure the required columns exist. In simulation_features.csv, the first col is standardly entropy.
            # We'll map the indices if names don't exist, based on our prior knowledge:
            # 0: entropy, 5: suspicious_api
            self.baseline_entropy = self.baseline_df.iloc[:, 0].values
            self.baseline_api = self.baseline_df.iloc[:, 5].values
            print(f"[{datetime.datetime.now()}] Baseline loaded: {len(self.baseline_df)} records.")
        except Exception as e:
            print(f"Error loading baseline: {e}")

    def simulate_incoming_data(self, drift_multiplier=1.0):
        """Simulate 24h incoming traffic, with an optional drift multiplier."""
        print(f"[{datetime.datetime.now()}] Aggregating 24-Hour incoming telemetry logs...")
        time.sleep(1.5)
        # Sample base logs but add normal distribution noise to shift the mean
        base_entropy_sample = np.random.choice(self.baseline_entropy, 1000)
        base_api_sample = np.random.choice(self.baseline_api, 1000)
        
        if drift_multiplier > 1.0:
             # Introduce distribution shift for drift testing
             live_entropy = np.clip(base_entropy_sample + np.random.normal(0.2, 0.1, 1000) * drift_multiplier, 0, 1)
             live_api = np.clip(base_api_sample + np.random.normal(0.15, 0.1, 1000) * drift_multiplier, 0, 1)
        else:
             live_entropy = base_entropy_sample
             live_api = base_api_sample
             
        return live_entropy, live_api

    def check_drift(self, incoming_entropy, incoming_api):
        """Perform Kolmogorov-Smirnov Test for distribution drift."""
        print(f"[{datetime.datetime.now()}] Executing Kolmogorov-Smirnov (K-S) Anomaly Test...")
        
        stat_entropy, p_entropy = ks_2samp(self.baseline_entropy, incoming_entropy)
        stat_api, p_api = ks_2samp(self.baseline_api, incoming_api)
        
        print(f"  - Entropy Drift Statistic: {stat_entropy:.4f} (p-value: {p_entropy:.4e})")
        print(f"  - Suspicious_API Drift Statistic: {stat_api:.4f} (p-value: {p_api:.4e})")

        # Define data drift score based on maximum K-S distance
        drift_score = max(stat_entropy, stat_api)
        print(f"[{datetime.datetime.now()}] Maximum Data Drift Score: {drift_score:.4f}")
        return drift_score

    def trigger_slack_alert(self, drift_score):
        """Simulate a Slack Alert web-hook."""
        print(f"\n[SLACK ALERT] #soc-ml-ops")
        print(f"CRITICAL DATA DRIFT DETECTED: Score {drift_score:.4f} exceeds threshold 0.15!")
        print(f"Initiating Automated Synthetic Re-training Incident Response...\n")

    def synthetic_retraining(self):
        """Simulate the Automated Synthetic Re-training session."""
        print(f"[{datetime.datetime.now()}] [RETRAINING MODULE] Booting isolated container...")
        time.sleep(1)
        print(f"[{datetime.datetime.now()}] [RETRAINING MODULE] Ingesting latest /var/logs/quarantine...")
        time.sleep(1)
        print(f"[{datetime.datetime.now()}] [RETRAINING MODULE] Augmenting dataset with SMOTE...")
        time.sleep(1)
        print(f"[{datetime.datetime.now()}] [RETRAINING MODULE] Retraining StackingClassifier (Cost-Sensitive)...")
        time.sleep(2.5)
        print(f"[{datetime.datetime.now()}] [RETRAINING MODULE] Validation passed. Model swapped via hot-reload.")

    def run_daily_job(self, day=1, drift_multiplier=1.0):
        print("\n" + "="*60)
        print(f"STARTING DAILY CRON: DAY {day}")
        print("="*60)
        live_entropy, live_api = self.simulate_incoming_data(drift_multiplier)
        drift_score = self.check_drift(live_entropy, live_api)
        
        if drift_score > 0.15:
            self.trigger_slack_alert(drift_score)
            self.synthetic_retraining()
            health_status = "WARNING -> RECOVERED"
        else:
            health_status = "HEALTHY"
            
        print(f"\nPOSTING DASHBOARD REPORT: Recall Health = {health_status}\n")


if __name__ == "__main__":
    baseline_filepath = 'c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/Datasets/preprocessed data/Ransomware/Simulation/model/simulation_features.csv'
    monitor = DriftMonitor(baseline_filepath, logs_path='/tmp/quarantine_logs')
    
    # DAY 1: Normal Operation (No drift)
    monitor.run_daily_job(day=1, drift_multiplier=1.0)
    
    time.sleep(1)
    
    # DAY 2: Adversarial Shift (Drift injected)
    monitor.run_daily_job(day=2, drift_multiplier=1.5)
