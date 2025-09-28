"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

type CurrentUser = {
  email: string;
  displayName?: string | null;
};

export function Header() {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    let active = true;
    const loadUser = async () => {
      try {
        const response = await fetch("/api/me", { credentials: "include" });
        if (!response.ok) {
          if (!active) return;
          setUser(null);
          return;
        }
        const data = (await response.json()) as CurrentUser;
        if (active) {
          setUser(data);
        }
      } catch {
        if (active) {
          setUser(null);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    };

    void loadUser();

    return () => {
      active = false;
    };
  }, []);

  const handleLogout = async () => {
    setError(null);
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) {
        setError("Logout failed. Please try again.");
        return;
      }
      setUser(null);
      router.refresh();
    } catch {
      setError("Logout failed. Please try again.");
    }
  };

  return (
    <header className="border-b border-slate-800 bg-slate-950/80">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-sm font-semibold text-slate-200 hover:text-white">
            AIC HUB
          </Link>
          <nav className="hidden md:flex items-center gap-4 text-sm">
            <Link href="/articles" className="text-slate-300 hover:text-white">
              Articles
            </Link>
            <Link href="/feed" className="text-slate-300 hover:text-white">
              Feed
            </Link>
            <Link href="/spaces" className="text-slate-300 hover:text-white">
              Spaces
            </Link>
          </nav>
        </div>

        {isLoading ? (
          <span className="text-xs text-slate-500">Loading session…</span>
        ) : user ? (
          <div className="flex items-center gap-3 text-sm text-slate-200">
            <Link
              href="/articles/new"
              className="text-slate-300 hover:text-white"
            >
              Write
            </Link>
            <Link
              href="/drafts"
              className="text-slate-300 hover:text-white"
            >
              My Drafts
            </Link>
            <Link
              href="/spaces?my_spaces=true"
              className="text-slate-300 hover:text-white"
            >
              My Spaces
            </Link>
            <span>
              Signed in as {user.displayName?.trim() || user.email}
            </span>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
            >
              Log out
            </button>
          </div>
        ) : (
          <nav className="flex items-center gap-4 text-sm">
            <Link href="/auth/login" className="text-slate-300 hover:text-white">
              Sign in
            </Link>
            <Link
              href="/auth/signup"
              className="rounded-md bg-slate-200 px-3 py-1 font-semibold text-slate-900 transition hover:bg-white"
            >
              Create account
            </Link>
          </nav>
        )}
      </div>
      {error ? <p className="bg-red-500/10 px-6 py-2 text-center text-xs text-red-200">{error}</p> : null}
    </header>
  );
}
