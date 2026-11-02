// ทดสอบกรณีส่งฟอร์มไม่สำเร็จ (เน็ตหลุด / backend ตอบผิด) แล้วลองใหม่สำเร็จ
// node src/tools/fail.js  → shots/fail-*.png
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');  // repo root = built site
const MIME = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.png': 'image/png', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml' };
const srv = http.createServer((q, r) => { let p = decodeURIComponent(q.url.split('?')[0]); if (p.endsWith('/')) p += 'index.html'; fs.readFile(path.join(ROOT, p), (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { 'content-type': MIME[path.extname(p)] || 'application/octet-stream' }); r.end(d); }); }).listen(8095);
(async () => {
  fs.mkdirSync('shots', { recursive: true });
  const b = await chromium.launch();
  const errs = [];
  const p = await (await b.newContext({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 2 })).newPage();
  p.on('pageerror', e => errs.push(String(e)));
  let mode = 'abort', calls = 0;
  await p.route(/script\.google\.com/, r => {
    calls++;
    if (mode === 'abort') return r.abort('failed');
    if (mode === 'bad') return r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ ok: false, error: 'x' }) });
    r.fulfill({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify({ ok: true, t: 'abcdef0123456789abcd', ref: 'KR-2481' }) });
  });
  await p.addInitScript(() => { window.fbq = (...a) => (window.__fb = window.__fb || []).push(a); });
  await p.goto('http://localhost:8095/', { waitUntil: 'load' });
  await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300);
  const f = p.locator('form');
  await f.getByRole('button', { name: /รถพร้อมขายทันที/ }).click(); await p.waitForTimeout(150);
  const sels = p.locator('form select');
  await sels.nth(0).selectOption('2020'); await sels.nth(1).selectOption('Toyota'); await sels.nth(2).selectOption('Yaris ATIV');
  await p.waitForTimeout(100);
  if (await sels.count() > 4) await sels.nth(3).selectOption({ index: 1 });
  await sels.last().selectOption({ index: 3 });  // ไมล์อยู่ท้ายสุด
  await f.getByRole('button', { name: 'ต่อไป' }).click(); await p.waitForTimeout(150);
    await f.getByRole('button', { name: 'ต่อไป' }).click(); await p.waitForTimeout(150);
  await p.locator('form input').last().fill('0812345678');
  const txt = async () => (await f.innerText()).replace(/\s+/g, ' ');
  // 1) network failure
  await f.getByRole('button', { name: 'เลือกรูปรถของคุณ' }).click(); await p.waitForTimeout(700);
  await f.screenshot({ path: 'shots/fail-1-network.png' });
  const t1 = await txt();
  console.log('network fail → still on form:', t1.includes('เลือกรูปรถของคุณ') && !t1.includes('รหัสอ้างอิง'), '| message:', t1.includes('ส่งไม่สำเร็จ'), '| button enabled:', await f.getByRole('button', { name: 'เลือกรูปรถของคุณ' }).isEnabled());
  // 2) backend says ok:false
  mode = 'bad';
  await f.getByRole('button', { name: 'เลือกรูปรถของคุณ' }).click(); await p.waitForTimeout(700);
  const t2 = await txt();
  console.log('ok:false → message:', t2.includes('ส่งไม่สำเร็จ'), '| not sent:', !t2.includes('รหัสอ้างอิง'));
  // 3) retry succeeds
  mode = 'ok';
  await f.getByRole('button', { name: 'เลือกรูปรถของคุณ' }).click(); await p.waitForTimeout(150);
  const leadCalls = p.evaluate(() => (window.__fb || []).filter(a => a[1] === 'Lead').length);
  await p.waitForURL(/\/line\//, { timeout: 5000 });
  console.log('retry ok → went to photos:', new URL(p.url()).pathname + new URL(p.url()).search);
  console.log('API calls:', calls, '| fbq Lead count before redirect:', await leadCalls, '| errors:', errs);
  await b.close(); srv.close();
})();
