// NeXifyAI Load Test — 9Router
// k6 v2.0.0 — Endpunkte: /api/health, /v1/models
// Targets: 50 RPS, max 2s P99 (LLM = langsam)

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const routerBase = 'http://localhost:20128';

const healthFailRate = new Rate('router_health_fails');
const modelsDuration = new Trend('router_models_duration');
const chatDuration = new Trend('router_chat_duration');

export const options = {
  scenarios: {
    router_health: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 2,
      maxVUs: 10,
      exec: 'testHealth',
    },
    router_models: {
      executor: 'constant-arrival-rate',
      rate: 20,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 2,
      maxVUs: 5,
      exec: 'testModels',
    },
    router_chat: {
      executor: 'per-vu-iterations',
      vus: 2,
      iterations: 10,
      maxDuration: '120s',
      exec: 'testChat',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<100', 'p(99)<500'],
    router_health_fails: ['rate<0.01'],
    router_models_duration: ['p(95)<500', 'p(99)<1000'],
    router_chat_duration: ['p(95)<5000', 'p(99)<10000'],
  },
};

function stripStreamSuffix(body) {
  const idx = body.lastIndexOf('data: [DONE]');
  return idx >= 0 ? body.substring(0, idx).trim() : body.trim();
}

export function testHealth() {
  const res = http.get(`${routerBase}/api/health`);
  const ok = check(res, {
    'health 200': (r) => r.status === 200,
    'health body ok': (r) => r.body === '{"ok":true}',
  });
  healthFailRate.add(!ok);
}

export function testModels() {
  const res = http.get(`${routerBase}/v1/models`);
  modelsDuration.add(res.timings.duration);
  check(res, {
    'models 200': (r) => r.status === 200,
    'models has data': (r) => r.json('data') !== undefined,
  });
}

export function testChat() {
  const payload = JSON.stringify({
    model: 'ds/deepseek-v4-flash',
    messages: [
      { role: 'user', content: 'Say "hello" in one word' },
    ],
    max_tokens: 10,
  });
  const res = http.post(`${routerBase}/v1/chat/completions`, payload, {
    headers: { 'Content-Type': 'application/json' },
    timeout: '30s',
  });
  chatDuration.add(res.timings.duration);
  check(res, {
    'chat 200': (r) => r.status === 200,
    'chat has choices': (r) => {
      try { return JSON.parse(stripStreamSuffix(r.body)).choices !== undefined; }
      catch (e) { return false; }
    },
  });
}
