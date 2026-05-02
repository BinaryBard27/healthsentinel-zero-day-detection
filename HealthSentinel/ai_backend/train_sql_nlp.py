"""
Train SQL Injection NLP Pipeline
==================================
TF-IDF (character n-grams) + XGBoost -- lightweight, fast, CPU-optimized.

CRITICAL DESIGN DECISION:
  Unlike standard NLP (phishing), we PRESERVE ALL PUNCTUATION.
  SQL injection weaponizes symbols:  '  =  --  ;  *  (  )  UNION  SELECT
  The vectorizer uses analyzer='char_wb' with ngram_range=(2,5) so that
  character patterns like "' OR", "=1--", "/*" are captured as features.

Usage:
    python train_sql_nlp.py

Output:
    sql_nlp_pipeline.pkl  (saved in the same directory as this script)
"""

import pandas as pd
import numpy as np
import pickle
import os
import sys
import gc
from functools import partial
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from xgboost import XGBClassifier

print = partial(print, flush=True)

# ============================================================================
# CONFIGURATION
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Dataset paths (cleaned_data has the full merged dataset)
DATA_DIR = PROJECT_ROOT / "Datasets" / "preprocessed data" / "sql injection and log" / "cleaned_data"
TRAIN_CSV = DATA_DIR / "sql_injection_train.csv"
VAL_CSV   = DATA_DIR / "sql_injection_val.csv"
TEST_CSV  = DATA_DIR / "sql_injection_test.csv"

# If cleaned_data split files don't exist, fall back to sql-injection-datasets
ALT_DATA_DIR = PROJECT_ROOT / "Datasets" / "preprocessed data" / "sql injection and log" / "sql-injection-datasets"

OUTPUT_PATH = SCRIPT_DIR / "sql_nlp_pipeline.pkl"
CHUNK_SIZE  = 10_000  # rows per chunk for memory-efficient loading

# ============================================================================
# DATA LOADING  (chunked for low-RAM environments)
# ============================================================================

def load_dataset_chunked(csv_path: Path, max_rows: int = None) -> tuple:
    """Load CSV in chunks, return (texts, labels) arrays."""
    print(f"  Loading: {csv_path.name} ({csv_path.stat().st_size / 1e6:.1f} MB) - Cap: {max_rows}")

    texts_0, texts_1 = [], []
    target_per_class = (max_rows // 2) if max_rows else float('inf')
    chunk_count = 0

    for chunk in pd.read_csv(csv_path, chunksize=CHUNK_SIZE, encoding='utf-8',
                              on_bad_lines='skip'):
        # Normalize column names (handle 'query'/'Query', 'label'/'Label')
        chunk.columns = [c.strip().lower() for c in chunk.columns]

        if 'query' not in chunk.columns or 'label' not in chunk.columns:
            print(f"    [WARN] Unexpected columns: {list(chunk.columns)}")
            continue

        # Drop rows with missing text or label
        chunk = chunk.dropna(subset=['query', 'label'])

        # -- DO NOT strip punctuation -- this is the critical difference.
        # Only lowercase and collapse whitespace.
        chunk['query'] = chunk['query'].astype(str).str.lower().str.strip()
        chunk['query'] = chunk['query'].str.replace(r'\s+', ' ', regex=True)

        for _, row in chunk.iterrows():
            label = int(row['label'])
            if label == 0 and len(texts_0) < target_per_class:
                texts_0.append(row['query'])
            elif label == 1 and len(texts_1) < target_per_class:
                texts_1.append(row['query'])
            
            if len(texts_0) >= target_per_class and len(texts_1) >= target_per_class:
                break

        chunk_count += 1
        if len(texts_0) >= target_per_class and len(texts_1) >= target_per_class:
            break

    texts = texts_0 + texts_1
    labels = [0]*len(texts_0) + [1]*len(texts_1)
    
    # Shuffle
    combined = list(zip(texts, labels))
    np.random.seed(42)
    np.random.shuffle(combined)
    texts, labels = zip(*combined)

    print(f"    [OK] Loaded {len(texts):,} rows in {chunk_count} chunks (Class 0: {len(texts_0)}, Class 1: {len(texts_1)})")
    return list(texts), np.array(labels)


def resolve_paths():
    """Pick whichever dataset directory actually has the files."""
    if TRAIN_CSV.exists():
        return TRAIN_CSV, VAL_CSV, TEST_CSV
    # Fallback
    alt_train = ALT_DATA_DIR / "sql_injection_train.csv"
    alt_val   = ALT_DATA_DIR / "sql_injection_val.csv"
    alt_test  = ALT_DATA_DIR / "sql_injection_test.csv"
    if alt_train.exists():
        print("  [INFO] Using sql-injection-datasets/ fallback directory")
        return alt_train, alt_val, alt_test
    print("[FATAL] No SQL injection dataset found!")
    sys.exit(1)

# ============================================================================
# MAIN TRAINING PIPELINE
# ============================================================================

def main():
    print("=" * 70)
    print("  SQL Injection NLP Pipeline -- TF-IDF (char_wb) + XGBoost")
    print("=" * 70)

    # 1. Resolve dataset paths
    train_path, val_path, test_path = resolve_paths()

    # 2. Load data
    print("\n[Phase 1] Loading datasets...")
    X_train_raw, y_train = load_dataset_chunked(train_path, max_rows=15000)
    X_val_raw,   y_val   = load_dataset_chunked(val_path, max_rows=3000)
    X_test_raw,  y_test  = load_dataset_chunked(test_path, max_rows=3000)

    print(f"\n  Train: {len(X_train_raw):,}  |  Val: {len(X_val_raw):,}  |  Test: {len(X_test_raw):,}")
    print(f"  Train class balance:  0={np.sum(y_train==0):,}  1={np.sum(y_train==1):,}")

    # 3. Vectorize with character n-grams (PRESERVE PUNCTUATION)
    print("\n[Phase 2] Fitting TF-IDF vectorizer (char_wb, ngram 2-5)...")
    gc.collect()
    vectorizer = TfidfVectorizer(
        analyzer='char_wb',         # character n-grams at word boundaries
        ngram_range=(2, 5),         # capture  '  OR   --   ;   etc.
        max_features=60_000,        # keep model lean
        sublinear_tf=True,          # dampens high-frequency n-grams
        min_df=2,                   # ignore singleton noise
        strip_accents=None,         # DO NOT strip anything
        lowercase=False,            # already lowered during loading
    )

    X_train = vectorizer.fit_transform(X_train_raw)
    X_val   = vectorizer.transform(X_val_raw)
    X_test  = vectorizer.transform(X_test_raw)

    feature_names = vectorizer.get_feature_names_out()
    print(f"  [OK] Vocabulary size: {len(feature_names):,} character n-grams")

    # 4. Train XGBoost
    print("\n[Phase 3] Training XGBClassifier (tree_method='hist')...")
    model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        tree_method='hist',         # fast CPU histogram method
        eval_metric='logloss',
        early_stopping_rounds=15,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=25,
    )

    # 5. Evaluate
    print("\n[Phase 4] Evaluation...")
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n  Test Accuracy: {accuracy:.4f}  ({accuracy*100:.2f}%)\n")
    print(classification_report(y_test, y_pred, target_names=['Safe (0)', 'Injection (1)']))

    # 6. Save pipeline
    print(f"\n[Phase 5] Saving pipeline to {OUTPUT_PATH}...")
    pipeline = {
        'vectorizer': vectorizer,
        'model': model,
        'feature_names': feature_names,
        'accuracy': accuracy,
        'type': 'sql_injection_nlp',
        'analyzer': 'char_wb',
        'ngram_range': '(2, 5)',
    }

    with open(OUTPUT_PATH, 'wb') as f:
        pickle.dump(pipeline, f)

    file_size_mb = OUTPUT_PATH.stat().st_size / 1e6
    print(f"  [OK] Saved: {OUTPUT_PATH.name}  ({file_size_mb:.1f} MB)")
    print("\n" + "=" * 70)
    print("  DONE.  The CodeBERT model (498 MB) has been replaced by a")
    print(f"  {file_size_mb:.1f} MB TF-IDF + XGBoost pipeline.")
    print("=" * 70)


if __name__ == "__main__":
    main()
