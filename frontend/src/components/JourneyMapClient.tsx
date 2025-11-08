"use client";

import dynamic from "next/dynamic";
import type { Journey } from "@/data/journeys";

const JourneyMapDynamic = dynamic(
  () => import("./JourneyMap").then((mod) => mod.JourneyMap),
  {
    ssr: false,
    loading: () => (
      <div className="flex h-[420px] w-full items-center justify-center rounded-[2.5rem] border border-emerald-200/70 bg-white/70 text-sm font-medium text-emerald-600 shadow-lg shadow-emerald-100/40 dark:border-emerald-500/40 dark:bg-emerald-950/50 dark:text-emerald-200 dark:shadow-emerald-900/40">
        Loading map preview…
      </div>
    ),
  },
);

type JourneyMapClientProps = {
  journey: Journey;
};

export function JourneyMapClient({ journey }: JourneyMapClientProps) {
  return <JourneyMapDynamic journey={journey} />;
}

