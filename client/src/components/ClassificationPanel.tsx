import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ConfidenceMeter } from "./ConfidenceMeter";
import type { Classification } from "@shared/schema";
import { FileText, Activity, Microscope, Scan, ClipboardList } from "lucide-react";

interface ClassificationPanelProps {
  classification: Classification;
}

const DOC_TYPE_ICONS: Record<string, any> = {
  "COMPLETE BLOOD COUNT": Activity,
  "BASIC METABOLIC PANEL": Microscope,
  "X-RAY": Scan,
  "CT": Scan,
  "CLINICAL NOTE": ClipboardList,
};

const DOC_TYPE_COLORS: Record<string, string> = {
  "COMPLETE BLOOD COUNT": "bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300",
  "BASIC METABOLIC PANEL": "bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300",
  "X-RAY": "bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300",
  "CT": "bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300",
  "CLINICAL NOTE": "bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300",
};

export function ClassificationPanel({ classification }: ClassificationPanelProps) {
  const Icon = DOC_TYPE_ICONS[classification.document_type] || FileText;
  const colorClass = DOC_TYPE_COLORS[classification.document_type] || "bg-gray-100 text-gray-800";

  return (
    <Card className="overflow-hidden">
      <CardHeader className="space-y-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-xl font-semibold">Document Classification</CardTitle>
            <CardDescription className="mt-1">AI-powered document type identification</CardDescription>
          </div>
          <Icon className="w-6 h-6 text-muted-foreground flex-shrink-0" />
        </div>
        
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-md font-medium ${colorClass}`}>
          <Icon className="w-5 h-5" />
          <span className="text-base">{classification.document_type}</span>
        </div>
      </CardHeader>
      
      <CardContent className="space-y-6">
        <ConfidenceMeter confidence={classification.confidence} size="md" />
        
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-foreground">Rationale</h4>
          <p className="text-sm text-muted-foreground leading-relaxed bg-muted/50 p-4 rounded-md">
            {classification.rationale}
          </p>
        </div>
        
        {classification.evidence && Array.isArray(classification.evidence) && classification.evidence.length > 0 && (
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-foreground">Supporting Evidence</h4>
            <div className="space-y-2">
              {classification.evidence.map((quote, idx) => (
                <div
                  key={idx}
                  className="border-l-4 border-primary/40 pl-4 py-2 bg-card/50"
                >
                  <p className="text-sm italic text-muted-foreground">
                    &ldquo;{quote}&rdquo;
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
