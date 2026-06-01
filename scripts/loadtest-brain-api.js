// NeXifyAI Load Test — Brain API
// k6 v2.0.0 — Endpunkte: /health, /v1/search (GET), /v1/store (POST)
// Targets: 50/100/200 RPS, P99 < 500ms

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const brainBase = 'http://127.0.0.1:8420';

const healthFailRate = new Rate('brain_health_fails');
const searchDuration = new Trend('brain_search_duration');
const storeDuration = new Trend('brain_store_duration');

export const options = {
  scenarios: {
    brain_health: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '30s',
      preAllocatedVUs: 5,
      maxVUs: 20,
      exec: 'testHealth',
    },
    brain_search: {
      executor: 'ramping-arrival-rate',
      startRate: 50,
      timeUnit: '1s',
      stages: [
        { duration: '20s', target: 100 },
        { duration: '20s', target: 200 },
        { duration: '10s', target: 0 },
      ],
      preAllocatedVUs: 10,
      maxVUs: 30,
      exec: 'testSearch',
    },
    brain_store: {
      executor: 'per-vu-iterations',
      vus: 5,
      iterations: 50,
      maxDuration: '60s',
      exec: 'testStore',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<300', 'p(99)<500'],
    brain_health_fails: ['rate<0.01'],
    brain_search_duration: ['p(95)<500', 'p(99)<1000'],
    brain_store_duration: ['p(95)<1000', 'p(99)<2000'],
  },
};

export function testHealth() {
  const res = http.get(`${brainBase}/health`);
  const ok = check(res, {
    'health status 200': (r) => r.status === 200,
    'health body ok': (r) => r.json('status') === 'ok',
  });
  healthFailRate.add(!ok);
}

export function testSearch() {
  const payload = JSON.stringify({
    query: 'autopilot pipeline',
    limit: 5,
  });
  const res = http.post(`${brainBase}/query`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  searchDuration.add(res.timings.duration);
  check(res, {
    'query status 200': (r) => r.status === 200,
    'query has results': (r) => r.json('results') !== undefined,
  });
}

export function testStore() {
  const payload = JSON.stringify({
    content: `Load test entry — ${__VU}_${__ITER}`,
    category: 'loadtest',
    source: 'k6-loadtest',
  });
  const res = http.post(`${brainBase}/store`, payload, {
    headers: { 'Content-Type': 'application/json' },
  });
  storeDuration.add(res.timings.duration);
  check(res, {
    'store status 200': (r) => r.status === 200,
  });
}
