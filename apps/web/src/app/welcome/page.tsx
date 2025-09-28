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
          Authentication is now live. Email + password accounts issue Argon2id-backed session cookies, and GitHub SSO
          links or provisions users automatically. Review the notes below before connecting providers or inviting your
          team.
        </p>
        <ul className="list-disc space-y-2 pl-6 text-sm text-slate-300">
          <li>Sessions use an HttpOnly cookie (`SameSite=Lax`, `Secure=false` in local HTTP) and expire after seven days.</li>
          <li>Signup and login endpoints enforce per-email/IP rate limits to reduce credential stuffing.</li>
          <li>GitHub OAuth never stores access tokens—only the provider account ID.</li>
          <li>All flows run over the shared origin http://localhost:3000 via Next.js rewrites to the FastAPI backend.</li>
        </ul>
      </div>
    </main>
  );
}
