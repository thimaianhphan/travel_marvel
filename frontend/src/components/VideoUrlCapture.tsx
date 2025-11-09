"use client";

import { useMemo, useState } from "react";

import { AlternativesRequestPayload, AlternativesResponse } from "@/models/alternatives";

type VideoUrlCaptureProps = {
  placeholder?: string;
  helperText?: string;
  userLat: number;
  userLon: number;
  searchRadiusKm: number;
  maxAlternatives?: number;
  onResult?: (data: AlternativesResponse) => void;
};

const modes = [
  { key: "video" as const, label: "Use video URL" },
  { key: "manual" as const, label: "Type destinations" },
];

export function VideoUrlCapture({
  placeholder = "https://youtube.com/watch?v=travel-story",
  helperText = "Paste a viral travel clip or provide your own destinations to discover nearby alternatives.",
  userLat,
  userLon,
  searchRadiusKm,
  maxAlternatives = 2,
  onResult,
}: VideoUrlCaptureProps) {
  const [mode, setMode] = useState<"video" | "manual">("video");
  const [videoUrl, setVideoUrl] = useState("");
  const [manualInput, setManualInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastResponse, setLastResponse] = useState<AlternativesResponse | null>(null);

  const apiBase = useMemo(
    () => process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://localhost:8000/api",
    [],
  );

  function buildPayload(): AlternativesRequestPayload | null {
    const base: AlternativesRequestPayload = {
      user_lat: userLat,
      user_lon: userLon,
      max_alternatives: maxAlternatives,
      search_radius_km: searchRadiusKm,
    };

    if (mode === "video") {
      if (!videoUrl.trim()) {
        setError("Drop a video URL first.");
        return null;
      }
      return { ...base, video_url: videoUrl.trim() };
    }

    const entries = manualInput
      .split(/\n|,/)
      .map((value) => value.trim())
      .filter(Boolean);

    if (entries.length === 0) {
      setError("Enter at least one destination.");
      return null;
    }

    return { ...base, manual_places: entries };
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);

    const payload = buildPayload();
    if (!payload) {
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${apiBase}/alternatives`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail ?? "Backend returned an error.");
      }

      const data: AlternativesResponse = await response.json();
      setLastResponse(data);
      onResult?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  }

  const showManual = mode === "manual";
  const dynamicHelperText = showManual
    ? "Type one or more destinations (comma or newline separated). Homie will look around and suggest quieter nearby alternatives."
    : helperText;

  return (
    <div className="w-full rounded-3xl border border-emerald-200 bg-white p-6 shadow-[0_20px_60px_rgba(16,185,129,0.12)]">
      <div className="flex flex-col gap-2">
        <div className="flex gap-2">
          {modes.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              onClick={() => {
                setMode(key);
                setError(null);
              }}
              className={`flex-1 rounded-xl border px-4 py-2 text-sm font-semibold transition ${
                mode === key
                  ? "border-emerald-400 bg-emerald-50 text-emerald-700 shadow-sm"
                  : "border-emerald-200 bg-white text-slate-600 hover:border-emerald-300"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <form className="flex flex-col gap-4 md:flex-row md:items-center" onSubmit={handleSubmit}>
          <label
            htmlFor="alternatives-input"
            className="text-sm font-semibold uppercase tracking-[0.4em] text-emerald-600/80"
          >
            {showManual ? "Destinations" : "Viral video URL"}
          </label>
          <div className="flex flex-1 flex-col gap-3 md:flex-row md:items-center">
            {showManual ? (
              <textarea
                id="alternatives-input"
                placeholder="Neuschwanstein Castle, Heidelberg Castle"
                value={manualInput}
                onChange={(event) => setManualInput(event.target.value)}
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-400 focus:ring-2 focus:ring-emerald-200"
                rows={3}
              />
            ) : (
              <input
                id="alternatives-input"
                type="url"
                placeholder={placeholder}
                value={videoUrl}
                onChange={(event) => setVideoUrl(event.target.value)}
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-emerald-400 focus:ring-2 focus:ring-emerald-200"
              />
            )}
            <button
              type="submit"
              disabled={loading}
              className="h-full rounded-xl bg-emerald-500 px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:bg-emerald-200 disabled:text-emerald-700"
            >
              {loading ? "Generating…" : "Find Alternatives"}
            </button>
          </div>
        </form>
      </div>

      <p className="mt-4 text-sm text-slate-600">{dynamicHelperText}</p>
      <p className="mt-1 text-xs text-slate-500">
        Current search radius: {Math.round(searchRadiusKm)} km. Larger areas may take a little longer to process.
      </p>
      {error && (
        <p className="mt-2 text-sm text-rose-500">
          {error}
        </p>
      )}
      {lastResponse && (
        <p className="mt-2 text-xs text-slate-500">
          Found {lastResponse.alternatives.length} alternative options for “{lastResponse.target_name}”.
        </p>
      )}
    </div>
  );
}