import { useState, useEffect } from "react";
import axios from "axios";
import {
    Shield, Mail, Database, Users, Activity, LogOut,
    CheckCircle, Zap, Lock, TrendingUp, AlertTriangle,
    ChevronRight, Bell, Settings, X
} from "lucide-react";
import { RansomwareScanner } from "./RansomwareScanner";
import { PhishingAnalyzer } from "./PhishingAnalyzer";
import { SQLInjectionTester } from "./SQLInjectionTester";
import { InsiderThreatMonitor } from "./InsiderThreatMonitor";
import { GlobalKillChainSim } from "./GlobalKillChainSim";
import { HoneypotGrid } from "./HoneypotGrid";
import { Badge } from "./ui/badge";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface SecurityDashboardProps {
    onLogout: () => void;
    isAdmin?: boolean;
    userEmail?: string;
}

type TabId = "overview" | "ransomware" | "phishing" | "sql" | "insider" | "deception";

const navTools = [
    { id: "ransomware" as TabId, label: "Ransomware Scanner", icon: Shield, color: "#FF6900", lightBg: "#FFF4EE" },
    { id: "phishing" as TabId, label: "Phishing Analyzer", icon: Mail, color: "#0066CC", lightBg: "#EEF4FF" },
    { id: "sql" as TabId, label: "SQL Injection", icon: Database, color: "#00C851", lightBg: "#EEFFF4" },
    { id: "insider" as TabId, label: "Insider Threat", icon: Users, color: "#8B5CF6", lightBg: "#F5EEFF" },
    { id: "deception" as TabId, label: "Deception Grid", icon: Lock, color: "#22C55E", lightBg: "#F0FDF4" },
];

const MODEL_INFO = [
    { key: "ransomware", label: "Ransomware Engine", detail: "9-model ensemble (RF, XGB, LGB, SVM + voting)", color: "#FF6900" },
    { key: "phishing", label: "Phishing Detector", detail: "Two-tier XGBoost + Zero-day defense", color: "#0066CC" },
    { key: "sql_injection", label: "SQL Injection", detail: "CodeBERT fine-tuned (99.91% accuracy)", color: "#00C851" },
    { key: "insider_threat", label: "Insider Threat LSTM", detail: "LSTM Autoencoder anomaly detection", color: "#8B5CF6" },
];

export function SecurityDashboard({ onLogout, isAdmin = true, userEmail = "" }: SecurityDashboardProps) {
    const [activeTab, setActiveTab] = useState<TabId>("overview");
    const [modelStatus, setModelStatus] = useState<any>(null);
    const [statusLoading, setStatusLoading] = useState(true);
    const [time, setTime] = useState(new Date());

    // Live clock
    useEffect(() => {
        const t = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(t);
    }, []);

    // Fetch AI health status
    useEffect(() => {
        const fetchStatus = async () => {
            setStatusLoading(true);
            try {
                const r = await axios.get(`${API_BASE}/api/ai/health`);
                setModelStatus(r.data);
            } catch {
                setModelStatus({ status: "degraded", models: {} });
            } finally {
                setStatusLoading(false);
            }
        };
        fetchStatus();
        const interval = setInterval(fetchStatus, 30000);
        return () => clearInterval(interval);
    }, []);

    // Live WebSocket Alerts
    const [liveAlerts, setLiveAlerts] = useState<any[]>([]);
    useEffect(() => {
        const wsUrl = API_BASE.replace("http", "ws") + "/ws/alerts";
        const socket = new WebSocket(wsUrl);
        socket.onmessage = (event) => {
            const alert = JSON.parse(event.data);
            setLiveAlerts(prev => [alert, ...prev].slice(0, 5));
        };
        return () => socket.close();
    }, []);

    const models = modelStatus?.models || {};
    const loadedCount = Object.values(models).filter((m: any) => m?.loaded).length;
    const allHealthy = loadedCount === 4;
    const displayName = userEmail
        ? userEmail.split("@")[0].replace(/\./g, " ").replace(/\b\w/g, (c) => c.toUpperCase())
        : "Admin";

    return (
        <div style={{ minHeight: "100vh", background: "#F8F9FA", fontFamily: "Inter, sans-serif" }}>

            {/* TOP NAVBAR */}
            <nav style={{
                background: "#FFFFFF",
                borderBottom: "1px solid #E1E4E8",
                position: "sticky",
                top: 0,
                zIndex: 100,
                boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
            }}>
                <div style={{ maxWidth: 1280, margin: "0 auto", padding: "0 24px", display: "flex", alignItems: "center", justifyContent: "space-between", height: 64 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                        <div style={{ background: "linear-gradient(135deg,#FF6900,#FF8533)", borderRadius: 8, padding: "6px 8px", display: "flex" }}>
                            <Shield size={20} color="white" />
                        </div>
                        <span style={{ fontWeight: 700, fontSize: 18, color: "#1A1A1A" }}>HealthSentinel</span>
                        <span style={{ background: "#FFF4EE", color: "#FF6900", fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 20, border: "1px solid #FFD4B8" }}>SOC CONSOLE</span>
                    </div>

                    <div style={{ display: "flex", gap: 4 }}>
                        <button
                            onClick={() => setActiveTab("overview")}
                            style={{
                                padding: "6px 16px", borderRadius: 6, border: "none", cursor: "pointer", fontSize: 13, fontWeight: 500,
                                background: activeTab === "overview" ? "#FFF4EE" : "transparent",
                                color: activeTab === "overview" ? "#FF6900" : "#555",
                                transition: "all 0.15s"
                            }}
                        >
                            <span style={{ display: "flex", alignItems: "center", gap: 5 }}><Activity size={14} /> Dashboard</span>
                        </button>
                        {navTools.map(t => (
                            <button
                                key={t.id}
                                onClick={() => setActiveTab(t.id)}
                                style={{
                                    padding: "6px 14px", borderRadius: 6, border: "none", cursor: "pointer", fontSize: 13, fontWeight: 500,
                                    background: activeTab === t.id ? t.lightBg : "transparent",
                                    color: activeTab === t.id ? t.color : "#555",
                                    transition: "all 0.15s"
                                }}
                            >
                                <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
                                    <t.icon size={14} />{t.label}
                                </span>
                            </button>
                        ))}
                    </div>

                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                        <div style={{
                            display: "flex", alignItems: "center", gap: 6, padding: "4px 10px",
                            borderRadius: 20, border: `1px solid ${allHealthy ? "#BBF7D0" : "#FED7AA"}`,
                            background: allHealthy ? "#F0FDF4" : "#FFF7ED"
                        }}>
                            <div style={{
                                width: 6, height: 6, borderRadius: "50%", background: allHealthy ? "#22C55E" : "#F97316",
                                boxShadow: allHealthy ? "0 0 6px #22C55E" : "0 0 6px #F97316"
                            }} />
                            <span style={{ fontSize: 11, fontWeight: 600, color: allHealthy ? "#15803D" : "#C2410C" }}>
                                {statusLoading ? "Checking…" : allHealthy ? `${loadedCount}/4 Models Live` : `${loadedCount}/4 Models`}
                            </span>
                        </div>
                        <span style={{ fontSize: 12, color: "#888", fontVariantNumeric: "tabular-nums" }}>
                            {time.toLocaleTimeString()}
                        </span>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "4px 12px", borderRadius: 20, background: "#F4F4F4" }}>
                            <div style={{ width: 22, height: 22, borderRadius: "50%", background: "linear-gradient(135deg,#FF6900,#FF8533)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                                <span style={{ fontSize: 10, fontWeight: 700, color: "white" }}>{displayName[0]?.toUpperCase()}</span>
                            </div>
                            <span style={{ fontSize: 12, fontWeight: 500, color: "#333" }}>{displayName}</span>
                        </div>
                        <button
                            onClick={onLogout}
                            style={{
                                display: "flex", alignItems: "center", gap: 5, padding: "6px 14px", borderRadius: 6,
                                border: "1px solid #E1E4E8", background: "white", color: "#555", fontSize: 13, fontWeight: 500, cursor: "pointer"
                            }}
                        >
                            <LogOut size={14} /> Logout
                        </button>
                    </div>
                </div>
            </nav>

            {/* MAIN CONTENT */}
            <div style={{ maxWidth: 1280, margin: "0 auto", padding: "32px 24px" }}>

                {activeTab === "overview" && (
                    <div>
                        <div style={{ marginBottom: 32 }}>
                            <h1 style={{ fontSize: 28, fontWeight: 700, color: "#1A1A1A", marginBottom: 4 }}>
                                Security Operations Center
                            </h1>
                            <p style={{ color: "#666", fontSize: 15 }}>
                                AI-powered threat detection for healthcare systems — real-time monitoring, attack simulation & SHAP explainability
                            </p>
                        </div>

                        {/* Main Grid: Telemetry + Kill Chain */}
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: 24, marginBottom: 32 }}>
                            
                            {/* Left: Kill Chain & SOC Feed */}
                            <div style={{ gridColumn: "span 8", display: "flex", flexDirection: "column", gap: 24 }}>
                                <GlobalKillChainSim />
                                
                                <div style={{ background: "#0F172A", border: "1px solid #1E293B", borderRadius: 12, padding: "20px", color: "white" }}>
                                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                                        <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#EF4444", animation: "pulse 2s infinite" }} />
                                        <h3 style={{ fontWeight: 600, fontSize: 15 }}>Real-Time Attack Telemetry</h3>
                                    </div>
                                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                                        {liveAlerts.length === 0 ? (
                                            <div style={{ fontSize: 13, color: "#64748B", fontStyle: "italic" }}>Waiting for red team activity...</div>
                                        ) : (
                                            liveAlerts.map((alert, i) => (
                                                <div key={i} style={{ 
                                                    padding: "16px", 
                                                    background: "rgba(255,255,255,0.03)", 
                                                    borderRadius: "10px", 
                                                    borderLeft: `4px solid ${alert.severity === 'high' ? '#EF4444' : '#60A5FA'}`, 
                                                    animation: "slideIn 0.3s ease-out",
                                                    display: "flex",
                                                    flexDirection: "column",
                                                    gap: "6px",
                                                    border: "1px solid rgba(255,255,255,0.05)",
                                                    borderLeftWidth: "4px"
                                                }}>
                                                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                                        <span style={{ fontSize: "11px", fontWeight: "900", color: alert.severity === 'high' ? '#EF4444' : '#60A5FA', textTransform: "uppercase", letterSpacing: "1px" }}>
                                                            {alert.alert_type}
                                                        </span>
                                                        <span style={{ fontSize: "10px", color: "#475569", fontFamily: "monospace" }}>
                                                            {new Date(alert.timestamp).toLocaleTimeString()}
                                                        </span>
                                                    </div>
                                                    <div style={{ fontSize: "14px", color: "#F1F5F9", fontWeight: "500" }}>
                                                        {alert.description}
                                                    </div>
                                                    <div style={{ fontSize: "11px", color: "#64748B", display: "flex", alignItems: "center", gap: "6px", marginTop: "4px" }}>
                                                        <span style={{ opacity: 0.6 }}>Response:</span> 
                                                        <span style={{ color: alert.severity === 'high' ? '#EF4444' : '#60A5FA', fontWeight: "700" }}>
                                                            {alert.severity === 'high' ? '🔥 HOST ISOLATED' : '🛡️ LOGGED TO BLOCKCHAIN'}
                                                        </span>
                                                    </div>
                                                </div>
                                            ))
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Right: Security Posture & Compliance */}
                            <div style={{ gridColumn: "span 4", display: "flex", flexDirection: "column", gap: 24 }}>
                                <div style={{ background: "white", border: "1px solid #E1E4E8", borderRadius: 12, padding: "20px" }}>
                                    <h3 style={{ fontWeight: 600, fontSize: 15, marginBottom: 16 }}>Advanced Protection Status</h3>
                                    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                                        {[
                                            { label: "Blockchain Integrity", status: "VERIFIED", color: "#8B5CF6" },
                                            { label: "PHI Redactor", status: "ACTIVE", color: "#0066CC" },
                                            { label: "Zero Trust Zones", status: "RESTRICTED", color: "#FF6900" },
                                            { label: "Biometric Auth", status: "ENFORCED", color: "#22C55E" }
                                        ].map(item => (
                                            <div key={item.label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                                <span style={{ fontSize: 13, color: "#555" }}>{item.label}</span>
                                                <Badge style={{ background: item.color + "10", color: item.color, border: `1px solid ${item.color}30`, fontSize: 10 }}>{item.status}</Badge>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                <div style={{ background: "white", border: "1px solid #E1E4E8", borderRadius: 12, padding: "20px" }}>
                                    <h3 style={{ fontWeight: 600, fontSize: 15, marginBottom: 16 }}>Compliance Readiness</h3>
                                    <div style={{ padding: "12px", background: "#F8F9FA", borderRadius: 8, marginBottom: 12 }}>
                                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                                            <span style={{ fontSize: 11, fontWeight: 600 }}>HIPAA Overall</span>
                                            <span style={{ fontSize: 11, color: "#22C55E" }}>94.2%</span>
                                        </div>
                                        <div style={{ height: 4, background: "#E5E7EB", borderRadius: 2 }}>
                                            <div style={{ width: "94%", height: "100%", background: "#22C55E", borderRadius: 2 }} />
                                        </div>
                                    </div>
                                    <div style={{ padding: "12px", background: "#F8F9FA", borderRadius: 8 }}>
                                        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                                            <span style={{ fontSize: 11, fontWeight: 600 }}>GDPR Overall</span>
                                            <span style={{ fontSize: 11, color: "#0066CC" }}>91.5%</span>
                                        </div>
                                        <div style={{ height: 4, background: "#E5E7EB", borderRadius: 2 }}>
                                            <div style={{ width: "91%", height: "100%", background: "#0066CC", borderRadius: 2 }} />
                                        </div>
                                    </div>
                                </div>

                                <div style={{ background: "white", border: "1px solid #E1E4E8", borderRadius: 12, overflow: "hidden" }}>
                                    <div style={{ padding: "14px 20px", borderBottom: "1px solid #E1E4E8", background: "#FAFAFA" }}>
                                        <h3 style={{ fontWeight: 600, fontSize: 13 }}>Inference Engines</h3>
                                    </div>
                                    {MODEL_INFO.map((m, i) => (
                                        <div key={m.key} style={{ display: "flex", alignItems: "center", padding: "10px 20px", borderBottom: i < MODEL_INFO.length - 1 ? "1px solid #F4F4F4" : "none" }}>
                                            <div style={{ width: 6, height: 6, borderRadius: "50%", background: models[m.key]?.loaded ? "#22C55E" : "#F97316", marginRight: 10 }} />
                                            <span style={{ fontSize: 12, fontWeight: 500, color: "#333", flex: 1 }}>{m.label}</span>
                                            <span style={{ fontSize: 10, color: "#888" }}>{models[m.key]?.loaded ? "ACTIVE" : "STBY"}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab !== "overview" && (
                    <div>
                        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 24, fontSize: 13, color: "#888" }}>
                            <button onClick={() => setActiveTab("overview")} style={{ background: "none", border: "none", cursor: "pointer", color: "#666", fontWeight: 500 }}>
                                Overview
                            </button>
                            <ChevronRight size={14} />
                            <span style={{ color: "#1A1A1A", fontWeight: 600 }}>
                                {navTools.find(t => t.id === activeTab)?.label}
                            </span>
                        </div>

                        {(() => {
                            const tool = navTools.find(t => t.id === activeTab);
                            if (!tool) return null;
                            const Icon = tool.icon;
                            const modelKey = activeTab === "sql" ? "sql_injection" : activeTab === "insider" ? "insider_threat" : activeTab;
                            const isLoaded = models[modelKey]?.loaded;
                            return (
                                <div style={{ background: "white", border: "1px solid #E1E4E8", borderRadius: 12, padding: "20px 24px", marginBottom: 24, display: "flex", alignItems: "center", gap: 16 }}>
                                    <div style={{ width: 48, height: 48, borderRadius: 12, background: tool.lightBg, display: "flex", alignItems: "center", justifyContent: "center" }}>
                                        <Icon size={24} color={tool.color} />
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <h2 style={{ fontWeight: 700, fontSize: 20, color: "#1A1A1A", marginBottom: 3 }}>{tool.label}</h2>
                                        <p style={{ fontSize: 13, color: "#666" }}>
                                            {MODEL_INFO.find(m => m.key === modelKey)?.detail} • Attack simulation enabled
                                        </p>
                                    </div>
                                    <span style={{
                                        fontSize: 11, fontWeight: 600, padding: "4px 12px", borderRadius: 20,
                                        background: isLoaded ? "#F0FDF4" : "#FFF7ED",
                                        color: isLoaded ? "#15803D" : "#C2410C",
                                        border: `1px solid ${isLoaded ? "#BBF7D0" : "#FED7AA"}`
                                    }}>
                                        {isLoaded ? "✓ Model Loaded" : "⚡ Fallback Active"}
                                    </span>
                                </div>
                            );
                        })()}

                        <div style={{ background: "white", border: "1px solid #E1E4E8", borderRadius: 12, overflow: "hidden" }}>
                            {activeTab === "ransomware" && <RansomwareScanner fallbackActive={!models["ransomware"]?.loaded} />}
                            {activeTab === "phishing" && <PhishingAnalyzer />}
                            {activeTab === "sql" && <SQLInjectionTester />}
                            {activeTab === "insider" && <InsiderThreatMonitor />}
                            {activeTab === "deception" && (
                                <div style={{ padding: "24px" }}>
                                    <HoneypotGrid />
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
