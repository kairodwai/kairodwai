// พรีวิวการ์ด Flex ฝั่งลูกค้า (nudgeFlex + การ์ดรูปครบ) แบบจำลองหน้าตาในแชท LINE ขนาดจอมือถือ
// node src/tools/flex-preview.js → shots/flex-preview.png
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const sum = 'มีเล่มพร้อมขาย · พร้อมขายทันที (1-7 วัน) · โทร 096-117-7117';
const html = `<!doctype html><meta charset="utf-8"><style>
body{margin:0;width:390px;background:#8CABD9;font-family:'Noto Sans Thai',Loma,sans-serif;color:#111;padding:12px 0}
.row{display:flex;gap:8px;padding:0 10px;margin:0 0 14px}.av{width:34px;height:34px;border-radius:50%;background:#111;display:grid;place-items:center;flex:none}.av img{width:22px}
.bub{background:#fff;border-radius:14px;width:300px;overflow:hidden}
.body{padding:20px;display:grid;grid-template-columns:minmax(0,1fr);gap:14px;font-size:15px;line-height:1.5}.body b{font-weight:700}.sum{font-size:13px;color:#5B6660}
.foot{padding:0 16px 16px}.btn{height:44px;border-radius:8px;background:#06C755;color:#fff;font-weight:600;font-size:15px;display:grid;place-items:center}
.hd{background:#06C755;color:#fff;padding:16px 20px}.hd h3{margin:0;font-size:17px}.hd p{margin:4px 0 0;font-size:12px;opacity:.9}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:6px}.ph{aspect-ratio:4/3;background:#cfd6d2;border-radius:6px}.ph.w{grid-column:1/-1;aspect-ratio:16/9}
.t{font-size:12px;color:#5B6660;text-align:center;margin:0 0 6px}
</style><body>
<p class="t">แชท LINE OA — การ์ดทัก (กรอกแล้ว ปิดหน้ารูปไป 1 นาที)</p>
<div class="row"><div class="av"><img src="${logo}"></div><div class="bub">
  <div class="body"><div>คุณ mOs ต้องการจะขาย <b>Hyundai Kona Electric SEL ปี 2022 ไมล์ 50,000 – 60,000 กม.</b></div>
  <div class="sum">${sum}</div>
  </div>
  <div class="foot"><div class="btn">อัพโหลดรูปรถของคุณ เพื่อประเมินราคา</div></div>
</div></div>
<p class="t">การ์ดตอนรูปครบ</p>
<div class="row"><div class="av"><img src="${logo}"></div><div class="bub">
  <div class="hd"><h3>ได้รับข้อมูลและรูปครบแล้ว</h3><p>กำลังประเมินราคา กรุณารอสักครู่ ทีมงานจะตอบในแชทนี้ภายใน 5 นาที (8:00–20:00)</p></div>
  <div class="body" style="gap:8px"><div style="font-size:14px"><b>Hyundai Kona Electric SEL ปี 2022 · KR-1015</b></div>
  <div class="sum" style="font-size:12px">${sum}</div>
  <div class="grid"><div class="ph"></div><div class="ph"></div><div class="ph"></div><div class="ph"></div><div class="ph w"></div></div></div>
</div></div>
</body>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 3 });
  await p.setContent(html); await p.waitForTimeout(200);
  const out = path.join(__dirname, '..', '..', 'shots', 'flex-preview.png');
  await p.screenshot({ path: out, fullPage: true }); await b.close(); console.log('wrote', out);
})();
