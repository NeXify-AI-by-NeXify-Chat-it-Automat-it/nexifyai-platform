import { Queue, Worker, QueueScheduler } from 'bullmq';
import Redis from 'ioredis';

const REDIS_HOST = process.env.REDIS_HOST || 'localhost';
const REDIS_PORT = parseInt(process.env.REDIS_PORT || '6379', 10);
const REDIS_PASSWORD = process.env.REDIS_PASSWORD || undefined;

export const connection = new Redis({
  host: REDIS_HOST,
  port: REDIS_PORT,
  password: REDIS_PASSWORD,
  maxRetriesPerRequest: null,
  enableOfflineQueue: false,
});

// ══════════════════════════════════════════════
// QUEUE DEFINITIONS
// ══════════════════════════════════════════════

/** System- und Business-Events */
export const eventQueue = new Queue('events', { connection });

/** E-Mail-Versand (Resend) */
export const emailQueue = new Queue('emails', { connection });

/** Autopilot-Tasks (cli-task-worker) */
export const taskQueue = new Queue('tasks', { connection });

/** Analytics Events (aggregation, batching) */
export const analyticsQueue = new Queue('analytics', { connection });

// Connection health check
connection.on('connect', () => {
  console.log('[workflows] Redis connected');
});

connection.on('error', (err) => {
  console.error('[workflows] Redis error:', err.message);
});
