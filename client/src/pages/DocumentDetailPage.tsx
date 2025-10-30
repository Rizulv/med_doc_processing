import { useQuery } from "@tanstack/react-query";
import { useParams, Link } from "wouter";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ClassificationPanel } from "@/components/ClassificationPanel";
import { CodeCard } from "@/components/CodeCard";
import { SummaryCard } from "@/components/SummaryCard";
import { SummaryReportCard } from "@/components/SummaryReportCard";
import { ArrowLeft, AlertCircle, FileText, Calendar } from "lucide-react";
import api from "@/lib/api";
import type { DocumentWithResults } from "@shared/schema";
import { format } from "date-fns";

export default function DocumentDetailPage() {
  const { id } = useParams<{ id: string }>();
  
  const { data: document, isLoading, error } = useQuery<DocumentWithResults>({
    queryKey: ['/documents', id],
    queryFn: async () => {
      const response = await api.get(`/documents/${id}`);
      return response.data;
    },
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <Skeleton className="h-8 w-32 mb-8" />
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <Skeleton className="h-96 w-full" />
            </div>
            <div className="space-y-6">
              <Skeleton className="h-64 w-full" />
              <Skeleton className="h-64 w-full" />
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <Link href="/documents">
            <Button variant="ghost" className="mb-8" data-testid="button-back-to-documents">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Documents
            </Button>
          </Link>
          <Card className="border-destructive/50">
            <CardContent className="p-8">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-destructive mb-2">Document Not Found</h3>
                  <p className="text-sm text-muted-foreground">
                    {error instanceof Error ? error.message : "Unable to load document"}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-6">
          <Link href="/documents">
            <Button variant="ghost" className="mb-4" data-testid="button-back-to-documents">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Documents
            </Button>
          </Link>
          <div className="flex items-start gap-3">
            <FileText className="w-8 h-8 text-primary mt-1" />
            <div>
              <h1 className="text-3xl font-semibold text-foreground mb-2">
                {document.original_filename}
              </h1>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Calendar className="w-4 h-4" />
                <span>Uploaded {format(new Date(document.created_at), 'MMMM d, yyyy · h:mm a')}</span>
              </div>
            </div>
          </div>
        </div>

        {!document.results ? (
          <Card>
            <CardContent className="p-8 text-center">
              <p className="text-muted-foreground">
                This document has not been processed yet
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-8">
            {/* Summary Report with Download Button */}
            <SummaryReportCard document={document} />

            <div className="grid lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2 space-y-8 order-2 lg:order-1">
                <ClassificationPanel classification={document.results.classification} />

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold">
                    ICD-10 Diagnostic Codes
                  </h3>

                  {document.results.codes.codes.length === 0 ? (
                    <Card>
                      <CardContent className="p-6 text-center">
                        <p className="text-sm text-muted-foreground">
                          No diagnostic codes identified in this document
                        </p>
                      </CardContent>
                    </Card>
                  ) : (
                    <div className="grid gap-4">
                      {document.results.codes.codes.map((code, idx) => (
                        <CodeCard key={idx} code={code} />
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="space-y-6 order-1 lg:order-2">
                <div className="lg:sticky lg:top-8">
                  <SummaryCard summary={document.results.summary} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
