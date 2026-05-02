# HealthSentinel | Healthcare AI Security Platform
## Project Summary & Final Documentation

### 🚀 Overview
HealthSentinel is a multi-layered, AI-driven security ecosystem designed for modern healthcare environments. It protects Electronic Health Records (EHR), Medical Devices (IoMT), and hospital networks from insider threats, zero-day attacks, and data exfiltration.

### 🛠️ Architecture
- **Detection Layer**: OSQuery + BiLSTM (Insider Threat) + 1D-CNN (Network Zero-Day).
- **Prevention Layer**: Zero Trust Zone Controller (PDP) enforcing micro-segmentation.
- **Privacy Layer**: HIPAA-compliant Data Masking & RBAC.
- **Deception Layer**: Multi-service Honeypots (Web, SQL, FTP).
- **Visibility Layer**: Real-time WebSocket Dashboard.

### 📂 Key Components
- [Aggregator](file:///c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/osquery/aggregator/log_aggregator.py): Central heart of the system.
- [Zero Trust](file:///c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/zerotrust/zone_controller.py): Access control engine.
- [Dashboard](file:///c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/web-dashboard/v2_dash.html): Visual security center.
- [Attack Suite](file:///c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/attacks/master_attack_sim.py): Automated validation scripts.

### 🧪 Verification
Run the following to see the AI in action:
1. Start Aggregator: `python HealthSentinel/osquery/aggregator/log_aggregator.py`
2. Run Attack Sim: `python HealthSentinel/attacks/master_attack_sim.py`
3. View Dashboard: Open `v2_dash.html` in browser.

---
*Status: 95% Complete (Deferred: Federated Learning)*
