"""
SHAP Explainability for Insider Threat Detection
=================================================
Uses SHAP (SHapley Additive exPlanations) to explain WHY a user was flagged.

For each flagged sequence:
  - Shows top 3 contributing features
  - Shows percentage contribution
  - Saves a bar chart: shap_explanation.png

Healthcare requirement: "Why was this user flagged?"
This answers it with statistical rigour.

Run:
    pip install shap  (if not installed)
    python explain_threat.py
"""

import numpy as np
import pandas as pd
import sys
import subprocess
from pathlib import Path

# Auto-install shap if missing
try:
    import shap
except ImportError:
    print("📦 Installing shap...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "shap", "-q"])
    import shap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# ── Feature definitions ───────────────────────────────────────────────────────
FEATURES = [
    "login_hour", "file_access_count", "sensitive_file_access", "process_spawns",
    "network_connections", "failed_logins", "data_volume_mb", "unique_ips",
    "after_hours_flag", "privilege_escalations", "usb_events", "email_attachments"
]

FEATURE_DESCRIPTIONS = {
    "login_hour":              "Login time (after-hours = suspicious)",
    "file_access_count":       "Total files accessed per window",
    "sensitive_file_access":   "PHI / sensitive file accesses",
    "process_spawns":          "New processes spawned",
    "network_connections":     "Outbound network connections",
    "failed_logins":           "Failed authentication attempts",
    "data_volume_mb":          "Data transferred (MB)",
    "unique_ips":              "Unique IP addresses contacted",
    "after_hours_flag":        "Activity outside business hours",
    "privilege_escalations":   "Privilege escalation events",
    "usb_events":              "USB device insertion events",
    "email_attachments":       "Email attachments sent",
}


def generate_training_data(n_normal=500, n_attack=50, seed=42):
    """Generate normal + attack feature vectors for Isolation Forest training."""
    rng = np.random.default_rng(seed)

    # Normal behaviour
    normal = rng.normal(loc=0.2, scale=0.05, size=(n_normal, 12)).clip(0, 1)
    normal[:, 8] = 0.0   # after_hours_flag
    normal[:, 9] = 0.0   # privilege_escalations
    normal[:, 10] = 0.0  # usb_events

    # Attack behaviour – inject anomalies
    attack = rng.normal(loc=0.2, scale=0.05, size=(n_attack, 12)).clip(0, 1)
    attack[:, 1]  = rng.uniform(0.80, 1.0, n_attack)  # file_access_count
    attack[:, 2]  = rng.uniform(0.75, 1.0, n_attack)  # sensitive_file_access
    attack[:, 8]  = 1.0                                 # after_hours_flag
    attack[:, 10] = rng.uniform(0.70, 1.0, n_attack)  # usb_events
    attack[:, 9]  = rng.uniform(0.60, 1.0, n_attack)  # privilege_escalations

    X = np.vstack([normal, attack])
    y = np.array([0] * n_normal + [1] * n_attack)
    return X, y


def build_attack_sample(seed=99):
    """Build a single suspicious user feature vector to explain."""
    rng = np.random.default_rng(seed)
    sample = rng.normal(loc=0.2, scale=0.04, size=(1, 12)).clip(0, 1)
    # Inject attack pattern
    sample[0, 1]  = 0.92   # file_access_count
    sample[0, 2]  = 0.88   # sensitive_file_access
    sample[0, 8]  = 1.00   # after_hours_flag
    sample[0, 10] = 0.85   # usb_events
    sample[0, 9]  = 0.75   # privilege_escalations
    return sample


def main():
    print("=" * 70)
    print("  SHAP EXPLAINABILITY — HealthSentinel Insider Threat")
    print("=" * 70)

    # 1. Generate data
    print("\n🔧 Generating training data...")
    X, y = generate_training_data()
    print(f"   Training samples: {len(X)} ({np.sum(y==0)} normal, {np.sum(y==1)} attack)")

    # 2. Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 3. Train Isolation Forest
    print("\n🌲 Training Isolation Forest...")
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination=0.09,   # ~9% attack rate
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_scaled)

    # Evaluate
    preds = iso_forest.predict(X_scaled)   # -1 = anomaly, 1 = normal
    flagged = np.sum(preds == -1)
    print(f"   Flagged as anomalous: {flagged} / {len(X)}")

    # 4. Build suspicious sample
    print("\n🔍 Building suspicious user sample (nurse_01 after-hours)...")
    attack_sample = build_attack_sample()
    attack_scaled = scaler.transform(attack_sample)

    iso_score = iso_forest.score_samples(attack_scaled)[0]
    iso_pred  = iso_forest.predict(attack_scaled)[0]
    print(f"   Isolation Forest score: {iso_score:.4f}  (more negative = more anomalous)")
    print(f"   Prediction:             {'🚨 ANOMALY' if iso_pred == -1 else '✅ NORMAL'}")

    # 5. SHAP explanation
    print("\n🧠 Computing SHAP values...")
    # Use TreeExplainer for Isolation Forest
    explainer = shap.TreeExplainer(iso_forest)

    # SHAP values for the attack sample
    shap_values = explainer.shap_values(attack_scaled)

    # shap_values shape: (1, n_features) — take absolute values for importance
    sv = np.abs(shap_values[0])
    total = sv.sum() + 1e-10
    pct   = (sv / total) * 100

    # Sort by importance
    order = np.argsort(sv)[::-1]

    print("\n📋 SHAP Feature Importances for Flagged User:")
    print(f"{'─'*65}")
    print(f"  {'Feature':<30} {'SHAP |value|':>12}  {'Contribution':>12}")
    print(f"{'─'*65}")
    for idx in order:
        bar = "█" * int(pct[idx] / 2)
        print(f"  {FEATURES[idx]:<30} {sv[idx]:>12.4f}  {pct[idx]:>10.1f}%  {bar}")
    print(f"{'─'*65}")

    top3 = order[:3]
    print(f"\n🏆 Top 3 Reasons User Was Flagged:")
    for rank, idx in enumerate(top3, 1):
        print(f"  {rank}. {FEATURES[idx]:30s}  ({pct[idx]:.1f}%)  — {FEATURE_DESCRIPTIONS[FEATURES[idx]]}")

    # 6. Plot
    print("\n📊 Generating SHAP explanation chart...")

    fig, axes = plt.subplots(1, 2, figsize=(16, 7), facecolor="#0d1117")
    fig.suptitle("SHAP Explainability — Why Was This User Flagged?",
                 color="white", fontsize=14, fontweight="bold")

    # ── Left: SHAP bar chart ──
    ax1 = axes[0]
    ax1.set_facecolor("#161b22")

    feat_labels = [FEATURES[i] for i in order]
    shap_vals   = [sv[i] for i in order]
    bar_colors  = ["#ef4444" if i < 3 else "#60a5fa" for i in range(len(order))]

    bars = ax1.barh(feat_labels[::-1], shap_vals[::-1], color=bar_colors[::-1],
                    edgecolor="#30363d", height=0.6)
    ax1.set_xlabel("SHAP |value| (contribution to anomaly score)", color="#94a3b8")
    ax1.set_title("Feature Contributions (SHAP)", color="#e2e8f0", pad=8)
    ax1.tick_params(colors="#64748b", labelsize=9)
    ax1.spines[:].set_color("#30363d")
    ax1.grid(alpha=0.12, axis="x", color="#30363d")

    # Annotate top 3
    for i, (bar, val) in enumerate(zip(bars[::-1][:3], shap_vals[:3])):
        ax1.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
                 f"  {pct[order[i]]:.1f}%", va="center", color="#fbbf24", fontsize=9)

    # ── Right: Pie chart of top contributions ──
    ax2 = axes[1]
    ax2.set_facecolor("#161b22")

    top_n = 5
    top_labels = [FEATURES[i] for i in order[:top_n]]
    top_vals   = [pct[i] for i in order[:top_n]]
    other_pct  = 100 - sum(top_vals)
    if other_pct > 0:
        top_labels.append("Other features")
        top_vals.append(other_pct)

    pie_colors = ["#ef4444", "#f97316", "#f59e0b", "#a855f7", "#3b82f6", "#64748b"]
    wedges, texts, autotexts = ax2.pie(
        top_vals, labels=top_labels, autopct="%1.1f%%",
        colors=pie_colors[:len(top_vals)],
        startangle=140, pctdistance=0.75,
        textprops={"color": "white", "fontsize": 9}
    )
    for at in autotexts:
        at.set_color("#fbbf24")
        at.set_fontsize(9)

    ax2.set_title("Contribution Breakdown (Top 5 Features)", color="#e2e8f0", pad=8)

    # Annotation box
    fig.text(0.5, 0.02,
             f"User: nurse_01  |  IF Score: {iso_score:.4f}  |  "
             f"Top reason: {FEATURES[top3[0]]} ({pct[top3[0]]:.1f}%)",
             ha="center", color="#94a3b8", fontsize=10,
             bbox=dict(facecolor="#1c2128", edgecolor="#30363d", boxstyle="round,pad=0.4"))

    plt.tight_layout(rect=[0, 0.06, 1, 0.95])
    out_png = Path("shap_explanation.png")
    plt.savefig(out_png, dpi=150, bbox_inches="tight", facecolor="#0d1117")
    print(f"💾 Saved: {out_png.resolve()}")

    # 7. Save explanation to CSV
    explanation_df = pd.DataFrame({
        "feature":      [FEATURES[i] for i in order],
        "description":  [FEATURE_DESCRIPTIONS[FEATURES[i]] for i in order],
        "shap_value":   [round(sv[i], 6) for i in order],
        "contribution_pct": [round(pct[i], 2) for i in order],
    })
    out_csv = Path("shap_explanation.csv")
    explanation_df.to_csv(out_csv, index=False)
    print(f"💾 Saved: {out_csv.resolve()}")

    print("\n✅ SHAP explainability complete!")
    print(f"   Top reason flagged: {FEATURES[top3[0]]} ({pct[top3[0]]:.1f}%)")
    print(f"   Chart: {out_png.resolve()}")
    print(f"   CSV:   {out_csv.resolve()}")
    print("\n   This answers: 'Why was this user flagged?' with statistical rigour.")


if __name__ == "__main__":
    main()
