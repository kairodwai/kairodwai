// ทดสอบ gate: แตะ/กดสั้นไม่หลุด, กดค้าง 0.7 วิ → หน้าแดง, reload ยังแดง, ?kr=reset ล้าง — node src/tools/hold.js
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); }).listen(8094);
(async () => {
  const b = await chromium.launch(); const errs = [];
  const ctx = await b.newContext({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 2, hasTouch: true });
  const p = await ctx.newPage();
  p.on('pageerror', e => errs.push(String(e)));
  await p.addInitScript(() => { window.fbq = (...a) => (window.__fb = window.__fb || []).push(a); });
  await p.goto('http://localhost:8094/', { waitUntil: 'load' }); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
  const f = p.locator('form'); const hold = f.getByRole('button', { name: /แค่มาเช็คราคา/ });
  await f.screenshot({ path: 'shots/hold-0-gate.png' });
  const dlg = () => p.locator('[role=dialog]').count();
  // 1) plain tap
  await hold.tap(); await p.waitForTimeout(300);
  console.log('tap → dialog:', await dlg(), '| hint shown:', await f.locator('[aria-live]').count());
  // 2) short hold 0.8s
  const bb = await hold.boundingBox(); const cx = bb.x + bb.width / 2, cy = bb.y + bb.height / 2;
  await p.mouse.move(cx, cy); await p.mouse.down(); await p.waitForTimeout(300);
  await f.screenshot({ path: 'shots/hold-1-holding.png' });
  await p.mouse.up(); await p.waitForTimeout(200);
  console.log('0.3s hold → dialog:', await dlg(), '| hint shown:', await f.locator('[aria-live]').count());
  await f.screenshot({ path: 'shots/hold-2-hint.png' });
  // 3) full hold 2.2s
  await p.mouse.move(cx, cy); await p.mouse.down(); await p.waitForTimeout(900); await p.mouse.up(); await p.waitForTimeout(300);
  console.log('0.9s hold → dialog:', await dlg(), '| fbq:', JSON.stringify(await p.evaluate(() => (window.__fb || []).map(a => a[1]))));
  await p.screenshot({ path: 'shots/hold-3-red-m.png' });
  const d = p.locator('[role=dialog]');
  console.log('red text has phone/line?', /09\d|ไลน์|LINE|เปลี่ยนใจ/.test(await d.innerText()), '| scroll/client:', await d.evaluate(e => [e.scrollHeight, e.clientHeight]));
  // 4) reload → still red
  await p.reload({ waitUntil: 'load' }); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
  console.log('reload → dialog:', await dlg());
  // 5) other page also locked
  await p.goto('http://localhost:8094/toyota/', { waitUntil: 'load' }); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
  console.log('/toyota/ → dialog:', await dlg());
  // 6) reset
  await p.goto('http://localhost:8094/?kr=reset', { waitUntil: 'load' }); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
  console.log('?kr=reset → dialog:', await dlg(), '| gate visible:', await f.getByRole('button', { name: 'รถพร้อมขายใน 1-7 วันนี้' }).count());
  await ctx.close();
  // desktop red
  const p2 = await (await b.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 })).newPage();
  await p2.goto('http://localhost:8094/', { waitUntil: 'load' }); await p2.waitForSelector('html.dc-ready'); await p2.waitForTimeout(300);
  await p2.locator('form').screenshot({ path: 'shots/hold-4-gate-d.png' });
  const h2 = p2.locator('form').getByRole('button', { name: /แค่มาเช็คราคา/ }); const b2 = await h2.boundingBox();
  await p2.mouse.move(b2.x + b2.width / 2, b2.y + b2.height / 2); await p2.mouse.down(); await p2.waitForTimeout(2200); await p2.mouse.up(); await p2.waitForTimeout(300);
  await p2.screenshot({ path: 'shots/hold-5-red-d.png' });
  console.log('desktop → dialog:', await p2.locator('[role=dialog]').count());
  // short phone (640 tall) — scrollable, not clipped
  const p3 = await (await b.newContext({ viewport: { width: 360, height: 640 }, deviceScaleFactor: 2 })).newPage();
  await p3.goto('http://localhost:8094/', { waitUntil: 'load' }); await p3.waitForSelector('html.dc-ready'); await p3.waitForTimeout(300);
  const h3 = p3.locator('form').getByRole('button', { name: /แค่มาเช็คราคา/ }); await h3.scrollIntoViewIfNeeded(); const b3 = await h3.boundingBox();
  await p3.mouse.move(b3.x + b3.width / 2, b3.y + b3.height / 2); await p3.mouse.down(); await p3.waitForTimeout(2200); await p3.mouse.up(); await p3.waitForTimeout(300);
  await p3.screenshot({ path: 'shots/hold-6-red-short.png' });
  console.log('short phone scroll/client:', await p3.locator('[role=dialog]').evaluate(e => [e.scrollHeight, e.clientHeight]));
  console.log('errors', errs); await b.close(); srv.close();
})();
