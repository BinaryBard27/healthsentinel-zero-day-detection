import { Button } from "./ui/button";
import { Shield, Linkedin, Twitter, Youtube, Mail, Phone, MapPin } from "lucide-react";

export function EnterpriseFooter() {
  const footerSections = [
    {
      title: "Products",
      links: [
        "HealthSentinel AI Engine",
        "HIPAA Compliance Suite", 
        "Real-Time Monitoring",
        "Incident Response",
        "API & Integrations",
        "Pricing"
      ]
    },
    {
      title: "Solutions",
      links: [
        "Hospitals & Health Systems",
        "Clinics & Private Practice",
        "Pharmaceutical Research",
        "Telehealth Platforms",
        "Medical Device Security",
        "View All Solutions"
      ]
    },
    {
      title: "Resources",
      links: [
        "Documentation",
        "White Papers",
        "Case Studies",
        "Webinars",
        "Security Research",
        "Blog"
      ]
    },
    {
      title: "Company",
      links: [
        "About Us",
        "Leadership Team",
        "Careers",
        "News & Press",
        "Partners",
        "Contact"
      ]
    },
    {
      title: "Support",
      links: [
        "Customer Portal",
        "Training Center",
        "Professional Services",
        "System Status",
        "Developer Resources",
        "Community Forum"
      ]
    }
  ];

  const certifications = [
    "SOC 2 Type II",
    "HIPAA Compliant",
    "ISO 27001",
    "GDPR Ready",
    "NIST Framework",
    "FedRAMP Ready"
  ];

  return (
    <footer className="bg-gray-900 text-white">
      {/* Main Footer */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid lg:grid-cols-6 gap-8">
          {/* Company Info */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-2 mb-6">
              <Shield className="w-8 h-8 text-primary" />
              <span className="text-xl font-bold">HealthSentinel</span>
            </div>
            <p className="text-gray-300 mb-6 leading-relaxed">
              AI-powered cybersecurity solutions designed specifically for healthcare organizations. 
              Protecting patient data and critical systems with enterprise-grade security.
            </p>
            
            {/* Contact Info */}
            <div className="space-y-3 mb-6">
              <div className="flex items-center space-x-3">
                <Phone className="w-4 h-4 text-primary" />
                <span className="text-gray-300">+1 (555) 123-4567</span>
              </div>
              <div className="flex items-center space-x-3">
                <Mail className="w-4 h-4 text-primary" />
                <span className="text-gray-300">contact@healthsentinel.ai</span>
              </div>
              <div className="flex items-start space-x-3">
                <MapPin className="w-4 h-4 text-primary mt-1" />
                <span className="text-gray-300">
                  Fr. Conceicao Rodrigues College of Engineering<br />
                  Agnel Technical Education Complex<br />
                  Bandra West, Mumbai - 400050, India
                </span>
              </div>
            </div>

            {/* Social Links */}
            <div className="flex space-x-4">
              <button className="w-10 h-10 rounded-lg bg-gray-800 hover:bg-primary/20 flex items-center justify-center transition-colors">
                <Linkedin className="w-5 h-5" />
              </button>
              <button className="w-10 h-10 rounded-lg bg-gray-800 hover:bg-primary/20 flex items-center justify-center transition-colors">
                <Twitter className="w-5 h-5" />
              </button>
              <button className="w-10 h-10 rounded-lg bg-gray-800 hover:bg-primary/20 flex items-center justify-center transition-colors">
                <Youtube className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Footer Links */}
          {footerSections.map((section, index) => (
            <div key={index}>
              <h4 className="font-semibold text-white mb-4">{section.title}</h4>
              <ul className="space-y-3">
                {section.links.map((link, linkIndex) => (
                  <li key={linkIndex}>
                    <a 
                      href="#" 
                      className="text-gray-300 hover:text-primary transition-colors text-sm"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Newsletter Signup */}
        <div className="mt-16 pt-12 border-t border-gray-800">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-xl font-semibold text-white mb-4">
                Stay Secure with HealthSentinel
              </h3>
              <p className="text-gray-300">
                Get the latest security updates, threat intelligence, and product news.
              </p>
            </div>
            <div>
              <div className="flex space-x-4">
                <input
                  type="email"
                  placeholder="Enter your email"
                  className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-primary"
                />
                <Button className="enterprise-gradient text-white px-6">
                  Subscribe
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Certifications */}
        <div className="mt-12 pt-8 border-t border-gray-800">
          <div className="text-center mb-6">
            <h4 className="font-semibold text-white mb-4">Security & Compliance Certifications</h4>
            <div className="flex flex-wrap justify-center gap-6">
              {certifications.map((cert, index) => (
                <div key={index} className="flex items-center space-x-2 text-gray-300">
                  <Shield className="w-4 h-4 text-primary" />
                  <span className="text-sm">{cert}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="border-t border-gray-800 bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
            <div className="text-sm text-gray-400">
              © 2024 HealthSentinel AI Security, Inc. All rights reserved.
            </div>
            <div className="flex space-x-6 text-sm">
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">Privacy Policy</a>
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">Terms of Service</a>
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">Cookie Policy</a>
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">Security</a>
              <a href="#" className="text-gray-400 hover:text-primary transition-colors">Accessibility</a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}