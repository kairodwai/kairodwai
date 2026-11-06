// รูปแชร์ (og:image) แยกต่อหน้า 1200×630: รูปหลักของเว็บ + แถบชื่อหน้า — แชร์ลิงก์หน้า Honda ใน LINE/Facebook ก็ขึ้นว่า "รับซื้อรถ Honda"
// ใช้: node src/tools/og.js → img/og/<slug>.jpg (รันเมื่อเพิ่ม/เปลี่ยนชื่อหน้า; build ใช้ไฟล์นี้ถ้ามี)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..', '..');
const pages = JSON.parse(fs.readFileSync(path.join(ROOT, 'src/site-src/pages.json'), 'utf8'));
const b64 = f => fs.readFileSync(path.join(ROOT, f)).toString('base64');
const photo = 'data:image/jpeg;base64,' + b64('src/site-src/og.jpg');
const F = (w, sub) => `@font-face{font-family:K;font-weight:${w};src:url(data:font/woff2;base64,${b64('src/site-src/fonts/kanit-' + sub + '-' + w + '-normal.woff2')}) format('woff2')}`;
const FONTS = F(500, 'latin') + F(700, 'latin') + F(500, 'thai') + F(700, 'thai');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 } });
  fs.mkdirSync(path.join(ROOT, 'img/og'), { recursive: true });
  for (const [name, url] of Object.entries(pages)) {
    if (url === '/' || name === 'Portfolio') continue;
    const html = fs.readFileSync(path.join(ROOT, url.replace(/^\//, ''), 'index.html'), 'utf8');
    const h1 = (html.match(/<h1[^>]*>([\s\S]*?)<\/h1>/) || [, ''])[1].split(/<br[^>]*>/).map(x => x.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim()).filter(Boolean);
    await p.setContent(`<style>${FONTS}
      body{margin:0;width:1200px;height:630px;overflow:hidden;font-family:K;background:#141414;display:flex}
      .ph{width:560px;height:630px;flex-shrink:0;background:url(${photo}) 42% center/auto 630px}
      .band{flex:1;display:flex;flex-direction:column;justify-content:center;gap:22px;padding:0 56px;box-sizing:border-box}
      h1{margin:0;color:#F5F4F0;font-weight:700;font-size:60px;line-height:1.18}h1 span{display:block;white-space:nowrap}
      .s{color:#B9B5AC;font-weight:500;font-size:26px;line-height:1.5}.s b{color:#06C755;font-weight:700;font-size:34px}</style>
      <div class="ph"></div><div class="band"><h1>${h1.map(x => '<span>' + x + '</span>').join('')}</h1><div class="s"><b>ขายรถไว</b><br>ทีมไปดูรถถึงบ้าน · kairodwai.com</div></div>`);
    await p.evaluate(async () => { await document.fonts.ready; const h = document.querySelector('h1'), max = h.parentElement.clientWidth - 112; let f = 60; while (f > 36 && [...h.children].some(c => c.scrollWidth > max)) { f -= 2; h.style.fontSize = f + 'px'; } }); await p.waitForTimeout(100);
    const slug = url.replace(/\//g, '') || 'home';
    await p.screenshot({ path: path.join(ROOT, 'img/og', slug + '.jpg'), type: 'jpeg', quality: 82 });
    console.log(slug, '|', h1.join(' / '));
  }
  await b.close();
})();
