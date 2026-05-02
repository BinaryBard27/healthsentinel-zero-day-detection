"""
Behavioral Feature Aggregator for LSTM Autoencoder
===================================================
Converts raw osquery/system logs into time-step behavioral vectors
suitable for insider threat detection via sequence reconstruction.

Author: HealthSentinel Team
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')


class BehavioralFeatureAggregator:
    """
    Aggregates raw event logs into fixed-interval behavioral time-steps.
    
    Each time-step represents aggregated user behavior over a window (e.g., 5 minutes)
    creating a feature vector suitable for LSTM sequence modeling.
    """
    
    def __init__(self, window_minutes: int = 5):
        """
        Args:
            window_minutes: Time window for aggregating events (default: 5 minutes)
        """
        self.window_minutes = window_minutes
        self.feature_names = [
            'login_hour_normalized',
            'file_access_count',
            'sensitive_file_flag',
            'new_process_flag',
            'network_entropy',
            'privilege_level',
            'usb_event_flag',
            'data_transfer_size_log',
            'unique_files_accessed',
            'command_diversity',
            'afterhours_flag',
            'weekend_flag'
        ]
    
    def aggregate_events_to_timesteps(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert raw events to time-step behavioral vectors.
        
        Args:
            df: Raw log DataFrame with columns: timestamp, user, action, resource, etc.
        
        Returns:
            DataFrame with time-step vectors per user
        """
        print(f"🔧 Aggregating events into {self.window_minutes}-minute time-steps...")
        
        # Ensure timestamp is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values(['user', 'timestamp']).reset_index(drop=True)
        
        # Add time window bins
        df['time_window'] = df['timestamp'].dt.floor(f'{self.window_minutes}T')
        
        # Aggregate by user and time window
        aggregated = []
        
        for (user, window), group in df.groupby(['user', 'time_window']):
            features = self._extract_window_features(group, window)
            features['user'] = user
            features['timestamp'] = window
            aggregated.append(features)
        
        result_df = pd.DataFrame(aggregated)
        print(f"✅ Created {len(result_df):,} time-step vectors from {len(df):,} raw events")
        print(f"   Users: {result_df['user'].nunique()}")
        print(f"   Features per time-step: {len(self.feature_names)}")
        
        return result_df
    
    def _extract_window_features(self, group: pd.DataFrame, window_time: datetime) -> Dict:
        """Extract behavioral features from a time window of events"""
        
        # Get first event time for hour info
        first_event = group.iloc[0]
        hour = first_event['timestamp'].hour
        day_of_week = first_event['timestamp'].dayofweek
        
        # Sensitive file keywords
        phi_keywords = ['patient', 'ehr', 'medical', 'lab', 'imaging', 'pacs', 'emr', 'phi', 'hipaa']
        
        # Content analysis
        content_str = ' '.join(group.get('Content', group.get('action', '')).fillna('').astype(str).str.lower())
        resource_str = ' '.join(group.get('resource', group.get('Resource', '')).fillna('').astype(str).str.lower())
        
        features = {
            # Time features
            'login_hour_normalized': hour / 24.0,
            'afterhours_flag': 1 if (hour < 7 or hour > 19) else 0,
            'weekend_flag': 1 if day_of_week >= 5 else 0,
            
            # File access patterns
            'file_access_count': len(group),
            'unique_files_accessed': group.get('resource', group.get('Resource', pd.Series([]))).nunique(),
            'sensitive_file_flag': 1 if any(kw in resource_str for kw in phi_keywords) else 0,
            
            # Process/command diversity
            'new_process_flag': 1 if 'process' in content_str or 'exec' in content_str else 0,
            'command_diversity': group.get('action', group.get('Action', pd.Series([]))).nunique(),
            
            # Network activity
            'network_entropy': self._calculate_entropy(group.get('source_ip', group.get('Source', pd.Series([])))),
            
            # Privilege level
            'privilege_level': 1 if 'admin' in content_str or 'sudo' in content_str or 'root' in content_str else 0,
            
            # USB/external device
            'usb_event_flag': 1 if 'usb' in content_str or 'removable' in content_str else 0,
            
            # Data transfer
            'data_transfer_size_log': np.log1p(group.get('bytes_transferred', group.get('Bytes', pd.Series([0]))).sum()),
        }
        
        return features
    
    def _calculate_entropy(self, series: pd.Series) -> float:
        """Calculate Shannon entropy of a series"""
        if len(series) == 0:
            return 0.0
        
        value_counts = series.value_counts()
        probabilities = value_counts / len(series)
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        return float(entropy)
    
    def create_user_sequences(self, timestep_df: pd.DataFrame, 
                             sequence_length: int = 30,
                             stride: int = 1) -> Tuple[Dict, np.ndarray, List]:
        """
        Create sliding window sequences per user.
        
        Args:
            timestep_df: DataFrame of time-step vectors
            sequence_length: Number of time-steps per sequence (default: 30)
            stride: Step size for sliding window (default: 1)
        
        Returns:
            Tuple of (user_sequences_dict, feature_array, user_ids)
        """
        print(f"\n🔧 Creating sliding window sequences (length={sequence_length}, stride={stride})...")
        
        sequences = []
        user_ids = []
        
        for user in timestep_df['user'].unique():
            user_data = timestep_df[timestep_df['user'] == user].sort_values('timestamp')
            user_features = user_data[self.feature_names].values
            
            # Create sliding windows
            for i in range(0, len(user_features) - sequence_length + 1, stride):
                seq = user_features[i:i + sequence_length]
                sequences.append(seq)
                user_ids.append(user)
        
        sequences_array = np.array(sequences, dtype=np.float32)
        
        print(f"✅ Created {len(sequences):,} sequences")
        print(f"   Unique users: {len(set(user_ids))}")
        print(f"   Sequence shape: {sequences_array.shape}")
        
        # Create user mapping
        user_sequences = defaultdict(list)
        for idx, user in enumerate(user_ids):
            user_sequences[user].append(idx)
        
        return dict(user_sequences), sequences_array, user_ids
    
    def filter_normal_behavior(self, df: pd.DataFrame, 
                               label_column: str = 'label') -> pd.DataFrame:
        """
        Filter dataset to only normal behavior for unsupervised training.
        
        Args:
            df: DataFrame with labels
            label_column: Name of label column (0=normal, 1=threat)
        
        Returns:
            DataFrame with only normal behavior
        """
        if label_column not in df.columns:
            print("⚠️  No label column found. Assuming all data is normal.")
            return df
        
        normal_df = df[df[label_column] == 0].copy()
        
        print(f"\n🔍 Filtering to normal behavior only:")
        print(f"   Original: {len(df):,} events")
        print(f"   Normal: {len(normal_df):,} events ({len(normal_df)/len(df)*100:.1f}%)")
        print(f"   Filtered out: {len(df) - len(normal_df):,} threat events")
        
        return normal_df


def load_and_prepare_data(file_path: str, sample_size: int = None) -> pd.DataFrame:
    """
    Load merged log file and prepare for feature extraction.
    
    Args:
        file_path: Path to merged log CSV
        sample_size: Optional sample size for faster testing
    
    Returns:
        Prepared DataFrame
    """
    print("📂 Loading merged log file...")
    print(f"   Path: {file_path}")
    
    df = pd.read_csv(file_path, on_bad_lines='skip')
    print(f"   Loaded: {len(df):,} rows, {len(df.columns)} columns")
    
    # Sample if requested
    if sample_size and len(df) > sample_size:
        df = df.sample(sample_size, random_state=42)
        print(f"   Sampled: {len(df):,} rows for faster processing")
    
    # Normalize column names (handle different log formats)
    column_mapping = {
        'User': 'user',
        'Username': 'user',
        'uid': 'user',
        'Action': 'action',
        'Event': 'action',
        'event_type': 'action',
        'Resource': 'resource',
        'Target': 'resource',
        'file_path': 'resource',
        'Timestamp': 'timestamp',
        'Time': 'timestamp',
        'datetime': 'timestamp',
        'Source': 'source_ip',
        'source': 'source_ip',
        'ip_address': 'source_ip',
        'Bytes': 'bytes_transferred',
        'size': 'bytes_transferred',
        'Label': 'label',
        'is_threat': 'label',
        'anomaly': 'label'
    }
    
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns and new_name not in df.columns:
            df[new_name] = df[old_name]
    
    # Ensure required columns exist
    required_cols = ['timestamp', 'user', 'action']
    missing = [col for col in required_cols if col not in df.columns]
    
    if missing:
        print(f"⚠️  Missing required columns: {missing}")
        print(f"   Available columns: {list(df.columns)[:20]}")
    
    # Fill missing optional columns
    if 'resource' not in df.columns:
        df['resource'] = 'unknown'
    if 'source_ip' not in df.columns:
        df['source_ip'] = 'unknown'
    if 'bytes_transferred' not in df.columns:
        df['bytes_transferred'] = 0
    
    return df
