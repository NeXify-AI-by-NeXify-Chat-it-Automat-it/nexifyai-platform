/** Supported queue names */
export type QueueName = 'events' | 'emails' | 'tasks' | 'analytics';

/** Standardized job result */
export interface JobResult {
  success: boolean;
  message: string;
  data?: unknown;
  error?: string;
  duration_ms: number;
}
