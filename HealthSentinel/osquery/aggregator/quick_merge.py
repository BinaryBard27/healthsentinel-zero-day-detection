"""Quick log merger - simplified version"""
import pandas as pd
import glob
import os

log_dir = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\preprocessed data\sql injection and log\log files"
output = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\Datasets\merged_all_logs.csv"

# Get structured log files
files = glob.glob(os.path.join(log_dir, "*structured*.csv"))
print(f"Found {len(files)} structured log files")

dfs = []
for f in files:
    print(f"Loading: {os.path.basename(f)}")
    df = pd.read_csv(f, on_bad_lines='skip')
    df['source'] = os.path.basename(f)
    dfs.append(df)
    print(f"  Rows: {len(df)}")

result = pd.concat(dfs, ignore_index=True)
result.to_csv(output, index=False)

print(f"\nMerged {len(dfs)} files")
print(f"Total rows: {len(result):,}")
print(f"Saved to: {output}")
