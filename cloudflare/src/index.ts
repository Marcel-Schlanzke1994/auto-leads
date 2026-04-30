import { readConfig } from "./config";
import { HttpError, isHttpError } from "./errors";
import { jsonError, jsonOk } from "./responses";
import { OutreachRateLimiter } from "./rate_limit_object";
import { type Env, type RateLimitCheckRequest, VALID_SCOPES } from "./types";

const MAX_BODY_BYTES = 4096;
const MAX_KEY_LENGTH = 256;
const MIN_LIMIT = 1;
const MAX_LIMIT = 1000;
const MIN_WINDOW_SECONDS = 1;
const MAX_WINDOW_SECONDS = 86400;

export { OutreachRateLimiter };

async function parseRequestBody(request: Request): Promise<unknown> {
  const contentLengthHeader = request.headers.get("content-length");
  if (contentLengthHeader) {
    const contentLength = Number(contentLengthHeader);
    if (Number.isFinite(contentLength) && contentLength > MAX_BODY_BYTES) {
      throw new HttpError(413, "payload_too_large", "Request body exceeds maximum allowed size.");
    }
  }

  const contentType = request.headers.get("content-type");
  if (contentType && !contentType.toLowerCase().includes("application/json")) {
    throw new HttpError(415, "unsupported_media_type", "Content-Type must be application/json.");
  }

  let raw = "";
  try {
    raw = await request.text();
  } catch {
    throw new HttpError(400, "invalid_request", "Request body could not be read.");
  }

  if (raw.length > MAX_BODY_BYTES) {
    throw new HttpError(413, "payload_too_large", "Request body exceeds maximum allowed size.");
  }

  try {
    return JSON.parse(raw);
  } catch {
    throw new HttpError(400, "invalid_json", "Request body must be valid JSON.");
  }
}

function validateRateLimitRequest(payload: unknown): RateLimitCheckRequest {
  if (!payload || typeof payload !== "object") {
    throw new HttpError(400, "bad_request", "Expected JSON object body.");
  }

  const record = payload as Record<string, unknown>;
  if (typeof record.scope !== "string" || !VALID_SCOPES.includes(record.scope as (typeof VALID_SCOPES)[number])) {
    throw new HttpError(400, "invalid_scope", "scope must be one of: lead, domain, operation.");
  }

  if (typeof record.key !== "string") {
    throw new HttpError(400, "invalid_key", "key must be a string.");
  }

  const key = record.key.trim();
  if (key.length < 1 || key.length > MAX_KEY_LENGTH) {
    throw new HttpError(400, "invalid_key", `key length must be between 1 and ${MAX_KEY_LENGTH} characters.`);
  }

  if (typeof record.limit !== "number" || !Number.isInteger(record.limit) || record.limit < MIN_LIMIT || record.limit > MAX_LIMIT) {
    throw new HttpError(400, "invalid_limit", `limit must be an integer between ${MIN_LIMIT} and ${MAX_LIMIT}.`);
  }

  if (
    typeof record.windowSeconds !== "number" ||
    !Number.isInteger(record.windowSeconds) ||
    record.windowSeconds < MIN_WINDOW_SECONDS ||
    record.windowSeconds > MAX_WINDOW_SECONDS
  ) {
    throw new HttpError(
      400,
      "invalid_window",
      `windowSeconds must be an integer between ${MIN_WINDOW_SECONDS} and ${MAX_WINDOW_SECONDS}.`,
    );
  }

  return {
    scope: record.scope as RateLimitCheckRequest["scope"],
    key,
    limit: record.limit,
    windowSeconds: record.windowSeconds,
  };
}

function methodNotAllowed(pathname: string): Response {
  if (pathname === "/health" || pathname === "/version") {
    return jsonError("method_not_allowed", "Use GET for this endpoint.", 405);
  }
  if (pathname === "/rate-limit/check") {
    return jsonError("method_not_allowed", "Use POST for this endpoint.", 405);
  }
  return jsonError("not_found", "Route not found.", 404);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const { pathname } = new URL(request.url);
    const config = readConfig(env);

    try {
      if (pathname === "/health") {
        if (request.method !== "GET") {
          return methodNotAllowed(pathname);
        }
        return jsonOk({ status: "ok", service: config.name, timestamp: new Date().toISOString() }, undefined, true);
      }

      if (pathname === "/version") {
        if (request.method !== "GET") {
          return methodNotAllowed(pathname);
        }
        return jsonOk({ name: config.name, version: config.version }, undefined, true);
      }

      if (pathname === "/rate-limit/check") {
        if (request.method !== "POST") {
          return methodNotAllowed(pathname);
        }
        if (!env.OUTREACH_RATE_LIMITER) {
          throw new HttpError(503, "service_unavailable", "Rate limiter binding is not configured.");
        }

        const payload = await parseRequestBody(request);
        const rateLimitInput = validateRateLimitRequest(payload);
        const durableObjectKey = `${rateLimitInput.scope}:${rateLimitInput.key}`;
        const stub = env.OUTREACH_RATE_LIMITER.getByName(durableObjectKey) as unknown as {
          checkRateLimit: (input: RateLimitCheckRequest) => Promise<unknown>;
        };
        const result = await stub.checkRateLimit(rateLimitInput);
        return jsonOk(result, undefined, true);
      }

      return jsonError("not_found", "Supported endpoints: GET /health, GET /version, POST /rate-limit/check.", 404);
    } catch (error: unknown) {
      if (isHttpError(error)) {
        console.warn(`[worker] route=${pathname} status=${error.status} code=${error.code}`);
        return jsonError(error.code, error.message, error.status, error.details);
      }

      console.error(`[worker] route=${pathname} status=500 code=internal_error`);
      return jsonError("internal_error", "Unexpected server error.", 500);
    }
  },
};
