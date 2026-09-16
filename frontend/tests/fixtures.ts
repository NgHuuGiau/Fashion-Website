import { test as base, expect } from '@playwright/test';

function testClientIp(testId: string): string {
  let hash = 2166136261;
  for (const char of testId) {
    hash = Math.imul(hash ^ char.charCodeAt(0), 16777619);
  }

  const address = hash >>> 0;
  const subnet = (address >>> 8) & 0xff;
  const host = (address % 254) + 1;
  return `198.18.${subnet}.${host}`;
}

export const test = base.extend({
  page: async ({ page }, use, testInfo) => {
    await page.setExtraHTTPHeaders({
      'X-Forwarded-For': testClientIp(`${testInfo.project.name}:${testInfo.testId}`),
    });
    await use(page);
  },
});

export { expect };
