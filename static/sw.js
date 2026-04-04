const CACHE_NAME = "nawab-urduverse-v2";
const OFFLINE_URL = "/static/offline.html";
const APP_SHELL = [
    "/",
    "/static/manifest.json",
    "/static/offline.html",
    "/static/css/style.css",
    "/static/css/premium-ui.css",
    "/static/css/dark-mode.css",
    "/static/js/main.js",
    "/static/js/premium-ui.js",
    "/static/images/nawab-logo.png",
    "/static/images/pwa-icon-192.png",
    "/static/images/pwa-icon-512.png"
];

self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", (event) => {
    event.waitUntil(
        caches.keys().then((keys) =>
            Promise.all(
                keys
                    .filter((key) => key !== CACHE_NAME)
                    .map((key) => caches.delete(key))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", (event) => {
    if (event.request.method !== "GET") return;

    const requestUrl = new URL(event.request.url);
    const isSameOrigin = requestUrl.origin === self.location.origin;
    const isStaticAsset = isSameOrigin && requestUrl.pathname.startsWith("/static/");

    if (event.request.mode === "navigate") {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
                    return response;
                })
                .catch(async () => {
                    const cachedPage = await caches.match(event.request);
                    if (cachedPage) return cachedPage;
                    return caches.match(OFFLINE_URL);
                })
        );
        return;
    }

    if (isStaticAsset) {
        event.respondWith(
            caches.match(event.request).then((cachedResponse) => {
                if (cachedResponse) return cachedResponse;

                return fetch(event.request).then((response) => {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
                    return response;
                });
            })
        );
    }
});
