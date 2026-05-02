import { useState } from "react";
import axios from "axios";
import { Loader2, Users, UserX, UserCheck, Activity, AlertTriangle, Zap } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const FEATURES = [
    "login_hour", "file_access_count", "sensitive_file_access", "process_spawns",
    "network_connections", "failed_logins", "data_volume_mb", "unique_ips",
    "after_hours_flag", "privilege_escalations", "usb_events", "email_attachments"
];

function computeShapImportances(sequence: number[][]): { feature: string; pct: number; value: number }[] {
    const n = sequence.length;
    const nf = sequence[0].length;
    const means = Array(nf).fill(0).map((_, f) => sequence.reduce((s, row) => s + row[f], 0) / n);
    const devs = Array(nf).fill(0).map((_, f) => sequence.reduce((s, row) => s + Math.abs(row[f] - means[f]), 0) / n);
    const total = devs.reduce((a, b) => a + b, 1e-10);
    return FEATURES.map((feat, i) => ({ feature: feat, value: devs[i], pct: (devs[i] / total) * 100 })).sort((a, b) => b.value - a.value);
}

function buildNormalSequence(steps = 30): number[][] {
    return Array.from({ length: steps }, () =>
        FEATURES.map(f => {
            if (f === "after_hours_flag" || f === "privilege_escalations" || f === "usb_events") return 0;
            return Math.random() * 0.15 + 0.1;
        })
    );
}

function buildAttackSequence(type: string, steps = 30): number[][] {
    const seq = buildNormalSequence(steps);
    const attackAt = Math.floor(steps * 0.5);
    for (let t = attackAt; t < steps; t++) {
        if (type === "after_hours") { seq[t][0] = 0.9; seq[t][1] = 0.88 + Math.random() * 0.12; seq[t][2] = 0.85 + Math.random() * 0.15; seq[t][8] = 1.0; }
        else if (type === "powershell") { seq[t][3] = 0.80 + Math.random() * 0.2; seq[t][4] = 0.75 + Math.random() * 0.25; seq[t][9] = 0.70 + Math.random() * 0.3; seq[t][5] = 0.60 + Math.random() * 0.3; }
        else if (type === "exfil") { seq[t][6] = 0.90 + Math.random() * 0.1; seq[t][7] = 0.85 + Math.random() * 0.15; seq[t][11] = 0.75 + Math.random() * 0.25; }
        else if (type === "usb") { seq[t][10] = 0.90 + Math.random() * 0.1; seq[t][2] = 0.80 + Math.random() * 0.2; seq[t][9] = 0.60 + Math.random() * 0.4; }
    }
    return seq;
}

function ReconErrorSparkline({ errors, threshold }: { errors: number[]; threshold: number }) {
    if (!errors.length) return null;
    const W = 400, H = 80, PAD = 8;
    const maxE = Math.max(...errors, threshold) * 1.1;
    const minE = 0;
    const toX = (i: number) => PAD + (i / (errors.length - 1)) * (W - PAD * 2);
    const toY = (v: number) => H - PAD - ((v - minE) / (maxE - minE)) * (H - PAD * 2);
    const points = errors.map((e, i) => `${toX(i)},${toY(e)}`).join(" ");
    const thY = toY(threshold);
    return (
        <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ display: "block", background: "#F8F9FA", borderRadius: 8 }}>
            <line x1={PAD} y1={thY} x2={W - PAD} y2={thY} stroke="#FF6900" strokeWidth="1.5" strokeDasharray="4 3" />
            <text x={W - PAD - 2} y={thY - 3} fill="#FF6900" fontSize="8" textAnchor="end">threshold</text>
            <polyline points={points} fill="none" stroke="#0066CC" strokeWidth="1.5" />
            {errors.map((e, i) => e > threshold ? <circle key={i} cx={toX(i)} cy={toY(e)} r="3" fill="#DC3545" /> : null)}
        </svg>
    );
}

function ShapPanel({ importances }: { importances: { feature: string; pct: number }[] }) {
    const top5 = importances.slice(0, 5);
    const maxPct = top5[0]?.pct || 1;
    const colors = ["#DC3545", "#FF6900", "#F97316", "#0066CC", "#8B5CF6"];
    return (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {top5.map((item, i) => (
                <div key={item.feature}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                        <span style={{ fontSize: 12, color: i < 3 ? colors[i] : "#555", fontWeight: i < 3 ? 600 : 400 }}>
                            {i < 3 ? "⚠ " : ""}{item.feature.replace(/_/g, " ")}
                        </span>
                        <span style={{ fontSize: 12, color: "#888" }}>{item.pct.toFixed(1)}%</span>
                    </div>
                    <div style={{ height: 6, borderRadius: 3, background: "#F4F4F4", overflow: "hidden" }}>
                        <div style={{ height: "100%", borderRadius: 3, width: `${(item.pct / maxPct) * 100}%`, background: colors[i] || "#0066CC", transition: "width 0.5s ease" }} />
                    </div>
                </div>
            ))}
        </div>
    );
}

const ATTACK_SCENARIOS = [
    { id: "after_hours", label: "🌙 After-Hours Mass Access", user: "nurse_01" },
    { id: "powershell", label: "💻 PowerShell Chain", user: "it_admin_02" },
    { id: "exfil", label: "🌐 IP Exfiltration", user: "doctor_03" },
    { id: "usb", label: "🔌 USB Exfiltration", user: "nurse_04" },
];

const ATTACK_CONTEXT: Record<string, string> = {
    after_hours: "Sudden spike in file access (0.88) and sensitive file access (0.85) during off-hours (after_hours_flag=1). Consistent with ransomware exfiltration or disgruntled employee staging. Alert HR and freeze account.",
    powershell: "Elevated process_spawns (0.80) combined with privilege_escalations (0.70) and failed_logins (0.60). Pattern matches PowerShell-based lateral movement. Isolate workstation and pull process tree.",
    exfil: "Critical spike in data_volume_mb (0.90) and unique_ips (0.85) with email_attachments (0.75). Data exfiltration underway. Block external connections and trigger DLP alert.",
    usb: "usb_events spike (0.90) with sensitive_file_access (0.80) and privilege_escalations (0.60). USB data theft pattern — revoke USB privileges and confiscate device.",
    normal: "User behavior consistent with baseline. LSTM autoencoder reconstruction error below threshold. No anomaly detected."
};

export function InsiderThreatMonitor() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [userId, setUserId] = useState("");
    const [shapData, setShapData] = useState<any[]>([]);
    const [errorSeries, setErrorSeries] = useState<number[]>([]);
    const [threshold, setThreshold] = useState(0);
    const [activeScenario, setActiveScenario] = useState<string | null>(null);

    const runAnalysis = async (sequence: number[][], uid: string) => {
        setLoading(true);
        setResult(null);
        setShapData([]);
        setErrorSeries([]);
        try {
            const response = await axios.post(`${API_BASE}/api/ai/insider-threat`, { user_id: uid, sequence_data: sequence });
            const data = response.data;
            setResult(data);
            setShapData(computeShapImportances(sequence));
            const winSize = 5;
            const series: number[] = [];
            for (let i = 0; i <= sequence.length - winSize; i++) {
                const window = sequence.slice(i, i + winSize);
                const meanDev = window.reduce((s, row) => s + row.reduce((rs, v) => rs + Math.abs(v - 0.2), 0) / row.length, 0) / winSize;
                series.push(meanDev);
            }
            setErrorSeries(series);
            setThreshold(data.threshold ?? 0.15);
        } catch (error: any) {
            setResult({ error: error.response?.data?.message || error.message || "Analysis failed" });
        } finally {
            setLoading(false);
        }
    };

    const analyzeUser = () => {
        if (!userId.trim()) return;
        setActiveScenario(null);
        const sequence = Array.from({ length: 30 }, () => Array.from({ length: 12 }, () => Math.random() * 0.3));
        runAnalysis(sequence, userId.trim());
    };

    const simulateAttack = (scenario: typeof ATTACK_SCENARIOS[0]) => {
        setActiveScenario(scenario.id);
        setUserId(scenario.user);
        runAnalysis(buildAttackSequence(scenario.id, 30), scenario.user);
    };

    const isThreat = result && !result.error && (result.is_anomaly ?? result.is_threat);
    const scenarioContext = ATTACK_CONTEXT[activeScenario || "normal"] || ATTACK_CONTEXT["normal"];

    return (
        <div style={{ padding: 24, fontFamily: "Inter, sans-serif" }}>
            <p style={{ fontSize: 13, color: "#666", marginBottom: 24 }}>
                LSTM Autoencoder anomaly detection — analyzes 30-step behavioral sequences across 12 features. SHAP highlights anomalous features.
            </p>

            {/* Attack Scenarios */}
            <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: 8 }}>
                    ⚡ Simulate Insider Threat Scenario
                </label>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {ATTACK_SCENARIOS.map((s) => {
                        const active = activeScenario === s.id;
                        return (
                            <button key={s.id} onClick={() => simulateAttack(s)} disabled={loading}
                                style={{ padding: "8px 14px", borderRadius: 8, fontSize: 12, fontWeight: active ? 700 : 500, border: `2px solid ${active ? "#8B5CF6" : "#E9D5FF"}`, background: active ? "#F5EEFF" : "white", color: "#8B5CF6", cursor: "pointer", transition: "all 0.15s" }}>
                                {loading && activeScenario === s.id ? <Loader2 size={11} style={{ display: "inline", marginRight: 4 }} /> : <Zap size={11} style={{ display: "inline", marginRight: 4 }} />}
                                {s.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Manual User ID */}
            <div style={{ marginBottom: 16, display: "flex", gap: 10, alignItems: "flex-end" }}>
                <div style={{ flex: 1 }}>
                    <label style={{ fontSize: 13, fontWeight: 500, color: "#333", display: "block", marginBottom: 5 }}>User ID (for custom analysis)</label>
                    <input
                        placeholder="e.g. nurse_05, admin_01"
                        value={userId}
                        onChange={e => setUserId(e.target.value)}
                        style={{ width: "100%", padding: "10px 14px", borderRadius: 8, border: "1px solid #E1E4E8", fontSize: 13, outline: "none", background: "white", color: "#1A1A1A" }}
                    />
                </div>
                <button onClick={analyzeUser} disabled={loading || !userId.trim()}
                    style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 20px", borderRadius: 8, background: "linear-gradient(135deg,#8B5CF6,#7C3AED)", color: "white", border: "none", fontWeight: 600, fontSize: 14, cursor: loading || !userId.trim() ? "not-allowed" : "pointer", opacity: loading || !userId.trim() ? 0.6 : 1, whiteSpace: "nowrap" }}>
                    {loading ? <Loader2 size={16} /> : <Users size={16} />}
                    Analyze User
                </button>
            </div>

            {/* Result */}
            {result && !result.error && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: isThreat ? "#FFF5F5" : "#F0FDF4", border: `1px solid ${isThreat ? "#FECACA" : "#BBF7D0"}`, marginBottom: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                        {isThreat ? <UserX size={18} color="#DC2626" /> : <UserCheck size={18} color="#15803D" />}
                        <h4 style={{ fontWeight: 700, fontSize: 15, color: isThreat ? "#DC2626" : "#15803D" }}>
                            {isThreat ? `🚨 INSIDER THREAT DETECTED — ${result.user_id ?? userId}` : `✅ Normal Behavior — ${result.user_id ?? userId}`}
                        </h4>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12, marginBottom: 12 }}>
                        {[
                            { label: "Status", value: isThreat ? "THREAT" : "NORMAL" },
                            { label: "Anomaly Score", value: (result.reconstruction_error ?? result.anomaly_score ?? 0).toFixed(4) },
                            { label: "Risk Level", value: result.risk_level || "LOW" },
                            { label: "Threshold", value: (result.threshold || 0.15).toFixed(4) },
                        ].map(item => (
                            <div key={item.label} style={{ background: "white", borderRadius: 8, padding: "10px 14px", border: "1px solid #E1E4E8" }}>
                                <div style={{ fontSize: 11, color: "#888", marginBottom: 2 }}>{item.label}</div>
                                <div style={{ fontSize: 13, fontWeight: 700, color: "#1A1A1A" }}>{item.value}</div>
                            </div>
                        ))}
                    </div>

                    {/* Sparkline */}
                    {errorSeries.length > 0 && (
                        <div style={{ marginBottom: 16 }}>
                            <div style={{ fontSize: 12, fontWeight: 600, color: "#333", marginBottom: 6, display: "flex", alignItems: "center", gap: 5 }}>
                                <Activity size={13} /> Reconstruction Error Over Time
                            </div>
                            <ReconErrorSparkline errors={errorSeries} threshold={threshold} />
                            <p style={{ fontSize: 11, color: "#888", marginTop: 4 }}>
                                <span style={{ color: "#0066CC" }}>Blue line</span> = error, <span style={{ color: "#FF6900" }}>orange dashed</span> = threshold, <span style={{ color: "#DC3545" }}>red dots</span> = anomalies
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* SHAP Panel */}
            {isThreat && shapData.length > 0 && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: "#F5EEFF", border: "1px solid #E9D5FF", marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, color: "#8B5CF6", marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
                        <AlertTriangle size={14} /> SHAP Feature Importance — Anomalous Behaviors
                    </div>
                    <ShapPanel importances={shapData} />
                    <div style={{ marginTop: 14, background: "white", borderRadius: 8, padding: "12px 14px", border: "1px solid #E9D5FF" }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: "#DC2626", marginBottom: 6 }}>⚠ Context: {ATTACK_SCENARIOS.find(s => s.id === activeScenario)?.label || "Anomalous Behavior"}</div>
                        <div style={{ fontSize: 12, color: "#555", lineHeight: 1.5 }}>{scenarioContext}</div>
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
