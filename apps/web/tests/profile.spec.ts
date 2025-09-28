import { expect, test } from "@playwright/test";

function uniqueSuffix() {
  return Date.now().toString(36);
}

test("authenticated user can update profile and view public page", async ({ page }) => {
  const suffix = uniqueSuffix();
  const email = `profile-${suffix}@example.com`;
  const password = "Sup3rSecure!";
  const displayName = "Builder One";
  const username = `builder-${suffix}`.slice(0, 30);

  await page.goto("/auth/signup");
  await page.getByLabel("Work email").fill(email);
  await page.getByLabel("Display name (optional)").fill(displayName);
  await page.getByLabel("Password").fill(password);
  await page.getByRole("button", { name: "Create account" }).click();
  await expect(page).toHaveURL(/\/welcome$/);

  await page.goto("/settings/profile");
  await expect(page.getByRole("heading", { name: "Edit profile" })).toBeVisible();

  // Client-side validation prevents short usernames.
  await page.getByLabel("Username").fill("ab");
  await page.getByRole("button", { name: "Save profile" }).click();
  await expect(
    page.locator('p[role="alert"]').filter({ hasText: "3-32 lowercase characters" }).first(),
  ).toBeVisible();

  // Update profile with valid data.
  await page.getByLabel("Display name").fill(displayName);
  await page.getByLabel("Username").fill(username);
  await page.getByLabel("Bio").fill("Building the AI Collective.");
  await page.getByLabel("Company").fill("AIC Ventures");
  await page.getByLabel("Location").fill("Remote");
  await page.getByLabel("LLMs").check();
  await page.getByLabel("Agents").check();
  await page.getByRole("button", { name: "Save profile" }).click();

  await expect(page.getByText("Profile updated.")).toBeVisible();
  await expect(page.getByLabel("Username")).toBeDisabled();

  await page.goto(`/users/${username}`);
  await expect(page.getByRole("heading", { name: displayName })).toBeVisible();
  await expect(page.getByText(`@${username}`)).toBeVisible();
  await expect(page.getByText("Building the AI Collective.")).toBeVisible();
  await expect(page.getByText("AIC Ventures")).toBeVisible();
  await expect(page.getByText("Remote")).toBeVisible();
  await expect(page.getByText("LLMs")).toBeVisible();
  await expect(page.getByText("Agents")).toBeVisible();

  await page.reload();
  await expect(page.getByText(`@${username}`)).toBeVisible();

  await page.goto("/settings/profile");
  await expect(page.getByLabel("Display name")).toHaveValue(displayName);
  await expect(page.getByLabel("Company")).toHaveValue("AIC Ventures");
  await expect(page.getByLabel("LLMs")).toBeChecked();
});
