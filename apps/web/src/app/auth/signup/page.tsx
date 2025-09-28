"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { FormEvent, useState } from "react";

const signupEndpoint = "/api/auth/signup";
const passwordHint = "Use at least 8 characters with letters and numbers.";

type SignupFormState = {
  email: string;
  password: string;
  displayName: string;
};

export default function SignupPage() {
  const router = useRouter();
  const [form, setForm] = useState<SignupFormState>({ email: "", password: "", displayName: "" });
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (form.password.length < 8 || !/[a-zA-Z]/.test(form.password) || !/\d/.test(form.password)) {
      setError(passwordHint);
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(signupEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          displayName: form.displayName.trim() || undefined,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setError(payload?.detail ?? "Unable to create your account. Try again.");
        setIsSubmitting(false);
        return;
      }

      router.push("/welcome");
    } catch {
      setError("Unable to create your account. Try again.");
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
          <h1 className="mt-4 text-3xl font-semibold text-slate-50">Create your account</h1>
          <p className="mt-2 text-sm text-slate-300">
            Passwords are validated server-side with Argon2id hashing. You’ll be redirected to the welcome page once
            signed in.
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
            <label htmlFor="displayName" className="text-sm font-medium text-slate-200">
              Display name <span className="text-xs text-slate-400">(optional)</span>
            </label>
            <input
              id="displayName"
              name="displayName"
              type="text"
              autoComplete="name"
              value={form.displayName}
              onChange={(event) => setForm((prev) => ({ ...prev, displayName: event.target.value }))}
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
              autoComplete="new-password"
              required
              value={form.password}
              onChange={(event) => setForm((prev) => ({ ...prev, password: event.target.value }))}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
              aria-describedby="password-hint"
            />
            <p id="password-hint" className="text-xs text-slate-400">
              {passwordHint}
            </p>
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
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="text-xs text-slate-400">
          Already have access? {" "}
          <Link href="/auth/login" className="text-slate-200 underline decoration-dotted">
            Sign in
          </Link>
          .
        </p>
      </div>
    </main>
  );
}
