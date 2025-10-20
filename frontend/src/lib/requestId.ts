export function makeRequestId(): string {
  return crypto.randomUUID().replace(/-/g, "");
}
