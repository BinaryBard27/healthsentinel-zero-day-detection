"""
================================================================================
HEALTHCARE INSIDER THREAT DETECTION - PRODUCTION LSTM SYSTEM
================================================================================

Production-grade LSTM training system for real osquery/healthcare log files
Addresses data leakage, adds proper feature engineering, and includes
model interpretability and threshold tuning

Author: Healthcare Security Team
Date: 2024
Version: 2.0 (Production)
================================================================================
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import pickle
import os
import glob
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# TensorFlow and Keras
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    LSTM, Dense, Dropout, Embedding, Bidirectional, 
    Input, Concatenate, BatchNormalization,
    GlobalAveragePooling1D, Conv1D, MaxPooling1D,
    MultiHeadAttention, LayerNormalization, Add
)
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau,
    TensorBoard, LearningRateScheduler
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

# Scikit-learn
from sklearn.preprocessing import LabelEncoder, StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
    roc_curve, precision_recall_curve, f1_score,
    accuracy_score, precision_score, recall_score
)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print(" " * 15 + "HEALTHCARE INSIDER THREAT DETECTION - PRODUCTION")
print(" " * 25 + "LSTM Training System v2.0")
print("="*80)


# ============================================================================
# SECTION 1: GPU CONFIGURATION
# ============================================================================

def configure_gpu():
    """Configure GPU for optimal performance"""
    print("\n[1/11] Configuring GPU...")
    print("-" * 80)
    
    gpus = tf.config.list_physical_devices('GPU')
    
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            
            from tensorflow.keras import mixed_precision
            policy = mixed_precision.Policy('mixed_float16')
            mixed_precision.set_global_policy(policy)
            
            print(f"GPU Detected: {gpus}")
            print(f"Mixed Precision: {policy.name}")
            print(f"Memory Growth: Enabled")
            return True
        except RuntimeError as e:
            print(f"GPU configuration error: {e}")
            return False
    else:
        print("No GPU detected - training will use CPU (slower)")
        return False


# ============================================================================
# SECTION 2: LOG FILE LOADING
# ============================================================================

class LogFileLoader:
    """Load and parse real log files from various formats"""
    
    @staticmethod
    def load_osquery_json(file_path: str) -> pd.DataFrame:
        """Load osquery JSON logs"""
        records = []
        
        with open(file_path, 'r') as f:
            for line in f:
                try:
                    record = json.loads(line.strip())
                    records.append(record)
                except json.JSONDecodeError:
                    continue
        
        return pd.DataFrame(records)
    
    @staticmethod
    def load_csv_logs(file_path: str) -> pd.DataFrame:
        """Load CSV formatted logs"""
        return pd.read_csv(file_path)
    
    @staticmethod
    def load_directory(directory: str, pattern: str = "*.json") -> pd.DataFrame:
        """Load all log files from directory"""
        print(f"\n[2/11] Loading Log Files from: {directory}")
        print("-" * 80)
        
        all_files = glob.glob(os.path.join(directory, pattern))
        
        if not all_files:
            raise FileNotFoundError(f"No files matching '{pattern}' found in {directory}")
        
        print(f"Found {len(all_files)} log files")
        
        dfs = []
        for file_path in all_files:
            try:
                if file_path.endswith('.json'):
                    df = LogFileLoader.load_osquery_json(file_path)
                elif file_path.endswith('.csv'):
                    df = LogFileLoader.load_csv_logs(file_path)
                else:
                    continue
                
                dfs.append(df)
                print(f"  Loaded: {os.path.basename(file_path)} ({len(df):,} records)")
            except Exception as e:
                print(f"  Error loading {file_path}: {e}")
                continue
        
        if not dfs:
            raise ValueError("No valid log files could be loaded")
        
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"\nTotal records loaded: {len(combined_df):,}")
        
        return combined_df
    
    @staticmethod
    def normalize_log_format(df: pd.DataFrame) -> pd.DataFrame:
        """Normalize different log formats to standard schema"""
        print("\n[2.5/11] Normalizing Log Format...")
        print("-" * 80)
        
        required_columns = {
            'user': ['username', 'user', 'uid', 'user_id'],
            'action': ['action', 'event_type', 'event', 'activity'],
            'resource': ['resource', 'target', 'object', 'file_path'],
            'timestamp': ['timestamp', 'time', 'datetime', 'event_time'],
            'source_ip': ['source_ip', 'ip_address', 'remote_address', 'client_ip']
        }
        
        optional_columns = {
            'access_type': ['access_type', 'operation', 'method'],
            'bytes_transferred': ['bytes', 'size', 'bytes_transferred'],
            'session_duration': ['duration', 'session_duration', 'time_spent']
        }
        
        normalized_df = pd.DataFrame()
        
        # Map required columns
        for standard_name, possible_names in required_columns.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    normalized_df[standard_name] = df[possible_name]
                    break
            
            if standard_name not in normalized_df.columns:
                if standard_name == 'source_ip':
                    normalized_df[standard_name] = 'unknown'
                else:
                    raise ValueError(f"Required column '{standard_name}' not found. "
                                   f"Looked for: {possible_names}")
        
        # Map optional columns
        for standard_name, possible_names in optional_columns.items():
            for possible_name in possible_names:
                if possible_name in df.columns:
                    normalized_df[standard_name] = df[possible_name]
                    break
            
            if standard_name not in normalized_df.columns:
                if standard_name == 'bytes_transferred':
                    normalized_df[standard_name] = 0
                elif standard_name == 'session_duration':
                    normalized_df[standard_name] = 0
                elif standard_name == 'access_type':
                    normalized_df[standard_name] = 'unknown'
        
        # Add label column if exists
        if 'label' in df.columns:
            normalized_df['label'] = df['label']
        elif 'is_threat' in df.columns:
            normalized_df['label'] = df['is_threat']
        elif 'anomaly' in df.columns:
            normalized_df['label'] = df['anomaly']
        else:
            print("WARNING: No label column found. You'll need to label data manually.")
            normalized_df['label'] = 0
        
        print(f"Normalized {len(normalized_df):,} records")
        print(f"Columns: {list(normalized_df.columns)}")
        
        return normalized_df


# ============================================================================
# SECTION 3: ADVANCED FEATURE ENGINEERING
# ============================================================================

class AdvancedFeatureEngineer:
    """Advanced feature engineering for behavioral analysis"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_jobs=-1
        )
        self.user_baselines = {}
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced behavioral features"""
        print("\n[3/11] Engineering Advanced Features...")
        print("-" * 80)
        
        df = df.copy()
        
        # Convert timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp'])
        df = df.sort_values(['user', 'timestamp']).reset_index(drop=True)
        
        # Basic time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        df['day_of_month'] = df['timestamp'].dt.day
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_afterhours'] = ((df['hour'] < 7) | (df['hour'] > 19)).astype(int)
        df['is_night'] = ((df['hour'] >= 22) | (df['hour'] < 6)).astype(int)
        
        # Temporal features
        df['time_since_last'] = df.groupby('user')['timestamp'].diff().dt.total_seconds().fillna(0)
        df['log_time_diff'] = np.log1p(df['time_since_last'])
        df['user_event_count'] = df.groupby('user').cumcount() + 1
        
        # Data transfer features
        df['log_bytes'] = np.log1p(df['bytes_transferred'].fillna(0))
        df['log_duration'] = np.log1p(df['session_duration'].fillna(0))
        
        # User behavioral baselines
        print("  Computing user behavioral baselines...")
        user_stats = df.groupby('user').agg({
            'hour': ['mean', 'std'],
            'day_of_week': ['mean', 'std'],
            'is_weekend': 'mean',
            'is_afterhours': 'mean',
            'bytes_transferred': ['mean', 'std', 'max'],
            'session_duration': ['mean', 'std']
        }).fillna(0)
        
        user_stats.columns = ['_'.join(col).strip() for col in user_stats.columns.values]
        user_stats = user_stats.add_prefix('user_baseline_')
        
        df = df.merge(user_stats, left_on='user', right_index=True, how='left')
        
        # Deviation from baseline
        df['hour_deviation'] = np.abs(df['hour'] - df['user_baseline_hour_mean'])
        df['bytes_zscore'] = ((df['bytes_transferred'] - df['user_baseline_bytes_transferred_mean']) / 
                              (df['user_baseline_bytes_transferred_std'] + 1e-6))
        df['duration_zscore'] = ((df['session_duration'] - df['user_baseline_session_duration_mean']) / 
                                (df['user_baseline_session_duration_std'] + 1e-6))
        
        # Rolling window features
        print("  Computing rolling window statistics...")
        for window in [5, 10, 20]:
            df[f'rolling_avg_bytes_{window}'] = (
                df.groupby('user')['bytes_transferred']
                .transform(lambda x: x.rolling(window, min_periods=1).mean())
            )
            df[f'rolling_std_bytes_{window}'] = (
                df.groupby('user')['bytes_transferred']
                .transform(lambda x: x.rolling(window, min_periods=1).std())
            )
        
        # Action frequency features
        df['action_count_last_hour'] = df.groupby('user')['timestamp'].transform(
            lambda x: x.rolling('1H').count()
        )
        
        # Resource access patterns
        df['unique_resources_accessed'] = df.groupby('user')['resource'].transform(
            lambda x: x.expanding().nunique()
        )
        
        # Healthcare-specific features
        phi_keywords = ['patient', 'ehr', 'medical', 'lab', 'imaging', 'pacs', 'emr', 'phi']
        df['is_phi'] = df['resource'].str.lower().str.contains('|'.join(phi_keywords), na=False).astype(int)
        df['is_vip'] = df['resource'].str.lower().str.contains('vip', na=False).astype(int)
        
        # Isolation Forest anomaly score
        print("  Computing anomaly scores with Isolation Forest...")
        numeric_features = [
            'hour', 'day_of_week', 'log_bytes', 'log_duration', 
            'hour_deviation', 'bytes_zscore', 'duration_zscore'
        ]
        
        X_anomaly = df[numeric_features].fillna(0)
        self.isolation_forest.fit(X_anomaly)
        df['anomaly_score'] = self.isolation_forest.score_samples(X_anomaly)
        df['is_anomaly'] = (self.isolation_forest.predict(X_anomaly) == -1).astype(int)
        
        print(f"  Total features created: {len(df.columns)}")
        print(f"  Anomalies detected: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.2f}%)")
        
        return df


# ============================================================================
# SECTION 4: USER-BASED DATA SPLITTING (PREVENTS LEAKAGE)
# ============================================================================

def split_by_users(df: pd.DataFrame, train_pct: float = 0.7, 
                   val_pct: float = 0.15, test_pct: float = 0.15,
                   random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split data by users to prevent data leakage
    
    This ensures that a user's sequences don't appear in both train and test sets
    """
    print("\n[4/11] Splitting Data by Users (Preventing Leakage)...")
    print("-" * 80)
    
    users = df['user'].unique()
    np.random.seed(random_state)
    np.random.shuffle(users)
    
    n_train = int(len(users) * train_pct)
    n_val = int(len(users) * val_pct)
    
    train_users = users[:n_train]
    val_users = users[n_train:n_train+n_val]
    test_users = users[n_train+n_val:]
    
    train_df = df[df['user'].isin(train_users)].copy()
    val_df = df[df['user'].isin(val_users)].copy()
    test_df = df[df['user'].isin(test_users)].copy()
    
    print(f"Train: {len(train_users)} users, {len(train_df):,} events ({train_df['label'].mean()*100:.2f}% threats)")
    print(f"Val:   {len(val_users)} users, {len(val_df):,} events ({val_df['label'].mean()*100:.2f}% threats)")
    print(f"Test:  {len(test_users)} users, {len(test_df):,} events ({test_df['label'].mean()*100:.2f}% threats)")
    print("\nNo user overlap - data leakage prevented")
    
    return train_df, val_df, test_df


# ============================================================================
# SECTION 5: ADVANCED PREPROCESSING
# ============================================================================

class AdvancedLogPreprocessor:
    """Advanced preprocessor with better handling of real-world data"""
    
    def __init__(self, sequence_length: int = 50):
        self.sequence_length = sequence_length
        self.encoders = {}
        self.scaler = RobustScaler()
        self.vocab_sizes = {}
        self.feature_names = []
        self.categorical_features = []
        self.numerical_features = []
        
    def fit_transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Fit and transform training data"""
        
        # Define features
        self.categorical_features = ['user', 'action', 'resource', 'access_type', 'source_ip']
        
        self.numerical_features = [
            'hour', 'day_of_week', 'month', 'is_weekend', 'is_afterhours', 'is_night',
            'log_time_diff', 'user_event_count', 'log_bytes', 'log_duration',
            'hour_deviation', 'bytes_zscore', 'duration_zscore',
            'rolling_avg_bytes_5', 'rolling_std_bytes_5',
            'rolling_avg_bytes_10', 'rolling_std_bytes_10',
            'action_count_last_hour', 'unique_resources_accessed',
            'is_phi', 'is_vip', 'anomaly_score', 'is_anomaly'
        ]
        
        # Filter to existing columns
        self.numerical_features = [f for f in self.numerical_features if f in df.columns]
        
        print("\n[5/11] Preprocessing Features...")
        print("-" * 80)
        print(f"Categorical features: {len(self.categorical_features)}")
        print(f"Numerical features: {len(self.numerical_features)}")
        
        # Encode categorical
        encoded_features = {}
        for feature in self.categorical_features:
            if feature in df.columns:
                self.encoders[feature] = LabelEncoder()
                df[feature] = df[feature].fillna('UNKNOWN').astype(str)
                encoded_features[feature] = self.encoders[feature].fit_transform(df[feature])
                self.vocab_sizes[feature] = len(self.encoders[feature].classes_)
                print(f"  {feature}: {self.vocab_sizes[feature]} unique values")
        
        # Scale numerical
        numerical_data = df[self.numerical_features].fillna(0).values
        scaled_numerical = self.scaler.fit_transform(numerical_data)
        
        # Combine features
        all_features = np.column_stack([
            encoded_features.get(f, np.zeros(len(df))) 
            for f in self.categorical_features if f in encoded_features
        ] + [scaled_numerical])
        
        # Create sequences
        sequences, labels = self._create_sequences(df, all_features)
        
        return sequences, labels
    
    def transform(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Transform validation/test data"""
        
        # Encode categorical
        encoded_features = {}
        for feature in self.categorical_features:
            if feature in df.columns:
                df[feature] = df[feature].fillna('UNKNOWN').astype(str)
                encoded_features[feature] = self.encoders[feature].transform(df[feature])
        
        # Scale numerical
        numerical_data = df[self.numerical_features].fillna(0).values
        scaled_numerical = self.scaler.transform(numerical_data)
        
        # Combine features
        all_features = np.column_stack([
            encoded_features.get(f, np.zeros(len(df))) 
            for f in self.categorical_features if f in encoded_features
        ] + [scaled_numerical])
        
        # Create sequences
        sequences, labels = self._create_sequences(df, all_features)
        
        return sequences, labels
    
    def _create_sequences(self, df: pd.DataFrame, features: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Create sequences grouped by user"""
        sequences = []
        labels = []
        
        for user in df['user'].unique():
            user_mask = df['user'] == user
            user_features = features[user_mask]
            user_labels = df.loc[user_mask, 'label'].values if 'label' in df.columns else np.zeros(sum(user_mask))
            
            # Sliding window
            for i in range(len(user_features) - self.sequence_length + 1):
                seq = user_features[i:i + self.sequence_length]
                sequences.append(seq)
                # Label is 1 if ANY event in sequence is a threat
                labels.append(int(user_labels[i:i + self.sequence_length].max()))
        
        return np.array(sequences, dtype=np.float32), np.array(labels, dtype=np.int32)


# ============================================================================
# SECTION 6: IMPROVED MODEL ARCHITECTURE
# ============================================================================

def build_production_lstm_model(input_shape: Tuple[int, int], 
                                lstm_units: int = 256,
                                dropout_rate: float = 0.3,
                                l2_reg: float = 0.001,
                                learning_rate: float = 0.001,
                                use_multi_head_attention: bool = True) -> Model:
    """
    Build production-grade LSTM with:
    - Multi-head attention
    - Residual connections
    - Better regularization
    - Layer normalization
    """
    print("\n[6/11] Building Production LSTM Model...")
    print("-" * 80)
    
    inputs = Input(shape=input_shape, name='sequence_input')
    
    # First Bidirectional LSTM
    x = Bidirectional(
        LSTM(
            lstm_units,
            return_sequences=True,
            kernel_regularizer=l2(l2_reg),
            recurrent_regularizer=l2(l2_reg),
            recurrent_dropout=0.1
        ),
        name='bi_lstm_1'
    )(inputs)
    x = LayerNormalization()(x)
    x = Dropout(dropout_rate)(x)
    
    # Second Bidirectional LSTM with residual
    lstm_2 = Bidirectional(
        LSTM(
            lstm_units // 2,
            return_sequences=True,
            kernel_regularizer=l2(l2_reg),
            recurrent_regularizer=l2(l2_reg),
            recurrent_dropout=0.1
        ),
        name='bi_lstm_2'
    )(x)
    lstm_2 = LayerNormalization()(lstm_2)
    
    # Multi-head attention mechanism
    if use_multi_head_attention:
        # Self-attention
        attention_output = MultiHeadAttention(
            num_heads=8,
            key_dim=lstm_units // 8,
            dropout=dropout_rate,
            name='multi_head_attention'
        )(lstm_2, lstm_2)
        attention_output = LayerNormalization()(attention_output)
        x = Add()([lstm_2, attention_output])  # Residual connection
    else:
        # Simple attention
        attention = Dense(1, activation='tanh', name='attention_scores')(lstm_2)
        attention_weights = tf.nn.softmax(attention, axis=1, name='attention_weights')
        x = tf.reduce_sum(lstm_2 * attention_weights, axis=1, name='attention_output')
    
    # Global pooling if using multi-head attention
    if use_multi_head_attention:
        x = GlobalAveragePooling1D()(x)
    
    x = Dropout(dropout_rate)(x)
    
    # Dense classification head
    x = Dense(128, activation='relu', kernel_regularizer=l2(l2_reg), name='dense_1')(x)
    x = LayerNormalization()(x)
    x = Dropout(dropout_rate + 0.1)(x)
    
    x = Dense(64, activation='relu', kernel_regularizer=l2(l2_reg), name='dense_2')(x)
    x = LayerNormalization()(x)
    x = Dropout(dropout_rate)(x)
    
    x = Dense(32, activation='relu', kernel_regularizer=l2(l2_reg), name='dense_3')(x)
    x = Dropout(dropout_rate)(x)
    
    # Output
    outputs = Dense(1, activation='sigmoid', dtype='float32', name='threat_probability')(x)
    
    # Create model
    model = Model(inputs=inputs, outputs=outputs, name='Healthcare_Threat_Detector_v2')
    
    # Compile
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='binary_crossentropy',
        metrics=[
            'accuracy',
            tf.keras.metrics.Precision(name='precision'),
            tf.keras.metrics.Recall(name='recall'),
            tf.keras.metrics.AUC(name='auc', curve='ROC'),
            tf.keras.metrics.AUC(name='prc', curve='PR')
        ]
    )
    
    print(f"Model built successfully")
    print(f"  Total parameters: {model.count_params():,}")
    print(f"  Trainable parameters: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")
    print(f"  Architecture: Bi-LSTM + Multi-Head Attention + Dense Layers")
    
    return model


# ============================================================================
# SECTION 7: TRAINING WITH CALLBACKS
# ============================================================================

def train_production_model(model: Model, 
                           X_train: np.ndarray, y_train: np.ndarray,
                           X_val: np.ndarray, y_val: np.ndarray,
                           epochs: int = 100,
                           batch_size: int = 256,
                           class_weight: Optional[Dict] = None) -> keras.callbacks.History:
    """Train the model with production-grade callbacks"""
    print("\n[7/11] Training Model...")
    print("-" * 80)
    
    # Calculate class weights if not provided
    if class_weight is None:
        neg_count = np.sum(y_train == 0)
        pos_count = np.sum(y_train == 1)
        total = len(y_train)
        
        class_weight = {
            0: total / (2 * neg_count) if neg_count > 0 else 1.0,
            1: total / (2 * pos_count) if pos_count > 0 else 1.0
        }
    
    print(f"  Epochs: {epochs}")
    print(f"  Batch size: {batch_size}")
    print(f"  Class weights: {class_weight}")
    print(f"  Training samples: {len(X_train):,}")
    print(f"  Validation samples: {len(X_val):,}")
    print("-" * 80)
    
    # Create output directory
    os.makedirs('models', exist_ok=True)
    os.makedirs('logs', exist_ok=True)
    
    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_auc',
            patience=20,
            restore_best_weights=True,
            mode='max',
            verbose=1
        ),
        ModelCheckpoint(
            'models/best_model.keras',
            monitor='val_auc',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=7,
            min_lr=1e-7,
            verbose=1
        ),
        TensorBoard(
            log_dir=f'logs/tensorboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
            histogram_freq=1
        )
    ]
    
    # Train
    history = model.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=1
    )
    
    print("\nTraining complete!")
    
    return history


# ============================================================================
# SECTION 8: THRESHOLD OPTIMIZATION
# ============================================================================

def find_optimal_threshold(y_true: np.ndarray, 
                          y_proba: np.ndarray,
                          target_recall: float = 0.95,
                          target_precision: float = None) -> Dict:
    """
    Find optimal threshold based on operational requirements
    
    Healthcare typically prioritizes high recall (catch all threats)
    even at the cost of some false positives
    """
    print("\n[8/11] Optimizing Decision Threshold...")
    print("-" * 80)
    
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
    
    results = {}
    
    # Threshold for target recall
    if target_recall:
        idx = np.argmin(np.abs(recall - target_recall))
        results['recall_optimized'] = {
            'threshold': float(thresholds[idx]) if idx < len(thresholds) else 0.5,
            'precision': float(precision[idx]),
            'recall': float(recall[idx]),
            'f1': float(2 * precision[idx] * recall[idx] / (precision[idx] + recall[idx]))
        }
        print(f"\nThreshold for {target_recall*100}% Recall:")
        print(f"  Threshold: {results['recall_optimized']['threshold']:.4f}")
        print(f"  Precision: {results['recall_optimized']['precision']:.4f}")
        print(f"  Recall: {results['recall_optimized']['recall']:.4f}")
        print(f"  F1: {results['recall_optimized']['f1']:.4f}")
    
    # Threshold for target precision
    if target_precision:
        idx = np.argmin(np.abs(precision - target_precision))
        results['precision_optimized'] = {
            'threshold': float(thresholds[idx]) if idx < len(thresholds) else 0.5,
            'precision': float(precision[idx]),
            'recall': float(recall[idx]),
            'f1': float(2 * precision[idx] * recall[idx] / (precision[idx] + recall[idx]))
        }
        print(f"\nThreshold for {target_precision*100}% Precision:")
        print(f"  Threshold: {results['precision_optimized']['threshold']:.4f}")
        print(f"  Precision: {results['precision_optimized']['precision']:.4f}")
        print(f"  Recall: {results['precision_optimized']['recall']:.4f}")
        print(f"  F1: {results['precision_optimized']['f1']:.4f}")
    
    # F1-optimal threshold
    f1_scores = 2 * precision * recall / (precision + recall + 1e-10)
    idx = np.argmax(f1_scores)
    results['f1_optimized'] = {
        'threshold': float(thresholds[idx]) if idx < len(thresholds) else 0.5,
        'precision': float(precision[idx]),
        'recall': float(recall[idx]),
        'f1': float(f1_scores[idx])
    }
    print(f"\nThreshold for Best F1:")
    print(f"  Threshold: {results['f1_optimized']['threshold']:.4f}")
    print(f"  Precision: {results['f1_optimized']['precision']:.4f}")
    print(f"  Recall: {results['f1_optimized']['recall']:.4f}")
    print(f"  F1: {results['f1_optimized']['f1']:.4f}")
    
    return results


# ============================================================================
# SECTION 9: EVALUATION
# ============================================================================

def evaluate_production_model(model: Model,
                              X_test: np.ndarray,
                              y_test: np.ndarray,
                              threshold: float = 0.5,
                              batch_size: int = 256) -> Dict:
    """Comprehensive model evaluation"""
    print("\n[9/11] Evaluating Model...")
    print("-" * 80)
    
    # Get predictions
    y_pred_proba = model.predict(X_test, batch_size=batch_size, verbose=0).flatten()
    y_pred = (y_pred_proba >= threshold).astype(int)
    
    # Metrics
    test_loss = model.evaluate(X_test, y_test, batch_size=batch_size, verbose=0)[0]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    auc = roc_auc_score(y_test, y_pred_proba)
    
    print("\nTEST SET RESULTS")
    print("=" * 80)
    print(f"Loss:              {test_loss:.4f}")
    print(f"Accuracy:          {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision:         {prec:.4f} ({prec*100:.2f}%)")
    print(f"Recall:            {rec:.4f} ({rec*100:.2f}%)")
    print(f"F1-Score:          {f1:.4f}")
    print(f"ROC-AUC:           {auc:.4f}")
    print(f"Threshold:         {threshold:.4f}")
    print("=" * 80)
    
    print("\nClassification Report:")
    print("-" * 80)
    print(classification_report(y_test, y_pred, target_names=['Benign', 'Threat'], digits=4))
    
    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    
    print("\nConfusion Matrix Breakdown:")
    print("-" * 80)
    print(f"True Negatives:    {tn:,} (Correctly identified benign)")
    print(f"False Positives:   {fp:,} (Benign misclassified as threat)")
    print(f"False Negatives:   {fn:,} (Threat misclassified as benign) [CRITICAL]")
    print(f"True Positives:    {tp:,} (Correctly identified threats)")
    print("-" * 80)
    
    return {
        'loss': test_loss,
        'accuracy': acc,
        'precision': prec,
        'recall': rec,
        'f1': f1,
        'auc': auc,
        'predictions': y_pred,
        'probabilities': y_pred_proba,
        'confusion_matrix': cm,
        'threshold': threshold
    }


# ============================================================================
# SECTION 10: VISUALIZATION
# ============================================================================

def create_visualizations(history: keras.callbacks.History,
                         results: Dict,
                         y_test: np.ndarray,
                         threshold_results: Dict) -> None:
    """Create comprehensive visualizations"""
    print("\n[10/11] Creating Visualizations...")
    print("-" * 80)
    
    os.makedirs('outputs', exist_ok=True)
    
    # 1. Training history
    fig, axes = plt.subplots(2, 3, figsize=(20, 12))
    fig.suptitle('Training History', fontsize=16, y=0.995)
    
    metrics = ['loss', 'accuracy', 'precision', 'recall', 'auc', 'prc']
    titles = ['Loss', 'Accuracy', 'Precision', 'Recall', 'ROC-AUC', 'PR-AUC']
    
    for idx, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[idx // 3, idx % 3]
        ax.plot(history.history[metric], label='Train', linewidth=2)
        ax.plot(history.history[f'val_{metric}'], label='Validation', linewidth=2)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Epoch')
        ax.set_ylabel(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/training_history.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: training_history.png")
    
    # 2. Confusion matrix
    fig, ax = plt.subplots(figsize=(10, 8))
    cm = results['confusion_matrix']
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax,
                xticklabels=['Benign', 'Threat'],
                yticklabels=['Benign', 'Threat'])
    ax.set_title('Confusion Matrix', fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('True Label', fontsize=12)
    ax.set_xlabel('Predicted Label', fontsize=12)
    plt.tight_layout()
    plt.savefig('outputs/confusion_matrix.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: confusion_matrix.png")
    
    # 3. ROC and PR curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    fpr, tpr, _ = roc_curve(y_test, results['probabilities'])
    ax1.plot(fpr, tpr, linewidth=3, label=f'ROC (AUC = {results["auc"]:.4f})')
    ax1.plot([0, 1], [0, 1], 'k--', linewidth=2, label='Random')
    ax1.set_xlabel('False Positive Rate', fontsize=12)
    ax1.set_ylabel('True Positive Rate', fontsize=12)
    ax1.set_title('ROC Curve', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    
    precision, recall, _ = precision_recall_curve(y_test, results['probabilities'])
    ax2.plot(recall, precision, linewidth=3, label='PR Curve')
    ax2.axhline(y=y_test.mean(), color='k', linestyle='--', linewidth=2,
                label=f'Baseline ({y_test.mean():.4f})')
    ax2.set_xlabel('Recall', fontsize=12)
    ax2.set_ylabel('Precision', fontsize=12)
    ax2.set_title('Precision-Recall Curve', fontsize=14, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/roc_pr_curves.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: roc_pr_curves.png")
    
    # 4. Threshold analysis
    fig, ax = plt.subplots(figsize=(12, 6))
    thresholds_to_plot = [
        ('Recall 95%', threshold_results.get('recall_optimized', {}).get('threshold')),
        ('F1 Optimal', threshold_results.get('f1_optimized', {}).get('threshold')),
        ('Default (0.5)', 0.5)
    ]
    
    precisions, recalls, thresholds = precision_recall_curve(y_test, results['probabilities'])
    f1_scores = 2 * precisions * recalls / (precisions + recalls + 1e-10)
    
    ax.plot(thresholds, precisions[:-1], label='Precision', linewidth=2)
    ax.plot(thresholds, recalls[:-1], label='Recall', linewidth=2)
    ax.plot(thresholds, f1_scores[:-1], label='F1-Score', linewidth=2)
    
    for name, thresh in thresholds_to_plot:
        if thresh is not None:
            ax.axvline(thresh, linestyle='--', alpha=0.7, label=f'{name} ({thresh:.3f})')
    
    ax.set_xlabel('Threshold', fontsize=12)
    ax.set_ylabel('Score', fontsize=12)
    ax.set_title('Threshold vs Metrics', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/threshold_analysis.png', dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: threshold_analysis.png")


# ============================================================================
# SECTION 11: SAVE ARTIFACTS
# ============================================================================

def save_all_artifacts(model: Model,
                      preprocessor: AdvancedLogPreprocessor,
                      feature_engineer: AdvancedFeatureEngineer,
                      history: keras.callbacks.History,
                      results: Dict,
                      threshold_results: Dict,
                      config: Dict) -> None:
    """Save all model artifacts"""
    print("\n[11/11] Saving Model Artifacts...")
    print("-" * 80)
    
    os.makedirs('models', exist_ok=True)
    
    # Save model
    model.save('models/healthcare_threat_detector_production.keras')
    print("  Saved: healthcare_threat_detector_production.keras")
    
    # Save preprocessor
    with open('models/preprocessor.pkl', 'wb') as f:
        pickle.dump(preprocessor, f)
    print("  Saved: preprocessor.pkl")
    
    # Save feature engineer
    with open('models/feature_engineer.pkl', 'wb') as f:
        pickle.dump(feature_engineer, f)
    print("  Saved: feature_engineer.pkl")
    
    # Save training history
    history_df = pd.DataFrame(history.history)
    history_df.to_csv('outputs/training_history.csv', index=False)
    print("  Saved: training_history.csv")
    
    # Save metadata
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'config': config,
        'performance': {
            'accuracy': float(results['accuracy']),
            'precision': float(results['precision']),
            'recall': float(results['recall']),
            'f1': float(results['f1']),
            'auc': float(results['auc']),
            'threshold': float(results['threshold'])
        },
        'threshold_optimization': threshold_results,
        'model_parameters': model.count_params(),
        'gpu_used': str(tf.config.list_physical_devices('GPU'))
    }
    
    with open('models/model_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    print("  Saved: model_metadata.json")


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main(log_directory: str = None,
         log_pattern: str = "*.json",
         sequence_length: int = 50,
         lstm_units: int = 256,
         dropout_rate: float = 0.3,
         l2_reg: float = 0.001,
         learning_rate: float = 0.001,
         epochs: int = 100,
         batch_size: int = 256,
         target_recall: float = 0.95):
    """
    Main training pipeline for production LSTM
    
    Args:
        log_directory: Path to directory containing log files
        log_pattern: Glob pattern for log files (default: *.json)
        sequence_length: Length of event sequences
        lstm_units: Number of LSTM units
        dropout_rate: Dropout rate for regularization
        l2_reg: L2 regularization factor
        learning_rate: Initial learning rate
        epochs: Maximum training epochs
        batch_size: Training batch size
        target_recall: Target recall for threshold optimization
    """
    
    config = {
        'log_directory': log_directory,
        'log_pattern': log_pattern,
        'sequence_length': sequence_length,
        'lstm_units': lstm_units,
        'dropout_rate': dropout_rate,
        'l2_reg': l2_reg,
        'learning_rate': learning_rate,
        'epochs': epochs,
        'batch_size': batch_size,
        'target_recall': target_recall
    }
    
    print("\nCONFIGURATION")
    print("=" * 80)
    for key, value in config.items():
        print(f"{key:20s}: {value}")
    print("=" * 80)
    
    # Step 1: Configure GPU
    configure_gpu()
    
    # Step 2: Load logs
    if log_directory is None:
        raise ValueError("log_directory must be specified")
    
    loader = LogFileLoader()
    raw_df = loader.load_directory(log_directory, log_pattern)
    df = loader.normalize_log_format(raw_df)
    
    # Step 3: Feature engineering
    engineer = AdvancedFeatureEngineer()
    df = engineer.engineer_features(df)
    
    # Step 4: Split by users
    train_df, val_df, test_df = split_by_users(df)
    
    # Step 5: Preprocess
    preprocessor = AdvancedLogPreprocessor(sequence_length=sequence_length)
    X_train, y_train = preprocessor.fit_transform(train_df)
    X_val, y_val = preprocessor.transform(val_df)
    X_test, y_test = preprocessor.transform(test_df)
    
    print(f"\nFinal sequence shapes:")
    print(f"  Train: {X_train.shape}")
    print(f"  Val:   {X_val.shape}")
    print(f"  Test:  {X_test.shape}")
    
    # Step 6: Build model
    model = build_production_lstm_model(
        input_shape=(X_train.shape[1], X_train.shape[2]),
        lstm_units=lstm_units,
        dropout_rate=dropout_rate,
        l2_reg=l2_reg,
        learning_rate=learning_rate,
        use_multi_head_attention=True
    )
    
    model.summary()
    
    # Step 7: Train
    history = train_production_model(
        model, X_train, y_train, X_val, y_val,
        epochs=epochs,
        batch_size=batch_size
    )
    
    # Step 8: Optimize threshold
    y_val_proba = model.predict(X_val, batch_size=batch_size, verbose=0).flatten()
    threshold_results = find_optimal_threshold(y_val, y_val_proba, target_recall=target_recall)
    
    # Use recall-optimized threshold for evaluation
    optimal_threshold = threshold_results['recall_optimized']['threshold']
    
    # Step 9: Evaluate
    results = evaluate_production_model(
        model, X_test, y_test,
        threshold=optimal_threshold,
        batch_size=batch_size
    )
    
    # Step 10: Visualize
    create_visualizations(history, results, y_test, threshold_results)
    
    # Step 11: Save
    save_all_artifacts(model, preprocessor, engineer, history, results, threshold_results, config)
    
    print("\n" + "=" * 80)
    print(" " * 25 + "TRAINING COMPLETE!")
    print("=" * 80)
    print("\nFiles Created:")
    print("  Models:")
    print("    - models/healthcare_threat_detector_production.keras")
    print("    - models/preprocessor.pkl")
    print("    - models/feature_engineer.pkl")
    print("    - models/model_metadata.json")
    print("  Outputs:")
    print("    - outputs/training_history.csv")
    print("    - outputs/training_history.png")
    print("    - outputs/confusion_matrix.png")
    print("    - outputs/roc_pr_curves.png")
    print("    - outputs/threshold_analysis.png")
    
    print(f"\nBest Results (Threshold={optimal_threshold:.4f}):")
    print(f"  Accuracy:  {results['accuracy']*100:.2f}%")
    print(f"  Precision: {results['precision']*100:.2f}%")
    print(f"  Recall:    {results['recall']*100:.2f}%")
    print(f"  F1-Score:  {results['f1']*100:.2f}%")
    print(f"  ROC-AUC:   {results['auc']:.4f}")
    
    print("\n" + "=" * 80)
    print("Next Steps:")
    print("1. Review threshold_analysis.png to choose appropriate threshold")
    print("2. Deploy model with real-time monitoring")
    print("3. Monitor for model drift and retrain periodically")
    print("4. Consider ensemble with other models for better performance")
    print("=" * 80)
    print("\nTraining pipeline complete!\n")


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Train production LSTM for healthcare threat detection')
    parser.add_argument('--log-dir', type=str, required=True, help='Directory containing log files')
    parser.add_argument('--log-pattern', type=str, default='*.json', help='Log file pattern')
    parser.add_argument('--sequence-length', type=int, default=50, help='Sequence length')
    parser.add_argument('--lstm-units', type=int, default=256, help='LSTM units')
    parser.add_argument('--epochs', type=int, default=100, help='Training epochs')
    parser.add_argument('--batch-size', type=int, default=256, help='Batch size')
    parser.add_argument('--target-recall', type=float, default=0.95, help='Target recall for threshold')
    
    args = parser.parse_args()
    
    try:
        main(
            log_directory=args.log_dir,
            log_pattern=args.log_pattern,
            sequence_length=args.sequence_length,
            lstm_units=args.lstm_units,
            epochs=args.epochs,
            batch_size=args.batch_size,
            target_recall=args.target_recall
        )
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
    except Exception as e:
        print(f"\n\nError during training: {e}")
        import traceback
        traceback.print_exc()
