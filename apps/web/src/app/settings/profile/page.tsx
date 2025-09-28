"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { AI_EXPERTISE_TAGS, type ExpertiseTag } from "../../../constants/ai-tags";
import { useCurrentUser } from "../../../hooks/use-current-user";
import { USERNAME_HELP_TEXT, isValidUsername, sanitizeUsernameInput } from "../../../lib/username";
import type { PrivateUserProfile } from "../../../types/user";

type FormState = {
  displayName: string;
  username: string;
  bio: string;
  company: string;
  location: string;
  expertiseTags: ExpertiseTag[];
};

const EMPTY_FORM: FormState = {
  displayName: "",
  username: "",
  bio: "",
  company: "",
  location: "",
  expertiseTags: [],
};

function toFormState(user: PrivateUserProfile): FormState {
  return {
    displayName: user.displayName ?? "",
    username: user.username ?? "",
    bio: user.bio ?? "",
    company: user.company ?? "",
    location: user.location ?? "",
    expertiseTags: user.expertiseTags.filter((tag): tag is ExpertiseTag => AI_EXPERTISE_TAGS.includes(tag as ExpertiseTag)),
  };
}

export default function ProfileSettingsPage() {
  const { data: user, isLoading, error, mutate } = useCurrentUser();
  const [form, setForm] = useState<FormState>(EMPTY_FORM);
  const [clientMessage, setClientMessage] = useState<string | null>(null);
  const [serverMessage, setServerMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    if (user) {
      setForm(toFormState(user));
    }
  }, [user?.id]);

  const usernameDisabled = useMemo(() => !user?.usernameEditable, [user?.usernameEditable]);

  const handleTagToggle = (tag: ExpertiseTag) => {
    setForm((prev) => {
      const exists = prev.expertiseTags.includes(tag);
      return {
        ...prev,
        expertiseTags: exists ? prev.expertiseTags.filter((item) => item !== tag) : [...prev.expertiseTags, tag],
      };
    });
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setClientMessage(null);
    setServerMessage(null);
    setSuccessMessage(null);

    let usernameToSend: string | undefined;
    if (!usernameDisabled) {
      const sanitized = sanitizeUsernameInput(form.username);
      if (!sanitized) {
        setClientMessage("Choose a username before saving.");
        return;
      }
      if (!isValidUsername(sanitized)) {
        setClientMessage(USERNAME_HELP_TEXT);
        return;
      }
      usernameToSend = sanitized;
    }

    setIsSaving(true);
    try {
      const payload: Record<string, unknown> = {
        displayName: form.displayName.trim() || null,
        bio: form.bio.trim() || null,
        company: form.company.trim() || null,
        location: form.location.trim() || null,
        expertiseTags: form.expertiseTags,
      };
      if (usernameToSend !== undefined) {
        payload.username = usernameToSend;
      }

      const response = await fetch("/api/users/me", {
        method: "PATCH",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (response.status === 401) {
        setServerMessage("Your session expired. Please sign in again.");
        await mutate(null, { revalidate: false });
        return;
      }

      if (!response.ok) {
        const detail = await response.json().catch(() => ({}));
        if (typeof detail?.detail === "string") {
          setServerMessage(detail.detail);
        } else if (detail?.detail?.message) {
          setServerMessage(detail.detail.message);
        } else {
          setServerMessage("Unable to save profile. Try again.");
        }
        return;
      }

      const updated = (await response.json()) as PrivateUserProfile;
      await mutate(updated, { revalidate: false });
      setForm(toFormState(updated));
      setSuccessMessage("Profile updated.");
    } catch {
      setServerMessage("Unable to save profile. Try again.");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
        <p className="text-sm text-slate-400">Loading profile…</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
        <p className="text-sm text-red-300">Unable to load profile settings.</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
        <div className="w-full max-w-xl space-y-6 text-center">
          <h1 className="text-3xl font-semibold text-slate-50">Sign in to edit your profile</h1>
          <p className="text-sm text-slate-400">
            <Link href="/auth/login" className="text-slate-200 underline decoration-dotted">
              Log in
            </Link>{" "}
            to update your profile details and share them publicly.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="flex min-h-[calc(100vh-64px)] flex-col items-center bg-slate-950 px-6 py-12 text-slate-100">
      <div className="w-full max-w-2xl space-y-8">
        <div className="space-y-2">
          <Link href="/" className="text-xs font-medium uppercase tracking-wide text-slate-400 hover:text-slate-200">
            ← Back
          </Link>
          <h1 className="text-3xl font-semibold text-slate-50">Edit profile</h1>
          <p className="text-sm text-slate-400">
            Control how the community sees you. Usernames are public and can only be updated once.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6" noValidate>
          <div className="space-y-2">
            <label htmlFor="displayName" className="text-sm font-medium text-slate-200">
              Display name
            </label>
            <input
              id="displayName"
              name="displayName"
              type="text"
              value={form.displayName}
              onChange={(event) => setForm((prev) => ({ ...prev, displayName: event.target.value }))}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label htmlFor="username" className="text-sm font-medium text-slate-200">
                Username
              </label>
              <span className="text-xs text-slate-500">{USERNAME_HELP_TEXT}</span>
            </div>
            <input
              id="username"
              name="username"
              type="text"
              value={form.username}
              onChange={(event) => setForm((prev) => ({ ...prev, username: sanitizeUsernameInput(event.target.value) }))}
              disabled={usernameDisabled}
              aria-describedby="username-help"
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50 disabled:cursor-not-allowed disabled:opacity-70"
            />
            <p id="username-help" className="text-xs text-slate-400">
              {usernameDisabled
                ? "Your username is locked in. Contact support if it needs to change."
                : "Visible on your public profile."}
            </p>
          </div>

          <div className="space-y-2">
            <label htmlFor="bio" className="text-sm font-medium text-slate-200">
              Bio
            </label>
            <textarea
              id="bio"
              name="bio"
              value={form.bio}
              onChange={(event) => setForm((prev) => ({ ...prev, bio: event.target.value }))}
              rows={4}
              className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="space-y-2">
              <label htmlFor="company" className="text-sm font-medium text-slate-200">
                Company
              </label>
              <input
                id="company"
                name="company"
                type="text"
                value={form.company}
                onChange={(event) => setForm((prev) => ({ ...prev, company: event.target.value }))}
                className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="location" className="text-sm font-medium text-slate-200">
                Location
              </label>
              <input
                id="location"
                name="location"
                type="text"
                value={form.location}
                onChange={(event) => setForm((prev) => ({ ...prev, location: event.target.value }))}
                className="w-full rounded-md border border-slate-800 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 focus:border-slate-500 focus:outline-none focus:ring-2 focus:ring-slate-500/50"
              />
            </div>
          </div>

          <fieldset className="space-y-3">
            <legend className="text-sm font-medium text-slate-200">Expertise tags</legend>
            <p className="text-xs text-slate-500">Select the topics you’d like to show on your public profile.</p>
            <div className="grid gap-2 sm:grid-cols-3">
              {AI_EXPERTISE_TAGS.map((tag) => {
                const checked = form.expertiseTags.includes(tag);
                return (
                  <label key={tag} className="flex items-center gap-2 text-sm text-slate-200">
                    <input
                      type="checkbox"
                      name="expertiseTags"
                      value={tag}
                      checked={checked}
                      onChange={() => handleTagToggle(tag)}
                      className="h-4 w-4 rounded border-slate-700 bg-slate-900 text-slate-200 focus:ring-slate-500"
                    />
                    {tag}
                  </label>
                );
              })}
            </div>
          </fieldset>

          {clientMessage ? (
            <p role="alert" className="rounded-md border border-amber-500/40 bg-amber-500/10 px-3 py-2 text-sm text-amber-200">
              {clientMessage}
            </p>
          ) : null}

          {serverMessage ? (
            <p role="alert" className="rounded-md border border-red-500/40 bg-red-500/10 px-3 py-2 text-sm text-red-200">
              {serverMessage}
            </p>
          ) : null}

          {successMessage ? (
            <p className="rounded-md border border-emerald-500/40 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-200">
              {successMessage}
            </p>
          ) : null}

          <div className="flex items-center gap-3">
            <button
              type="submit"
              disabled={isSaving}
              className="inline-flex items-center justify-center rounded-md bg-slate-200 px-4 py-2 text-sm font-semibold text-slate-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-70"
            >
              {isSaving ? "Saving…" : "Save profile"}
            </button>
            <span className="text-xs text-slate-500">Changes go live immediately.</span>
          </div>
        </form>
      </div>
    </main>
  );
}
