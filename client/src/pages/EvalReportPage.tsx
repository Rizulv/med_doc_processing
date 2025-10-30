import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, XCircle, AlertCircle, Loader2, RefreshCw } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { useState } from "react";

interface TestResult {
  id: string;
  document_type: string;
  query: string;
  expected_codes: string[];
  predicted_codes: string[];
  expected_facts: string[];
  generated_summary: string;
  metrics: {
    precision: number;
    recall: number;
    f1: number;
    coverage: number;
  };
}

interface EvalResults {
  items: number;
  codes_precision: number;
  codes_recall: number;
  codes_f1: number;
  summary_coverage: number;
  mode: string;
  test_results: TestResult[];
  metadata?: {
    timestamp: string;
    git_commit: string;
    git_branch: string;
    workflow_run_id: string;
    workflow_run_number: number;
    repository: string;
  };
}

async function fetchEvalResults(): Promise<EvalResults> {
  // Try to fetch from S3 first, fallback to API
  try {
    const s3Response = await fetch(
      "https://med-docs-dev.s3.ap-south-1.amazonaws.com/eval-results/latest.json"
    );
    if (s3Response.ok) {
      return s3Response.json();
    }
  } catch (e) {
    console.warn("Failed to fetch from S3, trying API endpoint...", e);
  }
  
  // Fallback to API endpoint (serves cached S3 results)
  const apiResponse = await fetch("/eval/latest");
  if (!apiResponse.ok) {
    throw new Error(`Failed to fetch eval results: ${apiResponse.status} ${apiResponse.statusText}`);
  }
  
  return apiResponse.json();
}

function MetricBadge({ label, value, threshold = 0.7 }: { label: string; value: number; threshold?: number }) {
  const variant = value >= threshold ? "default" : value >= threshold * 0.7 ? "secondary" : "destructive";
  return (
    <Badge variant={variant} className="text-sm">
      {label}: {value.toFixed(2)}
    </Badge>
  );
}

function TestCaseCard({ result }: { result: TestResult }) {
  const correctCodes = result.expected_codes.filter(code =>
    result.predicted_codes.includes(code)
  );
  const missedCodes = result.expected_codes.filter(code =>
    !result.predicted_codes.includes(code)
  );
  const extraCodes = result.predicted_codes.filter(code =>
    !result.expected_codes.includes(code)
  );

  return (
    <Card className="mb-4">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">{result.id}</CardTitle>
            <CardDescription>{result.document_type}</CardDescription>
          </div>
          <div className="flex gap-2">
            <MetricBadge label="F1" value={result.metrics.f1} />
            <MetricBadge label="Coverage" value={result.metrics.coverage} />
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Accordion type="single" collapsible className="w-full">
          <AccordionItem value="query">
            <AccordionTrigger>Document Query</AccordionTrigger>
            <AccordionContent>
              <div className="bg-muted p-4 rounded-md">
                <p className="text-sm font-mono">{result.query}</p>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="codes">
            <AccordionTrigger>ICD-10 Codes Analysis</AccordionTrigger>
            <AccordionContent className="space-y-3">
              <div className="flex gap-2 flex-wrap">
                <MetricBadge label="Precision" value={result.metrics.precision} />
                <MetricBadge label="Recall" value={result.metrics.recall} />
                <MetricBadge label="F1" value={result.metrics.f1} />
              </div>

              {correctCodes.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-green-600 mb-2 flex items-center gap-1">
                    <CheckCircle2 className="w-4 h-4" />
                    Correct Predictions ({correctCodes.length})
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {correctCodes.map((code) => (
                      <Badge key={code} variant="default" className="bg-green-600">
                        {code}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {missedCodes.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-red-600 mb-2 flex items-center gap-1">
                    <XCircle className="w-4 h-4" />
                    Missed Codes ({missedCodes.length})
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {missedCodes.map((code) => (
                      <Badge key={code} variant="destructive">
                        {code}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}

              {extraCodes.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-orange-600 mb-2 flex items-center gap-1">
                    <AlertCircle className="w-4 h-4" />
                    Extra Predictions ({extraCodes.length})
                  </p>
                  <div className="flex gap-2 flex-wrap">
                    {extraCodes.map((code) => (
                      <Badge key={code} variant="secondary" className="bg-orange-100 text-orange-800">
                        {code}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="summary">
            <AccordionTrigger>Summary Analysis</AccordionTrigger>
            <AccordionContent className="space-y-3">
              <div>
                <p className="text-sm font-medium mb-2">Expected Facts:</p>
                <ul className="list-disc list-inside space-y-1">
                  {result.expected_facts.map((fact, idx) => (
                    <li key={idx} className="text-sm text-muted-foreground">
                      {fact}
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="text-sm font-medium mb-2">Generated Summary:</p>
                <div className="bg-muted p-4 rounded-md">
                  <p className="text-sm">{result.generated_summary}</p>
                </div>
              </div>

              <MetricBadge label="Fact Coverage" value={result.metrics.coverage} threshold={0.8} />
            </AccordionContent>
          </AccordionItem>
        </Accordion>
      </CardContent>
    </Card>
  );
}

export default function EvalReportPage() {
  const { data, isLoading, error, refetch, isFetching } = useQuery({
    queryKey: ["evalResults"],
    queryFn: fetchEvalResults,
    staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    retry: 2,
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-900 flex items-center gap-2">
              <Loader2 className="w-6 h-6 animate-spin" />
              Loading Evaluation Results
            </CardTitle>
            <CardDescription className="text-blue-700">
              Fetching the latest evaluation report from storage...
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-4 w-5/6" />
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Eval Results</CardTitle>
            <CardDescription>
              Failed to fetch evaluation data from the API
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-sm font-mono text-red-800">
                {error instanceof Error ? error.message : "An unknown error occurred"}
              </p>
            </div>
            <div className="text-sm text-muted-foreground">
              <p className="font-semibold mb-2">Possible causes:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>API endpoint not responding (check backend health)</li>
                <li>Anthropic API key not configured or invalid</li>
                <li>Network timeout (evaluation takes 2-3 minutes)</li>
                <li>CORS or proxy configuration issue</li>
              </ul>
            </div>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Retry
            </button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Evaluation Test Report</h1>
            <p className="text-muted-foreground">
              Comprehensive analysis of medical document processing performance
            </p>
          </div>
          <button
            onClick={() => refetch()}
            disabled={isFetching}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw className={`w-4 h-4 ${isFetching ? 'animate-spin' : ''}`} />
            {isFetching ? 'Refreshing...' : 'Refresh'}
          </button>
        </div>
        
        {data?.metadata && (
          <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Report Metadata</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
              <div>
                <span className="text-gray-500">Generated:</span>
                <div className="font-medium">
                  {new Date(data.metadata.timestamp).toLocaleString()}
                </div>
              </div>
              <div>
                <span className="text-gray-500">Commit:</span>
                <div className="font-mono text-xs">
                  {data.metadata.git_commit.substring(0, 7)}
                </div>
              </div>
              <div>
                <span className="text-gray-500">Branch:</span>
                <div className="font-medium">{data.metadata.git_branch}</div>
              </div>
              <div>
                <span className="text-gray-500">Build:</span>
                <div className="font-medium">#{data.metadata.workflow_run_number}</div>
              </div>
              <div>
                <span className="text-gray-500">Mode:</span>
                <div className="font-medium">{data.mode}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      <Card className="mb-8 bg-gradient-to-br from-primary/5 to-primary/10">
        <CardHeader>
          <CardTitle>Overall Performance Metrics</CardTitle>
          <CardDescription>{data.mode}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Test Cases</p>
              <p className="text-3xl font-bold">{data.items}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Code Precision</p>
              <p className="text-3xl font-bold text-primary">{data.codes_precision.toFixed(2)}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Code Recall</p>
              <p className="text-3xl font-bold text-primary">{data.codes_recall.toFixed(2)}</p>
            </div>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground">Code F1 Score</p>
              <p className="text-3xl font-bold text-primary">{data.codes_f1.toFixed(2)}</p>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Summary Fact Coverage</p>
              <p className="text-2xl font-bold text-primary">{data.summary_coverage.toFixed(2)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-4">
        <h2 className="text-2xl font-semibold mb-4">Test Case Results</h2>
        {data.test_results && data.test_results.length > 0 ? (
          data.test_results.map((result) => (
            <TestCaseCard key={result.id} result={result} />
          ))
        ) : (
          <Card>
            <CardContent className="py-8">
              <p className="text-center text-muted-foreground">No test results available</p>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
