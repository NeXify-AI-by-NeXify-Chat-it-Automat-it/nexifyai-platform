const BACKEND_URL = 'https://contract-os.preview.emergentagent.com';
const CRON_SECRET = process.env.CRON_SECRET || '';

export default async function handler(req) {
  if (req.headers.get('authorization') !== `Bearer ${CRON_SECRET}`) {
    return new Response('Unauthorized', { status: 401 });
  }

  try {
    // Trigger Oracle task processing cycle
    const token = await getAdminToken();
    if (!token) {
      return new Response(JSON.stringify({ error: 'Auth failed' }), { status: 401 });
    }

    const res = await fetch(`${BACKEND_URL}/api/admin/oracle/process-pending`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'x-vercel-cron': '1'
      },
      signal: AbortSignal.timeout(55000)
    });

    const data = await res.json();
    return new Response(JSON.stringify({
      timestamp: new Date().toISOString(),
      processed: data.processed || 0,
      status: res.status === 200 ? 'ok' : 'error'
    }), {
      status: res.status,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    console.error('[CRON:oracle] Error:', e.message);
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
