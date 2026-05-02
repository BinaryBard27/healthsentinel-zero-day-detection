import { useState } from "react";

// ─── COMPLETE DATA ────────────────────────────────────────────────────────────

const checklistItems = [
  { id: "insider", label: "Insider Threat (OSQuery + LSTM)", done: false },
  { id: "zeroday", label: "Zero-Day Threats (GAN + 1D-CNN)", done: false },
  { id: "honeypot", label: "Honeypots (3 Decoys)", done: false },
  { id: "zerotrust", label: "Zero Trust Architecture", done: false },
  { id: "thirdparty", label: "Third-Party Software Protection", done: false },
  { id: "ehr", label: "EHR / Electronic Health Records", done: false },
  { id: "iomeddevice", label: "Electronic Medical Devices (IoMed)", done: false },
  { id: "patientdata", label: "Patient Data Protection", done: false },
  { id: "colab", label: "Google Colab Training Pipeline", done: false },
  { id: "dashboard", label: "Unified Dashboard v2", done: false },
];

const SECTIONS = {
  // ═══════════════════════════════════════════════════════════════════════════
  // 1. INSIDER THREAT
  // ═══════════════════════════════════════════════════════════════════════════
  insider: {
    title: "INSIDER THREAT DETECTION",
    subtitle: "OSQuery + LSTM Deep Dive",
    color: "#f59e0b",
    icon: "👤",
    blocks: [
      {
        heading: "What is the Threat?",
        content: `An insider threat is when someone ALREADY INSIDE the organization causes damage — a nurse downloading thousands of patient records onto a USB, an admin selling credentials, or a compromised employee account being used to exfiltrate data. Traditional firewalls cannot stop this because the person is already authenticated and trusted. This is why we need BEHAVIORAL analysis — watching HOW people act over time, not just IF they are allowed in.`
      },
      {
        heading: "Step 1 — OSQuery Agent Setup",
        content: `OSQuery is an open-source tool by Facebook that turns every operating system into a queryable database. You install a lightweight agent on every machine in the hospital network.

WHAT IT COLLECTS (every 60 seconds):
• User login events — who logged in, when, from which IP
• File access events — which files were opened, read, copied, deleted
• USB device events — any USB plugged in or out
• Network connections — which external IPs the machine talked to
• Process execution — what programs were launched and by whom
• Registry/config changes — any system settings modified

WHERE IT RUNS:
• Doctor workstations (Windows)
• Nurse stations (Linux)
• Admin servers
• EHR application servers
• File servers

HOW DATA FLOWS OUT:
OSQuery → JSON log files → Central Log Aggregator (a simple Flask/FastAPI server that receives and stores logs) → Training data for LSTM`
      },
      {
        heading: "Step 2 — Data Preprocessing for LSTM",
        content: `Raw OSQuery logs are messy. The LSTM needs clean, structured sequences.

PREPROCESSING PIPELINE:
1. PARSE: Convert raw JSON logs into structured rows (user_id, timestamp, event_type, resource_accessed, source_ip, destination_ip)
2. ENCODE: Convert categorical fields into numbers:
   • event_type → one-hot vector: [login, logout, file_read, file_write, file_copy, usb_in, usb_out, net_connect, process_exec]
   • resource → embed using a learned embedding layer (maps each resource ID to a 32-dim vector)
3. WINDOW: Group events by user into time windows of 1 hour. Each window = one input sequence to the LSTM.
   Example: User_42, Hour_14 → [login, file_read×3, net_connect×2, file_copy×1] → vector sequence of shape (T, D) where T = number of events in the window, D = feature dimension
4. LABEL: For training, we create synthetic labels:
   • Normal behavior: random realistic patterns
   • Suspicious: mass file access + USB copy + off-hours login + access to patient records outside the user's department
   • Malicious: bulk export + external network upload + credential changes`
      },
      {
        heading: "Step 3 — LSTM Model Architecture",
        content: `WHY LSTM?
LSTMs (Long Short-Term Memory) are designed exactly for this: they learn patterns in SEQUENCES over time. A single login at 3 AM is normal. But login at 3 AM + access 500 records + copy to USB + connect to external IP — that SEQUENCE is the threat. LSTM learns these sequential patterns.

ARCHITECTURE (layer by layer):
1. INPUT LAYER
   Shape: (batch_size, sequence_length=60, feature_dim=64)
   — 60 events max per user per hour window
   — 64 features per event (after encoding)

2. EMBEDDING LAYER
   Maps discrete event types and resource IDs into dense vectors.
   Output shape: (batch, 60, 128)

3. BiLSTM LAYER 1
   Bidirectional — reads the sequence forward AND backward.
   Units: 128 per direction → 256 total
   Returns full sequence output (not just last hidden state)
   Dropout: 0.3

4. BiLSTM LAYER 2
   Units: 64 per direction → 128 total
   Returns full sequence output
   Dropout: 0.3

5. ATTENTION LAYER
   Learns which events in the sequence matter most.
   Produces a weighted sum → single vector of size 128
   (This is critical — not all events are equally suspicious)

6. DENSE LAYER
   128 → 64 → 32 (with ReLU activation, dropout 0.2 between each)

7. OUTPUT LAYER
   32 → 1 (Sigmoid activation)
   Output = probability of insider threat (0.0 to 1.0)

LOSS FUNCTION: Binary Cross Entropy
OPTIMIZER: Adam (lr=0.001)
THRESHOLD: If output > 0.7 → flag as insider threat`
      },
      {
        heading: "Step 4 — Training on Google Colab",
        content: `NOTEBOOK: insider_threat_lstm.ipynb

STEP-BY-STEP IN COLAB:
1. Mount Google Drive (to save/load data and model checkpoints)
2. Upload preprocessed dataset (JSON sequences)
3. Import libraries: torch, torch.nn, pandas, numpy, sklearn
4. Define Dataset class (custom PyTorch Dataset that loads sequences)
5. Define model class (the BiLSTM + Attention architecture above)
6. Training loop:
   • Epochs: 50
   • Batch size: 64
   • Early stopping: if validation loss doesn't improve for 5 epochs, stop
   • Save best model checkpoint every epoch
7. Evaluation:
   • Accuracy, Precision, Recall, F1-Score, AUC-ROC
   • Confusion matrix
8. Save final model as insider_threat_lstm.pt`
      },
      {
        heading: "Step 5 — Runtime Detection",
        content: `AFTER TRAINING, the model runs LIVE:

FLOW:
1. OSQuery agent on endpoint sends new event log (every 60s)
2. Central aggregator receives log, adds to the current user's event buffer
3. Every 5 minutes, the buffer is preprocessed into a sequence
4. Sequence is fed into the LSTM model
5. Model outputs a risk score (0.0 – 1.0)
6. If score > 0.7:
   • Alert is sent to the dashboard
   • Zero Trust engine is notified → token revocation triggered
   • The event is logged in the audit trail
7. If score < 0.3: nothing happens, behavior is normal
8. Scores between 0.3–0.7: logged as "watch list" — monitored more frequently`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 2. ZERO-DAY THREATS
  // ═══════════════════════════════════════════════════════════════════════════
  zeroday: {
    title: "ZERO-DAY THREAT DETECTION",
    subtitle: "GAN + 1D-CNN Pipeline",
    color: "#ef4444",
    icon: "⚡",
    blocks: [
      {
        heading: "What is a Zero-Day Threat?",
        content: `A zero-day attack exploits a vulnerability that NOBODY knows about yet — no patch exists, no signature exists, no antivirus can catch it. Traditional security works by matching known attack signatures. Zero-day attacks have NO known signature. 

THIS IS WHY WE USE A GAN: We train a GAN to INVENT new attack signatures that look like real attacks but are novel. Then we train a classifier on BOTH real attacks AND these synthetic novel attacks. The classifier learns the PATTERNS of what attacks look like, not just memorizing specific signatures. This gives it the ability to detect attacks it has never seen before.`
      },
      {
        heading: "Step 1 — Network Traffic Dataset",
        content: `We need a dataset of network traffic — both normal and attack traffic.

DATA SOURCES:
• Use the CICIDS-2017 or CICIDS-2018 dataset (publicly available, contains real attack traffic captures)
• Supplement with traffic captured from your own simulated hospital network

FEATURES EXTRACTED PER PACKET/FLOW (these become the input vectors):
• Source IP, Destination IP (encoded)
• Source Port, Destination Port
• Protocol (TCP/UDP/ICMP → one-hot)
• Packet length (min, max, mean, std)
• Flow duration
• Number of packets sent/received
• Bytes per second
• TCP flags (SYN, ACK, FIN, RST counts)
• Inter-arrival time between packets
• Number of unique destination IPs contacted

FINAL FEATURE VECTOR PER FLOW: 42-dimensional vector
SEQUENCE: Group flows into windows of 100 flows → shape (100, 42) per sample`
      },
      {
        heading: "Step 2 — GAN Architecture (Attack Generator)",
        content: `THE GAN has two networks fighting each other:

GENERATOR (creates fake attack traffic):
  Input: Random noise vector (100-dim)
  → Dense(256) → LeakyReLU → BatchNorm
  → Dense(512) → LeakyReLU → BatchNorm
  → Dense(1024) → LeakyReLU → BatchNorm
  → Reshape to (100, 42) — a fake traffic sequence
  → Conv1DTranspose layers to add temporal realism
  Output: A synthetic network traffic sequence that looks like an attack

DISCRIMINATOR (judges if traffic is real or fake):
  Input: Traffic sequence (100, 42)
  → Conv1D(64, kernel=3) → LeakyReLU → BatchNorm
  → Conv1D(128, kernel=3) → LeakyReLU → BatchNorm
  → Conv1D(256, kernel=3) → LeakyReLU → BatchNorm
  → GlobalAveragePooling
  → Dense(128) → LeakyReLU
  → Dense(1) → Sigmoid
  Output: Probability that input is REAL traffic (not fake)

TRAINING:
• Generator tries to FOOL the discriminator
• Discriminator tries to CORRECTLY identify fakes
• They fight each other until Generator produces traffic so realistic the Discriminator cannot tell the difference
• Loss: Wasserstein Loss (more stable than standard GAN loss)
• Train for 200 epochs on Colab GPU`
      },
      {
        heading: "Step 3 — Generate Synthetic Zero-Day Attacks",
        content: `AFTER GAN IS TRAINED:

1. Feed 10,000 random noise vectors into the trained Generator
2. Each output = one synthetic attack traffic sequence
3. These sequences look like real attacks but are NOVEL — patterns the classifier has never seen
4. This is your synthetic zero-day dataset

WHY THIS WORKS:
The Generator learned the STRUCTURE of attacks (timing patterns, port behaviors, packet sizes) from real attack data. But because it's generative, it produces NEW variations — like a music composer who learned jazz and now improvises new solos. Each generated sequence is a plausible attack the world has never seen.`
      },
      {
        heading: "Step 4 — 1D-CNN Zero-Day Classifier",
        content: `NOW we train a classifier on COMBINED data:
• Real normal traffic (labeled: 0)
• Real known attacks (labeled: 1)  
• GAN-generated synthetic attacks (labeled: 1)

ARCHITECTURE:
  Input: (100, 42) — traffic sequence

  → Conv1D(64, kernel=3, padding=same) → ReLU → BatchNorm
  → Conv1D(64, kernel=3, padding=same) → ReLU → BatchNorm
  → MaxPool1D(2) → shape becomes (50, 64)

  → Conv1D(128, kernel=3, padding=same) → ReLU → BatchNorm
  → Conv1D(128, kernel=3, padding=same) → ReLU → BatchNorm
  → MaxPool1D(2) → shape becomes (25, 128)

  → Conv1D(256, kernel=3, padding=same) → ReLU → BatchNorm
  → GlobalAveragePooling → shape becomes (256,)

  → Dense(128) → ReLU → Dropout(0.4)
  → Dense(64) → ReLU → Dropout(0.3)
  → Dense(1) → Sigmoid

  Output: Probability of being an attack (0.0 – 1.0)

TRAINING:
• Epochs: 80
• Batch size: 128  
• Optimizer: Adam (lr=0.001)
• Loss: Binary Cross Entropy
• Threshold: > 0.6 → flag as potential zero-day`
      },
      {
        heading: "Step 5 — Runtime Zero-Day Detection",
        content: `LIVE DETECTION FLOW:
1. All incoming network traffic passes through the API Gateway
2. Traffic is captured and grouped into 100-flow windows
3. Each window is fed into the 1D-CNN classifier
4. If score > 0.6 → ZERO-DAY ALERT
5. Alert includes: source IP, destination, timestamp, confidence score, top suspicious features
6. Threat aggregation engine cross-references with honeypot logs
7. If honeypot also flagged activity from same source → confidence boosted to CRITICAL
8. Zero Trust engine blocks the source automatically`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 3. HONEYPOTS
  // ═══════════════════════════════════════════════════════════════════════════
  honeypot: {
    title: "HONEYPOT DEPLOYMENT",
    subtitle: "3 Decoy Systems Inside the Network",
    color: "#22c55e",
    icon: "🍯",
    blocks: [
      {
        heading: "What Are Honeypots?",
        content: `A honeypot is a FAKE system designed to look real but has NO legitimate traffic. If ANYONE touches it, that's an immediate red flag — because no real user or real system should ever interact with it. Think of it as a trap: we place fake valuables in a room, and if anyone tries to steal them, we know they're a thief.

In our healthcare network, we deploy 3 honeypots that mimic systems attackers would TARGET:`
      },
      {
        heading: "Honeypot 1 — Fake EHR Database Server",
        content: `WHAT IT LOOKS LIKE:
• A PostgreSQL server running on a realistic port (5432)
• It has fake patient records (dummy names, fake SSNs, fake medical histories)
• It responds to legitimate-looking SQL queries
• Its hostname looks like a real EHR server (e.g., "ehr-db-prod-03.hospital.internal")

WHAT IT ACTUALLY DOES:
• Logs EVERY connection attempt, query, and authentication attempt
• Never actually serves data to anyone — it just records who tried
• Sends an INSTANT alert the moment any connection is made

DETECTION SCENARIOS:
• Attacker compromises an internal machine and scans for database servers → hits the honeypot → ALERT
• Insider tries to access "another" EHR server to avoid audit logs → hits the honeypot → ALERT
• Ransomware spreading laterally and hitting database servers → hits the honeypot → ALERT`
      },
      {
        heading: "Honeypot 2 — Fake File Share Server",
        content: `WHAT IT LOOKS LIKE:
• An SMB/CIFS file share server (port 445)
• Contains folders that look like real hospital folders: "Patient_Records_2024", "Staff_Schedules", "Financial_Reports"
• Each folder has dummy files (PDFs, CSVs, DOCXs) with realistic names

WHAT IT ACTUALLY DOES:
• Records every login attempt, file browse, file download attempt
• Files are empty or contain random data — but the attacker doesn't know that
• Alerts on ANY access

WHY FILE SHARES ARE TARGETED:
• Ransomware encrypts files on shared drives (this catches ransomware spreading)
• Data thieves download bulk patient records from file shares
• This honeypot catches lateral movement in progress`
      },
      {
        heading: "Honeypot 3 — Fake Admin Portal",
        content: `WHAT IT LOOKS LIKE:
• A web application on port 443 (HTTPS)
• Login page that looks like a real hospital admin panel
• Has fake dashboards, user management pages, system settings
• Accepts any credentials (always says "login successful") to lure attackers deeper

WHAT IT ACTUALLY DOES:
• Logs the IP, credentials used, pages visited, actions attempted
• If an attacker tries to change settings or download data → deeper logging + alert
• Captures the attacker's tools, techniques, and procedures (TTPs)

WHY THIS IS VALUABLE:
• Attackers who gain initial access often look for admin panels to escalate privileges
• This honeypot wastes the attacker's time while we detect and respond
• The TTPs captured help us understand the attack methodology`
      },
      {
        heading: "Technical Setup",
        content: `DEPLOYMENT:
• Each honeypot runs as a Docker container
• All 3 are placed on the SAME internal network as real systems (so they look natural)
• But they are in a SEPARATE micro-segment — no real traffic should ever reach them
• Zero Trust policy: no service has permission to connect to these IPs

ALERTING PIPELINE:
Honeypot interaction → Honeypot logs event → Sends webhook to Threat Aggregation Engine → Dashboard alert fires → Cross-referenced with LSTM insider scores and 1D-CNN zero-day scores

If honeypot fires AND LSTM flags the same user AND 1D-CNN flags anomalous traffic → CRITICAL INCIDENT — full auto-lockdown of that network segment.`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 4. ZERO TRUST
  // ═══════════════════════════════════════════════════════════════════════════
  zerotrust: {
    title: "ZERO TRUST ARCHITECTURE",
    subtitle: "Never Trust, Always Verify",
    color: "#8b5cf6",
    icon: "🛡",
    blocks: [
      {
        heading: "What is Zero Trust?",
        content: `Traditional security assumes: "If you're inside the network, you're trusted." Zero Trust assumes the OPPOSITE: "NOBODY is trusted — not employees, not devices, not internal services. Every single request must be verified EVERY SINGLE TIME."

This is critical for healthcare because:
• A compromised internal account should NOT have free access to everything
• A third-party app should NOT be able to talk to the EHR database
• A medical device should NOT be able to send data to the internet
• Even if an attacker gets past the firewall, they hit a wall at every step`
      },
      {
        heading: "Principle 1 — Micro-Segmentation",
        content: `The hospital network is divided into ISOLATED ZONES. Services in one zone CANNOT talk to services in another zone unless explicitly allowed.

ZONES:
┌─────────────────────────────────────────────────────┐
│ ZONE A: EHR Zone                                    │
│   • EHR Application Server                          │
│   • EHR Database (PostgreSQL, encrypted)            │
│   • Audit Log Server                                │
├─────────────────────────────────────────────────────┤
│ ZONE B: Imaging Zone                                │
│   • PACS Server (medical image storage)             │
│   • Image Processing Server                         │
├─────────────────────────────────────────────────────┤
│ ZONE C: Billing Zone                                │
│   • Billing Application                             │
│   • Payment Processing (most isolated)              │
├─────────────────────────────────────────────────────┤
│ ZONE D: Medical Device Zone                         │
│   • All IoMed devices (ventilators, monitors, etc.) │
│   • Device Management Server                        │
│   • CANNOT reach the internet directly              │
├─────────────────────────────────────────────────────┤
│ ZONE E: Third-Party App Zone                        │
│   • All third-party integrations                    │
│   • Sandboxed, monitored, permission-scoped         │
├─────────────────────────────────────────────────────┤
│ ZONE F: Honeypot Zone                               │
│   • Fake EHR DB, File Share, Admin Portal           │
│   • Should NEVER receive traffic                    │
└─────────────────────────────────────────────────────┘

IMPLEMENTATION: Docker networks or VLANs. Firewall rules between each zone. Only explicitly allowed routes are open.`
      },
      {
        heading: "Principle 2 — Mutual TLS (mTLS)",
        content: `Every service-to-service communication uses MUTUAL TLS:
• Both the client AND the server prove their identity with a certificate
• If either side doesn't have a valid certificate → connection REFUSED
• Certificates are short-lived (24 hours) — if compromised, they expire quickly

HOW IT WORKS:
1. Service A wants to talk to Service B
2. Service A presents its TLS certificate: "I am Service A, here is my proof"
3. Service B checks: "Is this certificate valid? Is Service A allowed to talk to me?"
4. Service B presents its own certificate: "I am Service B, here is my proof"
5. Service A checks: "Is this really Service B?"
6. Only if BOTH checks pass → encrypted communication begins

This stops man-in-the-middle attacks and impersonation attacks dead in their tracks.`
      },
      {
        heading: "Principle 3 — Short-Lived Tokens + Risk Gating",
        content: `AUTHENTICATION:
• When a user logs in, they get a JWT (JSON Web Token) that expires in 15 MINUTES
• After 15 minutes, they must re-authenticate (silently via refresh token, or manually if risk is high)
• This means even if a token is stolen, it's useless after 15 minutes

RISK-SCORE GATING (this is where LSTM connects):
• Before EVERY request, the system checks the user's current LSTM risk score
• Risk < 0.3: Request allowed normally
• Risk 0.3–0.7: Request allowed but LOGGED with extra detail
• Risk > 0.7: Token is REVOKED. User must re-authenticate with MFA. Access is restricted to read-only on non-sensitive data.
• Risk > 0.9: Full LOCKOUT. User cannot access anything. Security team alerted.

This means our AI (LSTM) directly CONTROLS access in real-time. The system gets smarter the more suspicious someone behaves.`
      },
      {
        heading: "Principle 4 — Least Privilege",
        content: `Every user, device, and service gets the MINIMUM permissions needed to do their job. Nothing more.

EXAMPLES:
• A nurse in Ward 3 can ONLY read patient records from Ward 3
• The billing app can ONLY access billing data — not EHR records
• A medical device can ONLY send telemetry to the Device Management Server — not to any other server
• A third-party app is told exactly which APIs it can call and which data fields it can access

If any entity tries to access something outside its permissions → BLOCKED + ALERT.`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 5. THIRD-PARTY SOFTWARE
  // ═══════════════════════════════════════════════════════════════════════════
  thirdparty: {
    title: "THIRD-PARTY SOFTWARE PROTECTION",
    subtitle: "Supply Chain Attack Defense",
    color: "#06b6d4",
    icon: "📦",
    blocks: [
      {
        heading: "Why Third-Party Software is Dangerous",
        content: `In 2020, the SolarWinds attack compromised thousands of companies — including hospitals — by hiding malicious code inside a TRUSTED software update. The attackers didn't hack the hospital directly. They hacked a software vendor the hospital trusted, and the malicious code came in through a legitimate update.

In healthcare, hospitals use dozens of third-party apps:
• Billing software
• Scheduling tools
• Lab result integrations
• Telemedicine platforms
• Medical device firmware updaters

ANY of these could be compromised. We need to VERIFY every third-party app before it touches our network.`
      },
      {
        heading: "Layer 1 — Static Analysis",
        content: `BEFORE the app even runs, we analyze its binary/code:

WHAT WE CHECK:
• Strings: Extract all text strings from the binary. Look for suspicious URLs, file paths, registry keys
• Imports: What system functions does it call? Does it call network functions? File system functions? Encryption functions? (Ransomware loves encryption functions)
• Permissions: What does the app request? Does a billing app really need camera access? Microphone access?
• Dependencies: What libraries does it use? Are any of those libraries known to be vulnerable?
• Code signing: Is the binary signed by a trusted certificate?

TOOLS: We build a custom Python script that uses:
• pefile (for Windows PE analysis)
• strings extraction
• Permission manifest parsing
• CVE database lookup for dependencies

OUTPUT: A static risk score (0–50 points). If > 30 → flagged before it even runs.`
      },
      {
        heading: "Layer 2 — Dynamic Analysis (Sandbox)",
        content: `If the app passes static analysis, we run it in a SANDBOX — an isolated container where it can run but cannot affect the real network.

WHAT WE MONITOR IN THE SANDBOX:
• System calls: Every call the app makes to the OS (open file, create network connection, delete file, modify registry)
• Network traffic: What IPs does it connect to? What data does it send?
• File system: What files does it create, read, modify, delete?
• Process creation: Does it spawn child processes? (Common in malware)
• Memory behavior: Does it inject code into other processes?

HOW LONG: Run the app in the sandbox for 10 minutes with simulated user interaction (automated clicking, form filling)

OUTPUT: A behavioral log. This log is then fed through our LSTM model for network anomaly scoring (adding 0–50 more points to the risk score).`
      },
      {
        heading: "Layer 3 — API Gateway Enforcement",
        content: `Apps that PASS both analyses are allowed to run, but ONLY through our API Gateway:

API GATEWAY DOES:
1. PERMISSION SCOPING: The app is given a whitelist of exactly which API endpoints it can call. Calls to anything outside the whitelist → blocked.
2. RATE LIMITING: The app can only make X requests per minute. If it exceeds that → temporarily blocked (prevents data exfiltration).
3. INPUT VALIDATION: Every request the app sends is validated. SQL injection? Blocked. XSS payload? Blocked.
4. OUTPUT FILTERING: Data returned to the app is filtered — sensitive fields (SSN, full DOB) are masked unless explicitly permitted.
5. CONTINUOUS MONITORING: Even after deployment, the app's network traffic is continuously fed to the 1D-CNN for ongoing zero-day detection.

IF AT ANY POINT the app behaves outside its allowed scope → AUTO-BLOCKED + ALERT + the app is killed.`
      },
      {
        heading: "Layer 4 — Software Update Verification",
        content: `When a third-party app releases an update:
1. The update is downloaded but NOT installed
2. It goes through the FULL pipeline again: static analysis → sandbox → risk scoring
3. Only if it passes → the update is installed
4. The update's hash is compared to the vendor's published hash (integrity check)
5. If hashes don't match → update is REJECTED (possible supply chain attack)

This is how we would have caught SolarWinds.`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 6. EHR PROTECTION
  // ═══════════════════════════════════════════════════════════════════════════
  ehr: {
    title: "EHR PROTECTION",
    subtitle: "Electronic Health Records Hardening",
    color: "#ec4899",
    icon: "🏥",
    blocks: [
      {
        heading: "Why EHR is the #1 Target",
        content: `Electronic Health Records contain the most sensitive data in existence: a person's complete medical history, SSN, date of birth, address, insurance details, genetic information. On the black market, a medical record is worth $250+ (compared to $1 for a credit card number). Hospitals are the most targeted sector for data breaches in the world.`
      },
      {
        heading: "Layer 1 — Encryption",
        content: `AT REST (data stored on disk):
• AES-256 encryption on the entire database volume
• Encryption keys are stored in a SEPARATE Key Management Service (KMS) — not on the same server as the data
• Even if an attacker physically steals the hard drive, they get encrypted garbage

IN TRANSIT (data moving between systems):
• TLS 1.3 on ALL connections to/from the EHR database
• No unencrypted connections are allowed — the server rejects them
• Certificate pinning: the app only accepts connections from known, verified certificates

IN MEMORY:
• Patient data is decrypted only for the fraction of a second it's being processed
• Immediately re-encrypted before being sent anywhere`
      },
      {
        heading: "Layer 2 — Role-Based Access Control (RBAC) with Attributes",
        content: `Standard RBAC says: "Doctors can read patient records." But that's too broad.

WE USE ATTRIBUTE-BASED ACCESS CONTROL (ABAC):
A doctor can read a patient record ONLY IF:
  • The doctor is currently on duty (time check)
  • The patient is in the doctor's ward/department
  • The doctor has an active, non-revoked token
  • The doctor's LSTM risk score is below 0.7
  • The access is logged

ROLES IN THE SYSTEM:
• Doctor → Read patient records (own ward only), Write treatment notes
• Nurse → Read patient records (own ward only), Update vitals
• Lab Technician → Read/Write lab results only
• Admin → Manage users and permissions (cannot read patient records)
• Billing → Read billing-related fields only (not medical history)
• IT Support → Cannot access any patient data at all

EVERY access attempt is logged: who, what, when, from which device, for how long.`
      },
      {
        heading: "Layer 3 — Audit Trail",
        content: `EVERY interaction with the EHR is recorded in an append-only audit log:

LOG ENTRY CONTAINS:
• User ID
• Timestamp
• Action (read, write, delete, export)
• Patient record ID accessed
• Fields accessed/modified
• Source IP and device
• Session token ID

APPEND-ONLY means: logs cannot be deleted or modified — even by admins. This is critical for forensics.

INTEGRATION WITH LSTM:
• The audit trail is continuously fed to the LSTM insider threat model
• If a user's access pattern deviates from their historical norm → risk score increases
• Example: A doctor who normally reads 5 records/day suddenly reads 200 → LSTM flags it`
      },
      {
        heading: "Layer 4 — Backup & Recovery",
        content: `BACKUP STRATEGY:
• Full backup every 24 hours (encrypted, stored offsite)
• Incremental backup every hour
• Backups are stored in a COMPLETELY SEPARATE network — not reachable from the main network
• If ransomware hits, we can restore from backup without paying ransom

RECOVERY:
• Recovery Time Objective (RTO): 4 hours — system back online within 4 hours of an incident
• Recovery Point Objective (RPO): 1 hour — maximum 1 hour of data loss`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 7. ELECTRONIC MEDICAL DEVICES (IoMed)
  // ═══════════════════════════════════════════════════════════════════════════
  iomeddevice: {
    title: "MEDICAL DEVICE PROTECTION",
    subtitle: "IoMed / Connected Device Security",
    color: "#14b8a6",
    icon: "🏋",
    blocks: [
      {
        heading: "Why Medical Devices Are Terrifying to Hack",
        content: `In 2020, researchers discovered vulnerabilities in Philips ventilators that could allow remote attackers to change settings — potentially killing patients. In 2017, the FDA recalled 465,000 pacemakers because hackers could remotely change their settings. A hacker who can control a ventilator, infusion pump, or cardiac monitor can literally kill someone.

DEVICES WE PROTECT:
• Ventilators (control breathing)
• Patient monitors (track vitals)
• Infusion pumps (deliver medication — wrong dose = death)
• Cardiac monitors and defibrillators
• Insulin pumps
• Imaging machines (CT, MRI, X-ray)`
      },
      {
        heading: "Layer 1 — Network Isolation",
        content: `ALL medical devices live in ZONE D — a completely isolated VLAN:
• Devices CANNOT reach the internet directly
• Devices can ONLY communicate with the Device Management Server (also in Zone D)
• The Device Management Server is the ONLY gateway — it relays approved data to other zones
• If a device tries to connect to ANY IP outside Zone D → the connection is BLOCKED by the firewall

This means even if a device is compromised, the attacker is trapped inside Zone D and cannot move laterally.`
      },
      {
        heading: "Layer 2 — Edge Agent + Command Monitoring",
        content: `A lightweight edge agent is installed on (or next to) each medical device:

WHAT IT MONITORS:
• Every command sent TO the device (set temperature, adjust flow rate, change alarm threshold)
• Every command sent BY the device (status reports, telemetry)
• Firmware version (alert if it changes without authorization)
• Network connections the device makes
• Power state changes

WHAT IS "NORMAL" for a ventilator:
• Set commands from the nurse's station during treatment hours
• Regular status reports every 30 seconds
• Alarm triggers when patient vitals go out of range

WHAT IS "ABNORMAL":
• A set command coming from an unknown IP
• A command changing a critical parameter (like respiratory rate) outside normal clinical range
• A command sent at 3 AM when no nurse is on the floor
• A firmware update request not initiated by IT`
      },
      {
        heading: "Layer 3 — 1D-CNN Anomaly Detection Model",
        content: `The edge agent collects command sequences and sends them to a 1D-CNN model for anomaly detection.

ARCHITECTURE:
  Input: Command sequence (50 time steps × 30 features)
  Features per command: [command_type, parameter_value, source_ip, timestamp_features, device_id, nurse_id_or_null, is_during_shift_hours, parameter_delta_from_baseline, ...]

  → Conv1D(64, kernel=3) → ReLU → BatchNorm
  → Conv1D(128, kernel=3) → ReLU → BatchNorm  
  → MaxPool1D(2)
  → Conv1D(256, kernel=3) → ReLU → BatchNorm
  → GlobalAveragePooling
  → Dense(128) → ReLU → Dropout(0.4)
  → Dense(1) → Sigmoid

  Output: Anomaly probability (0.0 – 1.0)

TRAINING DATA:
• Normal: Real device command logs from operational devices (labeled 0)
• Anomalous: Synthetic attack commands (generated by domain experts) — wrong parameter ranges, commands from unauthorized sources, off-hours commands (labeled 1)

THRESHOLD: > 0.75 → ANOMALY DETECTED`
      },
      {
        heading: "Layer 4 — Auto-Isolation",
        content: `IF THE MODEL DETECTS AN ANOMALY:

IMMEDIATE ACTIONS (within 1 second):
1. The device is CUT from the network — its network interface is disabled
2. An alert fires on the dashboard: "MEDICAL DEVICE ANOMALY — [Device Name] — [Device ID]"
3. The security team is notified via SMS + email + dashboard
4. The last 10 minutes of command logs are preserved for forensics

CLINICAL TEAM NOTIFICATION:
• The nurse/doctor responsible for the device is alerted: "Device [X] has been isolated due to a security event"
• They can manually override ONLY if a senior clinician authorizes it
• The override is logged

WHY AUTO-ISOLATION IS CRITICAL:
A compromised ventilator can kill a patient in seconds. We cannot wait for a human to review alerts. The system must act INSTANTLY.`
      },
      {
        heading: "Layer 5 — Firmware Integrity",
        content: `Medical device firmware is a prime target for attackers (modify firmware = permanent compromise).

PROTECTION:
• Every device's firmware hash is stored in a trusted database
• The edge agent checks the firmware hash every hour
• If the hash changes (firmware was modified) → IMMEDIATE ISOLATION + ALERT
• Firmware updates can ONLY be installed through the Device Management Server
• Updates are verified against the manufacturer's published hash before installation
• Updates are installed during a maintenance window only — not during active patient care`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 8. PATIENT DATA
  // ═══════════════════════════════════════════════════════════════════════════
  patientdata: {
    title: "PATIENT DATA PROTECTION",
    subtitle: "End-to-End Data Security",
    color: "#a855f7",
    icon: "🔒",
    blocks: [
      {
        heading: "What Patient Data Includes",
        content: `HIPAA-protected health information (PHI) includes:
• Name, address, phone number, email
• Social Security Number
• Medical Record Number
• Date of Birth
• Diagnosis, treatment history, lab results
• Insurance provider and policy numbers
• Prescription details
• Genetic information
• Mental health records (extra legal protection)
• Photos/images

ALL of this must be protected at every layer of our system.`
      },
      {
        heading: "Protection Layer: At Rest",
        content: `• Database volumes encrypted with AES-256
• Backup files encrypted with AES-256
• Encryption keys in a separate Key Management Service
• Even database admins cannot read patient data without going through the application layer (which enforces RBAC)`
      },
      {
        heading: "Protection Layer: In Transit",
        content: `• TLS 1.3 on ALL network connections
• mTLS between all internal services
• No patient data is sent in URL parameters (always in encrypted POST body)
• API Gateway strips sensitive headers before forwarding`
      },
      {
        heading: "Protection Layer: In Application",
        content: `• RBAC + ABAC controls who can access what
• Data masking: When data is displayed, sensitive fields are masked unless the user's role requires the full value
  • Example: SSN shown as ***-**-1234
  • Full SSN only visible to authorized billing staff
• De-identification: For analytics and research, patient data is de-identified (names, SSNs removed) before being shared
• Audit trail logs every access`
      },
      {
        heading: "Protection Layer: Against Exfiltration",
        content: `• USB device policy: USB ports on hospital computers are DISABLED by default (via OSQuery + endpoint policy)
• Clipboard monitoring: If patient data is copied, it's logged
• Email filtering: Outgoing emails are scanned for PHI before sending — if PHI is detected, the email is blocked
• DLP (Data Loss Prevention): Any attempt to upload patient data to external cloud services is blocked by the API Gateway`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 9. GOOGLE COLAB TRAINING
  // ═══════════════════════════════════════════════════════════════════════════
  colab: {
    title: "GOOGLE COLAB TRAINING PLAN",
    subtitle: "4 Notebooks — Step by Step",
    color: "#6366f1",
    icon: "☁",
    blocks: [
      {
        heading: "Setup (Do This First)",
        content: `1. Go to colab.research.google.com
2. Click "New Notebook"
3. Click Runtime → Change Runtime → Hardware Accelerator: GPU (T4)
4. Mount Google Drive:
   from google.codrive import drive
   drive.mount('/content/drive')
5. Upload your datasets to Google Drive first, then load them in Colab via the mounted path
6. Install required libraries (in the first cell of each notebook)`
      },
      {
        heading: "Notebook 1: LSTM Insider Threat (Days 3–5)",
        content: `CELLS IN ORDER:

Cell 1 — Imports & Setup
Cell 2 — Mount Drive, load dataset
Cell 3 — Preprocessing: parse OSQuery JSON → sequences
Cell 4 — Split: train (70%), validation (15%), test (15%)
Cell 5 — Define PyTorch Dataset class
Cell 6 — Define LSTM Model class (Embedding → BiLSTM → Attention → Dense)
Cell 7 — Training loop with early stopping
Cell 8 — Validation loop
Cell 9 — Plot training/validation loss curves
Cell 10 — Evaluate on test set (accuracy, F1, AUC-ROC, confusion matrix)
Cell 11 — Save model: torch.save(model.state_dict(), '/content/drive/insider_threat_lstm.pt')

EXPECTED TRAINING TIME: 30–60 minutes on Colab GPU
TARGET ACCURACY: > 92%`
      },
      {
        heading: "Notebook 2: GAN Zero-Day Generator (Days 6–7)",
        content: `CELLS IN ORDER:

Cell 1 — Imports (torch, torch.nn, numpy, pandas)
Cell 2 — Load network traffic dataset (CICIDS or your own)
Cell 3 — Preprocess: extract 42 features per flow, create sequences of 100 flows
Cell 4 — Define Generator class (Dense layers → Reshape → Conv1DTranspose)
Cell 5 — Define Discriminator class (Conv1D layers → GlobalAvgPool → Dense)
Cell 6 — Define training loop:
   • Generate fake data from random noise
   • Train Discriminator on real + fake data
   • Train Generator to fool Discriminator
   • Use Wasserstein Loss
Cell 7 — Monitor loss curves (Generator loss should decrease, Discriminator loss should stabilize)
Cell 8 — After training: generate 10,000 synthetic attack sequences
Cell 9 — Save Generator: torch.save(generator.state_dict(), '/content/drive/gan_generator.pt')
Cell 10 — Save synthetic dataset for use in Notebook 3

EXPECTED TRAINING TIME: 45–90 minutes on Colab GPU
WATCH FOR: Mode collapse (Generator produces same output). If it happens, reduce learning rate or add noise injection.`
      },
      {
        heading: "Notebook 3: 1D-CNN Zero-Day Classifier (Days 8–9)",
        content: `CELLS IN ORDER:

Cell 1 — Imports
Cell 2 — Load: real normal traffic + real attack traffic + GAN-generated synthetic attacks
Cell 3 — Label: normal = 0, all attacks = 1
Cell 4 — Split: train/val/test
Cell 5 — Define 1D-CNN Model class (Conv1D blocks → GlobalAvgPool → Dense)
Cell 6 — Training loop with class weighting (attacks are rare → weight them higher)
Cell 7 — Validation loop
Cell 8 — Evaluate: accuracy, precision, recall, F1, AUC-ROC
Cell 9 — Test specifically on GAN-generated samples (this tests zero-day detection ability)
Cell 10 — Save model: torch.save(model.state_dict(), '/content/drive/zeroday_cnn.pt')

EXPECTED TRAINING TIME: 20–40 minutes on Colab GPU
TARGET: Recall > 90% on GAN-generated samples (this means we catch 90%+ of zero-days)`
      },
      {
        heading: "Notebook 4: 1D-CNN Device Anomaly (Days 25–26)",
        content: `CELLS IN ORDER:

Cell 1 — Imports
Cell 2 — Load device command sequence dataset (from edge agents)
Cell 3 — Preprocess: sequences of 50 commands × 30 features
Cell 4 — Label: normal commands = 0, anomalous commands = 1
Cell 5 — Define 1D-CNN Model class (same architecture as Notebook 3, adjusted input shape)
Cell 6 — Training loop
Cell 7 — Evaluate: focus on recall (we CANNOT miss a real anomaly on a medical device)
Cell 8 — Save model: torch.save(model.state_dict(), '/content/drive/device_anomaly_cnn.pt')

EXPECTED TRAINING TIME: 15–30 minutes on Colab GPU
TARGET: Recall > 95% (missing an anomaly on a ventilator could kill someone)`
      }
    ]
  },

  // ═══════════════════════════════════════════════════════════════════════════
  // 10. DASHBOARD
  // ═══════════════════════════════════════════════════════════════════════════
  dashboard: {
    title: "UNIFIED THREAT DASHBOARD v2",
    subtitle: "Single Pane of Glass",
    color: "#f97316",
    icon: "📊",
    blocks: [
      {
        heading: "What It Shows",
        content: `The dashboard aggregates ALL signals from ALL systems into ONE view:

PANEL 1 — Real-Time Threat Heatmap
• Visual map of the hospital network
• Color-coded by threat level (green → yellow → red)
• Click any node to see details

PANEL 2 — Insider Threat Scoreboard
• List of all users with their current LSTM risk scores
• Sorted by risk (highest first)
• Shows trend over time (is the score rising?)

PANEL 3 — Zero-Day Alert Feed
• Live feed of all 1D-CNN flags
• Each alert shows: source IP, confidence, suspicious features

PANEL 4 — Honeypot Status
• All 3 honeypots shown
• Green = no interaction (good)
• Red = interaction detected (ALERT)
• Click to see who touched it and what they did

PANEL 5 — Medical Device Status
• All connected devices listed
• Each shows: status (online/isolated/offline), last command, anomaly score
• Red devices = isolated due to anomaly

PANEL 6 — Third-Party App Risk Board
• All third-party apps with their risk scores
• Status: allowed, flagged, or blocked

PANEL 7 — EHR Audit Feed
• Recent EHR access events
• Flagged accesses highlighted`
      },
      {
        heading: "Technical Implementation",
        content: `BACKEND:
• FastAPI server that collects events from all subsystems via webhooks
• WebSocket connections to push real-time updates to the frontend
• PostgreSQL database for storing historical alert data

FRONTEND:
• React + Recharts for visualizations
• WebSocket client for real-time updates
• Auto-refresh every 5 seconds for non-WebSocket panels

DATA FLOW TO DASHBOARD:
LSTM scores → WebSocket push → Dashboard updates Insider panel
Honeypot alerts → WebSocket push → Dashboard updates Honeypot panel
1D-CNN flags → WebSocket push → Dashboard updates Zero-Day panel
Device edge agents → WebSocket push → Dashboard updates Device panel
Third-party analysis → WebSocket push → Dashboard updates App panel`
      }
    ]
  }
};

// DAY-BY-DAY (expanded)
const DAYS = [
  { day: 1, phase: 1, title: "OSQuery Setup", detail: "Install OSQuery on 3 simulated VMs (1 Windows, 2 Linux). Write custom query configs: user_logins, file_events, usb_events, network_connections, process_events. Test that logs are being generated every 60s. Set up the central log aggregator (simple FastAPI server that receives JSON logs and saves to a folder)." },
  { day: 2, phase: 1, title: "Data Collection & Preprocessing", detail: "Let OSQuery run for 12+ hours to collect realistic telemetry. Write preprocessing script: parse JSON → structured DataFrames. Encode categorical fields. Create time windows (1 hour per user). Generate synthetic labels (normal vs suspicious vs malicious patterns). Save preprocessed dataset." },
  { day: 3, phase: 1, title: "LSTM Architecture + First Train", detail: "Open Colab notebook 1. Define PyTorch Dataset, DataLoader. Build the LSTM model class: Embedding → BiLSTM (2 layers) → Attention → Dense → Sigmoid. Run the first training epoch to make sure shapes match and no errors. Monitor loss." },
  { day: 4, phase: 1, title: "LSTM Training & Tuning", detail: "Continue training LSTM for 50 epochs with early stopping. Monitor train/val loss curves. If overfitting → increase dropout. If underfitting → increase model size. Tune learning rate if needed." },
  { day: 5, phase: 1, title: "LSTM Evaluation + Deployment Prep", detail: "Evaluate LSTM on test set: accuracy, F1, AUC-ROC, confusion matrix. If metrics are good (>92% accuracy) → save model. Write the inference script: takes a sequence → outputs risk score. Test the inference script end-to-end." },
  { day: 6, phase: 1, title: "GAN Architecture + Setup", detail: "Open Colab notebook 2. Load network traffic dataset (CICIDS-2017). Preprocess into 100-flow sequences of 42 features. Define Generator and Discriminator architectures. Set up Wasserstein loss and training loop. Run first few epochs to check for errors." },
  { day: 7, phase: 1, title: "GAN Training + Synthetic Generation", detail: "Train GAN for 200 epochs. Monitor both losses. Watch for mode collapse. After training, generate 10,000 synthetic attack sequences. Visually inspect a few (compare feature distributions of real vs synthetic). Save Generator model and synthetic dataset." },
  { day: 8, phase: 1, title: "1D-CNN Zero-Day Classifier Build", detail: "Open Colab notebook 3. Combine real normal + real attacks + GAN synthetic attacks. Label and split. Define 1D-CNN architecture. Start training with class weighting." },
  { day: 9, phase: 1, title: "1D-CNN Evaluation", detail: "Evaluate 1D-CNN: overall accuracy + specifically test on GAN-generated samples (this is the zero-day detection test). Target: >90% recall on synthetic samples. Save model. Write inference script." },
  { day: 10, phase: 1, title: "Honeypot Deployment", detail: "Build 3 Docker containers: (1) Fake PostgreSQL with dummy patient data, (2) Fake SMB file share with decoy folders/files, (3) Fake admin web portal. Configure each to log all interactions and send webhooks to the threat aggregation engine. Place them in the simulated network alongside real (simulated) services." },
  { day: 11, phase: 1, title: "Phase 1 Integration Test", detail: "Run the full Phase 1 pipeline: simulate a suspicious user (mass file access + USB event) → OSQuery captures it → LSTM scores it high → alert fires. Simulate an attacker probing the honeypot → alert fires. Simulate anomalous network traffic → 1D-CNN flags it. Verify all alerts appear correctly." },
  { day: 12, phase: 1, title: "Phase 1 Bug Fix + Documentation", detail: "Fix any pipeline bugs found in Day 11 testing. Document all model metrics. Write README for Phase 1. Prepare model files for deployment." },
  { day: 13, phase: 2, title: "Zero Trust — Micro-Segmentation", detail: "Set up 6 network zones using Docker networks: EHR Zone, Imaging Zone, Billing Zone, Device Zone, Third-Party Zone, Honeypot Zone. Configure firewall rules: only explicitly allowed routes are open between zones. Test that a service in Zone A cannot reach Zone B without permission." },
  { day: 14, phase: 2, title: "Zero Trust — mTLS Setup", detail: "Set up a Certificate Authority (CA) — can use a self-signed CA for the project. Generate short-lived certificates (24h expiry) for each service. Configure all services to use mTLS. Test: service without valid cert → connection refused." },
  { day: 15, phase: 2, title: "Zero Trust — Token Auth + Risk Gating", detail: "Implement JWT-based authentication: tokens expire in 15 minutes, refresh tokens are used for re-auth. Integrate LSTM risk scores into the auth flow: before each request, check the user's current risk score. If score > 0.7 → revoke token. If score > 0.9 → full lockout. Test all scenarios." },
  { day: 16, phase: 2, title: "Third-Party — Sandbox Setup", detail: "Build a Docker-based sandbox environment. Configure it to capture: system calls (using strace or similar), network traffic (using tcpdump), file system events (using inotifywait). Test by running a benign app in the sandbox and verifying all events are captured." },
  { day: 17, phase: 2, title: "Third-Party — Static Analyzer", detail: "Build the static analysis script: extract strings, imports, permissions from app binaries. Build a scoring system: suspicious strings (+10), network imports (+5), encryption imports (+15), unsigned binary (+20), known-vulnerable dependency (+30). Test on a sample of benign and malicious binaries." },
  { day: 18, phase: 2, title: "Third-Party — Dynamic Analysis Integration", detail: "Connect sandbox output to the LSTM model: after an app runs in the sandbox, its network traffic is fed through the 1D-CNN for anomaly scoring. Combine static score + dynamic score into a final risk score. Test on a benign app (low score) and a simulated malicious app (high score)." },
  { day: 19, phase: 2, title: "API Gateway Setup", detail: "Deploy API Gateway (FastAPI or Kong). Configure permission scoping for each third-party app (whitelist of allowed endpoints). Implement rate limiting. Implement input validation (SQL injection, XSS detection using the CodeBERT model). Test: app trying to call an unauthorized endpoint → blocked." },
  { day: 20, phase: 2, title: "Third-Party Full Pipeline Test", detail: "Run a complete test: deploy a benign third-party app → goes through static analysis → sandbox → risk score computed → deployed behind API Gateway. Then deploy a simulated malicious app → flagged in static analysis OR sandbox → blocked. Verify the entire pipeline works." },
  { day: 21, phase: 2, title: "Zero Trust Stress Test", detail: "Attempt to bypass zero trust: try token replay attack, try to cross zone boundaries, try lateral movement from a compromised simulated service. Verify: all attempts are blocked. Fix any gaps found." },
  { day: 22, phase: 2, title: "Phase 2 Review + Documentation", detail: "Fix all bugs from Day 21 testing. Document zero trust policies, API gateway config, third-party analysis pipeline. Test everything one more time end-to-end." },
  { day: 23, phase: 3, title: "Medical Device Simulation Setup", detail: "Simulate 3 medical devices as lightweight Docker containers: ventilator (sends respiratory data, accepts set commands), patient monitor (sends vitals continuously), infusion pump (accepts dosage commands). Place all in Zone D (Device Zone). Verify they cannot reach the internet or other zones." },
  { day: 24, phase: 3, title: "Edge Agent Deployment", detail: "Build edge agent scripts that run alongside each simulated device. Each agent captures: every command sent to/from the device, firmware hash (check hourly), network connections attempted. Agents send captured data to the Device Management Server. Test that agents are running and data is flowing." },
  { day: 25, phase: 3, title: "Device Anomaly CNN — Build + Train", detail: "Open Colab notebook 4. Create training dataset: normal command sequences (from simulated devices during normal operation) + anomalous sequences (manually crafted: wrong parameter ranges, commands from bad IPs, off-hours commands). Define 1D-CNN architecture. Train the model." },
  { day: 26, phase: 3, title: "Device Anomaly CNN — Evaluate + Deploy", detail: "Evaluate CNN: focus on recall (>95% target — we cannot miss anomalies on medical devices). Save model. Deploy inference script on the Device Management Server. Wire up auto-isolation: if anomaly detected → device network interface disabled + alert sent. Test: inject a malicious command → verify device is isolated within 1 second." },
  { day: 27, phase: 3, title: "EHR Database Setup + Encryption", detail: "Set up PostgreSQL in the EHR Zone. Create schema for patient records. Enable AES-256 encryption at rest (using pgcrypto or filesystem-level encryption). Configure TLS 1.3. Set up Key Management Service (separate container). Populate with dummy patient data. Verify: direct database access without going through the application → blocked." },
  { day: 28, phase: 3, title: "EHR — RBAC + Audit Trail", detail: "Implement ABAC in the EHR application layer: each user has a role + department + ward. Access rules enforce: only own ward's patients, only during shift hours, only if risk score is low. Build the audit trail: every access logged to an append-only log. Wire audit trail into the LSTM pipeline (new access patterns affect risk scores). Test all role scenarios." },
  { day: 29, phase: 3, title: "Patient Data Protection — DLP", detail: "Implement USB blocking policy (via OSQuery endpoint policy). Set up email scanning for PHI (check outgoing emails for SSN patterns, patient names). Configure API Gateway to mask sensitive fields in responses (SSN → ***-**-1234). Set up de-identification pipeline for analytics/research data. Test all DLP controls." },
  { day: 30, phase: 3, title: "Unified Dashboard v2 Build", detail: "Build the React frontend: 7 panels (Heatmap, Insider Scores, Zero-Day Alerts, Honeypot Status, Device Status, Third-Party Apps, EHR Audit). Build the FastAPI backend that aggregates data from all subsystems. Set up WebSocket connections for real-time updates. Connect all data streams. Test that all panels update in real-time." },
  { day: 31, phase: 4, title: "Attack Chain Simulation #1", detail: "Simulate full attack chain: (1) Attacker compromises a third-party app → (2) App tries to access EHR data outside its permissions → blocked by API Gateway → (3) Attacker pivots, tries to reach another zone → blocked by micro-segmentation → (4) Attacker probes honeypot → alert fires → (5) LSTM flags the compromised app's user account → token revoked → (6) Dashboard shows the full attack chain in real-time." },
  { day: 32, phase: 4, title: "Attack Chain Simulation #2", detail: "Simulate medical device attack: (1) Attacker gains access to Device Zone somehow → (2) Sends malicious commands to ventilator → (3) Edge agent captures commands → (4) 1D-CNN flags anomaly → (5) Ventilator auto-isolated within 1 second → (6) Alert fires on dashboard → (7) Clinical team notified. Verify the entire chain works correctly and timing is within targets." },
  { day: 33, phase: 4, title: "Penetration Testing", detail: "Attempt to break the system: (1) Try SQL injection on EHR → CodeBERT catches it. (2) Try to exfiltrate patient data via USB → blocked. (3) Try to send PHI via email → blocked. (4) Try to bypass zero trust with a stolen token → token expired. (5) Try to modify device firmware → hash mismatch detected. (6) Try to access honeypot without detection → impossible (any access = alert). Document all findings." },
  { day: 34, phase: 4, title: "Bug Fixes + Re-Testing", detail: "Fix all issues found during penetration testing on Day 33. Re-run the specific tests that failed. Verify all fixes work. Run the full attack chain simulations again to make sure fixes didn't break anything else." },
  { day: 35, phase: 4, title: "Performance Metrics + Architecture Docs", detail: "Compile all model performance reports: CodeBERT (SQL injection), Phishing model, Ransomware model, LSTM (insider threat), GAN (zero-day gen), 1D-CNN (zero-day clf), 1D-CNN (device anomaly). Create system architecture diagrams. Document all components, how they connect, and how data flows. Prepare the demo environment (make sure everything is running and stable)." },
  { day: 36, phase: 4, title: "Final Demo Rehearsal", detail: "Do a complete walkthrough of the demo: show the dashboard, trigger each type of alert live (insider threat, zero-day, honeypot, device anomaly, third-party block), show the auto-response in action, explain the architecture. Practice the presentation. Make sure everything is green. Final submission." }
];

const phaseColor = { 1: "#f59e0b", 2: "#8b5cf6", 3: "#14b8a6", 4: "#ec4899" };
const phaseName = { 1: "Insider + Zero-Day", 2: "Zero Trust + 3rd Party", 3: "Devices + EHR + Data", 4: "Integration + Testing" };

// ─── COMPONENT ────────────────────────────────────────────────────────────────

export default function App() {
  const [tab, setTab] = useState("checklist");
  const [openSection, setOpenSection] = useState(null);
  const [openBlock, setOpenBlock] = useState(null);
  const [expandedDay, setExpandedDay] = useState(null);
  const [dayFilter, setDayFilter] = useState(0); // 0 = all

  const tabs = [
    { id: "checklist", label: "✓ Coverage Check" },
    { id: "sections", label: "📖 Full Details" },
    { id: "days", label: "📅 36-Day Plan" },
    { id: "architecture", label: "🔗 How It All Connects" }
  ];

  const sectionKeys = Object.keys(SECTIONS);

  return (
    <div style={{ background: "#080c18", color: "#e2e8f0", minHeight: "100vh", fontFamily: "'SF Mono', 'Fira Code', monospace", padding: 20, maxWidth: 920, margin: "0 auto" }}>
      {/* HEADER */}
      <div style={{ textAlign: "center", marginBottom: 24, paddingBottom: 20, borderBottom: "1px solid #1e293b" }}>
        <div style={{ fontSize: 9, letterSpacing: 5, color: "#475569", textTransform: "uppercase", marginBottom: 8 }}>Healthcare Cyber Shield — Master Plan</div>
        <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", margin: 0 }}>
          <span style={{ color: "#ef4444" }}>●</span> FULL EXECUTION BLUEPRINT
        </h1>
        <div style={{ fontSize: 10, color: "#475569", marginTop: 6 }}>Every aspect covered — 10 subsystems · 7 ML models · 36 days · end to end</div>
      </div>

      {/* TABS */}
      <div style={{ display: "flex", gap: 4, marginBottom: 20, flexWrap: "wrap" }}>
        {tabs.map(t => (
          <button key={t.id} onClick={() => setTab(t.id)} style={{
            background: tab === t.id ? "#1e293b" : "transparent",
            border: tab === t.id ? "1px solid #334155" : "1px solid #1a2332",
            color: tab === t.id ? "#f1f5f9" : "#64748b",
            borderRadius: 6, padding: "7px 13px", fontSize: 10.5, cursor: "pointer", whiteSpace: "nowrap", transition: "all .15s"
          }}>{t.label}</button>
        ))}
      </div>

      {/* ═══ CHECKLIST TAB ═══ */}
      {tab === "checklist" && (
        <div>
          <div style={{ fontSize: 10, color: "#475569", marginBottom: 12, letterSpacing: 2 }}>COVERAGE VERIFICATION — EVERY REQUIREMENT YOU MENTIONED</div>
          {checklistItems.map((item, i) => (
            <div key={item.id} style={{
              display: "flex", alignItems: "center", gap: 12, padding: "11px 16px",
              background: "#0f1729", border: "1px solid #1e293b", borderRadius: 7, marginBottom: 5
            }}>
              <div style={{ width: 22, height: 22, borderRadius: 5, background: "#052e16", border: "1.5px solid #22c55e", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                <span style={{ color: "#22c55e", fontSize: 12 }}>✓</span>
              </div>
              <div>
                <div style={{ fontSize: 12, color: "#f1f5f9", fontWeight: 600 }}>{item.label}</div>
                <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>
                  {item.id === "insider" && "Covered in Section 1: OSQuery agent collects telemetry → LSTM scores behavior in real-time → auto-revoke if suspicious"}
                  {item.id === "zeroday" && "Covered in Section 2: GAN generates synthetic zero-day attacks → 1D-CNN trained on real + synthetic → detects novel attacks"}
                  {item.id === "honeypot" && "Covered in Section 3: 3 decoys (fake EHR DB, file share, admin portal) — any touch = instant alert"}
                  {item.id === "zerotrust" && "Covered in Section 4: Micro-segmentation + mTLS + short-lived tokens + risk-score gating + least privilege"}
                  {item.id === "thirdparty" && "Covered in Section 5: Static analysis + sandbox dynamic analysis + API gateway enforcement + update verification"}
                  {item.id === "ehr" && "Covered in Section 6: AES-256 encryption + RBAC/ABAC + append-only audit trail + backup/recovery"}
                  {item.id === "iomeddevice" && "Covered in Section 7: Network isolation + edge agents + 1D-CNN anomaly detection + auto-isolation in <1 sec + firmware integrity"}
                  {item.id === "patientdata" && "Covered in Section 8: At-rest encryption + in-transit TLS + RBAC masking + USB blocking + email PHI scanning + DLP"}
                  {item.id === "colab" && "Covered in Section 9: 4 notebooks with cell-by-cell instructions — LSTM, GAN, CNN zero-day, CNN device anomaly"}
                  {item.id === "dashboard" && "Covered in Section 10: 7-panel unified dashboard — all signals in one place, real-time WebSocket updates"}
                </div>
              </div>
            </div>
          ))}
          <div style={{ marginTop: 16, padding: 14, background: "#052e16", border: "1px solid #22c55e33", borderRadius: 8, textAlign: "center" }}>
            <span style={{ fontSize: 11, color: "#22c55e", fontWeight: 600 }}>✓ All 10 requirements fully covered in this plan</span>
          </div>
        </div>
      )}

      {/* ═══ SECTIONS TAB ═══ */}
      {tab === "sections" && (
        <div>
          <div style={{ fontSize: 10, color: "#475569", marginBottom: 12, letterSpacing: 2 }}>10 SUBSYSTEMS — CLICK TO EXPAND FULL DETAILS</div>
          {sectionKeys.map((key) => {
            const sec = SECTIONS[key];
            const isOpen = openSection === key;
            return (
              <div key={key} style={{ marginBottom: 6 }}>
                <button onClick={() => { setOpenSection(isOpen ? null : key); setOpenBlock(null); }} style={{
                  width: "100%", background: isOpen ? "#12192e" : "#0f1729",
                  border: `1px solid ${isOpen ? sec.color + "44" : "#1e293b"}`,
                  borderRadius: 7, padding: "11px 15px", cursor: "pointer",
                  display: "flex", justifyContent: "space-between", alignItems: "center", transition: "all .15s"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 18 }}>{sec.icon}</span>
                    <div style={{ textAlign: "left" }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: sec.color }}>{sec.title}</div>
                      <div style={{ fontSize: 9, color: "#475569" }}>{sec.subtitle}</div>
                    </div>
                  </div>
                  <span style={{ color: "#475569", fontSize: 16 }}>{isOpen ? "−" : "+"}</span>
                </button>

                {isOpen && (
                  <div style={{ marginLeft: 12, marginTop: 4 }}>
                    {sec.blocks.map((block, bi) => {
                      const bKey = key + bi;
                      const bOpen = openBlock === bKey;
                      return (
                        <div key={bi} style={{ marginBottom: 4 }}>
                          <button onClick={() => setOpenBlock(bOpen ? null : bKey)} style={{
                            width: "100%", background: "#0a1020", border: "1px solid #1a2638",
                            borderRadius: 5, padding: "8px 12px", cursor: "pointer",
                            display: "flex", justifyContent: "space-between", alignItems: "center"
                          }}>
                            <span style={{ fontSize: 11, color: bOpen ? sec.color : "#94a3b8", fontWeight: 600 }}>{block.heading}</span>
                            <span style={{ color: "#475569", fontSize: 13 }}>{bOpen ? "−" : "+"}</span>
                          </button>
                          {bOpen && (
                            <div style={{ background: "#070b18", border: "1px solid #1a2638", borderTop: "none", borderRadius: "0 0 5px 5px", padding: "12px 14px" }}>
                              {block.content.split("\n").map((line, li) => {
                                if (line.trim() === "") return <div key={li} style={{ height: 8 }}></div>;
                                const isBullet = line.trim().startsWith("•");
                                const isHeader = line.trim().startsWith("WHAT") || line.trim().startsWith("HOW") || line.trim().startsWith("WHY") || line.trim().startsWith("DETECTION") || line.trim().startsWith("FLOW") || line.trim().startsWith("CELLS") || line.trim().startsWith("STEP") || line.trim().startsWith("ZONES") || line.trim().startsWith("ROLES") || line.trim().startsWith("DEPLOYMENT") || line.trim().startsWith("ALERTING") || line.trim().startsWith("DATA") || line.trim().startsWith("FEATURES") || line.trim().startsWith("FINAL") || line.trim().startsWith("SEQUENCE") || line.trim().startsWith("ARCHITECTURE") || line.trim().startsWith("LOSS") || line.trim().startsWith("OPTIMIZER") || line.trim().startsWith("THRESHOLD") || line.trim().startsWith("TRAINING") || line.trim().startsWith("EXPECTED") || line.trim().startsWith("TARGET") || line.trim().startsWith("WATCH") || line.trim().startsWith("IMMEDIATE") || line.trim().startsWith("CLINICAL") || line.trim().startsWith("PROTECTION") || line.trim().startsWith("BACKUP") || line.trim().startsWith("RECOVERY") || line.trim().startsWith("AT REST") || line.trim().startsWith("IN TRANSIT") || line.trim().startsWith("IN MEMORY") || line.trim().startsWith("PANEL") || line.trim().startsWith("BACKEND") || line.trim().startsWith("FRONTEND") || line.trim().startsWith("LOG") || line.trim().startsWith("APPEND") || line.trim().startsWith("INTEGRATION") || line.trim().startsWith("EXAMPLES") || line.trim().startsWith("WHAT WE") || line.trim().startsWith("TOOLS") || line.trim().startsWith("OUTPUT") || line.trim().startsWith("DEVICES") || line.trim().startsWith("LAYER") || line.trim().startsWith("SETUP") || line.trim().startsWith("INPUT") || line.trim().startsWith("→");
                                return (
                                  <div key={li} style={{
                                    fontSize: isBullet ? 10.5 : isHeader ? 10 : 11,
                                    color: isBullet ? "#94a3b8" : isHeader ? sec.color : "#cbd5e1",
                                    fontWeight: isHeader ? 700 : 400,
                                    marginLeft: isBullet ? 12 : 0,
                                    lineHeight: 1.7,
                                    letterSpacing: isHeader ? 0.5 : 0
                                  }}>{line}</div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ═══ DAYS TAB ═══ */}
      {tab === "days" && (
        <div>
          <div style={{ display: "flex", gap: 6, marginBottom: 14, flexWrap: "wrap", alignItems: "center" }}>
            <span style={{ fontSize: 10, color: "#475569" }}>Filter:</span>
            {[0, 1, 2, 3, 4].map(p => (
              <button key={p} onClick={() => setDayFilter(p)} style={{
                background: dayFilter === p ? (p === 0 ? "#1e293b" : phaseColor[p] + "22") : "transparent",
                border: `1px solid ${dayFilter === p ? (p === 0 ? "#334155" : phaseColor[p] + "55") : "#1a2638"}`,
                color: dayFilter === p ? (p === 0 ? "#f1f5f9" : phaseColor[p]) : "#64748b",
                borderRadius: 5, padding: "3px 10px", fontSize: 9.5, cursor: "pointer"
              }}>{p === 0 ? "All" : `P${p}`}</button>
            ))}
          </div>
          <div>
            {DAYS.filter(d => dayFilter === 0 || d.phase === dayFilter).map((d, i) => {
              const isOpen = expandedDay === i;
              return (
                <div key={i} style={{ display: "flex", gap: 8, marginBottom: 3 }}>
                  <div style={{
                    minWidth: 52, background: "#0f1729", border: `1px solid ${phaseColor[d.phase]}33`,
                    borderRadius: 5, padding: "5px 0", textAlign: "center", flexShrink: 0
                  }}>
                    <div style={{ fontSize: 9, color: phaseColor[d.phase], fontWeight: 700 }}>Day {d.day}</div>
                    <div style={{ fontSize: 7.5, color: "#475569" }}>P{d.phase}</div>
                  </div>
                  <div style={{ flex: 1 }}>
                    <button onClick={() => setExpandedDay(isOpen ? null : i)} style={{
                      width: "100%", textAlign: "left", background: "#0a1020",
                      border: `1px solid ${isOpen ? phaseColor[d.phase] + "44" : "#1a2638"}`,
                      borderLeft: `3px solid ${phaseColor[d.phase]}`,
                      borderRadius: 5, padding: "7px 11px", cursor: "pointer", transition: "all .15s"
                    }}>
                      <div style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{d.title}</div>
                      {isOpen && (
                        <div style={{ fontSize: 10.5, color: "#94a3b8", marginTop: 6, lineHeight: 1.7 }}>{d.detail}</div>
                      )}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
          {/* Legend */}
          <div style={{ display: "flex", gap: 14, marginTop: 16, flexWrap: "wrap" }}>
            {[1, 2, 3, 4].map(p => (
              <div key={p} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 9.5 }}>
                <div style={{ width: 9, height: 9, background: phaseColor[p], borderRadius: 2 }}></div>
                <span style={{ color: phaseColor[p] }}>P{p}</span>
                <span style={{ color: "#475569" }}>— {phaseName[p]}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ═══ ARCHITECTURE TAB ═══ */}
      {tab === "architecture" && (
        <div>
          <div style={{ fontSize: 10, color: "#475569", marginBottom: 14, letterSpacing: 2 }}>HOW EVERYTHING CONNECTS — SIGNAL FLOW & INTEGRATION MAP</div>

          {/* Layered Architecture */}
          {[
            { label: "EDGE LAYER", color: "#14b8a6", items: [
              { name: "OSQuery Agents", detail: "On every endpoint. Collect telemetry every 60s. Send to Central Aggregator." },
              { name: "IoMed Edge Agents", detail: "On/next to every medical device. Monitor commands, firmware, network. Send to Device Mgmt Server." },
              { name: "Honeypot 1: Fake EHR DB", detail: "Fake PostgreSQL. Logs all connections. Alerts on any touch." },
              { name: "Honeypot 2: Fake File Share", detail: "Fake SMB server. Decoy folders with dummy files. Alerts on any access." },
              { name: "Honeypot 3: Fake Admin Portal", detail: "Fake web app. Accepts any credentials. Logs all activity." }
            ]},
            { label: "NETWORK LAYER", color: "#8b5cf6", items: [
              { name: "Micro-Segmentation", detail: "6 isolated zones (EHR, Imaging, Billing, Device, Third-Party, Honeypot). Firewall rules between each." },
              { name: "mTLS", detail: "All service-to-service communication uses mutual TLS. Short-lived certs (24h)." },
              { name: "API Gateway", detail: "All external/third-party traffic routes through here. Rate limiting, input validation, permission scoping." },
              { name: "Zero Trust Policy Engine", detail: "Checks risk scores before every request. Revokes tokens if risk is high." }
            ]},
            { label: "AI / ML LAYER", color: "#f59e0b", items: [
              { name: "LSTM — Insider Threat", detail: "Input: OSQuery sequences. Output: risk score per user. Feeds into Zero Trust." },
              { name: "GAN — Zero-Day Generator", detail: "Generates synthetic attack traffic. Output used to train the 1D-CNN below." },
              { name: "1D-CNN — Zero-Day Classifier", detail: "Input: network traffic. Trained on real + GAN synthetic. Flags novel attacks." },
              { name: "1D-CNN — Device Anomaly", detail: "Input: device command streams. Flags anomalous commands on medical devices." },
              { name: "CodeBERT — SQL Injection", detail: "Runs at API Gateway. Blocks SQL injection in real-time." },
              { name: "Phishing Model", detail: "Scans emails/URLs for phishing attempts." },
              { name: "Ransomware Model", detail: "Monitors file system for ransomware behavior patterns." }
            ]},
            { label: "DATA LAYER", color: "#22c55e", items: [
              { name: "EHR Database", detail: "AES-256 encrypted. RBAC/ABAC enforced at app layer. Append-only audit trail." },
              { name: "Telemetry Store", detail: "Central log aggregator. Stores all OSQuery and edge agent data." },
              { name: "Third-Party Sandbox Logs", detail: "Syscalls, network traffic, file events from sandbox analysis." },
              { name: "Patient Data Store", detail: "Encrypted. Masked in responses. USB/email DLP enforced." }
            ]},
            { label: "ORCHESTRATION LAYER", color: "#ec4899", items: [
              { name: "Threat Aggregation Engine", detail: "Receives signals from ALL subsystems. Correlates and escalates." },
              { name: "Auto-Response Engine", detail: "Isolate device / block user / revoke token / kill app — automatically." },
              { name: "Unified Dashboard v2", detail: "7 panels. Real-time WebSocket updates. Single pane of glass." }
            ]}
          ].map((layer, li) => (
            <div key={li} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
                <div style={{ width: 7, height: 7, borderRadius: "50%", background: layer.color, boxShadow: `0 0 6px ${layer.color}55` }}></div>
                <span style={{ fontSize: 10, fontWeight: 700, color: layer.color, letterSpacing: 2 }}>{layer.label}</span>
              </div>
              <div style={{ background: "#0f1729", border: `1px solid ${layer.color}1a`, borderRadius: 6, overflow: "hidden" }}>
                {layer.items.map((item, ii) => (
                  <div key={ii} style={{ display: "flex", gap: 10, padding: "7px 12px", alignItems: "flex-start", borderBottom: ii < layer.items.length - 1 ? "1px solid #141e33" : "none" }}>
                    <span style={{ color: layer.color, fontSize: 9, marginTop: 3, flexShrink: 0 }}>▸</span>
                    <div>
                      <span style={{ fontSize: 11, color: "#f1f5f9", fontWeight: 600 }}>{item.name}</span>
                      <span style={{ fontSize: 10, color: "#64748b" }}> — {item.detail}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Integration connections */}
          <div style={{ marginTop: 18, background: "#0f1729", border: "1px solid #1e293b", borderRadius: 8, padding: 16 }}>
            <div style={{ fontSize: 10, color: "#475569", letterSpacing: 2, marginBottom: 12 }}>KEY INTEGRATION CONNECTIONS</div>
            {[
              { from: "OSQuery Agents", arrow: "→", to: "Central Aggregator", then: "→", final: "LSTM Model", color: "#f59e0b" },
              { from: "LSTM Risk Score", arrow: "→", to: "Zero Trust Engine", then: "→", final: "Token Revocation / Lockout", color: "#8b5cf6" },
              { from: "Network Traffic", arrow: "→", to: "1D-CNN Classifier", then: "→", final: "Zero-Day Alert", color: "#ef4444" },
              { from: "GAN Generator", arrow: "→", to: "Synthetic Attacks", then: "→", final: "1D-CNN Training Data", color: "#ef4444" },
              { from: "Honeypot Interaction", arrow: "→", to: "Threat Aggregator", then: "→", final: "Cross-Reference + Alert", color: "#22c55e" },
              { from: "Third-Party App", arrow: "→", to: "Static + Sandbox Analysis", then: "→", final: "Risk Score → Allow/Block", color: "#06b6d4" },
              { from: "Device Edge Agent", arrow: "→", to: "1D-CNN Device Model", then: "→", final: "Auto-Isolation if Anomaly", color: "#14b8a6" },
              { from: "EHR Access", arrow: "→", to: "Audit Trail", then: "→", final: "LSTM (updates risk score)", color: "#ec4899" },
              { from: "API Gateway", arrow: "→", to: "CodeBERT", then: "→", final: "Block SQL Injection", color: "#a855f7" },
              { from: "All Alerts", arrow: "→", to: "Threat Aggregator", then: "→", final: "Dashboard (real-time)", color: "#f97316" }
            ].map((conn, ci) => (
              <div key={ci} style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 0", flexWrap: "wrap" }}>
                <span style={{ fontSize: 10, color: conn.color, fontWeight: 600 }}>{conn.from}</span>
                <span style={{ fontSize: 10, color: "#475569" }}>{conn.arrow}</span>
                <span style={{ fontSize: 10, color: "#94a3b8" }}>{conn.to}</span>
                <span style={{ fontSize: 10, color: "#475569" }}>{conn.then}</span>
                <span style={{ fontSize: 10, color: "#64748b", fontStyle: "italic" }}>{conn.final}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Footer */}
      <div style={{ marginTop: 24, paddingTop: 14, borderTop: "1px solid #1e293b", textAlign: "center" }}>
        <div style={{ fontSize: 9, color: "#334155" }}>TOOLS: Cursor · Google AI Studio IDE · Google Colab GPU · Docker · OSQuery · PyTorch · FastAPI · React</div>
      </div>
    </div>
  );
}
