"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { FormEvent, useState } from "react";

const loginEndpoint = "/api/auth/login";

type LoginFormState = {
  email: string;
  password: string;
};

export default function LoginPage() {
  const router = useRouter();
  const [form, setForm] = useState<LoginFormState>({ email: "", password: "" });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const response = await fetch(loginEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: form.email, password: form.password }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setError(payload?.detail ?? "Invalid credentials");
        setIsSubmitting(false);
        return;
      }

      router.push("/welcome");
    } catch {
      setError("Unable to sign in. Please try again.");
      setIsSubmitting(false);
    }
  };

  return (
    <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
      <div className="w-full max-w-md space-y-8">
        <div>
          <Link href="/" className="text-xs font-medium uppercase tracking-wide text-slate-400 hover:text-slate-200">
            ← Back
          </Link>
          <h1 className="mt-4 text-3xl font-semibold text-slate-50">Sign in to AIC HUB</h1>
          <p className="mt-2 text-sm text-slate-300">
            Sessions issue HttpOnly cookies and expose your email in the header. Sign out anytime from the global
            navigation.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-5" noValidate>
          <div className="space-y-2">
            <label htmlFor="email" className="text-sm font-medium text-slate-200">
              Work email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={form.email}
              onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
            />
          </div>

          <div className="space-y-2">
            <label htmlFor="password" className="text-sm font-medium text-slate-200">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={form.password}
              onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
            />
          </div>

          {error ? (
            <p role="alert" className="rounded-md border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
              {error}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={isSubmitting}
            className="inline-flex w-full items-center justify-center rounded-md bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-70"
          >
            {isSubmitting ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="space-y-2 text-xs text-slate-400">
          <p>
            Need an account? {" "}
            <Link href="/auth/signup" className="text-slate-200 underline decoration-dotted">
              Create one here
            </Link>
            .
          </p>
          <p>
            Prefer OAuth? {" "}
            <Link href="/api/auth/login/github" className="text-slate-200 underline decoration-dotted">
              Continue with GitHub
            </Link>
            .
          </p>
        </div>
      </div>
    </main>
  );
}
