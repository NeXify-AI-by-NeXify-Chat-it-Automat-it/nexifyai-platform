import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const brainErr = new Rate('brain_errors');
const brainLatency = new Trend('brain_latency');

export const options = {
  stages: [
    { duration: '30s', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 200 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    brain_errors: ['rate<0.01'],
    brain_latency: ['p(95)<200', 'p(99)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1:8420';

export default function () {
  // Health check
  const healthRes = http.get(`${BASE_URL}/health`);
  check(healthRes, { 'health 200': (r) => r.status === 200 });
  brainErr.add(healthRes.status !== 200);
  brainLatency.add(healthRes.timings.duration);

  // Search query
  const searchRes = http.post(`${BASE_URL}/query`, JSON.stringify({
    query: 'autopilot pipeline system state',
    limit: 5
  }), { headers: { 'Content-Type': 'application/json' } });
  check(searchRes, { 'search 200': (r) => r.status === 200 });
  brainErr.add(searchRes.status !== 200);
  brainLatency.add(searchRes.timings.duration);

  // Stats
  const statsRes = http.get(`${BASE_URL}/stats`);
  check(statsRes, { 'stats 200': (r) => r.status === 200 });

  sleep(1);
}
