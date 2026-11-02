# kairodwai.com — source (โฟลเดอร์ src/)

เว็บ "ขายรถไว" (รับซื้อรถถึงบ้าน) เป็น static site บน GitHub Pages: **root ของ repo นี้คือเว็บที่ออนไลน์อยู่** (branch main, custom domain kairodwai.com, DNS บน Cloudflare, Enforce HTTPS เปิด)
`src/` ถูก exclude จาก Pages ด้วย `_config.yml` ที่ root จึงไม่ถูก serve

## โครงสร้าง
```
src/site-src/    build.py (ตัว build), patches.py (แก้พฤติกรรมหน้าเว็บ), dc.js (runtime Preact), site.js (tracking + ส่ง lead),
                 logo.png / logo-light.png / favicon.png / apple-touch-icon.png / og.jpg, prerender.json
src/design/      project/*.dc.html จาก Claude Design (Main, Mobile, Brand, Province, Portfolio, Finance, Docs, Privacy) + canvas.json
src/line-page/   index.html = หน้า /line/ (ส่งรูป 6 ช่อง หลัง LIFF login)
src/vendor/      preact.min.umd.js
src/logo/        ไฟล์โลโก้ต้นฉบับ (kairodwai-logo-1254.png เป็น master)
src/tools/       สคริปต์ทดสอบ Playwright (gate.js = e2e gate→ฟอร์ม→ส่ง, measure.js = วัดโลโก้, pre.js = prerender, อื่นๆ = screenshot)
```

## build
```
python3 src/site-src/build.py                 # เขียนทับหน้าเว็บที่ root ของ repo ตรงๆ
KR_OUT=/tmp/dry python3 src/site-src/build.py # build ลงที่อื่นเพื่อเทียบก่อน (diff -rq /tmp/dry . -x .git -x src)
node src/tools/speed.js http://localhost:8090  # วัดโหลดทุกหน้าแบบมือถือ+4G ช้า (เปิด python3 -m http.server 8090 ที่ root ก่อน; container ยิง kairodwai.com ตรงไม่ได้)
node src/tools/gate.js                        # e2e: gate → ไม่พร้อม → เปลี่ยนใจ → 3 ขั้น → ส่ง (mock backend) → screenshots ใน shots/
node src/tools/pre.js && python3 src/site-src/build.py --prerender   # prerender สำหรับ SEO (ยังไม่เปิดใช้จริง)
```
รูปประกอบหน้าเว็บอยู่ที่ `/img/*.jpg` (root) — build ทำ .webp + ตัวย่อ -800/-1200 ให้เอง (ข้ามถ้ามีแล้ว; ลบ .webp ทิ้งถ้าเปลี่ยน jpg) และใส่ srcset/lazy/fetchpriority ให้ทุก <img> (`img_attrs` ใน build.py) ถ้า export ดีไซน์ใหม่จาก Claude Design ให้วาง jpg ไว้ใน `src/design/` แล้ว build จะ copy ไปให้

## หน้าเว็บ
`/` (Main desktop / Mobile), `/toyota/` (Brand), `/chiang-mai/` (Province), `/portfolio/`, `/finance/`, `/documents/`, `/privacy/`, `/line/`
flow: gate "พร้อมขายรถตอนนี้ไหม?" → ฟอร์ม 3 ขั้น → `KR.lead()` POST ไป Apps Script → ได้ ref KR-xxxx → `/line/?t=…&ref=…` → ส่งรูป → "คุยต่อในไลน์"
events (site.js `track()`): ReadyToSell / NotReady (trackCustom), Lead เฉพาะกรอกฟอร์มจบ; fbq สำหรับชื่อมาตรฐาน (Lead, Contact, ViewContent, CompleteRegistration, SubmitApplication) ใช้ `track` ที่เหลือ `trackCustom`

## หลังบ้าน
Apps Script (บัญชี Google ของทีม, project "ขายรถไว ระบบหลังบ้าน", web app **v20** 2 พ.ย. 2026) — URL อยู่ใน site.js, โค้ดไฟล์เดียว Code.gs (แก้ผ่าน editor ในเบราว์เซอร์)
flow แจ้งทีม: saveLead เก็บเงียบ (ไม่แจ้ง) → รูปครบ (type done) แจ้งทีม 1 ข้อความแบบ "Kairodwai Lead : KR-xxxx / Details / Status / Call / Source / Photos" + สถานะชีท "รูปครบ รอโทร" → ลูกค้าส่ง "KR-xxxx" ในไลน์ (linkWebLead) → ตอบการ์ด "ได้รับข้อมูลและรูปครบแล้ว กำลังประเมินราคา" (รูปกดไม่ได้) + เปลี่ยนเมนูล่างของคนนั้นเป็น "รอประเมินราคา" (rich menu รายคน 2500×843 ไม่มีปุ่ม — รูป /img/richmenu-wait.png สร้างด้วย src/tools/richmenu.js, ตั้ง/อัปเดตด้วย setupWaitMenu() → WAIT_MENU_ID (dropdown เลือกฟังก์ชันผ่านเบราว์เซอร์อัตโนมัติไม่เสถียร: คลิก listbox ด้วย JS แล้ว click option ที่ width>0, รอ 3 วิ, ตรวจ label ก่อนกด Run; deploy: ตั้งค่า description ด้วย JS setter แล้วตรวจว่า combobox = "New version" ก่อนกด Deploy — เคยเผลอ deploy v10/v14/v16 ซ้ำเพราะ dropdown เพี้ยน); แบบ B (2 พ.ย. 22:13, richmenu a47154…) · ลองแบบอื่น: `node src/tools/richmenu-variants.js` → shots/richmenu-compare.png (ย่อเท่าจอมือถือ); ลีดใหม่ที่มีไลน์ saveLead จะถอดเมนูรายคนคืนค่าเริ่มต้น) + แจ้งทีมด้วยการ์ด `teamFlex()` (หัวสี: เขียว=รูปครบ / ส้ม=กรอกแล้วหนี / แดง=ค้าง 1 วัน; มีสถานะไฟแนนซ์ "มีเล่มพร้อมขาย"/ผ่อนอยู่, เบอร์ + ปุ่ม tel: โทรออกได้เลย, ชื่อไลน์, ที่มา, ปุ่มดูรูป; ทดสอบหน้าตาด้วย testTeamFlex()); การ์ดฝั่งลูกค้า (nudgeFlex / การ์ดรูปครบ) มีบรรทัดสรุป `leadSummary()` = สถานะเล่ม/ไฟแนนซ์ · ขายเมื่อ · เบอร์ ให้แอดมินอ่านในแชท OA ได้เลย (อยู่ใน altText ด้วย) · ปุ่ม "อัพโหลดรูปรถของคุณ เพื่อประเมินราคา" ไม่ใส่ emoji (Android เรนเดอร์น่าเกลียด) · OA Manager บนคอมเรนเดอร์ Flex ได้แต่เบอร์ไม่เป็นลิงก์ (LINE ไม่ auto-link ใน Flex) — โทรจากมือถือผ่านการ์ดกลุ่มทีม → จากนั้นบอทเงียบ ทีมพิมพ์ตอบเองในแชท (OA อยู่โหมด chat ตรวจด้วย botInfo())
ปุ่ม "เก็บลิงก์ไว้ในไลน์" (แผง "ยังไม่สะดวกถ่ายตอนนี้") = oaMessage ส่งลิงก์ /line/?t=… เข้าแชท OA → บอท keepLink ผูก userId กับ token (ไม่แจ้งทีม) → followUp เตือนทางไลน์ (push) แทน SMS; SMS เฉพาะคนไม่มีไลน์กับเรา (v12)
ทดสอบจริงครบสาย 2 พ.ย. 2026 (KR-1009) ผ่าน; ข้อความทักทายเพื่อนใหม่ตั้งใน LINE OA Manager (ใช้ {Nickname}) แยก 2 ทาง: กรอกจากเว็บแล้ว → กดส่งข้อความที่เตรียมไว้ / ยังไม่เคย → ปุ่ม "ส่งรูปรถ"
saveLead กันซ้ำด้วย cache ต่อเบอร์ 10 นาที (ทดสอบซ้ำต้องเปลี่ยนเบอร์หรือรอ) · sheet "ฟอร์มเว็บ" คอลัมน์ I-L (รหัส, หน้าเว็บ, มาจาก, token), M = ติดตามแล้ว (FOLLOW_COL); saveSiteImg (หมดอายุ 2026-11-03) — ถอดออกได้
ตามลีดที่ค้างรูป: trigger รายชั่วโมง `followUp()` (ติดตั้งด้วย installFollowUp) → SMS หลัง 2 ชม. + วันถัดไป (ลิงก์ /line/?t=… เดิม), ครบ 24 ชม. แจ้งทีมโทรตาม
SMS: Thaibulksm API v2 (`sendSms()` ใน Code.gs) — บัญชี Thaibulksm ของทีม, API Key ชื่อแอป "Kairodwai" (ช่องทาง SMS/LON) — ค่าอยู่ใน Script properties `SMS_KEY`, `SMS_SECRET`, `SMS_TEST_TO` (เบอร์ทดสอบ), `SMS_SENDER` (ยังไม่ตั้ง = ใช้ "Demo"); ทดสอบด้วย `testSms()` ผ่านแล้ว 2 พ.ย. 2026
  ค้าง: เติมเครดิต (ทดลองได้ 10 เครดิต ส่งเข้าเบอร์ตัวเองเท่านั้น) + ขอชื่อผู้ส่ง KAIRODWAI แล้วใส่ `SMS_SENDER`

## เมนูล่างรายคน (per-user rich menu ผ่าน Messaging API) — 3 สถานะ
- ปกติ (แอดมาเอง/เพื่อนแนะนำ): เมนูเริ่มต้นของ OA "ส่งรูปรถ | โทรหาเรา" (ตั้งใน OA Manager)
- กรอกฟอร์มแล้ว ยังไม่ส่งรูป: `leadMenu(uid)` → "รอรูปรถของคุณ (กดไม่ได้) | โทรหาเรา" — รูป /img/richmenu-lead.png (src/tools/richmenu-lead.js), สร้างด้วย `setupLeadMenu()` → LEAD_MENU_ID, เบอร์ CALL_PHONE (ไม่ตั้ง = 0914922662); เรียกใน saveLead (มี uid) และ keepLink
- รูปครบ: `waitMenu(uid)` → "รอประเมินราคา" (ไม่มีปุ่ม) — /img/richmenu-wait.png, `setupWaitMenu()` → WAIT_MENU_ID

## เปิดเว็บในไลน์ (LIFF) — ทางหลักสำหรับคนจากโฆษณา
LIFF app "kairodwai-web" (LINE Login channel 2012318037, endpoint https://kairodwai.com/, scope profile+openid, bot link = Aggressive) — LIFF ID ใส่ที่ `LIFF_WEB_ID` ใน build.py (ลงทั้งหน้าเว็บ /line/ และ /go) และ Script property `LIFF_WEB_ID` (ปุ่ม "ถ่ายรูปต่อ" ใน followUp)
ลิงก์โฆษณา = `https://kairodwai.com/go?utm_…` → มือถือ: เด้งไป `liff.line.me/<ID>?via=liff&utm_…` (เปิดเว็บในแอปไลน์) / คอม: เว็บธรรมดา
โหมด `?via=liff`: site.js โหลด LIFF SDK → getProfile → ซ่อนปุ่มแอดไลน์ (`.via-liff .kr-line`) → เลื่อนไปกล่อง "พร้อมขายรถตอนนี้ไหม?" → lead ส่ง uid/lname → saveLead ผูก userId กับ token ตั้งแต่แรก → /line/?…&via=liff → รูปครบ: finishPhotos ส่งการ์ด "ได้รับข้อมูลและรูปครบแล้ว" (กดไม่ได้) + เมนูรอประเมิน + ทีมได้ Kairodwai Lead พร้อม "LINE : ชื่อ" → หน้าเว็บโชว์ "กำลังพาคุณไปที่แชท…" + แถบวิ่ง 2.4 วิ แล้ว liff.closeWindow() (ปุ่ม "กลับไปที่แชท" โผล่หลัง 3.6 วิถ้าปิดเองไม่ได้)
คนค้าง: หน้ารูปส่ง type left ตอนปิดหน้า (pagehide) → markLeft ตั้ง trigger 1 นาที (v17; trigger ของ Google หน่วงเองได้อีก ~0-1 นาที) → leftCheck: ยังไม่ครบ → push ปุ่ม "ถ่ายรูปต่อ" ให้ลูกค้า + แจ้งทีม "กรอกแล้ว ยังไม่ส่งรูป" (คอลัมน์ M = left) · followUp รายชั่วโมง: เห็น userId → push แทน SMS (push ไม่ผ่าน → SMS); โหมดไลน์ไม่มีกล่องถามตอนออก/ไม่มีแผง "ถ่ายทีหลัง" · เว็บธรรมดา (Google/คอม) ยังใช้ flow รหัส KR + Add LINE เหมือนเดิม
ทดสอบจำลอง: `node src/tools/liff.js` · storyboard: `node src/tools/storyboard.js`

## Health Monitor (หน้าเช็ค SEO/GEO + งานหลังบ้าน)
หน้า private ใน Claude (Dashboard artifact "ขายรถไว Health Monitor") — ข้อมูลมาจาก 2 สคริปต์:
`python3 -m http.server 8090` (ที่ root) แล้ว `node src/tools/seo-audit.js` → shots/seo-audit.json (ตรวจจริงทุกหน้า: HTML ดิบ vs หลังรัน JS, title/desc/H1/schema/alt/ลิงก์)
`python3 src/tools/health-data.py` → shots/health.json (เช็คลิสต์ 83 ข้อ + หลังบ้าน 17 ข้อ + roadmap 6 เดือน 1 พ.ย. 2026 – 1 พ.ค. 2027; ข้อที่มี check=True อ่านผลจาก audit)
อัปเดตหน้า: แก้สถานะใน health-data.py → รันสองสคริปต์ → อัปโหลด JSON ใหม่เข้า artifact

## บั๊กที่รู้แล้ว
- gate.js: ขั้น goBack หลัง redirect ไป /line/ รอ html.dc-ready ไม่ทัน (TimeoutError) — ของเดิมก่อน LIFF, ขั้นก่อนหน้าผ่านครบ
site.js `lead()`: ถ้า POST ล้มเหลว (เน็ตหลุด) ฟอร์มค้างที่ "กำลังส่ง…" ตลอด — ต้องใส่ .catch → setState({sending:false, missing:true}) พร้อมข้อความให้ลองใหม่

## ค้างอยู่
- Meta Pixel ID / Google Ads conversion ID ยังไม่ใส่
- placeholder ที่รอข้อมูลจริง: รีวิวหน้าแรก, การ์ด portfolio, Finance ข้อ 3, intro เชียงใหม่, Privacy (ชื่อบริษัท วันที่ ระยะเก็บข้อมูล)
- Cloudflare: CNAME www → ควรชี้ kairodwai.github.io
- รูปคน: ห้าม generate เอง
- แผนโครงสร้าง funnel ทั้งระบบ: https://claude.ai/artifact/1aLPX8djoyrfAZtcQfrbzX
