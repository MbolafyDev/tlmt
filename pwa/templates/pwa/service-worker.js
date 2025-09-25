// Version d’app (sert à invalider les anciens caches lors du déploiement)
const APP_VERSION = "{{ APP_VERSION }}";
const CACHE_NAME = `tlmt-precache-${APP_VERSION}`;

// Fichiers critiques à mettre en cache
const PRECACHE_URLS = [
  "/",                 // page d'accueil
  "/offline/",         // page de secours hors-ligne
  "/static/css/main.css",
  "/static/js/main.js",
  "/static/pwa/icons/icon-192.png",
  "/static/pwa/icons/icon-512.png",
  "/static/pwa/icons/maskable-512.png",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(PRECACHE_URLS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.map((k) => (k !== CACHE_NAME ? caches.delete(k) : null)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Ne pas interférer avec l’admin
  if (url.pathname.startsWith("/admin/")) return;

  // PDFs → network-first pour ouverture inline
  if (url.pathname.endsWith(".pdf")) {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(async () => {
          const cached = await caches.match(req);
          return cached || caches.match("/offline/");
        })
    );
    return;
  }

  // Navigation (HTML) → network-first
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const copy = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
          return res;
        })
        .catch(async () => {
          const cached = await caches.match(req);
          return cached || caches.match("/offline/");
        })
    );
    return;
  }

  // Statiques → cache-first
  if (
    req.destination === "style" ||
    req.destination === "script" ||
    req.destination === "image" ||
    url.pathname.startsWith("/static/")
  ) {
    event.respondWith(
      caches.match(req).then((cached) => {
        return (
          cached ||
          fetch(req).then((res) => {
            const copy = res.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put(req, copy));
            return res;
          })
        );
      })
    );
    return;
  }

  // Par défaut → passe-réseau
});
