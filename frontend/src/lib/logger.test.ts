import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { logger } from "./logger";

beforeEach(() => {
  vi.spyOn(console, "info").mockImplementation(() => {});
  vi.spyOn(console, "warn").mockImplementation(() => {});
  vi.spyOn(console, "error").mockImplementation(() => {});
});

afterEach(() => {
  vi.restoreAllMocks();
  vi.unstubAllEnvs();
});

describe("logger in development (default vitest env)", () => {
  it("emits info to console.info with fields", () => {
    logger.info("hello", { foo: "bar" });

    expect(console.info).toHaveBeenCalledWith("hello", { foo: "bar" });
  });

  it("emits warn to console.warn with fields", () => {
    logger.warn("alert", { level: 1 });

    expect(console.warn).toHaveBeenCalledWith("alert", { level: 1 });
  });

  it("emits error to console.error", () => {
    logger.error("oops");

    expect(console.error).toHaveBeenCalledWith("oops", undefined);
  });
});

describe("logger when PROD is true (production build)", () => {
  it("drops info calls so logs are not noisy in production", () => {
    vi.stubEnv("PROD", "true");

    logger.info("hello");

    expect(console.info).not.toHaveBeenCalled();
  });

  it("still emits warn so production issues remain visible", () => {
    vi.stubEnv("PROD", "true");

    logger.warn("alert");

    expect(console.warn).toHaveBeenCalledWith("alert", undefined);
  });

  it("still emits error so production failures remain visible", () => {
    vi.stubEnv("PROD", "true");

    logger.error("boom", { code: "x" });

    expect(console.error).toHaveBeenCalledWith("boom", { code: "x" });
  });
});
