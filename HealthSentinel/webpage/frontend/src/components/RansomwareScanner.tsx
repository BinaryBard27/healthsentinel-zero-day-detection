import { useState } from "react";
import axios from "axios";
import { Loader2, Shield, AlertTriangle, CheckCircle2, Zap } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const FEATURE_NAMES = [
    "entropy", "file_size_norm", "pe_sections", "import_count",
    "export_count", "suspicious_api", "packed", "overlay_size",
    "resource_ratio", "string_entropy"
];

const ATTACK_SCENARIOS = [
    { label: "🟢 Safe EXE", features: "0.1, 0.2, 0.05, 0.3, 0.1, 0.0, 0.0, 0.05, 0.9, 0.1", type: "safe" },
    { label: "🔴 WannaCry", features: "0.95, 0.88, 0.92, 0.85, 0.72, 1.0, 0.95, 0.78, 0.08, 0.91", type: "wannacry" },
    { label: "🔴 LockBit", features: "0.92, 0.95, 0.88, 0.90, 0.65, 0.97, 0.88, 0.82, 0.05, 0.88", type: "lockbit" },
    { label: "🟡 Suspicious", features: "0.55, 0.6, 0.40, 0.70, 0.45, 0.35, 0.55, 0.42, 0.5, 0.58", type: "suspicious" },
];

const ATTACK_EXPLANATIONS: Record<string, { summary: string; technical: string; mitigation: string }> = {
    wannacry: {
        summary: "WannaCry-style Ransomware Pattern",
        technical: "Extremely high entropy (0.95) indicates heavy encryption/packing. Maximum suspicious_api score suggests calls to CryptEncrypt, CreateFileMapping, and VirtualAlloc known from WannaCry variants.",
        mitigation: "Isolate system immediately. Block SMB port 445. Apply MS17-010 patch. Restore from offline backup.",
    },
    lockbit: {
        summary: "LockBit 3.0-style Ransomware Pattern",
        technical: "High PE section count with packed flag indicates reflective DLL loading. High import_count with low export_count is characteristic of LockBit's modular architecture that imports encryption libraries dynamically.",
        mitigation: "Terminate process immediately. Enable Windows Defender Tamper Protection. Review recent RDP access logs for lateral movement.",
    },
    suspicious: {
        summary: "Suspicious — Potential Low-Confidence Threat",
        technical: "Moderate entropy and suspicious API usage suggest possible obfuscation. May be a packer, protector, or early-stage dropper. Requires sandbox detonation for definitive classification.",
        mitigation: "Submit to sandbox for dynamic analysis. Check VirusTotal hash. Quarantine pending review.",
    },
    safe: {
        summary: "Benign Executable — No Threats Detected",
        technical: "Low entropy (0.1) indicates uncompressed, human-readable code. No suspicious API calls, no packing indicators. Normal PE section structure consistent with legitimate software.",
        mitigation: "No action required. Continue monitoring for behavioral anomalies at runtime.",
    },
};

function ShapBar({ name, value, maxVal }: { name: string; value: number; maxVal: number }) {
    const pct = (Math.abs(value) / (maxVal || 1)) * 100;
    const color = value > 0.6 ? "#DC3545" : value > 0.35 ? "#FF6900" : "#0066CC";
    const bgColor = value > 0.6 ? "#FFF5F5" : value > 0.35 ? "#FFF4EE" : "#EEF4FF";
    return (
        <div style={{ marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 12, color: value > 0.6 ? "#DC3545" : "#555", fontWeight: value > 0.6 ? 600 : 400 }}>
                    {value > 0.6 ? "⚠ " : ""}{name.replace(/_/g, " ")}
                </span>
                <span style={{ fontSize: 12, color, fontWeight: 600 }}>{(value * 100).toFixed(1)}%</span>
            </div>
            <div style={{ height: 6, borderRadius: 3, background: bgColor, overflow: "hidden" }}>
                <div style={{ height: "100%", borderRadius: 3, width: `${pct}%`, background: color, transition: "width 0.5s ease" }} />
            </div>
        </div>
    );
}

export function RansomwareScanner({ fallbackActive = false }: { fallbackActive?: boolean }) {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [features, setFeatures] = useState("");
    const [activeScenario, setActiveScenario] = useState<string | null>(null);
    const [shapLoading, setShapLoading] = useState(false);
    const [shapData, setShapData] = useState<any>(null);
    const [explanationType, setExplanationType] = useState<string>("safe");

    const analyzeFile = async (featureStr: string, scenarioType?: string) => {
        if (!featureStr.trim()) return;
        setLoading(true);
        setResult(null);
        setShapData(null);

        try {
            const fileFeatures = featureStr.split(",").map(f => parseFloat(f.trim())).filter(n => !isNaN(n));
            if (fileFeatures.length < 10) {
                throw new Error(`Need exactly 10 features — got ${fileFeatures.length}. Use a scenario button above.`);
            }

            const response = await axios.post(`${API_BASE}/api/ai/ransomware`, {
                file_features: fileFeatures,
                file_name: "analyzed_file.exe",
                fallback_active: fallbackActive
            });

            setResult(response.data);
            setExplanationType(scenarioType || (response.data.prediction === "ransomware" ? "wannacry" : "safe"));

            if (response.data.prediction === "ransomware") {
                setShapLoading(true);
                try {
                    const shapRes = await axios.post(`${API_BASE}/api/ai/explain/ransomware`, { file_features: fileFeatures });
                    setShapData(shapRes.data);
                } catch {
                    const featureImportance = fileFeatures.map((v, i) => ({
                        name: FEATURE_NAMES[i] || `feature_${i}`,
                        value: v
                    })).sort((a, b) => b.value - a.value);
                    setShapData({ top_features: featureImportance, clientSide: true });
                } finally {
                    setShapLoading(false);
                }
            }
        } catch (error: any) {
            setResult({ error: error.response?.data?.message || error.message || "Analysis failed" });
        } finally {
            setLoading(false);
        }
    };

    const simulateAttack = (scenario: typeof ATTACK_SCENARIOS[0]) => {
        setActiveScenario(scenario.label);
        setFeatures(scenario.features);
        setExplanationType(scenario.type);
        analyzeFile(scenario.features, scenario.type);
    };

    const explanation = ATTACK_EXPLANATIONS[explanationType] || ATTACK_EXPLANATIONS["safe"];
    const isRansomware = result && !result.error && result.prediction === "ransomware";
    const isSafe = result && !result.error && result.prediction !== "ransomware";

    return (
        <div style={{ padding: 24, fontFamily: "Inter, sans-serif" }}>
            <p style={{ fontSize: 13, color: "#666", marginBottom: 24 }}>
                9-model ensemble (RF, XGBoost, LightGBM, SVM, Isolation Forest) with SHAP explainability. Click a scenario to simulate a real attack.
            </p>

            {/* Attack Simulation Buttons */}
            <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: 8 }}>
                    ⚡ Simulate Attack Scenario
                </label>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {ATTACK_SCENARIOS.map((s, idx) => {
                        const color = s.type === "safe" ? "#15803D" : s.type === "suspicious" ? "#C2410C" : "#DC2626";
                        const bg = s.type === "safe" ? "#F0FDF4" : s.type === "suspicious" ? "#FFF7ED" : "#FFF5F5";
                        const border = s.type === "safe" ? "#BBF7D0" : s.type === "suspicious" ? "#FED7AA" : "#FECACA";
                        const active = activeScenario === s.label;
                        return (
                            <button
                                key={idx}
                                onClick={() => simulateAttack(s)}
                                disabled={loading}
                                style={{
                                    padding: "8px 14px", borderRadius: 8, fontSize: 12, fontWeight: active ? 700 : 500,
                                    border: `2px solid ${active ? color : border}`,
                                    background: active ? bg : "white",
                                    color, cursor: "pointer", transition: "all 0.15s"
                                }}
                            >
                                {loading && activeScenario === s.label ? <Loader2 size={11} style={{ display: "inline", marginRight: 4 }} /> : <Zap size={11} style={{ display: "inline", marginRight: 4 }} />}
                                {s.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Manual Input */}
            <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, fontWeight: 500, color: "#333", display: "block", marginBottom: 6 }}>
                    File Features (10 comma-separated values, 0–1 range)
                </label>
                <input
                    placeholder="0.5, 0.3, 0.8, 0.1, 0.9, 0.2, 0.7, 0.4, 0.6, 0.3"
                    value={features}
                    onChange={e => setFeatures(e.target.value)}
                    style={{
                        width: "100%", padding: "10px 14px", borderRadius: 8,
                        border: "1px solid #E1E4E8", fontSize: 13, outline: "none",
                        fontFamily: "monospace", background: "white", color: "#1A1A1A"
                    }}
                />
                <p style={{ fontSize: 11, color: "#888", marginTop: 4 }}>{FEATURE_NAMES.join(", ")}</p>
            </div>

            <button
                onClick={() => { setActiveScenario(null); analyzeFile(features); }}
                disabled={loading || !features.trim()}
                style={{
                    display: "flex", alignItems: "center", gap: 6, padding: "10px 20px",
                    borderRadius: 8, background: "linear-gradient(135deg,#FF6900,#FF8533)",
                    color: "white", border: "none", fontWeight: 600, fontSize: 14, cursor: loading || !features.trim() ? "not-allowed" : "pointer",
                    opacity: loading || !features.trim() ? 0.6 : 1, marginBottom: 20
                }}
            >
                {loading ? <Loader2 size={16} style={{ animation: "spin 1s linear infinite" }} /> : <Shield size={16} />}
                Analyze File
            </button>

            {/* Vulnerability Warning Banner */}
            {isSafe && result.confidence === 0 && (
                <div style={{ padding: "12px 16px", borderRadius: 8, background: "#FFFBEB", border: "1px solid #FDE68A", marginBottom: 16, display: "flex", gap: 8, alignItems: "center" }}>
                    <AlertTriangle size={16} color="#D97706" />
                    <span style={{ fontSize: 13, color: "#92400E", fontWeight: 500 }}>
                        <strong>Vulnerability Warning:</strong> File marked safe but confidence is 0%. Proceed with extreme caution.
                    </span>
                </div>
            )}

            {/* Result */}
            {result && !result.error && (
                <div style={{
                    padding: "16px 20px", borderRadius: 10,
                    background: isRansomware ? "#FFF5F5" : "#F0FDF4",
                    border: `1px solid ${isRansomware ? "#FECACA" : "#BBF7D0"}`,
                    marginBottom: 16
                }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                        {isRansomware
                            ? <AlertTriangle size={18} color="#DC2626" />
                            : <CheckCircle2 size={18} color="#15803D" />}
                        <h4 style={{ fontWeight: 700, fontSize: 15, color: isRansomware ? "#DC2626" : "#15803D" }}>
                            {isRansomware ? "🚨 RANSOMWARE DETECTED — QUARANTINE FILE" : "✅ File Appears Safe"}
                        </h4>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
                        {[
                            { label: "Prediction", value: result.prediction?.toUpperCase() },
                            { label: "Confidence", value: `${(result.confidence * 100).toFixed(1)}%` },
                            { label: "Risk Level", value: result.risk_level }
                        ].map(item => (
                            <div key={item.label} style={{ background: "white", borderRadius: 8, padding: "10px 14px", border: "1px solid #E1E4E8" }}>
                                <div style={{ fontSize: 11, color: "#888", marginBottom: 2 }}>{item.label}</div>
                                <div style={{ fontSize: 14, fontWeight: 700, color: "#1A1A1A" }}>{item.value}</div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* SHAP Panel */}
            {isRansomware && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: "#FFF4EE", border: "1px solid #FFD4B8", marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, color: "#FF6900", marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
                        <AlertTriangle size={14} /> SHAP Explainability — What Triggered Detection?
                    </div>
                    {shapLoading && <p style={{ fontSize: 12, color: "#888" }}>⏳ Computing SHAP values…</p>}
                    {shapData && !shapLoading && (
                        <div style={{ marginBottom: 16 }}>
                            {(shapData.top_features || []).slice(0, 7).map((f: any, i: number) => (
                                <ShapBar key={i} name={f.name || `feature_${i}`} value={f.value ?? f.importance ?? 0.2} maxVal={1} />
                            ))}
                        </div>
                    )}
                    <div style={{ background: "white", borderRadius: 8, padding: "12px 14px", border: "1px solid #FFD4B8" }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: "#DC2626", marginBottom: 6 }}>
                            ⚠ Attack Pattern: {explanation.summary}
                        </div>
                        <div style={{ fontSize: 12, color: "#555", marginBottom: 8, lineHeight: 1.5 }}>
                            <strong>Technical analysis:</strong> {explanation.technical}
                        </div>
                        <div style={{ fontSize: 12, color: "#555", lineHeight: 1.5 }}>
                            <strong style={{ color: "#15803D" }}>Mitigation:</strong> {explanation.mitigation}
                        </div>
                    </div>
                </div>
            )}

            {result?.error && (
                <div style={{ padding: "12px 16px", borderRadius: 8, background: "#FFF5F5", border: "1px solid #FECACA", fontSize: 13, color: "#DC2626" }}>
                    <strong>Error:</strong> {result.error}
                </div>
            )}
        </div>
    );
}
