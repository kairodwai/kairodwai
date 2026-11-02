const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': p.endsWith('.html') ? 'text/html; charset=utf-8' : p.endsWith('.js') ? 'text/javascript' : 'image/jpeg' }); r.end(d); }); }).listen(8097);
const PAGES = { Main: '/', Brand: '/toyota/', Province: '/chiang-mai/', Portfolio: '/portfolio/', Finance: '/finance/', Docs: '/documents/', Privacy: '/privacy/' };
(async () => {
  const b = await chromium.launch(); const out = {};
  const p = await (await b.newContext({ viewport: { width: 390, height: 900 } })).newPage();
  await p.route(/fonts\./, r => r.abort());
  for (const [k, u] of Object.entries(PAGES)) { await p.goto('http://localhost:8097' + u); await p.waitForFunction(() => document.documentElement.classList.contains('dc-ready')); out[k] = await p.evaluate(() => document.getElementById('root').innerHTML); }
  fs.writeFileSync(path.join(__dirname, '..', 'site-src/prerender.json'), JSON.stringify(out));
  console.log(Object.entries(out).map(([k, v]) => k + ':' + v.length).join(' '));
  await b.close(); srv.close();
})();
