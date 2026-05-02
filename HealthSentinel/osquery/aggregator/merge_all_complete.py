"""
Comprehensive Log Merger - Includes ALL Log Files
Merges structured logs + large network traffic files
"""
import pandas as pd
import glob
import os
from datetime import datetime

print("=" * 80)
print("COMPREHENSIVE LOG FILE MERGER")
print("=" * 80)

log_dir = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\preprocessed data\sql injection and log\log files"
output = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs_complete.csv"

print(f"\nSource: {log_dir}")
print(f"Output: {output}\n")
print("=" * 80)

# Find ALL CSV files
all_csv_files = glob.glob(os.path.join(log_dir, "*.csv"))
print(f"\nFound {len(all_csv_files)} CSV files total\n")

# Filter for data files (exclude template files)
data_files = [f for f in all_csv_files if 'template' not in f.lower()]
print(f"Data files (excluding templates): {len(data_files)}\n")
print("-" * 80)

# Process files
dfs = []
total_size = 0

for idx, file_path in enumerate(data_files, 1):
    filename = os.path.basename(file_path)
    file_size_mb = os.path.getsize(file_path) / (1024**2)
    total_size += file_size_mb
    
    print(f"[{idx}/{len(data_files)}] {filename}")
    print(f"     Size: {file_size_mb:.1f} MB")
    
    try:
        # Read with chunk processing for large files
        if file_size_mb > 50:
            print(f"     Reading in chunks (large file)...")
            chunks = []
            for chunk in pd.read_csv(file_path, on_bad_lines='skip', 
                                    low_memory=False, chunksize=50000):
                chunks.append(chunk)
            df = pd.concat(chunks, ignore_index=True)
        else:
            df = pd.read_csv(file_path, on_bad_lines='skip', low_memory=False)
        
        # Add metadata
        df['source_file'] = filename
        df['log_category'] = 'network_traffic' if 'pcap' in filename.lower() else 'system_log'
        
        dfs.append(df)
        print(f"     Loaded: {len(df):,} rows\n")
        
    except Exception as e:
        print(f"     ERROR: {e}\n")
        continue

print("=" * 80)
print("Merging all dataframes...")

if dfs:
    result = pd.concat(dfs, ignore_index=True, sort=False)
    
    print(f"Saving to {output}...")
    result.to_csv(output, index=False)
    
    # Final statistics
    output_size_mb = os.path.getsize(output) / (1024**2)
    
    print("\n" + "=" * 80)
    print("MERGE COMPLETE!")
    print("=" * 80)
    print(f"Files merged:          {len(dfs)}")
    print(f"Total rows:            {len(result):,}")
    print(f"Total columns:         {len(result.columns)}")
    print(f"Input size:            {total_size:.1f} MB")
    print(f"Output file size:      {output_size_mb:.1f} MB")
    print(f"Memory usage:          {result.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    print("\nFile breakdown:")
    if 'source_file' in result.columns:
        for source, count in result['source_file'].value_counts().items():
            print(f"  {source:50s} {count:>10,} rows")
    
    print("\nCategory breakdown:")
    if 'log_category' in result.columns:
        print(result['log_category'].value_counts())
    
    print("\n" + "=" * 80)
    print("Dataset ready for LSTM training!")
    print("=" * 80)
else:
    print("ERROR: No files merged!")
