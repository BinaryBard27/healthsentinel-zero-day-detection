import { MedGuardCard } from "./MedGuardCard";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { LineChart, Line, XAxis, YAxis, ResponsiveContainer, BarChart, Bar } from "recharts";
import { TrendingDown, Shield, Clock, DollarSign } from "lucide-react";

export function CaseStudiesSection() {
  // Mock data for Hospital A - Ransomware Prevention
  const hospitalAData = [
    { month: "Jan", beforeMedGuard: 15, afterMedGuard: 0 },
    { month: "Feb", beforeMedGuard: 22, afterMedGuard: 0 },
    { month: "Mar", beforeMedGuard: 18, afterMedGuard: 0 },
    { month: "Apr", beforeMedGuard: 31, afterMedGuard: 0 },
    { month: "May", beforeMedGuard: 28, afterMedGuard: 0 },
    { month: "Jun", beforeMedGuard: 35, afterMedGuard: 0 }
  ];

  // Mock data for Hospital B - Phishing Timeline
  const hospitalBData = [
    { time: "Week 1", threats: 124, blocked: 122 },
    { time: "Week 2", threats: 89, blocked: 89 },
    { time: "Week 3", threats: 156, blocked: 156 },
    { time: "Week 4", threats: 203, blocked: 201 }
  ];

  const caseStudies = [
    {
      id: "hospital-a",
      title: "Regional Medical Center",
      subtitle: "Ransomware Attack Prevention",
      description: "How MedGuard prevented a sophisticated ransomware campaign targeting patient records and billing systems.",
      metrics: {
        threatsStopped: "847",
        downtimePrevented: "72 hours",
        costSaved: "$2.3M",
        detectionTime: "0.03s"
      },
      timeline: "Implementation completed in 48 hours"
    },
    {
      id: "hospital-b", 
      title: "Metropolitan Health Network",
      subtitle: "Advanced Phishing Campaign Blocked",
      description: "MedGuard's AI identified and neutralized a coordinated spear-phishing attack targeting healthcare staff credentials.",
      metrics: {
        threatsStopped: "572",
        downtimePrevented: "24 hours", 
        costSaved: "$1.8M",
        detectionTime: "0.05s"
      },
      timeline: "Zero successful breaches in 6 months"
    }
  ];

  return (
    <section id="case-studies" className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-foreground mb-6 text-glow-primary">
            Proven Results in Healthcare Security
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Real-world case studies demonstrating MedGuard's effectiveness in protecting 
            healthcare organizations from sophisticated cyber threats.
          </p>
        </div>

        <div className="space-y-16">
          {/* Hospital A Case Study */}
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <Card className="bg-gradient-cyber border-glow">
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <Badge className="bg-accent text-accent-foreground">Case Study 1</Badge>
                    <Badge className="bg-secondary text-secondary-foreground">Success</Badge>
                  </div>
                  <CardTitle className="text-foreground">{caseStudies[0].title}</CardTitle>
                  <p className="text-primary">{caseStudies[0].subtitle}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-6">{caseStudies[0].description}</p>
                  
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-accent mb-1">{caseStudies[0].metrics.threatsStopped}</div>
                      <div className="text-xs text-muted-foreground">Threats Stopped</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-primary mb-1">{caseStudies[0].metrics.downtimePrevented}</div>
                      <div className="text-xs text-muted-foreground">Downtime Prevented</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-secondary mb-1">{caseStudies[0].metrics.costSaved}</div>
                      <div className="text-xs text-muted-foreground">Cost Saved</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-primary mb-1">{caseStudies[0].metrics.detectionTime}</div>
                      <div className="text-xs text-muted-foreground">Detection Time</div>
                    </div>
                  </div>

                  <div className="text-sm text-muted-foreground italic">
                    "{caseStudies[0].timeline}"
                  </div>
                </CardContent>
              </Card>
            </div>

            <div>
              <Card className="bg-gradient-cyber border-glow">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <TrendingDown className="w-5 h-5 text-secondary" />
                    <span>Ransomware Attacks: Before vs After</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={hospitalAData}>
                      <XAxis dataKey="month" stroke="#A0A0A0" />
                      <YAxis stroke="#A0A0A0" />
                      <Bar dataKey="beforeMedGuard" fill="#FF4D6D" name="Before MedGuard" />
                      <Bar dataKey="afterMedGuard" fill="#3AFF87" name="After MedGuard" />
                    </BarChart>
                  </ResponsiveContainer>
                  <div className="mt-4 flex justify-center space-x-6 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-accent rounded"></div>
                      <span className="text-muted-foreground">Before MedGuard</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-secondary rounded"></div>
                      <span className="text-muted-foreground">After MedGuard</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>

          {/* Hospital B Case Study */}
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="lg:order-2">
              <Card className="bg-gradient-cyber border-glow">
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <Badge className="bg-accent text-accent-foreground">Case Study 2</Badge>
                    <Badge className="bg-secondary text-secondary-foreground">Success</Badge>
                  </div>
                  <CardTitle className="text-foreground">{caseStudies[1].title}</CardTitle>
                  <p className="text-primary">{caseStudies[1].subtitle}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-6">{caseStudies[1].description}</p>
                  
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-accent mb-1">{caseStudies[1].metrics.threatsStopped}</div>
                      <div className="text-xs text-muted-foreground">Threats Stopped</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-primary mb-1">{caseStudies[1].metrics.downtimePrevented}</div>
                      <div className="text-xs text-muted-foreground">Downtime Prevented</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-secondary mb-1">{caseStudies[1].metrics.costSaved}</div>
                      <div className="text-xs text-muted-foreground">Cost Saved</div>
                    </div>
                    <div className="text-center p-3 rounded-lg bg-background/50">
                      <div className="text-xl font-bold text-primary mb-1">{caseStudies[1].metrics.detectionTime}</div>
                      <div className="text-xs text-muted-foreground">Detection Time</div>
                    </div>
                  </div>

                  <div className="text-sm text-muted-foreground italic">
                    "{caseStudies[1].timeline}"
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="lg:order-1">
              <Card className="bg-gradient-cyber border-glow">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Shield className="w-5 h-5 text-primary" />
                    <span>Phishing Campaign Defense</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={hospitalBData}>
                      <XAxis dataKey="time" stroke="#A0A0A0" />
                      <YAxis stroke="#A0A0A0" />
                      <Line 
                        type="monotone" 
                        dataKey="threats" 
                        stroke="#FF4D6D" 
                        strokeWidth={2}
                        name="Threats Detected"
                      />
                      <Line 
                        type="monotone" 
                        dataKey="blocked" 
                        stroke="#00FFE0" 
                        strokeWidth={2}
                        name="Threats Blocked"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                  <div className="mt-4 flex justify-center space-x-6 text-sm">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-accent rounded"></div>
                      <span className="text-muted-foreground">Threats Detected</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 bg-primary rounded"></div>
                      <span className="text-muted-foreground">Threats Blocked</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="mt-16 grid md:grid-cols-4 gap-6">
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <DollarSign className="w-8 h-8 text-secondary mx-auto mb-2" />
              <div className="text-2xl font-bold text-secondary mb-2">$4.1M</div>
              <div className="text-sm text-muted-foreground">Total Cost Savings</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <Shield className="w-8 h-8 text-primary mx-auto mb-2" />
              <div className="text-2xl font-bold text-primary mb-2">1,419</div>
              <div className="text-sm text-muted-foreground">Threats Prevented</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <Clock className="w-8 h-8 text-accent mx-auto mb-2" />
              <div className="text-2xl font-bold text-accent mb-2">96h</div>
              <div className="text-sm text-muted-foreground">Downtime Prevented</div>
            </CardContent>
          </Card>
          
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <TrendingDown className="w-8 h-8 text-secondary mx-auto mb-2" />
              <div className="text-2xl font-bold text-secondary mb-2">100%</div>
              <div className="text-sm text-muted-foreground">Success Rate</div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}