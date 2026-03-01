type CacheEntry<T> = {
  expiresAt: number;
  value: T;
};

const store = new Map<string, CacheEntry<unknown>>();

export function getCached<T>(key: string): T | null {
  const entry = store.get(key);
  if (!entry) {
    return null;
  }
  if (Date.now() > entry.expiresAt) {
    store.delete(key);
    return null;
  }
  return entry.value as T;
}

export function setCached<T>(key: string, value: T, ttlMs: number) {
  store.set(key, { value, expiresAt: Date.now() + ttlMs });
}

export async function withCache<T>(key: string, ttlMs: number, loader: () => Promise<T> | T): Promise<T> {
  const cached = getCached<T>(key);
  if (cached) {
    return cached;
  }
  const value = await loader();
  setCached(key, value, ttlMs);
  return value;
}
