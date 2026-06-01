import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const gatewayErr = new Rate('gateway_errors');
const gatewayLatency = new Trend('gateway_latency');

export const options = {
  stages: [
    { duration: '15s', target: 20 },
    { duration: '15s', target: 50 },
    { duration: '15s', target: 100 },
    { duration: '15s', target: 0 },
  ],
  thresholds: {
    'gateway_errors': ['rate<0.01'],
    'gateway_latency': ['p(95)<500', 'p(99)<1000'],
    http_req_failed: ['rate<0.05'],
  },
};

const HOSTS = [
  __ENV.HOST1 || 'https://nexifyai.cloud',
  __ENV.HOST2 || 'https://nexify-automate.com',
];

export default function () {
  const host = HOSTS[Math.floor(Math.random() * HOSTS.length)];

  group(`Gateway Home ${host}`, () => {
    const res = http.get(`${host}/`, { timeout: '10s' });
    check(res, {
      'homepage ok': (r) => r.status >= 200 && r.status < 400,
    });
    gatewayErr.add(res.status >= 500);
    gatewayLatency.add(res.timings.duration);
  });

  sleep(0.5);

  group(`Gateway Root ${host}`, () => {
    const res = http.get(host, { timeout: '10s' });
    check(res, {
      'root ok': (r) => r.status >= 200 && r.status < 400,
    });
    gatewayErr.add(res.status >= 500);
    gatewayLatency.add(res.timings.duration);
  });

  sleep(1);
}
