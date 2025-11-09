import Link from "next/link";
import type { Journey } from "@/data/journeys";

type JourneyPreviewCardProps = {
  journey: Journey;
};

const modeLabels: Record<Journey["segments"][number]["mode"], string> = {
  rail: "Rail",
  bike: "Bike",
  hike: "Hike",
};

export function JourneyPreviewCard({ journey }: JourneyPreviewCardProps) {
  return (
    <article className="group relative flex h-full flex-col overflow-hidden rounded-3xl border border-emerald-100/80 bg-white shadow-lg shadow-emerald-100/30 transition hover:-translate-y-1 hover:shadow-emerald-200/60 dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <div className="relative min-h-48 bg-gradient-to-br from-emerald-500 via-emerald-600 to-emerald-900 p-6 text-emerald-50">
        <p className="text-sm uppercase tracking-[0.25em] text-emerald-200/90">
          {journey.season} • {journey.durationDays} days
        </p>
        <h3 className="mt-3 text-2xl font-semibold leading-tight">
          {journey.title}
        </h3>
        <p className="mt-3 max-w-md text-sm text-emerald-100/85">
          {journey.heroTagline}
        </p>
        <div className="mt-6 flex flex-wrap gap-3 text-xs font-medium text-emerald-100/90">
          {journey.segments.slice(0, 3).map((segment) => (
            <span
              key={`${segment.from}-${segment.to}`}
              className="rounded-full bg-emerald-800/40 px-4 py-1 uppercase tracking-wide"
            >
              {modeLabels[segment.mode]} • {segment.distanceKm} km
            </span>
          ))}
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-6 p-6">
        <p className="text-sm text-slate-600 dark:text-emerald-100/85">
          {journey.summary}
        </p>
        <div className="space-y-3 rounded-2xl bg-emerald-50/80 p-4 dark:bg-emerald-900/40">
          <p className="text-xs font-semibold uppercase tracking-widest text-emerald-700 dark:text-emerald-200">
            Destinations from the viral video
          </p>
          <ul className="space-y-2 text-sm text-slate-700 dark:text-emerald-100/80">
            {journey.destinations.map((destination) => (
              <li key={destination.name} className="flex flex-col">
                <span className="font-semibold text-slate-800 dark:text-emerald-50">
                  {destination.name}
                </span>
                <span className="text-xs text-slate-500 dark:text-emerald-200/70">
                  {destination.summary}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-emerald-200/70">
          <span>{journey.userHomeBase}</span>
          <span>
            {journey.distanceKm} km total • {journey.carbonSavedKg} kg CO₂ saved
          </span>
        </div>
        <Link
          href={`/journeys/${journey.slug}`}
          className="mt-auto inline-flex items-center justify-center rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500 dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400"
        >
          View concept journey
        </Link>
      </div>
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.2),transparent_55%)] opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
    </article>
  );
}


