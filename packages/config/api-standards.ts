/**
 * NeXifyAI — API Standards & Error Schema
 * Version: 1.0 | Stand: 2026-05-08
 * Verbindlich für alle Backend-APIs ab sofort.
 *
 * Usage:
 *   import { ApiError, errorResponse } from '@nexifyai/api-standards';
 *   throw new ApiError(400, 'VALIDATION_ERROR', 'Ungültige Eingabe', [...]);
 */

// ══════════════════════════════════════════════
// ERROR RESPONSE (Standard)
// ══════════════════════════════════════════════

export interface ApiErrorDetail {
  field?: string;
  reason: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
    details?: ApiErrorDetail[];
    request_id: string;
    timestamp: string;
  };
}

export class ApiError extends Error {
  status: number;
  code: string;
  details?: ApiErrorDetail[];

  constructor(status: number, code: string, message: string, details?: ApiErrorDetail[]) {
    super(message);
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

export function errorResponse(
  status: number,
  code: string,
  message: string,
  details?: ApiErrorDetail[],
  requestId?: string
): { status: number; body: ApiErrorResponse } {
  return {
    status,
    body: {
      error: {
        code,
        message,
        details: details || [],
        request_id: requestId || crypto.randomUUID(),
        timestamp: new Date().toISOString(),
      },
    },
  };
}

// ══════════════════════════════════════════════
// PAGINATION (Standard)
// ══════════════════════════════════════════════

export interface PaginationParams {
  page?: number;   // default: 1
  limit?: number;  // default: 50, max: 200
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    pages: number;
  };
}

// ══════════════════════════════════════════════
// HTTP STATUS CODES (Standard)
// ══════════════════════════════════════════════

export const HttpStatus = {
  OK: 200,
  CREATED: 201,
  NO_CONTENT: 204,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  CONFLICT: 409,
  RATE_LIMITED: 429,
  INTERNAL_ERROR: 500,
  SERVICE_UNAVAILABLE: 503,
} as const;

// ══════════════════════════════════════════════
// ERROR CODES (Standard)
// ══════════════════════════════════════════════

export const ErrorCodes = {
  // 400
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  INVALID_INPUT: 'INVALID_INPUT',
  MISSING_FIELD: 'MISSING_FIELD',

  // 401
  UNAUTHORIZED: 'UNAUTHORIZED',
  TOKEN_EXPIRED: 'TOKEN_EXPIRED',
  INVALID_TOKEN: 'INVALID_TOKEN',

  // 403
  FORBIDDEN: 'FORBIDDEN',
  INSUFFICIENT_SCOPE: 'INSUFFICIENT_SCOPE',

  // 404
  NOT_FOUND: 'NOT_FOUND',
  RESOURCE_NOT_FOUND: 'RESOURCE_NOT_FOUND',

  // 409
  CONFLICT: 'CONFLICT',
  DUPLICATE_ENTRY: 'DUPLICATE_ENTRY',

  // 429
  RATE_LIMITED: 'RATE_LIMITED',

  // 500
  INTERNAL_ERROR: 'INTERNAL_ERROR',
  DATABASE_ERROR: 'DATABASE_ERROR',
  LLM_ERROR: 'LLM_ERROR',
  GATEWAY_ERROR: 'GATEWAY_ERROR',
} as const;

// ══════════════════════════════════════════════
// AUTH HEADERS
// ══════════════════════════════════════════════

export const AuthHeaders = {
  USER: 'Authorization',           // Bearer {jwt_token}
  API_KEY: 'X-API-Key',            // nxa_live_{...}
  IDEMPOTENCY: 'Idempotency-Key',  // UUID
} as const;

// ══════════════════════════════════════════════
// RATE LIMITS
// ══════════════════════════════════════════════

export const RateLimits = {
  DEFAULT: 100,      // Requests pro Minute (Standard-User)
  AUTHENTICATED: 300, // Requests pro Minute (Auth-User)
  API_KEY: 1000,      // Requests pro Stunde (API-Key)
  ADMIN: 600,         // Requests pro Minute (Admin)
} as const;

// ══════════════════════════════════════════════
// VERSIONING
// ══════════════════════════════════════════════

export const ApiVersion = {
  CURRENT: 'v1',
  DEPRECATED: [] as string[],
  SUNSET_DATES: {} as Record<string, string>,
} as const;
