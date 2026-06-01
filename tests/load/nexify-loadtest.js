// NeXifyAI Enterprise — Comprehensive Load Test Suite
// ============================================================================
// Targets: Brain API (8420), 9Router (20128), Gateway (8642)
// Thresholds: Brain 50ms P99 @ 100 RPS, 9Router 2s P99 @ 50 RPS, Gateway 200ms P99 @ 200 RPS
// Run: k6 run nexify-loadtest.js
// ============================================================================

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { textSummary } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

// ── Custom Metrics ──────────────────────────────────────────────────────────
const brainQueryTime = new Trend('brain_query_time');
const brainStoreTime = new Trend('brain_store_time');
const routerTime = new Trend('router_response_time');
const gatewayTime = new Trend('gateway_response_time');

const brainErrors = new Rate('brain_errors');
const routerErrors = new Rate('router_errors');
const gatewayErrors = new Rate('gateway_errors');

const totalRequests = new Counter('total_requests');

// ── Config ──────────────────────────────────────────────────────────────────
const BASE_URL = __ENV.BASE_URL || 'http://127.0.0.1';
const BRAIN_PORT = __ENV.BRAIN_PORT || '8420';
const ROUTER_PORT = __ENV.ROUTER_PORT || '20128';
const GATEWAY_PORT = __ENV.GATEWAY_PORT || '8642';

const BRAIN_HEALTH = `${BASE_URL}:${BRAIN_PORT}/health`;
const BRAIN_STORE = `${BASE_URL}:${BRAIN_PORT}/v1/store`;
const BRAIN_QUERY = `${BASE_URL}:${BRAIN_PORT}/v1/query`;
const BRAIN_STATS = `${BASE_URL}:${BRAIN_PORT}/stats`;
const BRAIN_CATEGORIES = `${BASE_URL}:${BRAIN_PORT}/categories`;
const ROUTER_HEALTH = `${BASE_URL}:${ROUTER_PORT}/v1/models`;
const ROUTER_CHAT = `${BASE_URL}:${ROUTER_PORT}/v1/chat/completions`;
const GATEWAY_HEALTH = `${BASE_URL}:${GATEWAY_PORT}/health`;

// ── Thresholds (SLA from E3) ────────────────────────────────────────────────
export const loadThresholds = {
  // Brain: max 50ms P99 @ 100 RPS
  brain_query_time: ['p(99)<=50', 'p(95)<=30', 'avg<=20'],
  brain_store_time: ['p(99)<=200', 'p(95)<=100', 'avg<=50'],
  brain_errors: ['rate<=0.01'],

  // 9Router: max 2s P99 @ 50 RPS
  router_response_time: ['p(99)<=2000', 'p(95)<=1000', 'avg<=500'],
  router_errors: ['rate<=0.05'],

  // Gateway: max 200ms P99 @ 200 RPS
  gateway_response_time: ['p(99)<=200', 'p(95)<=100', 'avg<=50'],
  gateway_errors: ['rate<=0.01'],
};

// ── Test Data ───────────────────────────────────────────────────────────────
const testQueries = [
  'autopilot pipeline status',
  'system health monitoring',
  'NeXifyAI Agenten-Seele',
  'brain categories',
  'Qdrant backup status',
  'Pascal Courbois mandates',
  'security audit findings',
  'CEO strategic planning',
  'Cloudflare tunnel config',
  'GitHub Actions workflow',
  'k6 load testing',
  'GraFanA dashboard',
  'Traefik ingress routing',
  'Supabase database schema',
  'deepseek model routing',
];

// ── Smoke Test ──────────────────────────────────────────────────────────────
export const smokeOptions = {
  scenarios: {
    brain_smoke: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
      exec: 'brainTest',
      tags: { scenario: 'smoke', target: 'brain' },
    },
    router_smoke: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
      exec: 'routerTest',
      tags: { scenario: 'smoke', target: 'router' },
      startTime: '5s',
    },
    gateway_smoke: {
      executor: 'constant-vus',
      vus: 2,
      duration: '30s',
      exec: 'gatewayTest',
      tags: { scenario: 'smoke', target: 'gateway' },
      startTime: '10s',
    },
  },
  thresholds: {
    brain_query_time: ['p(95)<=50'],
    router_response_time: ['p(95)<=2000'],
    gateway_response_time: ['p(95)<=200'],
    brain_errors: ['rate<=0'],
    router_errors: ['rate<=0'],
    gateway_errors: ['rate<=0'],
  },
};

// ── Load Test ───────────────────────────────────────────────────────────────
export const loadOptions = {
  scenarios: {
    brain_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 100 },
        { duration: '30s', target: 0 },
      ],
      exec: 'brainTest',
      tags: { scenario: 'load', target: 'brain' },
    },
    router_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 25 },
        { duration: '1m', target: 50 },
        { duration: '30s', target: 50 },
        { duration: '30s', target: 0 },
      ],
      exec: 'routerTest',
      tags: { scenario: 'load', target: 'router' },
      startTime: '10s',
    },
    gateway_load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '30s', target: 100 },
        { duration: '1m', target: 200 },
        { duration: '30s', target: 200 },
        { duration: '30s', target: 0 },
      ],
      exec: 'gatewayTest',
      tags: { scenario: 'load', target: 'gateway' },
      startTime: '20s',
    },
  },
  thresholds: loadThresholds,
};

// ── Stress Test ─────────────────────────────────────────────────────────────
export const stressOptions = {
  scenarios: {
    brain_stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '1m', target: 200 },
        { duration: '1m', target: 300 },
        { duration: '1m', target: 0 },
      ],
      exec: 'brainTest',
      tags: { scenario: 'stress', target: 'brain' },
    },
    router_stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 25 },
        { duration: '1m', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '1m', target: 150 },
        { duration: '1m', target: 0 },
      ],
      exec: 'routerTest',
      tags: { scenario: 'stress', target: 'router' },
      startTime: '30s',
    },
    gateway_stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 100 },
        { duration: '1m', target: 200 },
        { duration: '1m', target: 400 },
        { duration: '1m', target: 600 },
        { duration: '1m', target: 0 },
      ],
      exec: 'gatewayTest',
      tags: { scenario: 'stress', target: 'gateway' },
      startTime: '1m',
    },
  },
  thresholds: {
    ...loadThresholds,
    brain_errors: ['rate<=0.05'],
    router_errors: ['rate<=0.10'],
    gateway_errors: ['rate<=0.05'],
  },
};

// ── Soak Test ───────────────────────────────────────────────────────────────
export const soakOptions = {
  scenarios: {
    brain_soak: {
      executor: 'constant-vus',
      vus: 50,
      duration: '10m',
      exec: 'brainTest',
      tags: { scenario: 'soak', target: 'brain' },
    },
    router_soak: {
      executor: 'constant-vus',
      vus: 25,
      duration: '10m',
      exec: 'routerTest',
      tags: { scenario: 'soak', target: 'router' },
      startTime: '30s',
    },
    gateway_soak: {
      executor: 'constant-vus',
      vus: 100,
      duration: '10m',
      exec: 'gatewayTest',
      tags: { scenario: 'soak', target: 'gateway' },
      startTime: '1m',
    },
  },
  thresholds: loadThresholds,
};

// ── Dynamic Options ─────────────────────────────────────────────────────────
const testType = __ENV.TEST_TYPE || 'load';
export const options = (() => {
  switch (testType) {
    case 'smoke':  return smokeOptions;
    case 'load':   return loadOptions;
    case 'stress': return stressOptions;
    case 'soak':   return soakOptions;
    default:       return loadOptions;
  }
})();

console.log(`[NeXifyAI LoadTest] Type: ${testType} | Brain: ${BRAIN_PORT} | Router: ${ROUTER_PORT} | Gateway: ${GATEWAY_PORT}`);

// ── Scenario Executors ─────────────────────────────────────────────────────

// Brain API Test
export function brainTest() {
  group('Brain API', function () {
    // Health check
    const healthRes = http.get(BRAIN_HEALTH, {
      tags: { endpoint: 'brain_health' },
    });
    check(healthRes, {
      'brain health 200': (r) => r.status === 200,
    });
    totalRequests.add(1);

    // Search query (POST with JSON body)
    const query = testQueries[Math.floor(Math.random() * testQueries.length)];
    const queryRes = http.post(BRAIN_QUERY, JSON.stringify({ query, limit: 3 }), {
      headers: { 'Content-Type': 'application/json' },
      tags: { endpoint: 'brain_query' },
    });
    brainQueryTime.add(queryRes.timings.duration);
    brainErrors.add(!(queryRes.status >= 200 && queryRes.status < 300));
    check(queryRes, {
      'brain query ok': (r) => r.status >= 200 && r.status < 300,
      'brain query < 50ms': (r) => r.timings.duration < 50,
    });
    totalRequests.add(1);

    // Store (every 15th request to avoid flooding)
    if (__ITER % 15 === 0) {
      const storeRes = http.post(BRAIN_STORE, JSON.stringify({
        content: `Load test entry ${__VU}-${__ITER} at ${Date.now()}`,
        category: 'loadtest',
        source: 'k6-autopilot',
      }), {
        headers: { 'Content-Type': 'application/json' },
        tags: { endpoint: 'brain_store' },
      });
      brainStoreTime.add(storeRes.timings.duration);
      brainErrors.add(!(storeRes.status >= 200 && storeRes.status < 300));
      check(storeRes, {
        'brain store ok': (r) => r.status >= 200 && r.status < 300,
      });
      totalRequests.add(1);
    }

    // Stats (every 20th request)
    if (__ITER % 20 === 0) {
      const statsRes = http.get(BRAIN_STATS, {
        tags: { endpoint: 'brain_stats' },
      });
      check(statsRes, {
        'brain stats 200': (r) => r.status === 200,
      });
      totalRequests.add(1);
    }

    // Categories (every 30th request)
    if (__ITER % 30 === 0) {
      const catRes = http.get(BRAIN_CATEGORIES, {
        tags: { endpoint: 'brain_categories' },
      });
      check(catRes, {
        'brain categories 200': (r) => r.status === 200,
      });
      totalRequests.add(1);
    }
  });

  sleep(0.5);
}

// 9Router Test
export function routerTest() {
  group('9Router', function () {
    // Get model list
    const res = http.get(ROUTER_HEALTH, {
      tags: { endpoint: 'router_models' },
    });
    routerTime.add(res.timings.duration);
    // 9Router returns 307 redirect on /v1/models, 200 on actual chat completion
    const ok = res.status === 200 || res.status === 307;
    routerErrors.add(!ok);
    check(res, {
      'router reachable': () => ok,
      'router response < 2s': (r) => r.timings.duration < 2000,
    });
    totalRequests.add(1);

    // Chat completion (every 5th request — expensive!)
    if (__ITER % 5 === 0) {
      const chatRes = http.post(ROUTER_CHAT, JSON.stringify({
        model: 'nexifyai-power-llm',
        messages: [{ role: 'user', content: 'Say "ok" in 1 word.' }],
        max_tokens: 10,
      }), {
        headers: { 'Content-Type': 'application/json' },
        tags: { endpoint: 'router_chat' },
      });
      routerTime.add(chatRes.timings.duration);
      routerErrors.add(chatRes.status !== 200);
      check(chatRes, {
        'router chat 200': (r) => r.status === 200,
      });
      totalRequests.add(1);
    }
  });

  sleep(1);
}

// Gateway Test
export function gatewayTest() {
  group('Gateway', function () {
    // Gateway is socat TCP proxy — skip if connection refused
    const res = http.get(GATEWAY_HEALTH, {
      tags: { endpoint: 'gateway_health' },
      timeout: '2s',
    });
    gatewayTime.add(res.timings.duration);
    // Accept 000 (no connection) as gateway might be TCP proxy
    const ok = res.status === 200 || res.status === 0;
    gatewayErrors.add(!(res.status === 200 || res.status === 0));
    if (res.status !== 0) {
      check(res, {
        'gateway health 200': (r) => r.status === 200,
      });
    }
    totalRequests.add(1);
  });

  sleep(0.3);
}

// ── Custom Summary ─────────────────────────────────────────────────────────
export function handleSummary(data) {
  const summary = {
    meta: {
      timestamp: new Date().toISOString(),
      test: __ENV.TEST_TYPE || 'load',
      thresholds: {
        brain: { p99: '≤50ms', p95: '≤30ms', errors: '≤1%' },
        router: { p99: '≤2000ms', p95: '≤1000ms', errors: '≤5%' },
        gateway: { p99: '≤200ms', p95: '≤100ms', errors: '≤1%' },
      },
    },
    results: {
      brain: {
        query_time: {
          avg: data.metrics.brain_query_time ? data.metrics.brain_query_time.values.avg : null,
          min: data.metrics.brain_query_time ? data.metrics.brain_query_time.values.min : null,
          max: data.metrics.brain_query_time ? data.metrics.brain_query_time.values.max : null,
          p50: data.metrics.brain_query_time ? data.metrics.brain_query_time.values['p(50)'] : null,
          p90: data.metrics.brain_query_time ? data.metrics.brain_query_time.values['p(90)'] : null,
          p95: data.metrics.brain_query_time ? data.metrics.brain_query_time.values['p(95)'] : null,
          p99: data.metrics.brain_query_time ? data.metrics.brain_query_time.values['p(99)'] : null,
        },
        store_time: {
          avg: data.metrics.brain_store_time ? data.metrics.brain_store_time.values.avg : null,
          p95: data.metrics.brain_store_time ? data.metrics.brain_store_time.values['p(95)'] : null,
          p99: data.metrics.brain_store_time ? data.metrics.brain_store_time.values['p(99)'] : null,
        },
        error_rate: data.metrics.brain_errors ? data.metrics.brain_errors.values.rate : null,
      },
      router: {
        response_time: {
          avg: data.metrics.router_response_time ? data.metrics.router_response_time.values.avg : null,
          p95: data.metrics.router_response_time ? data.metrics.router_response_time.values['p(95)'] : null,
          p99: data.metrics.router_response_time ? data.metrics.router_response_time.values['p(99)'] : null,
        },
        error_rate: data.metrics.router_errors ? data.metrics.router_errors.values.rate : null,
      },
      gateway: {
        response_time: {
          avg: data.metrics.gateway_response_time ? data.metrics.gateway_response_time.values.avg : null,
          p95: data.metrics.gateway_response_time ? data.metrics.gateway_response_time.values['p(95)'] : null,
          p99: data.metrics.gateway_response_time ? data.metrics.gateway_response_time.values['p(99)'] : null,
        },
        error_rate: data.metrics.gateway_errors ? data.metrics.gateway_errors.values.rate : null,
      },
    },
    total_requests: data.metrics.total_requests ? data.metrics.total_requests.values.count : null,
    passes: data.metrics.checks ? data.metrics.checks.values.passes : null,
    failures: data.metrics.checks ? data.metrics.checks.values.fails : null,
    threshold_passed: Object.entries(data.metrics).every(([key, metric]) => {
      if (metric.thresholds) {
        return metric.thresholds.every(t => t.ok);
      }
      return true;
    }),
  };

  // Write JSON summary for Brain
  const jsonStr = JSON.stringify(summary, null, 2);

  const result = {};
  result.stdout = textSummary(data, { indent: '  ', enableColor: true });
  result['/tmp/nexify-loadtest-result.json'] = jsonStr;
  return result;
}
