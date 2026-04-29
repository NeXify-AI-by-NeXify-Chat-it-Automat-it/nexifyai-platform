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

    // Trigger competitor monitoring via Trigger.dev task
    const res = await fetch(`${BACKEND_URL}/api/admin/trigger/run`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'x-vercel-cron': '1'
      },
      body: JSON.stringify({
        task_id: 'competitor-monitor',
        payload: {
          competitors: [
            { name: 'Default', url: '', keywords: ['KI Agentur', 'AI Automation', 'B2B AI'] }
          ],
          lookbackDays: 1
        }
      }),
      signal: AbortSignal.timeout(55000)
    });

    const data = await res.json();
    return new Response(JSON.stringify({
      timestamp: new Date().toISOString(),
      task: 'competitor-monitor',
      success: data.success || false,
      run_id: data.run_id || null,
      fallback: data.fallback || false
    }), {
      status: data.success ? 200 : 500,
      headers: { 'Content-Type': 'application/json' }
    });
  } catch (e) {
    console.error('[CRON:competitor] Error:', e.message);
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
