"use client";

import { AlternativesResponse, AlternativeRoute } from "@/models/alternatives";

type AlternativesResultsProps = {
  data: AlternativesResponse;
};

export function AlternativesResults({ data }: AlternativesResultsProps) {
  if (!data.alternatives.length) {
    return (
      <section className="mx-auto w-full max-w-5xl rounded-3xl border border-emerald-500/30 bg-slate-900/40 px-6 py-10 text-left text-emerald-50">
        <h2 className="text-2xl font-semibold">No alternatives found yet</h2>
        <p className="mt-2 text-sm text-emerald-300/70">
          Adjust the destination or widen the search area to uncover quieter spots nearby.
        </p>
      </section>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-6 text-left text-emerald-50">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-300/70">
          Suggested alternatives
        </p>
        <h2 className="text-3xl font-semibold">
          Remix “{data.target_name}” into regional adventures.
        </h2>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {data.alternatives.map((route) => (
          <RouteCard
            key={`${route.destination.name}-${route.destination.lat}-${route.destination.lon}`}
            route={route}
          />
        ))}
      </div>
    </section>
  );
}

function RouteCard({ route }: { route: AlternativeRoute }) {
  return (
    <article className="flex h-full flex-col justify-between rounded-3xl border border-emerald-500/30 bg-slate-900/50 p-6 shadow-[0_0_40px_rgba(16,185,129,0.08)]">
      <header className="space-y-1">
        <h3 className="text-xl font-semibold text-emerald-50">
          {route.destination.name}
        </h3>
        <p className="text-sm text-emerald-300/70">
          {route.destination.poi_type.replace(/_/g, " ")} • Score {route.score !== null ? route.score.toFixed(2) : "n/a"}
        </p>
      </header>

      <dl className="mt-4 grow space-y-4 text-sm text-emerald-100/80">
        <div>
          <dt className="font-semibold text-emerald-200/80">Coordinates</dt>
          <dd className="mt-1 font-mono text-xs text-emerald-300/70">
            {route.destination.lat.toFixed(4)}, {route.destination.lon.toFixed(4)}
          </dd>
        </div>

        <div>
          <dt className="font-semibold text-emerald-200/80">Waypoints en route</dt>
          <dd className="mt-2 space-y-3">
            {route.scenic_waypoints.length ? (
              route.scenic_waypoints.map((poi) => (
                <div key={`${poi.name}-${poi.lat}-${poi.lon}`}>
                  <p className="font-medium text-emerald-50">{poi.name}</p>
                  <p className="text-xs text-emerald-300/70">
                    {poi.poi_type.replace(/_/g, " ")} • {poi.lat.toFixed(4)}, {poi.lon.toFixed(4)}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-xs text-emerald-300/60">Direct route — no mid-way stops required.</p>
            )}
          </dd>
        </div>
      </dl>
    </article>
  );
}

