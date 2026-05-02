import { useState } from "react";
import { MedGuardButton } from "./MedGuardButton";
import { Menu, X, Shield } from "lucide-react";
import { cn } from "./ui/utils";

interface NavItem {
  label: string;
  href: string;
}

interface MedGuardNavbarProps {
  logo?: string;
  menuItems?: NavItem[];
  ctaButton?: string;
  className?: string;
}

export function MedGuardNavbar({ 
  logo = "MedGuard",
  menuItems = [
    { label: "Features", href: "#features" },
    { label: "Case Studies", href: "#case-studies" },
    { label: "Team", href: "#team" },
    { label: "Contact", href: "#contact" }
  ],
  ctaButton = "Request Demo",
  className
}: MedGuardNavbarProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className={cn(
      "sticky top-0 z-50 bg-background/90 backdrop-blur-md border-b border-glow",
      className
    )}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center space-x-2">
            <Shield className="w-8 h-8 text-primary animate-pulse-glow" />
            <span className="text-xl font-bold text-primary text-glow-primary">
              {logo}
            </span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {menuItems.map((item) => (
              <a
                key={item.label}
                href={item.href}
                className="text-foreground hover:text-primary transition-colors duration-300 hover:text-glow-primary"
              >
                {item.label}
              </a>
            ))}
          </div>

          {/* CTA Button */}
          <div className="hidden md:block">
            <MedGuardButton 
              label={ctaButton} 
              variant="glow"
              size="sm"
            />
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="text-foreground hover:text-primary transition-colors"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden border-t border-glow">
            <div className="px-2 pt-2 pb-3 space-y-1">
              {menuItems.map((item) => (
                <a
                  key={item.label}
                  href={item.href}
                  className="block px-3 py-2 text-foreground hover:text-primary transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  {item.label}
                </a>
              ))}
              <div className="px-3 py-2">
                <MedGuardButton 
                  label={ctaButton} 
                  variant="glow"
                  size="sm"
                  className="w-full"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}