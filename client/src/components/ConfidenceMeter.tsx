import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface ConfidenceMeterProps {
  confidence: number;
  label?: string;
  showBadge?: boolean;
  size?: "sm" | "md" | "lg";
}

export function ConfidenceMeter({ 
  confidence, 
  label = "Confidence",
  showBadge = true,
  size = "md"
}: ConfidenceMeterProps) {
  const percentage = Math.round(confidence * 100);
  
  const getConfidenceLevel = (conf: number) => {
    if (conf >= 0.8) return { level: "High", variant: "default" as const, color: "text-green-600 dark:text-green-400" };
    if (conf >= 0.5) return { level: "Medium", variant: "secondary" as const, color: "text-yellow-600 dark:text-yellow-400" };
    return { level: "Low", variant: "destructive" as const, color: "text-red-600 dark:text-red-400" };
  };

  const { level, variant, color } = getConfidenceLevel(confidence);
  
  const heightClass = size === "sm" ? "h-1.5" : size === "lg" ? "h-3" : "h-2";
  const textSizeClass = size === "sm" ? "text-xs" : size === "lg" ? "text-base" : "text-sm";

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between gap-2">
        <span className={cn("font-medium text-muted-foreground", textSizeClass)}>{label}</span>
        <div className="flex items-center gap-2">
          <span className={cn("font-mono font-medium", color, textSizeClass)}>{percentage}%</span>
          {showBadge && <Badge variant={variant} className="text-xs">{level}</Badge>}
        </div>
      </div>
      <Progress value={percentage} className={heightClass} />
    </div>
  );
}
