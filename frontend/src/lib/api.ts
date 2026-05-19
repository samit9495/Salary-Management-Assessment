import { logger } from "./logger";

export class ApiError extends Error {
  readonly status: number;
  readonly code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

type ApiInit = Omit<RequestInit, "body"> & { body?: unknown };

export async function apiFetch<T>(path: string, init: ApiInit = {}): Promise<T> {
  const { body, headers, method, ...rest } = init;

  const response = await fetch(`${BASE_URL}${path}`, {
    ...rest,
    method,
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let detail = response.statusText;
    let code: string | undefined;
    try {
      const errorBody = (await response.json()) as { detail?: string; code?: string };
      if (errorBody.detail) detail = errorBody.detail;
      code = errorBody.code;
    } catch {
      // body wasn't JSON; keep statusText
    }
    logger.warn("api_error", {
      method: method ?? "GET",
      path,
      status: response.status,
      requestId: response.headers.get("X-Request-ID") ?? undefined,
    });
    throw new ApiError(response.status, detail, code);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
