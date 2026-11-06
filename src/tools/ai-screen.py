#!/usr/bin/env python3
"""สกรีนเนื้อหาก่อนขึ้นเว็บ (Moss 6 พ.ย. 69: "ระบบเช็ค AI เผื่อเห็นความเป็น AI แล้วลดคะแนน มึงต้องสกรีนด้วย")
Google ไม่ได้ลงโทษเพราะ "AI เขียน" แต่ลงโทษ scaled content abuse = หน้าเยอะๆ ที่เนื้อหาซ้ำ/แทนชื่อ ไม่มีประโยชน์เพิ่ม
และ doorway pages = หน้าจังหวัด/ยี่ห้อที่ต่างกันแค่ชื่อ — สคริปต์นี้วัดสองเรื่องนั้น + คำติดปากของ AI
ใช้: python3 src/tools/ai-screen.py  (อ่านหน้าที่ build แล้วใน repo) → exit 1 ถ้าไม่ผ่าน
"""
import json, os, re, sys, html
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGES = json.load(open(os.path.join(ROOT, 'src', 'site-src', 'pages.json'), encoding='utf-8'))
SKIP = {'Portfolio', 'Privacy'}

# คำ/รูปประโยคที่คนอ่านแล้วรู้ว่า AI เขียน (ภาษาไทยการตลาด + แปลจากอังกฤษ) — เจอ = แก้
TELLS = ['อย่างไรก็ตาม', 'นอกจากนี้', 'ไม่ว่าจะเป็น', 'ครบวงจร', 'ยกระดับ', 'ในยุคปัจจุบัน', 'ในยุคนี้', 'มั่นใจได้เลย', 'ตอบโจทย์',
         'หลากหลาย', 'อย่างมืออาชีพ', 'ไม่ต้องกังวล', 'ที่ดีที่สุด', 'ง่ายๆ เพียง', 'เพียงแค่คลิก', 'ไม่ว่าคุณจะ', 'สิ่งสำคัญคือ',
         'กล่าวโดยสรุป', 'โดยสรุปแล้ว', 'ปลดล็อก', 'เหนือระดับ', 'อย่างไร้รอยต่อ', 'ไร้กังวล', 'สุดคุ้ม', 'ราคาดีที่สุด',
         'อันดับหนึ่ง', 'เบอร์ 1', 'ทุกความต้องการ', 'ประสบการณ์ที่ดี', 'คุณภาพสูง', 'อย่างแท้จริง', 'อย่างครอบคลุม']


def main_text(path):
    s = open(os.path.join(ROOT, path.strip('/'), 'index.html'), encoding='utf-8').read()
    s = s[s.index('<div id="root">'):]
    s = re.split(r'<script', s)[0]
    s = re.sub(r'<header.*?</header>|<footer.*?</footer>|<form.*?</form>', ' ', s, flags=re.S)
    s = re.sub(r'<(br|/p|/li|/h\d|/summary|/span|/a|/div)[^>]*>', '\n', s)
    s = html.unescape(re.sub(r'<[^>]+>', '', s))
    return [x.strip() for x in s.split('\n') if len(x.strip()) >= 12]


def norm(x):   # ประโยคเดียวกันที่ต่างแค่ชื่อจังหวัด/ยี่ห้อ = ประโยคแม่แบบ → ยุบชื่อเฉพาะออกก่อนเทียบ
    return re.sub(r'\s+', ' ', x)


pages = {n: main_text(p) for n, p in PAGES.items() if n not in SKIP}
names = {n: [] for n in pages}
for n, p in PAGES.items():   # ชื่อเฉพาะของแต่ละหน้า (จังหวัด/ยี่ห้อ) ไว้ยุบตอนเทียบประโยคแม่แบบ
    if n.startswith('Province') or n.startswith('Brand'):
        names[n] = [w for w in re.findall(r'[A-Za-z][A-Za-z\-]+|[฀-๿]+', open(os.path.join(ROOT, p.strip('/'), 'index.html'), encoding='utf-8').read().split('<h1')[1].split('</h1>')[0]) if len(w) > 2]
def tmpl(n, x):
    for w in names.get(n, []):
        x = x.replace(w, '§')
    return norm(x)

# ประโยคที่อยู่แทบทุกหน้า (ปุ่ม, เกณฑ์รับซื้อ, แถบเครดิต) = ส่วนกลางของเว็บ ไม่นับ
from collections import Counter
cnt = Counter(t for n, xs in pages.items() for t in set(tmpl(n, x) for x in xs))
common = {t for t, c in cnt.items() if c >= len(pages) * 0.6}

fail, warns = [], []
print(f'{"หน้า":<16}{"ตัวอักษร":>8}{"ของตัวเอง":>10}{"ซ้ำแม่แบบ":>10}  คำติดปาก AI')
for n, xs in pages.items():
    body = [x for x in xs if tmpl(n, x) not in common]
    total = sum(len(x) for x in body) or 1
    own = sum(len(x) for x in body if cnt[tmpl(n, x)] == 1)
    dup = 1 - own / total
    tells = sorted({t for t in TELLS for x in xs if t in x})
    dash = sum(x.count('—') for x in xs)
    flag, warn = [], []   # flag = ห้ามขึ้น · warn = ขึ้นได้ แต่ควรเติมข้อมูลจริง
    loc = n.startswith('Province') or n.startswith('Brand')
    if loc and dup > 0.7: flag.append('ซ้ำแม่แบบเกิน 70% (หน้าปั๊ม)')
    elif loc and dup > 0.55: warn.append('ซ้ำแม่แบบเกิน 55%')
    if own < 500: warn.append('เนื้อหาเฉพาะหน้าน้อย')
    if tells: flag.append('คำ AI')
    if dash: flag.append(f'ขีดยาว — {dash}')
    print(f'{PAGES[n]:<16}{total:>8}{own:>10}{dup:>9.0%}  {" ".join(tells)}  {"✗ " + ", ".join(flag) if flag else ("⚠ " + ", ".join(warn) if warn else "ok")}')
    if flag: fail.append((PAGES[n], flag))
    if warn: warns.append(PAGES[n])
print()
print(('ผ่าน' if not fail else f'ไม่ผ่าน {len(fail)} หน้า') + (f' · ควรเติมข้อมูลจริง {len(warns)} หน้า: ' + ' '.join(warns) if warns else ''))
sys.exit(1 if fail and '--warn' not in sys.argv else 0)
