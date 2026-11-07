# ผลงานรับซื้อจริง (Moss 7 พ.ย. 69): รูปส่งมอบรถ 30 คันจากทีม — เบลอป้ายทะเบียนและหน้าลูกค้าแล้ว (ทีมงานเห็นหน้าได้) ทำที่ /home/claude/kr-photos
# ข้อมูลใน data/portfolio.json: img (hash ของ img/<hash>.jpg — build ทำ webp/srcset ให้เอง), brand, model, prov, dist, bslug (หน้ายี่ห้อ), pslug (หน้าจังหวัด)
# ไม่มีปี/เดือน/ไฟแนนซ์ของแต่ละคัน (ทีมถ่ายรูปเดียวตอนส่งมอบ ไม่เก็บข้อมูลอื่น) — ห้ามแต่งเพิ่ม
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CARS = json.load(open(os.path.join(HERE, 'data', 'portfolio.json'), encoding='utf-8'))

CARD = ('<article style="background: #FFFFFF; border: 1px solid #DEDBD3; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column;">'
        '<img src="/img/{img}.jpg" alt="{alt}" width="1440" height="1080" style="display: block; width: 100%; height: auto; aspect-ratio: 4 / 3; object-fit: cover; background: #ECEAE4;">'
        '<div style="padding: 16px; display: flex; flex-direction: column; gap: 6px;">'
        '<{h} style="margin: 0; font-family: \'Kanit\', sans-serif; font-weight: 500; font-size: 19px; line-height: 1.35;">{model}</{h}>'
        '{meta}</div></article>')
META = '<span style="font-size: 14px; color: #55534E;">{}</span>'
GRID = '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr)); gap: 16px;">{}</div>'


def where(c):
    return c['prov'] + (' ' + c['dist'] if c['dist'] else '')


def card(c, h='h3', meta=None):
    # meta: None = "รับซื้อถึงบ้าน · จังหวัด" (หน้าแรก/หน้าผลงาน) · ฟังก์ชัน = ข้อความเฉพาะหน้า · '' = ไม่มีบรรทัดรอง
    # ข้อความการ์ดต้องไม่ซ้ำกันข้ามหน้า (ด่าน ai-screen นับบรรทัด ≥ 12 ตัวอักษรที่ซ้ำกับหน้าอื่นเป็น "ซ้ำแม่แบบ")
    alt = f"{c['model']} ที่ขายรถไวรับซื้อถึงบ้านที่{where(c)}"
    m = ('รับซื้อถึงบ้าน · ' + where(c)) if meta is None else meta
    return CARD.format(img=c['img'], alt=html.escape(alt), h=h, model=html.escape(c['model']),
                       meta=META.format(html.escape(m)) if m else '')


def by_brand(slug, n=3):
    return [c for c in CARS if c['bslug'] == slug][:n]


def by_prov(slug, n=6):
    return [c for c in CARS if c['pslug'] == slug][:n]


def grid(cars, h='h3', meta=None):
    return GRID.format(''.join(card(c, h, meta(c) if callable(meta) else meta) for c in cars))


def prov_meta(c):
    # ในหน้าจังหวัดไม่ต้องย้ำชื่อจังหวัด — บอกเขต/อำเภอถ้ามี ไม่มีก็ไม่ใส่บรรทัดรอง
    return (('เขต' if c['prov'] == 'กรุงเทพฯ' else 'อ.') + c['dist']) if c['dist'] else ''


def brand_meta(c):
    return where(c)


def intro(cars, label):
    # ประโยคเปิดเซกชัน "รับซื้อล่าสุด" ต่อหน้า — ใส่รายชื่อรุ่นจริง จะได้ไม่ซ้ำกับหน้าอื่น (ด่าน ai-screen)
    return f"{len(cars)} คันที่ทีมไปรับถึงบ้าน{label}: " + ', '.join(c['model'] for c in cars) + ' ถ่ายตอนส่งมอบ เบลอป้ายทะเบียนและหน้าลูกค้า'


def chips(linkable):
    """แถวชิปลิงก์ไปหน้ายี่ห้อ/จังหวัดที่มีรถจริง (ลิงก์ภายใน: Google ตามจากหน้าผลงานไปหน้าอื่นได้)"""
    chip = 'height: 40px; padding: 0 14px; box-sizing: border-box; border-radius: 20px; background: #FFFFFF; border: 1px solid #DEDBD3; display: inline-flex; align-items: center; gap: 6px; font-size: 14px; white-space: nowrap; text-decoration: none; color: #141414;'
    cnt = '<span style="color: #55534E;">{}</span>'
    return '<div style="display: flex; flex-wrap: wrap; gap: 8px;">' + ''.join(
        f'<a href="/{slug}/" style="{chip}">{html.escape(label)} ' + cnt.format(n) + '</a>' for slug, label, n in linkable) + '</div>'


def portfolio_sections():
    """หน้า /portfolio/: การ์ดทั้ง 30 คันแบบ static (อยู่ใน HTML ตรงๆ — ไม่ต้องรอ JS, build ใส่ webp/srcset/lazy ให้ทุกรูป)"""
    import brands, provinces
    bc = {}
    for c in CARS:
        if c['bslug']: bc[c['bslug']] = bc.get(c['bslug'], 0) + 1
    pc = {}
    for c in CARS:
        if c['pslug'] and c['pslug'] in provinces.BY: pc[c['pslug']] = pc.get(c['pslug'], 0) + 1
    brand_chips = chips([(s, brands.BY[s]['name'], n) for s, n in sorted(bc.items(), key=lambda x: -x[1])])
    prov_chips = chips([(s, provinces.BY[s]['h1'], n) for s, n in sorted(pc.items(), key=lambda x: -x[1])])
    lab = '<span style="font-size: 14px; font-weight: 500; color: #55534E;">{}</span>'
    nprov = len(set(c['prov'] for c in CARS))
    head = (f'<p style="margin: 0; font-size: 17px; line-height: 1.6; color: #3D3B37;">{len(CARS)} คันจาก {nprov} จังหวัด ถ่ายตอนทีมไปรับรถและส่งมอบเงินถึงบ้านลูกค้า '
            'เบลอป้ายทะเบียนและหน้าลูกค้าทุกคัน ไม่มีรูปสต็อกหรือรูปที่สร้างด้วยคอมพิวเตอร์</p>'
            '<div style="display: flex; flex-direction: column; gap: 10px;">' + lab.format('ดูหน้ายี่ห้อ') + brand_chips
            + lab.format('ดูหน้าจังหวัด') + prov_chips + '</div>')
    return head, grid(CARS, 'h2')
