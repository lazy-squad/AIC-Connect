export const USERNAME_PATTERN = /^[a-z0-9](?:[a-z0-9-]{1,30})[a-z0-9]$/;
export const USERNAME_HELP_TEXT = "3-32 lowercase characters. Letters, numbers, and hyphens only.";

export function sanitizeUsernameInput(value: string): string {
  const lowered = value.toLowerCase();
  const replaced = lowered.replace(/[^a-z0-9-]/g, "-");
  const collapsed = replaced.replace(/-+/g, "-");
  const trimmed = collapsed.replace(/^-+|-+$/g, "");
  return trimmed.slice(0, 32);
}

export function isValidUsername(value: string): boolean {
  return USERNAME_PATTERN.test(value);
}
