import Link from "next/link";

export default function LoginSuccessPage() {
  return (
    <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-16 text-slate-100">
      <div className="flex w-full max-w-xl flex-col items-center gap-6 text-center">
        <h1 className="text-4xl font-semibold text-slate-50">You’re signed in</h1>
        <p className="text-base text-slate-300">
          Session cookies are active for the next seven days. Head to your profile settings to personalize your
          workspace, or jump straight into the app.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-3 text-sm">
          <Link
            href="/settings/profile"
            className="rounded-md bg-slate-200 px-4 py-2 font-semibold text-slate-900 transition hover:bg-white"
          >
            Edit profile
          </Link>
          <Link
            href="/welcome"
            className="rounded-md border border-slate-700 px-4 py-2 text-slate-100 transition hover:border-slate-500 hover:bg-slate-900"
          >
            View onboarding tips
          </Link>
          <Link href="/" className="text-slate-300 underline-offset-2 hover:text-white hover:underline">
            Back to home
          </Link>
        </div>
      </div>
    </main>
  );
}
