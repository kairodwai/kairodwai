/* ขายรถไว — service worker: มีไว้ให้ Chrome ติดตั้งเว็บเป็นแอปจริงบนมือถือ (WebAPK) เท่านั้น
   ไม่เก็บแคชอะไร ทุกคำขอวิ่งไปเน็ตตามปกติ (เว็บอัปเดตทันทีทุกครั้ง) */
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});
