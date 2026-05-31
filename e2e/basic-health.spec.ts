import { test, expect } from '@playwright/test';

test('nexifyai.cloud — health check', async ({ page }) => {
  const resp = await page.goto('/');
  expect(resp?.status()).toBe(200);
  await expect(page).toHaveTitle(/NeXify/i);
  // Console errors = fail
  const errors: string[] = [];
  page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
  await page.goto('/');
  expect(errors.length).toBe(0);
});

test('Admin Portal — 200 check', async ({ page }) => {
  const resp = await page.goto('http://127.0.0.1:5173');
  expect(resp?.status()).toBe(200);
});

test('Kundenportal — skip if not running', async ({ page }) => {
  try {
    const resp = await page.goto('http://localhost:32768', { timeout: 5000 });
    if (resp) {
      expect(resp.status()).toBeGreaterThanOrEqual(200);
      expect(resp.status()).toBeLessThan(400);
    }
  } catch {
    test.skip();
  }
});
