import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const routerErr = new Rate('9router_errors');
const routerLatency = new Trend('9router_latency');

export const options = {
  stages: [
    { duration: '30s', target: 20 },
    { duration: '30s', target: 50 },
    { duration: '30s', target: 100 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    '9router_errors': ['rate<0.05'],
    '9router_latency': ['p(95)<5000', 'p(99)<10000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:20128/v1';

export default function () {
  const payload = JSON.stringify({
    model: 'ds/deepseek-v4-flash',
    messages: [{ role: 'user', content: 'Sag "ok" in einem Wort.' }],
    max_tokens: 10,
  });

  const res = http.post(`${BASE_URL}/chat/completions`, payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: '10s',
  });

  check(res, { 'llm 200': (r) => r.status === 200 });
  routerErr.add(res.status !== 200);
  routerLatency.add(res.timings.duration);

  sleep(2);
}
