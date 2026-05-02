import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Card } from "./ui/card";
import { Play, ArrowRight, Shield, Lock, Zap, Award } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export function EnterpriseHero() {
  const trustedLogos = [
    "Mayo Clinic", "Johns Hopkins", "Kaiser Permanente", "Cleveland Clinic", "Mass General"
  ];

  const keyMetrics = [
    { value: "99.9%", label: "Threat Detection Rate" },
    { value: "< 1ms", label: "Response Time" },
    { value: "500+", label: "Healthcare Customers" },
    { value: "24/7", label: "AI Monitoring" }
  ];

  return (
    <section className="relative pt-8 pb-20 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Hero Content */}
          <div className="lg:pr-8">
            {/* Announcement Badge */}
            <div className="inline-flex items-center space-x-2 bg-primary/5 border border-primary/20 rounded-full px-4 py-2 mb-6">
              <Badge variant="secondary" className="bg-primary text-white text-xs">New</Badge>
              <span className="text-sm text-foreground">Introducing HealthSentinel 3.0 with Advanced AI</span>
              <ArrowRight className="w-4 h-4 text-primary" />
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold text-foreground mb-6 leading-tight">
              Next-Generation 
              <span className="text-primary block">Cybersecurity</span>
              for Healthcare
            </h1>

            <p className="text-xl text-muted-foreground mb-8 leading-relaxed">
              Protect patient data and critical systems with AI-powered threat detection that stops 
              cyberattacks before they impact care. Trusted by leading healthcare organizations worldwide.
            </p>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4 mb-12">
              <Button size="lg" className="enterprise-gradient text-white h-12 px-8">
                Request Demo
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
              <Button variant="outline" size="lg" className="h-12 px-8">
                <Play className="w-4 h-4 mr-2" />
                Watch Overview
              </Button>
            </div>

            {/* Key Metrics */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
              {keyMetrics.map((metric, index) => (
                <div key={index} className="text-center">
                  <div className="text-2xl font-bold text-primary mb-1">{metric.value}</div>
                  <div className="text-sm text-muted-foreground">{metric.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Hero Visual */}
          <div className="relative">
            <Card className="overflow-hidden border-0 shadow-2xl">
              <ImageWithFallback 
                src="https://images.unsplash.com/photo-1655036387197-566206c80980?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZGFzaGJvYXJkJTIwcHJvZmVzc2lvbmFsfGVufDF8fHx8MTc1OTQ4Mzc5NXww&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                alt="HealthSentinel cybersecurity dashboard"
                className="w-full h-96 object-cover"
              />
            </Card>

            {/* Floating elements */}
            <div className="absolute -top-4 -left-4 bg-white rounded-lg shadow-lg p-3 border">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-green-500" />
                <span className="text-sm font-medium">Threat Blocked</span>
              </div>
            </div>

            <div className="absolute -bottom-4 -right-4 bg-white rounded-lg shadow-lg p-3 border">
              <div className="flex items-center space-x-2">
                <Lock className="w-5 h-5 text-primary" />
                <span className="text-sm font-medium">HIPAA Compliant</span>
              </div>
            </div>

            <div className="absolute top-1/2 -right-8 bg-white rounded-lg shadow-lg p-3 border transform -translate-y-1/2">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-yellow-500" />
                <span className="text-sm font-medium">AI Active</span>
              </div>
            </div>
          </div>
        </div>

        {/* Trusted By Section */}
        <div className="mt-20 pt-12 border-t border-border">
          <div className="text-center mb-8">
            <p className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
              Trusted by Leading Healthcare Organizations
            </p>
          </div>
          
          <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
            {trustedLogos.map((logo, index) => (
              <div key={index} className="text-lg font-semibold text-muted-foreground">
                {logo}
              </div>
            ))}
          </div>

          {/* Certifications */}
          <div className="flex justify-center items-center space-x-8 mt-8">
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-muted-foreground">SOC 2 Type II</span>
            </div>
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-muted-foreground">HIPAA Compliant</span>
            </div>
            <div className="flex items-center space-x-2">
              <Award className="w-5 h-5 text-primary" />
              <span className="text-sm font-medium text-muted-foreground">ISO 27001</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}