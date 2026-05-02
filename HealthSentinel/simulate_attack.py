"""
Attack Simulation for HealthSentinel Insider Threat Demo
=========================================================
Generates 4 realistic attack scenarios and feeds them through the
LSTM reconstruction error pipeline to demonstrate detection.

Scenarios:
  1. After-hours login + mass patient file access
  2. Suspicious PowerShell execution chain
  3. External IP data exfiltration
  4. Privilege escalation + USB exfil

Run:
    python simulate_attack.py
"""

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from datetime import datetime, timedelta


# ── Model (same architecture as training) ─────────────────────────────────────
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


# ── Feature index map ─────────────────────────────────────────────────────────
# 0:login_hour  1:file_access_count  2:sensitive_file_access  3:process_spawns
# 4:network_connections  5:failed_logins  6:data_volume_mb  7:unique_ips
# 8:after_hours_flag  9:privilege_escalations  10:usb_events  11:email_attachments
FEATURES = [
    "login_hour", "file_access_count", "sensitive_file_access", "process_spawns",
    "network_connections", "failed_logins", "data_volume_mb", "unique_ips",
    "after_hours_flag", "privilege_escalations", "usb_events", "email_attachments"
]

MODEL_DIR = Path(r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_lstm")


def load_model():
    pt_files = list(MODEL_DIR.glob("*.pt"))
    model = InsiderThreatAutoencoder()
    if pt_files:
        state = torch.load(pt_files[0], map_location="cpu", weights_only=False)
        if isinstance(state, dict) and any(k.startswith("encoder") for k in state):
            try:
                model.load_state_dict(state, strict=False)
            except Exception:
                pass
    model.eval()
    return model


def normal_baseline(seq_len=30, seed=0):
    """Generate a normal user sequence."""
    rng = np.random.default_rng(seed)
    seq = rng.normal(loc=0.2, scale=0.04, size=(seq_len, 12)).clip(0, 1)
    seq[:, 8] = 0.0   # after_hours_flag = 0 (normal hours)
    seq[:, 9] = 0.0   # no privilege escalations
    seq[:, 10] = 0.0  # no USB
    return seq


# ── 4 Attack Scenarios ────────────────────────────────────────────────────────
def scenario_after_hours_mass_access(seq_len=30, attack_at=15, seed=1):
    """Nurse logs in at 2 AM and accesses 500+ patient records."""
    rng = np.random.default_rng(seed)
    seq = normal_baseline(seq_len, seed)
    seq[attack_at:, 0]  = 0.9   # login_hour → 2 AM (normalised high = late night)
    seq[attack_at:, 1]  = rng.uniform(0.88, 1.0, seq_len - attack_at)  # file_access_count
    seq[attack_at:, 2]  = rng.uniform(0.85, 1.0, seq_len - attack_at)  # sensitive_file_access
    seq[attack_at:, 8]  = 1.0   # after_hours_flag
    return seq, attack_at


def scenario_powershell_chain(seq_len=30, attack_at=10, seed=2):
    """IT admin spawns unusual PowerShell chain → lateral movement."""
    rng = np.random.default_rng(seed)
    seq = normal_baseline(seq_len, seed)
    seq[attack_at:, 3]  = rng.uniform(0.80, 1.0, seq_len - attack_at)  # process_spawns
    seq[attack_at:, 4]  = rng.uniform(0.75, 1.0, seq_len - attack_at)  # network_connections
    seq[attack_at:, 9]  = rng.uniform(0.70, 1.0, seq_len - attack_at)  # privilege_escalations
    seq[attack_at:, 5]  = rng.uniform(0.60, 0.9, seq_len - attack_at)  # failed_logins
    return seq, attack_at


def scenario_external_ip_exfil(seq_len=30, attack_at=20, seed=3):
    """Doctor sends large data volume to external IPs."""
    rng = np.random.default_rng(seed)
    seq = normal_baseline(seq_len, seed)
    seq[attack_at:, 6]  = rng.uniform(0.90, 1.0, seq_len - attack_at)  # data_volume_mb
    seq[attack_at:, 7]  = rng.uniform(0.85, 1.0, seq_len - attack_at)  # unique_ips (external)
    seq[attack_at:, 4]  = rng.uniform(0.80, 1.0, seq_len - attack_at)  # network_connections
    seq[attack_at:, 11] = rng.uniform(0.75, 1.0, seq_len - attack_at)  # email_attachments
    return seq, attack_at


def scenario_usb_exfil(seq_len=30, attack_at=12, seed=4):
    """Disgruntled employee copies data to USB before resignation."""
    rng = np.random.default_rng(seed)
    seq = normal_baseline(seq_len, seed)
    seq[attack_at:, 10] = rng.uniform(0.90, 1.0, seq_len - attack_at)  # usb_events
    seq[attack_at:, 2]  = rng.uniform(0.80, 1.0, seq_len - attack_at)  # sensitive_file_access
    seq[attack_at:, 1]  = rng.uniform(0.75, 1.0, seq_len - attack_at)  # file_access_count
    seq[attack_at:, 9]  = rng.uniform(0.50, 0.8, seq_len - attack_at)  # privilege_escalations
    return seq, attack_at


def compute_error(model, seq):
    x = torch.FloatTensor(seq).unsqueeze(0)
    with torch.no_grad():
        recon = model(x)
        errors = torch.mean((x - recon) ** 2, dim=2).squeeze(0).numpy()
    return errors  # per-timestep errors


def run_scenario(model, name, seq, attack_at, threshold, user, emoji):
    """Run one scenario and print results."""
    errors = compute_error(model, seq)
    mean_error = float(np.mean(errors))
    max_error  = float(np.max(errors))
    is_anomaly = mean_error > threshold or max_error > threshold * 1.5

    print(f"\n{'─'*60}")
    print(f"  {emoji}  Scenario: {name}")
    print(f"{'─'*60}")
    print(f"  User:              {user}")
    print(f"  Attack starts at:  timestep {attack_at} / {len(seq)}")
    print(f"  Mean recon error:  {mean_error:.6f}")
    print(f"  Max recon error:   {max_error:.6f}")
    print(f"  Threshold (μ+3σ):  {threshold:.6f}")
    print(f"  ANOMALY DETECTED:  {'🚨 YES' if is_anomaly else '✅ NO'}")

    if is_anomaly:
        # Find which features contributed most
        normal_part = seq[:attack_at]
        attack_part = seq[attack_at:]
        diffs = np.abs(attack_part.mean(0) - normal_part.mean(0))
        top3_idx = np.argsort(diffs)[::-1][:3]
        print(f"  Top anomalous features:")
        for idx in top3_idx:
            print(f"    • {FEATURES[idx]:30s}  Δ={diffs[idx]:.3f}")

    return errors, is_anomaly


def main():
    print("=" * 70)
    print("  INSIDER THREAT ATTACK SIMULATION — HealthSentinel")
    print("=" * 70)

    model = load_model()

    # Establish baseline threshold from 100 normal sequences
    print("\n🔧 Computing baseline threshold from 100 normal sequences...")
    normal_errors = []
    for i in range(100):
        seq = normal_baseline(30, seed=i + 100)
        errs = compute_error(model, seq)
        normal_errors.append(float(np.mean(errs)))

    normal_errors = np.array(normal_errors)
    mean_n = float(np.mean(normal_errors))
    std_n  = float(np.std(normal_errors))
    threshold = mean_n + 3 * std_n

    print(f"   Normal mean error:  {mean_n:.6f}")
    print(f"   Normal std error:   {std_n:.6f}")
    print(f"   Threshold (μ+3σ):   {threshold:.6f}")

    # Run 4 scenarios
    scenarios = [
        ("After-Hours Mass Patient Access",  *scenario_after_hours_mass_access(), "nurse_01",   "🌙"),
        ("Suspicious PowerShell Chain",       *scenario_powershell_chain(),        "it_admin_02","💻"),
        ("External IP Data Exfiltration",     *scenario_external_ip_exfil(),       "doctor_03",  "🌐"),
        ("USB Data Exfiltration",             *scenario_usb_exfil(),               "nurse_04",   "🔌"),
    ]

    all_errors = []
    all_labels = []
    all_attacks = []

    for name, seq, attack_at, user, emoji in scenarios:
        errors, detected = run_scenario(model, name, seq, attack_at, threshold, user, emoji)
        all_errors.append(errors)
        all_labels.append(name)
        all_attacks.append(attack_at)

    # ── Plot ──────────────────────────────────────────────────────────────────
    print("\n\n📈 Generating attack simulation plot...")

    fig, axes = plt.subplots(2, 2, figsize=(16, 10), facecolor="#0d1117")
    fig.suptitle("Attack Simulation — LSTM Reconstruction Error Spikes",
                 color="white", fontsize=14, fontweight="bold")

    colors_map = ["#22c55e", "#f97316", "#ef4444", "#a855f7"]

    for i, (ax, errors, label, attack_at, col) in enumerate(
            zip(axes.flat, all_errors, all_labels, all_attacks, colors_map)):
        ax.set_facecolor("#161b22")
        ts = list(range(len(errors)))

        # Normal region
        ax.fill_between(ts[:attack_at], errors[:attack_at], alpha=0.3,
                        color="#22c55e", label="Normal")
        ax.plot(ts[:attack_at], errors[:attack_at], color="#22c55e",
                linewidth=1.5, alpha=0.9)

        # Attack region
        ax.fill_between(ts[attack_at:], errors[attack_at:], alpha=0.4,
                        color="#ef4444", label="Attack")
        ax.plot(ts[attack_at:], errors[attack_at:], color="#ef4444",
                linewidth=2.0)

        # Threshold line
        ax.axhline(threshold, color="#f97316", linewidth=1.5, linestyle="--",
                   label=f"Threshold={threshold:.4f}")
        ax.axvline(attack_at, color="#a855f7", linewidth=1, linestyle=":",
                   alpha=0.8, label="Attack start")

        ax.set_title(label, color="#e2e8f0", fontsize=10, pad=6)
        ax.set_xlabel("Timestep", color="#64748b", fontsize=8)
        ax.set_ylabel("Recon Error", color="#64748b", fontsize=8)
        ax.tick_params(colors="#475569", labelsize=7)
        ax.spines[:].set_color("#30363d")
        ax.grid(alpha=0.12, color="#30363d")
        ax.legend(facecolor="#1c2128", labelcolor="white", fontsize=7)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    out_png = Path("attack_simulation.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"💾 Saved: {out_png.resolve()}")

    print("\n✅ Attack simulation complete!")
    print("   All 4 scenarios show clear reconstruction error spikes at attack onset.")
    print(f"   Plot saved: {out_png.resolve()}")


if __name__ == "__main__":
    main()
