import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { cn } from "./ui/utils";
import { ImageWithFallback } from "./figma/ImageWithFallback";

interface MedGuardCardProps {
  title: string;
  description: string;
  icon?: React.ReactNode;
  image?: string;
  type?: "feature" | "team" | "caseStudy";
  className?: string;
  children?: React.ReactNode;
}

export function MedGuardCard({ 
  title, 
  description, 
  icon, 
  image, 
  type = "feature",
  className,
  children 
}: MedGuardCardProps) {
  const typeClasses = {
    feature: "bg-gradient-cyber border-glow hover:glow-primary",
    team: "bg-muted/50 border-glow hover:glow-secondary",
    caseStudy: "bg-gradient-cyber border-glow hover:glow-accent"
  };

  return (
    <Card className={cn(
      "transition-all duration-300 hover:scale-105 rounded-lg overflow-hidden",
      typeClasses[type],
      className
    )}>
      {image && (
        <div className="aspect-video overflow-hidden">
          <ImageWithFallback 
            src={image} 
            alt={title}
            className="w-full h-full object-cover"
          />
        </div>
      )}
      
      <CardHeader className="pb-4">
        {icon && (
          <div className="w-12 h-12 flex items-center justify-center rounded-lg bg-primary/10 text-primary mb-4">
            {icon}
          </div>
        )}
        <CardTitle className="text-foreground">{title}</CardTitle>
      </CardHeader>
      
      <CardContent className="pt-0">
        <CardDescription className="text-muted-foreground">
          {description}
        </CardDescription>
        {children}
      </CardContent>
    </Card>
  );
}