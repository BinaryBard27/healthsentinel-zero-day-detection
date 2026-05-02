import { healthsenitalCard } from "./healthsenitalCard";
import { Brain, Network, Shield } from "lucide-react";

export function SolutionSection() {
  const solutions = [
    {
      title: "GANs",
      description: "Generative Adversarial Networks create adaptive threat scenarios, continuously training our defense systems against evolving attack patterns in real-time.",
      icon: <Brain className="w-6 h-6" />
    },
    {
      title: "LSTM Autoencoders",
      description: "Long Short-Term Memory networks analyze system logs and network traffic, detecting subtle anomalies that indicate sophisticated intrusion attempts.",
      icon: <Network className="w-6 h-6" />
    },
    {
      title: "Isolation Forests",
      description: "Advanced machine learning algorithms identify outlier behaviors in user activities and system processes, catching zero-day exploits before they execute.",
      icon: <Shield className="w-6 h-6" />
    }
  ];

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-foreground mb-6 text-glow-primary">
            AI-Powered Defense Architecture
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Our revolutionary AI system combines three cutting-edge machine learning approaches 
            to create an impenetrable defense against cyber threats.
          </p>
        </div>

        {/* Solution Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          {solutions.map((solution, index) => (
            <healthsenitalCard
              key={index}
              title={solution.title}
              description={solution.description}
              icon={solution.icon}
              type="feature"
              className="h-full"
            />
          ))}
        </div>

        {/* How It Works */}
        <div className="bg-gradient-cyber rounded-2xl p-8 border-glow">
          <h3 className="text-center text-foreground mb-8">How healthsenital Works</h3>
          
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-2xl font-bold text-primary">1</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">Monitor</h4>
              <p className="text-sm text-muted-foreground">Continuous surveillance of network traffic and system behavior</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-secondary/20 flex items-center justify-center">
                <span className="text-2xl font-bold text-secondary">2</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">Analyze</h4>
              <p className="text-sm text-muted-foreground">AI algorithms process patterns and detect anomalies</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/20 flex items-center justify-center">
                <span className="text-2xl font-bold text-accent">3</span>
              </div>
              <h4 className="font-semibold text-foreground mb-2">Predict</h4>
              <p className="text-sm text-muted-foreground">Forecast potential threats before they materialize</p>
            </div>
            
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center glow-primary">
                <Shield className="w-8 h-8 text-primary" />
              </div>
              <h4 className="font-semibold text-foreground mb-2">Protect</h4>
              <p className="text-sm text-muted-foreground">Automatically block threats and fortify defenses</p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}