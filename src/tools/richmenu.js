// สร้างรูปเมนูล่าง "รอประเมินราคา" (rich menu รายคน หลังลูกค้าส่งรหัสจากเว็บแล้ว) 1200x405
// node src/tools/richmenu.js  → src/site-src/richmenu-wait.png  (build จะ copy ไป /img/)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '..', 'site-src', 'richmenu-wait.png');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const html = `<!doctype html><meta charset="utf-8"><style>
html,body{margin:0}body{width:1200px;height:405px;background:#fff;font-family:Loma,'Noto Sans Thai',sans-serif;color:#0B1A10;display:flex;align-items:center;gap:48px;padding:0 72px;box-sizing:border-box}
.logo{width:160px;height:160px;flex:none}
.t1{font-size:54px;font-weight:700;line-height:1.2;margin:0 0 16px}
.t2{font-size:31px;line-height:1.45;color:#3F4A44;margin:0;white-space:nowrap}
.dot{display:inline-block;width:22px;height:22px;border-radius:50%;background:#06C755;margin-right:16px;vertical-align:middle}
</style><body><img class="logo" src="${logo}"><div><p class="t1"><span class="dot"></span>ได้รับข้อมูลและรูปครบแล้ว</p><p class="t2">ทีมงานกำลังประเมินราคา จะตอบในแชทนี้ภายใน 5 นาที<br>เวลา 8:00–20:00 · ไม่ต้องกดอะไรเพิ่ม รอข้อความจากทีมงานได้เลย</p></div></body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 405 } });
  await p.setContent(html); await p.waitForTimeout(200);
  await p.screenshot({ path: OUT });
  await b.close();
  console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
})();
