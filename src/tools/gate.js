const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); }).listen(8099);
(async () => {
  const b = await chromium.launch();
  const errs = [], tracked = [];
  const run = async (width, tag) => {
    const p = await (await b.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 2 })).newPage();
    p.on('pageerror', e => errs.push(tag + ': ' + e));
    let posted = null;
    await p.route(/script\.google\.com/, r => { posted = r.request().postData(); r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ ok: true, t: 'abcdef0123456789abcd', ref: 'KR-2481' }) }); });
    await p.addInitScript(() => { window.fbq = (...a) => (window.__fb = window.__fb || []).push(a); });
    await p.goto('http://localhost:8099/', { waitUntil: 'load' });
    await p.waitForSelector('html.dc-ready');
    await p.waitForTimeout(400);
    const f = p.locator('form');
    await p.screenshot({ path: `shots/${tag}-0-top.png` });
    await f.screenshot({ path: `shots/${tag}-1-gate.png` });
    // "แค่มาเช็คราคา" ต้องกดค้าง 0.7 วิ — แตะเฉยๆ ต้องไม่หลุดออก (ทดสอบเต็มใน hold.js)
    await f.getByRole('button', { name: /แค่มาเช็คราคา/ }).click();
    await p.waitForTimeout(150);
    console.log(tag, 'tap on just-checking stays on gate:', await p.locator('[role=dialog]').count() === 0, '| hint elements:', await f.locator('[aria-live]').count());
    await f.screenshot({ path: `shots/${tag}-2-gate-hint.png` });
    // ready → form step 1
    await f.getByRole('button', { name: 'รถพร้อมขายทันที (ภายใน 1-7 วันนี้)' }).click();
    await p.waitForTimeout(150);
    await f.screenshot({ path: `shots/${tag}-3-step1.png` });
    const sels = p.locator('form select');
    await sels.nth(0).selectOption('2020'); await sels.nth(1).selectOption('Toyota'); await sels.nth(2).selectOption('Yaris ATIV');
    await p.waitForTimeout(100);
    if (await sels.count() > 4) await sels.nth(3).selectOption({ index: 1 });
    await sels.last().selectOption({ index: 3 });  // ไมล์อยู่ท้ายสุด
    await f.getByRole('button', { name: 'ต่อไป' }).click(); await p.waitForTimeout(150);
    await f.screenshot({ path: `shots/${tag}-4-step2.png` });
        await f.getByRole('button', { name: 'ต่อไป' }).click(); await p.waitForTimeout(150);
    await f.screenshot({ path: `shots/${tag}-5-step3.png` });
    await p.locator('form input').last().fill('0812345678');
    await f.getByRole('button', { name: 'ยืนยัน' }).click(); await p.waitForURL(/\/line\//, { timeout: 5000 }); await p.waitForTimeout(300);
    await p.screenshot({ path: `shots/${tag}-6-photos.png` });
    console.log(tag, 'posted when:', posted && JSON.parse(posted).when, '| after ขอราคา → url:', new URL(p.url()).pathname + new URL(p.url()).search);
    await p.goBack(); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
    console.log(tag, 'header logo:', await p.locator('header img[src="/img/logo.png"]').evaluate(i => i.naturalWidth + 'x' + i.naturalHeight + ' css ' + i.getBoundingClientRect().height.toFixed(1)), '| footer logo:', await p.locator('footer img').count(), '| LINE text:', (await p.locator('body').innerText()).includes('@kairodwai'));
    await p.context().close();
  };
  await run(390, 'm');
  await run(1280, 'd');
  console.log('errors', errs);
  await b.close(); srv.close();
})();
