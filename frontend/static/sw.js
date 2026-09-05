const CACHE_NAME = "huugiau-v1";
const STATIC_ASSETS = [
  "/",
  "/static/css/site_theme.css",
  "/static/js/base_interactions.js",
  "/static/js/site_interactions.js",
  "/static/manifest.json"
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== "GET") return;

  if (url.pathname.startsWith("/api/")) {
    event.respondWith(fetch(request));
    return;
  }

  if (
    url.pathname.startsWith("/static/") ||
    url.pathname === "/manifest.json" ||
    url.pathname === "/robots.txt" ||
    url.pathname === "/sitemap.xml"
  ) {
    event.respondWith(
      caches.match(request).then((cached) => cached || fetch(request).then((resp) => {
        if (resp.ok) {
          const clone = resp.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, clone)).catch(() => {});
        }
        return resp;
      }))
    );
    return;
  }

  // Trang HTML: luôn lấy mới từ mạng, KHÔNG lưu cache (tránh giữ
  // thông tin giỏ hàng/thanh toán/tài khoản trong bộ nhớ trình duyệt).
  // Chỉ dùng cache làm fallback khi mất mạng (trang chủ đã precache).
  event.respondWith(fetch(request).catch(() => caches.match(request)));
});

self.addEventListener("push", (event) => {
  if (!event.data) return;
  const data = event.data.json();
  const options = {
    body: data.body || "Thông báo mới từ HUUGIAU",
    icon: "/static/icons/icon-192.png",
    badge: "/static/icons/badge-72.png",
    data: { url: data.url || "/" },
    actions: [{ action: "open", title: "Mở ứng dụng" }]
  };
  event.waitUntil(self.registration.showNotification(data.title || "HUUGIAU", options));
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data?.url || "/";
  event.waitUntil(clients.matchAll({ type: "window" }).then((clientList) => {
    for (const client of clientList) {
      if (client.url === url && "focus" in client) return client.focus();
    }
    return clients.openWindow(url);
  }));
});
