import { useState } from "react";
import axios from "axios";
import { Loader2, Mail, ShieldAlert, ShieldCheck, AlertTriangle, Zap } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const ATTACK_SCENARIOS = [
    { label: "🟢 Safe Email", sender: "newsletter@hospital.org", subject: "Monthly Staff Newsletter - March 2025", message: "Hello team, please find our monthly newsletter with updates on upcoming training sessions and team events. No action needed.", type: "safe" },
    { label: "🔴 Credential Phish", sender: "security@payroll-verify.xyz", subject: "URGENT: Your payroll account will be suspended in 24 hours", message: "Your healthcare payroll account requires immediate verification. Click here http://bit.ly/payroll-urgent123 to prevent account suspension. Enter your hospital ID and password to verify.", type: "credential" },
    { label: "🔴 CEO Fraud", sender: "ceo-office@hospital-corp.net", subject: "Urgent wire transfer request", message: "This is urgent. I need you to process a wire transfer of $45,000 to a new vendor immediately. Do not discuss with anyone. Reply with confirmation. Time sensitive.", type: "ceo-fraud" },
    { label: "🟡 Invoice Scam", sender: "billing@med-supply-invoice.co", subject: "Invoice #INV-2025-8847 requires payment", message: "Please find attached invoice for medical supplies. Payment is overdue. Please click login to approve payment and avoid service interruption.", type: "invoice" },
];

const ATTACK_EXPLANATIONS: Record<string, { summary: string; technical: string; mitigation: string }> = {
    credential: { summary: "Credential Harvesting Phishing Attack", technical: "Fake urgency ('suspended in 24 hours'), suspicious sender domain (.xyz), and URL shortener (bit.ly) are hallmark credential phishing signals. The request for hospital ID + password confirms data-theft intent.", mitigation: "Block sender domain. Never follow shortened URLs from emails. Enable MFA. Report to IT security team within 1 hour." },
    "ceo-fraud": { summary: "CEO/BEC (Business Email Compromise) Fraud", technical: "Business Email Compromise spoofs executive authority with urgency + secrecy. 'Do not discuss with anyone' and wire transfer request are classic BEC patterns. Sender domain mimics legitimate hospital domain.", mitigation: "Verify wire transfers via phone call to known number. Implement dual-approval policy for transfers. Flag domain lookalikes in email gateway." },
    invoice: { summary: "Fake Invoice / Billing Scam", technical: "Pretexts as a known vendor with overdue invoice. 'Click to approve payment' leads to credential harvesting or malware. Suspicious billing domain (.co suffix impersonating .com).", mitigation: "Verify invoices against purchase orders. Never log in via email links — go directly to vendor portal. Block payment approval via email." },
    safe: { summary: "Legitimate Internal Communication", technical: "Sender matches known hospital domain (@hospital.org). No URLs, no urgency language, no credential requests, no financial action items. Content matches typical newsletter format.", mitigation: "No action required. This email pattern is consistent with legitimate internal communications." },
};

// SHAP scores are now fetched from the backend for consistency.

function ShapBar({ name, value, impact }: { name: string; value: number; impact: string }) {
    // SHAP values can be large; we normalize for display (0.1 impact = 40% bar, 0.4+ = 100%)
    const displayScore = Math.min(1, Math.abs(value) * 2.5);
    const isHighRisk = impact === "positive" && displayScore > 0.5;
    
    const color = impact === "positive" ? (displayScore > 0.6 ? "#DC3545" : "#FF6900") : "#0066CC";
    const bg = impact === "positive" ? (displayScore > 0.6 ? "#FFF5F5" : "#FFF4EE") : "#EEF4FF";
    
    return (
        <div style={{ marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 12, color: isHighRisk ? "#DC3545" : "#555", fontWeight: isHighRisk ? 600 : 400 }}>
                    {isHighRisk ? "⚠ " : ""}{name.replace(/_/g, " ")}
                </span>
                <span style={{ fontSize: 12, color, fontWeight: 600 }}>
                    {impact === "positive" ? "+" : "-"}{Math.abs(value).toFixed(3)}
                </span>
            </div>
            <div style={{ height: 6, borderRadius: 3, background: bg, overflow: "hidden" }}>
                <div style={{ height: "100%", borderRadius: 3, width: `${displayScore * 100}%`, background: color, transition: "width 0.5s ease" }} />
            </div>
        </div>
    );
}

export function PhishingAnalyzer() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [emailData, setEmailData] = useState({ sender: "", subject: "", message: "" });
    const [activeScenario, setActiveScenario] = useState<string | null>(null);
    const [shapData, setShapData] = useState<any[]>([]);
    const [explanationType, setExplanationType] = useState<string>("safe");

    const analyzeEmail = async (data: typeof emailData, type?: string) => {
        setLoading(true);
        setResult(null);
        setShapData([]);
        try {
            const urls = data.message.match(/(https?:\/\/[^\s]+)/g) || [];
            const response = await axios.post(`${API_BASE}/api/ai/phishing`, { ...data, urls });
            setResult(response.data);
            setExplanationType(type || (response.data.action !== "ALLOW" ? "credential" : "safe"));
            
            // Map backend SHAP data
            if (response.data.explain_data?.top_features) {
                setShapData(response.data.explain_data.top_features);
            }
        } catch (error: any) {
            setResult({ error: error.response?.data?.message || error.message || "Analysis failed" });
        } finally {
            setLoading(false);
        }
    };

    const simulateAttack = (scenario: typeof ATTACK_SCENARIOS[0]) => {
        setActiveScenario(scenario.label);
        setExplanationType(scenario.type);
        const data = { sender: scenario.sender, subject: scenario.subject, message: scenario.message };
        setEmailData(data);
        analyzeEmail(data, scenario.type);
    };

    const explanation = ATTACK_EXPLANATIONS[explanationType] || ATTACK_EXPLANATIONS["safe"];
    const isBlocked = result && !result.error && result.action !== "ALLOW";
    const isQuarantine = result && !result.error && result.action === "QUARANTINE";

    const resultColor = result?.action === "BLOCK" ? "#DC2626" : result?.action === "QUARANTINE" ? "#C2410C" : "#15803D";
    const resultBg = result?.action === "BLOCK" ? "#FFF5F5" : result?.action === "QUARANTINE" ? "#FFF7ED" : "#F0FDF4";
    const resultBorder = result?.action === "BLOCK" ? "#FECACA" : result?.action === "QUARANTINE" ? "#FED7AA" : "#BBF7D0";

    return (
        <div style={{ padding: 24, fontFamily: "Inter, sans-serif" }}>
            <p style={{ fontSize: 13, color: "#666", marginBottom: 24 }}>
                XGBoost ML model + Zero-Day anomaly detection + OpenPhish database. SHAP explains every verdict.
            </p>

            {/* Attack Scenario Buttons */}
            <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: 8 }}>
                    ⚡ Simulate Attack Scenario
                </label>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {ATTACK_SCENARIOS.map((s, idx) => {
                        const color = s.type === "safe" ? "#15803D" : s.type === "invoice" ? "#C2410C" : "#DC2626";
                        const bg = s.type === "safe" ? "#F0FDF4" : s.type === "invoice" ? "#FFF7ED" : "#FFF5F5";
                        const border = s.type === "safe" ? "#BBF7D0" : s.type === "invoice" ? "#FED7AA" : "#FECACA";
                        const active = activeScenario === s.label;
                        return (
                            <button key={idx} onClick={() => simulateAttack(s)} disabled={loading}
                                style={{ padding: "8px 14px", borderRadius: 8, fontSize: 12, fontWeight: active ? 700 : 500, border: `2px solid ${active ? color : border}`, background: active ? bg : "white", color, cursor: "pointer", transition: "all 0.15s" }}>
                                {loading && activeScenario === s.label ? <Loader2 size={11} style={{ display: "inline", marginRight: 4 }} /> : <Zap size={11} style={{ display: "inline", marginRight: 4 }} />}
                                {s.label}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Form Fields */}
            {([
                { id: "sender", label: "Sender Email", placeholder: "sender@example.com", value: emailData.sender, onChange: (v: string) => setEmailData({ ...emailData, sender: v }) },
                { id: "subject", label: "Subject", placeholder: "Email subject line", value: emailData.subject, onChange: (v: string) => setEmailData({ ...emailData, subject: v }) },
            ] as const).map(field => (
                <div key={field.id} style={{ marginBottom: 12 }}>
                    <label style={{ fontSize: 13, fontWeight: 500, color: "#333", display: "block", marginBottom: 5 }}>{field.label}</label>
                    <input placeholder={field.placeholder} value={field.value} onChange={e => field.onChange(e.target.value)}
                        style={{ width: "100%", padding: "10px 14px", borderRadius: 8, border: "1px solid #E1E4E8", fontSize: 13, outline: "none", background: "white", color: "#1A1A1A" }} />
                </div>
            ))}
            <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, fontWeight: 500, color: "#333", display: "block", marginBottom: 5 }}>Message Body</label>
                <textarea placeholder="Email message content..." rows={4} value={emailData.message}
                    onChange={e => setEmailData({ ...emailData, message: e.target.value })}
                    style={{ width: "100%", padding: "10px 14px", borderRadius: 8, border: "1px solid #E1E4E8", fontSize: 13, outline: "none", background: "white", color: "#1A1A1A", resize: "vertical" }} />
            </div>

            <button onClick={() => { setActiveScenario(null); analyzeEmail(emailData); }}
                disabled={loading || !emailData.sender || !emailData.subject || !emailData.message}
                style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 20px", borderRadius: 8, background: "linear-gradient(135deg,#0066CC,#0052A3)", color: "white", border: "none", fontWeight: 600, fontSize: 14, cursor: loading || !emailData.sender ? "not-allowed" : "pointer", opacity: loading || !emailData.sender ? 0.6 : 1, marginBottom: 20 }}>
                {loading ? <Loader2 size={16} /> : <Mail size={16} />}
                Analyze Email
            </button>

            {/* Result */}
            {result && !result.error && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: resultBg, border: `1px solid ${resultBorder}`, marginBottom: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                        {result.action === "BLOCK" ? <ShieldAlert size={18} color={resultColor} /> : result.action === "QUARANTINE" ? <AlertTriangle size={18} color={resultColor} /> : <ShieldCheck size={18} color={resultColor} />}
                        <h4 style={{ fontWeight: 700, fontSize: 15, color: resultColor }}>{result.user_message}</h4>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 12 }}>
                        {[{ label: "Action", value: result.action }, { label: "Risk Level", value: result.risk_level }, { label: "Confidence", value: `${(result.confidence * 100).toFixed(1)}%` }].map(item => (
                            <div key={item.label} style={{ background: "white", borderRadius: 8, padding: "10px 14px", border: "1px solid #E1E4E8" }}>
                                <div style={{ fontSize: 11, color: "#888", marginBottom: 2 }}>{item.label}</div>
                                <div style={{ fontSize: 14, fontWeight: 700, color: "#1A1A1A" }}>{item.value}</div>
                            </div>
                        ))}
                    </div>
                    {result.reasons?.length > 0 && (
                        <div>
                            <div style={{ fontSize: 12, fontWeight: 600, color: "#555", marginBottom: 6 }}>Detection Signals:</div>
                            <ul style={{ paddingLeft: 16, margin: 0 }}>
                                {result.reasons.map((r: string, i: number) => <li key={i} style={{ fontSize: 12, color: "#555", marginBottom: 3 }}>{r}</li>)}
                            </ul>
                        </div>
                    )}
                </div>
            )}

            {/* SHAP Panel */}
            {result && !result.error && shapData.length > 0 && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: isBlocked ? "#FFF4EE" : "#F0FDF4", border: `1px solid ${isBlocked ? "#FFD4B8" : "#BBF7D0"}`, marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, color: isBlocked ? "#FF6900" : "#15803D", marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
                        <AlertTriangle size={14} /> SHAP Explainability — Why Was This Email {result.action === "ALLOW" ? "Allowed" : "Blocked"}?
                    </div>
                    <div style={{ marginBottom: 16 }}>
                        {shapData.slice(0, 6).map((f, i) => <ShapBar key={i} name={f.name} value={f.value} impact={f.impact} />)}
                    </div>
                    <div style={{ background: "white", borderRadius: 8, padding: "12px 14px", border: "1px solid #E1E4E8" }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: isBlocked ? "#DC2626" : "#15803D", marginBottom: 6 }}>
                            {isBlocked ? "⚠" : "✅"} {explanation.summary}
                        </div>
                        <div style={{ fontSize: 12, color: "#555", marginBottom: 8, lineHeight: 1.5 }}><strong>Technical:</strong> {explanation.technical}</div>
                        <div style={{ fontSize: 12, color: "#555", lineHeight: 1.5 }}><strong style={{ color: "#15803D" }}>Response:</strong> {explanation.mitigation}</div>
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
