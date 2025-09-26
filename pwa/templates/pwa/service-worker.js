// ---------- Service Worker TLMT (Django) ----------
// Invalidation de cache par version d'app (passée depuis Django)
const APP_VERSION = "{{ APP_VERSION }}";
const CACHE_NAME = `tlmt-precache-${APP_VERSION}`;
const RUNTIME_CACHE = `tlmt-runtime-${APP_VERSION}`;

// URL offline (doit être routée !)
const OFFLINE_URL = "/offline/";

// Fichiers critiques à mettre en cache au "install"
const PRECACHE_URLS = [
  "/",                     // accueil
  OFFLINE_URL,             // page hors-ligne
  "/static/css/main.css",
  "/static/js/main.js",
  "/static/pwa/icons/icon-192.png",
  "/static/pwa/icons/icon-512.png",
  "/static/pwa/icons/maskable-512.png",
];

// Outils
const isHtmlRequest = (req) =>
  req.mode === "navigate" ||
  (req.headers.get("accept") || "").includes("text/html");

const isStaticRequest = (req, url) =>
  req.destination === "style" ||
  req.destination === "script" ||
  req.destination === "image" ||
  req.destination === "font" ||
  url.pathname.startsWith("/static/");

// ---------- INSTALL : pré-cache (tolérant aux erreurs) ----------
self.addEventListener("install", (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_NAME);
      // addAll échoue si 1 ressource manque -> on passe par allSettled
      const requests = PRECACHE_URLS.map((u) => new Request(u, { cache: "reload" }));
      const results = await Promise.allSettled(
        requests.map((req) => fetch(req).then((res) => res.ok ? res : Promise.reject(res)))
      );
      const okResponses = [];
      results.forEach((r, i) => { if (r.status === "fulfilled") okResponses.push([requests[i], r.value]); });
      await Promise.all(okResponses.map(([req, res]) => cache.put(req, res.clone())));
    })()
  );
  // activer immédiatement la nouvelle version côté SW
  self.skipWaiting();
});

// ---------- ACTIVATE : nettoyage des anciens caches ----------
self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const keys = await caches.keys();
      await Promise.all(
        keys
          .filter((k) => ![CACHE_NAME, RUNTIME_CACHE].includes(k))
          .map((k) => caches.delete(k))
      );
      await self.clients.claim();
      // Tente de pré-charger OFFLINE_URL si absent
      const c = await caches.open(CACHE_NAME);
      const hit = await c.match(OFFLINE_URL);
      if (!hit) {
        try {
          const res = await fetch(OFFLINE_URL, { cache: "reload" });
          if (res.ok) await c.put(OFFLINE_URL, res.clone());
        } catch (_) {
          // ignore si offline indisponible au premier tour
        }
      }
    })()
  );
});

// Permettre le "skipWaiting" depuis la page (après déploiement)
self.addEventListener("message", (event) => {
  if (event.data === "SKIP_WAITING") self.skipWaiting();
});

// ---------- FETCH : stratégies par type ----------
self.addEventListener("fetch", (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // On ne gère que les requêtes GET
  if (req.method !== "GET") return;

  // Ne pas interférer avec l’admin Django, ni endpoints sensibles
  if (url.pathname.startsWith("/admin/")) return;

  // PDFs → network-first (pour lecture inline), fallback cache/offline
  if (url.pathname.endsWith(".pdf")) {
    event.respondWith(networkFirst(req));
    return;
  }

  // Pages HTML → network-first (offline fallback)
  if (isHtmlRequest(req)) {
    event.respondWith(networkFirst(req, { offlineFallback: true }));
    return;
  }

  // Statique (CSS/JS/images/polices ou /static/) → stale-while-revalidate
  if (isStaticRequest(req, url)) {
    event.respondWith(staleWhileRevalidate(req));
    return;
  }

  // Par défaut : passthrough réseau (avec petit cache opportuniste)
  event.respondWith(staleWhileRevalidate(req));
});

// ---------- Stratégies ----------

async function networkFirst(request, { offlineFallback = false } = {}) {
  try {
    const response = await fetch(request);
    // On met en cache la réponse si valide
    if (response && response.ok) {
      const cache = await caches.open(RUNTIME_CACHE);
      cache.put(request, response.clone()).catch(() => {});
    }
    return response;
  } catch (err) {
    // Si réseau KO → retour cache, sinon offline
    const cached = await caches.match(request);
    if (cached) return cached;
    if (offlineFallback && isHtmlRequest(request)) {
      const offlineCached = await caches.match(OFFLINE_URL);
      if (offlineCached) return offlineCached;
    }
    // Dernier recours : réponse basique
    return new Response("", { status: 504, statusText: "Gateway Timeout" });
  }
}

async function staleWhileRevalidate(request) {
  const cache = await caches.open(RUNTIME_CACHE);
  const cached = await cache.match(request);

  const fetchPromise = fetch(request)
    .then((networkResponse) => {
      // On évite de cacher les réponses opaques qui ne sont pas utiles partout
      if (networkResponse && networkResponse.ok) {
        cache.put(request, networkResponse.clone()).catch(() => {});
      }
      return networkResponse;
    })
    .catch(() => null);

  // Renvoie le cache en priorité (rapide), puis met à jour en arrière-plan
  return cached || (await fetchPromise) || new Response("", { status: 504, statusText: "Gateway Timeout" });
}
