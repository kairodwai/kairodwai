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
node src/tools/gate.js                        # e2e: gate → ไม่พร้อม → เปลี่ยนใจ → 3 ขั้น → ส่ง (mock backend) → screenshots ใน shots/
node src/tools/pre.js && python3 src/site-src/build.py --prerender   # prerender สำหรับ SEO (ยังไม่เปิดใช้จริง)
```
รูปประกอบหน้าเว็บอยู่ที่ `/img/*.jpg` (root) ถ้า export ดีไซน์ใหม่จาก Claude Design ให้วาง jpg ไว้ใน `src/design/` แล้ว build จะ copy ไปให้

## หน้าเว็บ
`/` (Main desktop / Mobile), `/toyota/` (Brand), `/chiang-mai/` (Province), `/portfolio/`, `/finance/`, `/documents/`, `/privacy/`, `/line/`
flow: gate "พร้อมขายรถตอนนี้ไหม?" → ฟอร์ม 3 ขั้น → `KR.lead()` POST ไป Apps Script → ได้ ref KR-xxxx → `/line/?t=…&ref=…` → ส่งรูป → "คุยต่อในไลน์"
events (site.js `track()`): ReadyToSell / NotReady (trackCustom), Lead เฉพาะกรอกฟอร์มจบ; fbq สำหรับชื่อมาตรฐาน (Lead, Contact, ViewContent, CompleteRegistration, SubmitApplication) ใช้ `track` ที่เหลือ `trackCustom`

## หลังบ้าน
Apps Script (บัญชี Google ของทีม, project "ขายรถไว ระบบหลังบ้าน", web app **v12** 2 พ.ย. 2026) — URL อยู่ใน site.js, โค้ดไฟล์เดียว Code.gs (แก้ผ่าน editor ในเบราว์เซอร์)
flow แจ้งทีม: saveLead เก็บเงียบ (ไม่แจ้ง) → รูปครบ (type done) แจ้งทีม 1 ข้อความแบบ "Kairodwai Lead : KR-xxxx / Details / Status / Call / Source / Photos" + สถานะชีท "รูปครบ รอโทร" → ลูกค้าส่ง "KR-xxxx" ในไลน์ (linkWebLead) → ตอบการ์ด "ได้รับข้อมูลและรูปครบแล้ว กำลังประเมินราคา" (รูปกดไม่ได้) + เปลี่ยนเมนูล่างของคนนั้นเป็น "รอประเมินราคา" (rich menu รายคน, ไม่มีปุ่ม — รูป /img/richmenu-wait.png สร้างด้วย src/tools/richmenu.js, ตั้งครั้งแรกด้วย setupWaitMenu() → WAIT_MENU_ID) + แจ้งทีม "แอดไลน์แล้ว ชื่อไลน์ …" → จากนั้นบอทเงียบ ทีมพิมพ์ตอบเองในแชท (OA อยู่โหมด chat ตรวจด้วย botInfo())
ปุ่ม "เก็บลิงก์ไว้ในไลน์" (แผง "ยังไม่สะดวกถ่ายตอนนี้") = oaMessage ส่งลิงก์ /line/?t=… เข้าแชท OA → บอท keepLink ผูก userId กับ token (ไม่แจ้งทีม) → followUp เตือนทางไลน์ (push) แทน SMS; SMS เฉพาะคนไม่มีไลน์กับเรา (v12)
ทดสอบจริงครบสาย 2 พ.ย. 2026 (KR-1009) ผ่าน; ข้อความทักทายเพื่อนใหม่ตั้งใน LINE OA Manager (ใช้ {Nickname}) แยก 2 ทาง: กรอกจากเว็บแล้ว → กดส่งข้อความที่เตรียมไว้ / ยังไม่เคย → ปุ่ม "ส่งรูปรถ"
sheet "ฟอร์มเว็บ" คอลัมน์ I-L (รหัส, หน้าเว็บ, มาจาก, token), M = ติดตามแล้ว (FOLLOW_COL); saveSiteImg (หมดอายุ 2026-11-03) — ถอดออกได้
ตามลีดที่ค้างรูป: trigger รายชั่วโมง `followUp()` (ติดตั้งด้วย installFollowUp) → SMS หลัง 2 ชม. + วันถัดไป (ลิงก์ /line/?t=… เดิม), ครบ 24 ชม. แจ้งทีมโทรตาม
SMS: Thaibulksm API v2 (`sendSms()` ใน Code.gs) — บัญชี Thaibulksm ของทีม, API Key ชื่อแอป "Kairodwai" (ช่องทาง SMS/LON) — ค่าอยู่ใน Script properties `SMS_KEY`, `SMS_SECRET`, `SMS_TEST_TO` (เบอร์ทดสอบ), `SMS_SENDER` (ยังไม่ตั้ง = ใช้ "Demo"); ทดสอบด้วย `testSms()` ผ่านแล้ว 2 พ.ย. 2026
  ค้าง: เติมเครดิต (ทดลองได้ 10 เครดิต ส่งเข้าเบอร์ตัวเองเท่านั้น) + ขอชื่อผู้ส่ง KAIRODWAI แล้วใส่ `SMS_SENDER`

## บั๊กที่รู้แล้ว
site.js `lead()`: ถ้า POST ล้มเหลว (เน็ตหลุด) ฟอร์มค้างที่ "กำลังส่ง…" ตลอด — ต้องใส่ .catch → setState({sending:false, missing:true}) พร้อมข้อความให้ลองใหม่

## ค้างอยู่
- Meta Pixel ID / Google Ads conversion ID ยังไม่ใส่
- placeholder ที่รอข้อมูลจริง: รีวิวหน้าแรก, การ์ด portfolio, Finance ข้อ 3, intro เชียงใหม่, Privacy (ชื่อบริษัท วันที่ ระยะเก็บข้อมูล)
- Cloudflare: CNAME www → ควรชี้ kairodwai.github.io
- รูปคน: ห้าม generate เอง
- แผนโครงสร้าง funnel ทั้งระบบ: https://claude.ai/artifact/1aLPX8djoyrfAZtcQfrbzX
