import { DEFAULT_VERSION, WORKER_NAME, type Env } from "./types";

export interface WorkerConfig {
  name: string;
  version: string;
}

export function readConfig(env: Env): WorkerConfig {
  return {
    name: WORKER_NAME,
    version: env.VERSION?.trim() || DEFAULT_VERSION,
  };
}
