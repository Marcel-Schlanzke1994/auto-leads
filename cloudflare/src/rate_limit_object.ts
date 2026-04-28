import { DurableObject } from "cloudflare:workers";

export interface RateLimitCheckRequest {
  scope: "lead" | "domain" | "operation";
  key: string;
  limit: number;
  windowSeconds: number;
}

export interface RateLimitCheckResult {
  allowed: boolean;
  remaining: number;
  resetAt: string;
  scope: RateLimitCheckRequest["scope"];
  key: string;
}

interface CounterRecord {
  count: number;
  resetAtMs: number;
}

export class OutreachRateLimiter extends DurableObject {
  async checkRateLimit(input: RateLimitCheckRequest): Promise<RateLimitCheckResult> {
    const now = Date.now();
    const storageKey = `${input.scope}:${input.key}`;
    const existing = await this.ctx.storage.get<CounterRecord>(storageKey);

    let counter = existing;
    if (!counter || now >= counter.resetAtMs) {
      counter = {
        count: 0,
        resetAtMs: now + input.windowSeconds * 1000,
      };
    }

    const allowed = counter.count < input.limit;
    if (allowed) {
      counter.count += 1;
      await this.ctx.storage.put(storageKey, counter);
    }

    const remaining = Math.max(input.limit - counter.count, 0);

    return {
      allowed,
      remaining,
      resetAt: new Date(counter.resetAtMs).toISOString(),
      scope: input.scope,
      key: input.key,
    };
  }
}

export function isValidRateLimitRequest(payload: unknown): payload is RateLimitCheckRequest {
  if (!payload || typeof payload !== "object") {
    return false;
  }

  const record = payload as Record<string, unknown>;
  const validScopes = new Set(["lead", "domain", "operation"]);

  return (
    typeof record.scope === "string" &&
    validScopes.has(record.scope) &&
    typeof record.key === "string" &&
    record.key.trim().length > 0 &&
    typeof record.limit === "number" &&
    Number.isInteger(record.limit) &&
    record.limit > 0 &&
    typeof record.windowSeconds === "number" &&
    Number.isInteger(record.windowSeconds) &&
    record.windowSeconds > 0
  );
}
