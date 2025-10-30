import { useQuery } from "@tanstack/react-query";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { CheckCircle2, XCircle, AlertCircle } from "lucide-react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";

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
}

async function fetchEvalResults(): Promise<EvalResults> {
  const res = await fetch("http://localhost:8000/eval/quick");
  if (!res.ok) throw new Error("Failed to fetch eval results");
  return res.json();
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
  const { data, isLoading, error } = useQuery({
    queryKey: ["evalResults"],
    queryFn: fetchEvalResults,
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Skeleton className="h-12 w-64 mb-6" />
        <Skeleton className="h-32 w-full mb-4" />
        <Skeleton className="h-64 w-full mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <Card className="border-destructive">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Eval Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">
              {error instanceof Error ? error.message : "An unknown error occurred"}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Evaluation Test Report</h1>
        <p className="text-muted-foreground">
          Comprehensive analysis of medical document processing performance
        </p>
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
