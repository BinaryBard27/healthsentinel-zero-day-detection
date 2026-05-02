import { MedGuardButton } from "./MedGuardButton";
import { MedGuardInput } from "./MedGuardInput";
import { Shield, Mail, Phone, MapPin, Linkedin, Twitter, Github } from "lucide-react";
import { useState } from "react";

export function FooterSection() {
  const [email, setEmail] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle early access signup
    console.log("Early access signup:", email);
    setEmail("");
  };

  return (
    <footer className="bg-background border-t border-glow">
      {/* Main Footer Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        {/* CTA Section */}
        <div className="text-center mb-16">
          <h2 className="text-foreground mb-6 text-glow-primary">
            Protect Your Hospital Today
          </h2>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto mb-8">
            Join the early access program and be among the first healthcare organizations 
            to deploy next-generation AI-powered cybersecurity.
          </p>
          
          <form onSubmit={handleSubmit} className="max-w-md mx-auto flex space-x-4">
            <MedGuardInput 
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="flex-1"
            />
            <MedGuardButton 
              type="submit"
              label="Join Early Access" 
              variant="glow"
            />
          </form>
          
          <p className="text-sm text-muted-foreground mt-4">
            No spam. Unsubscribe at any time. HIPAA-compliant communications.
          </p>
        </div>

        {/* Footer Links */}
        <div className="grid md:grid-cols-4 gap-8 mb-12">
          {/* Company Info */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <Shield className="w-6 h-6 text-primary animate-pulse-glow" />
              <span className="font-bold text-primary text-glow-primary">MedGuard</span>
            </div>
            <p className="text-muted-foreground text-sm mb-4">
              AI-powered zero-day defense specifically designed for healthcare organizations. 
              Protecting patient data and critical systems 24/7.
            </p>
            <div className="flex space-x-3">
              <button className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary/20 transition-colors border border-primary/20">
                <Linkedin className="w-4 h-4 text-primary" />
              </button>
              <button className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary/20 transition-colors border border-primary/20">
                <Twitter className="w-4 h-4 text-primary" />
              </button>
              <button className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center hover:bg-primary/20 transition-colors border border-primary/20">
                <Github className="w-4 h-4 text-primary" />
              </button>
            </div>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#features" className="text-muted-foreground hover:text-primary transition-colors">Features</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">Pricing</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">Demo</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">API</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">Integrations</a></li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Resources</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">Documentation</a></li>
              <li><a href="#case-studies" className="text-muted-foreground hover:text-primary transition-colors">Case Studies</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">White Papers</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">Blog</a></li>
              <li><a href="#" className="text-muted-foreground hover:text-primary transition-colors">Security Research</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-semibold text-foreground mb-4">Contact</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-center space-x-2">
                <Mail className="w-4 h-4 text-primary" />
                <span className="text-muted-foreground">security@medguard.ai</span>
              </li>
              <li className="flex items-center space-x-2">
                <Phone className="w-4 h-4 text-primary" />
                <span className="text-muted-foreground">+1 (555) 123-4567</span>
              </li>
              <li className="flex items-start space-x-2">
                <MapPin className="w-4 h-4 text-primary mt-0.5" />
                <span className="text-muted-foreground">
                  123 Innovation Drive<br />
                  San Francisco, CA 94105
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Compliance & Certifications */}
        <div className="border-t border-glow pt-8 mb-8">
          <h4 className="font-semibold text-foreground mb-4 text-center">Compliance & Certifications</h4>
          <div className="flex flex-wrap justify-center items-center space-x-8 text-sm text-muted-foreground">
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>HIPAA Compliant</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>SOC 2 Type II</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>GDPR Ready</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>ISO 27001</span>
            </div>
            <div className="flex items-center space-x-2">
              <Shield className="w-4 h-4 text-primary" />
              <span>NIST Framework</span>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-glow bg-muted/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-muted-foreground">
              © 2024 MedGuard AI Security. All rights reserved.
            </div>
            <div className="flex space-x-6 text-sm">
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">Privacy Policy</a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">Terms of Service</a>
              <a href="#" className="text-muted-foreground hover:text-primary transition-colors">Cookie Policy</a>
              <a href="#contact" className="text-muted-foreground hover:text-primary transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}