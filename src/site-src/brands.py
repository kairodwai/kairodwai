# หน้ายี่ห้อ (SEO ขั้น 2, Moss 6 พ.ย. 69 "ลุยต่อให้จบ"): ยี่ห้อที่คนค้นขายเยอะ + ราคาต่อคันสูง
# ทุกหน้าสร้างจาก design/project/Brand.dc.html (ต้นแบบ Toyota) แล้วแทนข้อความเฉพาะยี่ห้อ
# รายชื่อรุ่น + ปี ดึงจาก CARS ตัวเดียวกับฟอร์ม (ข้อมูลเดียว ไม่พิมพ์ซ้ำ) · ไม่รับกระบะทุกรุ่น (Moss 5 พ.ย. 69)
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
_MAIN = os.path.join(os.path.dirname(HERE), 'design', 'project', 'Main.dc.html')

# slug, ชื่อในข้อมูล CARS, ชื่อที่โชว์, ชื่อไทยที่คนพิมพ์ค้น, ประโยคเปิด, คำถามเฉพาะยี่ห้อ
B = [
    dict(slug='toyota', key='Toyota', name='Toyota', th='โตโยต้า', page='Brand'),
    dict(slug='honda', key='Honda', name='Honda', th='ฮอนด้า',
         intro='City, Civic, Accord, HR-V, CR-V, Jazz และ Honda รุ่นอื่นๆ รวมรุ่นไฮบริด e:HEV รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('Honda ไฮบริด e:HEV รับไหม', 'รับ City, Civic, Accord, HR-V และ CR-V รุ่น e:HEV ตามรุ่นในรายการด้านบน ราคาคิดจากรุ่นย่อย ปี ไมล์ และสภาพรถจริง')),
    dict(slug='benz', key='Mercedes-Benz', name='Benz', th='เบนซ์',
         intro='C-Class, E-Class, GLA, GLC, CLA, S-Class และ Benz รุ่นอื่นๆ รวมรุ่นปลั๊กอินไฮบริดและ EQ ไฟฟ้า รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('Benz ปลั๊กอินไฮบริด อย่าง C 350 e, E 300 e รับไหม', 'รับ ทั้งรุ่นปลั๊กอินไฮบริด (รุ่นที่ลงท้ายด้วย e) และรุ่น EQ ไฟฟ้า ตามรุ่นในรายการด้านบน')),
    dict(slug='bmw', key='BMW', name='BMW', th='บีเอ็มดับเบิลยู',
         intro='Series 3, Series 5, X1, X3, X5, i4, iX และ BMW รุ่นอื่นๆ รวมรุ่นปลั๊กอินไฮบริดอย่าง 330e และ 530e รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('BMW 330e หรือ 530e รับไหม', 'รับ ทั้ง 330e, 530e และ BMW ไฟฟ้าอย่าง i4, iX ตามรุ่นในรายการด้านบน')),
    dict(slug='mg', key='MG', name='MG', th='เอ็มจี',
         intro='MG ZS, MG5, HS, MG4 Electric, ZS EV และ MG รุ่นอื่นๆ รวมรถไฟฟ้า รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('MG ไฟฟ้า อย่าง MG4, ZS EV รับไหม', 'รับ ทั้ง MG4 Electric, ZS EV, ES และ S5 EV ตามรุ่นในรายการด้านบน ราคาคิดจากรุ่นย่อย ปี ไมล์ และสภาพรถจริง')),
    dict(slug='porsche', key='Porsche', name='Porsche', th='ปอร์เช่',
         intro='Cayenne, Macan, Panamera, 911, Taycan, 718 และ Porsche รุ่นอื่นๆ รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('Porsche Taycan หรือ Macan Electric รับไหม', 'รับ ทั้ง Taycan และ Macan Electric ตามปีในรายการด้านบน')),
    dict(slug='mazda', key='Mazda', name='Mazda', th='มาสด้า',
         intro='Mazda2, Mazda3, CX-3, CX-30, CX-5, CX-8 และ Mazda รุ่นอื่นๆ รวมรุ่นไฟฟ้า Mazda 6e และ CX-6e รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('Mazda BT-50 รับไหม', 'ไม่รับ BT-50 และรถกระบะทุกรุ่น รับเฉพาะรุ่นในรายการด้านบน')),
    dict(slug='nissan', key='Nissan', name='Nissan', th='นิสสัน',
         intro='Almera, Kicks e-POWER, X-Trail, Terra, Note, Sylphy และ Nissan รุ่นอื่นๆ รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('Nissan Navara รับไหม', 'ไม่รับ Navara และรถกระบะทุกรุ่น ส่วน Terra ที่เป็นรถอเนกประสงค์ 7 ที่นั่ง รับตามปีในรายการด้านบน')),
    dict(slug='hyundai', key='Hyundai', name='Hyundai', th='ฮุนได',
         intro='Staria, H-1, Grand Starex, Creta, Stargazer, Ioniq 5 และ Hyundai รุ่นอื่นๆ รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ',
         q=('Hyundai H-1 หรือ Staria รับไหม', 'รับ H-1, Grand Starex และ Staria ที่จดทะเบียนเป็นรถส่วนบุคคล (ป้ายขาว) ไม่รับรถตู้ป้ายเหลืองหรือรถสาธารณะ')),
]
BY = {d['slug']: d for d in B}
BY_KEY = {d['key']: d for d in B}


def _cars():
    s = open(_MAIN, encoding='utf-8').read()
    i = s.index('var CARS = '); j = s.index('// END CARS')
    return json.loads(s[i + 11:j].strip().rstrip(';'))


def models(key):
    out = []
    for m, trims in _cars()[key].items():
        ys = [y for v in trims.values() for y in v]
        a, b = max(2016, min(ys)), max(ys)
        out.append((m, f'ปี {a}' if a == b else f'ปี {a}–{b}'))
    return sorted(out, key=lambda x: x[0].lower())


GREEN = re.compile(r'e:HEV|\bHEV\b|Hybrid|PHEV|\bEV\b|Electric|electric|e-POWER|e-Power|\d{3} ?e\b|\be\b|^EQ|^i\d|^iX|Taycan|Leaf|Ioniq|e:N|bZ|6e$|S5 EV|Cyberster|^IM\d')


DIESEL = re.compile(r'\bXD|\b\d{3}d\b|\b\d{3} d\b|[A-Z] \d{3} d\b|Diesel|diesel|CRDi|dCi|\b2\.2 ?D\b|VGS')


def facts(key):   # ข้อมูลเฉพาะยี่ห้อ ดึงจากรายชื่อรุ่นจริงของฟอร์ม (ไม่ใช่ข้อความแม่แบบ): รุ่นไฮบริด/ไฟฟ้า + รุ่นที่เลิกขายรถใหม่แล้ว
    cars = _cars()[key]
    green, old, diesel = [], [], []
    for m, trims in cars.items():
        ys = [y for v in trims.values() for y in v]
        g = sorted({t for t in trims if t and GREEN.search(t)})
        if GREEN.search(m): green.append(m)
        elif g: green.append(f'{m} ({", ".join(g[:3])}{" ฯลฯ" if len(g) > 3 else ""})')
        dz = sorted({t for t in trims if t and DIESEL.search(t)})
        if dz: diesel.append(f'{m} ({", ".join(dz[:2])}{" ฯลฯ" if len(dz) > 2 else ""})')
        if max(ys) <= 2024: old.append(f'{m} (ถึงปี {max(ys)})')
    ntrim = sum(len([t for t in v if t]) for v in cars.values())
    return sorted(green, key=str.lower), sorted(old, key=str.lower), ntrim, sorted(diesel, key=str.lower)


def pages():
    out = {}
    for d in B:
        if d['slug'] == 'toyota': continue
        n, th = d['name'], d['th']
        top = d['intro'].split(' และ ')[0]
        out['Brand@' + d['slug']] = (f'/{d["slug"]}/', f'รับซื้อรถ {d["key"]} มือสอง ({th}) ให้ราคาสูง | ขายรถไว',
                                     f'รับซื้อรถ {d["key"]} ({th}) มือสองทุกรุ่น {top} ถึงหน้าบ้าน ประเมินราคาไว รับรถติดไฟแนนซ์ จ่ายเงินทันที')
    return out


def _facts_block(body, d):
    green, old, ntrim, diesel = facts(d['key'])
    n = d['name']
    H3 = '<h3 style="margin: 8px 0 0; font-family: \'Kanit\', sans-serif; font-weight: 600; font-size: 20px; line-height: 1.35;">{}</h3>'
    P = '<p style="margin: 0; font-size: 16px; line-height: 1.7; color: #3D3B37; max-width: 760px;">{}</p>'
    add = P.format(f'ในรายการของเรามี {n} ทั้งหมด {ntrim} รุ่นย่อย ตั้งแต่ปี 2016 เลือกรุ่นย่อยได้ในฟอร์มด้านบน ราคาที่ได้คิดจากรุ่นย่อยจริง ไม่ใช่ราคากลางของรุ่น')
    if green:
        add += H3.format(f'{n} ไฮบริดและไฟฟ้าที่รับซื้อ') + P.format(', '.join(green))
    if diesel:
        add += H3.format(f'{n} ดีเซลที่รับซื้อ') + P.format(', '.join(diesel))
    if old:
        add += H3.format('รุ่นที่ไม่มีขายรถใหม่แล้ว ก็ยังรับ') + P.format(', '.join(old) + ' ขอแค่ปี 2016 ขึ้นไป ไมล์ไม่เกิน 150,000 กม.')
    i = body.index('รุ่นที่รับซื้อ</h2>')
    a = body.index('</ul>', i) + len('</ul>')
    return body[:a] + add + body[a:]


def transform(body, slug):
    d = BY[slug]
    def rep(a, b, n=1):
        nonlocal body
        assert body.count(a) == n, (slug, a[:60], body.count(a))
        body = body.replace(a, b)
    # breadcrumb: "รับซื้อรถทุกยี่ห้อ" เดิมลิงก์ไป Province.dc.html (= หน้าเชียงใหม่) -> ตัดออก
    rep('<a href="Province.dc.html" style="color: #55534E;">รับซื้อรถทุกยี่ห้อ</a><span aria-hidden="true" style="color: #A8A49B;">›</span><span aria-current="page" style="color: #141414;">Toyota</span>',
        f'<span aria-current="page" style="color: #141414;">รับซื้อรถ {d["name"]}</span>')
    # ยี่ห้ออื่นที่รับซื้อ: เดิมทุกอันลิงก์กลับหน้า Toyota -> ยี่ห้อที่มีหน้าลิงก์จริง ที่เหลือเป็นป้ายเฉยๆ
    i = body.index('>ยี่ห้ออื่นที่รับซื้อ</h2>')
    a = body.index('<div style="display: flex; flex-wrap: wrap; gap: 8px;">', i); b = body.index('</div>', a)
    chips = re.findall(r'<a href="Brand\.dc\.html" (style="[^"]*")>([^<]+)</a>', body[a:b])
    st = chips[0][0]
    span_st = st.replace('text-decoration: none;', '').replace('  ', ' ')
    def chip(nm):
        x = BY_KEY.get(nm)
        return f'<a href="/{x["slug"]}/" {st}>{nm}</a>' if x else f'<span {span_st}>{nm}</span>'
    linked = [x['key'] for x in B if x['key'] != d['key']]
    rest = [nm for _, nm in chips if nm not in linked and nm != d['key']]
    body = body[:a] + '<div style="display: flex; flex-wrap: wrap; gap: 8px;">' + ''.join(chip(nm) for nm in linked + rest) + body[b:]
    k = 'ประเมินราคา Toyota ของคุณ ฟรี'   # กัน "ฟรี" ตกบรรทัดเดี่ยวบนมือถือ
    rep(k, 'ประเมินราคา Toyota <span style="white-space: nowrap;">ของคุณ ฟรี</span>')
    body = _facts_block(body, d)
    if slug == 'toyota':
        return body
    n = d['name']
    rep('<span style="white-space: nowrap;">รับซื้อรถ Toyota</span><br>', f'<span style="white-space: nowrap;">รับซื้อรถ {n}</span><br>')
    rep('Yaris, Vios, Corolla Altis, Camry, Fortuner, Corolla Cross และ Toyota รุ่นอื่นๆ รับทั้งรถติดไฟแนนซ์ ทีมไปดูรถถึงบ้านคุณ', d['intro'])
    rep('ประเมินราคา Toyota <span', f'ประเมินราคา {n} <span')
    ms = models(d['key'])
    rep('>Toyota รุ่นที่รับซื้อ</h2>', f'>{n} รุ่นที่รับซื้อ</h2>')
    rep('>25 รุ่น ตามปีที่ขายในไทย ไม่รับรถกระบะ</p>', f'>{len(ms)} รุ่น ตามปีที่ขายในไทย ปี 2016 ขึ้นไป</p>')
    i = body.index(f'>{n} รุ่นที่รับซื้อ</h2>')
    a = body.index('<ul', i); b = body.index('</ul>', a)
    li = re.search(r'<li style="background: #FFFFFF;[^>]*>', body[a:b]).group(0)
    s1, s2 = re.search(r'<li style="background: #FFFFFF;[^>]*>(<span[^>]*>)[^<]*</span>(<span[^>]*>)', body[a:b]).groups()
    body = body[:a] + body[a:body.index('>', a) + 1] + ''.join(f'{li}{s1}{m}</span>{s2}{y}</span></li>' for m, y in ms) + body[b:]
    rep('>คำถามเรื่องขาย Toyota</h2>', f'>คำถามเรื่องขาย {n}</h2>')
    rep('Toyota ยังผ่อนไม่หมด ขายได้ไหม', f'{n} ยังผ่อนไม่หมด ขายได้ไหม')
    rep('Fortuner หรือ Toyota อเนกประสงค์ รับไหม', d['q'][0])
    rep('รับ Fortuner และ Toyota ทุกรุ่นในรายการด้านบน ยกเว้นรถกระบะ', d['q'][1])
    body = body.replace('Toyota ที่รับซื้อล่าสุด', f'{n} ที่รับซื้อล่าสุด').replace('Toyota [รุ่น', f'{n} [รุ่น')   # ส่วน placeholder นี้ patches ตัดทิ้งอยู่แล้ว
    rep('>ขาย Toyota อยากรู้ราคา</h2>', f'>ขาย {n} อยากรู้ราคา</h2>')
    i = body.index('>ยี่ห้ออื่นที่รับซื้อ</h2>'); j = body.index('</div>', i)
    assert 'Toyota' not in body[:i] + body[j:], (slug, 'leftover Toyota')
    return body
