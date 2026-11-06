#!/usr/bin/env python3
"""สร้างเว็บ kairodwai.com จากไฟล์ดีไซน์ .dc.html"""
import html, json, os, re, shutil, sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))        # <repo>/src/site-src
SRC = os.path.dirname(HERE)                               # <repo>/src
ROOT = os.path.dirname(SRC)                               # <repo> = GitHub Pages root
DESIGN = os.path.join(SRC, 'design')                      # design/project/*.dc.html (+ optional *.jpg)
OUT = os.environ.get('KR_OUT') or ROOT                    # build in place; KR_OUT=/tmp/x for a dry run
DOMAIN = 'https://kairodwai.com'

PAGES = {
    'Main':      ('/',            'รับซื้อรถมือสอง ถึงหน้าบ้าน ให้ราคาไว | ขายรถไว',
                  'ขายรถไว รับซื้อรถยนต์มือสองถึงหน้าบ้านคุณ กรอกข้อมูลรถ ส่งรูป ได้ราคาไว จ่ายเงินทันทีใน 1 ชั่วโมง รถติดไฟแนนซ์ก็ขายได้'),
    'Brand':     ('/toyota/',     'รับซื้อรถ Toyota มือสอง ให้ราคาสูง | ขายรถไว',
                  'รับซื้อรถ Toyota มือสองทุกรุ่น Yaris, Vios, Altis, Camry, Fortuner ถึงหน้าบ้าน ประเมินราคาไว จ่ายเงินทันที'),
    'Province':  ('/chiang-mai/', 'รับซื้อรถมือสอง เชียงใหม่ ถึงหน้าบ้าน | ขายรถไว',
                  'รับซื้อรถยนต์มือสองในเชียงใหม่ ทีมเข้าดูรถถึงบ้าน ประเมินราคาไว จ่ายเงินทันที รถติดไฟแนนซ์ก็ขายได้'),
    'Portfolio': ('/portfolio/',  'ผลงานรับซื้อรถ | ขายรถไว',
                  'ตัวอย่างรถที่ขายรถไวรับซื้อมาแล้ว'),
    'Price':     ('/check-price/', 'ประเมินราคารถมือสองฟรี รู้ราคาจริงใน 5 นาที | ขายรถไว',
                  'ประเมินราคารถมือสองฟรี กรอกรุ่น ปี ไมล์ ส่งรูป 5 มุม ทีมรับซื้อแจ้งราคาจริงจากสภาพรถคุณภายใน 5 นาที พร้อมวิธีเช็คราคาเองให้แม่น'),
    'Finance':   ('/finance/',    'ขายรถติดไฟแนนซ์ ทำยังไง | ขายรถไว',
                  'คู่มือขายรถที่ยังผ่อนไม่หมด ปิดไฟแนนซ์ยังไง ได้เงินส่วนต่างเท่าไหร่ ขายรถไวจัดการให้ครบ'),
    'Docs':      ('/documents/',  'โอนรถมือสอง ใช้เอกสารอะไร ค่าธรรมเนียมเท่าไหร่ | ขายรถไว',
                  'เอกสารขายรถและโอนรถมือสอง: โอนต่อหน้านายทะเบียนกับโอนลอยต่างกันยังไง เอกสารที่ขนส่งใช้ ขั้นตอน ค่าธรรมเนียมโอน และต้องแจ้งภายใน 15 วัน'),
    'Privacy':   ('/privacy/',    'นโยบายความเป็นส่วนตัว | ขายรถไว',
                  'นโยบายความเป็นส่วนตัวของขายรถไว เราเก็บข้อมูลอะไร ใช้ทำอะไร เก็บนานแค่ไหน และคุณขอดูหรือขอลบข้อมูลของตัวเองได้อย่างไร'),
}
LINKS = {'Mobile.dc.html': '/', 'Main.dc.html': '/'}
LINKS.update({k + '.dc.html': v[0] for k, v in PAGES.items()})
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
ATTR_RE = re.compile(r'''\s([^\s=/>"']+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?''')
WHOLE = re.compile(r'^\s*\{\{\s*([^}]*?)\s*\}\}\s*$')


HIDDEN = {'Portfolio'}   # หน้าที่ยังไม่มีข้อมูลจริง: noindex + ไม่อยู่ใน sitemap + ไม่มีลิงก์เข้า (patches.common)
ROBOTS_NOINDEX = '\n<meta name="robots" content="noindex">'
PLACEHOLDER = re.compile(r'\[[^\]{}"<>0-9,\'\[]*[\u0e00-\u0e7f][^\]{}"<>]{0,60}\]')   # ข้อความในวงเล็บเหลี่ยมภาษาไทย = placeholder ที่ยังไม่ได้ใส่ข้อมูลจริง

# Google Ads (บัญชี ขายรถไว · kairodwai 861-119-9182): โหลด tag ทุกหน้า (/, /go, /line/) — gclid จากแอดถูกเก็บเป็นคุกกี้ในเบราว์เซอร์ไลน์ตอนเปิดหน้าแรก แล้ว /line/ ยิง conversion "ส่งรูปครบ" ตอนรูปครบ
AW_ID = 'AW-11123976879'
AW_PHOTOS_DONE = AW_ID + '/I3aICJOklrEdEK_Vqbgp'   # conversion "ส่งรูปครบ (photos complete)" — primary, Submit lead form, 1,666 บาท/ครั้ง, นับครั้งเดียวต่อคลิก
META_PIXEL = '4292793881011346'   # Meta Pixel "ขายรถไว เว็บ" (บัญชีธุรกิจ ขายรถไว)
META_PX = ("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');"
           f"window.KR_PX='{META_PIXEL}';fbq('init','{META_PIXEL}');fbq('track','PageView');</script>")
GTAG = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={AW_ID}"></script>'
        f"<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag('js',new Date());gtag('config','{AW_ID}');window.KR_AW='{AW_PHOTOS_DONE}';</script>"
        + META_PX)

IMG_MAP = json.load(open(os.path.join(HERE, 'img_map.json'))) if os.path.exists(os.path.join(HERE, 'img_map.json')) else {}

# รูปประกอบหน้าเว็บ: jpg ต้นฉบับอยู่ <repo>/img → build ทำ .webp (เบากว่า ~3 เท่า ภาพเท่าเดิม) + ตัวย่อ 800px สำหรับมือถือ แล้วใส่ srcset/lazy ให้ทุก <img>
IMG_SIZES = {}                                            # hash → ความกว้างต้นฉบับ (เติมตอน make_webp)
def make_webp():
    try: from PIL import Image
    except ImportError: print('no PIL: skip webp'); return
    d = os.path.join(OUT, 'img'); src_d = os.path.join(ROOT, 'img')
    os.makedirs(d, exist_ok=True)
    for f in os.listdir(src_d):
        if not re.match(r'^[0-9a-f]{32}\.jpg$', f): continue
        h = f[:-4]; im = Image.open(os.path.join(src_d, f)).convert('RGB'); IMG_SIZES[h] = im.width
        full = os.path.join(d, h + '.webp'); small = os.path.join(d, h + '-800.webp')
        if not os.path.exists(full): im.save(full, 'WEBP', quality=78, method=6)
        if im.width > 800 and not os.path.exists(small):
            s = im.copy(); s.thumbnail((800, 800 * im.height // im.width)); s.save(small, 'WEBP', quality=76, method=6)
        mid = os.path.join(d, h + '-1200.webp')                                 # จอมือถือ 3x เลือกตัวนี้ (คมพอ ไม่ต้องโหลด 1600)
        if im.width > 1200 and not os.path.exists(mid):
            s = im.copy(); s.thumbnail((1200, 1200 * im.height // im.width)); s.save(mid, 'WEBP', quality=76, method=6)
        elif im.width <= 800: IMG_SIZES[h] = -im.width                   # ติดลบ = ไม่มีตัวย่อ

def img_attrs(attrs):
    cls = next((a.get('v', '') for a in attrs if a['n'] == 'class'), '')
    for a in attrs:
        if a['n'] == 'src' and 'v' in a:
            m = re.match(r'^/img/([0-9a-f]{32})\.jpg$', a['v'])
            if m and m.group(1) in IMG_SIZES:
                h, w = m.group(1), IMG_SIZES[m.group(1)]
                a['v'] = '/img/' + h + '.webp'
                if w > 800:
                    ss = '/img/%s-800.webp 800w, ' % h + ('/img/%s-1200.webp 1200w, ' % h if w > 1200 else '') + '/img/%s.webp %dw' % (h, w)
                    attrs.append({'n': 'srcset', 'v': ss})
                    attrs.append({'n': 'sizes', 'v': '(max-width: 760px) 100vw, 600px'})
    src = next((a.get('v', '') for a in attrs if a['n'] == 'src'), '')
    attrs.append({'n': 'decoding', 'v': 'async'})
    if 'hero' in cls: attrs.append({'n': 'fetchpriority', 'v': 'high'})   # รูปแรกบนจอ = LCP โหลดก่อน
    elif 'logo' not in src: attrs.append({'n': 'loading', 'v': 'lazy'})  # รูปอื่นโหลดเมื่อเลื่อนถึง (โลโก้บนหัวไม่ lazy)


def fix_val(v):
    v = LINKS.get(v, v)
    def img(m):
        d = IMG_MAP.get(m.group(1))
        return 'https://lh3.googleusercontent.com/d/' + d + '=w1200' if d else '/img/' + m.group(1) + '.jpg'
    v = re.sub(r'/_blob/([0-9a-f]{32})', img, v)
    return v


class Compiler(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {'kids': []}
        self.stack = [self.root]

    def _node(self, tag):
        raw = self.get_starttag_text()
        names = [m.group(1) for m in ATTR_RE.finditer(raw[len(tag) + 1:])]
        vals = [m.group(2) for m in ATTR_RE.finditer(raw[len(tag) + 1:])]
        attrs = []
        ttype = ''
        for n, v in zip(names, vals):
            if v is None: v = ''
            elif v[0] in '"\'': v = v[1:-1]
            v = html.unescape(v)
            if n.lower() == 'type': ttype = v
        text_input = tag == 'textarea' or (tag == 'input' and not re.match(r'^(checkbox|radio|file|submit|button)$', ttype, re.I))
        for n, v in zip(names, vals):
            if v is None: v = ''
            elif v[0] in '"\'': v = v[1:-1]
            v = fix_val(html.unescape(v))
            if n.startswith('hint-'): continue
            if n == 'onChange' and text_input: n = 'onInput'
            m = WHOLE.match(v)
            if m: attrs.append({'n': n, 'p': m.group(1)})
            elif '{{' in v: attrs.append({'n': n, 's': v})
            else: attrs.append({'n': n, 'v': v})
        if tag == 'sc-if':
            p = next((a.get('p') or a.get('v') for a in attrs if a['n'] == 'value'), 'false')
            return {'k': 'if', 'p': p, 'kids': []}
        if tag == 'sc-for':
            p = next((a.get('p') or a.get('v') for a in attrs if a['n'] == 'list'), '')
            a_ = next((a.get('v') for a in attrs if a['n'] == 'as'), 'item')
            return {'k': 'for', 'p': p, 'as': a_, 'kids': []}
        if tag == 'img': img_attrs(attrs)
        return {'k': 'e', 'tag': tag, 'attrs': attrs, 'kids': []}

    def handle_starttag(self, tag, attrs):
        n = self._node(tag)
        self.stack[-1]['kids'].append(n)
        if tag not in VOID: self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.stack[-1]['kids'].append(self._node(tag))

    def handle_endtag(self, tag):
        if tag in VOID: return
        for i in range(len(self.stack) - 1, 0, -1):
            n = self.stack[i]
            if n.get('tag') == tag or (n['k'] == 'if' and tag == 'sc-if') or (n['k'] == 'for' and tag == 'sc-for'):
                del self.stack[i:]
                return

    def handle_data(self, data):
        k = self.stack[-1]['kids']
        if '{{' in data:
            parts, last = [], 0
            for m in re.finditer(r'\{\{\s*([^}]*?)\s*\}\}', data):
                if m.start() > last: parts.append(data[last:m.start()])
                parts.append({'p': m.group(1)})
                last = m.end()
            if last < len(data): parts.append(data[last:])
            k.append({'k': 'x', 'parts': parts})
        else:
            k.append({'k': 't', 'v': data})


def strip_ws(n):
    """ตัดช่องว่างระหว่างแท็กที่เป็นแค่ขึ้นบรรทัด (ไม่กระทบหน้าตา) ให้ไฟล์เล็กลง"""
    if 'kids' not in n: return
    out = []
    for c in n['kids']:
        if c['k'] == 't' and c['v'].strip() == '' and '\n' in c['v']:
            continue
        strip_ws(c); out.append(c)
    n['kids'] = out


def split_page(path):
    s = open(path, encoding='utf-8').read()
    helmet = re.search(r'<helmet>(.*?)</helmet>', s, re.S).group(1)
    body = re.search(r'</helmet>(.*?)</x-dc>', s, re.S).group(1)
    logic = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', s, re.S).group(1)
    return helmet, body, logic


def js_safe(t):
    return t.replace('</', '<\\/')


# แผ่นเงื่อนไขเมื่อกดปุ่มไลน์: bottom sheet บนมือถือ, กล่องกลางจอบนคอม (เด้งทันทีที่กด ให้รู้ว่ามาจากปุ่มนั้น)
LIFF_WEB_ID = '2012318037-06TwYIml'   # LIFF app "kairodwai-web" (LINE Login channel 2012318037, endpoint https://kairodwai.com/) — ว่าง = ยังไม่เปิดโหมดเปิดในไลน์
SHEET_CSS = ('.kr-ov{position:fixed;inset:0;background:rgba(20,20,20,.55);z-index:9990;animation:krFade .2s}'
    '.kr-sheet{position:fixed;left:0;right:0;bottom:0;z-index:9991;background:#FFFFFF;color:#141414;border-radius:24px 24px 0 0;'
    'padding:12px 24px calc(24px + env(safe-area-inset-bottom,0px));display:flex;flex-direction:column;gap:16px;max-width:560px;margin:0 auto;'
    'box-sizing:border-box;animation:krUp .25s ease-out}'
    '.kr-grab{width:40px;height:4px;border-radius:2px;background:#DEDBD3;align-self:center;margin-bottom:4px}'
    '@media(min-width:720px){.kr-sheet{bottom:auto;top:50%;left:50%;right:auto;transform:translate(-50%,-50%);border-radius:24px;'
    'padding:32px;width:min(480px,calc(100% - 48px));animation:krPop .2s ease-out}.kr-grab{display:none}}'
    '@keyframes krUp{from{transform:translateY(32px);opacity:0}to{transform:none;opacity:1}}'
    '@keyframes krPop{from{transform:translate(-50%,-50%) scale(.96);opacity:0}to{transform:translate(-50%,-50%);opacity:1}}'
    '@keyframes krFade{from{opacity:0}}'
    '@media(prefers-reduced-motion:reduce){.kr-ov,.kr-sheet{animation:none}}'
    '.via-liff .kr-line{display:none!important}')   # เปิดในไลน์ (LIFF): เป็นเพื่อนกันแล้ว ไม่ต้องมีปุ่มแอดไลน์


def page_html(name, helmet, tree, logic, prerender='', ld=''):
    path, title, desc = PAGES[name]
    url = DOMAIN + path
    helmet = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com">\s*', '', helmet)
    return f'''<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="facebook-domain-verification" content="6qio2m0h19tu6rmc24q9r7ozlmnm6x" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">{ROBOTS_NOINDEX if name in HIDDEN else ''}
<meta property="og:type" content="website">
<meta property="og:site_name" content="ขายรถไว">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/img/og.jpg">
<meta name="theme-color" content="#F5F4F0">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="manifest" href="/manifest.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{helmet.strip()}
<style>{SHEET_CSS}</style>
{ld}{GTAG}
<script>window.KR_LIFF_ID='{LIFF_WEB_ID}';</script>
<script src="/assets/preact.min.js" defer></script>
<script src="/assets/site.js" defer></script>
<script src="/assets/dc.js" defer></script>
</head>
<body>
<div id="root">{prerender}</div>
<script type="application/json" id="dc-tpl">{js_safe(json.dumps(tree, ensure_ascii=False, separators=(',', ':')))}</script>
<script type="text/x-dc" id="dc-logic">{js_safe(logic)}</script>
</body>
</html>
'''


CRUMB = {'Price': 'ประเมินราคารถมือสอง', 'Brand': 'รับซื้อรถ Toyota', 'Province': 'รับซื้อรถมือสอง เชียงใหม่', 'Finance': 'ขายรถติดไฟแนนซ์', 'Docs': 'เอกสารขายรถ · โอนรถ', 'Privacy': 'นโยบายความเป็นส่วนตัว'}


def json_ld(name, pre_html):
    """structured data (Google + AI อ่านว่าเราเป็นใคร ทำอะไร): Organization, WebSite, Service, FAQPage (จากคำถามในหน้า), BreadcrumbList
    ไม่ใส่ชื่อบริษัท/ที่อยู่ (Moss 5 พ.ย. 69 ไม่เอา) · FAQ อ่านจากหน้าที่ prerender แล้ว = ตรงกับที่คนเห็นเป๊ะ (กฎ Google: schema ต้องตรงกับเนื้อหาบนหน้า)"""
    path, title, desc = PAGES[name]
    url = DOMAIN + path
    org = {'@type': 'Organization', '@id': DOMAIN + '/#org', 'name': 'ขายรถไว', 'alternateName': 'Kairodwai', 'url': DOMAIN + '/',
           'logo': DOMAIN + '/icon-512.png', 'areaServed': {'@type': 'Country', 'name': 'Thailand'}}
    g = [org, {'@type': 'WebSite', '@id': DOMAIN + '/#site', 'url': DOMAIN + '/', 'name': 'ขายรถไว', 'inLanguage': 'th', 'publisher': {'@id': DOMAIN + '/#org'}},
         {'@type': 'WebPage', '@id': url + '#page', 'url': url, 'name': title, 'description': desc, 'inLanguage': 'th', 'isPartOf': {'@id': DOMAIN + '/#site'}}]
    if name in ('Main', 'Price', 'Brand', 'Province', 'Finance'):
        svc = {'@type': 'Service', '@id': url + '#service', 'serviceType': 'รับซื้อรถยนต์มือสอง', 'name': title.split(' | ')[0], 'description': desc,
               'provider': {'@id': DOMAIN + '/#org'}, 'areaServed': {'@type': 'Country', 'name': 'Thailand'}, 'url': url}
        if name == 'Province':
            svc['areaServed'] = {'@type': 'AdministrativeArea', 'name': 'เชียงใหม่'}
        g.append(svc)
    qa = re.findall(r'<summary[^>]*>\s*<span>(.*?)</span>.*?</summary>\s*<p[^>]*>(.*?)</p>', pre_html or '', re.S)
    clean = lambda t: html.unescape(re.sub(r'<[^>]+>', '', t)).strip()
    if qa:
        g.append({'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
            {'@type': 'Question', 'name': clean(q), 'acceptedAnswer': {'@type': 'Answer', 'text': clean(a)}} for q, a in qa]})
    if name in CRUMB:
        g.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'ขายรถไว', 'item': DOMAIN + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': CRUMB[name], 'item': url}]})
    data = json.dumps({'@context': 'https://schema.org', '@graph': g}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return '<script type="application/ld+json">' + data + '</script>\n'


def lastmod(name):   # วันที่แก้หน้าจริงล่าสุด (git) — Google ใช้ lastmod เมื่อมันตรงกับความจริงเท่านั้น
    import subprocess
    files = [os.path.join(DESIGN, 'project', name + '.dc.html'), os.path.join(HERE, 'patches.py')]
    try:
        out = subprocess.run(['git', 'log', '-1', '--format=%cs', '--'] + files, cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return out or None
    except Exception:
        return None


def main():
    pre = {}
    pre_file = os.path.join(HERE, 'prerender.json')
    if '--prerender' in sys.argv and os.path.exists(pre_file):
        pre = json.load(open(pre_file, encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    make_webp()
    patches = __import__('patches')
    for name in PAGES:
        helmet, body, logic = split_page(os.path.join(DESIGN, 'project', name + '.dc.html'))
        body, logic = patches.apply(name, body, logic)
        c = Compiler(); c.feed(body); c.close()
        strip_ws(c.root)
        d = os.path.join(OUT, PAGES[name][0].strip('/'))
        os.makedirs(d, exist_ok=True)
        out_html = page_html(name, helmet, c.root['kids'], logic, pre.get(name, ''), '' if name in HIDDEN else json_ld(name, pre.get(name, '')))
        # content gate: placeholder ภาษาไทยในวงเล็บเหลี่ยม = ข้อมูลที่ยังไม่ได้ใส่ — หน้าแรก (หน้าที่แอดพามา) ห้ามมีเลย, หน้าอื่นเตือน
        ph = sorted(set(m for m in PLACEHOLDER.findall(out_html) if not m.startswith("['")))
        if ph:
            print(('BLOCK ' if name == 'Main' else 'WARN  ') + PAGES[name][0] + ' placeholder: ' + ' '.join(ph))
            if name == 'Main': sys.exit('content gate: หน้าแรกยังมี placeholder')
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(out_html)
    # ไฟล์ประกอบ
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
    shutil.copy(os.path.join(SRC, 'vendor/preact.min.umd.js'), os.path.join(OUT, 'assets/preact.min.js'))
    shutil.copy(os.path.join(HERE, 'dc.js'), os.path.join(OUT, 'assets/dc.js'))
    shutil.copy(os.path.join(HERE, 'site.js'), os.path.join(OUT, 'assets/site.js'))
    shutil.copy(os.path.join(SRC, 'vendor/qrcode.min.js'), os.path.join(OUT, 'assets/qrcode.min.js'))   # QR บนหน้า /line/ (เปิดจากคอม → สแกนไปส่งรูปในไลน์) — qrcode-generator 1.4.4 MIT
    for f in os.listdir(DESIGN):  # page photos live in <repo>/img; design/*.jpg only if re-exported from Claude Design
        if f.endswith('.jpg'): shutil.copy(os.path.join(DESIGN, f), os.path.join(OUT, 'img', f))
    print('built', OUT)




def build_line():
    s = open(os.path.join(SRC, 'line-page/index.html'), encoding='utf-8').read()
    os.makedirs(os.path.join(OUT, 'line'), exist_ok=True)
    open(os.path.join(OUT, 'line/index.html'), 'w', encoding='utf-8').write(s.replace('__LIFF_WEB_ID__', LIFF_WEB_ID).replace('</head>', GTAG + '\n</head>', 1))


def extras():
    os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
    shutil.copy(os.path.join(HERE, 'og.jpg'), os.path.join(OUT, 'img/og.jpg'))
    shutil.copy(os.path.join(HERE, 'logo.png'), os.path.join(OUT, 'img/logo.png'))
    shutil.copy(os.path.join(HERE, 'logo-light.png'), os.path.join(OUT, 'img/logo-light.png'))
    shutil.copy(os.path.join(HERE, 'richmenu-wait.png'), os.path.join(OUT, 'img/richmenu-wait.png'))
    shutil.copy(os.path.join(HERE, 'richmenu-lead.png'), os.path.join(OUT, 'img/richmenu-lead.png'))
    os.makedirs(os.path.join(OUT, 'img/ico'), exist_ok=True)   # ไอคอนเส้นบนปุ่มการ์ดกลุ่มทีม (LINE flex ดึงจาก URL นี้)
    for f in os.listdir(os.path.join(HERE, 'ico')): shutil.copy(os.path.join(HERE, 'ico', f), os.path.join(OUT, 'img/ico', f))   # เมนูล่าง "รอรูปรถของคุณ | โทรหาเรา" (กรอกฟอร์มแล้ว ยังไม่ส่งรูป — setupLeadMenu)
    os.makedirs(os.path.join(OUT, 'go'), exist_ok=True)
    open(os.path.join(OUT, 'go/index.html'), 'w', encoding='utf-8').write(open(os.path.join(HERE, 'go.html'), encoding='utf-8').read().replace('__LIFF_WEB_ID__', LIFF_WEB_ID).replace('</head>', GTAG + '</head>', 1))   # ลิงก์โฆษณา kairodwai.com/go → เด้งเข้า LIFF (มือถือ) / เว็บธรรมดา (คอม)  # เมนูล่าง LINE "รอประเมินราคา" (Apps Script setupWaitMenu ดึงจาก URL นี้)
    shutil.copy(os.path.join(HERE, 'favicon.png'), os.path.join(OUT, 'favicon.png'))
    shutil.copy(os.path.join(HERE, 'favicon.ico'), os.path.join(OUT, 'favicon.ico'))  # browsers that ask /favicon.ico by default
    shutil.copy(os.path.join(HERE, 'apple-touch-icon.png'), os.path.join(OUT, 'apple-touch-icon.png'))
    for f in ('manifest.webmanifest', 'icon-192.png', 'icon-512.png', 'icon-maskable-512.png', 'sw.js'):   # ไอคอน + service worker = ติดตั้งเป็นแอปจริง (WebAPK)
        shutil.copy(os.path.join(HERE, f), os.path.join(OUT, f))
    os.makedirs(os.path.join(OUT, 'app'), exist_ok=True)   # /app/ = หน้าลับไว้ติดตั้งแอป (noindex ไม่อยู่ใน sitemap)
    shutil.copy(os.path.join(HERE, 'app.html'), os.path.join(OUT, 'app', 'index.html'))
    open(os.path.join(OUT, 'CNAME'), 'w').write('kairodwai.com\n')
    open(os.path.join(OUT, 'googlef54c075a0606bad3.html'), 'w').write('google-site-verification: googlef54c075a0606bad3.html')   # ไฟล์ยืนยัน Google Search Console (Moss อนุมัติ 6 พ.ย. 69) ห้ามลบ
    urls = [(DOMAIN + v[0], lastmod(k)) for k, v in PAGES.items() if k not in HIDDEN]
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{u}</loc>' + (f'<lastmod>{d}</lastmod>' if d else '') + '</url>\n' for u, d in urls) + '</urlset>\n')
    open(os.path.join(OUT, 'robots.txt'), 'w').write(f'User-agent: *\nDisallow: /line/\nSitemap: {DOMAIN}/sitemap.xml\n')
    open(os.path.join(OUT, '404.html'), 'w', encoding='utf-8').write(
        '<!doctype html><html lang="th"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>ไม่พบหน้านี้ | ขายรถไว</title><body style="margin:0;font-family:system-ui,sans-serif;background:#F5F4F0;color:#141414;'
        'display:grid;place-items:center;min-height:100vh;text-align:center;padding:24px"><div><h1 style="font-size:24px">ไม่พบหน้านี้</h1>'
        '<p><a href="/" style="color:#141414">กลับหน้าแรก ขายรถไว</a></p></div></body></html>')


if __name__ == '__main__':
    build_line(); extras()

    sys.path.insert(0, HERE)
    main()
