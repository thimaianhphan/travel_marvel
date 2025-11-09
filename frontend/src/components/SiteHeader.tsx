import Link from "next/link";

const navItems = [{ label: "Journeys", href: "/journeys" }];

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-emerald-100 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4 text-slate-900">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold text-emerald-600">
          <span className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-500/10 text-base font-bold uppercase tracking-wide text-emerald-600">
            HM
          </span>
          <span className="text-xl font-semibold text-slate-900">Homie</span>
        </Link>
        <nav className="hidden items-center gap-6 text-sm font-medium text-slate-500 md:flex">
          {navItems.map((item) => (
            <Link key={item.label} href={item.href} className="transition hover:text-emerald-600">
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}


