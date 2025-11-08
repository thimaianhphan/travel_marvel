"use client";

import { useMemo, useState } from "react";
import {
  MapContainer,
  Marker,
  Polyline,
  TileLayer,
  Tooltip,
  useMap,
} from "react-leaflet";
import type {
  LatLngBoundsExpression,
  LatLngExpression,
  LatLngTuple,
} from "leaflet";
import { divIcon, latLngBounds } from "leaflet";
import type { Journey, PointOfInterest } from "@/data/journeys";
import "leaflet/dist/leaflet.css";

type JourneyMapProps = {
  journey: Journey;
};

type JourneyMapPoint = {
  key: string;
  name: string;
  description: string;
  coordinates: [number, number];
  type: "home" | "destination" | "poi";
  extra?: string;
  municipality?: string;
};

const markerColors: Record<JourneyMapPoint["type"], string> = {
  home: "#10b981",
  destination: "#2563eb",
  poi: "#f97316",
};

const createMarkerIcon = (color: string) =>
  divIcon({
    className: "journey-map-marker",
    html: `<div style="
        width: 22px;
        height: 22px;
        border-radius: 9999px;
        border: 3px solid white;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.28);
        background: ${color};
      "></div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -11],
  });

const markerIconCache: Record<JourneyMapPoint["type"], ReturnType<
  typeof createMarkerIcon
>> = {
  home: createMarkerIcon(markerColors.home),
  destination: createMarkerIcon(markerColors.destination),
  poi: createMarkerIcon(markerColors.poi),
};

function BoundsUpdater({
  bounds,
  slug,
}: {
  bounds: LatLngBoundsExpression;
  slug: string;
}) {
  const map = useMap();

  useMemo(() => {
    map.fitBounds(bounds, { padding: [48, 48] });
  }, [map, bounds, slug]);

  return null;
}

export function JourneyMap({ journey }: JourneyMapProps) {
  const [selectedPoint, setSelectedPoint] = useState<JourneyMapPoint | null>(
    null,
  );

  const mapPoints = useMemo<JourneyMapPoint[]>(() => {
    const destinationPoints: JourneyMapPoint[] = journey.destinations.map(
      (destination) => ({
        key: `destination-${destination.name}`,
        name: destination.name,
        description: destination.summary,
        extra: destination.travelTip,
        coordinates: destination.coordinates,
        type: "destination",
      }),
    );

    const poiPoints: JourneyMapPoint[] = journey.featuredPoi.map(
      (poi: PointOfInterest) => ({
        key: `poi-${poi.name}`,
        name: poi.name,
        description: poi.description,
        coordinates: poi.coordinates,
        type: "poi",
        municipality: poi.municipality,
      }),
    );

    return [
      {
        key: "home-base",
        name: journey.userHomeBase,
        description: "Suggested starting point for this remix.",
        coordinates: journey.homeBaseCoordinates,
        type: "home",
        extra: journey.heroTagline,
      },
      ...destinationPoints,
      ...poiPoints,
    ];
  }, [journey]);

  const pathPositions = useMemo<LatLngExpression[]>(() => {
    if (!journey.mapPath.length) {
      return [];
    }
    return journey.mapPath.map(
      (coords) => [coords[0], coords[1]] as LatLngTuple,
    );
  }, [journey.mapPath]);

  const bounds = useMemo<LatLngBoundsExpression>(() => {
    const coordinatePool = pathPositions.length
      ? pathPositions
      : mapPoints.map((point) => point.coordinates);

    const validPool =
      coordinatePool.length > 0
        ? coordinatePool
        : [journey.homeBaseCoordinates];

    const calculatedBounds = latLngBounds(
      validPool.map(([lat, lng]) => [lat, lng]) as LatLngTuple[],
    );

    return calculatedBounds.pad(0.12);
  }, [journey.homeBaseCoordinates, mapPoints, pathPositions]);

  const primaryCenter = journey.homeBaseCoordinates as LatLngTuple;

  return (
    <div className="relative z-0">
      <MapContainer
        key={journey.slug}
        center={primaryCenter}
        bounds={bounds}
        className="z-0 h-[420px] w-full overflow-hidden rounded-[2.5rem] border border-emerald-200/70 shadow-xl shadow-emerald-100/40 dark:border-emerald-500/40 dark:shadow-emerald-900/40"
        scrollWheelZoom={false}
        preferCanvas
      >
        <BoundsUpdater bounds={bounds} slug={journey.slug} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {pathPositions.length > 1 && (
          <Polyline
            positions={pathPositions}
            pathOptions={{
              color: "#0ea5e9",
              weight: 6,
              opacity: 0.75,
              dashArray: "12 12",
            }}
          />
        )}
        {mapPoints.map((point) => (
          <Marker
            key={point.key}
            position={point.coordinates}
            icon={markerIconCache[point.type]}
            eventHandlers={{
              click: () => setSelectedPoint(point),
            }}
          >
            <Tooltip direction="top" offset={[0, -10]}>
              {point.name}
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>

      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center pb-6">
        <div className="rounded-full bg-white/80 px-4 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 shadow-md shadow-emerald-100/40 backdrop-blur dark:bg-emerald-950/70 dark:text-emerald-200 dark:shadow-emerald-900/30">
          Interactive route preview
        </div>
      </div>

      {selectedPoint && (
        <aside className="pointer-events-auto absolute bottom-6 left-6 right-6 z-30 mx-auto max-w-md rounded-3xl border border-emerald-200/60 bg-white/95 p-6 shadow-xl shadow-emerald-100/50 backdrop-blur-lg transition-all dark:border-emerald-500/40 dark:bg-emerald-950/80 dark:text-emerald-100 dark:shadow-emerald-900/40 md:left-auto md:right-10">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-700 dark:text-emerald-200">
                {selectedPoint.type === "home"
                  ? "Home base"
                  : selectedPoint.type === "destination"
                    ? "Video destination"
                    : "Point of interest"}
              </p>
              <h3 className="mt-2 text-lg font-semibold text-slate-900 dark:text-emerald-50">
                {selectedPoint.name}
              </h3>
            </div>
            <button
              type="button"
              onClick={() => setSelectedPoint(null)}
              className="rounded-full border border-emerald-200/60 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-emerald-700 transition hover:border-emerald-400 hover:text-emerald-900 dark:border-emerald-600/50 dark:text-emerald-200 dark:hover:border-emerald-300 dark:hover:text-emerald-100"
            >
              Close
            </button>
          </div>
          <p className="mt-3 text-sm text-slate-600 dark:text-emerald-100/80">
            {selectedPoint.description}
          </p>
          {selectedPoint.extra && (
            <p className="mt-3 text-sm font-medium text-emerald-700 dark:text-emerald-200/80">
              {selectedPoint.extra}
            </p>
          )}
          {selectedPoint.municipality && (
            <p className="mt-3 text-xs uppercase tracking-[0.3em] text-slate-500 dark:text-emerald-200/60">
              {selectedPoint.municipality}
            </p>
          )}
        </aside>
      )}
    </div>
  );
}

