# Training Time Estimation Guide

## Your Merged Dataset Location

**File Path:**
```
C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs.csv
```

**File Size:** ~4.9 MB (4,939,704 bytes)

**Created by:** `osquery/aggregator/merge_logs.py`
- Merges all structured log files from preprocessed data directory
- Combines multiple CSV files into single dataset

---

## Training Time Estimates

### Dataset Size Estimation
Based on your ~5 MB merged file:
- **Estimated rows:** ~30,000-50,000 log events (typical for 5MB CSV)
- **After sequence creation:** ~20,000-40,000 sequences (with sequence_length=50)

### Training Time by Hardware

#### 1. Google Colab T4 GPU (FREE)
```
Dataset: ~40,000 sequences
Epochs: 100 (with early stopping ~30-50 epochs typically)

Total Time: 15-25 minutes
  - Data loading: 1-2 minutes
  - Feature engineering: 2-3 minutes
  - Model training: 10-15 minutes
  - Evaluation: 1-2 minutes
```

#### 2. Google Colab A100 GPU (Colab Pro)
```
Dataset: ~40,000 sequences
Epochs: 100

Total Time: 8-12 minutes
  - Data loading: 1 minute
  - Feature engineering: 1-2 minutes
  - Model training: 5-7 minutes
  - Evaluation: 1 minute
```

#### 3. CPU Only (Local Machine)
```
Dataset: ~40,000 sequences
Epochs: 100

Total Time: 2-4 hours
  - Data loading: 2-3 minutes
  - Feature engineering: 5-10 minutes
  - Model training: 1.5-3.5 hours (SLOW!)
  - Evaluation: 5-10 minutes
```

#### 4. Local GPU (RTX 3060/3070)
```
Dataset: ~40,000 sequences
Epochs: 100

Total Time: 20-35 minutes
  - Similar to Colab T4
```

---

## Factors Affecting Training Time

### 1. Dataset Size
```
10,000 sequences   → ~5-10 min (T4 GPU)
50,000 sequences   → ~15-25 min (T4 GPU)
100,000 sequences  → ~30-45 min (T4 GPU)
500,000 sequences  → ~2-3 hours (T4 GPU)
```

### 2. Sequence Length
```
sequence_length=30  → Faster (~20% less time)
sequence_length=50  → Baseline
sequence_length=100 → Slower (~40% more time)
```

### 3. Model Size
```
lstm_units=128   → ~30% faster
lstm_units=256   → Baseline (recommended)
lstm_units=512   → ~50% slower
```

### 4. Batch Size
```
batch_size=128   → Slower but more stable
batch_size=256   → Balanced (recommended)
batch_size=512   → Faster on good GPU
```

### 5. Early Stopping
```
Without early stopping: Full 100 epochs
With early stopping:    Typically 30-50 epochs (saves 50%+ time)
```

---

## Recommendations for Your Dataset

### Quick Training (Testing)
```python
main_with_upload(
    sequence_length=30,
    lstm_units=128,
    epochs=50,
    batch_size=256,
    target_recall=0.90
)
# Time: ~8-12 minutes on T4 GPU
```

### Balanced Training (Recommended)
```python
main_with_upload(
    sequence_length=50,
    lstm_units=256,
    epochs=100,
    batch_size=256,
    target_recall=0.95
)
# Time: ~15-25 minutes on T4 GPU
```

### Best Performance (Longer)
```python
main_with_upload(
    sequence_length=100,
    lstm_units=512,
    epochs=150,
    batch_size=128,
    target_recall=0.95
)
# Time: ~45-60 minutes on T4 GPU
```

---

## Expected Timeline for Your ~5MB Dataset

### On Google Colab (T4 GPU) - RECOMMENDED

```
[0/11] Upload dataset          → 30 seconds
[1/11] Configure GPU            → 5 seconds
[2/11] Load log files           → 1 minute
[3/11] Feature engineering      → 2-3 minutes
[4/11] Split by users           → 10 seconds
[5/11] Preprocessing            → 1-2 minutes
[6/11] Build model              → 10 seconds
[7/11] Training (100 epochs)    → 10-15 minutes
[8/11] Threshold optimization   → 30 seconds
[9/11] Evaluation               → 30 seconds
[10/11] Visualization           → 1 minute
[11/11] Save artifacts          → 30 seconds

TOTAL: 18-25 minutes
```

---

## How to Monitor Progress

### 1. Real-time Progress Bar
The training will show:
```
Epoch 1/100
45/157 [=====>........................] - ETA: 2:15 - loss: 0.3421
```

### 2. Validation Metrics
After each epoch:
```
Epoch 00015: val_auc improved from 0.9234 to 0.9267
```

### 3. Early Stopping
```
Epoch 00043: early stopping
```
(Saves time if model stops improving)

---

## Tips to Speed Up Training

1. **Use Google Colab GPU** (Free)
   - 10-20x faster than CPU
   - Enable: Runtime → Change runtime type → GPU

2. **Enable Early Stopping** (Already included)
   - Stops when model stops improving
   - Saves 30-50% time

3. **Reduce Epochs for Testing**
   ```python
   epochs=20  # Quick test run
   ```

4. **Smaller Batch Size if OOM**
   ```python
   batch_size=128  # If you get "Out of Memory" errors
   ```

5. **Cache Preprocessed Data** (For multiple runs)
   ```python
   # Save preprocessed sequences
   np.save('X_train.npy', X_train)
   np.save('y_train.npy', y_train)
   ```

---

## Memory Requirements

### Your Dataset (~5MB, ~40K sequences)
```
RAM Required:
  - CPU training:  ~4-8 GB
  - GPU training:  ~2-4 GB GPU VRAM + 4 GB RAM

Colab Free Tier:  12.7 GB RAM, 15 GB GPU VRAM ✓ SUFFICIENT
```

### Larger Datasets
```
100K sequences  → 8 GB GPU VRAM (use Colab Pro)
500K sequences  → 16+ GB GPU VRAM (use Colab Pro+ or local A100)
```

---

## Starting Your Training

### Step 1: Upload to Google Colab
```
1. Go to colab.google.com
2. Upload train_lstm_colab_upload.py
3. Runtime → Change runtime type → T4 GPU
4. Run the script
```

### Step 2: Upload Your Dataset
```
When prompted, upload:
  merged_all_logs.csv
  
Or create a zip file for faster upload:
  zip healthcare_logs.zip merged_all_logs.csv
```

### Step 3: Wait for Training
```
Expected time: ~20 minutes
Grab a coffee ☕
```

### Step 4: Download Results
```
Auto-downloads:
  - healthcare_threat_detector.keras
  - preprocessor.pkl
  - feature_engineer.pkl
  - model_metadata.json
```
