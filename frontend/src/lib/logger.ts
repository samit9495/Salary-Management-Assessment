/**
 * Thin wrapper around `console` that:
 *
 * - emits structured `(event, fields)` calls so callers can include context
 *   like `requestId`, `status`, `path`;
 * - drops `info` calls in a production build so the user's console is not
 *   polluted by routine traffic, while keeping `warn` and `error` so real
 *   issues remain visible.
 *
 * Reads `import.meta.env.PROD` at call time (not module load) so tests
 * can flip it via `vi.stubEnv`.
 */

export type LogFields = Record<string, unknown>;

function isProductionBuild(): boolean {
  return Boolean(import.meta.env.PROD);
}

export const logger = {
  info(event: string, fields?: LogFields): void {
    if (isProductionBuild()) return;
    // eslint-disable-next-line no-console
    console.info(event, fields);
  },
  warn(event: string, fields?: LogFields): void {
    // eslint-disable-next-line no-console
    console.warn(event, fields);
  },
  error(event: string, fields?: LogFields): void {
    // eslint-disable-next-line no-console
    console.error(event, fields);
  },
};
