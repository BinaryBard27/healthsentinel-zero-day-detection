import { useState } from "react";
import { Button } from "./ui/button";
import { Badge } from "./ui/badge";
import { Menu, X, ChevronDown, Search, Shield } from "lucide-react";
import { cn } from "./ui/utils";

interface MegaMenuProps {
  isOpen: boolean;
  category: string;
}

function MegaMenu({ isOpen, category }: MegaMenuProps) {
  if (!isOpen) return null;

  const menuContent = {
    products: {
      title: "AI-Powered Security Platform",
      sections: [
        {
          title: "Core Platform",
          items: [
            { name: "HealthSentinel AI Engine", desc: "Advanced threat detection for healthcare", badge: "New" },
            { name: "Zero-Day Defense", desc: "Proactive protection against unknown threats" },
            { name: "Behavioral Analytics", desc: "ML-powered user behavior monitoring" },
            { name: "Incident Response", desc: "Automated threat response and remediation" }
          ]
        },
        {
          title: "Healthcare Solutions",
          items: [
            { name: "HIPAA Compliance Suite", desc: "Comprehensive regulatory compliance" },
            { name: "Medical Device Security", desc: "IoT and legacy device protection" },
            { name: "Patient Data Protection", desc: "Advanced encryption and access controls" },
            { name: "Clinical Workflow Security", desc: "Seamless security integration" }
          ]
        }
      ]
    },
    solutions: {
      title: "Industry Solutions",
      sections: [
        {
          title: "By Healthcare Segment",
          items: [
            { name: "Hospitals & Health Systems", desc: "Enterprise-scale protection" },
            { name: "Clinics & Private Practice", desc: "Small to medium practice security" },
            { name: "Pharmaceutical Research", desc: "Research data and IP protection" },
            { name: "Telehealth Platforms", desc: "Remote care security solutions" }
          ]
        },
        {
          title: "By Threat Type",
          items: [
            { name: "Ransomware Protection", desc: "Advanced ransomware prevention" },
            { name: "Phishing Defense", desc: "Email and communication security" },
            { name: "Insider Threat", desc: "Internal risk monitoring and prevention" },
            { name: "Supply Chain Security", desc: "Third-party vendor risk management" }
          ]
        }
      ]
    },
    resources: {
      title: "Resources & Support",
      sections: [
        {
          title: "Learn",
          items: [
            { name: "Documentation", desc: "Implementation and API guides" },
            { name: "White Papers", desc: "Research and industry insights", badge: "Popular" },
            { name: "Case Studies", desc: "Real-world success stories" },
            { name: "Webinars", desc: "Expert-led training sessions" }
          ]
        },
        {
          title: "Support",
          items: [
            { name: "Customer Portal", desc: "24/7 support and resources" },
            { name: "Training Center", desc: "Professional certification programs" },
            { name: "Community Forum", desc: "Peer support and discussions" },
            { name: "Professional Services", desc: "Implementation and consulting" }
          ]
        }
      ]
    }
  };

  const content = menuContent[category as keyof typeof menuContent];
  if (!content) return null;

  return (
    <div className="absolute top-full left-0 w-full bg-white border-t border-border shadow-xl z-50">
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="mb-6">
          <h3 className="text-xl font-semibold text-foreground mb-2">{content.title}</h3>
        </div>
        <div className="grid md:grid-cols-2 gap-8">
          {content.sections.map((section, index) => (
            <div key={index}>
              <h4 className="font-semibold text-foreground mb-4 text-sm uppercase tracking-wide">
                {section.title}
              </h4>
              <div className="space-y-3">
                {section.items.map((item, itemIndex) => (
                  <a
                    key={itemIndex}
                    href="#"
                    className="block group p-3 rounded-lg hover:bg-muted transition-colors"
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-foreground group-hover:text-primary">
                        {item.name}
                      </span>
                      {item.badge && (
                        <Badge variant="secondary" className="text-xs">
                          {item.badge}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{item.desc}</p>
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

interface EnterpriseNavbarProps {
  onLoginClick?: () => void;
}

export function EnterpriseNavbar({ onLoginClick }: EnterpriseNavbarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [activeMega, setActiveMega] = useState<string | null>(null);

  const navItems = [
    { label: "Products", key: "products", hasMega: true },
    { label: "Solutions", key: "solutions", hasMega: true },
    { label: "Resources", key: "resources", hasMega: true },
    { label: "Pricing", key: "pricing", hasMega: false },
    { label: "Company", key: "company", hasMega: false }
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-8">
            <div className="flex items-center space-x-2">
              <Shield className="w-8 h-8 text-primary" />
              <span className="text-xl font-bold text-foreground">HealthSentinel</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-1">
              {navItems.map((item) => (
                <div
                  key={item.key}
                  className="relative"
                >
                  <a
                    href={`#${item.key}`}
                    className={cn(
                      "flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                      "text-foreground hover:text-primary hover:bg-muted"
                    )}
                  >
                    <span>{item.label}</span>
                  </a>
                </div>
              ))}
            </div>
          </div>

          {/* Right side */}
          <div className="flex items-center space-x-4">
            {/* Search */}
            <button className="hidden md:flex items-center space-x-2 px-3 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors">
              <Search className="w-4 h-4" />
              <span>Search</span>
            </button>

            {/* Login */}
            <Button 
              variant="ghost" 
              size="sm" 
              className="hidden md:inline-flex"
              onClick={onLoginClick}
            >
              Log In
            </Button>

            {/* Demo CTA */}
            <Button size="sm" className="enterprise-gradient text-white">
              Request Demo
            </Button>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="lg:hidden p-2 text-foreground hover:text-primary"
            >
              {isOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="lg:hidden border-t border-border py-4">
            <div className="space-y-1">
              {navItems.map((item) => (
                <a
                  key={item.key}
                  href="#"
                  className="block px-3 py-2 text-base font-medium text-foreground hover:text-primary hover:bg-muted rounded-lg"
                >
                  {item.label}
                </a>
              ))}
              <div className="pt-4 border-t border-border mt-4">
                <Button 
                  variant="ghost" 
                  className="w-full justify-start mb-2"
                  onClick={onLoginClick}
                >
                  Log In
                </Button>
                <Button className="w-full enterprise-gradient text-white">
                  Request Demo
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}