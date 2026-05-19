import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiFetch } from "./api";
import { logger } from "./logger";

function mockFetchOnce(
  status: number,
  body: unknown,
  headers: Record<string, string> = {},
): void {
  const response = new Response(body !== undefined ? JSON.stringify(body) : null, {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
  vi.stubGlobal("fetch", vi.fn(async () => response));
}

beforeEach(() => {
  vi.spyOn(logger, "warn").mockImplementation(() => {});
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("apiFetch error logging", () => {
  it("logs api_error with method, path, status, and request id on non-OK", async () => {
    mockFetchOnce(
      500,
      { detail: "boom", code: "internal_error" },
      { "X-Request-ID": "req-xyz" },
    );

    await expect(apiFetch("/things")).rejects.toBeInstanceOf(ApiError);

    expect(logger.warn).toHaveBeenCalledWith("api_error", {
      method: "GET",
      path: "/things",
      status: 500,
      requestId: "req-xyz",
    });
  });

  it("captures the inbound method when provided", async () => {
    mockFetchOnce(404, { detail: "not found", code: "not_found" });

    await expect(
      apiFetch("/things/1", { method: "DELETE" }),
    ).rejects.toBeInstanceOf(ApiError);

    expect(logger.warn).toHaveBeenCalledWith(
      "api_error",
      expect.objectContaining({
        method: "DELETE",
        path: "/things/1",
        status: 404,
      }),
    );
  });

  it("uses undefined for requestId when the response lacks the header", async () => {
    mockFetchOnce(409, { detail: "conflict", code: "duplicate_email" });

    await expect(apiFetch("/employees", { method: "POST" })).rejects.toBeInstanceOf(
      ApiError,
    );

    expect(logger.warn).toHaveBeenCalledWith(
      "api_error",
      expect.objectContaining({ requestId: undefined }),
    );
  });

  it("does not log on successful responses", async () => {
    mockFetchOnce(200, { hello: "world" });

    await apiFetch<{ hello: string }>("/ok");

    expect(logger.warn).not.toHaveBeenCalled();
  });
});
