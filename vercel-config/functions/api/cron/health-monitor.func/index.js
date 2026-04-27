const BACKEND_URL = 'https://contract-os.preview.emergentagent.com';
const CRON_SECRET = process.env.CRON_SECRET || '';

export default async function handler(req) {
  if (req.headers.get('authorization') !== `Bearer ${CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    const res = await fetch(`${BACKEND_URL}/api/health`, {
      headers: { 'x-vercel-cron': '1' },
      signal: AbortSignal.timeout(10000)
    });
    const data = await res.json();
    const unhealthy = Object.entries(data.services || {})
      .filter(([_, v]) => v.status !== 'ok')
      .map(([k]) => k);

    const result = {
      timestamp: new Date().toISOString(),
      status: data.status,
      services_total: Object.keys(data.services || {}).length,
      unhealthy: unhealthy,
      version: data.version
    };

    if (unhealthy.length > 0) {
      console.error('[CRON:health] Unhealthy services:', unhealthy.join(', '));
    }

    return new Response(JSON.stringify(result), {
      status: unhealthy.length > 0 ? 503 : 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    console.error('[CRON:health] Backend unreachable:', e.message);
    return new Response(JSON.stringify({ error: e.message, timestamp: new Date().toISOString() }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

export const config = { runtime: 'edge' };
