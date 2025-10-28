import { useState } from "react";
import { UploadCard } from "@/components/UploadCard";
import { ClassificationPanel } from "@/components/ClassificationPanel";
import { CodeCard } from "@/components/CodeCard";
import { SummaryCard } from "@/components/SummaryCard";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { AlertCircle, CheckCircle2 } from "lucide-react";
import api from "@/lib/api";
import type { UploadResponse } from "@shared/schema";

export default function UploadPage() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [result, setResult] = useState<UploadResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { toast } = useToast();

  const handleFileUpload = async (file: File) => {
    setIsProcessing(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('run_pipeline', 'true');

      const response = await api.post<UploadResponse>('/documents', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);
      
      toast({
        title: "Processing Complete",
        description: "Document classified and analyzed successfully",
      });
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || "Failed to process document";
      setError(errorMessage);
      
      toast({
        title: "Processing Failed",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-semibold text-foreground mb-2">
            Medical Document Analysis
          </h1>
          <p className="text-muted-foreground">
            Upload medical documents for AI-powered classification, ICD-10 code extraction, and clinical summarization
          </p>
        </div>

        <div className="max-w-2xl mx-auto mb-8">
          <UploadCard 
            onFileSelect={handleFileUpload} 
            isProcessing={isProcessing}
          />
        </div>

        {error && (
          <div className="max-w-4xl mx-auto mb-8">
            <Card className="border-destructive/50 bg-destructive/5">
              <CardContent className="p-6">
                <div className="flex items-start gap-4">
                  <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-semibold text-destructive mb-1">Processing Error</h3>
                    <p className="text-sm text-destructive/90">{error}</p>
                  </div>
                  <Button variant="outline" onClick={handleReset} size="sm">
                    Try Again
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {result && result.processed && result.results && (
          <div className="max-w-4xl mx-auto space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
                <h2 className="text-2xl font-semibold">Analysis Results</h2>
              </div>
              <Button variant="outline" onClick={handleReset} data-testid="button-analyze-another">
                Analyze Another Document
              </Button>
            </div>

            <ClassificationPanel classification={result.results.classification} />

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold">
                  ICD-10 Diagnostic Codes
                </h3>
                <span className="text-sm text-muted-foreground">
                  {result.results.codes.codes.length} {result.results.codes.codes.length === 1 ? 'code' : 'codes'} identified
                </span>
              </div>

              {result.results.codes.codes.length === 0 ? (
                <Card>
                  <CardContent className="p-8 text-center">
                    <p className="text-sm text-muted-foreground">
                      No diagnostic codes identified in this document
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid gap-4 sm:grid-cols-2">
                  {result.results.codes.codes.map((code, idx) => (
                    <CodeCard key={idx} code={code} />
                  ))}
                </div>
              )}
            </div>

            <SummaryCard summary={result.results.summary} />
          </div>
        )}
      </div>
    </div>
  );
}
