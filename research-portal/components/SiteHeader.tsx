import Link from "next/link";
import { NAV_ITEMS } from "@/lib/nav";
import { ThemeToggle } from "./ThemeToggle";

export function SiteHeader() {
  return (
    <header className="site-header">
      <div className="site-header-inner">
        <Link href="/" className="brand">
          Drift-Robust TinyML
          <span className="brand-sub">Chronological drift · resource-aware XAI · edge deployment</span>
        </Link>
        <nav className="nav" aria-label="Primary">
          {NAV_ITEMS.map((item) => (
            <Link key={item.href} href={item.href}>
              {item.label}
            </Link>
          ))}
        </nav>
        <ThemeToggle />
      </div>
    </header>
  );
}
