// สร้างรูปเมนูล่าง "รอประเมินราคา" (rich menu รายคน หลังลูกค้าส่งรูปครบ) 2500x843 (ขนาดมาตรฐานครึ่งจอของไลน์)
// node src/tools/richmenu.js  → src/site-src/richmenu-wait.png  (build จะ copy ไป /img/)  แล้วรัน setupWaitMenu() ใน Apps Script
// บนมือถือ 2500px ≈ กว้างจอ (~390pt) → ตัวอักษร 144px ≈ 22pt, 84px ≈ 13pt (แบบ B ที่ Moss เคาะ 2 พ.ย.; ภาษาไทยต้อง line-height ≥1.7 ไม่งั้นสระ/วรรณยุกต์ชนกัน)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '..', 'site-src', 'richmenu-wait.png');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const html = `<!doctype html><meta charset="utf-8"><style>
html,body{margin:0}body{width:2500px;height:843px;background:#fff;font-family:Loma,'Noto Sans Thai',sans-serif;color:#0B1A10;display:grid;place-items:center;text-align:center}
.wrap{display:grid;justify-items:center;gap:0}
.logo{width:440px;height:auto;display:block}
.t1{font-size:144px;font-weight:700;line-height:1.15;margin:40px 0 0;display:flex;align-items:center;gap:40px}
.t1 i{width:60px;height:60px;border-radius:50%;background:#06C755;display:inline-block}
.t2{font-size:84px;line-height:1.7;color:#3F4A44;margin:36px 0 0}.t2 b{font-weight:600;color:#0B1A10}
</style><body><div class="wrap"><img class="logo" src="${logo}"><p class="t1"><i></i>ได้รับข้อมูลและรูปครบแล้ว</p><p class="t2">ทีมงานกำลังประเมินราคา<br>ตอบในแชทนี้<b>ภายใน 5 นาที</b> (8:00–20:00)</p></div></body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2500, height: 843 } });
  await p.setContent(html); await p.waitForTimeout(200);
  const m = await p.evaluate(() => ['.wrap', '.logo', '.t1', '.t2'].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return [s, Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), 'cx=' + Math.round(r.x + r.width / 2)]; }));
  console.log(m);
  await p.screenshot({ path: OUT });
  await b.close();
  console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
})();
