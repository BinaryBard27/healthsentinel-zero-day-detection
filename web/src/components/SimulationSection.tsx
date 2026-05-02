import { useState, useEffect } from "react";
import { MedGuardButton } from "./MedGuardButton";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { Mail, Database, Shield, CheckCircle, AlertTriangle, Zap } from "lucide-react";
import { motion } from "motion/react";

export function SimulationSection() {
  const [currentDemo, setCurrentDemo] = useState<"phishing" | "sql">("phishing");
  const [simulationStep, setSimulationStep] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  const phishingSteps = [
    { title: "Phishing Email Received", status: "detected", icon: Mail },
    { title: "AI Content Analysis", status: "processing", icon: Zap },
    { title: "Threat Identified", status: "blocked", icon: AlertTriangle },
    { title: "Email Quarantined", status: "complete", icon: Shield }
  ];

  const sqlSteps = [
    { title: "SQL Injection Attempt", status: "detected", icon: Database },
    { title: "Query Pattern Analysis", status: "processing", icon: Zap },
    { title: "Malicious Code Detected", status: "blocked", icon: AlertTriangle },
    { title: "Connection Blocked", status: "complete", icon: Shield }
  ];

  const currentSteps = currentDemo === "phishing" ? phishingSteps : sqlSteps;

  useEffect(() => {
    if (isRunning) {
      const timer = setInterval(() => {
        setSimulationStep((prev) => {
          if (prev >= currentSteps.length - 1) {
            setIsRunning(false);
            return 0;
          }
          return prev + 1;
        });
      }, 1500);

      return () => clearInterval(timer);
    }
  }, [isRunning, currentSteps.length]);

  const runSimulation = () => {
    setSimulationStep(0);
    setIsRunning(true);
  };

  const getStepStatus = (index: number) => {
    if (!isRunning) return "pending";
    if (index < simulationStep) return "complete";
    if (index === simulationStep) return "active";
    return "pending";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "complete": return "text-secondary";
      case "active": return "text-primary animate-pulse";
      case "pending": return "text-muted-foreground";
      default: return "text-muted-foreground";
    }
  };

  return (
    <section className="py-20 bg-muted/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-foreground mb-6 text-glow-primary">
            Live Attack Simulation
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Watch MedGuard AI in action as it detects and blocks real-world cyber attacks in real-time.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Attack Simulation */}
          <div>
            <Card className="bg-gradient-cyber border-glow">
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Attack Scenario</span>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => setCurrentDemo("phishing")}
                      className={`px-3 py-1 rounded text-sm ${
                        currentDemo === "phishing" 
                          ? "bg-primary text-primary-foreground" 
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      Phishing
                    </button>
                    <button
                      onClick={() => setCurrentDemo("sql")}
                      className={`px-3 py-1 rounded text-sm ${
                        currentDemo === "sql" 
                          ? "bg-primary text-primary-foreground" 
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      SQL Injection
                    </button>
                  </div>
                </CardTitle>
              </CardHeader>
              <CardContent>
                {currentDemo === "phishing" ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-background/50 rounded-lg border border-accent/30">
                      <div className="flex items-center space-x-2 mb-2">
                        <Mail className="w-4 h-4 text-accent" />
                        <span className="font-medium text-foreground">Suspicious Email</span>
                        <Badge className="bg-accent text-accent-foreground">High Risk</Badge>
                      </div>
                      <div className="text-sm space-y-2">
                        <div><strong>From:</strong> ceo@medguard-security.com</div>
                        <div><strong>Subject:</strong> Urgent: Update Your Login Credentials</div>
                        <div className="p-2 bg-accent/10 rounded text-xs">
                          "Please click the link below to update your password immediately 
                          or your account will be suspended..."
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <strong>Threat Indicators:</strong> Suspicious domain, urgency tactics, 
                      credential harvesting attempt
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div className="p-4 bg-background/50 rounded-lg border border-accent/30">
                      <div className="flex items-center space-x-2 mb-2">
                        <Database className="w-4 h-4 text-accent" />
                        <span className="font-medium text-foreground">Malicious Query</span>
                        <Badge className="bg-accent text-accent-foreground">Critical</Badge>
                      </div>
                      <div className="text-sm space-y-2">
                        <div><strong>Source:</strong> 192.168.1.157</div>
                        <div><strong>Target:</strong> Patient Database</div>
                        <div className="p-2 bg-accent/10 rounded text-xs font-mono">
                          SELECT * FROM patients WHERE id = '1' OR '1'='1'; DROP TABLE patients;--
                        </div>
                      </div>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      <strong>Attack Vector:</strong> Union-based SQL injection with table deletion attempt
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* AI Defense Response */}
          <div>
            <Card className="bg-gradient-cyber border-glow">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-primary" />
                  <span>MedGuard AI Response</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4 mb-6">
                  {currentSteps.map((step, index) => {
                    const Icon = step.icon;
                    const status = getStepStatus(index);
                    
                    return (
                      <motion.div
                        key={index}
                        className="flex items-center space-x-3 p-3 rounded-lg bg-background/30"
                        initial={{ opacity: 0.5 }}
                        animate={{ 
                          opacity: status === "pending" ? 0.5 : 1,
                          scale: status === "active" ? 1.05 : 1
                        }}
                        transition={{ duration: 0.3 }}
                      >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          status === "complete" ? "bg-secondary/20" : 
                          status === "active" ? "bg-primary/20 animate-pulse-glow" : 
                          "bg-muted/20"
                        }`}>
                          {status === "complete" ? (
                            <CheckCircle className="w-4 h-4 text-secondary" />
                          ) : (
                            <Icon className={`w-4 h-4 ${getStatusColor(status)}`} />
                          )}
                        </div>
                        <div className="flex-1">
                          <div className={`font-medium ${getStatusColor(status)}`}>
                            {step.title}
                          </div>
                          {status === "active" && (
                            <div className="text-xs text-primary">Processing...</div>
                          )}
                          {status === "complete" && (
                            <div className="text-xs text-secondary">Complete</div>
                          )}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>

                {!isRunning && simulationStep === 0 && (
                  <MedGuardButton 
                    label="Run Live Demo" 
                    variant="glow"
                    onClick={runSimulation}
                    className="w-full"
                  />
                )}

                {!isRunning && simulationStep > 0 && (
                  <div className="text-center">
                    <div className="text-secondary font-semibold mb-2">
                      ✅ Threat Successfully Blocked!
                    </div>
                    <MedGuardButton 
                      label="Run Demo Again" 
                      variant="outline"
                      onClick={runSimulation}
                      className="w-full"
                    />
                  </div>
                )}

                {isRunning && (
                  <div className="text-center">
                    <div className="text-primary font-semibold animate-pulse">
                      🛡️ MedGuard AI Active...
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="mt-12 grid md:grid-cols-4 gap-6">
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-primary mb-2">&lt; 100ms</div>
              <div className="text-sm text-muted-foreground">Detection Time</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-secondary mb-2">99.97%</div>
              <div className="text-sm text-muted-foreground">Accuracy Rate</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-accent mb-2">0.003%</div>
              <div className="text-sm text-muted-foreground">False Positives</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="text-2xl font-bold text-primary mb-2">24/7</div>
              <div className="text-sm text-muted-foreground">Protection</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}