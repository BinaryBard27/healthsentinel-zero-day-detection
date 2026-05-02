import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Building2, Stethoscope, FlaskConical, Smartphone, ArrowRight, Users, Shield, Zap } from "lucide-react";

export function SolutionsByIndustry() {
  const solutions = [
    {
      icon: Building2,
      title: "Hospitals & Health Systems",
      description: "Enterprise-scale cybersecurity for large healthcare organizations with complex infrastructure.",
      features: ["Multi-site deployment", "Centralized management", "Advanced analytics", "24/7 SOC support"],
      metrics: { customers: "200+", threats: "10M+", uptime: "99.99%" },
      badge: "Enterprise"
    },
    {
      icon: Stethoscope,
      title: "Clinics & Private Practice",
      description: "Affordable, easy-to-deploy security solutions for small to medium healthcare practices.",
      features: ["Quick deployment", "Minimal IT overhead", "Automated updates", "Compliance reporting"],
      metrics: { customers: "500+", threats: "2M+", uptime: "99.9%" },
      badge: "SMB"
    },
    {
      icon: FlaskConical,
      title: "Pharmaceutical & Research",
      description: "Protect valuable research data and intellectual property from sophisticated cyber threats.",
      features: ["IP protection", "Research data security", "Regulatory compliance", "Advanced threat intel"],
      metrics: { customers: "50+", threats: "5M+", uptime: "99.95%" },
      badge: "Specialized"
    },
    {
      icon: Smartphone,
      title: "Telehealth Platforms",
      description: "Secure remote healthcare delivery with end-to-end encryption and privacy protection.",
      features: ["Video security", "Data encryption", "Access controls", "Patient privacy"],
      metrics: { customers: "100+", threats: "3M+", uptime: "99.9%" },
      badge: "Digital Health"
    }
  ];

  const useCases = [
    {
      title: "Ransomware Protection",
      description: "Advanced AI detection and prevention of ransomware attacks targeting healthcare data.",
      stats: "99.8% prevention rate",
      icon: Shield
    },
    {
      title: "Insider Threat Detection",
      description: "Monitor and detect suspicious behavior from authorized users and employees.",
      stats: "95% accuracy rate",
      icon: Users
    },
    {
      title: "Zero-Day Defense",
      description: "Proactive protection against unknown vulnerabilities and attack vectors.",
      stats: "< 1 minute response",
      icon: Zap
    }
  ];

  return (
    <section className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <Badge variant="secondary" className="mb-4">Solutions</Badge>
          <h2 className="text-4xl font-bold text-foreground mb-6">
            Tailored for Healthcare Segments
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Purpose-built security solutions that understand the unique challenges 
            and requirements of different healthcare organizations.
          </p>
        </div>

        {/* Solutions Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-20">
          {solutions.map((solution, index) => {
            const Icon = solution.icon;
            return (
              <Card key={index} className="hover-lift bg-white">
                <CardHeader>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                    <Badge variant="outline">{solution.badge}</Badge>
                  </div>
                  <CardTitle className="text-xl mb-2">{solution.title}</CardTitle>
                  <p className="text-muted-foreground">{solution.description}</p>
                </CardHeader>
                <CardContent>
                  {/* Features */}
                  <div className="space-y-2 mb-6">
                    {solution.features.map((feature, featureIndex) => (
                      <div key={featureIndex} className="flex items-center space-x-2">
                        <div className="w-1.5 h-1.5 bg-primary rounded-full"></div>
                        <span className="text-sm text-foreground">{feature}</span>
                      </div>
                    ))}
                  </div>

                  {/* Metrics */}
                  <div className="grid grid-cols-3 gap-4 mb-6 p-4 bg-muted/50 rounded-lg">
                    <div className="text-center">
                      <div className="font-bold text-primary">{solution.metrics.customers}</div>
                      <div className="text-xs text-muted-foreground">Customers</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-primary">{solution.metrics.threats}</div>
                      <div className="text-xs text-muted-foreground">Threats Blocked</div>
                    </div>
                    <div className="text-center">
                      <div className="font-bold text-primary">{solution.metrics.uptime}</div>
                      <div className="text-xs text-muted-foreground">Uptime</div>
                    </div>
                  </div>

                  <Button variant="outline" className="w-full group">
                    Learn More
                    <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </Button>
                </CardContent>
              </Card>
            );
          })}
        </div>

        {/* Use Cases Section */}
        <div className="border-t border-border pt-16">
          <div className="text-center mb-12">
            <h3 className="text-2xl font-bold text-foreground mb-4">
              Common Security Challenges We Solve
            </h3>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our platform addresses the most critical cybersecurity threats facing healthcare organizations today.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {useCases.map((useCase, index) => {
              const Icon = useCase.icon;
              return (
                <Card key={index} className="text-center hover-lift bg-white">
                  <CardContent className="pt-8">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                      <Icon className="w-8 h-8 text-primary" />
                    </div>
                    <h4 className="font-semibold text-foreground mb-3">{useCase.title}</h4>
                    <p className="text-muted-foreground text-sm mb-4">{useCase.description}</p>
                    <div className="inline-flex items-center space-x-2 bg-primary/5 border border-primary/20 rounded-full px-3 py-1">
                      <span className="text-sm font-medium text-primary">{useCase.stats}</span>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-20 text-center bg-white rounded-2xl p-12 shadow-lg">
          <h3 className="text-2xl font-bold text-foreground mb-4">
            Ready to Secure Your Healthcare Organization?
          </h3>
          <p className="text-muted-foreground mb-8 max-w-2xl mx-auto">
            Join hundreds of healthcare organizations that trust HealthSentinel to protect their 
            critical systems and patient data.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="enterprise-gradient text-white">
              Schedule Consultation
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
            <Button variant="outline" size="lg">
              View Customer Stories
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}