"use client";

import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Circle,
  CircleMarker,
  useMap,
  useMapEvents,
} from "react-leaflet";
import "leaflet/dist/leaflet.css";

type LeafletMapInnerProps = {
  lat: number;
  lon: number;
  radiusKm: number;
  onLocationChange?: (lat: number, lon: number) => void;
};

function MapSync({ lat, lon }: { lat: number; lon: number }) {
  const map = useMap();

  useEffect(() => {
    map.setView([lat, lon]);
  }, [lat, lon, map]);

  return null;
}

function MapClickHandler({
  onLocationChange,
}: {
  onLocationChange?: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click: (event) => {
      onLocationChange?.(event.latlng.lat, event.latlng.lng);
    },
  });
  return null;
}

export function LeafletMapInner({
  lat,
  lon,
  radiusKm,
  onLocationChange,
}: LeafletMapInnerProps) {
  return (
    <MapContainer
      center={[lat, lon]}
      zoom={8}
      zoomControl={false}
      scrollWheelZoom={false}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <Circle
        center={[lat, lon]}
        radius={radiusKm * 1000}
        pathOptions={{ color: "#34d399", fillColor: "#34d399", fillOpacity: 0.08, weight: 1.5 }}
      />
      <CircleMarker
        center={[lat, lon]}
        radius={6}
        pathOptions={{ color: "#34d399", fillColor: "#34d399", fillOpacity: 1 }}
      />
      <MapSync lat={lat} lon={lon} />
      <MapClickHandler onLocationChange={onLocationChange} />
    </MapContainer>
  );
}

