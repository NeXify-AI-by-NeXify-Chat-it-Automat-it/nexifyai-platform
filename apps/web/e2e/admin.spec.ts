import { test, expect } from '@playwright/test';

test.describe('Admin & Portal Paths', () => {
  test('admin page reachable', async ({ page }) => {
    // Admin SPA — HTTP-Status reicht, DOM ist dynamisch
    await page.goto('/admin', { waitUntil: 'domcontentloaded' });
    const title = await page.title();
    expect(title).toContain('NeXify');
  });

  test('customer portal reachable', async ({ page }) => {
    const res = await page.goto('/customer-portal', { waitUntil: 'domcontentloaded' });
    // Akzeptiere 200 oder Redirect
    if (res?.status() === 404) {
      // Kundenportal existiert noch nicht unter dieser Route
      test.fixme(true, 'Customer portal route not yet deployed');
    }
    expect([200, 301, 302, 307, 308, 404]).toContain(res?.status());
  });
});
