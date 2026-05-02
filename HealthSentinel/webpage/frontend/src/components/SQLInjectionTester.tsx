import { useState } from "react";
import axios from "axios";
import { Loader2, Database, AlertTriangle, CheckCircle2, Zap, ShieldAlert } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

const ATTACK_SCENARIOS = [
    { label: "🟢 Safe Query", query: "SELECT patient_id, name FROM patients WHERE department = 'cardiology' ORDER BY name", type: "safe" },
    { label: "🔴 Auth Bypass", query: "SELECT * FROM users WHERE username = 'admin' OR '1'='1' -- AND password = 'x'", type: "auth-bypass" },
    { label: "🔴 UNION Dump", query: "SELECT name FROM products WHERE id = 1 UNION SELECT username, password FROM admin_users --", type: "union-dump" },
    { label: "🔴 Drop Table", query: "'; DROP TABLE patients; INSERT INTO logs VALUES ('deleted'); --", type: "drop-table" },
    { label: "🟡 Data Exfil", query: "SELECT * FROM patient_records WHERE 1=1 AND SLEEP(5) AND (SELECT COUNT(*) FROM information_schema.tables) > 0", type: "data-exfil" },
];

const ATTACK_EXPLANATIONS: Record<string, { summary: string; technical: string; mitigation: string }> = {
    "auth-bypass": { summary: "Authentication Bypass via OR Injection", technical: "The OR '1'='1' clause makes the WHERE condition always true, bypassing login authentication. The -- comment terminates the remaining SQL, ignoring the password check entirely. Classic Tier-1 SQLi.", mitigation: "Use parameterized queries. Implement prepared statements. Deploy WAF with SQL injection ruleset. Enable database activity monitoring." },
    "union-dump": { summary: "UNION-Based Data Extraction Attack", technical: "UNION SELECT appends attacker-controlled query results to legitimate query output. The attacker is attempting to extract admin credentials from a separate table by column count matching with the original query.", mitigation: "Use least-privilege DB accounts. Block UNION statements in WAF. Implement output encoding and column type validation." },
    "drop-table": { summary: "Destructive SQL Injection — Data Destruction", technical: "Stacked queries (`;`) allow execution of multiple SQL statements including DDL commands like DROP TABLE. The attacker terminates the current query and executes DROP TABLE, potentially destroying the entire patient database.", mitigation: "Disable stacked queries in DB driver. Use stored procedures only. Implement regular backups with air-gap. Restrict DDL privileges to DBA accounts only." },
    "data-exfil": { summary: "Blind Time-Based SQL Injection + Schema Enumeration", technical: "SLEEP(5) probes for time-based blind SQLi. The information_schema query maps database structure. This is reconnaissance—the attacker is identifying tables for targeted data extraction.", mitigation: "Set strict query timeout (< 2s). Block SLEEP/BENCHMARK functions. Implement DB firewall to block information_schema access from app accounts." },
    safe: { summary: "Legitimate Database Query", technical: "Standard parameterizable SELECT query with appropriate WHERE clause and ORDER BY. No injection patterns detected. Query structure consistent with normal healthcare application operations.", mitigation: "No action required. Continue monitoring for anomalous query patterns. Consider adding query auditing for PHI access." },
};

/* ───────── Token-level explainability bar ───────── */
interface TokenFeature {
    name: string;
    value: number;
    impact?: string;
}

function ShapBar({ name, value, maxVal }: { name: string; value: number; maxVal: number }) {
    const absVal = Math.abs(value);
    const pct = (absVal / (maxVal || 1)) * 100;
    const isPositive = value >= 0; // positive = contributing towards "injection"
    const color = isPositive
        ? absVal > 0.6 ? "#DC3545" : absVal > 0.35 ? "#FF6900" : "#F59E0B"
        : "#00C851";
    const bg = isPositive
        ? absVal > 0.6 ? "#FFF5F5" : absVal > 0.35 ? "#FFF4EE" : "#FFFBEB"
        : "#EEFFF4";
    return (
        <div style={{ marginBottom: 10 }}>
            <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                <span style={{ fontSize: 12, color: isPositive && absVal > 0.35 ? "#DC3545" : "#555", fontWeight: isPositive && absVal > 0.35 ? 600 : 400 }}>
                    {isPositive && absVal > 0.35 ? "⚠ " : ""}<code style={{ background: isPositive && absVal > 0.35 ? "#FEE2E2" : "#F3F4F6", padding: "1px 5px", borderRadius: 3, fontSize: 12 }}>{name}</code>
                </span>
                <span style={{ fontSize: 12, color, fontWeight: 600 }}>{isPositive ? "+" : "−"}{(absVal * 100).toFixed(1)}%</span>
            </div>
            <div style={{ height: 6, borderRadius: 3, background: bg, overflow: "hidden" }}>
                <div style={{ height: "100%", borderRadius: 3, width: `${Math.min(pct, 100)}%`, background: color, transition: "width 0.5s ease" }} />
            </div>
        </div>
    );
}

/* ───────── Detect attack type from the response details ───────── */
function inferAttackType(details: string, query: string): string {
    const d = (details + " " + query).toLowerCase();
    if (/union\s+(all\s+)?select/i.test(d)) return "union-dump";
    if (/drop\s+table/i.test(d)) return "drop-table";
    if (/sleep|benchmark|waitfor|information_schema/i.test(d)) return "data-exfil";
    if (/or\s+['"]\d['"]\s*=\s*['"]\d/i.test(d) || /or\s+1\s*=\s*1/i.test(d)) return "auth-bypass";
    return "auth-bypass"; // generic injection fallback
}

/* ───────── Main Component ───────── */
export function SQLInjectionTester() {
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [query, setQuery] = useState("");
    const [activeScenario, setActiveScenario] = useState<string | null>(null);
    const [shapData, setShapData] = useState<TokenFeature[]>([]);
    const [explanationType, setExplanationType] = useState<string>("safe");

    const analyzeQuery = async (q: string, type?: string) => {
        if (!q.trim()) return;
        setLoading(true);
        setResult(null);
        setShapData([]);
        try {
            // 1. Detect via CodeBERT (or rule-based fallback on the backend)
            const response = await axios.post(`${API_BASE}/api/ai/sql-injection`, { query: q.trim() });
            const data = response.data;
            setResult(data);

            // 2. Determine explanation type dynamically from the actual result
            const detectedType = type
                || (data.is_injection ? inferAttackType(data.details || "", q) : "safe");
            setExplanationType(detectedType);

            // 3. Fetch real token-level explainability from the backend
            if (data.is_injection || data.risk_level !== "LOW") {
                try {
                    const shapRes = await axios.post(`${API_BASE}/api/ai/explain/sql-injection`, { query: q.trim() });
                    const features: TokenFeature[] = shapRes.data?.top_features || [];
                    if (features.length > 0) {
                        setShapData(features);
                    }
                    // If backend returns empty features, leave shapData empty — no fake data
                } catch (shapErr) {
                    console.warn("SHAP explain endpoint unavailable, no explainability data.", shapErr);
                    // Do NOT fall back to hardcoded data — leave empty
                }
            }
        } catch (error: any) {
            setResult({ error: error.response?.data?.detail || error.response?.data?.message || error.message || "Analysis failed. Is the AI backend running on port 8000?" });
        } finally {
            setLoading(false);
        }
    };

    const simulateAttack = (scenario: typeof ATTACK_SCENARIOS[0]) => {
        setActiveScenario(scenario.label);
        setQuery(scenario.query);
        setExplanationType(scenario.type);
        analyzeQuery(scenario.query, scenario.type);
    };

    const explanation = ATTACK_EXPLANATIONS[explanationType] || ATTACK_EXPLANATIONS["safe"];
    const isInjection = result && !result.error && result.is_injection;
    const isSafe = result && !result.error && !result.is_injection;

    // Compute max SHAP value for normalization
    const maxShapVal = shapData.length > 0
        ? Math.max(...shapData.map(f => Math.abs(f.value)), 0.01)
        : 1;

    return (
        <div style={{ padding: 24, fontFamily: "Inter, sans-serif" }}>
            <p style={{ fontSize: 13, color: "#666", marginBottom: 24 }}>
                CodeBERT fine-tuned model (99.91% accuracy) + rule-based fallback. Token-level attention weights explain each injection pattern detected.
            </p>

            {/* Attack Scenarios */}
            <div style={{ marginBottom: 20 }}>
                <label style={{ fontSize: 11, fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em", display: "block", marginBottom: 8 }}>
                    ⚡ Simulate Attack Scenario
                </label>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {ATTACK_SCENARIOS.map((s, idx) => {
                        const color = s.type === "safe" ? "#15803D" : s.type === "data-exfil" ? "#C2410C" : "#DC2626";
                        const bg = s.type === "safe" ? "#F0FDF4" : s.type === "data-exfil" ? "#FFF7ED" : "#FFF5F5";
                        const border = s.type === "safe" ? "#BBF7D0" : s.type === "data-exfil" ? "#FED7AA" : "#FECACA";
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

            {/* Query Input */}
            <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 13, fontWeight: 500, color: "#333", display: "block", marginBottom: 5 }}>SQL Query</label>
                <textarea
                    placeholder="SELECT * FROM patients WHERE id = 1"
                    rows={4} value={query}
                    onChange={e => setQuery(e.target.value)}
                    style={{ width: "100%", padding: "10px 14px", borderRadius: 8, border: "1px solid #E1E4E8", fontSize: 13, outline: "none", background: "white", color: "#1A1A1A", fontFamily: "monospace", resize: "vertical" }}
                />
            </div>

            <button onClick={() => { setActiveScenario(null); analyzeQuery(query); }}
                disabled={loading || !query.trim()}
                style={{ display: "flex", alignItems: "center", gap: 6, padding: "10px 20px", borderRadius: 8, background: "linear-gradient(135deg,#00C851,#00A843)", color: "white", border: "none", fontWeight: 600, fontSize: 14, cursor: loading || !query.trim() ? "not-allowed" : "pointer", opacity: loading || !query.trim() ? 0.6 : 1, marginBottom: 20 }}>
                {loading ? <Loader2 size={16} /> : <Database size={16} />}
                Analyze Query
            </button>

            {/* Result */}
            {result && !result.error && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: isInjection ? "#FFF5F5" : "#F0FDF4", border: `1px solid ${isInjection ? "#FECACA" : "#BBF7D0"}`, marginBottom: 16 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                        {isInjection ? <ShieldAlert size={18} color="#DC2626" /> : <CheckCircle2 size={18} color="#15803D" />}
                        <h4 style={{ fontWeight: 700, fontSize: 15, color: isInjection ? "#DC2626" : "#15803D" }}>
                            {isInjection ? "🚨 SQL INJECTION DETECTED — QUERY BLOCKED" : "✅ Query Appears Safe — ALLOW"}
                        </h4>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12, marginBottom: 12 }}>
                        {[{ label: "Action", value: isInjection ? "BLOCK" : "ALLOW" }, { label: "Risk Level", value: result.risk_level }, { label: "Confidence", value: `${(result.confidence * 100).toFixed(1)}%` }].map(item => (
                            <div key={item.label} style={{ background: "white", borderRadius: 8, padding: "10px 14px", border: "1px solid #E1E4E8" }}>
                                <div style={{ fontSize: 11, color: "#888", marginBottom: 2 }}>{item.label}</div>
                                <div style={{ fontSize: 14, fontWeight: 700, color: item.label === "Action" ? (isInjection ? "#DC2626" : "#15803D") : "#1A1A1A" }}>{item.value}</div>
                            </div>
                        ))}
                    </div>
                    {result.details && <p style={{ fontSize: 12, color: "#555", fontFamily: "monospace" }}>{result.details}</p>}
                </div>
            )}

            {/* SHAP Token Explainability Panel — only when we have real data */}
            {isInjection && shapData.length > 0 && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: "#FFF4EE", border: "1px solid #FFD4B8", marginBottom: 16 }}>
                    <div style={{ fontWeight: 600, fontSize: 13, color: "#FF6900", marginBottom: 12, display: "flex", alignItems: "center", gap: 6 }}>
                        <AlertTriangle size={14} /> Token-Level Explainability — Malicious Tokens Highlighted
                    </div>
                    <div style={{ marginBottom: 16 }}>
                        {shapData.slice(0, 7).map((f: TokenFeature, i: number) => (
                            <ShapBar key={i} name={f.name || `token_${i}`} value={f.value ?? 0} maxVal={maxShapVal} />
                        ))}
                    </div>
                    <div style={{ background: "white", borderRadius: 8, padding: "12px 14px", border: "1px solid #FFD4B8" }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: "#DC2626", marginBottom: 6 }}>⚠ Attack Pattern: {explanation.summary}</div>
                        <div style={{ fontSize: 12, color: "#555", marginBottom: 8, lineHeight: 1.5 }}><strong>Technical:</strong> {explanation.technical}</div>
                        <div style={{ fontSize: 12, color: "#555", lineHeight: 1.5 }}><strong style={{ color: "#15803D" }}>Mitigation:</strong> {explanation.mitigation}</div>
                    </div>
                </div>
            )}

            {/* Safe query — show green explainability panel */}
            {isSafe && (
                <div style={{ padding: "16px 20px", borderRadius: 10, background: "#F0FDF4", border: "1px solid #BBF7D0", marginBottom: 16 }}>
                    <div style={{ background: "white", borderRadius: 8, padding: "12px 14px", border: "1px solid #BBF7D0" }}>
                        <div style={{ fontSize: 12, fontWeight: 700, color: "#15803D", marginBottom: 6 }}>✅ {explanation.summary}</div>
                        <div style={{ fontSize: 12, color: "#555", marginBottom: 8, lineHeight: 1.5 }}><strong>Analysis:</strong> {explanation.technical}</div>
                        <div style={{ fontSize: 12, color: "#555", lineHeight: 1.5 }}><strong style={{ color: "#15803D" }}>Recommendation:</strong> {explanation.mitigation}</div>
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
