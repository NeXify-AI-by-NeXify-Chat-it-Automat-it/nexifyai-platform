import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// ====== METRICS ======
const brainHealth = new Trend('brain_health');
const brainSearch = new Trend('brain_search');
const routerModels = new Trend('router_models');
const routerChat = new Trend('router_chat');
const gatewayHealth = new Trend('gateway_health');
const errRate = new Rate('errors');

// ====== OPTIONS ======
export const options = {
  vus: 1,
  iterations: 1,
  thresholds: {
    brain_health: ['p(99)<500', 'avg<100'],
    brain_search: ['p(99)<2000', 'avg<1000'],
    router_models: ['p(99)<500', 'avg<100'],
    router_chat: ['p(99)<15000', 'avg<5000'],
    gateway_health: ['p(99)<200', 'avg<50'],
    errors: ['rate<0.20'],
    http_req_failed: ['rate<0.20'],
  },
};

const BASE = 'http://127.0.0.1';
const HDR = { 'Content-Type': 'application/json' };

export default function () {
  // 1. Brain Health
  let r = http.get(`${BASE}:8420/health`);
  brainHealth.add(r.timings.duration);
  check(r, { 'brain health 200': (r) => r.status === 200 });

  // 2. Brain Search
  r = http.post(`${BASE}:8420/query`,
    JSON.stringify({ query: 'autopilot brain governance', limit: 3 }), { headers: HDR });
  brainSearch.add(r.timings.duration);
  check(r, { 'brain search 200': (r) => r.status === 200 });
  if (r.status !== 200) errRate.add(1);

  // 3. Router Models
  r = http.get(`${BASE}:20128/v1/models`);
  routerModels.add(r.timings.duration);
  check(r, { 'router models 200': (r) => r.status === 200 });
  if (r.status !== 200) errRate.add(1);

  // 4. Router Chat
  r = http.post(`${BASE}:20128/v1/chat/completions`,
    JSON.stringify({
      model: 'ds/deepseek-v4-flash',
      messages: [{ role: 'user', content: 'Hi' }],
      max_tokens: 5, temperature: 0.1,
    }),
    { headers: HDR, timeout: 15000 }
  );
  routerChat.add(r.timings.duration);
  check(r, { 'router chat 200': (r) => r.status === 200 });
  if (r.status !== 200) errRate.add(1);

  // 5. Gateway Health
  r = http.get(`${BASE}:8001/health`);
  gatewayHealth.add(r.timings.duration);
  check(r, { 'gateway health 200': (r) => r.status === 200 });
  if (r.status !== 200) errRate.add(1);
}

// ====== FULL LOAD TEST ======
// Run: k6 run --env full=1 tests/loadtest.js
// Or create a second file for scenarios
