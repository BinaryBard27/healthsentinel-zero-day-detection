"""
Comprehensive Log File Merger
Merges all structured log files for LSTM training
"""
import pandas as pd
import glob
import os
from datetime import datetime

print("=" * 80)
print("LOG FILE MERGER - Healthcare Insider Threat Detection")
print("=" * 80)

# Directories
log_dir = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\preprocessed data\sql injection and log\log files"
output_file = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs.csv"

print(f"\nSource directory: {log_dir}")
print(f"Output file: {output_file}")
print("\n" + "=" * 80)

# Find all structured CSV files (these are the parsed log files, not templates)
print("\nSearching for structured log files...")
files = glob.glob(os.path.join(log_dir, "*structured*.csv"))

# Also include the network traffic CSV files
network_files = [
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX_reduced.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX_cleaned.csv",
    "Monday-WorkingHours.pcap_ISCX_cleaned_20250910_011850.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX_cleaned.csv"
]

for nf in network_files:
    full_path = os.path.join(log_dir, nf)
    if os.path.exists(full_path):
        files.append(full_path)

print(f"Found {len(files)} files to merge\n")
print("-" * 80)

# Load and merge files
dfs = []
total_rows = 0

for idx, file_path in enumerate(files, 1):
    filename = os.path.basename(file_path)
    print(f"[{idx}/{len(files)}] Processing: {filename}")
    
    try:
        # Read CSV with error handling
        df = pd.read_csv(file_path, on_bad_lines='skip', low_memory=False)
        
        # Add metadata columns
        df['source_file'] = filename
        df['log_type'] = filename.split('_')[0]  # Extract log type
        
        # Add timestamp if not present
        if 'timestamp' not in df.columns and 'Timestamp' not in df.columns:
            # Generate sequential timestamps for logs without them
            base_time = pd.Timestamp.now()
            df['timestamp'] = [base_time + pd.Timedelta(seconds=i) for i in range(len(df))]
        
        dfs.append(df)
        total_rows += len(df)
        print(f"    -> Loaded {len(df):,} rows")
        
    except Exception as e:
        print(f"    -> ERROR: {e}")
        continue

print("-" * 80)

# Merge all dataframes
if dfs:
    print("\nMerging all dataframes...")
    result = pd.concat(dfs, ignore_index=True, sort=False)
    
    # Save to CSV
    print(f"Saving to: {output_file}")
    result.to_csv(output_file, index=False)
    
    # Statistics
    print("\n" + "=" * 80)
    print("MERGE COMPLETE!")
    print("=" * 80)
    print(f"Total files merged:     {len(dfs)}")
    print(f"Total rows:             {len(result):,}")
    print(f"Total columns:          {len(result.columns)}")
    print(f"File size:              {os.path.getsize(output_file) / 1024**2:.2f} MB")
    print(f"Memory usage:           {result.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    
    print("\nColumn names:")
    for col in result.columns[:20]:  # Show first 20 columns
        print(f"  - {col}")
    if len(result.columns) > 20:
        print(f"  ... and {len(result.columns) - 20} more columns")
    
    print("\nData types:")
    print(result.dtypes.value_counts())
    
    print("\nFirst few rows:")
    print(result.head(3))
    
    print("\n" + "=" * 80)
    print("Dataset ready for LSTM training!")
    print("=" * 80)
    
else:
    print("\nERROR: No data could be merged!")
