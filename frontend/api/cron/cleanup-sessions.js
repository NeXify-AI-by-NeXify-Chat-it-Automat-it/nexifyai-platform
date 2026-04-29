const BACKEND_URL = 'https://contract-os.preview.emergentagent.com';
const CRON_SECRET = process.env.CRON_SECRET || '';

export default async function handler(req) {
  if (req.headers.get('authorization') !== `Bearer ${CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    const token = await getAdminToken();
    if (!token) {
      return new Response(JSON.stringify({ error: 'Auth failed' }), { status: 401 });
    }

    // Cleanup stale chat sessions (older than 24h)
    const res = await fetch(`${BACKEND_URL}/api/admin/system/cleanup-sessions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'x-vercel-cron': '1'
      },
      body: JSON.stringify({ max_age_hours: 24 }),
      signal: AbortSignal.timeout(30000)
    });

    let data = {};
    try { data = await res.json(); } catch {}

    return new Response(JSON.stringify({
      timestamp: new Date().toISOString(),
      cleaned: data.cleaned || 0,
      status: res.status <= 299 ? 'ok' : 'skipped'
    }), {
      status: 200,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    console.error('[CRON:cleanup] Error:', e.message);
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

async function getAdminToken() {
  try {
    const res = await fetch(`${BACKEND_URL}/api/admin/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        username: process.env.ADMIN_EMAIL || '',
        password: process.env.ADMIN_PASSWORD || ''
      }),
      signal: AbortSignal.timeout(10000)
    });
    if (res.ok) {
      const data = await res.json();
      return data.access_token;
    }
  } catch {}
  return null;
}

export const config = { runtime: 'edge' };
