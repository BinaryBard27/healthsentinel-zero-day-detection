import { MedGuardCard } from "./MedGuardCard";
import { Card, CardContent } from "./ui/card";
import { Linkedin, Github, Mail } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";

export function TeamSection() {
  const teamMembers = [
    {
      name: "Dr. Sarah Chen",
      role: "Chief Security Officer & Co-Founder",
      image: "https://images.unsplash.com/photo-1585900464046-f713a61424dd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZXhwZXJ0JTIwcG9ydHJhaXR8ZW58MXx8fHwxNzU5NDgzMTg2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      bio: "Former CISO at Mayo Clinic with 15+ years securing healthcare infrastructure. PhD in Cybersecurity from MIT.",
      expertise: ["Healthcare Security", "Incident Response", "Compliance"]
    },
    {
      name: "Marcus Rodriguez",
      role: "AI/ML Engineering Lead",
      image: "https://images.unsplash.com/photo-1739287088635-444554e7ac0e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjB0ZWFtJTIwdGVjaG5vbG9neSUyMG9mZmljZXxlbnwxfHx8fDE3NTk0ODMxODZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      bio: "Ex-Google AI researcher specializing in adversarial networks and anomaly detection. MS Computer Science from Stanford.",
      expertise: ["Machine Learning", "GANs", "Neural Networks"]
    },
    {
      name: "Dr. Emily Watson",
      role: "Healthcare Technology Advisor",
      image: "https://images.unsplash.com/photo-1585900464046-f713a61424dd?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjeWJlcnNlY3VyaXR5JTIwZXhwZXJ0JTIwcG9ydHJhaXR8ZW58MXx8fHwxNzU5NDgzMTg2fDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      bio: "Practicing physician and former CTO at Johns Hopkins. Expert in healthcare workflow integration and patient privacy.",
      expertise: ["Healthcare Workflows", "HIPAA Compliance", "Clinical Systems"]
    },
    {
      name: "Alex Kim",
      role: "Principal Security Engineer", 
      image: "https://images.unsplash.com/photo-1739287088635-444554e7ac0e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxwcm9mZXNzaW9uYWwlMjB0ZWFtJTIwdGVjaG5vbG9neSUyMG9mZmljZXxlbnwxfHx8fDE3NTk0ODMxODZ8MA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral",
      bio: "Ethical hacker and former NSA cybersecurity analyst. Discovered multiple zero-day vulnerabilities in healthcare systems.",
      expertise: ["Penetration Testing", "Threat Intelligence", "Zero-Day Research"]
    }
  ];

  return (
    <section id="team" className="py-20 bg-muted/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-foreground mb-6 text-glow-primary">
            Meet the MedGuard Team
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Our world-class team combines deep healthcare expertise with cutting-edge AI research 
            to protect what matters most - patient safety and data security.
          </p>
          
          {/* Mission Statement */}
          <Card className="bg-gradient-cyber border-glow max-w-4xl mx-auto">
            <CardContent className="pt-6">
              <blockquote className="text-lg italic text-foreground text-center">
                "Making healthcare immune to cyber threats through intelligent, proactive defense systems 
                that understand the unique challenges and critical nature of medical environments."
              </blockquote>
              <div className="text-center mt-4 text-primary font-semibold">
                - MedGuard Mission Statement
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Team Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
          {teamMembers.map((member, index) => (
            <Card key={index} className="bg-gradient-cyber border-glow hover:glow-secondary transition-all duration-300 hover:scale-105">
              <CardContent className="pt-6">
                {/* Profile Image */}
                <div className="relative mb-4">
                  <div className="w-24 h-24 mx-auto rounded-full overflow-hidden border-2 border-primary/30">
                    <ImageWithFallback 
                      src={member.image}
                      alt={member.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 w-6 h-6 bg-secondary rounded-full flex items-center justify-center animate-pulse">
                    <div className="w-2 h-2 bg-primary-foreground rounded-full"></div>
                  </div>
                </div>

                {/* Member Info */}
                <div className="text-center mb-4">
                  <h3 className="font-semibold text-foreground mb-1">{member.name}</h3>
                  <p className="text-primary text-sm font-medium mb-3">{member.role}</p>
                  <p className="text-muted-foreground text-xs leading-relaxed mb-4">{member.bio}</p>
                </div>

                {/* Expertise Tags */}
                <div className="flex flex-wrap justify-center gap-1 mb-4">
                  {member.expertise.map((skill, skillIndex) => (
                    <span 
                      key={skillIndex}
                      className="px-2 py-1 bg-primary/10 text-primary text-xs rounded border border-primary/20"
                    >
                      {skill}
                    </span>
                  ))}
                </div>

                {/* Social Links */}
                <div className="flex justify-center space-x-3">
                  <button className="w-8 h-8 rounded-full bg-background/50 flex items-center justify-center hover:bg-primary/20 transition-colors">
                    <Linkedin className="w-4 h-4 text-muted-foreground hover:text-primary" />
                  </button>
                  <button className="w-8 h-8 rounded-full bg-background/50 flex items-center justify-center hover:bg-primary/20 transition-colors">
                    <Github className="w-4 h-4 text-muted-foreground hover:text-primary" />
                  </button>
                  <button className="w-8 h-8 rounded-full bg-background/50 flex items-center justify-center hover:bg-primary/20 transition-colors">
                    <Mail className="w-4 h-4 text-muted-foreground hover:text-primary" />
                  </button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Company Values */}
        <div className="grid md:grid-cols-3 gap-8">
          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/20 flex items-center justify-center">
                <span className="text-2xl">🛡️</span>
              </div>
              <h3 className="font-semibold text-foreground mb-2">Security First</h3>
              <p className="text-muted-foreground text-sm">
                Every decision is guided by the principle of maximum security with zero compromise on patient care.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-secondary/20 flex items-center justify-center">
                <span className="text-2xl">🧠</span>
              </div>
              <h3 className="font-semibold text-foreground mb-2">AI Innovation</h3>
              <p className="text-muted-foreground text-sm">
                Leveraging cutting-edge artificial intelligence to stay ahead of evolving cyber threats.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gradient-cyber border-glow text-center">
            <CardContent className="pt-6">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-accent/20 flex items-center justify-center">
                <span className="text-2xl">❤️</span>
              </div>
              <h3 className="font-semibold text-foreground mb-2">Patient Care</h3>
              <p className="text-muted-foreground text-sm">
                Understanding that behind every data point is a patient whose wellbeing depends on secure systems.
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  );
}