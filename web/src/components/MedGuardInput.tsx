import { Input } from "./ui/input";
import { cn } from "./ui/utils";

interface MedGuardInputProps {
  type?: "text" | "email" | "password" | "search";
  placeholder?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  className?: string;
}

export function MedGuardInput({ 
  type = "text",
  placeholder,
  value,
  onChange,
  className
}: MedGuardInputProps) {
  return (
    <Input
      type={type}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      className={cn(
        "bg-input-background border-glow text-foreground placeholder:text-muted-foreground",
        "focus:border-primary focus:ring-1 focus:ring-primary transition-all duration-300",
        "rounded-lg px-4 py-3",
        className
      )}
    />
  );
}