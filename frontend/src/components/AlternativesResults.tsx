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
      <section className="mx-auto w-full max-w-5xl rounded-3xl border border-emerald-200 bg-white px-6 py-10 text-left text-slate-900 shadow-[0_20px_60px_rgba(16,185,129,0.1)]">
        <h2 className="text-2xl font-semibold text-slate-900">No alternatives found yet</h2>
        <p className="mt-2 text-sm text-slate-600">
          Adjust the destination or widen the search radius to uncover quieter spots nearby.
        </p>
      </section>
    );
  }

  return (
    <section className="mx-auto w-full max-w-5xl space-y-10 text-left text-slate-900">
      <div className="space-y-2">
        <p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-600/80">
          Suggested alternatives
        </p>
        <h2 className="text-3xl font-semibold text-slate-900">
          {data.target_name} vibes, local edition.
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
        <div className="space-y-6 rounded-3xl border border-emerald-200 bg-white p-6 shadow-[0_20px_60px_rgba(16,185,129,0.08)]">
          <header className="space-y-2">
            <p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-600/80">
              Map view
            </p>
            <h3 className="text-2xl font-semibold text-slate-900">
              {selectedRoute.destination.name}
            </h3>
            <p className="text-sm text-slate-600">
              Start from your location, weave through waypoints, and arrive at the alternative destination.
            </p>
          </header>

          <div className="h-[420px] overflow-hidden rounded-3xl border border-emerald-200 bg-white">
            <RouteDetailMap
              originLat={originLat}
              originLon={originLon}
              route={selectedRoute}
            />
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <article className="space-y-3">
              <h4 className="text-sm font-semibold uppercase tracking-[0.35em] text-emerald-600/80">
                Destination insight
              </h4>
              <p className="text-lg text-slate-800">
                {selectedRoute.destination.name} ({selectedRoute.destination.poi_type.replace(/_/g, " ")})
              </p>
              <p className="text-xs text-slate-500">
                Coordinates: {selectedRoute.destination.lat.toFixed(4)}, {selectedRoute.destination.lon.toFixed(4)}
              </p>
            </article>

            <article className="space-y-3">
              <h4 className="text-sm font-semibold uppercase tracking-[0.35em] text-emerald-600/80">
                Waypoints on the way
              </h4>
              {selectedRoute.scenic_waypoints.length ? (
                <ul className="space-y-2 text-sm text-slate-700">
                  {selectedRoute.scenic_waypoints.map((poi) => (
                    <li key={`${poi.name}-${poi.lat}-${poi.lon}`}>
                      <p className="font-medium text-slate-900">{poi.name}</p>
                      <p className="text-xs text-slate-500">
                        {poi.poi_type.replace(/_/g, " ")} • {poi.lat.toFixed(4)}, {poi.lon.toFixed(4)}
                      </p>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-xs text-slate-500">Direct route — no mid-way stops required.</p>
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
    <article
      className={`flex h-full flex-col justify-between rounded-3xl border ${
        isSelected ? "border-emerald-400 bg-emerald-50/60" : "border-emerald-200 bg-white"
      } p-6 shadow-[0_20px_60px_rgba(16,185,129,0.08)] transition`}
    >
      <header className="space-y-1">
        <h3 className="text-xl font-semibold text-slate-900">{route.destination.name}</h3>
        <p className="text-sm text-slate-600">
          {route.destination.poi_type.replace(/_/g, " ")} • Score {route.score !== null ? route.score.toFixed(2) : "n/a"}
        </p>
      </header>

      <dl className="mt-4 grow space-y-4 text-sm text-slate-700">
        <div>
          <dt className="font-semibold text-emerald-600/80">Coordinates</dt>
          <dd className="mt-1 font-mono text-xs text-slate-500">
            {route.destination.lat.toFixed(4)}, {route.destination.lon.toFixed(4)}
          </dd>
        </div>

        <div>
          <dt className="font-semibold text-emerald-600/80">Waypoints en route</dt>
          <dd className="mt-2 space-y-3">
            {route.scenic_waypoints.length ? (
              route.scenic_waypoints.slice(0, 3).map((poi) => (
                <div key={`${poi.name}-${poi.lat}-${poi.lon}`}>
                  <p className="font-medium text-slate-900">{poi.name}</p>
                  <p className="text-xs text-slate-500">
                    {poi.poi_type.replace(/_/g, " ")} • {poi.lat.toFixed(4)}, {poi.lon.toFixed(4)}
                  </p>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-500">Direct route — no mid-way stops required.</p>
            )}
          </dd>
        </div>
      </dl>

      <button
        type="button"
        onClick={onSelect}
        className={`mt-4 inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-semibold transition ${
          isSelected
            ? "border-emerald-500 bg-emerald-500 text-white hover:bg-emerald-600"
            : "border-emerald-300 text-emerald-600 hover:bg-emerald-50"
        }`}
      >
        {isSelected ? "Hide details" : "View details"}
      </button>
    </article>
  );
}
