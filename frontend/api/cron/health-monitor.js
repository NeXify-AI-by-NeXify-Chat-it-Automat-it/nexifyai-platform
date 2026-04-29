const BACKEND_URL = 'https://contract-os.preview.emergentagent.com';
const CRON_SECRET = process.env.CRON_SECRET || '';

export default async function handler(req) {
  if (req.headers.get('authorization') !== `Bearer ${CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  const timestamp = new Date().toISOString();
  let result = { timestamp, status: 'unknown', services_total: 0, unhealthy: [] };

  try {
    const res = await fetch(`${BACKEND_URL}/api/health`, {
      headers: { 'x-vercel-cron': '1' },
      signal: AbortSignal.timeout(10000),
    });
    const data = await res.json();
    const unhealthy = Object.entries(data.services || {})
      .filter(([, v]) => v.status !== 'ok')
      .map(([k]) => k);

    result = {
      timestamp,
      status: data.status,
      services_total: Object.keys(data.services || {}).length,
      unhealthy,
      version: data.version,
    };

    if (unhealthy.length > 0) {
      console.error('[CRON:health] Unhealthy services:', unhealthy.join(', '));
    }
  } catch (e) {
    console.error('[CRON:health] Backend unreachable:', e.message);
    result = { timestamp, status: 'unreachable', services_total: 0, unhealthy: ['backend'], error: e.message };
  }

  // Always notify backend so it can reconcile recoveries / trigger alerts.
  try {
    await fetch(`${BACKEND_URL}/api/internal/alerts/health`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${CRON_SECRET}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(result),
      signal: AbortSignal.timeout(10000),
    });
  } catch (e) {
    console.error('[CRON:health] Alert dispatch failed:', e.message);
  }

  return new Response(JSON.stringify(result), {
    status: result.unhealthy.length > 0 ? 503 : 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

export const config = { runtime: 'edge' };
