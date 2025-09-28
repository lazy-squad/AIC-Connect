import Link from "next/link";

const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";
const normalizedApiBase = apiBase.replace(/\/$/, "");
const githubAuthUrl = `${normalizedApiBase}/auth/login/github`;

export default function Home() {
  return (
    <main className="flex min-h-[calc(100vh-64px)] flex-col bg-slate-950 text-slate-100">
      <div className="mx-auto flex w-full max-w-4xl flex-1 flex-col justify-center gap-12 px-6 py-16">
        <section className="space-y-4 text-center sm:text-left">
          <span className="inline-flex items-center gap-2 rounded-full border border-slate-800 bg-slate-900/80 px-3 py-1 text-xs uppercase tracking-wide text-slate-300">
            AIC HUB Access
          </span>
          <h1 className="text-4xl font-semibold tracking-tight text-slate-50 sm:text-5xl">
            Choose how you’d like to sign in.
          </h1>
          <p className="text-base text-slate-300">
            Use your work email with a secure password or authenticate with GitHub. Sessions issue HttpOnly cookies and
            stay scoped to this origin so you can move between the web and API without CORS headaches.
          </p>
        </section>

        <section className="grid gap-6 sm:grid-cols-2">
          <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-slate-100">Email + Password</h2>
            <p className="mt-2 text-sm text-slate-300">
              Create an account or sign in with a password that’s at least eight characters and includes letters and
              numbers.
            </p>
            <div className="mt-6 flex flex-col gap-3">
              <Link
                href="/auth/signup"
                className="inline-flex items-center justify-center rounded-md bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-white"
              >
                Create an account
              </Link>
              <Link
                href="/auth/login"
                className="inline-flex items-center justify-center rounded-md border border-slate-700 px-4 py-2 text-sm font-semibold text-slate-200 transition hover:border-slate-500 hover:bg-slate-800"
              >
                Sign in with email
              </Link>
            </div>
          </article>

          <article className="rounded-xl border border-slate-800 bg-slate-900/60 p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-slate-100">GitHub</h2>
            <p className="mt-2 text-sm text-slate-300">
              Redirects through the FastAPI gateway, links the account if your email already exists, and creates a new
              user if not.
            </p>
            <div className="mt-6">
              <Link
                href={githubAuthUrl}
                prefetch={false}
                className="inline-flex w-full items-center justify-center gap-2 rounded-md border border-slate-700 bg-slate-900 px-4 py-2 text-sm font-semibold text-slate-100 transition hover:border-slate-500 hover:bg-slate-800"
              >
                <svg aria-hidden="true" viewBox="0 0 24 24" className="h-5 w-5 fill-current">
                  <path d="M12 .5a12 12 0 0 0-3.79 23.4c.6.11.82-.26.82-.58l-.02-2.26c-3.34.73-4.04-1.61-4.04-1.61-.55-1.41-1.35-1.79-1.35-1.79-1.1-.77.09-.76.09-.76 1.22.09 1.86 1.27 1.86 1.27 1.08 1.86 2.82 1.32 3.5 1.01.11-.79.42-1.32.76-1.62-2.67-.3-5.47-1.34-5.47-5.98 0-1.32.47-2.39 1.24-3.23-.13-.3-.54-1.52.12-3.17 0 0 1.01-.32 3.3 1.23a11.46 11.46 0 0 1 6 0c2.28-1.55 3.29-1.23 3.29-1.23.66 1.65.25 2.87.12 3.17.77.84 1.23 1.91 1.23 3.23 0 4.65-2.81 5.68-5.49 5.98.44.38.82 1.12.82 2.26l-.01 3.35c0 .32.21.7.83.58A12 12 0 0 0 12 .5Z" />
                </svg>
                Continue with GitHub
              </Link>
            </div>
          </article>
        </section>

        <footer className="space-y-1 text-xs text-slate-500">
          <p>API base URL: {normalizedApiBase}</p>
          <p>
            Need help getting started? Visit the <Link href="/welcome" className="underline decoration-dotted">welcome guide</Link>.
          </p>
        </footer>
      </div>
    </main>
  );
}
