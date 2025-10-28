import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ConfidenceMeter } from "./ConfidenceMeter";
import type { Summary } from "@shared/schema";
import { FileText } from "lucide-react";

interface SummaryCardProps {
  summary: Summary;
}

export function SummaryCard({ summary }: SummaryCardProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-semibold">Clinical Summary</CardTitle>
            <CardDescription className="mt-1">Provider-facing structured summary</CardDescription>
          </div>
          <FileText className="w-5 h-5 text-muted-foreground" />
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <p className="text-sm text-foreground leading-relaxed whitespace-pre-line">
            {summary.summary}
          </p>
        </div>

        <ConfidenceMeter confidence={summary.confidence} size="sm" />

        {summary.evidence && summary.evidence.length > 0 && (
          <div className="space-y-2 pt-4 border-t">
            <h4 className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
              Key Evidence Citations
            </h4>
            <div className="space-y-2">
              {summary.evidence.map((quote, idx) => (
                <div 
                  key={idx}
                  className="text-xs italic text-muted-foreground bg-muted/30 p-3 rounded border-l-2 border-primary/40"
                >
                  &ldquo;{quote}&rdquo;
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
