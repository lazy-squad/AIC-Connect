import Link from "next/link";

export default function WelcomePage() {
  return (
    <main className="flex min-h-screen flex-col bg-slate-950 text-slate-100">
      <div className="mx-auto flex w-full max-w-2xl flex-1 flex-col gap-6 px-6 py-16">
        <Link
          href="/"
          className="w-fit text-xs font-medium uppercase tracking-wide text-slate-400 hover:text-slate-200"
        >
          ← Back
        </Link>
        <h1 className="text-4xl font-semibold tracking-tight text-slate-50">Welcome to AIC HUB</h1>
        <p className="text-base text-slate-300">
          You successfully reached the welcome page scaffold. OAuth callbacks and magic links are placeholders
          for now—track the FastAPI logs to observe requests. When onboarding is ready, this page will outline
          provider-specific steps and workspace provisioning status.
        </p>
        <ul className="list-disc space-y-2 pl-6 text-sm text-slate-300">
          <li>GitHub OAuth flows redirect through the FastAPI backend.</li>
          <li>Magic link emails are written to development logs instead of being sent.</li>
          <li>Local development runs over HTTP on http://localhost:3000 with Next.js rewrites to the FastAPI backend.</li>
        </ul>
      </div>
    </main>
  );
}
