"use client";

import useSWR, { SWRResponse } from "swr";

import type { PublicUserProfile } from "../types/user";

class PublicUserError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchPublicUser(url: string): Promise<PublicUserProfile> {
  const response = await fetch(url, { credentials: "include" });
  if (response.status === 404) {
    throw new PublicUserError("Profile not found", 404);
  }
  if (!response.ok) {
    throw new PublicUserError("Unable to load profile", response.status);
  }
  return (await response.json()) as PublicUserProfile;
}

export function usePublicUser(
  username: string | null,
): SWRResponse<PublicUserProfile | null, PublicUserError> {
  return useSWR<PublicUserProfile | null, PublicUserError>(
    username ? `/api/users/${username}` : null,
    async (url) => fetchPublicUser(url),
    {
      shouldRetryOnError: false,
      revalidateOnFocus: false,
    },
  );
}
