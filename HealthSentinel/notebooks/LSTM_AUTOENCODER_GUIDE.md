# LSTM Autoencoder for Insider Threat Detection - Quick Start Guide

## 🎯 What This Does

**Proper behavioral insider threat detection** using LSTM autoencoder:

✅ Trains **ONLY on normal behavior** (unsupervised)  
✅ Detects anomalies via **sequence reconstruction error**  
✅ **Per-user behavioral baselines** (context-aware)  
✅ **Temporal sequence modeling** (order matters)  
✅ **No synthetic labels** needed

---

## 📂 Files Created

### Training
- **`notebooks/train_lstm_autoencoder.py`** - Main training script
- **`src/behavioral_feature_aggregator.py`** - Feature engineering module

### Inference
- **`src/insider_threat_detector.py`** - Real-time detection module

---

## 🚀 Quick Start

### Step 1: Train the Model

```bash
cd C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel
python notebooks/train_lstm_autoencoder.py
```

**Training Data Path (hardcoded):**
```
C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs_complete.csv
```

**What it does:**
1. Loads 294 MB merged log file (~1.13M events)
2. Filters to ONLY normal behavior
3. Aggregates events into 5-minute time-step vectors
4. Creates sliding window sequences (30 time-steps each)
5. Trains LSTM autoencoder to reconstruct normal sequences
6. Computes per-user reconstruction error baselines
7. Saves model + baselines

**Output Directory:**
```
C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_autoencoder\
├── best_autoencoder.pt          # Model weights
├── user_baselines.json          # Per-user baselines
├── training_results.json        # Metrics & config
├── training_curve.png           # Loss curves
└── error_distribution.png       # Error histogram
```

**Expected Training Time:**
- **CPU:** ~40-60 minutes
- **GPU (T4):** ~15-20 minutes
- **GPU (V100):** ~8-12 minutes

---

### Step 2: Test Detection

```bash
python src/insider_threat_detector.py
```

This runs the demo that:
- Loads trained model
- Processes test sequences
- Detects behavioral anomalies
- Shows reconstruction errors

---

## 🔧 Configuration

Edit `CONFIG` in `train_lstm_autoencoder.py`:

```python
CONFIG = {
    # Adjust sample size for faster testing
    'sample_size': 100000,  # Use subset (or None for all data)
    
    # Time window for aggregation
    'window_minutes': 5,  # Events aggregated per 5-min window
    
    # Sequence parameters
    'sequence_length': 30,  # 30 time-steps = 2.5 hours of behavior
    'stride': 5,  # Overlap sequences
    
    # Model size
    'hidden_dim': 128,
    'latent_dim': 64,
    
    # Training
    'epochs': 50,
    'batch_size': 64,
}
```

---

## 📊 How Detection Works

### Architecture

```
Normal Behavior Sequence
         ↓
    LSTM Encoder
         ↓
   Latent Vector (compressed behavioral pattern)
         ↓
    LSTM Decoder
         ↓
Reconstructed Sequence
         ↓
Reconstruction Error = ||Original - Reconstructed||²
         ↓
If error > user's baseline threshold → ANOMALY
```

### Time-Step Features (12 per window)

Each 5-minute window is represented by:

```python
[
    login_hour_normalized,      # Time of day
    file_access_count,           # Activity level
    sensitive_file_flag,         # PHI/EHR access
    new_process_flag,            # New processes
    network_entropy,             # Network diversity
    privilege_level,             # Admin/sudo usage
    usb_event_flag,              # External device
    data_transfer_size_log,      # Data volume
    unique_files_accessed,       # File diversity
    command_diversity,           # Command variety
    afterhours_flag,             # Outside work hours
    weekend_flag,                # Weekend activity
]
```

### Per-User Baselines

```json
{
  "user_id": {
    "mean_error": 0.0023,
    "std_error": 0.0008,
    "p95_error": 0.0035,
    "p99_error": 0.0042
  }
}
```

**Anomaly threshold:** `mean + 2×std`

---

## 🎯 Real-Time Usage

```python
from src.insider_threat_detector import InsiderThreatDetector

# Initialize
detector = InsiderThreatDetector(
    model_path='models/insider_threat_autoencoder/best_autoencoder.pt',
    baselines_path='models/insider_threat_autoencoder/user_baselines.json',
    config_path='models/insider_threat_autoencoder/training_results.json'
)

# Detect on time-step vector
result = detector.detect(
    user_id='john_doe',
    time_step_vector=np.array([...]),  # 12 features
    threshold_multiplier=2.0
)

# Check result
if result['is_anomaly']:
    print(f"🚨 Insider threat detected!")
    print(f"   Risk score: {result['risk_score']:.2f}")
    print(f"   Reconstruction error: {result['reconstruction_error']:.6f}")
    print(f"   Threshold: {result['threshold']:.6f}")
```

---

## 🔍 What Makes This Different

### ❌ Old (Classification) Approach
- Supervised learning with fake labels
- Treats threat detection as classification
- No temporal modeling
- No per-user context

### ✅ New (Autoencoder) Approach
- **Unsupervised** (trains only on normal behavior)
- **Reconstruction error** indicates deviation
- **Temporal sequences** (behavior patterns over time)
- **Per-user baselines** (context-aware)
- **No labels needed** for training

---

## 📈 Expected Results

**Normal Behavior:**
- Low reconstruction error (< baseline)
- Model can reconstruct sequence accurately

**Anomalous Behavior:**
- High reconstruction error (> baseline)
- Model cannot reconstruct unusual patterns

**Example Anomalies Detected:**
- After-hours data access (unusual time)
- Sudden privilege escalation (unusual commands)
- Mass file access (unusual volume)
- External USB usage (unusual device)
- Lateral movement (unusual network connections)

---

## 🛠️ Troubleshooting

### Error: "Missing required columns"
Check that merged CSV has: `timestamp`, `user`, `action`

### Training too slow on CPU
Reduce `sample_size` or use GPU:
```python
CONFIG['sample_size'] = 50000  # Use subset
```

### Out of memory
Reduce batch size:
```python
CONFIG['batch_size'] = 32  # Lower batch size
```

---

## 📁 Integration with HealthSentinel

To integrate with main app:

1. **Training:** Run periodically (weekly) on new normal behavior
2. **Inference:** Call `detector.detect()` in real-time as events arrive
3. **Alerts:** Trigger alert when `is_anomaly == True` and `risk_score > 0.7`
4. **Baseline Updates:** Retrain baselines as users' normal behavior evolves

---

## ✅ Verification

After training, check:

1. **Training curve** - Loss should decrease smoothly
2. **Error distribution** - Should be right-skewed (most errors low)
3. **User baselines** - All users should have baselines computed
4. **Test detection** - Run `insider_threat_detector.py` demo

---

**Questions? Check `implementation_plan.md` for full architecture details.**
