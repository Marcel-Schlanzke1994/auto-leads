import type { ErrorBody } from "./types";

const SECURITY_HEADERS: Record<string, string> = {
  "content-type": "application/json; charset=utf-8",
  "x-content-type-options": "nosniff",
};

function mergeHeaders(init?: ResponseInit, noStore = false): Headers {
  const headers = new Headers(init?.headers);
  Object.entries(SECURITY_HEADERS).forEach(([k, v]) => headers.set(k, v));
  if (noStore) {
    headers.set("cache-control", "no-store");
  }
  return headers;
}

export function jsonOk(data: unknown, init?: ResponseInit, noStore = false): Response {
  return new Response(JSON.stringify(data), {
    ...init,
    headers: mergeHeaders(init, noStore),
  });
}

export function jsonError(
  code: string,
  message: string,
  status: number,
  details?: Record<string, unknown>,
): Response {
  const body: ErrorBody = { error: code, message };
  if (details) {
    body.details = details;
  }

  return new Response(JSON.stringify(body), {
    status,
    headers: mergeHeaders(undefined, true),
  });
}
