'use client';

import { useMemo, useState } from "react";

import { AlternativeRoute, AlternativesResponse } from "@/models/alternatives";
import { RouteDetailMap } from "@/components/RouteDetailMap";

type AlternativesResultsProps = {
  data: AlternativesResponse;
  originLat: number;
  originLon: number;
};

export function AlternativesResults({ data, originLat, originLon }: AlternativesResultsProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);

  const selectedRoute = useMemo(() => {
    if (selectedIndex === null) return null;
    return data.alternatives[selectedIndex] ?? null;
  }, [data.alternatives, selectedIndex]);

  if (!data.alternatives.length) {
    return (
      <section className="mx-auto w-full max-w-5xl rounded-3xl border border-emerald-500/30 bg-slate-900/40 px-6 py-10 text-left text-emerald-50">
        <h2 className="text-2xl font-semibold">No alternatives found yet</h2>
        <p className="mt-2 text-sm text-emerald-300/70">
          Adjust the destination or widen the search radius to uncover quieter spots nearby.
        </p>
      </section>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-10 text-left text-emerald-50">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-300/70">
          Suggested alternatives
        </p>
        <h2 className="text-3xl font-semibold">
          Remix “{data.target_name}” into regional adventures.
        </h2>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {data.alternatives.map((route, index) => (
          <RouteCard
            key={`${route.destination.name}-${route.destination.lat}-${route.destination.lon}`}
            route={route}
            isSelected={index === selectedIndex}
            onSelect={() => setSelectedIndex(index === selectedIndex ? null : index)}
          />
        ))}
      </div>

      {selectedRoute && (
        <div className="space-y-6 rounded-3xl border border-emerald-500/30 bg-slate-900/50 p-6 shadow-[0_0_40px_rgba(16,185,129,0.08)]">
          <header className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-300/70">
              Map view
            </p>
            <h3 className="text-2xl font-semibold text-emerald-50">
              {selectedRoute.destination.name}
            </h3>
            <p className="text-sm text-emerald-300/70">
              Start from your location, weave through waypoints, and arrive at the alternative destination.
            </p>
          </header>

          <div className="h-[420px] overflow-hidden rounded-3xl border border-emerald-500/30 bg-slate-900">
            <RouteDetailMap
              originLat={originLat}
              originLon={originLon}
              route={selectedRoute}
            />
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <article className="space-y-3">
              <h4 className="text-sm font-semibold uppercase tracking-[0.35em] text-emerald-300/80">
                Destination insight
              </h4>
              <p className="text-lg text-emerald-100/80">
                {selectedRoute.destination.name} ({selectedRoute.destination.poi_type.replace(/_/g, " ")})
              </p>
              <p className="text-xs text-emerald-300/70">
                Coordinates: {selectedRoute.destination.lat.toFixed(4)}, {selectedRoute.destination.lon.toFixed(4)}
              </p>
            </article>

            <article className="space-y-3">
              <h4 className="text-sm font-semibold uppercase tracking-[0.35em] text-emerald-300/80">
                Waypoints on the way
              </h4>
              {selectedRoute.scenic_waypoints.length ? (
                <ul className="space-y-2 text-sm text-emerald-100/80">
                  {selectedRoute.scenic_waypoints.map((poi) => (
                    <li key={`${poi.name}-${poi.lat}-${poi.lon}`}>
                      <p className="font-medium text-emerald-50">{poi.name}</p>
                      <p className="text-xs text-emerald-300/70">
                        {poi.poi_type.replace(/_/g, " ")} • {poi.lat.toFixed(4)}, {poi.lon.toFixed(4)}
                      </p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-emerald-300/60">Direct route — no mid-way stops required.</p>
              )}
            </article>
          </div>
        </div>
      )}
    </section>
  );
}

function RouteCard({
  route,
  isSelected,
  onSelect,
}: {
  route: AlternativeRoute;
  isSelected: boolean;
  onSelect: () => void;
}) {
  return (
    <article className={`flex h-full flex-col justify-between rounded-3xl border ${
      isSelected ? "border-emerald-400/60" : "border-emerald-500/30"
    } bg-slate-900/50 p-6 shadow-[0_0_40px_rgba(16,185,129,0.06)] transition`}
    >
      <header className="space-y-1">
        <h3 className="text-xl font-semibold text-emerald-50">{route.destination.name}</h3>
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
              route.scenic_waypoints.slice(0, 3).map((poi) => (
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

      <button
        type="button"
        onClick={onSelect}
        className="mt-4 inline-flex items-center justify-center rounded-full border border-emerald-400/40 px-4 py-2 text-sm font-semibold text-emerald-200 transition hover:border-emerald-300 hover:text-emerald-100"
      >
        {isSelected ? "Hide details" : "View details"}
      </button>
    </article>
  );
}
