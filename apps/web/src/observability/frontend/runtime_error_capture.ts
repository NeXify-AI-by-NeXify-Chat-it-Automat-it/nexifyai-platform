// runtime_error_capture.ts — Global error, rejection & console interception
// P0: Frontend Runtime Diagnostics — deployed with app
interface RuntimeErrorEvent {
  type: 'error' | 'unhandledrejection' | 'console.error' | 'react.error' | 'hydration.error';
  message: string;
  stack?: string;
  componentStack?: string;
  route?: string;
  timestamp: string;
  buildInfo?: string;
  meta?: Record<string, unknown>;
}

const captured: RuntimeErrorEvent[] = [];
const MAX_CAPTURED = 50;

function capture(ev: RuntimeErrorEvent) {
  ev.timestamp = new Date().toISOString();
  ev.route = window.location.pathname;
  captured.push(ev);
  if (captured.length > MAX_CAPTURED) captured.shift();
  // Store for ErrorBoundary to read
  (window as unknown as Record<string, unknown>).__NX_RUNTIME_ERRORS__ = captured;
}

// Intercept window.onerror
window.onerror = (msg, source, line, col, err) => {
  capture({
    type: 'error',
    message: String(msg),
    stack: err?.stack || `${source}:${line}:${col}`,
  });
  return false;
};

// Intercept unhandled rejections
window.onunhandledrejection = (ev: PromiseRejectionEvent) => {
  const reason = ev.reason;
  capture({
    type: 'unhandledrejection',
    message: reason?.message || String(reason),
    stack: reason?.stack,
  });
};

// Intercept console.error
const origConsoleError = console.error;
console.error = (...args: unknown[]) => {
  capture({
    type: 'console.error',
    message: args.map(a => typeof a === 'object' ? safeStringify(a) : String(a)).join(' '),
  });
  origConsoleError.apply(console, args);
};

// Intercept React error boundary failures via DOM observation
const observer = new MutationObserver(() => {
  const errElems = document.querySelectorAll('[data-rrdu-error]');
  if (errElems.length > 0) {
    capture({
      type: 'react.error',
      message: 'React ErrorBoundary triggered',
      componentStack: document.getElementById('nx-error-stack')?.textContent || undefined,
    });
  }
});
observer.observe(document.body, { childList: true, subtree: true, attributes: true });

function safeStringify(obj: unknown): string {
  try { return JSON.stringify(obj); } catch { return String(obj); }
}

// Build info from meta tag or env
const meta = document.querySelector('meta[name=build-info]');
const buildInfo = meta?.getAttribute('content') || 'dev';

export function getCapturedErrors(): RuntimeErrorEvent[] {
  return [...captured];
}

export function clearCaptured(): void {
  captured.length = 0;
}
