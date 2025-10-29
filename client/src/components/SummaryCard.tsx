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

        <p className="leading-7">{summary.summary}</p>

        {summary.bullets?.length ? (
          <ul className="list-disc pl-6 space-y-1">
            {summary.bullets.map((b, i) => (
              <li key={i}>{b}</li>
            ))}
          </ul>
        ) : null}

        <div className="pt-2">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-muted-foreground">Confidence</span>
            <span className="text-sm text-muted-foreground">{pct}%</span>
          </div>
          <div className="h-2 rounded bg-muted">
            <div
              className="h-2 rounded bg-primary"
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
