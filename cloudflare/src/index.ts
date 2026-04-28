export interface Env {
  APP_ENV?: string;
}

const FOUNDATION_INFO = {
  name: "auto-leads-cloudflare-foundation",
  version: "0.1.0",
};

export default {
  async fetch(request: Request, _env: Env): Promise<Response> {
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

    return Response.json(
      {
        error: "not_found",
        message: "Only /health and /version are available in foundation phase.",
      },
      { status: 404 },
    );
  },
};
