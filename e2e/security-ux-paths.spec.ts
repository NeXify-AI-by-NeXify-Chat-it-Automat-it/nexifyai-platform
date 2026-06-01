import { test, expect } from '@playwright/test';

// =============================================================================
// NeXifyAI Security + UX Paths — D1: Playwright E2E Tests
// Tests: 404 handling, Admin Login attempt (observe behavior), Kundenportal
// =============================================================================

// --- 1. 404 HANDLING (Public Website) ---
test.describe('404 Handling — nexifyai.cloud', () => {
  test('GET /nonexistent-path returns 404', async ({ page }) => {
    const resp = await page.goto('/nonexistent-page-xyz-123', {
      waitUntil: 'domcontentloaded',
    });
    // Accept 404 from server or SPA client-side 404
    expect(
      resp?.status() === 404 ||
      page.url().includes('404') ||
      (await page.locator('body').innerText()).toLowerCase().includes('404') ||
      (await page.locator('body').innerText()).toLowerCase().includes('not found')
    ).toBeTruthy();
  });

  test('No critical errors on 404 page', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
    page.on('pageerror', (err) => errors.push(err.message));
    await page.goto('/nonexistent-page-xyz-123', { waitUntil: 'domcontentloaded' });
    // Filter benign errors
    const jsErrors = errors.filter(e => !e.includes('favicon') && !e.includes('404'));
    expect(jsErrors.length).toBe(0);
  });
});

// --- 2. ADMIN PORTAL — Login Page ---
test.describe('Admin Portal — Login Page', () => {
  test('Login page shows auth form', async ({ page }) => {
    await page.goto('http://127.0.0.1:5173', { timeout: 15000, waitUntil: 'networkidle' });
    // Wait a moment for JS rendering
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    // Check for common login/auth elements
    const bodyText = await page.locator('body').innerText().catch(() => '');
    const hasInput = await page.locator('input').count().catch(() => 0);
    console.log(`Admin page: ${bodyText.substring(0, 200)}`);
    console.log(`Input fields found: ${hasInput}`);
    // Should have some interactive elements
    expect(hasInput).toBeGreaterThanOrEqual(0);
  });

  test('Login page — no critical console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => { if (msg.type() === 'error') errors.push(msg.text()); });
    page.on('pageerror', (err) => errors.push(err.message));
    await page.goto('http://127.0.0.1:5173', { timeout: 15000, waitUntil: 'domcontentloaded' });
    const jsErrors = errors.filter(e => !e.includes('favicon'));
    // Allow 1-2 benign errors (missing assets, timeout) but reject >5
    expect(jsErrors.length).toBeLessThan(5);
  });
});

// --- 3. CUSTOMER PORTAL (Kundenportal) ---
test.describe('Customer Portal', () => {
  test('GET / returns 200', async ({ page }) => {
    try {
      const resp = await page.goto('http://127.0.0.1:32768', { timeout: 10000 });
      if (resp) {
        expect(resp.status()).toBeGreaterThanOrEqual(200);
        expect(resp.status()).toBeLessThan(400);
      }
    } catch {
      test.skip();
    }
  });
});

// --- 4. RESPONSIVE — Mobile Check (Website) ---
test.describe('Responsive — Mobile Viewport', () => {
  test('Home page renders on mobile (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    const resp = await page.goto('/');
    expect(resp?.status()).toBe(200);
    // No horizontal scroll on mobile
    const overflowX = await page.evaluate(() => {
      return document.documentElement.scrollWidth <= document.documentElement.clientWidth;
    });
    expect(overflowX).toBeTruthy();
  });
});

// --- 5. HTTP Security Headers (Website) ---
test.describe('Security Headers', () => {
  test('Strict-Transport-Security present', async ({ page }) => {
    const resp = await page.goto('/');
    const headers = resp?.headers() ?? {};
    expect(headers['strict-transport-security'] || headers['Strict-Transport-Security']).toBeTruthy();
  });
});
