import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { AlertTriangle, Shield, Zap, Activity, Users, Server } from "lucide-react";

export function FeaturesSection() {
  const [activeTab, setActiveTab] = useState("phishing");

  // Mock data for threat detection chart
  const threatData = [
    { time: "00:00", detected: 45, blocked: 43 },
    { time: "04:00", detected: 32, blocked: 32 },
    { time: "08:00", detected: 78, blocked: 76 },
    { time: "12:00", detected: 65, blocked: 64 },
    { time: "16:00", detected: 89, blocked: 87 },
    { time: "20:00", detected: 56, blocked: 55 },
    { time: "24:00", detected: 41, blocked: 41 }
  ];

  // Mock data for threat types
  const threatTypes = [
    { name: "Phishing", value: 35, color: "#FF4D6D" },
    { name: "Ransomware", value: 25, color: "#00FFE0" },
    { name: "SQL Injection", value: 20, color: "#3AFF87" },
    { name: "Malware", value: 15, color: "#8B5CF6" },
    { name: "Other", value: 5, color: "#F59E0B" }
  ];

  // Mock alerts data
  const recentAlerts = [
    { id: 1, type: "Phishing", severity: "High", time: "2 min ago", source: "email-gateway", status: "Blocked" },
    { id: 2, type: "SQL Injection", severity: "Critical", time: "5 min ago", source: "web-server", status: "Blocked" },
    { id: 3, type: "Suspicious Login", severity: "Medium", time: "8 min ago", source: "user-auth", status: "Investigating" },
    { id: 4, type: "Malware Detection", severity: "High", time: "12 min ago", source: "endpoint", status: "Quarantined" },
    { id: 5, type: "Network Anomaly", severity: "Low", time: "15 min ago", source: "firewall", status: "Monitoring" }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "Critical": return "bg-accent text-accent-foreground";
      case "High": return "bg-destructive text-destructive-foreground";
      case "Medium": return "bg-secondary text-secondary-foreground";
      case "Low": return "bg-muted text-muted-foreground";
      default: return "bg-muted text-muted-foreground";
    }
  };

  return (
    <section id="features" className="py-20 bg-muted/10">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-foreground mb-6 text-glow-primary">
            Real-Time Threat Intelligence Dashboard
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Monitor, analyze, and respond to cybersecurity threats with our comprehensive AI-powered dashboard.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Threat Alerts Panel */}
          <div className="lg:col-span-1">
            <Card className="bg-gradient-cyber border-glow h-full">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-accent" />
                  <span>Live Threat Alerts</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {recentAlerts.map((alert) => (
                  <div key={alert.id} className="p-3 rounded-lg bg-background/50 border border-border/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium text-foreground">{alert.type}</span>
                      <Badge className={getSeverityColor(alert.severity)}>
                        {alert.severity}
                      </Badge>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <div>Source: {alert.source}</div>
                      <div className="flex justify-between items-center mt-1">
                        <span>{alert.time}</span>
                        <span className="text-primary">{alert.status}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Dashboard Charts */}
          <div className="lg:col-span-2 space-y-8">
            {/* Real-time Graph */}
            <Card className="bg-gradient-cyber border-glow">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Activity className="w-5 h-5 text-primary" />
                  <span>Threats Detected vs Blocked (24h)</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={threatData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(0, 255, 224, 0.1)" />
                    <XAxis dataKey="time" stroke="#A0A0A0" />
                    <YAxis stroke="#A0A0A0" />
                    <Tooltip 
                      contentStyle={{ 
                        backgroundColor: '#1A2332', 
                        border: '1px solid rgba(0, 255, 224, 0.2)',
                        borderRadius: '8px'
                      }} 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="detected" 
                      stackId="1" 
                      stroke="#FF4D6D" 
                      fill="rgba(255, 77, 109, 0.3)" 
                      name="Detected"
                    />
                    <Area 
                      type="monotone" 
                      dataKey="blocked" 
                      stackId="2" 
                      stroke="#00FFE0" 
                      fill="rgba(0, 255, 224, 0.3)" 
                      name="Blocked"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Threat Distribution */}
            <Card className="bg-gradient-cyber border-glow">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-secondary" />
                  <span>Threat Type Distribution</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <ResponsiveContainer width="100%" height={200}>
                    <PieChart>
                      <Pie
                        data={threatTypes}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        dataKey="value"
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      >
                        {threatTypes.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  
                  <div className="space-y-3">
                    {threatTypes.map((type, index) => (
                      <div key={index} className="flex items-center space-x-3">
                        <div 
                          className="w-4 h-4 rounded-full" 
                          style={{ backgroundColor: type.color }}
                        ></div>
                        <span className="text-foreground">{type.name}</span>
                        <span className="text-muted-foreground">({type.value}%)</span>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Detailed Tabs */}
        <div className="mt-12">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-3 bg-muted/50 border-glow">
              <TabsTrigger value="phishing" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                Phishing Detection
              </TabsTrigger>
              <TabsTrigger value="sql" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                SQL Injection
              </TabsTrigger>
              <TabsTrigger value="behavior" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">
                Behavior Analysis
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="phishing" className="mt-6">
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-gradient-cyber border-glow">
                  <CardHeader>
                    <CardTitle>Email Threat Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Emails Scanned</span>
                        <span className="text-primary font-bold">15,247</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Phishing Detected</span>
                        <span className="text-accent font-bold">127</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Success Rate</span>
                        <span className="text-secondary font-bold">99.2%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-gradient-cyber border-glow">
                  <CardHeader>
                    <CardTitle>Recent Phishing Patterns</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-sm">
                        <div className="font-medium text-foreground">CEO Impersonation</div>
                        <div className="text-muted-foreground">Blocked 45 attempts in last hour</div>
                      </div>
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Fake IT Support</div>
                        <div className="text-muted-foreground">Blocked 23 attempts in last hour</div>
                      </div>
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Invoice Scams</div>
                        <div className="text-muted-foreground">Blocked 18 attempts in last hour</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="sql" className="mt-6">
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-gradient-cyber border-glow">
                  <CardHeader>
                    <CardTitle>Database Protection</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Queries Analyzed</span>
                        <span className="text-primary font-bold">892,341</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Malicious Blocked</span>
                        <span className="text-accent font-bold">1,247</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Zero Breaches</span>
                        <span className="text-secondary font-bold">100%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-gradient-cyber border-glow">
                  <CardHeader>
                    <CardTitle>Attack Vectors Detected</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Union-based SQLi</div>
                        <div className="text-muted-foreground">67 attempts blocked today</div>
                      </div>
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Boolean-based SQLi</div>
                        <div className="text-muted-foreground">34 attempts blocked today</div>
                      </div>
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Time-based SQLi</div>
                        <div className="text-muted-foreground">12 attempts blocked today</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
            
            <TabsContent value="behavior" className="mt-6">
              <div className="grid md:grid-cols-2 gap-6">
                <Card className="bg-gradient-cyber border-glow">
                  <CardHeader>
                    <CardTitle>User Behavior Analysis</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Users Monitored</span>
                        <span className="text-primary font-bold">2,847</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Anomalies Detected</span>
                        <span className="text-accent font-bold">23</span>
                      </div>
                      <div className="flex justify-between items-center p-3 rounded bg-background/30">
                        <span>Accuracy Rate</span>
                        <span className="text-secondary font-bold">98.7%</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="bg-gradient-cyber border-glow">
                  <CardHeader>
                    <CardTitle>Behavior Patterns</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Unusual Access Times</div>
                        <div className="text-muted-foreground">8 cases flagged for review</div>
                      </div>
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Suspicious File Access</div>
                        <div className="text-muted-foreground">5 cases investigated</div>
                      </div>
                      <div className="text-sm">
                        <div className="font-medium text-foreground">Location Anomalies</div>
                        <div className="text-muted-foreground">3 cases under monitoring</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </section>
  );
}