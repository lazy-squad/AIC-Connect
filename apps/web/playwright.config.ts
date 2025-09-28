import type { PlaywrightTestConfig } from "@playwright/test";

const config: PlaywrightTestConfig = {
  testDir: "./tests",
  retries: process.env.CI ? 2 : 0,
  timeout: 60_000,
  use: {
    baseURL: process.env.WEB_BASE_URL ?? "http://localhost:3000",
    viewport: { width: 1280, height: 720 },
    trace: "on-first-retry",
  },
  webServer: {
    command: "pnpm --filter web dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
};

export default config;
