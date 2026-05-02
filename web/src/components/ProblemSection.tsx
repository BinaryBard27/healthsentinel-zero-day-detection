import { AlertTriangle, TrendingUp, Shield } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export function ProblemSection() {
  const stats = [
    { value: "80%", label: "of hospitals attacked in 2024", icon: AlertTriangle },
    { value: "$10.9M", label: "average cost per breach", icon: TrendingUp },
    { value: "45%", label: "increase in ransomware attacks", icon: Shield }
  ];

  return (
    <section className="py-20 bg-muted/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Problem Content */}
          <div>
            <h2 className="text-foreground mb-6 text-glow-primary">
              Healthcare Under Siege
            </h2>
            
            <p className="text-lg text-muted-foreground mb-8 leading-relaxed">
              Healthcare organizations face an unprecedented wave of sophisticated cyberattacks. 
              Traditional security solutions are failing against zero-day exploits, advanced persistent threats, 
              and AI-powered attacks that evolve faster than human response teams.
            </p>

            <div className="space-y-6">
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <AlertTriangle className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <h4 className="text-foreground font-semibold mb-2">Legacy Systems Vulnerable</h4>
                  <p className="text-muted-foreground">Outdated security infrastructure can't detect modern threats</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <TrendingUp className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <h4 className="text-foreground font-semibold mb-2">Escalating Attack Costs</h4>
                  <p className="text-muted-foreground">Patient data breaches and system downtime cost millions</p>
                </div>
              </div>
              
              <div className="flex items-start space-x-4">
                <div className="w-8 h-8 rounded-full bg-accent/20 flex items-center justify-center flex-shrink-0 mt-1">
                  <Shield className="w-4 h-4 text-accent" />
                </div>
                <div>
                  <h4 className="text-foreground font-semibold mb-2">Reactive Defense</h4>
                  <p className="text-muted-foreground">Current solutions only respond after damage is done</p>
                </div>
              </div>
            </div>
          </div>

          {/* Infographic */}
          <div className="relative">
            <div className="bg-gradient-cyber rounded-2xl p-8 border-glow">
              <h3 className="text-center text-foreground mb-8">Cybersecurity Crisis in Healthcare</h3>
              
              <div className="space-y-6">
                {stats.map((stat, index) => {
                  const Icon = stat.icon;
                  return (
                    <div key={index} className="flex items-center space-x-4 p-4 rounded-lg bg-background/50 border-glow">
                      <div className="w-12 h-12 rounded-full bg-accent/20 flex items-center justify-center">
                        <Icon className="w-6 h-6 text-accent" />
                      </div>
                      <div className="flex-1">
                        <div className="text-2xl font-bold text-accent">{stat.value}</div>
                        <div className="text-sm text-muted-foreground">{stat.label}</div>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Visual element */}
              <div className="mt-8 relative h-32 rounded-lg overflow-hidden">
                <ImageWithFallback 
                  src="https://images.unsplash.com/photo-1647610229306-3906b8f72539?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlciUyMGF0dGFjayUyMGhhY2tlciUyMGRhcmt8ZW58MXx8fHwxNzU5NDgzMDM2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
                  alt="Cyber attack visualization"
                  className="w-full h-full object-cover opacity-30"
                />
                <div className="absolute inset-0 bg-gradient-to-r from-accent/20 to-transparent flex items-center justify-center">
                  <div className="text-center">
                    <div className="text-lg font-semibold text-foreground">Time to Act</div>
                    <div className="text-sm text-muted-foreground">Before it's too late</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}