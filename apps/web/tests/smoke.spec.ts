import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

const normalizedApiBase = apiBaseUrl.replace(/\/$/, "");

const selectors = {
  signupPasswordHint: "text=Use at least 8 characters",
};

test("home page renders auth options", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("heading", { name: "Choose how you’d like to sign in." })).toBeVisible();
  await expect(page.getByRole("link", { name: "Create an account" })).toHaveAttribute("href", "/auth/signup");
  await expect(page.getByRole("link", { name: "Sign in with email" })).toHaveAttribute("href", "/auth/login");
  await expect(page.getByRole("link", { name: "Continue with GitHub" })).toHaveAttribute(
    "href",
    `${normalizedApiBase}/auth/login/github`,
  );
});

test("signup page enforces password hints client-side", async ({ page }) => {
  await page.goto("/auth/signup");

  await page.getByLabel("Work email").fill("test@example.com");
  await page.getByLabel("Password").fill("short");
  await page.getByRole("button", { name: "Create account" }).click();

  await expect(page.locator('p[role="alert"]')).toContainText("Use at least 8 characters");
});

test("login page provides navigation to GitHub OAuth", async ({ page }) => {
  await page.goto("/auth/login");
  const githubLink = page.getByRole("link", { name: "Continue with GitHub" });
  await expect(githubLink).toHaveAttribute("href", `${normalizedApiBase}/auth/login/github`);
});
