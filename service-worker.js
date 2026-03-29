const CACHE_NAME = 'arthsetu-v1';
const urlsToCache = [
  '/',
  '/api/health',
  '/api/market/ticker',
  '/api/market/recommendations',
  '/api/sectors'
];

// Install event
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
      .catch(err => console.log('Cache install error:', err))
  );
});

// Activate event
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - Network first, fallback to cache
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone the response
        const responseClone = response.clone();
        
        // Cache the response for future use
        caches.open(CACHE_NAME)
          .then(cache => {
            cache.put(event.request, responseClone);
          });
        
        return response;
      })
      .catch(err => {
        // If fetch fails, try to get from cache
        return caches.match(event.request)
          .then(response => {
            if (response) {
              return response;
            }
            // If not in cache, return a fallback page
            return new Response('Offline - No cached response available', {
              status: 503,
              statusText: 'Service Unavailable'
            });
          });
      })
  );
});
