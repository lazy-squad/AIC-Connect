export type PrivateUserProfile = {
  id: string;
  email: string;
  username: string;
  displayName?: string | null;
  avatarUrl?: string | null;
  bio?: string | null;
  company?: string | null;
  location?: string | null;
  expertiseTags: string[];
  createdAt: string;
  updatedAt?: string | null;
  usernameEditable: boolean;
  githubUsername?: string | null;
};

export type PublicUserProfile = Omit<PrivateUserProfile, "email" | "usernameEditable">;
