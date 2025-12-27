// /src/components/SummaryCard.tsx
import { Card, CardContent } from "@/components/ui/card";

type SummaryResult = {
  summary: string;
  bullets?: string[];
  citations?: string[];
  confidence?: number; // 0..1
};

function clamp01(n: number) {
  return Math.max(0, Math.min(1, n));
}

function SummaryCard({ summary }: { summary: SummaryResult }) {
  const conf =
    Number.isFinite(summary?.confidence as number)
      ? clamp01(summary.confidence as number)
      : 0.75;

  const pct = Math.round(conf * 100);
  const level = conf >= 0.7 ? "High" : conf >= 0.4 ? "Medium" : "Low";

  return (
    <Card>
      <CardContent className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold">Clinical Summary</h3>
            <p className="text-sm text-muted-foreground">
              Provider-facing structured summary
            </p>
          </div>
          <div className="text-sm px-3 py-1 rounded-md bg-muted">{level}</div>
        </div>

        <p className="leading-7 text-slate-700">{summary.summary}</p>

        {summary.bullets?.length ? (
          <div className="space-y-2">
            <h4 className="font-semibold text-sm text-slate-600">Detailed Breakdown:</h4>
            <ul className="list-disc pl-6 space-y-3">
              {summary.bullets.map((b, i) => (
                <li key={i} className="text-sm leading-relaxed text-slate-700">{b}</li>
              ))}
            </ul>
          </div>
        ) : null}

        <div className="pt-4 border-t">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-muted-foreground">Confidence</span>
            <span className="text-sm font-semibold text-muted-foreground">{pct}%</span>
          </div>
          <div className="h-2 rounded-full bg-muted overflow-hidden">
            <div
              className="h-2 rounded-full bg-gradient-to-r from-blue-500 to-blue-600 transition-all duration-300"
              style={{ width: `${pct}%` }}
              aria-label="summary-confidence"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default SummaryCard;
export { SummaryCard }; // <-- named export too
