/**
 * NeXifyAI Workflows — Native event-driven workflow services.
 * BullMQ-based queue system for background jobs, email processing, task execution.
 * 
 * @package @nexifyai/workflows
 * @version 1.0.0
 */

export { eventQueue, emailQueue, taskQueue, connection as redisConnection } from './queue';
export type { JobResult, QueueName } from './types';
