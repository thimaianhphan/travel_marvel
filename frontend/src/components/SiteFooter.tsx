import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-slate-200 bg-gradient-to-b from-emerald-950 via-emerald-900 to-emerald-950 text-emerald-50">
      <div className="mx-auto flex max-w-6xl flex-col gap-10 px-6 py-16 md:flex-row md:items-start md:justify-between">
        <div className="max-w-md space-y-3">
          <p className="text-sm uppercase tracking-wide text-emerald-300/90">
            Travel Marvel
          </p>
          <h3 className="text-2xl font-semibold">
            Slow down, stay local, spark new stories.
          </h3>
          <p className="text-sm text-emerald-100/80">
            Concept built for the Cassini hackathon to champion sustainable
            micro-adventures from Baden-Württemberg.
          </p>
        </div>
        <div className="grid grid-cols-1 gap-8 text-sm md:grid-cols-2">
          <div className="space-y-3">
            <p className="font-semibold text-emerald-200">Explore</p>
            <ul className="space-y-2 text-emerald-100/80">
              <li>
                <Link
                  href="/journeys"
                  className="transition hover:text-white"
                >
                  Sample journeys
                </Link>
              </li>
              <li>
                <Link href="/#impact" className="transition hover:text-white">
                  Impact approach
                </Link>
              </li>
              <li>
                <Link
                  href="/#how-it-works"
                  className="transition hover:text-white"
                >
                  Workflow outline
                </Link>
              </li>
            </ul>
          </div>
          <div className="space-y-3">
            <p className="font-semibold text-emerald-200">Connect</p>
            <ul className="space-y-2 text-emerald-100/80">
              <li>
                <Link
                  href="mailto:hello@travelmarvel.local"
                  className="transition hover:text-white"
                >
                  Email the team
                </Link>
              </li>
              <li>
                <Link
                  href="https://www.komoot.com/de-de"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="transition hover:text-white"
                >
                  Inspired by Komoot
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
      <div className="border-t border-emerald-800/80 bg-emerald-950/70">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-5 text-xs text-emerald-200/80 md:flex-row">
          <p>© {new Date().getFullYear()} Travel Marvel. Built for exploration.</p>
          <div className="flex items-center gap-4">
            <Link href="/privacy" className="hover:text-white">
              Privacy
            </Link>
            <Link href="/imprint" className="hover:text-white">
              Imprint
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}


