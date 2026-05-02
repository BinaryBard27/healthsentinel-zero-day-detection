import { useState, useEffect } from "react";
import axios from "axios";
import {
    Database, Server, Shield, Globe,
    AlertTriangle, CheckCircle, Activity, RefreshCw
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";
import { Badge } from "./ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface HoneypotAsset {
    id: string;
    name: string;
    type: string;
    status: "idle" | "triggered";
    ip: string;
}

export function HoneypotGrid() {
    const [assets, setAssets] = useState<HoneypotAsset[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchAssets = async () => {
        try {
            const res = await axios.get(`${API_BASE}/api/ai/simulate/honeypots`);
            setAssets(res.data);
        } catch (err) {
            console.error("Failed to fetch honeypots", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAssets();
        const interval = setInterval(fetchAssets, 5000);
        return () => clearInterval(interval);
    }, []);

    const getIcon = (type: string) => {
        switch (type) {
            case "Database": return <Database size={16} />;
            case "Web Server": return <Globe size={16} />;
            case "Management": return <Server size={16} />;
            default: return <Shield size={16} />;
        }
    };

    return (
        <div style={{ display: "flex", flexDirection: "column", gap: "24px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px" }}>
                <Card style={{ background: "#0F172A", color: "white", borderColor: "#1E293B" }}>
                    <CardContent style={{ paddingTop: "24px" }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <div>
                                <p style={{ fontSize: "14px", color: "#64748B" }}>Deception Assets</p>
                                <h3 style={{ fontSize: "24px", fontWeight: "bold" }}>{assets.length}</h3>
                            </div>
                            <Shield color="#3B82F6" size={24} />
                        </div>
                    </CardContent>
                </Card>

                <Card style={{ background: "#0F172A", color: "white", borderColor: "#1E293B" }}>
                    <CardContent style={{ paddingTop: "24px" }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <div>
                                <p style={{ fontSize: "14px", color: "#64748B" }}>Active Triggers</p>
                                <h3 style={{ fontSize: "24px", fontWeight: "bold", color: "#F97316" }}>
                                    {assets.filter(a => a.status === "triggered").length}
                                </h3>
                            </div>
                            <AlertTriangle color="#F97316" size={24} />
                        </div>
                    </CardContent>
                </Card>

                <Card style={{ background: "#0F172A", color: "white", borderColor: "#1E293B" }}>
                    <CardContent style={{ paddingTop: "24px" }}>
                        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                            <div>
                                <p style={{ fontSize: "14px", color: "#64748B" }}>Status</p>
                                <h3 style={{ fontSize: "24px", fontWeight: "bold", color: "#22C55E" }}>Active</h3>
                            </div>
                            <Activity color="#22C55E" size={24} />
                        </div>
                    </CardContent>
                </Card>
            </div>

            <Card style={{ background: "#0F172A", color: "white", borderColor: "#1E293B" }}>
                <CardHeader style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                        <CardTitle>Deception Asset Grid</CardTitle>
                        <CardDescription style={{ color: "#64748B" }}>Real-time monitoring of shadow assets.</CardDescription>
                    </div>
                    <button onClick={fetchAssets} style={{ background: "none", border: "none", cursor: "pointer", color: "#64748B" }}>
                        <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
                    </button>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead style={{ color: "#64748B" }}>Asset Name</TableHead>
                                <TableHead style={{ color: "#64748B" }}>Type</TableHead>
                                <TableHead style={{ color: "#64748B" }}>IP Address</TableHead>
                                <TableHead style={{ color: "#64748B" }}>Status</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {assets.map((asset) => (
                                <TableRow key={asset.id} style={{ borderColor: "#1E293B" }}>
                                    <TableCell style={{ fontWeight: "600", display: "flex", alignItems: "center", gap: "8px" }}>
                                        {getIcon(asset.type)}
                                        {asset.name}
                                    </TableCell>
                                    <TableCell>{asset.type}</TableCell>
                                    <TableCell style={{ fontFamily: "monospace", fontSize: "12px" }}>{asset.ip}</TableCell>
                                    <TableCell>
                                        {asset.status === "triggered" ? (
                                            <Badge variant="destructive">TRIGGERED</Badge>
                                        ) : (
                                            <Badge style={{ background: "#065F46", color: "#34D399" }}>IDLE</Badge>
                                        )}
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}
