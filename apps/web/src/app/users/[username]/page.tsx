"use client";

import Link from "next/link";
import { useMemo } from "react";

import { AI_EXPERTISE_TAGS, type ExpertiseTag } from "../../../constants/ai-tags";
import { usePublicUser } from "../../../hooks/use-public-user";

interface UserProfilePageProps {
  params: { username: string };
}

export default function UserProfilePage({ params }: UserProfilePageProps) {
  const username = useMemo(() => params.username?.toLowerCase() ?? "", [params.username]);
  const { data: profile, error, isLoading } = usePublicUser(username);

  if (isLoading) {
    return (
      <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
        <p className="text-sm text-slate-400">Loading profile…</p>
      </main>
    );
  }

  if (error?.status === 404 || !profile) {
    return (
      <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
        <div className="w-full max-w-xl space-y-4 text-center">
          <h1 className="text-3xl font-semibold text-slate-50">Profile not found</h1>
          <p className="text-sm text-slate-400">
            We couldn’t find a member with the username <span className="text-slate-200">@{username}</span>.
          </p>
          <Link href="/" className="text-sm text-slate-200 underline decoration-dotted">
            Return home
          </Link>
        </div>
      </main>
    );
  }

  const displayName = profile.displayName?.trim() || `@${profile.username}`;
  const avatarLetter = displayName.trim().charAt(0)?.toUpperCase() || profile.username.charAt(0)?.toUpperCase() || "?";
  const expertiseTags = profile.expertiseTags.filter((tag): tag is ExpertiseTag =>
    AI_EXPERTISE_TAGS.includes(tag as ExpertiseTag),
  );

  return (
    <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
      <article className="w-full max-w-2xl space-y-8">
        <header className="flex items-start gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-slate-800 text-xl font-semibold text-slate-200">
            {profile.avatarUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={profile.avatarUrl}
                alt={`Avatar for ${displayName}`}
                className="h-16 w-16 rounded-full object-cover"
              />
            ) : (
              avatarLetter
            )}
          </div>
          <div className="space-y-1">
            <h1 className="text-3xl font-semibold text-slate-50">{displayName}</h1>
            <p className="text-sm text-slate-400">@{profile.username}</p>
            {profile.githubUsername ? (
              <p className="text-sm text-slate-400">
                GitHub: <span className="text-slate-200">{profile.githubUsername}</span>
              </p>
            ) : null}
          </div>
        </header>

        {profile.bio ? <p className="text-base text-slate-200">{profile.bio}</p> : null}

        <dl className="grid gap-6 rounded-md border border-slate-800 bg-slate-900/40 p-4 text-sm text-slate-300 sm:grid-cols-2">
          {profile.company ? (
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Company</dt>
              <dd className="text-slate-200">{profile.company}</dd>
            </div>
          ) : null}
          {profile.location ? (
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Location</dt>
              <dd className="text-slate-200">{profile.location}</dd>
            </div>
          ) : null}
          <div>
            <dt className="text-xs uppercase tracking-wide text-slate-500">Member since</dt>
            <dd className="text-slate-200">
              {new Date(profile.createdAt).toLocaleDateString(undefined, {
                year: "numeric",
                month: "short",
                day: "numeric",
              })}
            </dd>
          </div>
          {profile.updatedAt ? (
            <div>
              <dt className="text-xs uppercase tracking-wide text-slate-500">Updated</dt>
              <dd className="text-slate-200">
                {new Date(profile.updatedAt).toLocaleDateString(undefined, {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                })}
              </dd>
            </div>
          ) : null}
        </dl>

        {expertiseTags.length ? (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Expertise</h2>
            <ul className="flex flex-wrap gap-2">
              {expertiseTags.map((tag) => (
                <li key={tag} className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1 text-xs text-slate-200">
                  {tag}
                </li>
              ))}
            </ul>
          </section>
        ) : null}
      </article>
    </main>
  );
}
