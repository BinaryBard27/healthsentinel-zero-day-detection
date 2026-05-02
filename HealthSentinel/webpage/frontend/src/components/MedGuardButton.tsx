import { Button } from "./ui/button";
import { cn } from "./ui/utils";

interface MedGuardButtonProps {
  label: string;
  onClick?: () => void;
  size?: "sm" | "md" | "lg";
  variant?: "primary" | "secondary" | "outline" | "glow";
  className?: string;
  type?: "button" | "submit" | "reset";
}

export function MedGuardButton({ 
  label, 
  onClick, 
  size = "md", 
  variant = "primary",
  className,
  type = "button"
}: MedGuardButtonProps) {
  const sizeClasses = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg"
  };

  const variantClasses = {
    primary: "bg-primary text-primary-foreground hover:bg-primary/90 glow-primary",
    secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/90 glow-secondary",
    outline: "border-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground border-glow",
    glow: "bg-gradient-to-r from-primary to-secondary text-primary-foreground hover:from-primary/90 hover:to-secondary/90 animate-pulse-glow"
  };

  return (
    <Button
      type={type}
      onClick={onClick}
      className={cn(
        "rounded-lg font-medium transition-all duration-300 border-0",
        sizeClasses[size],
        variantClasses[variant],
        className
      )}
    >
      {label}
    </Button>
  );
}