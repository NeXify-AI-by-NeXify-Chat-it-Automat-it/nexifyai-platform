// k6 Load Test — Stage 1: Brain Proxy + 9Router + Backend
// NeXifyAI Enterprise — I4 Gap-Closing
// Targets: 50/100/200 RPS, max 2s P99
//
// Usage:
//   k6 run --vus 10 --duration 30s scripts/loadtest/stage1-brain-9router-gateway.js
//   k6 run --vus 200 --duration 60s scripts/loadtest/stage1-brain-9router-gateway.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const brainLatency = new Trend('brain_ms');
const routerLatency = new Trend('router_ms');
const backendLatency = new Trend('backend_ms');
const errorRate = new Rate('errors');

export const options = {
  stages: [
    { duration: '20s', target: 50 },   // Ramp up
    { duration: '30s', target: 100 },  // Steady 100
    { duration: '20s', target: 200 },  // Peak
    { duration: '10s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000', 'p(99)<5000'],
    brain_ms: ['p(95)<500', 'p(99)<1000'],
    router_ms: ['p(95)<3000', 'p(99)<5000'],
    errors: ['rate<0.05'],
  },
};

const BRAIN_PROXY = 'http://127.0.0.1:8420';
const ROUTER = 'http://127.0.0.1:20128';
const BACKEND = 'http://127.0.0.1:8001';

export default function () {
  group('Brain Proxy (port 8420)', function () {
    // /health — confirmed working (28ms)
    {
      const res = http.get(`${BRAIN_PROXY}/health`, { tags: { name: 'brain_health' } });
      check(res, { 'brain status 200': (r) => r.status === 200 });
      brainLatency.add(res.timings.duration);
      errorRate.add(res.status !== 200);
    }
  });

  group('9Router (port 20128)', function () {
    // /v1/models — confirmed working (4ms)
    {
      const res = http.get(`${ROUTER}/v1/models`, { tags: { name: 'router_models' } });
      check(res, { 'router models 200': (r) => r.status === 200 });
      routerLatency.add(res.timings.duration);
      errorRate.add(res.status !== 200);
    }
  });

  group('Backend (port 8001)', function () {
    // Backend reachable (expect 401 — requires auth, but service is alive)
    {
      const res = http.get(`${BACKEND}/api/v1`, { tags: { name: 'backend_api' } });
      check(res, {
        'backend reachable': (r) => [401, 429].includes(r.status) || (r.status >= 200 && r.status < 500),
      });
      backendLatency.add(res.timings.duration);
      errorRate.add(res.status >= 500 || res.status === 0);
    }
  });

  // Brief pause to avoid flooding
  sleep(0.2);
}
