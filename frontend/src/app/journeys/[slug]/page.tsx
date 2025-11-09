import { notFound } from "next/navigation";
import Link from "next/link";
import { JourneyMapClient } from "@/components/JourneyMapClient";
import { getJourneyBySlug, journeys, type Journey } from "@/data/journeys";

type JourneyPageProps = {
  params: Promise<{ slug: string }>;
};

export async function generateStaticParams() {
  return journeys.map((journey) => ({ slug: journey.slug }));
}

export async function generateMetadata({ params }: JourneyPageProps) {
  const { slug } = await params;
  const journey = getJourneyBySlug(slug);

  if (!journey) {
    return {
      title: "Journey not found | Travel Marvel",
    };
  }

  return {
    title: `${journey.title} | Travel Marvel`,
    description: journey.summary,
  } as const;
}

export default async function JourneyDetailPage({ params }: JourneyPageProps) {
  const { slug } = await params;
  const journey = getJourneyBySlug(slug);

  if (!journey) {
    notFound();
  }

  const definedJourney = journey as Journey;

  return (
    <div className="mx-auto max-w-5xl px-6 py-16 md:py-24">
      <Breadcrumbs journey={definedJourney} />
      <header className="mt-6 overflow-hidden rounded-[3rem] bg-gradient-to-br from-emerald-100 via-emerald-50 to-white p-10 text-slate-900 shadow-xl shadow-emerald-100/50">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div className="max-w-2xl space-y-4">
            <span className="inline-flex rounded-full border border-emerald-200 bg-white/80 px-3 py-1 text-xs font-semibold uppercase tracking-[0.35em] text-emerald-700">
              {definedJourney.season} • {definedJourney.durationDays} days
            </span>
            <h1 className="text-4xl font-semibold leading-tight md:text-5xl">
              {definedJourney.title}
            </h1>
            <p className="text-lg text-slate-600">{definedJourney.summary}</p>
          </div>
          <div className="rounded-3xl bg-white/80 p-6 text-sm text-slate-700 shadow-inner shadow-emerald-50">
            <p className="font-semibold uppercase tracking-[0.3em] text-emerald-700">
              Journey stats
            </p>
            <ul className="mt-4 space-y-3">
              <li>
                <span className="text-slate-500">Total distance</span>{" "}
                <span className="font-semibold text-slate-900">
                  {definedJourney.distanceKm} km
                </span>
              </li>
              <li>
                <span className="text-slate-500">CO₂ saved</span>{" "}
                <span className="font-semibold text-slate-900">
                  {definedJourney.carbonSavedKg} kg
                </span>
              </li>
              <li>
                <span className="text-slate-500">Home base</span>{" "}
                <span className="font-semibold text-slate-900">
                  {definedJourney.userHomeBase}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </header>

      <section className="mt-16 md:mt-20">
        <JourneyMapClient journey={definedJourney} />
      </section>

      <section className="mt-12 grid gap-10 lg:grid-cols-[2fr_1fr]">
        <div className="space-y-10">
          <VideoSource journey={definedJourney} />
          <Segments journey={definedJourney} />
          <SustainabilityNotes journey={definedJourney} />
        </div>
        <div className="space-y-10">
          <Destinations journey={definedJourney} />
          <PointsOfInterest journey={definedJourney} />
        </div>
      </section>
    </div>
  );
}

function Breadcrumbs({ journey }: { journey: Journey }) {
  return (
    <nav className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-emerald-200/70">
      <Link
        href="/"
        className="transition hover:text-emerald-600 dark:hover:text-emerald-100"
      >
        Home
      </Link>
      <span>•</span>
      <Link
        href="/journeys"
        className="transition hover:text-emerald-600 dark:hover:text-emerald-100"
      >
        Journeys
      </Link>
      <span>•</span>
      <span className="text-slate-800 dark:text-emerald-50">{journey.title}</span>
    </nav>
  );
}

function VideoSource({ journey }: { journey: Journey }) {
  return (
    <article className="rounded-3xl border border-emerald-200/60 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
        Source video
      </p>
      <h2 className="mt-4 text-2xl font-semibold text-slate-900 dark:text-emerald-50">
        {journey.videoTitle}
      </h2>
      <p className="mt-3 text-sm text-slate-600 dark:text-emerald-100/80">
        We analyzed this creator&apos;s footage to extract the locations they
        rave about, then looked for regional equivalents accessible from{" "}
        {journey.userHomeBase}.
      </p>
      <Link
        href={journey.videoUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="mt-6 inline-flex items-center justify-center rounded-full bg-emerald-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-emerald-500 dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400"
      >
        Open YouTube video
      </Link>
    </article>
  );
}

function Segments({ journey }: { journey: Journey }) {
  return (
    <article className="rounded-3xl border border-emerald-200/60 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
        Route narrative
      </p>
      <h2 className="mt-4 text-2xl font-semibold text-slate-900 dark:text-emerald-50">
        Scenic-first path between highlights
      </h2>
      <ol className="mt-6 space-y-6">
        {journey.segments.map((segment, index) => (
          <li key={`${segment.from}-${segment.to}`} className="flex gap-4">
            <span className="mt-1 flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-sm font-semibold text-emerald-700">
              {String(index + 1).padStart(2, "0")}
            </span>
            <div className="space-y-1">
              <p className="text-sm font-semibold uppercase tracking-[0.3em] text-emerald-600 dark:text-emerald-200">
                {segment.mode.toUpperCase()} • {segment.distanceKm} km
              </p>
              <p className="text-lg font-semibold text-slate-900 dark:text-emerald-50">
                {segment.from} → {segment.to}
              </p>
              <p className="text-sm text-slate-600 dark:text-emerald-100/80">
                {segment.narrative}
              </p>
            </div>
          </li>
        ))}
      </ol>
    </article>
  );
}

function Destinations({ journey }: { journey: Journey }) {
  return (
    <aside className="rounded-3xl border border-emerald-200/60 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
        Viral hotspots remixed
      </p>
      <ul className="mt-6 space-y-4">
        {journey.destinations.map((destination) => (
          <li key={destination.name} className="space-y-2">
            <p className="text-lg font-semibold text-slate-900 dark:text-emerald-50">
              {destination.name}
            </p>
            <p className="text-sm text-slate-600 dark:text-emerald-100/80">
              {destination.summary}
            </p>
            <p className="text-xs text-emerald-700 dark:text-emerald-200/70">
              {destination.travelTip}
            </p>
          </li>
        ))}
      </ul>
    </aside>
  );
}

function PointsOfInterest({ journey }: { journey: Journey }) {
  return (
    <aside className="rounded-3xl border border-emerald-200/60 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
        Points of interest en route
      </p>
      <ul className="mt-6 space-y-4">
        {journey.featuredPoi.map((poi) => (
          <li key={poi.name} className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-base font-semibold text-slate-900 dark:text-emerald-50">
                {poi.name}
              </p>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-200">
                {poi.category}
              </span>
            </div>
            <p className="text-sm text-slate-600 dark:text-emerald-100/80">
              {poi.description}
            </p>
            <p className="text-xs text-slate-500 dark:text-emerald-200/70">
              {poi.municipality}
            </p>
          </li>
        ))}
      </ul>
    </aside>
  );
}

function SustainabilityNotes({ journey }: { journey: Journey }) {
  return (
    <article className="rounded-3xl border border-emerald-200/60 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
        Sustainability rationale
      </p>
      <p className="mt-4 text-lg text-slate-600 dark:text-emerald-100/80">
        {journey.sustainabilityNotes}
      </p>
    </article>
  );
}

