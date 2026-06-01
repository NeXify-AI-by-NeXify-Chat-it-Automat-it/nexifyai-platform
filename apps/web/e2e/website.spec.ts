import { test, expect } from '@playwright/test';

test.describe('Website Core Paths', () => {
  test('homepage loads with 200', async ({ page }) => {
    const res = await page.goto('/');
    expect(res?.status()).toBe(200);
    await expect(page.locator('body')).toBeVisible();
  });

  test('ai-agents page accessible', async ({ page }) => {
    const res = await page.goto('/ai-agents');
    // Admin-SPA returned, keine garantierten DOM-Elemente sichtbar
    expect(res?.ok()).toBeTruthy();
  });

  test('404 returns error page', async ({ page }) => {
    const res = await page.goto('/nonexistent-page-xyz');
    expect(res?.status()).toBe(404);
  });
});
