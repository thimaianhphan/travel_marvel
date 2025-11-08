import Link from "next/link";
import { JourneyPreviewCard } from "@/components/JourneyPreviewCard";
import { journeys } from "@/data/journeys";

export const metadata = {
  title: "Concept Journeys | Travel Marvel",
};

export default function JourneysPage() {
  return (
    <div className="mx-auto max-w-6xl px-6 py-16 md:py-24">
      <div className="max-w-3xl space-y-6">
        <span className="inline-flex rounded-full border border-emerald-200/70 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:border-emerald-500/40 dark:bg-emerald-900/40 dark:text-emerald-200">
          Concept Library
        </span>
        <h1 className="text-4xl font-semibold text-slate-900 md:text-5xl dark:text-emerald-50">
          Two remixed journeys to inspire the final Travel Marvel flow.
        </h1>
        <p className="text-lg text-slate-600 dark:text-emerald-100/80">
          Each itinerary is built from the same backend contracts we&apos;ll
          wire up later—from viral video parsing, to alternative destinations,
          to scenic pathfinding across Baden-Württemberg. Explore the structure,
          layout, and copy tone here first.
        </p>
      </div>
      <div className="mt-12 grid gap-12 lg:grid-cols-2">
        {journeys.map((journey) => (
          <JourneyPreviewCard key={journey.slug} journey={journey} />
        ))}
      </div>
      <div className="mt-16 rounded-3xl border border-emerald-200/60 bg-white/80 p-8 shadow-lg shadow-emerald-100/40">
        <h2 className="text-2xl font-semibold text-slate-900 dark:text-emerald-50">
          Next up in the build
        </h2>
        <ul className="mt-4 list-disc space-y-2 pl-5 text-sm text-slate-600 dark:text-emerald-100/80">
          <li>Connect the video ingestion flow once the backend is ready.</li>
          <li>
            Visualize the multi-segment path on a map canvas with POIs.
          </li>
          <li>
            Layer in sustainability nudges like off-peak suggestions and carbon
            savings comparisons.
          </li>
        </ul>
        <Link
          href="/"
          className="mt-6 inline-flex items-center justify-center rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500 dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400"
        >
          Back to landing page
        </Link>
      </div>
    </div>
  );
}


