import { useState, useEffect } from "react";
import { EnterpriseNavbar } from "./components/EnterpriseNavbar";
import { EnterpriseHero } from "./components/EnterpriseHero";
import { ProductShowcase } from "./components/ProductShowcase";
import { SolutionsByIndustry } from "./components/SolutionsByIndustry";
import { CustomerTestimonials } from "./components/CustomerTestimonials";
import { ResourcesSection } from "./components/ResourcesSection";
import { EnterpriseFooter } from "./components/EnterpriseFooter";
import { LoginPage } from "./components/LoginPage";
import { SecurityDashboard } from "./components/SecurityDashboard";
import { Toaster } from "./components/ui/sonner";

// Demo admin accounts — everyone who logs in sees the full dashboard
// admin@test.com is the built-in demo user from the TS backend
const ADMIN_EMAILS = [
  "admin@test.com",
  "admin@healthsentinel.com",
  "demo@healthsentinel.com",
  "admin@hospital.org"
];

export default function App() {
  const [currentPage, setCurrentPage] = useState<"home" | "login" | "dashboard">("home");
  const [authToken, setAuthToken] = useState<string | null>(null);
  const [userEmail, setUserEmail] = useState<string>("");
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    const email = localStorage.getItem("userEmail") || "";
    const adminFlag = localStorage.getItem("isAdmin") === "true";
    if (token) {
      setAuthToken(token);
      setUserEmail(email);
      setIsAdmin(adminFlag);
      setCurrentPage("dashboard");
    }
  }, []);

  const handleLoginSuccess = (token: string, email?: string) => {
    const resolvedEmail = email || userEmail;
    const adminRole = ADMIN_EMAILS.includes(resolvedEmail.toLowerCase());
    setAuthToken(token);
    setUserEmail(resolvedEmail);
    setIsAdmin(adminRole);
    localStorage.setItem("authToken", token);
    localStorage.setItem("userEmail", resolvedEmail);
    localStorage.setItem("isAdmin", String(adminRole));
    setCurrentPage("dashboard");
  };

  const handleLogout = () => {
    setAuthToken(null);
    setUserEmail("");
    setIsAdmin(false);
    localStorage.removeItem("authToken");
    localStorage.removeItem("userEmail");
    localStorage.removeItem("isAdmin");
    setCurrentPage("home");
  };

  // Security Dashboard — shown after successful login
  if (currentPage === "dashboard" && authToken) {
    return (
      <>
        <SecurityDashboard onLogout={handleLogout} isAdmin={isAdmin} userEmail={userEmail} />
        <Toaster />
      </>
    );
  }

  // Login Page
  if (currentPage === "login") {
    return (
      <>
        <LoginPage
          onBackToHome={() => setCurrentPage("home")}
          onLoginSuccess={handleLoginSuccess}
          onEmailChange={setUserEmail}
        />
        <Toaster />
      </>
    );
  }

  // Home Page
  return (
    <div className="min-h-screen bg-white text-foreground">
      <EnterpriseNavbar onLoginClick={() => setCurrentPage("login")} />

      <main>
        <EnterpriseHero />
        <ProductShowcase />
        <SolutionsByIndustry />
        <CustomerTestimonials />
        <ResourcesSection />
      </main>
      <EnterpriseFooter />
      <Toaster />
    </div>
  );
}