// ตรวจ SEO/GEO ทุกหน้าของเว็บ (build ใน repo) ทั้งแบบ "HTML ดิบ" (ที่บอท AI / Bing บางตัวเห็น เพราะไม่รัน JS) และแบบ "หลังรัน JS" (ที่ Googlebot เห็น)
// ใช้: (cd <repo> && python3 -m http.server 8090 &) ; node src/tools/seo-audit.js [http://localhost:8090] → shots/seo-audit.json + สรุปบนจอ
const { chromium, devices } = require('playwright');
const fs = require('fs'), path = require('path');
const BASE = process.argv[2] || 'http://localhost:8090';
const ROOT = path.join(__dirname, '..', '..');
const INDEXABLE = ['/', '/toyota/', '/chiang-mai/', '/finance/', '/documents/', '/privacy/'];   // /portfolio/ = noindex จนกว่าจะมีรถที่ซื้อจริง
const NOINDEX = ['/line/', '/go/'];

const checks = []; const add = (group, name, pass, detail, count) => checks.push({ group, name, pass: !!pass, detail: detail || '', count: count || 0 });

(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ ...devices['iPhone 13'] });
  const pages = {};
  for (const p of INDEXABLE.concat(NOINDEX)) {
    const file = path.join(ROOT, p.replace(/^\//, ''), 'index.html');
    const raw = fs.readFileSync(fs.existsSync(file) ? file : path.join(ROOT, 'index.html'), 'utf8');
    const head = raw.split('</head>')[0];
    const bodyRaw = (raw.split(/<body[^>]*>/)[1] || '').replace(/<script[\s\S]*?<\/script>|<style[\s\S]*?<\/style>/g, '');
    const rawText = bodyRaw.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    const pg = await ctx.newPage();
    const errs = []; pg.on('pageerror', e => errs.push(String(e)));
    await pg.goto(BASE + p + '?audit=1', { waitUntil: 'networkidle', timeout: 45000 }).catch(e => errs.push(String(e)));
    await pg.waitForTimeout(800);
    const r = await pg.evaluate(() => {
      const q = s => [...document.querySelectorAll(s)];
      const meta = n => (document.querySelector(`meta[name="${n}"],meta[property="${n}"]`) || {}).content || '';
      const text = (document.body.innerText || '').replace(/\s+/g, ' ').trim();
      const imgs = q('img');
      return {
        lang: document.documentElement.lang, title: document.title, desc: meta('description'), robots: meta('robots'),
        canonical: (document.querySelector('link[rel=canonical]') || {}).href || '',
        ogTitle: meta('og:title'), ogImage: meta('og:image'), ogDesc: meta('og:description'), twitter: meta('twitter:card'),
        h1: q('h1').map(h => h.innerText.trim()).filter(Boolean), h2: q('h2').length,
        words: text.length, ld: q('script[type="application/ld+json"]').map(s => { try { const j = JSON.parse(s.textContent); return [].concat(j['@graph'] || j).map(x => x['@type']).join(','); } catch (e) { return 'INVALID'; } }),
        imgs: imgs.length, imgNoAlt: imgs.filter(i => !i.getAttribute('alt')).length, imgNoDim: imgs.filter(i => !(i.getAttribute('width') && i.getAttribute('height')) && !i.style.aspectRatio && !/aspect-ratio/.test(i.getAttribute('style') || '')).length,
        links: q('a[href]').map(a => a.getAttribute('href')), tel: q('a[href^="tel:"]').length,
        viewport: !!document.querySelector('meta[name=viewport]'), favicon: !!document.querySelector('link[rel~=icon]'),
        breadcrumbs: !!document.querySelector('[aria-label*=breadcrumb i], nav.breadcrumb, .breadcrumb'),
        faqHtml: /คำถามที่พบบ่อย|FAQ/i.test(text), nap: /0\d{1,2}[- ]?\d{3}[- ]?\d{4}/.test(text)
      };
    });
    pages[p] = { ...r, rawText: rawText.length, rawH1: (raw.match(/<h1/g) || []).length, rawLd: (raw.match(/application\/ld\+json/g) || []).length, errs };
    await pg.close();
  }
  await b.close();

  const idx = INDEXABLE.map(p => [p, pages[p]]);
  const titles = idx.map(([, r]) => r.title);
  add('Indexing', 'robots.txt exists and points to sitemap', /Sitemap:/.test(fs.readFileSync(path.join(ROOT, 'robots.txt'), 'utf8')), 'robots.txt', 1);
  const sm = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8'); const smUrls = [...sm.matchAll(/<loc>([^<]+)<\/loc>/g)].map(m => m[1].replace('https://kairodwai.com', ''));
  add('Indexing', 'Sitemap lists every indexable page', INDEXABLE.every(p => smUrls.includes(p)), smUrls.length + ' URLs', smUrls.length);
  add('Indexing', 'Sitemap has lastmod dates', /<lastmod>/.test(sm), 'no <lastmod>', smUrls.length);
  add('Indexing', 'Photo/LINE pages kept out of Google (noindex)', NOINDEX.every(p => /noindex/.test(pages[p].robots)), NOINDEX.join(' '), NOINDEX.length);
  add('Indexing', 'Canonical URL on every page', idx.every(([p, r]) => r.canonical === 'https://kairodwai.com' + p), '', idx.length);
  add('Content in HTML', 'Page text is in the HTML (not only after JavaScript)', idx.every(([, r]) => r.rawText > 300), idx.map(([p, r]) => p + ' ' + r.rawText + ' chars').join(' · '), idx.length);
  add('Content in HTML', 'H1 is in the HTML (AI bots that skip JS can see it)', idx.every(([, r]) => r.rawH1 === 1), idx.filter(([, r]) => r.rawH1 !== 1).map(([p]) => p).join(' '), idx.length);
  add('On-page', 'Exactly one H1 per page (after JS)', idx.every(([, r]) => r.h1.length === 1), idx.filter(([, r]) => r.h1.length !== 1).map(([p, r]) => p + '=' + r.h1.length).join(' '), idx.length);
  add('On-page', 'Every page has a unique title', new Set(titles).size === titles.length && titles.every(Boolean), '', idx.length);
  add('On-page', 'Title length 30–65 characters', idx.every(([, r]) => r.title.length >= 30 && r.title.length <= 65), idx.filter(([, r]) => r.title.length < 30 || r.title.length > 65).map(([p, r]) => p + '=' + r.title.length).join(' '), idx.length);
  add('On-page', 'Meta description 70–160 characters', idx.every(([, r]) => r.desc.length >= 70 && r.desc.length <= 160), idx.filter(([, r]) => r.desc.length < 70 || r.desc.length > 160).map(([p, r]) => p + '=' + r.desc.length).join(' '), idx.length);
  add('On-page', 'Page language set to Thai', idx.every(([, r]) => /^th/.test(r.lang)), '', idx.length);
  add('On-page', 'Images have alt text', idx.every(([, r]) => r.imgNoAlt === 0), idx.map(([p, r]) => p + ' ' + r.imgNoAlt + '/' + r.imgs).join(' · '), idx.reduce((s, [, r]) => s + r.imgs, 0));
  add('On-page', 'Thin content (fewer than 1,500 characters)', idx.every(([, r]) => r.words >= 1500), idx.filter(([, r]) => r.words < 1500).map(([p, r]) => p + ' ' + r.words).join(' · '), idx.length);
  add('Structured data', 'Structured data (JSON-LD) on pages', idx.every(([, r]) => r.ld.length > 0), idx.map(([p, r]) => p + ':' + (r.ld.join('|') || 'none')).join(' · '), idx.length);
  add('Structured data', 'Organization / LocalBusiness schema', idx.some(([, r]) => r.ld.some(t => /Organization|LocalBusiness|AutoDealer/.test(t))), '', 1);
  add('Structured data', 'FAQPage schema where page has FAQ', !idx.some(([, r]) => r.faqHtml) || idx.some(([, r]) => r.ld.some(t => /FAQPage/.test(t))), idx.filter(([, r]) => r.faqHtml).map(([p]) => p).join(' '), idx.filter(([, r]) => r.faqHtml).length);
  add('Structured data', 'BreadcrumbList on inner pages', idx.slice(1).every(([, r]) => r.ld.some(t => /BreadcrumbList/.test(t))), '', idx.length - 1);
  add('Social', 'Open Graph title + image on every page', idx.every(([, r]) => r.ogTitle && r.ogImage), '', idx.length);
  add('Mobile', 'Mobile viewport + favicon', idx.every(([, r]) => r.viewport && r.favicon), '', idx.length);
  add('Mobile', 'No JavaScript errors on load', Object.values(pages).every(r => !r.errs.length), Object.entries(pages).filter(([, r]) => r.errs.length).map(([p, r]) => p + ': ' + r.errs[0].slice(0, 80)).join(' · '), Object.keys(pages).length);
  const internal = new Set(); idx.forEach(([, r]) => r.links.forEach(l => { if (/^\/[^/]/.test(l) || l === '/') internal.add(l.split('?')[0].split('#')[0]); }));
  const broken = [...internal].filter(l => !fs.existsSync(path.join(ROOT, l.replace(/^\//, ''), l.endsWith('/') ? 'index.html' : '')) && !fs.existsSync(path.join(ROOT, l.replace(/^\//, ''))));
  add('Links', 'No broken internal links', broken.length === 0, broken.join(' '), internal.size);
  add('Links', 'Every indexable page linked from another page', INDEXABLE.slice(1).every(p => idx.some(([q, r]) => q !== p && r.links.some(l => l.split('?')[0] === p))), INDEXABLE.slice(1).filter(p => !idx.some(([q, r]) => q !== p && r.links.some(l => l.split('?')[0] === p))).join(' '), INDEXABLE.length - 1);
  add('Local', 'Phone number visible on pages (NAP)', idx.every(([, r]) => r.nap || r.tel), idx.filter(([, r]) => !(r.nap || r.tel)).map(([p]) => p).join(' '), idx.length);

  const out = { at: new Date().toISOString(), base: BASE, pages: Object.fromEntries(Object.entries(pages).map(([p, r]) => [p, { title: r.title, titleLen: r.title.length, descLen: r.desc.length, h1: r.h1, rawText: r.rawText, rawH1: r.rawH1, text: r.words, ld: r.ld, imgs: r.imgs, imgNoAlt: r.imgNoAlt, og: !!(r.ogTitle && r.ogImage), errs: r.errs.length }])), checks };
  fs.mkdirSync(path.join(ROOT, 'shots'), { recursive: true });
  fs.writeFileSync(path.join(ROOT, 'shots', 'seo-audit.json'), JSON.stringify(out, null, 1));
  for (const c of checks) console.log((c.pass ? 'PASS ' : 'FAIL ') + c.group.padEnd(16) + c.name + (c.detail ? '  — ' + c.detail : ''));
  console.log(checks.filter(c => c.pass).length + ' passed / ' + checks.filter(c => !c.pass).length + ' failed');
  for (const [p, r] of Object.entries(out.pages)) console.log(p.padEnd(13), 'title', r.titleLen, 'desc', r.descLen, 'h1', r.h1.length, 'text', r.text, 'raw', r.rawText, 'ld', r.ld.join('|') || '-', 'img', r.imgNoAlt + '/' + r.imgs);
})();
