"use client";

import useSWR, { SWRResponse } from "swr";

import type { PrivateUserProfile } from "../types/user";

async function fetchCurrentUser(url: string): Promise<PrivateUserProfile | null> {
  const response = await fetch(url, { credentials: "include" });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    const error = new Error("Failed to load current user");
    (error as Error & { status?: number }).status = response.status;
    throw error;
  }
  return (await response.json()) as PrivateUserProfile;
}

export function useCurrentUser(): SWRResponse<PrivateUserProfile | null, Error> {
  return useSWR<PrivateUserProfile | null, Error>("/api/users/me", fetchCurrentUser, {
    revalidateOnFocus: false,
  });
}
