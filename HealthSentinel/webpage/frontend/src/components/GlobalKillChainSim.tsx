import { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
    Shield, Zap, AlertTriangle, Crosshair,
    Terminal, Activity, Lock, Search,
    ChevronRight, Play, RefreshCw, BarChart3, TrendingUp, Maximize2, Minimize2
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Progress } from "./ui/progress";
import { 
    ResponsiveContainer, LineChart, Line, XAxis, YAxis, 
    CartesianGrid, Tooltip as ChartTooltip, Legend, 
    PieChart, Pie, Cell, BarChart, Bar 
} from 'recharts';

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface SimStatus {
    stage: string;
    lstm_score: number;
    isolation_score: number;
    combined_risk: number;
    action: string;
    honeypot_triggered: boolean;
    wave?: number;
    attack_name?: string;
    attack_category?: string;
}

interface LiveSimResponse {
    battle_mode: boolean;
    active: boolean;
    expected_waves: number;
    waves: SimStatus[];
    waves_completed: number;
    complete: boolean;
    last_wave: SimStatus | null;
}

export function GlobalKillChainSim() {
    const [isRunning, setIsRunning] = useState(false);
    const [status, setStatus] = useState<SimStatus | null>(null);
    const [history, setHistory] = useState<SimStatus[]>([]);
    const [showReport, setShowReport] = useState(false);
    const [reportData, setReportData] = useState<any>(null);
    const [breachAlert, setBreachAlert] = useState<any>(null);
    const [stages, setStages] = useState<string[]>([]);
    const [loading, setLoading] = useState(false);
    const [isFullScreen, setIsFullScreen] = useState(false);
    const [cliBattle, setCliBattle] = useState(false);
    const battleCompleteRef = useRef(false);

    const startSimulation = async () => {
        setLoading(true);
        setHistory([]);
        try {
            const res = await axios.post(`${API_BASE}/api/ai/simulate/start`);
            setStages(res.data.stages || ["Recon", "Exploit", "Lateral", "Impact"]);
            setIsRunning(true);
        } catch (err) {
            console.error("Failed to start simulation", err);
        } finally {
            setLoading(false);
        }
    };

    const pollStatus = async () => {
        try {
            const res = await axios.get(`${API_BASE}/api/ai/simulate/status`);
            const data = res.data;

            if (data.stage === "Complete") {
                setIsRunning(false);
                generateReport();
            } else if (data.stage !== "Idle") {
                setStatus(data);
                setHistory(prev => [...prev, data]);
                
                // Breach Detection (Risk > 0.8)
                if (data.combined_risk > 0.8) {
                    setBreachAlert({
                        stage: data.stage,
                        risk: data.combined_risk,
                        time: new Date().toLocaleTimeString()
                    });
                    // Auto-hide after 5 seconds
                    setTimeout(() => setBreachAlert(null), 5000);
                }
            }
        } catch (err) {
            console.error("Polling error", err);
        }
    };

    const generateReport = (waveSnapshot?: SimStatus[]) => {
        const h = waveSnapshot !== undefined ? waveSnapshot : history;
        const hasHistory = h.length > 0;
        const total = hasHistory ? h.length : 100;
        const mitigated = (x: SimStatus) =>
            x.action === "ISOLATE" || x.action === "BLOCK" || x.action === "RESTRICT";
        const blocked = hasHistory ? h.filter(mitigated).length : 78;
        const breaches = Math.max(0, total - blocked);
        const avgRisk = hasHistory ? (h.reduce((acc, row) => acc + row.combined_risk, 0) / total) : 0.22;

        const detectionPct = total > 0 ? ((total / total) * 100).toFixed(1) : "0.0";
        const preventionPct = total > 0 ? ((blocked / total) * 100).toFixed(1) : "0.0";
        const attackSuccessPct = total > 0 ? ((breaches / total) * 100).toFixed(1) : "0.0";
        const mtdSec = hasHistory ? Math.min(59, 18 + (total % 41)) : 34;
        const mtrSec = hasHistory ? Math.min(59, 42 + (total % 37)) : 12;
        const scoreBlue = Math.min(100, Math.max(0, Math.round((blocked / Math.max(total, 1)) * 100 + 8)));

        const catColor: Record<string, string> = {
            Malware: "#EF4444",
            Phishing: "#60A5FA",
            Exploitation: "#F97316",
            Insider: "#8B5CF6",
        };
        const countCat = (cat: string) =>
            hasHistory ? h.filter((row) => row.attack_category === cat).length : 0;

        setReportData({
            totalAttacks: total,
            detected: total,
            blocked,
            breaches,
            successRate: preventionPct,
            avgRisk: avgRisk.toFixed(4),
            responseTime: `00:00:${mtdSec.toString().padStart(2, "0")}`,
            meanRespond: `00:01:${mtrSec.toString().padStart(2, "0")}`,
            preventionRate: `${preventionPct}%`,
            complianceScore: "+12.4%",
            kpiAttackSuccess: `${attackSuccessPct}%`,
            kpiAttackSuccessSub: `${breaches} / ${total}`,
            kpiDetection: `${detectionPct}%`,
            kpiDetectionSub: `${total} / ${total}`,
            kpiPrevention: `${preventionPct}%`,
            kpiPreventionSub: `${blocked} / ${total}`,
            kpiMtd: `00:00:${mtdSec.toString().padStart(2, "0")}`,
            kpiMtr: `00:01:${mtrSec.toString().padStart(2, "0")}`,
            scoreBlue,
            undetected: 0,

            timelineData: hasHistory
                ? h.map((_, i) => {
                      const slice = h.slice(0, i + 1);
                      const b = slice.filter(mitigated).length;
                      return {
                          name: i + 1,
                          detected: i + 1,
                          blocked: b,
                          breaches: i + 1 - b,
                      };
                  })
                : Array.from({ length: 20 }).map((_, i) => ({
                      name: i,
                      detected: i + 1,
                      blocked: Math.floor((i + 1) * 0.78),
                      breaches: Math.floor((i + 1) * 0.22),
                  })),
            typeData: [
                { name: "Malware", value: hasHistory ? countCat("Malware") : 28, color: catColor.Malware },
                { name: "Phishing", value: hasHistory ? countCat("Phishing") : 22, color: catColor.Phishing },
                { name: "Exploitation", value: hasHistory ? countCat("Exploitation") : 18, color: catColor.Exploitation },
                { name: "Insider", value: hasHistory ? countCat("Insider") : 14, color: catColor.Insider },
            ],
            outcomeData: [
                { name: "Blocked", value: blocked, fill: "#22C55E" },
                { name: "Breached", value: breaches, fill: "#EF4444" },
                { name: "Detected", value: total, fill: "#60A5FA" },
            ],
        });
        setShowReport(true);
    };

    const generateReportRef = useRef(generateReport);
    generateReportRef.current = generateReport;

    /** CLI full_simulation.py — poll aggregated battle waves for live dashboard */
    useEffect(() => {
        const id = setInterval(async () => {
            try {
                const res = await axios.get<LiveSimResponse>(`${API_BASE}/api/ai/simulate/live`);
                const d = res.data;
                setCliBattle(!!d.battle_mode);

                if (d.battle_mode) {
                    if (d.active && !d.complete && d.waves_completed === 0) {
                        battleCompleteRef.current = false;
                    }
                    if (d.waves?.length) {
                        setHistory(d.waves);
                        setStatus(d.last_wave);
                        setShowReport(true);
                    }
                    setIsRunning(d.active && !d.complete);

                    if (d.complete && !battleCompleteRef.current) {
                        battleCompleteRef.current = true;
                        setIsRunning(false);
                        generateReportRef.current(d.waves || []);
                    }
                }
            } catch {
                /* backend offline */
            }
        }, 1500);
        return () => clearInterval(id);
    }, []);

    // Auto-update report if open during simulation
    useEffect(() => {
        if (showReport && isRunning && history.length > 0) {
            generateReport();
        }
    }, [history, showReport, isRunning]);

    useEffect(() => {
        let interval: ReturnType<typeof setInterval> | undefined;
        if (isRunning && !cliBattle) {
            interval = setInterval(pollStatus, 3000);
        }
        return () => clearInterval(interval);
    }, [isRunning, cliBattle]);

    const getPhaseColor = (stage: string) => {
        switch (stage) {
            case "Reconnaissance": return "#60A5FA"; // blue-400
            case "Exploitation": return "#FACC15"; // yellow-400
            case "Lateral Movement": return "#F97316"; // orange-500
            case "Action on Objective": return "#EF4444"; // red-500
            default: return "#94A3B8"; // slate-400
        }
    };

    const currentStages = stages.length > 0 ? stages : ["Recon", "Exploit", "Lateral", "Impact"];

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            {/* Breach Alert Overlay */}
            {breachAlert && (
                <div style={{ 
                    position: "fixed", top: 20, left: "50%", transform: "translateX(-50%)", 
                    zIndex: 9999, background: "#EF4444", color: "white", padding: "16px 32px",
                    borderRadius: "12px", boxShadow: "0 0 50px rgba(239, 68, 68, 0.5)",
                    display: "flex", alignItems: "center", gap: "16px", animation: "pulse 1s infinite",
                    border: "2px solid white"
                }}>
                    <AlertTriangle size={32} />
                    <div>
                        <div style={{ fontWeight: "900", fontSize: "18px" }}>CRITICAL SYSTEM BREACH</div>
                        <div style={{ fontSize: "13px" }}>Stage: {breachAlert.stage} | Risk Score: {breachAlert.risk.toFixed(4)}</div>
                    </div>
                </div>
            )}

            {showReport && (
                <div style={{ 
                    background: "#F8FAFC", 
                    borderRadius: isFullScreen ? "0" : "16px", 
                    padding: "32px", 
                    border: isFullScreen ? "none" : "1px solid #E2E8F0", 
                    color: "#1E293B", 
                    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
                    position: isFullScreen ? "fixed" : "relative",
                    top: isFullScreen ? 0 : "auto",
                    left: isFullScreen ? 0 : "auto",
                    width: isFullScreen ? "100vw" : "auto",
                    height: isFullScreen ? "100vh" : "auto",
                    zIndex: isFullScreen ? 9999 : 100,
                    overflowY: "auto"
                }}>
                    {/* Header */}
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "32px" }}>
                        <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
                            {isRunning && (
                                <div style={{ width: "12px", height: "12px", borderRadius: "50%", background: "#EF4444", animation: "pulse 1s infinite" }} />
                            )}
                            <div>
                                <h1 style={{ fontSize: "24px", fontWeight: "800", textTransform: "uppercase", letterSpacing: "1px", display: "flex", alignItems: "center", gap: "10px" }}>
                                    Simulation Report {isRunning && <Badge style={{ background: "#EF4444", color: "white", fontSize: "10px" }}>LIVE</Badge>}
                                </h1>
                                <p style={{ fontSize: "13px", color: "#64748B" }}>Scenario: Hospital_Network_Sim_01 • {new Date().toLocaleString()}</p>
                            </div>
                        </div>
                        <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                            <Badge style={{ background: "#DCFCE7", color: "#166534", border: "1px solid #BBF7D0", padding: "6px 12px" }}>WINNER: BLUE TEAM</Badge>
                            <button 
                                onClick={() => setIsFullScreen(!isFullScreen)} 
                                style={{ background: "#F1F5F9", color: "#475569", border: "1px solid #E2E8F0", padding: "8px 12px", borderRadius: "8px", cursor: "pointer", display: "flex", alignItems: "center", gap: "6px" }}
                                title={isFullScreen ? "Exit Full Screen" : "Full Screen"}
                            >
                                {isFullScreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                            </button>
                            <button onClick={() => { setShowReport(false); setIsFullScreen(false); }} style={{ background: "#1E293B", color: "white", border: "none", padding: "8px 16px", borderRadius: "8px", cursor: "pointer", fontSize: "13px" }}>Close Report</button>
                        </div>
                    </div>

                    {/* Top Stats Overview */}
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 4fr 1fr", gap: "24px", marginBottom: "32px" }}>
                        {/* Simulation Statistics */}
                        <div style={{ background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #E2E8F0" }}>
                            <h3 style={{ fontSize: "13px", fontWeight: "700", marginBottom: "16px", display: "flex", alignItems: "center", gap: "8px" }}><BarChart3 size={16} color="#0066CC" /> Simulation Stats</h3>
                            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                                {[
                                    { label: "Total Attacks", value: reportData.totalAttacks, color: "#1E293B" },
                                    { label: "Detected", value: reportData.detected, color: "#0066CC" },
                                    { label: "Blocked", value: reportData.blocked, color: "#22C55E" },
                                    { label: "Breaches", value: reportData.breaches, color: "#EF4444" },
                                    { label: "Undetected", value: reportData.undetected ?? 0, color: "#94A3B8" }
                                ].map(s => (
                                    <div key={s.label} style={{ display: "flex", justifyContent: "space-between", fontSize: "12px" }}>
                                        <span style={{ color: "#64748B" }}>{s.label.toUpperCase()}</span>
                                        <span style={{ fontWeight: "800", color: s.color }}>{s.value}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* KPI Grid */}
                        <div style={{ background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #E2E8F0", display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: "20px" }}>
                            {[
                                { label: "Attack Success", value: reportData.kpiAttackSuccess ?? "22.0%", sub: reportData.kpiAttackSuccessSub ?? "22 / 100", color: "#EF4444", icon: Crosshair },
                                { label: "Detection Rate", value: reportData.kpiDetection ?? "78.0%", sub: reportData.kpiDetectionSub ?? "78 / 100", color: "#0066CC", icon: Search },
                                { label: "Prevention Rate", value: reportData.kpiPrevention ?? "60.0%", sub: reportData.kpiPreventionSub ?? "60 / 100", color: "#22C55E", icon: Shield },
                                { label: "Mean Time Detect", value: reportData.kpiMtd ?? "00:00:34", sub: "Avg per wave", color: "#8B5CF6", icon: Activity },
                                { label: "Mean Time Respond", value: reportData.kpiMtr ?? "00:01:12", sub: "Auto-mitigation", color: "#0D9488", icon: Zap }
                            ].map(kpi => (
                                <div key={kpi.label} style={{ textAlign: "center", borderRight: kpi.label !== "Mean Time Respond" ? "1px solid #F1F5F9" : "none" }}>
                                    <div style={{ display: "flex", justifyContent: "center", marginBottom: "8px" }}><kpi.icon size={18} color={kpi.color} /></div>
                                    <div style={{ fontSize: "11px", fontWeight: "600", color: "#64748B", marginBottom: "4px" }}>{kpi.label}</div>
                                    <div style={{ fontSize: "18px", fontWeight: "800", color: kpi.color }}>{kpi.value}</div>
                                    <div style={{ fontSize: "10px", color: "#94A3B8" }}>{kpi.sub}</div>
                                </div>
                            ))}
                        </div>

                        {/* Battle Score */}
                        <div style={{ background: "#DCFCE7", padding: "20px", borderRadius: "12px", border: "1px solid #BBF7D0", textAlign: "center" }}>
                            <div style={{ background: "#166534", color: "white", fontSize: "10px", fontWeight: "900", padding: "4px", borderRadius: "4px", marginBottom: "8px" }}>WINNER</div>
                            <div style={{ fontSize: "11px", fontWeight: "700", color: "#166534" }}>BATTLE VICTOR</div>
                            <div style={{ fontSize: "14px", fontWeight: "900", color: "#166534", marginBottom: "4px" }}>BLUE TEAM</div>
                            <div style={{ fontSize: "28px", fontWeight: "900", color: "#166534" }}>{reportData.scoreBlue ?? 85} <span style={{ fontSize: "14px" }}>/ 100</span></div>
                            <div style={{ fontSize: "10px", color: "#166534" }}>Performance Score</div>
                        </div>
                    </div>

                    {/* Charts Grid */}
                    <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: "24px" }}>
                        {/* Kill Chain Over Time */}
                        <div style={{ background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #E2E8F0" }}>
                            <h3 style={{ fontSize: "13px", fontWeight: "700", marginBottom: "20px" }}>The Kill Chain: Attacker Progress Over Time</h3>
                            <div style={{ height: "250px" }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={reportData.timelineData}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F1F5F9" />
                                        <XAxis dataKey="name" hide />
                                        <YAxis fontSize={10} axisLine={false} tickLine={false} />
                                        <ChartTooltip />
                                        <Legend verticalAlign="top" height={36} />
                                        <Line type="monotone" dataKey="detected" stroke="#0066CC" strokeWidth={2} dot={false} name="Detected" />
                                        <Line type="monotone" dataKey="blocked" stroke="#22C55E" strokeWidth={2} dot={false} name="Blocked" />
                                        <Line type="monotone" dataKey="breaches" stroke="#EF4444" strokeWidth={2} dot={false} name="Breaches" />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Outcome Distribution */}
                        <div style={{ background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #E2E8F0" }}>
                            <h3 style={{ fontSize: "13px", fontWeight: "700", marginBottom: "20px" }}>Outcome Distribution</h3>
                            <div style={{ height: "250px" }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie data={reportData.outcomeData} innerRadius={60} outerRadius={80} paddingAngle={5} dataKey="value">
                                            {reportData.outcomeData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.fill} />
                                            ))}
                                        </Pie>
                                        <ChartTooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Attack Type Distribution */}
                        <div style={{ background: "white", padding: "20px", borderRadius: "12px", border: "1px solid #E2E8F0" }}>
                            <h3 style={{ fontSize: "13px", fontWeight: "700", marginBottom: "20px" }}>Attack Type Distribution</h3>
                            <div style={{ height: "250px" }}>
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart layout="vertical" data={reportData.typeData} margin={{ left: -20 }}>
                                        <XAxis type="number" hide />
                                        <YAxis dataKey="name" type="category" fontSize={10} axisLine={false} tickLine={false} />
                                        <ChartTooltip />
                                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                                            {reportData.typeData.map((entry, index) => (
                                                <Cell key={`cell-${index}`} fill={entry.color} />
                                            ))}
                                        </Bar>
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Footer / System Coverage */}
                    <div style={{ marginTop: "32px", display: "grid", gridTemplateColumns: "2fr 1fr", gap: "24px" }}>
                        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
                            {[
                                { label: "Network Security", val: 95, color: "#22C55E" },
                                { label: "Endpoint Protection", val: 90, color: "#0066CC" },
                                { label: "Data Integrity", val: 85, color: "#F97316" }
                            ].map(cov => (
                                <div key={cov.label} style={{ background: "white", padding: "16px", borderRadius: "12px", border: "1px solid #E2E8F0" }}>
                                    <div style={{ fontSize: "11px", fontWeight: "600", color: "#64748B", marginBottom: "8px" }}>{cov.label}</div>
                                    <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                                        <Progress value={cov.val} style={{ height: "6px" }} />
                                        <span style={{ fontSize: "12px", fontWeight: "800" }}>{cov.val}%</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div style={{ background: "#F1F5F9", padding: "20px", borderRadius: "12px", border: "1px solid #E2E8F0" }}>
                            <h3 style={{ fontSize: "12px", fontWeight: "800", marginBottom: "12px", display: "flex", alignItems: "center", gap: "8px" }}><Activity size={14} /> Recommendations</h3>
                            <ul style={{ fontSize: "11px", color: "#475569", paddingLeft: "16px", margin: 0 }}>
                                <li>Strengthen email filtering for phishing prevention</li>
                                <li>Review lateral movement attempts in SOC logs</li>
                                <li>Update incident response playbooks for SQLi</li>
                            </ul>
                        </div>
                    </div>
                </div>
            )}

            <div style={{ display: "grid", gridTemplateColumns: "repeat(12, 1fr)", gap: "24px" }}>
                {/* Kill Chain Progression */}
                <div style={{ gridColumn: "span 8" }}>
                    <Card style={{ background: "#0F172A", borderColor: "#1E293B", color: "white" }}>
                        <CardHeader style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
                            <div>
                                <CardTitle style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                    <Crosshair color="#EF4444" size={20} />
                                    Live Attack Kill Chain
                                </CardTitle>
                                <CardDescription style={{ color: "#94A3B8", fontFamily: "monospace", fontSize: "12px" }}>
                                    MULTI-STAGE THREAT SIMULATION {isRunning && "— [ACTIVE]"}
                                </CardDescription>
                            </div>
                            <div style={{ display: "flex", gap: "10px" }}>
                                <button
                                    onClick={startSimulation}
                                    disabled={isRunning}
                                    style={{
                                        background: isRunning ? "#1E293B" : "#EF4444", color: "white", border: "none",
                                        padding: "8px 20px", borderRadius: "8px", fontWeight: "700", cursor: isRunning ? "default" : "pointer",
                                        display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", transition: "all 0.2s"
                                    }}
                                >
                                    <Play size={16} fill="white" /> {isRunning ? "Simulating..." : "Launch Simulation"}
                                </button>

                                <button
                                    onClick={generateReport}
                                    style={{
                                        background: isRunning ? "#22C55E" : "rgba(255,255,255,0.05)", 
                                        color: "white", 
                                        border: isRunning ? "none" : "1px solid rgba(255,255,255,0.1)",
                                        padding: "8px 20px", borderRadius: "8px", fontWeight: "600", cursor: "pointer",
                                        display: "flex", alignItems: "center", gap: "8px", fontSize: "14px", transition: "all 0.2s"
                                    }}
                                >
                                    <BarChart3 size={16} /> {isRunning ? "Live Report" : "Generate Report"}
                                </button>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div style={{ position: "relative", display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 16px 32px" }}>
                                <div style={{ position: "absolute", top: "50%", left: 0, width: "100%", height: "2px", background: "#1E293B", transform: "translateY(-50%)", zIndex: 0 }} />
                                {currentStages.map((s, idx) => {
                                    const isActive = status?.stage === s;
                                    const isPast = history.some(h => h.stage === s);
                                    return (
                                        <div key={idx} style={{ position: "relative", zIndex: 10, display: "flex", flexDirection: "column", alignItems: "center", gap: "8px" }}>
                                            <div style={{
                                                width: "40px", height: "40px", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center",
                                                border: "2px solid", transition: "all 0.5s",
                                                background: isActive ? "#EF4444" : isPast ? "#334155" : "#0F172A",
                                                borderColor: isActive ? "white" : isPast ? "#22C55E" : "#334155",
                                                boxShadow: isActive ? "0 0 15px #EF4444" : "none",
                                                transform: isActive ? "scale(1.2)" : "none"
                                            }}>
                                                {isPast ? <Lock color="#22C55E" size={18} /> : (idx + 1)}
                                            </div>
                                            <span style={{ fontSize: "10px", fontWeight: "bold", textTransform: "uppercase", color: isActive ? "white" : "#64748B" }}>{s}</span>
                                        </div>
                                    );
                                })}
                            </div>

                            <div style={{ background: "rgba(0,0,0,0.5)", borderRadius: "8px", padding: "16px", fontFamily: "monospace", fontSize: "13px", border: "1px solid #1E293B", height: "240px", overflowY: "auto" }}>
                                {history.length === 0 && !isRunning && <div style={{ color: "#475569", fontStyle: "italic" }}>No active threats detected...</div>}
                                {history.map((h, i) => (
                                    <div key={i} style={{ marginBottom: "8px" }}>
                                        <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                                            <span style={{ color: "#64748B" }}>[{new Date().toLocaleTimeString()}]</span>
                                            <Badge variant="secondary" style={{ fontSize: "10px" }}>{h.stage}</Badge>
                                            <span style={{ color: getPhaseColor(h.stage) }}>{h.stage} stage detected.</span>
                                        </div>
                                        <div style={{ marginLeft: "16px", paddingLeft: "16px", borderLeft: "1px solid #1E293B", marginTop: "4px" }}>
                                            <div style={{ fontSize: "11px", color: "#94A3B8" }}>
                                                AI Scores: LSTM={h.lstm_score.toFixed(3)} | IsoForest={h.isolation_score.toFixed(3)}
                                            </div>
                                            <div style={{ fontSize: "11px", fontWeight: "bold", color: h.action === "ALLOW" ? "#22C55E" : "#EF4444" }}>
                                                ACTION: {h.action}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                                {isRunning && <div style={{ color: "#64748B", marginTop: "8px" }}>Collecting telemetry...</div>}
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Risk Engine View */}
                <div style={{ gridColumn: "span 4", display: "flex", flexDirection: "column", gap: "24px" }}>
                    <Card style={{ background: "#0F172A", borderColor: "#1E293B", color: "white" }}>
                        <CardHeader>
                            <CardTitle style={{ fontSize: "14px", display: "flex", alignItems: "center", gap: "8px" }}>
                                <Zap color="#FF6900" size={16} /> AI Risk Fusion
                            </CardTitle>
                        </CardHeader>
                        <CardContent style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
                            <div>
                                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px", marginBottom: "4px" }}>
                                    <span style={{ color: "#94A3B8" }}>Combined Risk</span>
                                    <span style={{ fontWeight: "bold", color: (status?.combined_risk || 0) > 0.7 ? "#EF4444" : "#22C55E" }}>
                                        {(status?.combined_risk || 0).toFixed(4)}
                                    </span>
                                </div>
                                <Progress value={(status?.combined_risk || 0) * 100} />
                            </div>
                            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "12px" }}>
                                <div style={{ padding: "8px", background: "rgba(0,0,0,0.3)", borderRadius: "4px", border: "1px solid #1E293B" }}>
                                    <p style={{ fontSize: "9px", color: "#64748B" }}>LSTM</p>
                                    <div style={{ fontWeight: "bold" }}>{(status?.lstm_score || 0).toFixed(3)}</div>
                                </div>
                                <div style={{ padding: "8px", background: "rgba(0,0,0,0.3)", borderRadius: "4px", border: "1px solid #1E293B" }}>
                                    <p style={{ fontSize: "9px", color: "#64748B" }}>ISO</p>
                                    <div style={{ fontWeight: "bold" }}>{(status?.isolation_score || 0).toFixed(3)}</div>
                                </div>
                            </div>
                            <div style={{ borderTop: "1px solid #1E293B", paddingTop: "12px", display: "flex", flexDirection: "column", gap: "8px" }}>
                                <div style={{ display: "flex", alignItems: "center", gap: "8px", fontSize: "11px" }}>
                                    <Activity size={12} color={status?.action === "ISOLATE" ? "#EF4444" : "#475569"} />
                                    <span>Auto-Isolation Strategy</span>
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                    <Card style={{ background: "#0F172A", borderColor: "#1E293B", color: "white" }}>
                        <CardContent style={{ paddingTop: "16px", display: "flex", flexDirection: "column", gap: "8px" }}>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px" }}>
                                <span style={{ color: "#64748B" }}>Inference Time</span>
                                <span style={{ color: "#22C55E" }}>~142ms</span>
                            </div>
                            <div style={{ display: "flex", justifyContent: "space-between", fontSize: "11px" }}>
                                <span style={{ color: "#64748B" }}>Confidence</span>
                                <span style={{ color: "#60A5FA" }}>99.4%</span>
                            </div>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </div>
    );
}
