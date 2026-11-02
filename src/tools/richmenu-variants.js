// ลองแบบเมนูล่าง "รอประเมินราคา" หลายแบบ แล้วย่อเป็นขนาดจริงบนจอมือถือ (390pt) เทียบกัน
// node src/tools/richmenu-variants.js → shots/richmenu-A.png … + shots/richmenu-compare.png
const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
const logo = 'data:image/png;base64,' + fs.readFileSync(path.join(__dirname, '..', 'site-src', 'logo.png')).toString('base64');
const base = `html,body{margin:0}body{width:2500px;height:843px;font-family:Loma,'Noto Sans Thai',sans-serif;color:#0B1A10;display:grid;place-items:center;text-align:center;background:#fff}
.wrap{display:grid;justify-items:center}.logo{display:block;height:auto}`;
const V = {
  A: { css: `.logo{width:600px}.t1{font-size:136px;font-weight:700;line-height:1.15;margin:64px 0 0;display:flex;align-items:center;gap:40px}.t1 i{width:56px;height:56px;border-radius:50%;background:#06C755;display:inline-block}.t2{font-size:68px;line-height:1.3;color:#3F4A44;margin:32px 0 0}`,
       html: `<img class="logo" src="${logo}"><p class="t1"><i></i>ได้รับข้อมูลและรูปครบแล้ว</p><p class="t2">ทีมงานกำลังประเมินราคา จะตอบในแชทนี้ภายใน 5 นาที (8:00–20:00)</p>` },
  B: { css: `.logo{width:440px}.t1{font-size:144px;font-weight:700;line-height:1.15;margin:40px 0 0;display:flex;align-items:center;gap:40px}.t1 i{width:60px;height:60px;border-radius:50%;background:#06C755;display:inline-block}.t2{font-size:84px;line-height:1.25;color:#3F4A44;margin:24px 0 0}.t2 b{font-weight:600;color:#0B1A10}`,
       html: `<img class="logo" src="${logo}"><p class="t1"><i></i>ได้รับข้อมูลและรูปครบแล้ว</p><p class="t2">ทีมงานกำลังประเมินราคา<br>ตอบในแชทนี้<b>ภายใน 5 นาที</b> (8:00–20:00)</p>` },
  C: { css: `body{background:#E9F8EF}.card{background:#fff;border-radius:48px;padding:72px 120px;display:grid;justify-items:center;box-shadow:0 8px 40px rgba(11,26,16,.06)}.logo{width:440px}.t1{font-size:140px;font-weight:700;line-height:1.15;margin:40px 0 0;display:flex;align-items:center;gap:36px}.t1 svg{width:110px;height:110px}.t2{font-size:76px;line-height:1.3;color:#3F4A44;margin:24px 0 0}`,
       html: `<div class="card"><img class="logo" src="${logo}"><p class="t1"><svg viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="12" fill="#06C755"/><path d="M7 12.5l3.2 3.2L17 9" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>ได้รับข้อมูลและรูปครบแล้ว</p><p class="t2">ทีมงานกำลังประเมินราคา ตอบในแชทนี้ภายใน 5 นาที (8:00–20:00)</p></div>` },
};
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2500, height: 843 } });
  const imgs = [];
  for (const k of Object.keys(V)) {
    await p.setContent(`<!doctype html><meta charset="utf-8"><style>${base}${V[k].css}</style><body><div class="wrap">${V[k].html}</div></body>`); await p.waitForTimeout(150);
    const m = await p.evaluate(() => ['.wrap', '.t1', '.t2'].map(s => { const r = document.querySelector(s).getBoundingClientRect(); return s + ' y' + Math.round(r.y) + '-' + Math.round(r.y + r.height) + ' w' + Math.round(r.width) + ' cx' + Math.round(r.x + r.width / 2); }));
    console.log(k, m.join(' | '));
    const out = path.join(__dirname, '..', '..', 'shots', 'richmenu-' + k + '.png');
    await p.screenshot({ path: out }); imgs.push([k, 'data:image/png;base64,' + fs.readFileSync(out).toString('base64')]);
  }
  // แผ่นเทียบ: กว้าง 390pt เท่าจอ iPhone (ใส่แถบแชทจำลองด้านบนให้เห็นสัดส่วนจริง)
  const pg = await b.newPage({ viewport: { width: 390, height: 3 * 300 }, deviceScaleFactor: 3 });
  await pg.setContent(`<!doctype html><meta charset="utf-8"><style>body{margin:0;background:#eee;font-family:Loma,sans-serif}.ph{width:390px;background:#8CABD9;margin:0 0 12px;position:relative}.ph img{display:block;width:390px}.lbl{position:absolute;top:8px;left:8px;background:#0B1A10;color:#fff;font:600 13px/1 sans-serif;padding:6px 10px;border-radius:8px}.chat{height:120px;background:#8CABD9}</style><body>${imgs.map(([k, d]) => `<div class="ph"><div class="chat"></div><img src="${d}"><span class="lbl">แบบ ${k}</span></div>`).join('')}</body>`);
  await pg.waitForTimeout(200);
  await pg.screenshot({ path: path.join(__dirname, '..', '..', 'shots', 'richmenu-compare.png'), fullPage: true });
  await b.close(); console.log('done');
})();
