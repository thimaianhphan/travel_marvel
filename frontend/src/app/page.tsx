import Link from "next/link";
import { featuredJourneys } from "@/data/journeys";
import { JourneyPreviewCard } from "@/components/JourneyPreviewCard";
import { VideoUrlCapture } from "@/components/VideoUrlCapture";

const impactStats = [
  {
    label: "Community-run spots mapped",
    value: "150+",
    description: "Co-ops, bakeries, hostels within Baden-Württemberg loops.",
  },
  {
    label: "Average CO₂ saved per trip",
    value: "32 kg",
    description: "Rail-first routing vs. single-car road trips.",
  },
  {
    label: "Journey remix time",
    value: "<60s",
    description: "From viral video to local-friendly itinerary.",
  },
];

export default function Home() {
  return (
    <div className="relative overflow-hidden">
      <section className="relative mx-auto flex max-w-6xl flex-col items-center gap-16 px-6 pb-24 pt-16 text-center md:items-start md:text-left lg:pt-24">
        <div className="absolute inset-0 -z-10 bg-[radial-gradient(circle_at_top_left,#bbf7d0,transparent_55%),radial-gradient(circle_at_bottom_right,#c4b5fd,transparent_45%)] opacity-60" />
        <div className="flex w-full flex-col gap-6">
          <span className="inline-flex items-center gap-2 self-center rounded-full border border-emerald-200/70 bg-white/70 px-4 py-2 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 md:self-start dark:border-emerald-400/40 dark:bg-emerald-900/40 dark:text-emerald-200">
            Sustainable Journeys
          </span>
          <h1 className="text-4xl font-semibold leading-tight text-slate-900 sm:text-5xl md:text-6xl dark:text-emerald-50">
            Turn viral wanderlust into Baden-Württemberg micro-adventures.
          </h1>
          <p className="max-w-2xl text-lg text-slate-600 md:text-xl dark:text-emerald-100/85">
            Travel Marvel listens to the destinations hyped in your favorite
            videos and remixes them into low-carbon itineraries stitched
            together with local gems between Stuttgart, the Black Forest, and
            the Swabian Alb.
          </p>
        </div>
        <VideoUrlCapture />
        <div className="grid w-full gap-6 md:grid-cols-3">
          {impactStats.map((item) => (
            <div
              key={item.label}
              className="rounded-3xl border border-emerald-200/60 bg-white/80 p-6 text-left shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/40 dark:shadow-emerald-900/40"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
                {item.label}
              </p>
              <p className="mt-4 text-3xl font-semibold text-emerald-600 dark:text-emerald-200">
                {item.value}
              </p>
              <p className="mt-2 text-sm text-slate-600 dark:text-emerald-100/80">
                {item.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section
        id="how-it-works"
        className="mx-auto max-w-6xl px-6 py-20 md:py-24"
      >
        <div className="max-w-2xl space-y-4">
          <span className="inline-flex rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200">
            How it works
          </span>
          <h2 className="text-3xl font-semibold text-slate-900 md:text-4xl dark:text-emerald-50">
            Three steps to remix any viral itinerary for local sustainability.
          </h2>
          <p className="text-lg text-slate-600 dark:text-emerald-100/80">
            We fetch the hotspots from the video transcript, match them with
            reachable alternatives, then thread a scenic arc through rail,
            cycling, and hiking segments dotted with community-owned stops.
          </p>
        </div>
        <div className="mt-12 grid gap-8 md:grid-cols-3">
          <article className="rounded-3xl border border-emerald-200/70 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/40 dark:shadow-emerald-900/40">
            <p className="text-emerald-600 dark:text-emerald-200">01.</p>
            <h3 className="mt-4 text-xl font-semibold text-slate-900 dark:text-emerald-50">
              Understand the viral hype
            </h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-emerald-100/80">
              Extract destination mentions, sentiment, and travel style hints
              from the source video or creator captions.
            </p>
          </article>
          <article className="rounded-3xl border border-emerald-200/70 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/40 dark:shadow-emerald-900/40">
            <p className="text-emerald-600 dark:text-emerald-200">02.</p>
            <h3 className="mt-4 text-xl font-semibold text-slate-900 dark:text-emerald-50">
              Swap in Baden-Württemberg chapters
            </h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-emerald-100/80">
              Use our POI discovery service to find alternative destinations
              within train reach, focusing on low-season and local operators.
            </p>
          </article>
          <article className="rounded-3xl border border-emerald-200/70 bg-white/90 p-8 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/40 dark:shadow-emerald-900/40">
            <p className="text-emerald-600 dark:text-emerald-200">03.</p>
            <h3 className="mt-4 text-xl font-semibold text-slate-900 dark:text-emerald-50">
              Thread the scenic loop
            </h3>
            <p className="mt-2 text-sm text-slate-600 dark:text-emerald-100/80">
              Plot a not-quite-shortest path linking all highlights, focusing on
              story-rich segments over raw efficiency.
            </p>
          </article>
        </div>
      </section>

      <section
        id="impact"
        className="relative mx-auto max-w-6xl px-6 py-20 md:py-24"
      >
        <div className="absolute inset-0 -z-10 rounded-[3rem] bg-gradient-to-br from-emerald-500/15 via-white to-emerald-100/40" />
        <div className="flex flex-col gap-10 md:flex-row md:items-center">
          <div className="flex-1 space-y-6">
            <span className="inline-flex rounded-full bg-emerald-700/10 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-200">
              Featured journeys
            </span>
            <h2 className="text-3xl font-semibold text-slate-900 md:text-4xl dark:text-emerald-50">
              Try the concept journeys we already remixed for Baden-Württemberg.
            </h2>
            <p className="text-lg text-slate-600 dark:text-emerald-100/80">
              Explore how the backend will feed in POIs, transport legs, and
              sustainability nudges—all presented in a UI paying homage to the
              clean, confident Komoot style.
            </p>
            <Link
              href="/journeys"
              className="inline-flex items-center justify-center rounded-full border border-emerald-400 bg-white px-5 py-3 text-sm font-semibold text-emerald-700 transition hover:border-emerald-500 hover:text-emerald-900 dark:border-emerald-400/60 dark:bg-emerald-950/60 dark:text-emerald-200 dark:hover:border-emerald-300 dark:hover:text-emerald-100"
            >
              Browse all concept journeys
            </Link>
          </div>
          <div className="flex-1">
            <div className="grid gap-8 lg:grid-cols-2">
              {featuredJourneys.map((journey) => (
                <JourneyPreviewCard key={journey.slug} journey={journey} />
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
