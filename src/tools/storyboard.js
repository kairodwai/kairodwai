// storyboard flow แบบ LIFF (เปิดเว็บในไลน์ รู้ตัวตนตั้งแต่แรก) — ภาพประกอบเพื่อคุยกัน ไม่ใช่ของจริง
// node src/tools/storyboard.js → shots/storyboard-liff.png  (ต้องรัน gate.js และ photos-ready.js ก่อนให้มี shots/m-*.png, rv-*.png)
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const S = path.join(__dirname, '..', '..', 'shots');
const img = f => 'data:image/png;base64,' + fs.readFileSync(path.join(S, f)).toString('base64');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const bar = (t) => `<div class="lbar"><span>✕</span><b>${t}</b><span>⋮</span></div>`;
const bubble = (html, cls = '') => `<div class="bub ${cls}">${html}</div>`;
const html = `<!doctype html><meta charset="utf-8"><style>
body{margin:0;background:#F3F5F4;font-family:Loma,'Noto Sans Thai',sans-serif;color:#16201A;padding:40px 48px 48px;width:1480px;box-sizing:border-box}
h1{font-size:30px;margin:0 0 6px}.sub{color:#5B6660;font-size:17px;margin:0 0 28px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:28px 24px}
.step{display:grid;gap:12px;justify-items:center}
.ph{width:300px;height:560px;border-radius:28px;background:#fff;box-shadow:0 0 0 8px #16201A,0 12px 30px rgba(0,0,0,.18);overflow:hidden;position:relative;display:flex;flex-direction:column}
.ph img.shot{width:300px;display:block;object-fit:cover;object-position:top;flex:1;min-height:0}
.lbar{height:44px;background:#fff;border-bottom:1px solid #E3E6E3;display:grid;grid-template-columns:40px 1fr 40px;align-items:center;text-align:center;font-size:14px;flex:none}.lbar span{color:#555;font-size:18px}
.cap{width:300px;text-align:center}.cap b{display:block;font-size:17px;margin-bottom:2px}.cap span{font-size:13.5px;color:#5B6660;line-height:1.45}
.n{position:absolute;top:10px;left:10px;width:30px;height:30px;border-radius:50%;background:#06C755;color:#0B1A10;font-weight:700;display:grid;place-items:center;z-index:2;font-size:15px}
/* mocks */
.consent{padding:40px 22px;display:grid;gap:14px;justify-items:center;text-align:center;flex:1}
.consent img{width:72px;height:72px;border-radius:18px}.consent h3{margin:0;font-size:17px}.consent p{margin:0;font-size:13px;color:#5B6660}
.perm{width:100%;text-align:left;font-size:13px;display:grid;gap:8px;background:#F3F5F4;border-radius:12px;padding:12px}.perm div::before{content:'☑ ';color:#06C755}
.btn{width:100%;height:44px;border-radius:10px;background:#06C755;color:#fff;display:grid;place-items:center;font-weight:700;font-size:15px}.btn.g{background:none;color:#5B6660;font-weight:400}
.chat{flex:1;background:#8A98B8;padding:12px;display:flex;flex-direction:column;gap:10px;font-size:12.5px;overflow:hidden}
.bub{background:#fff;border-radius:14px;padding:10px 12px;max-width:86%;line-height:1.45;align-self:flex-start;box-shadow:0 1px 1px rgba(0,0,0,.08)}
.bub.card{padding:0;overflow:hidden;max-width:92%}.card .hd{background:#06C755;color:#fff;padding:10px 12px;font-weight:700}.card .hd small{display:block;font-weight:400;font-size:11px;opacity:.9}
.card .bd{padding:10px 12px;display:grid;gap:8px}.pics{display:grid;grid-template-columns:1fr 1fr;gap:6px}.pics i{display:block;aspect-ratio:4/3;background:#D9DED9;border-radius:6px}
.cbtn{margin-top:4px;border:1.5px solid #06C755;color:#0B7A36;border-radius:8px;text-align:center;padding:7px;font-weight:700}
.tbar{height:40px;background:#fff;border-top:1px solid #E3E6E3;display:grid;place-items:center;font-size:13px;color:#16201A;flex:none}
.team{background:#fff;font-family:ui-monospace,Consolas,monospace;font-size:11.5px;white-space:pre-line;padding:10px 12px;border-radius:12px;align-self:flex-start;max-width:92%;line-height:1.5}
.me{align-self:flex-end;background:#C8F5C8}
</style><body>
<h1>ถ้าเปิดเว็บ "ในไลน์" (LIFF) ลูกค้าจะเจออะไรบ้าง</h1>
<p class="sub">ภาพ 2-4 คือหน้าเว็บของจริงวันนี้ · ภาพ 1, 5, 6, 7 เป็นภาพจำลองหน้าตาในแอปไลน์ · ไม่มีขั้นไหนต้องพิมพ์รหัส กด Add LINE หรือกดส่งข้อความ</p>
<div class="grid">

<div class="step"><div class="ph"><div class="n">1</div>${bar('LINE')}<div class="consent"><img src="${logo}"><h3>ขายรถไว รับซื้อรถ</h3><p>ขอสิทธิ์เข้าถึงข้อมูลต่อไปนี้</p><div class="perm"><div>ชื่อและรูปโปรไฟล์</div><div>เพิ่ม "ขายรถไว รับซื้อรถ" เป็นเพื่อน</div></div><div class="btn">อนุญาต</div><div class="btn g">ยกเลิก</div></div></div>
<div class="cap"><b>กดโฆษณา → เด้งเปิดในไลน์</b><span>ครั้งแรกครั้งเดียว ไลน์ถาม 1 จอ กด "อนุญาต" = ระบบรู้ว่าเค้าคือใคร + เป็นเพื่อนกับเราทันที (ครั้งต่อไปไม่ถามอีก)</span></div></div>

<div class="step"><div class="ph"><div class="n">2</div>${bar('ขายรถไว รับซื้อรถ')}<img class="shot" src="${img('m-0-top.png')}"></div>
<div class="cap"><b>หน้าเว็บเดิม แต่อยู่ในไลน์</b><span>ปุ่ม "แอดไลน์" ไม่ต้องมีแล้ว (เป็นเพื่อนกันแล้ว) เหลือคำถามเดียว: พร้อมขายไหม</span></div></div>

<div class="step"><div class="ph"><div class="n">3</div>${bar('ขายรถไว รับซื้อรถ')}<img class="shot" src="${img('m-3-step1.png')}"></div>
<div class="cap"><b>ฟอร์ม 3 ขั้น เหมือนเดิม</b><span>ทุกอย่างที่กรอกผูกกับไลน์เค้าอัตโนมัติ เบอร์โทรยังขอไว้ให้ทีมโทร</span></div></div>

<div class="step"><div class="ph"><div class="n">4</div>${bar('ขายรถไว รับซื้อรถ')}<img class="shot" src="${img('rv-0.png')}"></div>
<div class="cap"><b>ถ่ายรูปรถ เหมือนเดิม</b><span>ครบแล้วหน้าเว็บปิดตัวเอง กลับไปที่แชทให้ (ไม่มีหน้า "กด Add LINE" อีกต่อไป)</span></div></div>

<div class="step"><div class="ph"><div class="n">5</div>${bar('ขายรถไว รับซื้อรถ')}<div class="chat">${bubble('สวัสดีครับคุณ mOs 🙏 ขายรถไว รับซื้อรถถึงบ้าน')}${bubble('<div class="hd">ได้รับข้อมูลและรูปครบแล้ว<small>กำลังประเมินราคา กรุณารอสักครู่ ทีมงานจะตอบในแชทนี้ภายใน 5 นาที (8:00–20:00)</small></div><div class="bd"><b>Honda City Hatchback 1.0 Turbo SV ปี 2022 · KR-1010</b><div class="pics"><i></i><i></i><i></i><i></i></div></div>', 'card')}</div><div class="tbar">รอประเมินราคา</div></div>
<div class="cap"><b>กลับมาที่แชท การ์ดรออยู่แล้ว</b><span>ไม่ต้องกดอะไร เมนูล่างเป็น "รอประเมินราคา" ทีมพิมพ์ตอบต่อในแชทนี้</span></div></div>

<div class="step"><div class="ph"><div class="n">6</div>${bar('ขายรถไว รับซื้อรถ')}<div class="chat">${bubble('คุณ mOs กรอกข้อมูล <b>Honda City Hatchback ปี 2022</b> ไว้แล้ว เหลือแค่รูปรถ 5 มุม (2 นาที) ทีมงานถึงจะประเมินราคาได้ครับ<div class="cbtn">ถ่ายรูปต่อ</div>')}${bubble('ยังไม่ได้รับรูปรถ KR-1010 ทีมงานจะโทรหาคุณวันนี้ หรือกดถ่ายรูปต่อได้เลย<div class="cbtn">ถ่ายรูปต่อ</div>')}</div><div class="tbar">📷 ส่งรูปรถ</div></div>
<div class="cap"><b>คนกรอกค้าง → บอททักเอง</b><span>2 ชม. และวันถัดไป ทางไลน์ ฟรี ไม่ใช้ SMS ไม่ต้องเก็บลิงก์ ไม่ต้อง Keep — กดปุ่มในแชทถ่ายต่อได้เลย</span></div></div>

<div class="step"><div class="ph"><div class="n">7</div>${bar('Kairodwai Report')}<div class="chat"><div class="team">Kairodwai Lead : KR-1010

Details : Honda City Hatchback 1.0 Turbo SV ปี 2022 ไมล์ 60,000 – 70,000 กม.
Status : ไม่ติดไฟแนนซ์
Call : 096-117-7117
LINE : mOs
Source : เว็บ · facebook
Photos : 5 รูป drive.google.com/…</div></div><div class="tbar">พิมพ์ข้อความ…</div></div>
<div class="cap"><b>กลุ่มทีมได้ข้อความเดียว</b><span>เพิ่มชื่อไลน์ลูกค้ามาด้วย เปิดแชท OA Manager ตอบได้เลย</span></div></div>

<div class="step"><div class="ph"><div class="n">8</div><div class="lbar" style="background:#F3F5F4"><span>⌂</span><b>kairodwai.com</b><span>⋮</span></div><img class="shot" src="${img('rv-1-ready.png')}"></div>
<div class="cap"><b>คนจาก Google / คอม</b><span>เว็บธรรมดายังอยู่ ใช้ flow แบบวันนี้ (Add LINE → กดส่งข้อความ) เป็นทางสำรอง</span></div></div>

</div></body>`;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1480, height: 1500 }, deviceScaleFactor: 1.5 });
  await p.setContent(html); await p.waitForTimeout(300);
  const out = path.join(S, 'storyboard-liff.png');
  await p.screenshot({ path: out, fullPage: true });
  await b.close(); console.log('wrote', out);
})();
