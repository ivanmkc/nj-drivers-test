import { defineConfig } from '@playwright/test';

// Runs against the production build served by `vite preview`, so the tests
// exercise the same base path, service worker, and data layout as Pages.
// Locally, point PW_CHROMIUM_PATH at a Chromium binary to skip the download.
const executablePath = process.env.PW_CHROMIUM_PATH;

export default defineConfig({
  testDir: './tests',
  timeout: 60_000,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: 'http://localhost:4173/nj-drivers-test/',
    trace: 'retain-on-failure',
    ...(executablePath ? { launchOptions: { executablePath } } : {}),
  },
  projects: [{ name: 'chromium', use: { browserName: 'chromium' } }],
  webServer: {
    command: 'npm run preview -- --port 4173 --strictPort',
    url: 'http://localhost:4173/nj-drivers-test/',
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
