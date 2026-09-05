/* Service worker for Driver's Test Prep.
 *
 * Strategy:
 *   - app shell (index.html, manifest, icons, i18n, state index): precached at
 *     install; navigations are network-first so a new deploy is picked up on
 *     the next online visit, with the cached shell as the offline fallback.
 *   - hashed build assets (/assets/*): cache-first, they never change.
 *   - question banks, sign images, static pages: stale-while-revalidate, so a
 *     state you have practised keeps working offline.
 *
 * CACHE_VERSION is bumped whenever the caching logic changes; old caches are
 * dropped on activate.
 */
const CACHE_VERSION = 'drivers-test-v1';
const SHELL = [
  './',
  './index.html',
  './manifest.webmanifest',
  './favicon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './i18n.json',
  './data/index.json',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches
      .open(CACHE_VERSION)
      .then((cache) => cache.addAll(SHELL))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))),
      )
      .then(() => self.clients.claim()),
  );
});

const scopePath = new URL(self.registration.scope).pathname;

function inScope(url) {
  return url.origin === self.location.origin && url.pathname.startsWith(scopePath);
}

async function networkFirst(request, fallbackPath) {
  const cache = await caches.open(CACHE_VERSION);
  try {
    const fresh = await fetch(request);
    if (fresh.ok) cache.put(request, fresh.clone());
    return fresh;
  } catch {
    const cached =
      (await cache.match(request)) || (fallbackPath && (await cache.match(fallbackPath)));
    if (cached) return cached;
    throw new Error('offline');
  }
}

async function cacheFirst(request) {
  const cache = await caches.open(CACHE_VERSION);
  const cached = await cache.match(request);
  if (cached) return cached;
  const fresh = await fetch(request);
  if (fresh.ok) cache.put(request, fresh.clone());
  return fresh;
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_VERSION);
  const cached = await cache.match(request);
  const refresh = fetch(request)
    .then((fresh) => {
      if (fresh.ok) cache.put(request, fresh.clone());
      return fresh;
    })
    .catch(() => cached);
  return cached || refresh;
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;
  const url = new URL(request.url);
  if (!inScope(url)) return;

  if (request.mode === 'navigate') {
    event.respondWith(networkFirst(request, './index.html'));
    return;
  }
  const rel = url.pathname.slice(scopePath.length);
  if (rel.startsWith('assets/')) {
    event.respondWith(cacheFirst(request));
    return;
  }
  event.respondWith(staleWhileRevalidate(request));
});
