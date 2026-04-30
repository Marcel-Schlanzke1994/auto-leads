import { DurableObject } from "cloudflare:workers";
import type { RateLimitCheckRequest, RateLimitCheckResult } from "./types";

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
