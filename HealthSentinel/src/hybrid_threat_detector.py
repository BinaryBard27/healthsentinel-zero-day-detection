"""
Hybrid Insider Threat Detector
==============================

Combines LSTM autoencoder (temporal) with Isolation Forest (feature-space)
for robust insider threat detection with confidence scoring.

Author: HealthSentinel Team
"""

import torch
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import deque
import pickle
from sklearn.ensemble import IsolationForest

from insider_threat_detector import InsiderThreatAutoencoder, InsiderThreatDetector


class HybridInsiderThreatDetector:
    """
    Combines two complementary anomaly detection approaches:
    
    1. LSTM Autoencoder: Detects temporal behavioral deviations
    2. Isolation Forest: Detects feature-space anomalies
    
    Confidence Levels:
    - HIGH: Both models agree (anomaly detected by both)
    - MEDIUM: One model detects anomaly
    - LOW: Neither model detects anomaly
    """
    
    def __init__(self, lstm_detector: InsiderThreatDetector, 
                 isolation_forest_path: Optional[str] = None):
        """
        Initialize hybrid detector.
        
        Args:
            lstm_detector: Trained LSTM autoencoder detector
            isolation_forest_path: Path to trained Isolation Forest (optional)
        """
        self.lstm_detector = lstm_detector
        
        # Load or create Isolation Forest
        if isolation_forest_path and Path(isolation_forest_path).exists():
            with open(isolation_forest_path, 'rb') as f:
                self.isolation_forest = pickle.load(f)
            print(f"✅ Loaded Isolation Forest from {isolation_forest_path}")
        else:
            self.isolation_forest = IsolationForest(
                contamination=0.1,  # Expect 10% anomalies
                random_state=42,
                n_jobs=-1
            )
            print("🆕 Initialized new Isolation Forest (needs training)")
        
        self.is_fitted = isolation_forest_path is not None
    
    def train_isolation_forest(self, time_step_vectors: np.ndarray):
        """
        Train Isolation Forest on normal behavior time-step vectors.
        
        Args:
            time_step_vectors: Array of shape [n_samples, n_features]
        """
        print(f"🔧 Training Isolation Forest on {len(time_step_vectors):,} time-steps...")
        self.isolation_forest.fit(time_step_vectors)
        self.is_fitted = True
        print("✅ Isolation Forest trained")
    
    def save_isolation_forest(self, path: str):
        """Save trained Isolation Forest"""
        with open(path, 'wb') as f:
            pickle.dump(self.isolation_forest, f)
        print(f"💾 Saved Isolation Forest to {path}")
    
    def detect(self, user_id: str, time_step_vector: np.ndarray,
               lstm_threshold_multiplier: float = 2.0,
               isolation_threshold: float = -0.5) -> Dict:
        """
        Hybrid detection using both LSTM and Isolation Forest.
        
        Args:
            user_id: User identifier
            time_step_vector: Current time-step feature vector [12 features]
            lstm_threshold_multiplier: LSTM threshold multiplier
            isolation_threshold: Isolation Forest decision threshold
        
        Returns:
            Detection result with combined confidence
        """
        # 1. LSTM temporal detection
        lstm_result = self.lstm_detector.detect(
            user_id, time_step_vector, lstm_threshold_multiplier
        )
        
        # 2. Isolation Forest feature-space detection
        if self.is_fitted:
            iso_score = self.isolation_forest.score_samples([time_step_vector])[0]
            iso_anomaly = iso_score < isolation_threshold
        else:
            iso_score = None
            iso_anomaly = False
        
        # 3. Combine results
        lstm_anomaly = lstm_result.get('is_anomaly', False)
        
        # Confidence levels
        if lstm_anomaly and iso_anomaly:
            confidence = 'HIGH'
            risk_score = 0.95
            alert_priority = 'CRITICAL'
        elif lstm_anomaly or iso_anomaly:
            confidence = 'MEDIUM'
            risk_score = 0.7 if lstm_anomaly else 0.6
            alert_priority = 'WARNING'
        else:
            confidence = 'LOW'
            risk_score = lstm_result.get('risk_score', 0.1)
            alert_priority = 'INFO'
        
        return {
            'is_anomaly': lstm_anomaly or iso_anomaly,
            'confidence': confidence,
            'alert_priority': alert_priority,
            'risk_score': risk_score,
            
            # LSTM details
            'lstm_anomaly': lstm_anomaly,
            'lstm_reconstruction_error': lstm_result.get('reconstruction_error'),
            'lstm_threshold': lstm_result.get('threshold'),
            'lstm_deviation_factor': lstm_result.get('deviation_factor'),
            
            # Isolation Forest details
            'isolation_forest_anomaly': iso_anomaly,
            'isolation_forest_score': float(iso_score) if iso_score is not None else None,
            'isolation_forest_threshold': isolation_threshold,
            
            # Metadata
            'user_id': user_id,
            'detection_method': self._get_detection_method(lstm_anomaly, iso_anomaly)
        }
    
    def _get_detection_method(self, lstm_anomaly: bool, iso_anomaly: bool) -> str:
        """Describe which method(s) detected the anomaly"""
        if lstm_anomaly and iso_anomaly:
            return 'LSTM + Isolation Forest (both agree)'
        elif lstm_anomaly:
            return 'LSTM only (temporal deviation)'
        elif iso_anomaly:
            return 'Isolation Forest only (feature-space anomaly)'
        else:
            return 'None (normal behavior)'
    
    def detect_batch(self, user_id: str, sequences: np.ndarray,
                    time_step_vectors: np.ndarray,
                    lstm_threshold_multiplier: float = 2.0,
                    isolation_threshold: float = -0.5) -> List[Dict]:
        """
        Batch detection on multiple sequences.
        
        Args:
            user_id: User identifier
            sequences: LSTM sequences [n_sequences, seq_len, n_features]
            time_step_vectors: Corresponding time-step vectors [n_sequences, n_features]
            lstm_threshold_multiplier: LSTM threshold
            isolation_threshold: Isolation Forest threshold
        
        Returns:
            List of detection results
        """
        # LSTM batch detection
        lstm_results = self.lstm_detector.detect_batch(
            user_id, sequences, lstm_threshold_multiplier
        )
        
        # Isolation Forest batch detection
        if self.is_fitted:
            iso_scores = self.isolation_forest.score_samples(time_step_vectors)
            iso_anomalies = iso_scores < isolation_threshold
        else:
            iso_scores = [None] * len(sequences)
            iso_anomalies = [False] * len(sequences)
        
        # Combine results
        results = []
        for i, (lstm_res, iso_score, iso_anom) in enumerate(zip(lstm_results, iso_scores, iso_anomalies)):
            lstm_anom = lstm_res['is_anomaly']
            
            if lstm_anom and iso_anom:
                confidence = 'HIGH'
                risk_score = 0.95
            elif lstm_anom or iso_anom:
                confidence = 'MEDIUM'
                risk_score = 0.7 if lstm_anom else 0.6
            else:
                confidence = 'LOW'
                risk_score = lstm_res['risk_score']
            
            results.append({
                'is_anomaly': lstm_anom or iso_anom,
                'confidence': confidence,
                'risk_score': risk_score,
                'lstm_anomaly': lstm_anom,
                'lstm_reconstruction_error': lstm_res['reconstruction_error'],
                'isolation_forest_anomaly': iso_anom,
                'isolation_forest_score': float(iso_score) if iso_score is not None else None
            })
        
        return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    import pandas as pd
    from behavioral_feature_aggregator import BehavioralFeatureAggregator, load_and_prepare_data
    
    print("="*80)
    print("HYBRID INSIDER THREAT DETECTOR - DEMO")
    print("="*80)
    
    # Paths
    MODEL_DIR = r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_autoencoder'
    
    # 1. Initialize LSTM detector
    print("\n📂 Loading LSTM detector...")
    lstm_detector = InsiderThreatDetector(
        model_path=f'{MODEL_DIR}/best_autoencoder.pt',
        baselines_path=f'{MODEL_DIR}/user_baselines.json',
        config_path=f'{MODEL_DIR}/training_results.json'
    )
    
    # 2. Initialize hybrid detector
    print("\n🔧 Initializing hybrid detector...")
    hybrid_detector = HybridInsiderThreatDetector(
        lstm_detector=lstm_detector,
        isolation_forest_path=f'{MODEL_DIR}/isolation_forest.pkl'
    )
    
    # 3. If Isolation Forest not trained, train it
    if not hybrid_detector.is_fitted:
        print("\n🔧 Training Isolation Forest...")
        
        # Load data
        df = load_and_prepare_data(
            r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs_complete.csv',
            sample_size=50000
        )
        
        # Aggregate to time-steps
        aggregator = BehavioralFeatureAggregator()
        timestep_df = aggregator.aggregate_events_to_timesteps(df)
        
        # Extract time-step vectors
        time_step_vectors = timestep_df[aggregator.feature_names].values
        
        # Train
        hybrid_detector.train_isolation_forest(time_step_vectors)
        hybrid_detector.save_isolation_forest(f'{MODEL_DIR}/isolation_forest.pkl')
    
    # 4. Test detection
    print("\n🔍 Testing hybrid detection...")
    
    # Load test data
    df = load_and_prepare_data(
        r'C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs_complete.csv',
        sample_size=5000
    )
    
    aggregator = BehavioralFeatureAggregator()
    timestep_df = aggregator.aggregate_events_to_timesteps(df)
    
    # Test on first user
    test_user = timestep_df['user'].iloc[0]
    user_data = timestep_df[timestep_df['user'] == test_user]
    
    print(f"\n   Testing user: {test_user}")
    print(f"   Time-steps: {len(user_data)}")
    
    # Detect
    anomalies = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
    
    for idx, row in user_data.iterrows():
        time_step = row[aggregator.feature_names].values
        
        result = hybrid_detector.detect(test_user, time_step)
        
        anomalies[result['confidence']] += 1
        
        if result['confidence'] in ['HIGH', 'MEDIUM']:
            print(f"\n   🚨 {result['confidence']} confidence anomaly at {row['timestamp']}")
            print(f"      Detection: {result['detection_method']}")
            print(f"      Risk score: {result['risk_score']:.2f}")
            if result['lstm_reconstruction_error']:
                print(f"      LSTM error: {result['lstm_reconstruction_error']:.6f}")
            if result['isolation_forest_score']:
                print(f"      Iso Forest score: {result['isolation_forest_score']:.6f}")
    
    print(f"\n📊 Detection Summary:")
    print(f"   Total time-steps: {len(user_data)}")
    print(f"   HIGH confidence: {anomalies['HIGH']}")
    print(f"   MEDIUM confidence: {anomalies['MEDIUM']}")
    print(f"   LOW confidence: {anomalies['LOW']}")
