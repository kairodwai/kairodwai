#!/usr/bin/env python3
"""ข้อมูลหน้า Website Health Monitor ของ ขายรถไว: เช็คลิสต์ SEO/GEO + งานหลังบ้าน + roadmap
รวมกับผลตรวจจริงจาก shots/seo-audit.json (node src/tools/seo-audit.js) → shots/health.json
สถานะ: done = เสร็จ, partly = ทำบางส่วน, todo = ยังไม่เริ่ม · who: Claude / mOs / ทีม · check = ระบบตรวจเองทุก build
"""
import json, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
audit = json.load(open(os.path.join(ROOT, 'shots', 'seo-audit.json')))
A = {c['name']: c for c in audit['checks']}
def chk(name):  # สถานะจากผลตรวจจริง
    return 'done' if A[name]['pass'] else 'todo'

G = 'https://developers.google.com/search/docs/'
S = {
  'js': (G + 'crawling-indexing/javascript/javascript-seo-basics', 'Google: JavaScript SEO basics'),
  'ai': ('https://vercel.com/blog/the-rise-of-the-ai-crawler', 'Vercel: AI crawlers ไม่รัน JavaScript'),
  'lb': (G + 'appearance/structured-data/local-business', 'Google: LocalBusiness structured data'),
  'bc': (G + 'appearance/structured-data/breadcrumb', 'Google: Breadcrumb structured data'),
  'faq': ('https://developers.google.com/search/blog/2023/08/howto-faq-changes', 'Google: เลิกโชว์ FAQ rich result กับเว็บทั่วไป (2023)'),
  'sm': (G + 'crawling-indexing/sitemaps/build-sitemap', 'Google: Build a sitemap (lastmod)'),
  'title': (G + 'appearance/title-link', 'Google: Title links'),
  'snip': (G + 'appearance/snippet', 'Google: Meta description / snippets'),
  'help': (G + 'fundamentals/creating-helpful-content', 'Google: Helpful, reliable, people-first content'),
  'spam': (G + 'essentials/spam-policies', 'Google: Spam policies (scaled content, doorway pages)'),
  'rev': (G + 'appearance/structured-data/review-snippet', 'Google: Review snippet (ห้ามรีวิวตัวเอง)'),
  'gbp': ('https://support.google.com/business/answer/9157481', 'Google Business Profile: service-area business'),
  'gsc': ('https://support.google.com/webmasters/answer/9008080', 'Search Console: verify ownership'),
  'bing': ('https://www.bing.com/webmasters/help/getting-started-checklist-66a806de', 'Bing Webmaster: getting started'),
  'cwv': ('https://web.dev/articles/vitals', 'web.dev: Core Web Vitals'),
  'img': (G + 'appearance/google-images', 'Google: Image SEO best practices'),
  'canon': (G + 'crawling-indexing/consolidate-duplicate-urls', 'Google: Canonical URLs'),
  'robots': (G + 'crawling-indexing/robots/intro', 'Google: robots.txt'),
  'noindex': (G + 'crawling-indexing/block-indexing', 'Google: noindex'),
  'mobile': (G + 'crawling-indexing/mobile/mobile-sites-mobile-first-indexing', 'Google: Mobile-first indexing'),
  'links': (G + 'crawling-indexing/links-crawlable', 'Google: Crawlable links'),
  'og': ('https://ogp.me/', 'The Open Graph protocol'),
  'eeat': (G + 'fundamentals/creating-helpful-content#eat', 'Google: E-E-A-T'),
  'pdpa': ('https://www.pdpc.or.th/', 'PDPC (สคส.) — PDPA'),
  'pixel': ('https://www.facebook.com/business/help/952192354843755', 'Meta: Meta Pixel'),
  'gads': ('https://support.google.com/google-ads/answer/1722022', 'Google Ads: conversion tracking'),
  'ga4': ('https://support.google.com/analytics/answer/9304153', 'GA4: set up'),
  'kp': ('https://support.google.com/google-ads/answer/7337243', 'Google Ads: Keyword Planner'),
  'liff': ('https://developers.line.biz/en/docs/liff/overview/', 'LINE: LIFF overview'),
  'rm': ('https://developers.line.biz/en/docs/messaging-api/use-per-user-rich-menus/', 'LINE: per-user rich menu'),
  'flex': ('https://developers.line.biz/en/docs/messaging-api/using-flex-messages/', 'LINE: Flex Message'),
  'tbs': ('https://developer.thaibulksms.com/', 'Thaibulksms API'),
}

# (หมวด, ชื่องาน, สถานะ, ใคร, priority, ทำอะไร/รายละเอียด, source key, check)
ITEMS = [
 # ---------- Indexing ----------
 ('Indexing', 'robots.txt ชี้ไป sitemap', chk('robots.txt exists and points to sitemap'), 'Claude', 'P1', 'มีแล้ว ปิด /line/ ไม่ให้เก็บ', 'robots', True),
 ('Indexing', 'sitemap.xml มีทุกหน้าที่ควรติด Google', chk('Sitemap lists every indexable page'), 'Claude', 'P1', A['Sitemap lists every indexable page']['detail'], 'sm', True),
 ('Indexing', 'sitemap ใส่วันที่แก้ล่าสุด (lastmod)', chk('Sitemap has lastmod dates'), 'Claude', 'P2', 'ให้ build ใส่วันที่ commit ล่าสุดของแต่ละหน้า Google ใช้ lastmod ตัดสินว่าจะกลับมาเก็บใหม่เมื่อไหร่', 'sm', True),
 ('Indexing', 'หน้าส่งรูป /line/ และ /go/ ไม่ติด Google (noindex)', chk('Photo/LINE pages kept out of Google (noindex)'), 'Claude', 'P1', 'หน้าทำงาน ไม่ใช่หน้าเนื้อหา', 'noindex', True),
 ('Indexing', 'Canonical URL ถูกทุกหน้า', chk('Canonical URL on every page'), 'Claude', 'P1', '', 'canon', True),
 ('Indexing', 'ยืนยันเว็บใน Google Search Console + ส่ง sitemap', 'partly', 'mOs', 'P1', 'ยืนยันแล้ว (บัญชี tpvcar 5 พ.ย.) ส่ง sitemap แล้ว แต่ Google ยังดึงไม่ได้ (ปกติของเว็บใหม่ ส่งซ้ำได้)', 'gsc', False),
 ('Indexing', 'Bing Webmaster Tools (นำเข้าจาก Search Console)', 'todo', 'mOs', 'P2', 'Bing ป้อนข้อมูลให้ ChatGPT search / Copilot — import จาก GSC ได้ใน 1 คลิก', 'bing', False),
 ('Indexing', 'www.kairodwai.com ชี้มาที่เว็บหลัก', 'todo', 'mOs', 'P2', 'Cloudflare: CNAME www → kairodwai.github.io แล้ว GitHub Pages จะ redirect ให้เอง', 'canon', False),
 ('Indexing', 'Request indexing หน้าแรก + หน้าหลักใน GSC', 'todo', 'mOs', 'P2', 'หลังยืนยัน GSC แล้ว กด URL Inspection → Request indexing ทีละหน้า', 'gsc', False),

 # ---------- Content in HTML (prerender) ----------
 ('Content in HTML', 'เนื้อหาอยู่ใน HTML ตั้งแต่แรก (prerender)', chk('Page text is in the HTML (not only after JavaScript)'), 'Claude', 'P1', 'ตอนนี้ทุกหน้า HTML ดิบมีตัวหนังสือ 0 ตัว ข้อความโผล่หลังรัน JavaScript — Google รอ render ได้แต่ช้ากว่า ส่วนบอท AI (ChatGPT, Claude, Perplexity) ไม่รัน JS เลยเห็นหน้าว่าง เครื่องมือ prerender มีแล้วแค่ยังไม่เปิด', 'ai', True),
 ('Content in HTML', 'H1 อยู่ใน HTML ตั้งแต่แรก', chk('H1 is in the HTML (AI bots that skip JS can see it)'), 'Claude', 'P1', 'ได้มาพร้อม prerender', 'js', True),
 ('Content in HTML', 'ลิงก์ภายในเป็น <a href> ที่บอทตามได้โดยไม่ต้องรัน JS', 'done', 'Claude', 'P1', 'ได้มาพร้อม prerender', 'links', False),
 ('Content in HTML', 'ข้อมูลติดต่อ/เวลาทำการอยู่ใน HTML ดิบ', 'done', 'Claude', 'P2', 'เบอร์ + เวลา 8:00–20:00 อยู่ใน HTML ทุกหน้า', 'ai', False),

 # ---------- On-page ----------
 ('On-page', 'H1 หนึ่งตัวต่อหน้า', chk('Exactly one H1 per page (after JS)'), 'Claude', 'P1', '', 'title', True),
 ('On-page', 'Title ไม่ซ้ำกันทุกหน้า', chk('Every page has a unique title'), 'Claude', 'P1', '', 'title', True),
 ('On-page', 'Title ยาว 30–65 ตัวอักษร', chk('Title length 30–65 characters'), 'Claude', 'P2', A['Title length 30–65 characters']['detail'] or 'ผ่าน', 'title', True),
 ('On-page', 'Meta description 70–160 ตัวอักษร', chk('Meta description 70–160 characters'), 'Claude', 'P2', A['Meta description 70–160 characters']['detail'] or 'ผ่าน', 'snip', True),
 ('On-page', 'ภาษาหน้าเป็นไทย (lang="th")', chk('Page language set to Thai'), 'Claude', 'P1', '', 'mobile', True),
 ('On-page', 'รูปมี alt text', chk('Images have alt text'), 'Claude', 'P2', '', 'img', True),
 ('On-page', 'ไม่มีหน้าเนื้อหาบาง (ต่ำกว่า 1,500 ตัวอักษร)', chk('Thin content (fewer than 1,500 characters)'), 'Claude', 'P2', A['Thin content (fewer than 1,500 characters)']['detail'], 'help', True),
 ('On-page', 'Keyword หลักอยู่ใน title, H1 และย่อหน้าแรก', 'done', 'Claude', 'P2', 'ทำตามคำค้นจริงจาก Keyword Planner (287 คำ, 5 พ.ย.)', 'title', False),
 ('On-page', 'URL ภาษาอังกฤษสั้น อ่านออก', 'done', 'Claude', 'P3', '/toyota/ /chiang-mai/ /finance/ …', 'links', False),
 ('On-page', 'ไม่มีข้อความ placeholder ค้างบนเว็บจริง', 'done', 'Claude', 'P1', 'ส่วน placeholder ถูกตัดตอน build + gate กันไว้', 'help', False),

 # ---------- Structured data ----------
 ('Structured data', 'JSON-LD ทุกหน้า', chk('Structured data (JSON-LD) on pages'), 'Claude', 'P1', 'ตอนนี้ไม่มีเลยสักหน้า', 'lb', True),
 ('Structured data', 'AutoDealer/LocalBusiness แบบ service-area (ไม่มีหน้าร้าน)', chk('Organization / LocalBusiness schema'), 'Claude', 'P1', 'ชื่อ ขายรถไว · เบอร์ · เวลา 8:00–20:00 · areaServed · logo · sameAs (LINE OA) — ไม่ใส่ที่อยู่หน้าร้านถ้าไม่ให้ลูกค้าเข้ามา', 'lb', True),
 ('Structured data', 'BreadcrumbList หน้าย่อย', chk('BreadcrumbList on inner pages'), 'Claude', 'P2', '', 'bc', True),
 ('Structured data', 'FAQPage (เพื่อ AI ไม่ใช่เพื่อ rich result)', chk('FAQPage schema where page has FAQ'), 'Claude', 'P3', 'Google เลิกโชว์ FAQ rich result กับเว็บทั่วไปแล้ว ใส่ไว้ให้ AI อ่านคำถาม-คำตอบได้ง่าย ไม่ได้ดาวเพิ่ม', 'faq', True),
 ('Structured data', 'ไม่ใส่ AggregateRating ของตัวเอง', 'done', 'Claude', 'P1', 'Google ห้ามรีวิวที่ธุรกิจเขียนเองบน LocalBusiness — ไม่ใส่ดาวปลอม', 'rev', False),
 ('Structured data', 'Service schema (รับซื้อรถ, รับซื้อรถติดไฟแนนซ์)', 'done', 'Claude', 'P3', 'Service ทุกหน้าขาย + areaServed รายจังหวัด', 'lb', False),

 # ---------- Social ----------
 ('Social', 'Open Graph title + รูป ทุกหน้า', chk('Open Graph title + image on every page'), 'Claude', 'P2', 'แชร์ลง LINE/Facebook ขึ้นรูปสวย', 'og', True),
 ('Social', 'รูป og แยกต่อหน้า (Toyota/เชียงใหม่/ไฟแนนซ์)', 'todo', 'Claude', 'P3', 'ตอนนี้ทุกหน้าใช้รูปเดียวกัน', 'og', False),

 # ---------- Mobile & speed ----------
 ('Speed', 'Mobile viewport + favicon', chk('Mobile viewport + favicon'), 'Claude', 'P1', '', 'mobile', True),
 ('Speed', 'ไม่มี JavaScript error ตอนโหลด', chk('No JavaScript errors on load'), 'Claude', 'P1', '', 'js', True),
 ('Speed', 'รูปเป็น WebP + ขนาดพอดีจอ + lazy load', 'done', 'Claude', 'P1', 'หน้าแรก 839 KB → 347 KB (2 พ.ย.)', 'img', False),
 ('Speed', 'หน้าแรกโหลดครบใน 4G ช้า ≤ 3.5 วิ', 'done', 'Claude', 'P2', 'วัด 3.2 วิ (iPhone 13 + Slow 4G จำลอง)', 'cwv', False),
 ('Speed', 'Core Web Vitals จากผู้ใช้จริง (CrUX) ผ่าน', 'todo', 'mOs', 'P2', 'ต้องมีคนเข้าพอก่อน ดูใน Search Console → Core Web Vitals หลังยิงแอด ~28 วัน', 'cwv', False),
 ('Speed', 'ฟอนต์ไม่บล็อกการแสดงผล', 'partly', 'Claude', 'P3', 'ใช้ Google Fonts display=swap แล้ว ยังไม่ได้ preload/self-host', 'cwv', False),

 # ---------- Links ----------
 ('Links', 'ไม่มีลิงก์ภายในเสีย', chk('No broken internal links'), 'Claude', 'P1', '', 'links', True),
 ('Links', 'ทุกหน้ามีลิงก์จากหน้าอื่น (ไม่มีหน้ากำพร้า)', chk('Every indexable page linked from another page'), 'Claude', 'P1', (A['Every indexable page linked from another page']['detail'] + ' ไม่มีลิงก์เข้า') if A['Every indexable page linked from another page']['detail'] else 'ผ่าน', 'links', True),
 ('Links', 'Footer ลิงก์ไปหน้าแบรนด์/จังหวัดทั้งหมด', 'partly', 'Claude', 'P2', 'หน้าแรกลิงก์ครบ 14 จังหวัด + 6 ยี่ห้อ หน้ายี่ห้อ/จังหวัดลิงก์หากัน แต่ footer ยังไม่มี', 'links', False),
 ('Links', 'Backlink จากเว็บ/เพจรถยนต์ไทยจริง', 'todo', 'ทีม', 'P3', 'ห้ามซื้อลิงก์ — PR, คลิปรีวิว, กลุ่มรถ, พาร์ทเนอร์ไฟแนนซ์', 'spam', False),

 # ---------- Local ----------
 ('Local', 'เบอร์โทรเห็นทุกหน้า', chk('Phone number visible on pages (NAP)'), 'Claude', 'P1', '', 'lb', True),
 ('Local', 'Google Business Profile แบบ service-area', 'todo', 'mOs', 'P1', 'คำว่า "รับซื้อรถ ใกล้ฉัน" ขึ้นจาก Maps เป็นหลัก — ชื่อในโปรไฟล์ต้องตรงกับแบรนด์ที่ใช้จริง ต้องตัดสินใจว่าจะใช้ชื่อไหน', 'gbp', False),
 ('Local', 'ชื่อ/เบอร์/เวลา ตรงกันทุกที่ (เว็บ, LINE OA, GBP, Facebook)', 'partly', 'Claude', 'P2', 'เว็บกับ LINE ตรงกันแล้ว รอ GBP/Facebook', 'gbp', False),
 ('Local', 'หน้าจังหวัดทำเลหลักครบ (กทม., ปริมณฑล, หัวเมือง)', 'done', 'Claude', 'P2', '14 หัวเมือง (6 พ.ย.) ไม่รวมเกาะ/พื้นที่ห่างไกล', 'spam', False),

 # ---------- Content ----------
 ('Content', 'หน้าแรก: บอกครบว่าทำอะไร ที่ไหน ยังไง ได้เงินเมื่อไหร่', 'done', 'Claude', 'P1', '', 'help', False),
 ('Content', 'หน้า Toyota', 'done', 'Claude', 'P2', '', 'help', False),
 ('Content', 'หน้าแบรนด์ยอดค้นสูงอื่นๆ (Honda, Isuzu, Mazda, Nissan, Ford, MG…)', 'partly', 'Claude', 'P2', 'มีแล้ว Toyota Honda Benz BMW MG Porsche ยังขาด Mazda Nissan Ford Hyundai ฯลฯ', 'spam', False),
 ('Content', 'หน้าเชียงใหม่: intro ข้อมูลจริง', 'done', 'Claude', 'P2', 'เขียนใหม่ (6 พ.ย.) ไม่อ้างทุกอำเภอ', 'help', False),
 ('Content', 'หน้าไฟแนนซ์: ขั้นที่ 3 ข้อมูลจริง', 'done', 'Claude', 'P2', 'เพิ่มขายดาวน์ vs ปิดยอด + ส่วนลดดอกเบี้ย สคบ.', 'help', False),
 ('Content', 'หน้าเอกสาร: เนื้อหาเพิ่ม (ตอนนี้ 671 ตัวอักษร)', 'done', 'Claude', 'P2', 'คู่มือโอนรถ อ้างอิงกรมการขนส่งทางบก (2,147 ตัวอักษร)', 'help', False),
 ('Content', 'หน้า Portfolio: รถที่รับซื้อจริง', 'partly', 'mOs', 'P1', 'การ์ดยังเป็น placeholder — ต้องการรูป+รุ่น+ปี+วันที่ของจริง (ห้าม gen รูป)', 'eeat', False),
 ('Content', 'รีวิวลูกค้าจริงบนหน้าแรก', 'todo', 'mOs', 'P1', 'ตอนนี้ placeholder ห้ามแต่งรีวิว — ใช้รีวิวจริงจาก GBP/LINE (ขออนุญาตลูกค้า)', 'rev', False),
 ('Content', 'บทความคำถามจริง: ขายรถติดไฟแนนซ์, โอนรถ, ปิดบัญชี, ภาษีรถ, ประเมินราคาเอง', 'partly', 'Claude', 'P2', 'ไฟแนนซ์ โอนรถ ประเมินราคา มีเป็นหน้าแล้ว ภาษีรถ/ต่อทะเบียน ยังไม่มี', 'help', False),
 ('Content', 'ราคาตัวอย่าง/ช่วงราคาที่รับซื้อจริงต่อรุ่นยอดนิยม', 'todo', 'ทีม', 'P3', 'ข้อมูลที่เว็บอื่นไม่มี = เหตุผลให้ Google/AI อ้างถึงเรา', 'help', False),
 ('Content', 'Content gate ก่อนขึ้นเว็บ (กันข้อความซ้ำ/placeholder/หน้าบาง)', 'done', 'Claude', 'P2', 'release.sh ไม่ผ่าน = ไม่ขึ้น', 'spam', False),

 # ---------- Trust (E-E-A-T) ----------
 ('Trust (E-E-A-T)', 'หน้า Privacy (PDPA) มีข้อมูลจริงครบ', 'partly', 'mOs', 'P1', 'ยังขาด ชื่อนิติบุคคล วันที่มีผล ระยะเวลาเก็บข้อมูล ช่องทางติดต่อ DPO — เก็บเบอร์+รูปรถ+LINE ID ต้องมี', 'pdpa', False),
 ('Trust (E-E-A-T)', 'หน้า "เกี่ยวกับเรา": ใครทำ ทำมากี่ปี ประเมินยังไง', 'todo', 'mOs', 'P2', 'ไม่ต้องเปิดชื่อบริษัทแม่ — แต่ต้องมีคนจริง/ทีมจริง/วิธีประเมินจริง', 'eeat', False),
 ('Trust (E-E-A-T)', 'บทความมีผู้เขียน วันที่ และแหล่งอ้างอิง', 'todo', 'Claude', 'P2', 'ใช้ตอนเริ่มทำบทความ', 'eeat', False),
 ('Trust (E-E-A-T)', 'HTTPS + โดเมนของตัวเอง', 'done', 'Claude', 'P1', 'GitHub Pages + Enforce HTTPS', 'help', False),
 ('Trust (E-E-A-T)', 'หน้า 404 ที่พาไปต่อได้', 'done', 'Claude', 'P3', '', 'help', False),

 # ---------- GEO (AI search) ----------
 ('GEO (AI)', 'บอท AI เข้าเว็บได้ (robots ไม่บล็อก GPTBot/ClaudeBot/PerplexityBot)', 'done', 'Claude', 'P1', 'User-agent * อนุญาตทุกตัว ยกเว้น /line/', 'robots', False),
 ('GEO (AI)', 'บอท AI อ่านเนื้อหาได้โดยไม่รัน JS', chk('Page text is in the HTML (not only after JavaScript)'), 'Claude', 'P1', 'ตัวเดียวกับ prerender — ตอนนี้ AI เห็นหน้าว่าง', 'ai', True),
 ('GEO (AI)', 'ย่อหน้าแรกตอบคำถามตรงๆ (ใคร ทำอะไร ที่ไหน กี่นาที)', 'partly', 'Claude', 'P2', 'AI ชอบอ้างประโยคที่ตอบจบในตัว', 'help', False),
 ('GEO (AI)', 'ข้อเท็จจริงเป็นตัวเลขที่ตรวจได้ (เวลาตอบ, จ่ายเงินภายในกี่ชม., พื้นที่)', 'partly', 'mOs', 'P2', 'มีบางตัว ต้องยืนยันตัวเลขจริงกับทีม', 'help', False),
 ('GEO (AI)', 'ชื่อแบรนด์ "ขายรถไว" ถูกพูดถึงนอกเว็บ (Facebook, กลุ่มรถ, ข่าว)', 'todo', 'ทีม', 'P3', 'AI เลือกอ้างแบรนด์ที่มีคนพูดถึงหลายที่', 'eeat', False),
 ('GEO (AI)', 'ลองถาม ChatGPT/Perplexity/Gemini ทุกเดือนว่า "รับซื้อรถ เชียงใหม่" เจอเรามั้ย', 'todo', 'Claude', 'P3', 'บันทึกผลเป็นตัวชี้วัด GEO', 'ai', False),

 # ---------- Tracking ----------
 ('Tracking', 'Meta Pixel ID ใส่ในเว็บ', 'done', 'Claude', 'P1', 'Pixel + CAPI (Lead, CompleteRegistration, Purchase, LeadRejected)', 'pixel', False),
 ('Tracking', 'Google Ads conversion ID + label', 'done', 'Claude', 'P1', 'ยิงตอนส่งรูปครบ', 'gads', False),
 ('Tracking', 'GA4 (หรือใช้ Search Console อย่างเดียว)', 'todo', 'mOs', 'P3', 'ตัดสินใจ: ถ้าไม่มีคนดู GA4 ข้ามได้', 'ga4', False),
 ('Tracking', 'UTM ส่งต่อถึงชีทลีด (รู้ว่าลีดมาจากแอดไหน)', 'done', 'Claude', 'P1', 'คอลัมน์ "มาจาก" ในชีท + การ์ดทีม', 'gads', False),
 ('Tracking', 'Conversion = ลีดที่ส่งรูปครบ (ไม่ใช่แค่กรอกฟอร์ม)', 'done', 'Claude', 'P2', 'ส่งรูปครบ = conversion ทั้ง Meta และ Google', 'pixel', False),

 # ---------- Keywords ----------
 ('Keywords', 'ดึง Keyword Planner (ไทย, 12 เดือน) — รับซื้อรถ + แบรนด์ + จังหวัด + ไฟแนนซ์', 'done', 'Claude', 'P1', '287 คำ (5 พ.ย.)', 'kp', False),
 ('Keywords', 'แผนที่ keyword → หน้า (ไม่ให้สองหน้าแย่งคำเดียวกัน)', 'done', 'Claude', 'P1', 'หน้าแรก/ประเมินราคา/ไฟแนนซ์/โอนรถ/จังหวัด/ยี่ห้อ แยกคำกันชัด', 'kp', False),
 ('Keywords', 'ดึงซ้ำทุกเดือน + ใช้ query จริงจาก Search Console', 'todo', 'mOs', 'P3', '', 'gsc', False),
 ('Indexing', 'หน้าที่ไม่มีอยู่ตอบ 404 จริง (ไม่ใช่ 200)', 'done', 'Claude', 'P3', 'GitHub Pages ส่ง 404.html พร้อมสถานะ 404', 'noindex', False),
 ('On-page', 'ข้อความลิงก์บอกว่าไปหน้าอะไร (ไม่ใช่ "คลิกที่นี่")', 'partly', 'Claude', 'P3', 'ปุ่มหลักโอเค ลิงก์ในเนื้อหาบางจุดยังกว้าง', 'links', False),
 ('Speed', 'JS+CSS ทั้งหน้าเล็ก (< 50 KB)', 'done', 'Claude', 'P3', 'preact 12k + site.js 7k + dc.js 3k', 'cwv', False),
 ('Speed', 'Cache รูป/ไฟล์นานขึ้น (ตอนนี้ 10 นาที)', 'todo', 'mOs', 'P3', 'เปิด Cloudflare proxy (ส้ม) + cache rule ให้ /img/ /assets/', 'cwv', False),
 ('Speed', 'ปุ่ม/ช่องกรอกบนมือถือใหญ่พอกด (≥ 44pt)', 'done', 'Claude', 'P2', 'ตรวจตอน /setperfect', 'mobile', False),
 ('Content', 'รูปทีมงาน/การตรวจรถของจริง (ห้าม gen)', 'todo', 'mOs', 'P2', 'รูปจริงช่วยทั้งความน่าเชื่อถือและ Google Images', 'img', False),
 ('Links', 'โปรไฟล์ LINE OA / Facebook ลิงก์กลับมาเว็บ', 'todo', 'mOs', 'P3', '', 'gbp', False),
 ('Tracking', 'เชื่อม Search Console กับ Google Ads', 'todo', 'mOs', 'P3', 'เห็นคำค้นธรรมชาติคู่กับแอดในที่เดียว', 'gads', False),
]

BACKEND = [
 ('LINE', 'ฟอร์มเว็บ → ชีท + รหัส KR', 'done', 'Claude', '', 'liff'),
 ('LINE', 'เปิดเว็บในแอป LINE (LIFF) รู้ตัวตนตั้งแต่หน้าแรก', 'done', 'Claude', 'kairodwai.com/go → liff', 'liff'),
 ('LINE', 'อัปโหลดรูป 5 มุม → Drive + การ์ดรูปครบ', 'done', 'Claude', '', 'flex'),
 ('LINE', 'ทักคนที่กรอกแล้วหนีใน 1 นาที (การ์ด + เบอร์)', 'done', 'Claude', 'v18–v20', 'flex'),
 ('LINE', 'เมนูล่างรายคน 3 สถานะ (ปกติ / รอรูป / รอประเมิน)', 'done', 'Claude', 'v20', 'rm'),
 ('LINE', 'การ์ดแจ้งทีมในกลุ่ม (สถานะเล่ม, เบอร์, ปุ่มโทร, ดูรูป)', 'done', 'Claude', 'v16', 'flex'),
 ('LINE', 'ปุ่ม "เปิดแชทลูกค้า" ในการ์ดกลุ่ม', 'todo', 'Claude', 'รอ URL หน้าแชทจาก OA Manager', 'flex'),
 ('LINE', 'ข้อความทักทายเพื่อนใหม่ใน OA Manager', 'todo', 'mOs', 'ข้อความเตรียมไว้แล้ว วางเองใน OA Manager', 'flex'),
 ('LINE', 'ทดสอบ /go บน Android จริง', 'todo', 'mOs', 'intent เด้งเข้าแอป LINE', 'liff'),
 ('SMS', 'SMS สำรองคนไม่มีไลน์ (Thaibulksms)', 'done', 'Claude', 'ทดสอบผ่าน 2 พ.ย.', 'tbs'),
 ('SMS', 'ชื่อผู้ส่ง "Kairodwai" อนุมัติ + ตั้ง SMS_SENDER', 'partly', 'mOs', 'รออนุมัติ 1–2 วันทำการ', 'tbs'),
 ('SMS', 'เติมเครดิต SMS + เตือนก่อนหมด 1–2 วัน', 'done', 'mOs', 'เช็กทุกวัน 9 โมง', 'tbs'),
 ('Ops', 'ตามลีดค้างรูปอัตโนมัติ (2 ชม. / 1 วัน)', 'done', 'Claude', 'trigger รายชั่วโมง', 'flex'),
 ('Ops', 'ฟอร์มเน็ตหลุดแล้วปุ่มค้าง "กำลังส่ง…"', 'todo', 'Claude', 'ต้องให้ลองใหม่ได้', 'js'),
 ('Ops', 'ลบฟังก์ชันอัปรูปชั่วคราว saveSiteImg (หมดอายุ 3 พ.ย.)', 'todo', 'Claude', '', 'js'),
 ('Ops', 'ชีทลีด: สถานะตามงานจริง → ซื้อแล้วส่ง Purchase ให้ Meta', 'done', 'Claude', '6 พ.ย. เลิกช่องติ๊ก ใช้สถานะช่องเดียว', 'gads'),
 ('Ops', 'นโยบายลบข้อมูลลีด (PDPA) ตามระยะที่ประกาศ', 'done', 'Claude', 'ลบอัตโนมัติครบ 30 วัน ยกเว้นคันที่ซื้อ', 'pdpa'),
 ('Ops', 'เตือนกลุ่มเมื่อลีดไม่มีคนโทรเกิน 1 / 3 ชม. (8:00–20:00)', 'done', 'Claude', '', 'flex'),
 ('Ops', 'กันรถกระบะทุกรุ่นที่ฟอร์ม', 'done', 'Claude', '5 พ.ย. (MU-X/MU-7 รับ)', 'js'),
]

today = datetime.date(2026, 11, 6)
start, goal = datetime.date(2026, 11, 1), datetime.date(2027, 5, 1)
PHASES = [
 {'name': 'Month 1 · Launch', 'from': '2026-11-01', 'to': '2026-12-01', 'focus': 'prerender, structured data, Search Console, GBP, tracking, ลบ placeholder',
  'groups': ['Indexing', 'Content in HTML', 'Structured data', 'Tracking', 'Keywords']},
 {'name': 'Months 2–3 · Content', 'from': '2026-12-01', 'to': '2027-02-01', 'focus': 'หน้าแบรนด์/จังหวัดตามยอดค้นจริง, บทความคำถามจริง, เนื้อหาจริงแทน placeholder',
  'groups': ['On-page', 'Content', 'Local', 'Links', 'Social']},
 {'name': 'Months 4–6 · Authority', 'from': '2027-02-01', 'to': '2027-05-01', 'focus': 'รีวิวจริง, backlink, แบรนด์ถูกพูดถึง, Core Web Vitals จริง, วัด GEO',
  'groups': ['Trust (E-E-A-T)', 'GEO (AI)', 'Speed']},
]
W = {'done': 1, 'partly': .5, 'todo': 0}
items = [dict(group=g, name=n, status=s, who=w, pri=p, note=d, src=S[k][0], srcName=S[k][1], check=c) for g, n, s, w, p, d, k, c in ITEMS]
back = [dict(group=g, name=n, status=s, who=w, note=d, src=S[k][0], srcName=S[k][1]) for g, n, s, w, d, k in BACKEND]
def pct(xs): return round(100 * sum(W[x['status']] for x in xs) / len(xs)) if xs else 0
for ph in PHASES:
    xs = [i for i in items if i['group'] in ph['groups']]
    ph['pct'], ph['n'], ph['done'] = pct(xs), len(xs), sum(1 for x in xs if x['status'] == 'done')
out = {
  'checkedAt': audit['at'], 'today': str(today), 'start': str(start), 'goal': str(goal),
  'dayN': (today - start).days + 1, 'dayTotal': (goal - start).days, 'daysLeft': (goal - today).days,
  'items': items, 'backend': back, 'phases': PHASES, 'audit': audit['checks'], 'pages': audit['pages'],
  'pct': pct(items), 'pctBackend': pct(back),
  'counts': {s: sum(1 for i in items if i['status'] == s) for s in W}, 'backCounts': {s: sum(1 for i in back if i['status'] == s) for s in W},
}
json.dump(out, open(os.path.join(ROOT, 'shots', 'health.json'), 'w'), ensure_ascii=False, indent=1)
print(len(items), 'SEO/GEO items', out['counts'], out['pct'], '% |', len(back), 'backend', out['backCounts'], out['pctBackend'], '% | audit', sum(c['pass'] for c in audit['checks']), '/', len(audit['checks']))
for ph in PHASES: print(ph['name'], ph['pct'], '%', ph['done'], '/', ph['n'])
