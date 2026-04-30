export const WORKER_NAME = "auto-leads-cloudflare-foundation";
export const DEFAULT_VERSION = "0.1.0";

export const VALID_SCOPES = ["lead", "domain", "operation"] as const;
export type RateLimitScope = (typeof VALID_SCOPES)[number];

export interface Env {
  VERSION?: string;
  OUTREACH_RATE_LIMITER?: DurableObjectNamespace;
}

export interface RateLimitCheckRequest {
  scope: RateLimitScope;
  key: string;
  limit: number;
  windowSeconds: number;
}

export interface RateLimitCheckResult {
  allowed: boolean;
  remaining: number;
  resetAt: string;
  scope: RateLimitScope;
  key: string;
}

export interface ErrorBody {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
