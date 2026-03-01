"use client";

import type { ReactNode } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BellRing, CandlestickChart, CreditCard, LayoutDashboard, MoonStar, ShieldAlert, SunMedium, UserRound } from "lucide-react";
import { useTheme } from "next-themes";

import { LogoutButton } from "@/components/logout-button";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/screener", label: "Screener", icon: CandlestickChart },
  { href: "/watchlist", label: "Watchlist", icon: BellRing },
  { href: "/portfolio", label: "Paper Portfolio", icon: ShieldAlert },
  { href: "/account", label: "Account", icon: UserRound },
  { href: "/pricing", label: "Pricing", icon: CreditCard }
];

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { theme, setTheme } = useTheme();
  const isAuthPage = pathname.startsWith("/login");

  if (isAuthPage) {
    return <div className="min-h-screen bg-background text-foreground">{children}</div>;
  }

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="mx-auto flex min-h-screen max-w-[1600px]">
        <aside className="hidden w-72 flex-col border-r border-border/60 px-6 py-8 lg:flex">
          <div className="rounded-3xl bg-hero-glow p-5 shadow-soft">
            <p className="text-sm uppercase tracking-[0.24em] text-primary/80">Stock Screening Agent</p>
            <h1 className="mt-4 font-display text-3xl font-semibold leading-tight">Research that answers what matters first.</h1>
            <p className="mt-3 text-sm text-muted-foreground">Top opportunities, catalyst context, risk flags, and paper-trade oversight without broker execution.</p>
          </div>
          <nav className="mt-8 space-y-2">
            {navItems.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-medium transition-colors",
                  pathname === href ? "bg-primary text-primary-foreground shadow-card" : "text-muted-foreground hover:bg-accent hover:text-foreground"
                )}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            ))}
          </nav>
        </aside>

        <div className="flex min-h-screen flex-1 flex-col">
          <header className="sticky top-0 z-40 border-b border-border/50 bg-background/80 px-4 py-4 backdrop-blur lg:px-8">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.26em] text-muted-foreground">Subscription-ready research console</p>
                <h2 className="font-display text-2xl font-semibold">Stock Screening + Research Agent</h2>
              </div>
              <div className="flex items-center gap-3">
                <Button variant="outline" size="icon" onClick={() => setTheme(theme === "dark" ? "light" : "dark")}>
                  {theme === "dark" ? <SunMedium className="size-4" /> : <MoonStar className="size-4" />}
                </Button>
                <LogoutButton />
              </div>
            </div>
            <nav className="mt-4 flex gap-2 overflow-x-auto lg:hidden">
              {navItems.map(({ href, label }) => (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "rounded-full border px-4 py-2 text-sm whitespace-nowrap",
                    pathname === href ? "border-primary bg-primary text-primary-foreground" : "border-border bg-card"
                  )}
                >
                  {label}
                </Link>
              ))}
            </nav>
          </header>
          <main className="flex-1 px-4 py-6 lg:px-8">{children}</main>
          <div className="sticky bottom-0 z-40 border-t border-border/60 bg-background/95 px-4 py-3 backdrop-blur lg:hidden">
            <div className="grid grid-cols-4 gap-2">
              {navItems.slice(0, 4).map(({ href, label, icon: Icon }) => (
                <Link
                  key={href}
                  href={href}
                  className={cn(
                    "flex flex-col items-center gap-1 rounded-2xl px-2 py-2 text-xs",
                    pathname === href ? "bg-primary text-primary-foreground" : "text-muted-foreground"
                  )}
                >
                  <Icon className="size-4" />
                  {label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
