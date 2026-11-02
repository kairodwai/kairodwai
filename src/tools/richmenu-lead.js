// เมนูล่างสถานะ "กรอกฟอร์มแล้ว ยังไม่ส่งรูป" (rich menu รายคน) 2500x843: ซ้าย 2/3 ข้อความเฉยๆ (กดไม่ได้), ขวา 1/3 ดำ "โทรหาเรา" ตำแหน่งเดียวกับเมนูปกติ
// node src/tools/richmenu-lead.js → src/site-src/richmenu-lead.png (build copy ไป /img/) แล้วรัน setupLeadMenu() ใน Apps Script
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '..', 'site-src', 'richmenu-lead.png');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const html = `<!doctype html><meta charset="utf-8"><style>
html,body{margin:0}body{width:2500px;height:843px;font-family:Loma,'Noto Sans Thai',sans-serif;display:grid;grid-template-columns:1667px 833px}
.l{background:#fff;color:#0B1A10;display:grid;place-items:center;text-align:center}
.l .wrap{display:grid;justify-items:center}
.logo{width:400px;height:auto;display:block}
.t1{font-size:120px;font-weight:700;line-height:1.2;margin:40px 0 0;display:flex;align-items:center;gap:36px}
.t1 i{width:52px;height:52px;border-radius:50%;background:#06C755;display:inline-block}
.t2{font-size:76px;line-height:1.7;color:#3F4A44;margin:24px 0 0}
.r{background:#0B0F0D;color:#fff;display:grid;place-items:center;text-align:center}
.r .wrap{display:grid;justify-items:center;gap:28px}
.r svg{width:150px;height:150px}
.r b{font-size:118px;font-weight:700;line-height:1.1;color:#B8F2CD}
.r span{font-size:80px;line-height:1.2;color:#fff}
</style><body>
<div class="l"><div class="wrap"><img class="logo" src="${logo}"><p class="t1"><i></i>รอรูปรถของคุณ</p><p class="t2">กดปุ่มเขียวในแชท เพื่ออัพโหลดรูปรถ</p></div></div>
<div class="r"><div class="wrap"><svg viewBox="0 0 24 24" fill="none" stroke="#B8F2CD" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.9.6 2.8.7a2 2 0 0 1 1.8 2z"/></svg><b>โทรหาเรา</b><span>8:00–20:00</span></div></div>
</body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2500, height: 843 } });
  await p.setContent(html); await p.waitForTimeout(200);
  const m = await p.evaluate(() => ['.l .wrap', '.t1', '.t2', '.r .wrap'].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [s, Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), 'cx=' + Math.round(r.x + r.width / 2), 'cy=' + Math.round(r.y + r.height / 2)]; }));
  console.log(m);
  await p.screenshot({ path: OUT });
  await b.close();
  console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
})();
