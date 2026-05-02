# Production LSTM Training - Usage Guide

## Overview
The production LSTM model (`train_lstm_production.py`) is designed to work with real log file datasets, addressing critical issues in the original code.

## Key Improvements

### 1. Real Log File Support
- Loads osquery JSON logs or CSV files
- Automatic format normalization
- Handles multiple log files from a directory

### 2. Prevents Data Leakage
- **User-based splitting** ensures same user's data doesn't appear in train/test
- Critical for realistic performance evaluation

### 3. Advanced Features
- Behavioral baseline per user
- Anomaly detection with Isolation Forest
- Rolling window statistics
- Deviation from normal behavior patterns

### 4. Better Architecture
- Multi-head attention mechanism
- Residual connections
- Layer normalization
- Bidirectional LSTM layers

### 5. Threshold Optimization
- Finds optimal threshold for target recall (default 95%)
- Healthcare prioritizes catching threats over false positives
- Provides multiple threshold options

## Usage

### Basic Usage

```bash
python train_lstm_production.py --log-dir /path/to/logs
```

### Full Options

```bash
python train_lstm_production.py \
  --log-dir /path/to/healthcare/logs \
  --log-pattern "*.json" \
  --sequence-length 50 \
  --lstm-units 256 \
  --epochs 100 \
  --batch-size 256 \
  --target-recall 0.95
```

### From Python Script

```python
from train_lstm_production import main

main(
    log_directory='C:/path/to/logs',
    log_pattern='*.json',
    sequence_length=50,
    lstm_units=256,
    epochs=100,
    batch_size=256,
    target_recall=0.95
)
```

## Log File Format

### Required Fields
Your log files must contain these fields (or similar):
- `user` / `username` / `uid` - User identifier
- `action` / `event_type` / `event` - Action performed
- `resource` / `target` / `object` - Accessed resource
- `timestamp` / `time` / `datetime` - Event timestamp
- `source_ip` / `ip_address` - Source IP

### Optional Fields
- `access_type` / `operation` - Type of access (read/write/delete)
- `bytes_transferred` / `size` - Data volume
- `session_duration` / `duration` - Session length
- `label` / `is_threat` / `anomaly` - Ground truth labels (if available)

### Example Log Entry (JSON)

```json
{
  "username": "physician_001",
  "event_type": "patient_chart_view",
  "target": "EHR_PatientRecords",
  "timestamp": "2024-02-10T14:23:45Z",
  "source_ip": "10.1.45.22",
  "operation": "read",
  "bytes": 45632,
  "duration": 120,
  "is_threat": 0
}
```

### Example Log Entry (CSV)

```csv
user,action,resource,timestamp,source_ip,access_type,bytes_transferred,label
physician_001,patient_chart_view,EHR_PatientRecords,2024-02-10T14:23:45Z,10.1.45.22,read,45632,0
nurse_023,lab_results_access,Laboratory_System,2024-02-10T14:25:12Z,10.1.50.18,read,12400,0
```

## Output Files

### Models Directory
- `healthcare_threat_detector_production.keras` - Trained model
- `preprocessor.pkl` - Feature preprocessor (required for inference)
- `feature_engineer.pkl` - Feature engineering pipeline
- `model_metadata.json` - Training metadata and performance

### Outputs Directory
- `training_history.csv` - Training metrics per epoch
- `training_history.png` - Training curves visualization
- `confusion_matrix.png` - Test set confusion matrix
- `roc_pr_curves.png` - ROC and Precision-Recall curves
- `threshold_analysis.png` - Threshold vs metrics plot

## Real-Time Inference Example

```python
import pickle
import numpy as np
import pandas as pd
from tensorflow import keras

# Load artifacts
model = keras.models.load_model('models/healthcare_threat_detector_production.keras')
with open('models/preprocessor.pkl', 'rb') as f:
    preprocessor = pickle.load(f)
with open('models/feature_engineer.pkl', 'rb') as f:
    feature_engineer = pickle.load(f)

# Load new logs
new_logs = pd.read_csv('new_logs.csv')

# Engineer features
new_logs = feature_engineer.engineer_features(new_logs)

# Preprocess
X_new, _ = preprocessor.transform(new_logs)

# Predict
predictions = model.predict(X_new)

# Use optimized threshold (from model_metadata.json)
threshold = 0.3524  # Example from threshold optimization
threats = predictions >= threshold

# Get threat indices
threat_sequences = np.where(threats)[0]
print(f"Detected {len(threat_sequences)} potential threats")
```

## Integration with osquery

### 1. Configure osquery to output JSON

Edit `/etc/osquery/osquery.conf`:

```json
{
  "options": {
    "logger_path": "/var/log/osquery",
    "logger_plugin": "filesystem"
  },
  "packs": {
    "healthcare_monitoring": "/path/to/healthcare_pack.conf"
  }
}
```

### 2. Create Healthcare Pack

`healthcare_pack.conf`:

```json
{
  "queries": {
    "user_logins": {
      "query": "SELECT username, time, host FROM last WHERE time > (strftime('%s', 'now') - 3600);",
      "interval": 300,
      "description": "User login events"
    },
    "file_access": {
      "query": "SELECT uid, path, action, time FROM file_events WHERE path LIKE '%patient%';",
      "interval": 60,
      "description": "Patient file access"
    }
  }
}
```

### 3. Parse osquery Results

```python
import json
from train_lstm_production import LogFileLoader

loader = LogFileLoader()
df = loader.load_directory('/var/log/osquery', pattern='osqueryd.results.log*')
```

## Performance Tuning

### For Limited Memory (< 16GB RAM)
```bash
python train_lstm_production.py \
  --log-dir /path/to/logs \
  --batch-size 128 \
  --lstm-units 128 \
  --sequence-length 30
```

### For High Performance (GPU + 32GB+ RAM)
```bash
python train_lstm_production.py \
  --log-dir /path/to/logs \
  --batch-size 512 \
  --lstm-units 512 \
  --sequence-length 100
```

### For Quick Testing
```bash
python train_lstm_production.py \
  --log-dir /path/to/logs \
  --epochs 10 \
  --batch-size 128
```

## Labeling Unlabeled Data

If your logs don't have labels, you can:

### 1. Use Rule-Based Labeling
```python
def label_threats(df):
    df['label'] = 0
    
    # After-hours PHI access
    df.loc[(df['is_afterhours'] == 1) & (df['is_phi'] == 1), 'label'] = 1
    
    # Bulk exports
    df.loc[df['action'].str.contains('export|bulk', case=False), 'label'] = 1
    
    # USB/External
    df.loc[df['resource'].str.contains('usb|external', case=False), 'label'] = 1
    
    return df
```

### 2. Use Unsupervised Methods First
```python
from sklearn.ensemble import IsolationForest

iso = IsolationForest(contamination=0.05)
df['label'] = (iso.fit_predict(features) == -1).astype(int)
```

### 3. Manual Review + Active Learning
- Train initial model with rule-based labels
- Review model predictions
- Correct labels for high-confidence predictions
- Retrain with corrected labels

## Troubleshooting

### "No files found"
- Check log directory path is correct
- Verify log pattern matches your files
- Ensure files are readable

### "Required column not found"
- Review log format normalization in `normalize_log_format()`
- Add your column names to the mapping dictionaries

### Out of Memory
- Reduce `--batch-size`
- Reduce `--sequence-length`
- Reduce `--lstm-units`
- Process logs in smaller batches

### Low Performance
- Check if labels are correct
- Increase `--sequence-length` for better context
- Try different `--target-recall` values
- Add more domain-specific features

## Next Steps

1. **Monitor Performance**: Track precision/recall over time
2. **Retrain Regularly**: Update model with new labeled data
3. **Ensemble Models**: Combine with XGBoost/Random Forest
4. **Add Explainability**: Use SHAP values to explain predictions
5. **Deploy**: Integrate with SIEM or monitoring dashboard
