import { MedGuardButton } from "./MedGuardButton";
import { Shield, Brain, Zap } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden">
      {/* Background with overlay */}
      <div className="absolute inset-0 z-0">
        <ImageWithFallback 
          src="https://images.unsplash.com/photo-1639503547276-90230c4a4198?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwc2hpZWxkJTIwdGVjaG5vbG9neXxlbnwxfHx8fDE3NTk0MDM3NDV8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
          alt="Cybersecurity shield background"
          className="w-full h-full object-cover opacity-20"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-background via-background/95 to-background/80" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Hero Content */}
          <div className="text-center lg:text-left">
            <h1 className="text-foreground mb-6 text-glow-primary">
              AI-Powered Zero-Day Defense for Healthcare
            </h1>
            
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
              Proactively stopping ransomware, phishing, and advanced cyberattacks before they strike. 
              Protect your hospital with cutting-edge artificial intelligence.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start">
              <MedGuardButton 
                label="Request Demo" 
                variant="glow"
                size="lg"
              />
              <MedGuardButton 
                label="Learn More" 
                variant="outline"
                size="lg"
              />
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-8 mt-12 pt-8 border-t border-glow">
              <div className="text-center">
                <div className="text-2xl font-bold text-primary text-glow-primary">99.9%</div>
                <div className="text-sm text-muted-foreground">Threat Detection</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-secondary text-glow-secondary">24/7</div>
                <div className="text-sm text-muted-foreground">AI Monitoring</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-accent">Zero</div>
                <div className="text-sm text-muted-foreground">Downtime</div>
              </div>
            </div>
          </div>

          {/* 3D Placeholder - AI Shield/Brain */}
          <div className="relative flex items-center justify-center">
            <div className="relative w-96 h-96 flex items-center justify-center">
              {/* Animated shield */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-primary/20 to-secondary/20 animate-pulse-glow"></div>
              
              {/* Central brain/shield icon */}
              <div className="relative z-10 w-32 h-32 flex items-center justify-center rounded-full bg-gradient-to-br from-primary to-secondary animate-float">
                <Brain className="w-16 h-16 text-primary-foreground" />
              </div>

              {/* Orbiting elements */}
              <div className="absolute inset-8 rounded-full border border-primary/30 animate-spin" style={{ animationDuration: '10s' }}>
                <div className="absolute -top-2 -left-2 w-4 h-4 rounded-full bg-primary animate-pulse"></div>
                <div className="absolute -top-2 -right-2 w-4 h-4 rounded-full bg-secondary animate-pulse"></div>
                <div className="absolute -bottom-2 -left-2 w-4 h-4 rounded-full bg-accent animate-pulse"></div>
                <div className="absolute -bottom-2 -right-2 w-4 h-4 rounded-full bg-primary animate-pulse"></div>
              </div>

              {/* Outer ring */}
              <div className="absolute inset-0 rounded-full border border-secondary/20 animate-spin" style={{ animationDuration: '15s', animationDirection: 'reverse' }}>
                <Shield className="absolute -top-3 left-1/2 transform -translate-x-1/2 w-6 h-6 text-primary" />
                <Zap className="absolute -bottom-3 left-1/2 transform -translate-x-1/2 w-6 h-6 text-secondary" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}