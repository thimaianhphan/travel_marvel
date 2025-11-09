import Link from "next/link";

const navItems = [{ label: "Journeys", href: "/journeys" }];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-emerald-900/20 bg-slate-950/80 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 text-emerald-50">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold text-emerald-300">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/20 text-base font-bold uppercase tracking-wide text-emerald-200">
            HM
          </span>
          <span className="text-xl font-semibold">Homie</span>
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium text-emerald-300/70 md:flex">
          {navItems.map((item) => (
            <Link key={item.label} href={item.href} className="transition hover:text-emerald-200">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}


