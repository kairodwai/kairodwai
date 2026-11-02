// รูปแนบข้อความทักทายเพื่อนใหม่ใน LINE OA Manager (ชิ้นที่ 2 ต่อจากข้อความ) 1040x1040
// บอกคนที่มาจากเว็บให้กดปุ่มส่งข้อความที่เตรียมไว้ — node src/tools/greeting.js → src/line-page/greeting-send.png
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const OUT = path.join(__dirname, '..', 'line-page', 'greeting-send.png');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const html = `<!doctype html><meta charset="utf-8"><style>
html,body{margin:0}body{width:1040px;height:1040px;background:#fff;font-family:Loma,'Noto Sans Thai',sans-serif;color:#0B1A10;display:flex;flex-direction:column;box-sizing:border-box;padding:64px 64px 56px;position:relative}
.top{display:flex;align-items:center;gap:24px}
.top img{width:96px;height:96px}
.top h1{font-size:44px;line-height:1.2;margin:0;font-weight:700}
.top h1 small{display:block;font-size:30px;font-weight:400;color:#3F4A44;margin-top:6px}
.bar{margin-top:56px;display:grid;grid-template-columns:56px 1fr 96px;align-items:center;gap:20px;background:#E9EBEF;border-radius:32px;padding:28px 28px 28px 24px}
.ic{color:#555;font-size:40px;text-align:center}
.inp{background:#fff;border-radius:40px;padding:22px 30px;font-size:30px;line-height:1.45;color:#222;white-space:pre-line}
.send{width:96px;height:96px;border-radius:50%;background:#fff;display:grid;place-items:center;box-shadow:0 0 0 8px #E53935}
.arrow{position:absolute;right:110px;top:640px;width:300px;height:230px}
.cta{margin-top:40px;font-size:44px;font-weight:700;color:#E53935;line-height:1.25}
.cta b{display:block;font-size:30px;font-weight:400;color:#0B1A10;margin-top:10px}
.foot{margin-top:auto;font-size:26px;color:#3F4A44;line-height:1.45;border-top:2px solid #E6E8E6;padding-top:24px}
.foot b{color:#0B1A10}
</style><body>
<div class="top"><img src="${logo}"><h1>กรอกข้อมูลรถจากเว็บมาแล้ว?<small>เหลือแค่กดส่งข้อความที่เตรียมไว้ให้</small></h1></div>
<div class="bar"><span class="ic">☰</span><div class="inp">กรุณากดปุ่มส่งข้อความทางขวามือ
ระบบจะส่งข้อมูลรถของคุณที่ลงไว้
(รหัส KR-1xxx)</div><span class="send"><svg width="66" height="66" viewBox="0 0 24 24"><path d="M5 5.5 L20 12 L5 18.5 Z" fill="#3B7DE8" stroke="#3B7DE8" stroke-width="3" stroke-linejoin="round"/><path d="M5 12 H11.5" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/></svg></span></div>
<div class="cta">กดปุ่มส่ง 1 ครั้ง ก็เสร็จ<b>ทีมงานได้รับข้อมูลรถของคุณ และเริ่มประเมินราคาทันที</b></div>
<svg class="arrow" viewBox="0 0 300 230" fill="none"><defs><marker id="h" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0 0 L6 3 L0 6 z" fill="#E53935"/></marker></defs><path d="M40 16 C 50 110, 150 130, 215 205" stroke="#E53935" stroke-width="16" stroke-linecap="round" marker-end="url(#h)"/></svg>
<div class="foot">ยังไม่เคยกรอกข้อมูล? กดปุ่ม <b>"ส่งรูปรถ"</b> ด้านล่างแทน<br>ทีมงานตอบในแชทนี้ ทุกวัน 8:00–20:00</div>
</body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1040, height: 1040 } });
  await p.setContent(html); await p.waitForTimeout(200);
  await p.screenshot({ path: OUT });
  await b.close();
  console.log('wrote', OUT, fs.statSync(OUT).size, 'bytes');
})();
