import { useState } from "react";
import { EnterpriseNavbar } from "./components/EnterpriseNavbar";
import { EnterpriseHero } from "./components/EnterpriseHero";
import { ProductShowcase } from "./components/ProductShowcase";
import { SolutionsByIndustry } from "./components/SolutionsByIndustry";
import { CustomerTestimonials } from "./components/CustomerTestimonials";
import { ResourcesSection } from "./components/ResourcesSection";
import { EnterpriseFooter } from "./components/EnterpriseFooter";
import { LoginPage } from "./components/LoginPage";
import { Toaster } from "./components/ui/sonner";

export default function App() {
  const [currentPage, setCurrentPage] = useState<"home" | "login">("home");

  if (currentPage === "login") {
    return (
      <>
        <LoginPage onBackToHome={() => setCurrentPage("home")} />
        <Toaster />
      </>
    );
  }

  return (
    <div className="min-h-screen bg-white text-foreground">
      {/* Navigation */}
      <EnterpriseNavbar onLoginClick={() => setCurrentPage("login")} />
      
      {/* Main Content */}
      <main>
        <EnterpriseHero />
        <ProductShowcase />
        <SolutionsByIndustry />
        <CustomerTestimonials />
        <ResourcesSection />
      </main>
      
      {/* Footer */}
      <EnterpriseFooter />
      
      {/* Toast Notifications */}
      <Toaster />
    </div>
  );
}