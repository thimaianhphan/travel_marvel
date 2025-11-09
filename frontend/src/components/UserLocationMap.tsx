"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const LeafletMapInner = dynamic(
  () => import("./LeafletMapInner").then((mod) => mod.LeafletMapInner),
  { ssr: false },
);

type UserLocationMapProps = {
  lat: number;
  lon: number;
  radiusKm: number;
  onLocationChange?: (lat: number, lon: number) => void;
  onRadiusChange?: (radiusKm: number) => void;
};

export function UserLocationMap({
  lat,
  lon,
  radiusKm,
  onLocationChange,
  onRadiusChange,
}: UserLocationMapProps) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return null;
  }

  return (
    <div className="space-y-4 text-left">
      <div className="h-72 w-full overflow-hidden rounded-3xl border border-emerald-500/30 bg-slate-900/40 shadow-[0_0_40px_rgba(16,185,129,0.08)]">
        <LeafletMapInner
          lat={lat}
          lon={lon}
          radiusKm={radiusKm}
          onLocationChange={onLocationChange}
        />
      </div>

      <div className="space-y-2">
        <div className="flex flex-col gap-1 text-sm text-emerald-200/80 md:flex-row md:items-center md:justify-between">
          <p>
            Location: {lat.toFixed(4)}, {lon.toFixed(4)}
          </p>
          {onRadiusChange && <p>Search radius: {Math.round(radiusKm)} km</p>}
        </div>
        {onRadiusChange && (
          <div className="flex items-center gap-3">
            <input
              type="range"
              min={10}
              max={250}
              step={5}
              value={radiusKm}
              onChange={(event) => onRadiusChange(Number(event.target.value))}
              className="w-full accent-emerald-400"
            />
          </div>
        )}
        <p className="text-xs text-emerald-300/60">
          Tap on the map to reposition. Wider circles explore more places but can take a little longer to compute.
        </p>
      </div>
    </div>
  );
}

