import Link from "next/link";

const navItems = [
  { label: "Journeys", href: "/journeys" },
  { label: "How it Works", href: "/#how-it-works" },
  { label: "Why Local", href: "/#impact" },
];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-emerald-100/70 bg-white/85 backdrop-blur-md dark:border-emerald-800/50 dark:bg-slate-950/80">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 text-slate-900 dark:text-emerald-50">
        <Link
          href="/"
          className="flex items-center gap-2 text-lg font-semibold text-emerald-700 transition-colors hover:text-emerald-900 dark:text-emerald-300 dark:hover:text-emerald-200"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-600/10 text-base font-bold uppercase tracking-wide text-emerald-700 dark:bg-emerald-400/10 dark:text-emerald-200">
            TM
          </span>
          <span className="text-xl font-semibold text-slate-900 dark:text-emerald-50">
            Travel Marvel
          </span>
        </Link>
        <nav className="hidden items-center gap-8 text-sm font-medium text-slate-600 md:flex dark:text-emerald-200">
          {navItems.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              className="relative transition-colors hover:text-emerald-700 dark:hover:text-emerald-100"
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <Link
          href="/journeys"
          className="rounded-full bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-500 dark:bg-emerald-500 dark:text-slate-950 dark:hover:bg-emerald-400"
        >
          See sample route
        </Link>
      </div>
    </header>
  );
}


