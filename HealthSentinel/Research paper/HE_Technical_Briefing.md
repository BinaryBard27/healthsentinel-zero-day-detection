# Technical Briefing: Privacy-Preserving Healthcare Systems Using Homomorphic Encryption

**Target Document:** IEEE Research Paper
**Focus Areas:** System Model, Methodology, Performance Metrics, Future Integration
**System Base:** HealthSentinel (XGBoost NLP Pipeline & LSTM Autoencoder)

---

## I. System Model and Architecture (Section III)

Integrating Homomorphic Encryption (HE) into HealthSentinel requires a decoupled architecture where cryptographic boundaries separate local healthcare endpoints from the untrusted cloud computation environment. The model establishes a secure inference pipeline for both the SQL/Phishing NLP system and the Insider Threat behavior analyzer.

**Architectural Data Flow diagram:**

```text
[ Edge / Healthcare Endpoints ] 
   ├── EHR Transaction Streams & HTTP Logs
   └── osquery Behavioral Logs (30-timestep aggregations)
           ↓ (Plaintext Pre-processing: TF-IDF Char N-Grams & Normalization)
           
[ Cryptographic Gateway (Client-Side) ]
   ├── Key Generation (Public Key: pk, Secret Key: sk, Eval Key: evk)
   └── Homomorphic Encryption (m → c)
           ↓ (Ciphertext Transmission over TLS)
           
[ HealthSentinel Untrusted Cloud Computation ]
   ├── Encrypted LSTM Autoencoder (Insider Threat Detection)
   │     └── Secure Tensor Arithmetic & Homomorphic Taylor Approximations
   └── Encrypted XGBoost Pipeline (SQLi & Phishing Detection)
         └── Homomorphic Decision Tree Path Evaluation
           ↓ (Secure Inference Results: c_score)
           
[ Authorized Sentinel Node / SOC Endpoint ]
   ├── Homomorphic Decryption (Dec_sk(c_score) → m_score)
   └── Risk Threshold Comparison & Quarantine Actuation
```

---

## II. Methodology & Mathematical Foundation (Section IV)

### 1. Optimal HE Scheme Selection
Given the dual nature of HealthSentinel's ML pipelines, we propose utilizing the **Cheon-Kim-Kim-Song (CKKS)** scheme universally, avoiding multi-scheme conversion overhead.
*   **LSTM Autoencoder (Insider Threat):** CKKS is mandatory. It natively supports approximate arithmetic on real/complex numbers, which is essential for preserving the precision of the 12-feature sliding window vectors and executing the matrix multiplications of the encoder/decoder blocks.
*   **XGBoost Pipeline (SQLi NLP):** While the Brakerski-Fan-Vercauteren (BFV) scheme is typically favored for discrete integer logic, our parameter tuning relies on a TF-IDF vectorizer outputting continuous sparsity. CKKS can handle these floating-point representations directly, streamlining the cryptographic state.

### 2. Cryptographic Parameters
To achieve ≥ 128-bit security while accommodating the depth of our networks:
*   **Ring Dimension / Polynomial Modulus Degree ($N$):** $N = 32768$. This massive state size is required to handle the multiplicative depth of the 300 estimators in XGBoost and the 30-step recurrence of the LSTM without exhausting the computational level budget.
*   **Ciphertext Modulus ($Q$):** A multi-precision integer $Q = \prod_{i=0}^{L} q_i$. For our implementation, a level budget of $L \approx 15-20$ is necessary, with an initial scaling factor $\Delta \approx 2^{40}$ to preserve the TF-IDF feature precision ($10^{-5}$).

### 3. Encrypted Domain Inference Formulation
*   **Vectorized Dot Products (TF-IDF):** The linear NLP features are mapped to ciphertext slots. A dot product between encrypted inputs $\mathbf{C}_{in}$ and plaintext feature weights $\mathbf{W}$ is computed via element-wise homomorphic multiplication followed by a logarithmic rotate-and-sum algorithm: $\sum \mathbf{C}_{in} \odot \mathbf{W}$.
*   **XGBoost Tree Splits (`max_depth=6`):** Since HE lacks non-linear zero-comparisons, internal node conditions ($x_f < \tau$) must be substituted with a minimax continuous polynomial approximation of the signum function over the interval $[-1, 1]$: $P_{split}(x) \approx \text{sgn}(x - \tau)$. The leaf output becomes a secure sum of weighted path indicators.
*   **LSTM Activations:** Non-linear operations such as $h_t = \tanh(W_{x} x_t + W_{h} h_{t-1} + b)$ are evaluated homomorphically by replacing the hyperbolic tangent with a low-degree Maclaurin series polynomial approximation (e.g., $deg = 3$ or $7$).

---

## III. Performance Parameters & Metrics (Sections VI & VII)

Extrapolating from the existing 2.3 MB CPU-optimized XGBoost SQLi model (99.33% accuracy, tree_method='hist'), transitioning to the encrypted paradigm imposes critical local environment engineering limits:

1.  **Computational Overhead & Latency constraints:** 
    Local CPU inference currently executes in $<10$ ms. Under CKKS with $N=32768$, polynomial multiplication relies on Number Theoretic Transforms (NTTs). Evaluating 300 deep decision trees will trigger geometric increases in computation. We estimate the inference latency to regress to **$4$ to $12$ seconds per payload** on a local standard CPU pipeline. 
2.  **Memory Expansion Factor:**
    A fundamental limitation of HE is ciphertext bloat. Encoding the bounded $60,000$ max_features TF-IDF array into a packed plaintext polynomial and subsequently encrypting it expands the required memory by $10^3\times$ to $10^4\times$. The 2.3 MB static XGBoost model structure, when loaded into HE evaluation contexts, may command a persistent **$250$ MB to $500$ MB RAM footprint** per active inference session.
3.  **Noise Growth and Multiplicative Limits:** 
    Executing `max_depth=6` necessitates nested polynomial evaluations. Without implementing a computationally heavy "bootstrapping" circuit to refresh ciphertexts mid-flight, the accumulated noise $\epsilon$ will destroy the lower significant bits of the scaling factor, resulting in classification accuracy degradation from $99.33\%$ to an estimated $< 85\%$ bounds unless parameter $Q$ is perfectly optimized. Local CPUs will encounter severe L3 cache thrashing moving these massive NTT arrays.

---

## IV. Future Integration Strategies (Section VIII)

To mitigate the rigid cryptographic barriers introduced in HealthSentinel, we propose two advanced extensions:

1.  **HE-Enabled Federated Learning (HE-FL) at Clinical Hubs:** 
    A pure architectural evolution. Rather than centralizing logging via `osquery` over HTTPS, localized HealthSentinel aggregators deploy models directly within isolated hospital subnets. Endpoints apply local gradients to the LSTM autoencoder and encrypt the delta matrices using HE. The central HealthSentinel cloud hub computes $\sum C_{\Delta W}$ entirely in the ciphertext domain, achieving differential privacy without degrading anomaly detection capabilities over diverse demographics.
2.  **Hardware-Accelerated Trusted Execution Environment (TEE) Hybrids:** 
    To bypass the polynomial degree limits obstructing real-time SQL/Phishing mitigation at the HTTP gateway, future revisions could proxy the HE "bootstrapping" phase to a hardware enclave like Intel SGX or AMD SEV. While the initial matrix arithmetic happens homomorphically on GPUs, depth-reset operations occur in the TEE, slashing latency from seconds to milliseconds while satisfying zero-trust cryptographic guarantees.
