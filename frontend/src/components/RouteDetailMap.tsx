"use client";

import dynamic from "next/dynamic";
import { useEffect, useMemo, useState } from "react";

import type { AlternativeRoute } from "@/models/alternatives";

const MapContainer = dynamic(
  () => import("react-leaflet").then((mod) => mod.MapContainer),
  { ssr: false },
) as any;
const TileLayer = dynamic(
  () => import("react-leaflet").then((mod) => mod.TileLayer),
  { ssr: false },
) as any;
const Polyline = dynamic(
  () => import("react-leaflet").then((mod) => mod.Polyline),
  { ssr: false },
) as any;
const Marker = dynamic(
  () => import("react-leaflet").then((mod) => mod.Marker),
  { ssr: false },
) as any;
const Tooltip = dynamic(
  () => import("react-leaflet").then((mod) => mod.Tooltip),
  { ssr: false },
) as any;

import "leaflet/dist/leaflet.css";
import type { Icon } from "leaflet";

type RouteDetailMapProps = {
  originLat: number;
  originLon: number;
  route: AlternativeRoute;
};

type MarkerInfo = {
  id: string;
  name: string;
  type: string;
  coords: [number, number];
  icon: Icon;
  score: number | null;
  tags?: Record<string, unknown>;
  isDestination?: boolean;
  imageUrl: string | null;
  description: string | null;
};

type WaypointEntry = {
  key: string;
  coords: [number, number];
  poi: AlternativeRoute["scenic_waypoints"][number];
};

type MarkerIcons = {
  origin: Icon;
  waypoint: Icon;
  destination: Icon;
};

const DEFAULT_ICON_SIZE: [number, number] = [32, 32];
const DEFAULT_ICON_ANCHOR: [number, number] = [16, 32];

const formatPoiType = (type: string) => type.replace(/_/g, " ");

const extractImageUrl = (tags?: Record<string, unknown>): string | null => {
  if (!tags) return null;

  const candidateKeys = [
    "image",
    "image_url",
    "photo",
    "photo_url",
    "picture",
    "thumbnail",
    "image:0",
    "image0",
  ];

  for (const key of candidateKeys) {
    const value = tags[key];
    if (typeof value === "string" && value.startsWith("http")) {
      return value;
    }
  }

  return null;
};

const extractDescription = (tags?: Record<string, unknown>): string | null => {
  if (!tags) return null;
  const order = ["description", "short_description", "note", "wikidata_description", "about"];
  for (const key of order) {
    const value = tags[key];
    if (typeof value === "string" && value.trim().length > 0) {
      return value;
    }
  }
  return null;
};

const toLatLngTuple = (lat: number, lon: number) => (Number.isFinite(lat) && Number.isFinite(lon) ? ([lat, lon] as [number, number]) : null);

export function RouteDetailMap({ originLat, originLon, route }: RouteDetailMapProps) {
  const [selectedMarker, setSelectedMarker] = useState<MarkerInfo | null>(null);
  const [icons, setIcons] = useState<MarkerIcons | null>(null);

  useEffect(() => {
    setSelectedMarker(null);
  }, [route]);

  useEffect(() => {
    let isMounted = true;
    const loadLeaflet = async () => {
      const leafletModule = await import("leaflet");
      const L = leafletModule.default ?? leafletModule;
      const origin = L.divIcon({
        className: "text-3xl select-none",
        html: "🧭",
        iconSize: DEFAULT_ICON_SIZE,
        iconAnchor: DEFAULT_ICON_ANCHOR,
      });
      const destination = L.divIcon({
        className: "text-3xl select-none",
        html: "🏁",
        iconSize: DEFAULT_ICON_SIZE,
        iconAnchor: DEFAULT_ICON_ANCHOR,
      });
      const waypoint = L.divIcon({
        className: "text-3xl select-none",
        html: "📍",
        iconSize: DEFAULT_ICON_SIZE,
        iconAnchor: DEFAULT_ICON_ANCHOR,
      });

      if (isMounted) {
        setIcons({
          origin,
          destination,
          waypoint,
        });
      }
    };

    loadLeaflet();

    return () => {
      isMounted = false;
    };
  }, []);

  const origin = useMemo(() => toLatLngTuple(originLat, originLon), [originLat, originLon]);
  const destination = useMemo(
    () => toLatLngTuple(route.destination.lat, route.destination.lon),
    [route.destination.lat, route.destination.lon],
  );

  const backendPath = useMemo(
    () =>
      (route.route_path ?? [])
        .map(([lat, lon]) => toLatLngTuple(lat, lon))
        .filter((coords): coords is [number, number] => coords !== null),
    [route.route_path],
  );

  const waypoints = useMemo(
    () =>
      route.scenic_waypoints
        .map((poi) => {
          const coords = toLatLngTuple(poi.lat, poi.lon);
          if (!coords) return null;
          return {
            key: `${poi.name}-${poi.lat}-${poi.lon}`,
            coords,
            poi,
          } satisfies WaypointEntry | null;
        })
        .filter((entry): entry is WaypointEntry => entry !== null),
    [route.scenic_waypoints],
  );

  const markers = useMemo(() => {
    if (!icons) return [];

    const waypointMarkers = waypoints.map<MarkerInfo>((entry) => ({
      id: `waypoint-${entry.key}`,
      name: entry.poi.name,
      type: entry.poi.poi_type,
      coords: entry.coords,
      icon: icons.waypoint,
      score: entry.poi.score ?? null,
      tags: entry.poi.tags,
      imageUrl: extractImageUrl(entry.poi.tags),
      description: extractDescription(entry.poi.tags),
    }));

    if (!destination) {
      return waypointMarkers;
    }

    const destinationMarker: MarkerInfo = {
      id: `destination-${route.destination.name}-${route.destination.lat}-${route.destination.lon}`,
      name: route.destination.name,
      type: route.destination.poi_type,
      coords: destination,
      icon: icons.destination,
      score: route.score ?? route.destination.score ?? null,
      tags: route.destination.tags,
      isDestination: true,
      imageUrl: extractImageUrl(route.destination.tags),
      description: extractDescription(route.destination.tags),
    };

    return [...waypointMarkers, destinationMarker];
  }, [
    destination,
    route.destination.lat,
    route.destination.lon,
    route.destination.name,
    route.destination.poi_type,
    route.destination.tags,
    route.destination.score,
    route.score,
    icons,
    waypoints,
  ]);

  const fallbackPath = useMemo(() => {
    const coordinates: [number, number][] = [];
    if (origin) coordinates.push(origin);
    waypoints.forEach((entry) => coordinates.push(entry.coords));
    if (destination) coordinates.push(destination);
    return coordinates;
  }, [destination, origin, waypoints]);

  const pathCoordinates = useMemo(
    () => (backendPath.length >= 2 ? backendPath : fallbackPath),
    [backendPath, fallbackPath],
  );

  const center = useMemo(() => {
    if (pathCoordinates.length > 0) {
      const { sumLat, sumLon } = pathCoordinates.reduce(
        (acc, [lat, lon]) => ({
          sumLat: acc.sumLat + lat,
          sumLon: acc.sumLon + lon,
        }),
        { sumLat: 0, sumLon: 0 },
      );
      return [sumLat / pathCoordinates.length, sumLon / pathCoordinates.length] as [number, number];
    }
    if (origin) return origin;
    if (destination) return destination;
    return [0, 0] as [number, number];
  }, [destination, origin, pathCoordinates]);

  if (!icons) {
    return (
      <div className="flex h-full w-full items-center justify-center rounded-3xl border border-emerald-500/30 bg-slate-900 text-sm text-emerald-200/70">
        Loading map…
      </div>
    );
  }

  return (
    <div className="relative h-full w-full">
      <MapContainer
        center={center}
        zoom={8}
        zoomControl={false}
        scrollWheelZoom={false}
        style={{ height: "100%", width: "100%" }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {pathCoordinates.length >= 2 && (
          <Polyline positions={pathCoordinates} pathOptions={{ color: "#34d399", weight: 4, opacity: 0.6 }} />
        )}

        {origin && (
          <Marker position={origin} icon={icons.origin}>
            <Tooltip direction="top" offset={[0, -24]} opacity={0.9} permanent>
              You
            </Tooltip>
          </Marker>
        )}

        {markers.map((marker) => (
          <Marker
            key={marker.id}
            position={marker.coords}
            icon={marker.icon}
            eventHandlers={{
              click: () => setSelectedMarker(marker),
            }}
          >
            <Tooltip direction="top" offset={[0, -24]} opacity={0.9}>
              {marker.name}
            </Tooltip>
          </Marker>
        ))}
      </MapContainer>

      {selectedMarker && (
        <div className="pointer-events-none absolute inset-0 flex items-end justify-start p-4">
          <div className="pointer-events-auto w-full max-w-sm rounded-3xl border border-emerald-500/40 bg-slate-900/95 shadow-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.25)]">
            <div className="flex items-start justify-between gap-4 border-b border-emerald-500/20 px-5 py-4">
              <div className="space-y-1">
                <p className="text-xs font-semibold uppercase tracking-[0.4em] text-emerald-300/80">
                  {selectedMarker.isDestination ? "Destination" : "Waypoint"}
                </p>
                <h4 className="text-lg font-semibold text-emerald-50">{selectedMarker.name}</h4>
                <p className="text-xs text-emerald-300/70">{formatPoiType(selectedMarker.type)}</p>
              </div>
              <button
                type="button"
                onClick={() => setSelectedMarker(null)}
                className="rounded-full border border-emerald-500/40 px-3 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-emerald-100 transition hover:bg-emerald-500/20"
              >
                Close
              </button>
            </div>
            <div className="space-y-4 px-5 py-4">
              {selectedMarker.imageUrl ? (
                <img
                  src={selectedMarker.imageUrl}
                  alt={selectedMarker.name}
                  className="h-36 w-full rounded-2xl object-cover"
                />
              ) : (
                <div className="flex h-36 w-full items-center justify-center rounded-2xl bg-slate-800/80 text-sm text-emerald-200/70">
                  No image found
                </div>
              )}
              {selectedMarker.description && (
                <p className="text-sm leading-relaxed text-emerald-100/80">{selectedMarker.description}</p>
              )}
              <dl className="grid grid-cols-2 gap-4 text-xs text-emerald-200/80">
                <div>
                  <dt className="font-semibold uppercase tracking-[0.3em] text-emerald-300/80">Coordinates</dt>
                  <dd className="mt-1 font-mono text-sm text-emerald-100">
                    {selectedMarker.coords[0].toFixed(4)}, {selectedMarker.coords[1].toFixed(4)}
                  </dd>
                </div>
                {selectedMarker.score !== null && (
                  <div>
                    <dt className="font-semibold uppercase tracking-[0.3em] text-emerald-300/80">Score</dt>
                    <dd className="mt-1 text-sm text-emerald-100">{selectedMarker.score.toFixed(2)}</dd>
                  </div>
                )}
              </dl>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

