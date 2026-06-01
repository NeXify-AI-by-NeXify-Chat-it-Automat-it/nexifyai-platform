import { test, expect } from '@playwright/test';

// =============================================================================
// NeXifyAI Core Paths — E2E Health Check
// Tests: Public Website, Admin Portal, 9Router Dashboard
// =============================================================================

// --- 1. PUBLIC WEBSITE (nexifyai.cloud) ---
test.describe('Public Website — nexifyai.cloud', () => {
  test('GET / returns 200 and NeXify title', async ({ page }) => {
    const resp = await page.goto('/');
    expect(resp?.status()).toBe(200);
    await expect(page).toHaveTitle(/NeXify/i);
  });

  test('No critical console errors', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    page.on('pageerror', (err) => errors.push(err.message));
    await page.goto('/');
    // Allow network 404s (fonts, analytics), reject JS errors
    const jsErrors = errors.filter(e => !e.includes('404') && !e.includes('favicon'));
    expect(jsErrors.length).toBe(0);
  });

  test('Meta tags present', async ({ page }) => {
    await page.goto('/');
    const desc = await page.$('meta[name="description"]');
    expect(desc).toBeTruthy();
    const ogTitle = await page.$('meta[property="og:title"]');
    expect(ogTitle).toBeTruthy();
  });
});

// --- 2. ADMIN PORTAL (127.0.0.1:5173) ---
test.describe('Admin Portal — localhost:5173', () => {
  test('GET / returns 200', async ({ page }) => {
    const resp = await page.goto('http://127.0.0.1:5173', { timeout: 15000 });
    expect(resp?.status()).toBe(200);
  });

  test('No critical errors in console', async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    await page.goto('http://127.0.0.1:5173', { timeout: 15000 });
    const jsErrors = errors.filter(e => !e.includes('favicon'));
    expect(jsErrors.length).toBe(0);
  });
});

// --- 3. 9Router Dashboard ---
test.describe('9Router Dashboard', () => {
  test('GET /dashboard redirects or loads', async ({ page }) => {
    const resp = await page.goto('http://localhost:20128/dashboard', { 
      timeout: 10000,
      waitUntil: 'domcontentloaded'
    });
    // 9Router may redirect to /dashboard or return 200
    expect(resp?.status() ?? 0).toBeGreaterThanOrEqual(200);
    expect(resp?.status() ?? 999).toBeLessThan(400);
  });
});

// --- 4. BRAIN API HEALTH ---
test.describe('Brain API Health', () => {
  test('GET /health returns 200', async ({ page }) => {
    const resp = await page.goto('http://127.0.0.1:8420/health', { timeout: 5000 });
    expect(resp?.status()).toBe(200);
  });

  test('GET /categories returns categories', async ({ page }) => {
    const resp = await page.goto('http://127.0.0.1:8420/categories', { timeout: 5000 });
    expect(resp?.status()).toBe(200);
  });
});
