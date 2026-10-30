import { Section } from "@/components/section";

const ASSUMPTIONS: [string, string][] = [
  [
    "The question",
    "If you had to plan the day before, using the latest wind forecast available at your decision time, how far off would it have been?",
  ],
  [
    "Data",
    "Elexon national GB wind: actual output (FUELHH, half-hourly) and the day-ahead wind forecast (WINDFOR, hourly). Delivery 2 January to 1 February 2026.",
  ],
  [
    "Decision time",
    "A time on the day before delivery, in UK time (default 09:00). For each hour we take the newest forecast published at or before that time. A forecast published later is never used.",
  ],
  [
    "Matching",
    "Forecasts are hourly and actuals half-hourly, so the two half-hours inside each forecast hour are averaged before comparing.",
  ],
  [
    "Error",
    "Forecast minus actual. Positive means the forecast promised more wind than came, so you would have been short.",
  ],
  [
    "Missing data",
    "Hours with no forecast before the decision time, or no actual, are skipped and counted under coverage, never filled in.",
  ],
  ["Times", "Charts and tables are in UTC. In January UTC and UK time are the same."],
];

/** Plain-language assumptions behind every number on the page. */
export function AboutPanel() {
  return (
    <Section
      id="about"
      title="About this analysis"
      description="What the numbers mean and how they were made."
    >
      <dl className="grid gap-x-6 gap-y-3 text-sm sm:grid-cols-[10rem_1fr]">
        {ASSUMPTIONS.map(([term, text]) => (
          <div key={term} className="contents">
            <dt className="font-medium">{term}</dt>
            <dd className="text-muted-foreground">{text}</dd>
          </div>
        ))}
      </dl>
    </Section>
  );
}
