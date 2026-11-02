const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); }).listen(8097);
(async () => {
  const b = await chromium.launch();
  for (const w of [390, 1280]) {
    const p = await (await b.newContext({ viewport: { width: w, height: 900 } })).newPage();
    await p.goto('http://localhost:8097/', { waitUntil: 'load' }); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
    const r = await p.evaluate(() => { const h = document.querySelector('header img'), f = document.querySelector('footer img'); const hb = h.getBoundingClientRect(), fb = f.getBoundingClientRect(); const hd = document.querySelector('header').getBoundingClientRect(); return { header: [hb.width.toFixed(1), hb.height.toFixed(1)], headerH: hd.height.toFixed(1), footer: [fb.width.toFixed(1), fb.height.toFixed(1)], fs: getComputedStyle(f).alignSelf }; });
    console.log(w, JSON.stringify(r));
    await p.context().close();
  }
  await b.close(); srv.close();
})();
