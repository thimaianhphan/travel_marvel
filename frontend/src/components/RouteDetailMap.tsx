"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";

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
const CircleMarker = dynamic(
  () => import("react-leaflet").then((mod) => mod.CircleMarker),
  { ssr: false },
) as any;
const Tooltip = dynamic(
  () => import("react-leaflet").then((mod) => mod.Tooltip),
  { ssr: false },
) as any;

import "leaflet/dist/leaflet.css";

type RouteDetailMapProps = {
  originLat: number;
  originLon: number;
  route: AlternativeRoute;
};

const toLatLngTuple = (lat: number, lon: number) => (Number.isFinite(lat) && Number.isFinite(lon) ? ([lat, lon] as [number, number]) : null);

export function RouteDetailMap({ originLat, originLon, route }: RouteDetailMapProps) {
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

  const waypointCoordinates = useMemo(
    () =>
      route.scenic_waypoints
        .map((poi) => ({
          key: `${poi.name}-${poi.lat}-${poi.lon}`,
          position: toLatLngTuple(poi.lat, poi.lon),
          name: poi.name,
        }))
        .filter((poi) => poi.position !== null),
    [route.scenic_waypoints],
  );

  const fallbackPath = useMemo(() => {
    const coordinates: [number, number][] = [];
    if (origin) coordinates.push(origin);
    waypointCoordinates.forEach((poi) => coordinates.push(poi.position!));
    if (destination) coordinates.push(destination);
    return coordinates;
  }, [destination, origin, waypointCoordinates]);

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

  return (
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
        <CircleMarker
          center={origin}
          radius={7}
          pathOptions={{ color: "#facc15", fillColor: "#facc15", fillOpacity: 1 }}
        >
          <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent>
            You
          </Tooltip>
        </CircleMarker>
      )}

      {waypointCoordinates.map((poi) => (
        <CircleMarker
          key={poi.key}
          center={poi.position!}
          radius={6}
          pathOptions={{ color: "#38bdf8", fillColor: "#38bdf8", fillOpacity: 1 }}
        >
          <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent>
            {poi.name}
          </Tooltip>
        </CircleMarker>
      ))}

      {destination && (
        <CircleMarker
          center={destination}
          radius={7}
          pathOptions={{ color: "#34d399", fillColor: "#34d399", fillOpacity: 1 }}
        >
          <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent>
            {route.destination.name}
          </Tooltip>
        </CircleMarker>
      )}
    </MapContainer>
  );
}

