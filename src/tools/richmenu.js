// สร้างรูปเมนูล่าง "รอประเมินราคา" (rich menu รายคน หลังลูกค้าส่งรหัสจากเว็บแล้ว) 2500x843 (ขนาดมาตรฐานครึ่งจอของไลน์)
// node src/tools/richmenu.js  → src/site-src/richmenu-wait.png  (build จะ copy ไป /img/)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '..', 'site-src', 'richmenu-wait.png');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const html = `<!doctype html><meta charset="utf-8"><style>
html,body{margin:0}body{width:2500px;height:843px;background:#fff;font-family:Loma,'Noto Sans Thai',sans-serif;color:#0B1A10;display:grid;place-items:center;text-align:center}
.wrap{display:grid;justify-items:center;gap:36px}
.logo{width:300px;height:300px}
.t1{font-size:112px;font-weight:700;line-height:1.15;margin:0;display:flex;align-items:center;gap:36px}
.t1 i{width:48px;height:48px;border-radius:50%;background:#06C755;display:inline-block}
.t2{font-size:60px;line-height:1.4;color:#3F4A44;margin:0}
</style><body><div class="wrap"><img class="logo" src="${logo}"><p class="t1"><i></i>ได้รับข้อมูลและรูปครบแล้ว</p><p class="t2">ทีมงานกำลังประเมินราคา จะตอบในแชทนี้ภายใน 5 นาที (8:00–20:00)<br>ไม่ต้องกดอะไรเพิ่ม รอข้อความจากทีมงานได้เลย</p></div></body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2500, height: 843 } });
  await p.setContent(html); await p.waitForTimeout(200);
  await p.screenshot({ path: OUT });
  await b.close();
  console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
})();
