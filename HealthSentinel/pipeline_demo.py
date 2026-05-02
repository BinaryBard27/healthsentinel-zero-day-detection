"""
Reconstruction Error Pipeline Demo
====================================
Loads the trained LSTM autoencoder, runs sequences through it,
computes reconstruction error per sequence, and visualizes results.

Outputs:
  - reconstruction_errors.csv  (sequence_id | timestamp | user | reconstruction_error)
  - reconstruction_error_plot.png

Run:
    python pipeline_demo.py
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # headless – no display needed
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from datetime import datetime, timedelta
import sys, os

# ── Model architecture (must match training) ──────────────────────────────────
class InsiderThreatAutoencoder(nn.Module):
    def __init__(self, input_dim=12, hidden_dim=64, latent_dim=32,
                 num_layers=2, dropout=0.2):
        super().__init__()
        self.encoder_lstm = nn.LSTM(input_dim, hidden_dim, num_layers,
                                    batch_first=True,
                                    dropout=dropout if num_layers > 1 else 0)
        self.encoder_fc   = nn.Sequential(nn.Linear(hidden_dim, latent_dim), nn.Tanh())
        self.decoder_fc   = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(hidden_dim, hidden_dim, num_layers,
                                    batch_first=True,
                                    dropout=dropout if num_layers > 1 else 0)
        self.output_fc    = nn.Linear(hidden_dim, input_dim)

    def forward(self, x):
        seq_len = x.size(1)
        _, (h, _) = self.encoder_lstm(x)
        latent = self.encoder_fc(h[-1])
        dec_in = self.decoder_fc(latent).unsqueeze(1).repeat(1, seq_len, 1)
        out, _ = self.decoder_lstm(dec_in)
        return self.output_fc(out)


# ── Helpers ───────────────────────────────────────────────────────────────────
FEATURE_NAMES = [
    "login_hour", "file_access_count", "sensitive_file_access",
    "process_spawns", "network_connections", "failed_logins",
    "data_volume_mb", "unique_ips", "after_hours_flag",
    "privilege_escalations", "usb_events", "email_attachments"
]

MODEL_DIR = Path(r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_lstm")


def load_model(device="cpu"):
    """Load LSTM autoencoder from state dict."""
    pt_files = list(MODEL_DIR.glob("*.pt"))
    if not pt_files:
        print("⚠️  No .pt file found – using randomly initialised model for demo.")
        model = InsiderThreatAutoencoder()
        model.eval()
        return model, False

    pt_path = pt_files[0]
    print(f"📂 Loading model from: {pt_path.name}")
    state = torch.load(pt_path, map_location=device, weights_only=False)

    # state dict may be wrapped in a dict
    if isinstance(state, dict) and "model_state_dict" in state:
        state = state["model_state_dict"]
    elif isinstance(state, dict) and not any(k.startswith("encoder") for k in state):
        # plain checkpoint dict without model weights – use random model
        print("⚠️  Checkpoint is a config/results dict, not weights – using random model.")
        model = InsiderThreatAutoencoder()
        model.eval()
        return model, False

    model = InsiderThreatAutoencoder()
    try:
        model.load_state_dict(state, strict=False)
        print("✅ Model weights loaded.")
        loaded = True
    except Exception as e:
        print(f"⚠️  Could not load weights ({e}) – using random model.")
        loaded = False

    model.eval()
    return model, loaded


def generate_sequences(n_normal=80, n_attack=20, seq_len=30, n_features=12,
                        seed=42):
    """Generate synthetic normal + attack sequences with timestamps."""
    rng = np.random.default_rng(seed)
    base_time = datetime(2026, 2, 18, 8, 0, 0)

    records = []

    # Normal sequences – low, consistent activity
    for i in range(n_normal):
        seq = rng.normal(loc=0.2, scale=0.05, size=(seq_len, n_features)).clip(0, 1)
        ts  = base_time + timedelta(minutes=i * 5)
        records.append({"seq_id": i, "timestamp": ts, "user": "nurse_01",
                         "label": "normal", "sequence": seq})

    # Attack sequences – spikes in sensitive features
    for i in range(n_attack):
        seq = rng.normal(loc=0.2, scale=0.05, size=(seq_len, n_features)).clip(0, 1)
        # Inject attack pattern: massive file access + after-hours + USB
        attack_start = rng.integers(10, seq_len - 5)
        seq[attack_start:, 1]  = rng.uniform(0.85, 1.0, seq_len - attack_start)  # file_access_count
        seq[attack_start:, 2]  = rng.uniform(0.80, 1.0, seq_len - attack_start)  # sensitive_file_access
        seq[attack_start:, 8]  = 1.0                                               # after_hours_flag
        seq[attack_start:, 10] = rng.uniform(0.70, 1.0, seq_len - attack_start)  # usb_events
        ts = base_time + timedelta(minutes=(n_normal + i) * 5)
        records.append({"seq_id": n_normal + i, "timestamp": ts, "user": "nurse_01",
                         "label": "attack", "sequence": seq})

    return records


def compute_reconstruction_errors(model, records, device="cpu"):
    """Pass sequences through model and compute per-sequence MSE."""
    errors = []
    with torch.no_grad():
        for rec in records:
            x = torch.FloatTensor(rec["sequence"]).unsqueeze(0).to(device)
            recon = model(x)
            mse = float(torch.mean((x - recon) ** 2).item())
            errors.append(mse)
    return np.array(errors)


def compute_threshold(errors_normal):
    """Statistical threshold: mean + 3 * std on normal sequences."""
    mean = np.mean(errors_normal)
    std  = np.std(errors_normal)
    threshold = mean + 3 * std
    return threshold, mean, std


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 70)
    print("  RECONSTRUCTION ERROR PIPELINE DEMO")
    print("=" * 70)

    device = "cpu"
    model, weights_loaded = load_model(device)

    # Generate sequences
    print("\n🔧 Generating synthetic sequences (80 normal + 20 attack)...")
    records = generate_sequences(n_normal=80, n_attack=20)

    # Compute errors
    print("⚙️  Computing reconstruction errors...")
    errors = compute_reconstruction_errors(model, records, device)

    # Threshold from normal sequences only
    normal_errors = errors[:80]
    threshold, mean_err, std_err = compute_threshold(normal_errors)

    print(f"\n📊 Threshold Analysis:")
    print(f"   Normal mean error : {mean_err:.6f}")
    print(f"   Normal std error  : {std_err:.6f}")
    print(f"   Threshold (μ+3σ)  : {threshold:.6f}   ← statistically justified")

    # Build output dataframe
    rows = []
    for i, (rec, err) in enumerate(zip(records, errors)):
        rows.append({
            "sequence_id":         rec["seq_id"],
            "timestamp":           rec["timestamp"].strftime("%Y-%m-%d %H:%M:%S"),
            "user":                rec["user"],
            "label":               rec["label"],
            "reconstruction_error": round(err, 8),
            "threshold":           round(threshold, 8),
            "is_anomaly":          err > threshold,
        })

    df = pd.DataFrame(rows)
    out_csv = Path("reconstruction_errors.csv")
    df.to_csv(out_csv, index=False)
    print(f"\n💾 Saved: {out_csv.resolve()}")

    # Print table preview
    print("\n📋 Sample Output (sequence_id | timestamp | user | reconstruction_error):")
    print("-" * 80)
    preview = df[["sequence_id", "timestamp", "user", "reconstruction_error", "is_anomaly"]].head(10)
    print(preview.to_string(index=False))
    print(f"  ... ({len(df)} total rows)")

    anomaly_count = df["is_anomaly"].sum()
    print(f"\n🚨 Anomalies detected: {anomaly_count} / {len(df)}")

    # ── Plot ──────────────────────────────────────────────────────────────────
    print("\n📈 Generating reconstruction error plot...")

    fig, axes = plt.subplots(2, 1, figsize=(14, 9), facecolor="#0d1117")
    fig.suptitle("LSTM Reconstruction Error Pipeline — HealthSentinel",
                 color="white", fontsize=14, fontweight="bold", y=0.98)

    timestamps = list(range(len(df)))
    colors = ["#ef4444" if a else "#22c55e" for a in df["is_anomaly"]]

    # ── Top: error over time ──
    ax1 = axes[0]
    ax1.set_facecolor("#161b22")
    ax1.plot(timestamps, df["reconstruction_error"], color="#60a5fa",
             linewidth=1.5, alpha=0.8, label="Reconstruction Error", zorder=2)
    ax1.axhline(threshold, color="#f97316", linewidth=1.5, linestyle="--",
                label=f"Threshold μ+3σ = {threshold:.5f}", zorder=3)
    ax1.fill_between(timestamps, df["reconstruction_error"], threshold,
                     where=df["reconstruction_error"] > threshold,
                     color="#ef4444", alpha=0.3, label="Anomaly Region")
    ax1.axvline(80, color="#a855f7", linewidth=1, linestyle=":", alpha=0.7,
                label="Attack starts →")
    ax1.set_ylabel("Reconstruction Error (MSE)", color="#94a3b8")
    ax1.set_xlabel("Sequence Index", color="#94a3b8")
    ax1.set_title("Reconstruction Error Over Time", color="#e2e8f0", pad=8)
    ax1.tick_params(colors="#64748b")
    ax1.spines[:].set_color("#30363d")
    ax1.legend(facecolor="#1c2128", labelcolor="white", fontsize=9)
    ax1.grid(alpha=0.15, color="#30363d")

    # ── Bottom: scatter coloured by anomaly ──
    ax2 = axes[1]
    ax2.set_facecolor("#161b22")
    ax2.scatter(timestamps, df["reconstruction_error"], c=colors, s=25,
                alpha=0.8, zorder=3)
    ax2.axhline(threshold, color="#f97316", linewidth=1.5, linestyle="--",
                label=f"Threshold = {threshold:.5f}")
    ax2.set_ylabel("Reconstruction Error", color="#94a3b8")
    ax2.set_xlabel("Sequence Index", color="#94a3b8")
    ax2.set_title("Anomaly Scatter (🟢 Normal  🔴 Anomaly)", color="#e2e8f0", pad=8)
    ax2.tick_params(colors="#64748b")
    ax2.spines[:].set_color("#30363d")
    ax2.legend(facecolor="#1c2128", labelcolor="white", fontsize=9)
    ax2.grid(alpha=0.15, color="#30363d")

    # Patch legend
    normal_patch = mpatches.Patch(color="#22c55e", label="Normal")
    attack_patch = mpatches.Patch(color="#ef4444", label="Anomaly")
    ax2.legend(handles=[normal_patch, attack_patch],
               facecolor="#1c2128", labelcolor="white", fontsize=9)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    out_png = Path("reconstruction_error_plot.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"💾 Saved: {out_png.resolve()}")

    print("\n✅ Pipeline demo complete!")
    print(f"   Model weights loaded: {weights_loaded}")
    print(f"   Threshold (μ+3σ):     {threshold:.6f}")
    print(f"   Anomalies detected:   {anomaly_count}")
    print(f"   Output CSV:           {out_csv.resolve()}")
    print(f"   Output plot:          {out_png.resolve()}")


if __name__ == "__main__":
    main()
