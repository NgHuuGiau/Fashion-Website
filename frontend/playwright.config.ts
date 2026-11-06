import { defineConfig, devices } from "@playwright/test";

const port = process.env.PORT || "8000";
const baseURL = process.env.BASE_URL || `http://localhost:${port}`;

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers:
    process.env.CI || process.env.DJANGO_SETTINGS_MODULE === "core.test_settings_sqlite"
      ? 1
      : undefined,
  timeout: 60000,
  expect: { timeout: 10000 },
  reporter: "html",
  globalSetup: require.resolve("./global-setup"),
  use: {
    baseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    actionTimeout: 15000,
    navigationTimeout: 30000,
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "webkit", use: { ...devices["Desktop Safari"] } },
    { name: "Mobile Chrome", use: { ...devices["Pixel 5"] } },
    { name: "Mobile Safari", use: { ...devices["iPhone 12"] } }
  ],
  webServer: undefined,
});