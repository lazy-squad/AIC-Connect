"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { useCurrentUser } from "../hooks/use-current-user";

export function Header() {
  const router = useRouter();
  const { data: user, error: userError, mutate, isValidating } = useCurrentUser();
  const [logoutError, setLogoutError] = useState<string | null>(null);

  const isLoading = user === undefined && !userError && isValidating;

  const handleLogout = async () => {
    setLogoutError(null);
    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "include",
      });
      if (!response.ok) {
        setLogoutError("Logout failed. Please try again.");
        return;
      }
      await mutate(null, { revalidate: false });
      router.refresh();
    } catch {
      setLogoutError("Logout failed. Please try again.");
    }
  };

  return (
    <header className="border-b border-slate-800 bg-slate-950/80">
      <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-sm font-semibold text-slate-200 hover:text-white">
          AIC HUB
        </Link>

        {isLoading ? (
          <span className="text-xs text-slate-500">Loading session…</span>
        ) : user ? (
          <nav className="flex items-center gap-4 text-sm text-slate-200">
            <span>
              Signed in as {user.displayName?.trim() || `@${user.username}`}
            </span>
            <Link
              href={`/users/${user.username}`}
              className="rounded-md border border-slate-800 px-3 py-1 text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
            >
              View profile
            </Link>
            <Link
              href="/settings/profile"
              className="rounded-md border border-slate-800 px-3 py-1 text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
            >
              Edit profile
            </Link>
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md border border-slate-700 px-3 py-1 text-xs font-medium text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
            >
              Log out
            </button>
          </nav>
        ) : userError ? (
          <span className="text-xs text-red-300">Unable to load session</span>
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
      {logoutError ? <p className="bg-red-500/10 px-6 py-2 text-center text-xs text-red-200">{logoutError}</p> : null}
    </header>
  );
}
