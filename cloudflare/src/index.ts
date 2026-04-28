import { OutreachRateLimiter, isValidRateLimitRequest, type RateLimitCheckRequest } from "./rate_limit_object";

export interface Env {
  APP_ENV?: string;
  OUTREACH_RATE_LIMITER: DurableObjectNamespace<OutreachRateLimiter>;
}

const FOUNDATION_INFO = {
  name: "auto-leads-cloudflare-foundation",
  version: "0.1.0",
};

const BAD_REQUEST_RESPONSE = {
  error: "bad_request",
  message:
    "Expected JSON body: { scope: 'lead|domain|operation', key: 'string', limit: number > 0, windowSeconds: number > 0 }",
};

export { OutreachRateLimiter };

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { pathname } = new URL(request.url);

    if (request.method === "GET" && pathname === "/health") {
      return Response.json({
        status: "ok",
        service: FOUNDATION_INFO.name,
      });
    }

    if (request.method === "GET" && pathname === "/version") {
      return Response.json(FOUNDATION_INFO);
    }

    if (request.method === "POST" && pathname === "/rate-limit/check") {
      let payload: unknown;
      try {
        payload = await request.json();
      } catch {
        return Response.json(BAD_REQUEST_RESPONSE, { status: 400 });
      }

      if (!isValidRateLimitRequest(payload)) {
        return Response.json(BAD_REQUEST_RESPONSE, { status: 400 });
      }

      const rateLimitInput = payload as RateLimitCheckRequest;
      const durableObjectKey = `${rateLimitInput.scope}:${rateLimitInput.key}`;
      const stub = env.OUTREACH_RATE_LIMITER.getByName(durableObjectKey);
      const result = await stub.checkRateLimit(rateLimitInput);

      return Response.json(result);
    }

    return Response.json(
      {
        error: "not_found",
        message:
          "Supported endpoints: GET /health, GET /version, POST /rate-limit/check (prototype only).",
      },
      { status: 404 },
    );
  },
};
