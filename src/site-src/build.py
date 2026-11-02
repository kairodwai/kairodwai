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
                  'ขายรถไว รับซื้อรถยนต์มือสองถึงหน้าบ้านทุกจังหวัด กรอกข้อมูลรถ ส่งรูป ได้ราคาไว จ่ายเงินทันทีใน 1 ชั่วโมง รถติดไฟแนนซ์ก็ขายได้'),
    'Brand':     ('/toyota/',     'รับซื้อรถ Toyota มือสอง ให้ราคาสูง | ขายรถไว',
                  'รับซื้อรถ Toyota มือสองทุกรุ่น Yaris, Vios, Altis, Camry, Fortuner ถึงหน้าบ้าน ประเมินราคาไว จ่ายเงินทันที'),
    'Province':  ('/chiang-mai/', 'รับซื้อรถมือสอง เชียงใหม่ ถึงหน้าบ้าน | ขายรถไว',
                  'รับซื้อรถยนต์มือสองในเชียงใหม่ ทีมเข้าดูรถถึงบ้าน ประเมินราคาไว จ่ายเงินทันที รถติดไฟแนนซ์ก็ขายได้'),
    'Portfolio': ('/portfolio/',  'ผลงานรับซื้อรถ | ขายรถไว',
                  'ตัวอย่างรถที่ขายรถไวรับซื้อมาแล้ว ทั่วประเทศ'),
    'Finance':   ('/finance/',    'ขายรถติดไฟแนนซ์ ทำยังไง | ขายรถไว',
                  'คู่มือขายรถที่ยังผ่อนไม่หมด ปิดไฟแนนซ์ยังไง ได้เงินส่วนต่างเท่าไหร่ ขายรถไวจัดการให้ครบ'),
    'Docs':      ('/documents/',  'เอกสารที่ต้องใช้ขายรถ | ขายรถไว',
                  'เตรียมเอกสารขายรถให้ครบ เล่มทะเบียน บัตรประชาชน และเอกสารกรณีรถติดไฟแนนซ์'),
    'Privacy':   ('/privacy/',    'นโยบายความเป็นส่วนตัว | ขายรถไว',
                  'นโยบายความเป็นส่วนตัวของขายรถไว'),
}
LINKS = {'Mobile.dc.html': '/', 'Main.dc.html': '/'}
LINKS.update({k + '.dc.html': v[0] for k, v in PAGES.items()})
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}
ATTR_RE = re.compile(r'''\s([^\s=/>"']+)(?:\s*=\s*("[^"]*"|'[^']*'|[^\s>]+))?''')
WHOLE = re.compile(r'^\s*\{\{\s*([^}]*?)\s*\}\}\s*$')


IMG_MAP = json.load(open(os.path.join(HERE, 'img_map.json'))) if os.path.exists(os.path.join(HERE, 'img_map.json')) else {}


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
    '@media(prefers-reduced-motion:reduce){.kr-ov,.kr-sheet{animation:none}}')


def page_html(name, helmet, tree, logic, prerender=''):
    path, title, desc = PAGES[name]
    url = DOMAIN + path
    helmet = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com">\s*', '', helmet)
    return f'''<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="ขายรถไว">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{DOMAIN}/img/og.jpg">
<meta name="theme-color" content="#F5F4F0">
<link rel="icon" type="image/png" sizes="32x32" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{helmet.strip()}
<style>{SHEET_CSS}</style>
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


def main():
    pre = {}
    pre_file = os.path.join(HERE, 'prerender.json')
    if '--prerender' in sys.argv and os.path.exists(pre_file):
        pre = json.load(open(pre_file, encoding='utf-8'))
    os.makedirs(OUT, exist_ok=True)
    patches = __import__('patches')
    for name in PAGES:
        helmet, body, logic = split_page(os.path.join(DESIGN, 'project', name + '.dc.html'))
        body, logic = patches.apply(name, body, logic)
        c = Compiler(); c.feed(body); c.close()
        strip_ws(c.root)
        d = os.path.join(OUT, PAGES[name][0].strip('/'))
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(
            page_html(name, helmet, c.root['kids'], logic, pre.get(name, '')))
    # ไฟล์ประกอบ
    os.makedirs(os.path.join(OUT, 'assets'), exist_ok=True)
    os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
    shutil.copy(os.path.join(SRC, 'vendor/preact.min.umd.js'), os.path.join(OUT, 'assets/preact.min.js'))
    shutil.copy(os.path.join(HERE, 'dc.js'), os.path.join(OUT, 'assets/dc.js'))
    shutil.copy(os.path.join(HERE, 'site.js'), os.path.join(OUT, 'assets/site.js'))
    for f in os.listdir(DESIGN):  # page photos live in <repo>/img; design/*.jpg only if re-exported from Claude Design
        if f.endswith('.jpg'): shutil.copy(os.path.join(DESIGN, f), os.path.join(OUT, 'img', f))
    print('built', OUT)




def build_line():
    s = open(os.path.join(SRC, 'line-page/index.html'), encoding='utf-8').read()
    os.makedirs(os.path.join(OUT, 'line'), exist_ok=True)
    open(os.path.join(OUT, 'line/index.html'), 'w', encoding='utf-8').write(s)


def extras():
    os.makedirs(os.path.join(OUT, 'img'), exist_ok=True)
    shutil.copy(os.path.join(HERE, 'og.jpg'), os.path.join(OUT, 'img/og.jpg'))
    shutil.copy(os.path.join(HERE, 'logo.png'), os.path.join(OUT, 'img/logo.png'))
    shutil.copy(os.path.join(HERE, 'logo-light.png'), os.path.join(OUT, 'img/logo-light.png'))
    shutil.copy(os.path.join(HERE, 'favicon.png'), os.path.join(OUT, 'favicon.png'))
    shutil.copy(os.path.join(HERE, 'favicon.ico'), os.path.join(OUT, 'favicon.ico'))  # browsers that ask /favicon.ico by default
    shutil.copy(os.path.join(HERE, 'apple-touch-icon.png'), os.path.join(OUT, 'apple-touch-icon.png'))
    open(os.path.join(OUT, 'CNAME'), 'w').write('kairodwai.com\n')
    urls = [DOMAIN + v[0] for v in PAGES.values()]
    open(os.path.join(OUT, 'sitemap.xml'), 'w').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        ''.join(f'  <url><loc>{u}</loc></url>\n' for u in urls) + '</urlset>\n')
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
