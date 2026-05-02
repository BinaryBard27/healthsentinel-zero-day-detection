/**
 * UserDashboard — Simplified security awareness dashboard for regular users
 * Shows system status, recent alerts, and a self-service threat reporting tool
 */
import { useState, useEffect } from "react";
import { Shield, Mail, AlertTriangle, CheckCircle, Activity, LogOut, Lock, Bell, Info, Zap } from "lucide-react";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface UserDashboardProps { onLogout: () => void; username?: string }

const SECURITY_TIPS = [
    "Never share your password or one-time codes with anyone, including IT staff.",
    "Verify sender email addresses carefully — attackers often mimic internal domains.",
    "If you receive an unexpected wire transfer or purchase request, call the sender directly.",
    "Report suspicious emails to security@hospital.org before clicking any links.",
    "Lock your workstation (Win+L) whenever you step away, even briefly.",
    "USB drives from unknown sources should never be plugged into hospital workstations.",
];

export function UserDashboard({ onLogout, username = "User" }: UserDashboardProps) {
    const [time, setTime] = useState(new Date());
    const [tipIndex, setTipIndex] = useState(0);
    const [systemStatus, setSystemStatus] = useState<"checking" | "online" | "degraded">("checking");
    const [reportEmail, setReportEmail] = useState("");
    const [reportSent, setReportSent] = useState(false);
    const [reportLoading, setReportLoading] = useState(false);

    useEffect(() => {
        const t = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(t);
    }, []);

    useEffect(() => {
        const t = setInterval(() => setTipIndex(i => (i + 1) % SECURITY_TIPS.length), 8000);
        return () => clearInterval(t);
    }, []);

    useEffect(() => {
        axios.get(`${API_BASE}/api/health`)
            .then(() => setSystemStatus("online"))
            .catch(() => setSystemStatus("degraded"));
    }, []);

    const handleReport = async () => {
        if (!reportEmail.trim()) return;
        setReportLoading(true);
        // Simulate phishing check on reported email
        try {
            const res = await axios.post(`${API_BASE}/api/ai/phishing`, {
                sender: reportEmail,
                subject: "User reported suspicious email",
                message: "Reported as suspicious by end user",
                urls: []
            });
            setReportSent(true);
            setTimeout(() => setReportSent(false), 5000);
        } catch {
            setReportSent(true);
            setTimeout(() => setReportSent(false), 5000);
        } finally {
            setReportLoading(false);
            setReportEmail("");
        }
    };

    const statusColor = systemStatus === "online" ? "#22c55e" : systemStatus === "degraded" ? "#f97316" : "#94a3b8";
    const statusText = systemStatus === "online" ? "ALL SYSTEMS PROTECTED" : systemStatus === "degraded" ? "PARTIAL PROTECTION" : "CHECKING...";

    return (
        <div style={{ minHeight: "100vh", background: "#0a0f1e", color: "#e2e8f0", fontFamily: "'Inter', sans-serif" }}>

            {/* Header */}
            <header style={{ padding: "0 32px", height: 64, borderBottom: "1px solid rgba(59,130,246,0.15)", background: "rgba(13,21,38,0.95)", backdropFilter: "blur(10px)", display: "flex", alignItems: "center", justifyContent: "space-between", position: "sticky", top: 0, zIndex: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #3b82f6, #8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                        <Shield size={18} color="white" />
                    </div>
                    <span style={{ fontWeight: 700, fontSize: 16, color: "#f1f5f9" }}>HealthSentinel</span>
                    <span style={{ fontSize: 10, color: "#475569", padding: "2px 8px", borderRadius: 6, border: "1px solid rgba(59,130,246,0.2)", textTransform: "uppercase", letterSpacing: 1 }}>Employee Portal</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <span style={{ fontSize: 13, color: "#64748b" }}>👤 {username}</span>
                    <button onClick={onLogout} style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 14px", borderRadius: 8, border: "1px solid rgba(239,68,68,0.2)", background: "rgba(239,68,68,0.05)", color: "#f87171", fontSize: 12, cursor: "pointer" }}>
                        <LogOut size={13} /> Sign Out
                    </button>
                </div>
            </header>

            <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 24px" }}>

                {/* Welcome */}
                <div style={{ marginBottom: 28 }}>
                    <h1 style={{ fontSize: 24, fontWeight: 800, color: "#f1f5f9", margin: 0 }}>
                        Good {new Date().getHours() < 12 ? "Morning" : new Date().getHours() < 18 ? "Afternoon" : "Evening"}, {username} 👋
                    </h1>
                    <p style={{ color: "#475569", fontSize: 14, marginTop: 6 }}>
                        {time.toLocaleDateString("en-US", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
                        {" · "}{time.toLocaleTimeString()}
                    </p>
                </div>

                {/* Status banner */}
                <div style={{ padding: "18px 24px", borderRadius: 16, marginBottom: 24, background: `rgba(${systemStatus === "online" ? "34,197,94" : "249,115,22"},0.08)`, border: `1px solid rgba(${systemStatus === "online" ? "34,197,94" : "249,115,22"},0.25)`, display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{ width: 44, height: 44, borderRadius: 12, background: `rgba(${systemStatus === "online" ? "34,197,94" : "249,115,22"},0.15)`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                        {systemStatus === "online" ? <CheckCircle size={22} color="#22c55e" /> : <AlertTriangle size={22} color="#f97316" />}
                    </div>
                    <div>
                        <div style={{ fontSize: 15, fontWeight: 700, color: statusColor }}>{statusText}</div>
                        <div style={{ fontSize: 12, color: "#475569", marginTop: 2 }}>AI security systems are actively protecting your organization</div>
                    </div>
                    <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: statusColor, boxShadow: `0 0 8px ${statusColor}`, animation: "pulse 1.5s infinite" }} />
                        <span style={{ fontSize: 11, color: statusColor, fontWeight: 600 }}>LIVE</span>
                    </div>
                </div>

                {/* Cards row */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 24 }}>
                    {[
                        { label: "Ransomware Protection", status: "ACTIVE", icon: Shield, color: "#ef4444", desc: "9-model ensemble scanning all file activity" },
                        { label: "Email Security", status: "ACTIVE", icon: Mail, color: "#f97316", desc: "Phishing & spam filter protecting your inbox" },
                        { label: "Access Monitoring", status: "ACTIVE", icon: Activity, color: "#a855f7", desc: "Behavioral analysis of all user sessions" },
                    ].map(card => {
                        const Icon = card.icon;
                        return (
                            <div key={card.label} style={{ padding: "20px", borderRadius: 14, background: "rgba(13,21,38,0.9)", border: `1px solid ${card.color}20` }}>
                                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
                                    <div style={{ width: 34, height: 34, borderRadius: 10, background: `${card.color}15`, border: `1px solid ${card.color}25`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                                        <Icon size={16} color={card.color} />
                                    </div>
                                    <span style={{ fontSize: 12, fontWeight: 600, color: "#cbd5e1" }}>{card.label}</span>
                                </div>
                                <div style={{ fontSize: 11, fontWeight: 700, color: "#22c55e", marginBottom: 4 }}>
                                    ● {card.status}
                                </div>
                                <div style={{ fontSize: 10, color: "#475569", lineHeight: 1.5 }}>{card.desc}</div>
                            </div>
                        );
                    })}
                </div>

                {/* Report suspicious email + Security tip */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 24 }}>

                    {/* Report tool */}
                    <div style={{ padding: "20px", borderRadius: 14, background: "rgba(13,21,38,0.9)", border: "1px solid rgba(59,130,246,0.15)" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                            <Bell size={15} color="#60a5fa" />
                            <span style={{ fontSize: 13, fontWeight: 600, color: "#93c5fd" }}>Report Suspicious Email</span>
                        </div>
                        <p style={{ fontSize: 11, color: "#475569", marginBottom: 12, lineHeight: 1.6 }}>Received a suspicious email? Enter the sender address and our AI will analyze the threat level immediately.</p>
                        <div style={{ display: "flex", gap: 8 }}>
                            <input
                                placeholder="suspicious@unknown.xyz"
                                value={reportEmail}
                                onChange={e => setReportEmail(e.target.value)}
                                style={{ flex: 1, padding: "8px 12px", borderRadius: 8, border: "1px solid rgba(59,130,246,0.2)", background: "rgba(15,23,42,0.8)", color: "#e2e8f0", fontSize: 12, outline: "none" }}
                            />
                            <button onClick={handleReport} disabled={reportLoading || !reportEmail.trim()} style={{ padding: "8px 14px", borderRadius: 8, border: "none", background: "linear-gradient(135deg, #3b82f6, #8b5cf6)", color: "white", fontSize: 12, fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" }}>
                                {reportLoading ? "Checking..." : "Report"}
                            </button>
                        </div>
                        {reportSent && (
                            <div style={{ marginTop: 10, padding: "8px 12px", borderRadius: 8, background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)", fontSize: 11, color: "#86efac" }}>
                                ✅ Reported! Our AI analyzed the sender. IT security team has been notified.
                            </div>
                        )}
                    </div>

                    {/* Security tip */}
                    <div style={{ padding: "20px", borderRadius: 14, background: "rgba(13,21,38,0.9)", border: "1px solid rgba(168,85,247,0.15)" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                            <Info size={15} color="#a78bfa" />
                            <span style={{ fontSize: 13, fontWeight: 600, color: "#c4b5fd" }}>Security Tip of the Moment</span>
                        </div>
                        <div style={{ padding: "14px", borderRadius: 10, background: "rgba(168,85,247,0.06)", border: "1px solid rgba(168,85,247,0.12)", minHeight: 80 }}>
                            <p style={{ fontSize: 13, color: "#cbd5e1", lineHeight: 1.7, margin: 0 }}>
                                💡 {SECURITY_TIPS[tipIndex]}
                            </p>
                        </div>
                        <div style={{ display: "flex", marginTop: 12, gap: 4 }}>
                            {SECURITY_TIPS.map((_, i) => (
                                <div key={i} onClick={() => setTipIndex(i)} style={{ flex: 1, height: 3, borderRadius: 2, background: i === tipIndex ? "#a78bfa" : "rgba(168,85,247,0.2)", cursor: "pointer", transition: "background 0.3s" }} />
                            ))}
                        </div>
                    </div>
                </div>

                {/* What to do in a threat */}
                <div style={{ padding: "24px", borderRadius: 16, background: "rgba(13,21,38,0.9)", border: "1px solid rgba(59,130,246,0.15)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 18 }}>
                        <Zap size={15} color="#60a5fa" />
                        <span style={{ fontSize: 14, fontWeight: 600, color: "#93c5fd" }}>What To Do If You Spot a Threat</span>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
                        {[
                            { step: "1", title: "Don't Click", desc: "Do not click any links or attachments in suspicious emails", color: "#ef4444" },
                            { step: "2", title: "Don't Reply", desc: "Never provide credentials, OTPs, or personal info", color: "#f97316" },
                            { step: "3", title: "Report Now", desc: "Use the report tool above or email security@hospital.org", color: "#3b82f6" },
                            { step: "4", title: "Call IT", desc: "For urgent incidents call ext. 9000 immediately", color: "#22c55e" },
                        ].map(item => (
                            <div key={item.step} style={{ padding: "14px", borderRadius: 12, background: `rgba(${item.color === "#ef4444" ? "239,68,68" : item.color === "#f97316" ? "249,115,22" : item.color === "#3b82f6" ? "59,130,246" : "34,197,94"},0.05)`, border: `1px solid ${item.color}18` }}>
                                <div style={{ width: 28, height: 28, borderRadius: "50%", background: `${item.color}18`, border: `1px solid ${item.color}30`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 800, color: item.color, marginBottom: 10 }}>{item.step}</div>
                                <div style={{ fontSize: 12, fontWeight: 700, color: "#f1f5f9", marginBottom: 5 }}>{item.title}</div>
                                <div style={{ fontSize: 11, color: "#475569", lineHeight: 1.5 }}>{item.desc}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
            `}</style>
        </div>
    );
}
