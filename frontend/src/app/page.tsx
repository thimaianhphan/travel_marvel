'use client';

import { useState } from "react";
import Link from "next/link";

import { VideoUrlCapture } from "@/components/VideoUrlCapture";
import { AlternativesResults } from "@/components/AlternativesResults";
import { UserLocationMap } from "@/components/UserLocationMap";
import { AlternativesResponse } from "@/models/alternatives";

const DEFAULT_LAT = 49.4875;
const DEFAULT_LON = 8.4660;
const DEFAULT_RADIUS_KM = 120;

export default function Home() {
  const [alternatives, setAlternatives] = useState<AlternativesResponse | null>(null);
  const [userLat, setUserLat] = useState(DEFAULT_LAT);
  const [userLon, setUserLon] = useState(DEFAULT_LON);
  const [searchRadiusKm, setSearchRadiusKm] = useState(DEFAULT_RADIUS_KM);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-emerald-50 via-white to-white px-6 py-16 text-slate-900">
      <div className="w-full max-w-4xl space-y-12 text-center">
        <div className="space-y-4">
          <span className="inline-block text-xs font-semibold uppercase tracking-[0.6em] text-emerald-600/70">
            Homie
          </span>
          <h1 className="text-4xl font-semibold leading-tight text-slate-900 md:text-5xl">
            Local travel beyond the crowd.
          </h1>
          <p className="mx-auto max-w-2xl text-sm text-slate-600">
            Paste a viral trip or type the places on your mind. Homie surfaces alternate destinations nearby so you can explore with fewer crowds and more local flavour.
          </p>
        </div>

        <UserLocationMap
          lat={userLat}
          lon={userLon}
          radiusKm={searchRadiusKm}
          onLocationChange={(lat, lon) => {
            setUserLat(lat);
            setUserLon(lon);
          }}
          onRadiusChange={setSearchRadiusKm}
        />

        <VideoUrlCapture
          userLat={userLat}
          userLon={userLon}
          searchRadiusKm={searchRadiusKm}
          onResult={setAlternatives}
        />

        {alternatives && (
          <div className="pt-12">
            <AlternativesResults data={alternatives} originLat={userLat} originLon={userLon} />
          </div>
        )}

        <p className="pt-16 text-xs text-slate-500">
          <Link href="/imprint" className="hover:text-emerald-600">
            Imprint
          </Link>
          <span className="px-2" aria-hidden>
            •
          </span>
          <Link href="/privacy" className="hover:text-emerald-600">
            Privacy
          </Link>
        </p>
      </div>
    </div>
  );
}
