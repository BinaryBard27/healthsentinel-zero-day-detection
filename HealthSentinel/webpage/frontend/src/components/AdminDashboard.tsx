/**
 * AdminDashboard — Full security operations center for admin/presenter role
 * Includes all 4 detection tools with attack simulation + SHAP explainability
 */
import { useState, useEffect } from "react";
import {
    Shield, Mail, Database, Users, Activity, LogOut,
    AlertTriangle, CheckCircle, Zap, Lock, TrendingUp,
    Eye, Bell, Settings, ChevronRight, Server
} from "lucide-react";
import { RansomwareScanner } from "./RansomwareScanner";
import { PhishingAnalyzer } from "./PhishingAnalyzer";
import { SQLInjectionTester } from "./SQLInjectionTester";
import { InsiderThreatMonitor } from "./InsiderThreatMonitor";
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface AdminDashboardProps { onLogout: () => void; username?: string }

const navItems = [
    { id: "overview", label: "SOC Overview", icon: Activity },
    { id: "ransomware", label: "Ransomware", icon: Shield, color: "#ef4444" },
    { id: "phishing", label: "Phishing", icon: Mail, color: "#f97316" },
    { id: "sql", label: "SQL Injection", icon: Database, color: "#3b82f6" },
    { id: "insider", label: "Insider Threat", icon: Users, color: "#a855f7" },
];

export function AdminDashboard({ onLogout, username = "Admin" }: AdminDashboardProps) {
    const [activeTab, setActiveTab] = useState("overview");
    const [time, setTime] = useState(new Date());
    const [scanPulse, setScanPulse] = useState(0);
    const [modelStatus, setModelStatus] = useState<any>(null);
    const [threatLog, setThreatLog] = useState([
        { time: new Date().toLocaleTimeString(), type: "System", msg: "Admin dashboard initialized", level: "success" },
        { time: new Date().toLocaleTimeString(), type: "AI", msg: "All 4 detection engines active with fallbacks", level: "info" },
        { time: new Date().toLocaleTimeString(), type: "SHAP", msg: "Explainability module ready", level: "info" },
    ]);

    useEffect(() => {
        const t = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(t);
    }, []);

    useEffect(() => {
        const t = setInterval(() => setScanPulse(p => (p + 1) % 100), 50);
        return () => clearInterval(t);
    }, []);

    useEffect(() => {
        axios.get(`${API_BASE}/api/health`).then(r => setModelStatus(r.data)).catch(() => setModelStatus(null));
    }, []);

    const addThreatLog = (type: string, msg: string, level = "warn") => {
        setThreatLog(prev => [
            { time: new Date().toLocaleTimeString(), type, msg, level },
            ...prev.slice(0, 9)
        ]);
    };

    useEffect(() => {
        const wsUrl = `ws://${window.location.hostname}:8085/ws/alerts`;
        const ws = new WebSocket(wsUrl);
        
        ws.onmessage = (event) => {
            try {
                const alertData = JSON.parse(event.data);
                addThreatLog(
                    alertData.alert_type || "ALERT", 
                    alertData.description || "Suspicious activity detected", 
                    alertData.severity === "critical" || alertData.severity === "high" ? "warn" : "info"
                );
            } catch (e) {
                console.error("WS parse error", e);
            }
        };

        return () => ws.close();
    }, []);

    const models = modelStatus?.models || {};
    const loadedCount = Object.values(models).filter(Boolean).length;

    return (
        <div style={{ display: "flex", minHeight: "100vh", background: "#0a0f1e", color: "#e2e8f0", fontFamily: "'Inter', sans-serif" }}>

            {/* ── SIDEBAR ── */}
            <aside style={{ width: 240, background: "linear-gradient(180deg, #0d1526 0%, #0a0f1e 100%)", borderRight: "1px solid rgba(59,130,246,0.15)", display: "flex", flexDirection: "column", position: "sticky", top: 0, height: "100vh", flexShrink: 0 }}>
                {/* Logo */}
                <div style={{ padding: "24px 20px 20px", borderBottom: "1px solid rgba(59,130,246,0.1)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                        <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #3b82f6, #8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 16px rgba(59,130,246,0.5)" }}>
                            <Shield size={20} color="white" />
                        </div>
                        <div>
                            <div style={{ fontWeight: 700, fontSize: 14, color: "#f1f5f9" }}>HealthSentinel</div>
                            <div style={{ fontSize: 10, color: "#ef4444", letterSpacing: 1, textTransform: "uppercase", fontWeight: 700 }}>ADMIN — SOC</div>
                        </div>
                    </div>
                </div>

                {/* Clock + User */}
                <div style={{ padding: "12px 20px", borderBottom: "1px solid rgba(59,130,246,0.08)" }}>
                    <div style={{ fontSize: 11, color: "#475569", marginBottom: 2, textTransform: "uppercase", letterSpacing: 1 }}>Live Monitor</div>
                    <div style={{ fontSize: 18, fontWeight: 700, color: "#22c55e", fontFamily: "monospace", letterSpacing: 2 }}>{time.toLocaleTimeString()}</div>
                    <div style={{ marginTop: 8, padding: "4px 10px", borderRadius: 6, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)", fontSize: 11, color: "#f87171", fontWeight: 600, display: "inline-block" }}>
                        👤 {username}
                    </div>
                </div>

                {/* Nav */}
                <nav style={{ flex: 1, padding: "12px 12px" }}>
                    {navItems.map(item => {
                        const Icon = item.icon;
                        const active = activeTab === item.id;
                        const c = item.color || "#3b82f6";
                        return (
                            <button key={item.id} onClick={() => setActiveTab(item.id)} style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 10, border: "none", cursor: "pointer", marginBottom: 4, background: active ? `linear-gradient(135deg, ${c}25, ${c}15)` : "transparent", color: active ? c : "#64748b", fontWeight: active ? 600 : 400, fontSize: 13, textAlign: "left", transition: "all 0.2s", boxShadow: active ? `inset 0 0 0 1px ${c}40` : "none" }}>
                                <Icon size={16} style={{ color: active ? c : "#475569", flexShrink: 0 }} />
                                {item.label}
                                {active && <div style={{ marginLeft: "auto", width: 6, height: 6, borderRadius: "50%", background: c, boxShadow: `0 0 6px ${c}` }} />}
                            </button>
                        );
                    })}
                </nav>

                {/* Model status mini */}
                <div style={{ padding: "12px 16px", borderTop: "1px solid rgba(59,130,246,0.1)", borderBottom: "1px solid rgba(59,130,246,0.1)", marginBottom: 4 }}>
                    <div style={{ fontSize: 10, color: "#475569", marginBottom: 6, textTransform: "uppercase", letterSpacing: 1 }}>AI Models</div>
                    <div style={{ fontSize: 13, fontWeight: 700, color: loadedCount >= 2 ? "#22c55e" : "#f97316" }}>
                        {loadedCount} / 4 Loaded
                    </div>
                    <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>Rest using fallbacks</div>
                </div>

                {/* Logout */}
                <div style={{ padding: "12px 12px" }}>
                    <button onClick={onLogout} style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderRadius: 10, border: "1px solid rgba(239,68,68,0.2)", cursor: "pointer", background: "rgba(239,68,68,0.05)", color: "#f87171", fontSize: 13, fontWeight: 500, transition: "all 0.2s" }}>
                        <LogOut size={15} /> Sign Out
                    </button>
                </div>
            </aside>

            {/* ── MAIN ── */}
            <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "auto" }}>

                {/* Top bar */}
                <header style={{ padding: "16px 32px", borderBottom: "1px solid rgba(59,130,246,0.1)", background: "rgba(13,21,38,0.8)", backdropFilter: "blur(10px)", display: "flex", alignItems: "center", justifyContent: "space-between", position: "sticky", top: 0, zIndex: 10 }}>
                    <div>
                        <h1 style={{ fontSize: 20, fontWeight: 700, color: "#f1f5f9", margin: 0 }}>
                            {navItems.find(n => n.id === activeTab)?.label || "Dashboard"}
                        </h1>
                        <p style={{ fontSize: 12, color: "#475569", margin: 0, marginTop: 2 }}>Security Operations Center — Admin View</p>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "6px 14px", borderRadius: 20, background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)" }}>
                            <div style={{ width: 7, height: 7, borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 8px #22c55e", animation: "pulse 1.5s infinite" }} />
                            <span style={{ fontSize: 11, color: "#22c55e", fontWeight: 600 }}>SCANNING</span>
                        </div>
                        <div style={{ padding: "6px 14px", borderRadius: 20, background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)", fontSize: 11, color: "#f87171", fontWeight: 600 }}>
                            ADMIN MODE
                        </div>
                    </div>
                </header>

                <div style={{ padding: "28px 32px", flex: 1 }}>

                    {/* ── OVERVIEW ── */}
                    {activeTab === "overview" && (
                        <div>
                            {/* Stat cards */}
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
                                {[
                                    { label: "System Status", value: "ACTIVE", sub: "All engines running", icon: CheckCircle, color: "#22c55e", glow: "rgba(34,197,94,0.3)", pulse: true },
                                    { label: "AI Models", value: `${loadedCount} / 4`, sub: "Loaded + fallbacks ready", icon: Zap, color: "#3b82f6", glow: "rgba(59,130,246,0.3)", pulse: false },
                                    { label: "SHAP Status", value: "READY", sub: "Explainability active", icon: Eye, color: "#a855f7", glow: "rgba(168,85,247,0.3)", pulse: false },
                                    { label: "Protection", value: "MAX", sub: "Enterprise-grade", icon: Lock, color: "#f97316", glow: "rgba(249,115,22,0.3)", pulse: false },
                                ].map(card => {
                                    const Icon = card.icon;
                                    return (
                                        <div key={card.label} style={{ background: "linear-gradient(135deg, rgba(13,21,38,0.9), rgba(15,23,42,0.8))", border: `1px solid ${card.color}30`, borderRadius: 16, padding: "20px 22px", position: "relative", overflow: "hidden", boxShadow: `0 4px 24px ${card.glow}` }}>
                                            <div style={{ position: "absolute", top: -20, right: -20, width: 80, height: 80, borderRadius: "50%", background: card.glow, filter: "blur(20px)" }} />
                                            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", position: "relative" }}>
                                                <div>
                                                    <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8 }}>{card.label}</div>
                                                    <div style={{ fontSize: 26, fontWeight: 800, color: card.color, fontFamily: "monospace" }}>{card.value}</div>
                                                    <div style={{ fontSize: 11, color: "#475569", marginTop: 6 }}>{card.sub}</div>
                                                </div>
                                                <div style={{ width: 40, height: 40, borderRadius: 12, background: `${card.color}18`, border: `1px solid ${card.color}30`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                                                    <Icon size={20} color={card.color} />
                                                </div>
                                            </div>
                                            {card.pulse && (
                                                <div style={{ marginTop: 12, height: 3, borderRadius: 2, background: "rgba(34,197,94,0.1)", overflow: "hidden" }}>
                                                    <div style={{ height: "100%", width: `${scanPulse}%`, background: "linear-gradient(90deg, #22c55e, #86efac)", transition: "width 0.05s linear" }} />
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>

                            {/* Two-column: threat feed + model status */}
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>

                                {/* Live Threat Feed */}
                                <div style={{ background: "rgba(13,21,38,0.9)", border: "1px solid rgba(59,130,246,0.15)", borderRadius: 16, padding: "20px 22px" }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                                        <Bell size={14} color="#60a5fa" />
                                        <span style={{ fontSize: 13, fontWeight: 600, color: "#93c5fd" }}>Live Activity Feed</span>
                                        <div style={{ marginLeft: "auto", width: 6, height: 6, borderRadius: "50%", background: "#22c55e", boxShadow: "0 0 6px #22c55e" }} />
                                    </div>
                                    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                                        {threatLog.map((item, i) => (
                                            <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: "8px 12px", borderRadius: 8, background: "rgba(15,23,42,0.6)", border: "1px solid rgba(59,130,246,0.08)" }}>
                                                <div style={{ width: 7, height: 7, borderRadius: "50%", flexShrink: 0, background: item.level === "success" ? "#22c55e" : item.level === "warn" ? "#f97316" : "#3b82f6", boxShadow: `0 0 5px ${item.level === "success" ? "#22c55e" : item.level === "warn" ? "#f97316" : "#3b82f6"}` }} />
                                                <span style={{ fontSize: 10, color: "#475569", fontFamily: "monospace", flexShrink: 0 }}>{item.time}</span>
                                                <span style={{ fontSize: 10, color: "#60a5fa", fontWeight: 600, minWidth: 60 }}>[{item.type}]</span>
                                                <span style={{ fontSize: 11, color: "#94a3b8" }}>{item.msg}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Model Status */}
                                <div style={{ background: "rgba(13,21,38,0.9)", border: "1px solid rgba(59,130,246,0.15)", borderRadius: 16, padding: "20px 22px" }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                                        <Server size={14} color="#a78bfa" />
                                        <span style={{ fontSize: 13, fontWeight: 600, color: "#c4b5fd" }}>AI Model Status</span>
                                    </div>
                                    {[
                                        { name: "Ransomware Ensemble", detail: "9 models (RF/XGB/LGB/SVM)", key: "ransomware" },
                                        { name: "Phishing Detector", detail: "XGBoost + rule-based fallback", key: "phishing" },
                                        { name: "SQL Injection (CodeBERT)", detail: "498 MB transformer", key: "sql_injection" },
                                        { name: "LSTM Insider Threat", detail: "Autoencoder + Isolation Forest", key: "insider_threat" },
                                    ].map((m, i) => {
                                        const isLoaded = models[m.key];
                                        const color = isLoaded ? "#22c55e" : "#f97316";
                                        return (
                                            <div key={i} style={{ marginBottom: 14 }}>
                                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 5 }}>
                                                    <div>
                                                        <div style={{ fontSize: 12, fontWeight: 600, color: "#cbd5e1" }}>{m.name}</div>
                                                        <div style={{ fontSize: 10, color: "#475569" }}>{m.detail}</div>
                                                    </div>
                                                    <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 6, background: `${color}18`, color, border: `1px solid ${color}30` }}>
                                                        {isLoaded ? "LOADED" : "FALLBACK"}
                                                    </span>
                                                </div>
                                                <div style={{ height: 4, borderRadius: 2, background: "rgba(59,130,246,0.1)" }}>
                                                    <div style={{ height: "100%", width: isLoaded ? "100%" : "60%", borderRadius: 2, background: `linear-gradient(90deg, ${color}, ${color}99)` }} />
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Quick access cards */}
                            <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
                                {[
                                    { id: "ransomware", label: "Simulate Ransomware", icon: Shield, color: "#ef4444", desc: "WannaCry / LockBit simulation + SHAP" },
                                    { id: "phishing", label: "Simulate Phishing", icon: Mail, color: "#f97316", desc: "CEO fraud / credential harvest + SHAP" },
                                    { id: "sql", label: "Simulate SQL Attack", icon: Database, color: "#3b82f6", desc: "Auth bypass / UNION dump + SHAP" },
                                    { id: "insider", label: "Simulate Insider Threat", icon: Users, color: "#a855f7", desc: "After-hours / USB exfil + SHAP" },
                                ].map(card => {
                                    const Icon = card.icon;
                                    return (
                                        <button key={card.id} onClick={() => setActiveTab(card.id)} style={{ background: "rgba(13,21,38,0.9)", border: `1px solid ${card.color}25`, borderRadius: 14, padding: "16px 18px", cursor: "pointer", textAlign: "left", transition: "all 0.2s" }}>
                                            <div style={{ width: 36, height: 36, borderRadius: 10, marginBottom: 10, background: `${card.color}18`, border: `1px solid ${card.color}30`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                                                <Icon size={18} color={card.color} />
                                            </div>
                                            <div style={{ fontSize: 12, fontWeight: 700, color: "#e2e8f0", marginBottom: 4 }}>{card.label}</div>
                                            <div style={{ fontSize: 10, color: "#475569" }}>{card.desc}</div>
                                            <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 4, fontSize: 10, color: card.color }}>
                                                Launch <ChevronRight size={10} />
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* ── TOOL TABS ── */}
                    {activeTab !== "overview" && (
                        <div style={{ background: "rgba(13,21,38,0.9)", border: "1px solid rgba(59,130,246,0.15)", borderRadius: 16, padding: "28px" }}>
                            <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24, paddingBottom: 20, borderBottom: "1px solid rgba(59,130,246,0.1)" }}>
                                {(() => {
                                    const nav = navItems.find(n => n.id === activeTab);
                                    if (!nav) return null;
                                    const Icon = nav.icon;
                                    const c = nav.color || "#3b82f6";
                                    return (
                                        <>
                                            <div style={{ width: 44, height: 44, borderRadius: 12, background: `${c}18`, border: `1px solid ${c}30`, display: "flex", alignItems: "center", justifyContent: "center", boxShadow: `0 0 16px ${c}30` }}>
                                                <Icon size={22} color={c} />
                                            </div>
                                            <div>
                                                <h2 style={{ margin: 0, fontSize: 18, fontWeight: 700, color: "#f1f5f9" }}>{nav.label}</h2>
                                                <p style={{ margin: 0, fontSize: 12, color: "#475569", marginTop: 2 }}>AI-powered detection with SHAP explainability</p>
                                            </div>
                                            <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
                                                <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "5px 12px", borderRadius: 20, background: "rgba(34,197,94,0.1)", border: "1px solid rgba(34,197,94,0.2)", fontSize: 11, color: "#22c55e", fontWeight: 600 }}>
                                                    <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#22c55e" }} /> ONLINE
                                                </div>
                                                <div style={{ padding: "5px 12px", borderRadius: 20, background: "rgba(168,85,247,0.1)", border: "1px solid rgba(168,85,247,0.2)", fontSize: 11, color: "#c084fc", fontWeight: 600 }}>
                                                    SHAP READY
                                                </div>
                                            </div>
                                        </>
                                    );
                                })()}
                            </div>

                            <style>{`
                                .dark-panel label { color: #94a3b8 !important; font-size: 12px !important; }
                                .dark-panel input, .dark-panel textarea {
                                    background: rgba(15,23,42,0.8) !important;
                                    border: 1px solid rgba(59,130,246,0.2) !important;
                                    color: #e2e8f0 !important; border-radius: 8px !important;
                                }
                                .dark-panel input:focus, .dark-panel textarea:focus {
                                    border-color: rgba(59,130,246,0.5) !important;
                                    outline: none !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.1) !important;
                                }
                                .dark-panel input::placeholder, .dark-panel textarea::placeholder { color: #334155 !important; }
                                .dark-panel [class*="card"], .dark-panel [class*="Card"] {
                                    background: rgba(15,23,42,0.6) !important;
                                    border: 1px solid rgba(59,130,246,0.12) !important;
                                    border-radius: 12px !important; color: #e2e8f0 !important;
                                }
                                .dark-panel h3 { color: #f1f5f9 !important; }
                                .dark-panel h4:not([style]) { color: #f1f5f9; }
                                .dark-panel p { color: #94a3b8; }
                                .dark-panel button.w-full:not([style]) {
                                    background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
                                    border: none !important; color: white !important;
                                    font-weight: 600 !important; border-radius: 8px !important;
                                }
                            `}</style>

                            <div className="dark-panel">
                                {activeTab === "ransomware" && <RansomwareScanner />}
                                {activeTab === "phishing" && <PhishingAnalyzer />}
                                {activeTab === "sql" && <SQLInjectionTester />}
                                {activeTab === "insider" && <InsiderThreatMonitor />}
                            </div>
                        </div>
                    )}
                </div>
            </main>

            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
                ::-webkit-scrollbar { width: 6px; }
                ::-webkit-scrollbar-track { background: #0a0f1e; }
                ::-webkit-scrollbar-thumb { background: rgba(59,130,246,0.3); border-radius: 3px; }
            `}</style>
        </div>
    );
}
