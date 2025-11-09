import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t border-emerald-900/20 bg-slate-950 text-emerald-200/80">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-6 py-6 text-xs md:flex-row">
        <p>© {new Date().getFullYear()} Homie. Local travel beyond the crowd.</p>
        <div className="flex items-center gap-4">
          <Link href="/privacy" className="hover:text-emerald-100">
            Privacy
          </Link>
          <Link href="/imprint" className="hover:text-emerald-100">
            Imprint
          </Link>
        </div>
      </div>
    </footer>
  );
}


