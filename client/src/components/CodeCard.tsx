import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ConfidenceMeter } from "./ConfidenceMeter";
import type { ICD10Code } from "@shared/schema";
import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

interface CodeCardProps {
  code: ICD10Code;
}

export function CodeCard({ code }: CodeCardProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card className="hover-elevate transition-all">
      <CardContent className="p-4 space-y-3">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <code className="text-base font-mono font-semibold text-foreground">
                {code.code}
              </code>
              {code.confidence >= 0.8 && (
                <Badge variant="default" className="text-xs">Verified</Badge>
              )}
            </div>
            <p className="text-sm text-foreground">{code.description}</p>
          </div>
        </div>

        <ConfidenceMeter 
          confidence={code.confidence} 
          label="Diagnostic Confidence"
          size="sm"
          showBadge={false}
        />

        {code.evidence && code.evidence.length > 0 && (
          <div className="pt-2 border-t">
            <button
              onClick={() => setExpanded(!expanded)}
              className="flex items-center gap-1 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
              data-testid={`button-toggle-evidence-${code.code}`}
            >
              {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              <span>{expanded ? "Hide" : "View"} Evidence ({code.evidence.length})</span>
            </button>
            
            {expanded && (
              <div className="mt-3 space-y-2">
                {code.evidence.map((quote, idx) => (
                  <div 
                    key={idx}
                    className="text-xs italic text-muted-foreground bg-muted/30 p-2 rounded border-l-2 border-primary/40"
                  >
                    &ldquo;{quote}&rdquo;
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
