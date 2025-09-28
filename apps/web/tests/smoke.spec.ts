import { expect, test } from "@playwright/test";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

test("home page renders sign-in options", async ({ page }) => {
  await page.goto("/");

  const githubLink = page.getByRole("link", { name: "Sign in with GitHub" });
  await expect(githubLink).toBeVisible();
  await expect(githubLink).toHaveAttribute("href", `${apiBaseUrl.replace(/\/$/, "")}/auth/login/github`);

  const emailField = page.getByLabel("Work email");
  await expect(emailField).toBeVisible();

  const magicLinkButton = page.getByRole("button", { name: "Email me a link" });
  await expect(magicLinkButton).toBeVisible();
});
