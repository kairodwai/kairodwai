const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml', '.css': 'text/css', '.png': 'image/png', '.json': 'application/json' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; const f = path.join(ROOT, p); fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': types[path.extname(f)] || 'application/octet-stream' }); r.end(d); }); }).listen(8099);
(async () => {
  const pages = process.argv[2].split(',');
  const widths = (process.argv[3] || '390').split(',').map(Number);
  const b = await chromium.launch();
  for (const w of widths) for (const pg of pages) {
    const ctx = await b.newContext({ viewport: { width: w, height: 900 }, deviceScaleFactor: 1 });
    const p = await ctx.newPage(); const errs = [];
    p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); }); p.on('pageerror', e => errs.push(String(e)));
    await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.abort());
    await p.goto('http://localhost:8099' + pg, { waitUntil: 'load' });
    await p.waitForTimeout(600);
    const name = 'shots/' + (pg.replace(/\//g, '_') || '_') + '-' + w + '.png';
    await p.screenshot({ path: name, fullPage: true });
    const hgt = await p.evaluate(() => document.documentElement.scrollHeight);
    console.log(name, 'h=' + hgt, errs.slice(0, 5).join(' | '));
    await ctx.close();
  }
  await b.close(); srv.close();
})();
