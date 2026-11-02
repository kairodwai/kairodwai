const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': p.endsWith('.html') ? 'text/html; charset=utf-8' : p.endsWith('.js') ? 'text/javascript' : 'image/jpeg' }); r.end(d); }); }).listen(8096);
(async () => {
  const b = await chromium.launch();
  for (const pg of ['/', '/toyota/', '/chiang-mai/']) {
  const p = await (await b.newContext({ viewport: { width: 390, height: 900 } })).newPage();
  await p.route(/fonts\./, r => r.abort());
  await p.goto('http://localhost:8096' + pg);
  await p.waitForTimeout(400);
  const t = await p.evaluate(() => document.body.innerText);
  console.log(pg, 'ไลน์ mentions:', (t.match(/[^\n]*ไลน์[^\n]*/g) || []).join(' | '));
  if (pg === '/') {
    await p.locator('header').screenshot({ path: 'shots/header.png' });
    const s = p.locator('form select'); await s.nth(0).selectOption('2020'); await s.nth(1).selectOption({ index: 3 }); await s.nth(2).selectOption('Honda'); await s.nth(3).selectOption('City');
    await p.locator('form').screenshot({ path: 'shots/step1.png' });
    await p.getByRole('button', { name: 'ต่อไป' }).click(); await p.waitForTimeout(100);
    await p.locator('form').screenshot({ path: 'shots/step2.png' });
  }
  }
  await b.close(); srv.close();
})();
