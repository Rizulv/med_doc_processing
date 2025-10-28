import { useQuery } from "@tanstack/react-query";
import { Link } from "wouter";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { FileText, Upload, AlertCircle, ExternalLink } from "lucide-react";
import api from "@/lib/api";
import type { Document } from "@shared/schema";
import { format } from "date-fns";

export default function DocumentsPage() {
  const { data: documents, isLoading, error } = useQuery<Document[]>({
    queryKey: ['/documents'],
    queryFn: async () => {
      const response = await api.get('/documents');
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="flex items-center justify-between mb-8">
            <Skeleton className="h-10 w-48" />
            <Skeleton className="h-10 w-32" />
          </div>
          <div className="space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <Skeleton key={i} className="h-24 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-background">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <Card className="border-destructive/50">
            <CardContent className="p-8">
              <div className="flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0" />
                <div>
                  <h3 className="font-semibold text-destructive mb-2">Failed to Load Documents</h3>
                  <p className="text-sm text-muted-foreground">
                    {error instanceof Error ? error.message : "An error occurred"}
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
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-semibold text-foreground mb-2">
              Documents
            </h1>
            <p className="text-muted-foreground">
              View all processed medical documents
            </p>
          </div>
          <Link href="/">
            <Button data-testid="button-upload-new">
              <Upload className="w-4 h-4 mr-2" />
              Upload New Document
            </Button>
          </Link>
        </div>

        {!documents || documents.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <div className="flex flex-col items-center gap-4">
                <div className="p-6 bg-muted rounded-full">
                  <FileText className="w-12 h-12 text-muted-foreground" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold">No documents yet</h3>
                  <p className="text-sm text-muted-foreground max-w-sm">
                    Upload your first medical document to get started with AI-powered analysis
                  </p>
                </div>
                <Link href="/">
                  <Button data-testid="button-get-started">
                    <Upload className="w-4 h-4 mr-2" />
                    Get Started
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <Link key={doc.id} href={`/documents/${doc.id}`}>
                <Card className="hover-elevate transition-all cursor-pointer">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between gap-4">
                      <div className="flex items-center gap-4 flex-1 min-w-0">
                        <div className="p-3 bg-primary/10 rounded-lg">
                          <FileText className="w-6 h-6 text-primary" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-medium text-foreground truncate mb-1" title={doc.original_filename}>
                            {doc.original_filename}
                          </h3>
                          <p className="text-sm text-muted-foreground">
                            Uploaded {format(new Date(doc.created_at), 'MMM d, yyyy · h:mm a')}
                          </p>
                        </div>
                      </div>
                      <ExternalLink className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
