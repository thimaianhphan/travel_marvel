type VideoUrlCaptureProps = {
  placeholder?: string;
  helperText?: string;
};

export function VideoUrlCapture({
  placeholder = "https://youtube.com/watch?v=travel-story",
  helperText = "Drop a viral travel video URL to remix it for Baden-Württemberg.",
}: VideoUrlCaptureProps) {
  return (
    <div className="w-full max-w-3xl rounded-2xl border border-emerald-200/70 bg-white/90 p-6 shadow-lg shadow-emerald-100/40 backdrop-blur dark:border-emerald-500/40 dark:bg-emerald-950/60 dark:shadow-emerald-900/40">
      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <label
          htmlFor="video-url"
          className="text-sm font-semibold uppercase tracking-widest text-emerald-700 dark:text-emerald-200"
        >
          Viral video URL
        </label>
        <div className="flex flex-1 flex-col gap-3 md:flex-row md:items-center">
          <input
            id="video-url"
            type="url"
            placeholder={placeholder}
            disabled
            className="w-full rounded-xl border border-emerald-200/70 bg-emerald-50/60 px-4 py-3 text-sm text-slate-800 outline-none transition focus:border-emerald-400 focus:ring-2 focus:ring-emerald-200/80 disabled:cursor-not-allowed disabled:border-emerald-200 disabled:text-slate-500 dark:border-emerald-500/40 dark:bg-emerald-900/50 dark:text-emerald-100 dark:disabled:border-emerald-700 dark:disabled:text-emerald-300"
          />
          <button
            disabled
            className="h-full rounded-xl bg-emerald-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-300 dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400 dark:disabled:bg-emerald-700/60"
          >
            Generate route
          </button>
        </div>
      </div>
      <p className="mt-4 text-sm text-slate-600 dark:text-emerald-100/80">
        {helperText}
      </p>
      <p className="mt-2 text-xs text-slate-400 dark:text-emerald-200/60">
        Hackathon preview: the backend route builder is coming soon. For now we
        visualize two concept journeys.
      </p>
    </div>
  );
}


