"""ปรับดีไซน์ให้ใช้งานจริง: ขอราคา -> ส่งเข้าระบบ -> ถ่ายรูปผ่านเว็บ (ไม่มีทางลัดไปไลน์ก่อนส่งรูป)"""
import re

CAM = '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex-shrink: 0;"><path d="M4 8h3l2-3h6l2 3h3v11H4z"></path><circle cx="12" cy="13" r="3.5"></circle></svg>'

NEW_SENT = '''<sc-if value="{{ refNo }}" hint-placeholder-val="{{ false }}">
<span style="font-size: 15px; color: #3D3B37;">รหัสอ้างอิง <b style="font-family: 'Kanit', sans-serif; font-weight: 600; font-size: 17px; color: #141414; letter-spacing: 0.5px;">{{ refNo }}</b></span>
</sc-if>
<sc-if value="{{ photoHref }}" hint-placeholder-val="{{ true }}">
<div style="align-self: stretch; display: flex; flex-direction: column; gap: 10px;">
<a href="{{ photoHref }}" style="display: flex; align-items: center; justify-content: center; gap: 10px; height: 56px; border-radius: 28px; background: #141414; text-decoration: none; font-family: 'Kanit', sans-serif; font-weight: 500; font-size: 18px; color: #FFFFFF;">''' + CAM + '''<span>ถ่ายรูปรถ 6 มุม ได้ราคาไวขึ้น</span></a>
<span style="font-size: 14px; color: #55534E;">ถ่ายจากมือถือได้เลย ใช้เวลาราว 2 นาที รูปส่งถึงทีมทันที</span>
</div>
</sc-if>
'''


HDR_OLD = '''<span style="font-family: 'Kanit', sans-serif; font-weight: 600; font-size: 24px; line-height: 1.1; letter-spacing: 0.5px; white-space: nowrap;">ขายรถไว</span>'''
HDR_NEW = '''<img src="/img/logo.png" alt="ขายรถไว" width="444" height="120" style="display: block; height: 30px; width: auto; align-self: flex-start;">'''
FTR_OLD = '''<span style="font-family: 'Kanit', sans-serif; font-size: 22px; font-weight: 600; color: #F5F4F0;">ขายรถไว</span>'''
FTR_NEW = '''<img src="/img/logo-light.png" alt="ขายรถไว" width="444" height="120" style="display: block; height: 26px; width: auto; align-self: flex-start;">'''

# ---- หน้าคัดกรองก่อนเข้าฟอร์ม: พร้อมขายไหม (กดปุ่มเดียว ไม่ต้องกรอก) ----
# "แค่มาเช็คราคา" ต้องกดค้าง 2 วิ (กันมือลั่น) -> หน้าแดงเต็มจอ บอกเหตุผล 3 ข้อ ไม่มีเบอร์/ไลน์ ไม่มีปุ่มเปลี่ยนใจ จำไว้ในเครื่อง 24 ชม. (ล้างด้วย ?kr=reset)
NUM = '''<span style="flex-shrink: 0; width: 28px; height: 28px; border-radius: 50%; border: 1px solid rgba(255,255,255,0.7); display: flex; align-items: center; justify-content: center; font-family: 'Kanit', sans-serif; font-weight: 600; font-size: 14px; line-height: 1;">'''
GATE = '''<sc-if value="{{ gateOn }}" hint-placeholder-val="{{ false }}">
<div style="display: flex; flex-direction: column; gap: 22px;">
<div style="display: flex; flex-direction: column; gap: 6px;">
<span style="font-size: 14px; font-weight: 500; color: #55534E;">ขายง่ายๆ ใน 3 ขั้นตอน · ใช้เวลาไม่ถึง 1 นาที</span>
<h2 style="margin: 0; font-family: 'Kanit', sans-serif; font-weight: 600; font-size: 26px; line-height: 1.3;">พร้อมขายรถตอนนี้ไหม?</h2>
<p style="margin: 0; font-size: 15px; line-height: 1.6; color: #3D3B37;">ทีมไปดูรถถึงบ้าน ประเมินฟรี ตรวจเสร็จโอนเงินทันที</p>
</div>
<div style="display: flex; flex-direction: column; gap: 10px;">
<button type="button" onClick="{{ readyYes }}" style="height: 56px; border: 0; border-radius: 28px; font-family: 'Kanit', sans-serif; font-size: 18px; font-weight: 500; background: #141414; color: #FFFFFF; cursor: pointer;">พร้อมขาย ภายใน 7 วันนี้</button>
<div style="display: flex; flex-direction: column; align-items: center; gap: 4px; padding-top: 4px;">
<button type="button" onPointerDown="{{ holdStart }}" onPointerUp="{{ holdEnd }}" onPointerLeave="{{ holdEnd }}" onPointerCancel="{{ holdEnd }}" onContextMenu="{{ noMenu }}" onKeyDown="{{ holdKey }}" onKeyUp="{{ holdKey }}" aria-label="ยังไม่พร้อมขาย แค่มาเช็คราคาเฉยๆ (กดค้างไว้ 2 วินาที)" style="position: relative; overflow: hidden; height: 40px; padding: 0 16px; border: 0; border-radius: 20px; background: transparent; font-family: inherit; font-size: 14px; font-weight: 400; color: #8C8983; cursor: pointer; touch-action: none; user-select: none; -webkit-user-select: none; -webkit-touch-callout: none; -webkit-tap-highlight-color: transparent;">
<span aria-hidden="true" style="position: absolute; left: 0; top: 0; bottom: 0; border-radius: 20px; background: #DEDBD3; {{ holdBar }}"></span>
<span style="position: relative;">ยังไม่พร้อมขาย แค่มาเช็คราคาเฉยๆ</span>
</button>
<span aria-live="polite" style="font-size: 12px; line-height: 16px; min-height: 16px; color: #8C8983;">{{ holdHint }}</span>
</div>
</div>
</div>
</sc-if>
<sc-if value="{{ notReady }}" hint-placeholder-val="{{ false }}">
<div role="dialog" aria-modal="true" aria-labelledby="kr-no-title" style="position: fixed; inset: 0; z-index: 9999; background: #B3121B; color: #FFFFFF; display: flex; overflow-y: auto; -webkit-overflow-scrolling: touch;">
<div style="margin: auto; width: 100%; max-width: 560px; box-sizing: border-box; padding: calc(40px + env(safe-area-inset-top, 0px)) 24px calc(40px + env(safe-area-inset-bottom, 0px)); display: flex; flex-direction: column; gap: 28px;">
<span style="font-family: 'Kanit', sans-serif; font-weight: 600; font-size: 18px; letter-spacing: 0.5px; opacity: 0.85;">ขายรถไว</span>
<div style="display: flex; flex-direction: column; gap: 12px;">
<h2 id="kr-no-title" style="margin: 0; font-family: 'Kanit', sans-serif; font-weight: 600; font-size: 34px; line-height: 1.2;">วันนี้เรายังไม่ประเมินราคาให้</h2>
<p style="margin: 0; font-size: 17px; line-height: 1.6; opacity: 0.92;">ไม่ใช่ไม่อยากช่วย แต่ราคาที่ให้ตอนคุณยังไม่พร้อมขาย จะทำให้คุณเสียประโยชน์เอง</p>
</div>
<ol style="margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 14px;">
<li style="display: flex; gap: 14px; align-items: flex-start;">''' + NUM + '''1</span><span style="font-size: 16px; line-height: 1.6;">ราคารถขึ้นลงทุกวัน ตัวเลขวันนี้ไม่ใช่ตัวเลขของวันที่คุณขายจริง</span></li>
<li style="display: flex; gap: 14px; align-items: flex-start;">''' + NUM + '''2</span><span style="font-size: 16px; line-height: 1.6;">เราตีราคาจากการดูรถจริงถึงบ้าน ไม่ใช่จากข้อมูลบนหน้าจอ</span></li>
<li style="display: flex; gap: 14px; align-items: flex-start;">''' + NUM + '''3</span><span style="font-size: 16px; line-height: 1.6;">ราคาที่เราให้ ต้องเป็นราคาที่รับเงินได้ทันที ไม่ใช่ราคาเอาไว้เทียบ</span></li>
</ol>
<div style="border-top: 1px solid rgba(255,255,255,0.3); padding-top: 24px; display: flex; flex-direction: column; gap: 18px;">
<p style="margin: 0; font-size: 16px; line-height: 1.6;">วันที่พร้อมขาย กลับมาที่นี่ได้เลย ทีมไปดูรถถึงบ้าน ประเมินฟรี ตรวจเสร็จโอนเงินทันที</p>
<p style="margin: 0; font-size: 14px; line-height: 1.6; opacity: 0.75;">หน้านี้จะเปิดให้กรอกข้อมูลอีกครั้งในวันพรุ่งนี้</p>
</div>
</div>
</div>
</sc-if>
'''

# ---- แถบขั้นตอนแบบเลข 1-2-3 (ขั้นที่ผ่านแล้วเป็นติ๊กเขียว) แทนเส้นบางๆ ----
SEG_OLD = '''<div style="display: flex; gap: 6px;" aria-hidden="true">
<span style="flex: 1 1 0; height: 4px; border-radius: 2px; background: #141414;"></span>
<span style="flex: 1 1 0; height: 4px; border-radius: 2px; {{ seg2 }}"></span>
<span style="flex: 1 1 0; height: 4px; border-radius: 2px; {{ seg3 }}"></span>
</div>'''
SEG_NEW = '''<div style="display: flex; align-items: center; gap: 8px;" aria-hidden="true">
<span style="{{ dot1 }}">{{ dot1Txt }}</span>
<span style="flex: 1 1 0; height: 2px; border-radius: 1px; {{ ln1 }}"></span>
<span style="{{ dot2 }}">{{ dot2Txt }}</span>
<span style="flex: 1 1 0; height: 2px; border-radius: 1px; {{ ln2 }}"></span>
<span style="{{ dot3 }}">3</span>
</div>'''

LOGIC_VALS = '''    const DOT = 'width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; font-family: \\'Kanit\\', sans-serif; font-weight: 600; font-size: 16px; line-height: 1; ';
    const DONE = 'background: #06C755; color: #FFFFFF;', ACTIVE = 'background: #141414; color: #FFFFFF;', TODO = 'background: #E9E6DF; color: #55534E;';
    const LN_ON = 'background: #06C755;', LN_OFF = 'background: #DEDBD3;';
    const trk = (n) => { try { window.KR.track(n); } catch (e) {} };
    const quit = () => { this._hold = null; this.setState({ holding: false, ready: false, missing: false }); trk('NotReady'); try { localStorage.setItem('kr_noready', String(Date.now())); } catch (e) {} };
    const holdStart = (e) => { if (e && e.preventDefault) e.preventDefault(); if (this._hold) return; this._hold = setTimeout(quit, 2000); this.setState({ holding: true, holdHint: '' }); };
    const holdEnd = () => { if (!this._hold) return; clearTimeout(this._hold); this._hold = null; this.setState({ holding: false, holdHint: 'กดค้างไว้ 2 วินาที' }); };
    return {
      holdStart, holdEnd,
      holdKey: (e) => { if (e.key !== ' ' && e.key !== 'Enter') return; e.preventDefault(); if (e.type === 'keydown') { if (!e.repeat) holdStart(); } else holdEnd(); },
      noMenu: (e) => e.preventDefault(),
      holdBar: st.holding ? 'width: 100%; transition: width 2s linear;' : 'width: 0; transition: none;',
      holdHint: st.holdHint || '',
      gateOn: !st.sent && st.ready === null,
      notReady: !st.sent && st.ready === false,
      readyYes: () => { this.setState({ ready: true, missing: false }); trk('ReadyToSell'); },
      readyNo: quit,
      dot1: DOT + (st.step > 1 ? DONE : ACTIVE), dot1Txt: st.step > 1 ? '\\u2713' : '1',
      dot2: DOT + (st.step > 2 ? DONE : st.step === 2 ? ACTIVE : TODO), dot2Txt: st.step > 2 ? '\\u2713' : '2',
      dot3: DOT + (st.step === 3 ? ACTIVE : TODO),
      ln1: st.step > 1 ? LN_ON : LN_OFF, ln2: st.step > 2 ? LN_ON : LN_OFF,
      refNo: st.refNo || '',
      photoHref: st.photoHref || '',
      brands:'''


def common(body):
    body = body.replace('รูปรถ 4 มุม เลขไมล์ หน้าเล่มทะเบียน ทีมแจ้งช่วงราคาภายใน [กี่ชั่วโมง]', 'ถ่ายรูปรถ 6 มุมผ่านเว็บ ทีมโทรกลับพร้อมราคาภายใน 5 นาที (8:00–20:00)')
    body = re.sub(r'<span[^>]*>ตัวอย่าง · รอรูปจริง</span>', '', body)
    body = body.replace('ส่งรูปทางไลน์ได้ 24 ชม.', 'ส่งข้อมูลผ่านเว็บได้ 24 ชม.')
    # โลโก้ตัวจริงแทนตัวหนังสือ หัวเว็บ + ท้ายเว็บ
    assert HDR_OLD in body and FTR_OLD in body, 'logo anchor missing'
    body = body.replace(HDR_OLD, HDR_NEW).replace(FTR_OLD, FTR_NEW)
    # ไม่พร้อมขาย ไม่ให้แอด: เอาไอดีไลน์ท้ายเว็บออก
    body = re.sub(r'<span>LINE @kairodwai</span>\s*', '', body)
    return body


def apply(name, body, logic):
    body = common(body)
    if name not in ('Main', 'Brand', 'Province'):
        return body, logic
    # ---- หน้าจอหลังกดขอราคา: แทนกล่อง "ส่งทางไลน์" + ปุ่มไลน์ ด้วยปุ่มถ่ายรูป ----
    a = body.index('<div style="align-self: stretch; background: #F5F4F0; border: 1px solid #DEDBD3; border-radius: 16px; padding: 20px;')
    b = body.index('<a href="{{ lineHref }}" style="align-self: stretch', a)
    c = body.index('</a>', b) + 4
    body = body[:a] + NEW_SENT + body[c:]
    # ---- ตัด "หรือ / ส่งรูปรถทางไลน์" ใต้ปุ่มต่อไป ----
    a = body.index('<div style="display: flex; align-items: center; gap: 12px; color: #55534E; font-size: 14px;" aria-hidden="true">')
    b = body.index('<p style="margin: 0; font-size: 13px; color: #55534E; text-align: center;">ข้อมูลใช้ติดต่อ', a)
    body = body[:a] + body[b:]
    # ---- ปุ่มหัวเว็บ: เลื่อนไปฟอร์ม เขียนว่าขอราคา ----
    body = re.sub(r'(<button type="button" onClick="\{\{ goForm \}\}" aria-label=")[^"]*("[^>]*>)\s*<svg.*?</svg>\s*<span>แอดไลน์</span>',
                  lambda m: m.group(1) + 'ขอราคา' + m.group(2).replace('background: #E4E1DA;', 'background: #141414;').replace('color: #4A4843;', 'color: #FFFFFF;') + '<span>ขอราคา</span>', body, count=1, flags=re.S)
    body = body.replace('ส่งรูปทางไลน์ รับราคา', 'กรอกข้อมูล ส่งรูป รับราคา')
    body = body.replace('ส่งรูปมาทางไลน์ ทีมตอบกลับเร็วในเวลาทำการ', 'กรอกข้อมูลรถ ถ่ายรูป 6 มุม ทีมโทรกลับพร้อมราคา')
    # ---- หน้าคัดกรอง "พร้อมขายไหม" ก่อนฟอร์ม + แถบขั้นตอนแบบเลข ----
    anchor = '<sc-if value="{{ formOn }}" hint-placeholder-val="{{ true }}">'
    assert body.count(anchor) == 1, (name, 'formOn anchor')
    body = body.replace(anchor, GATE + anchor)
    assert body.count(SEG_OLD) == 1, (name, 'segment anchor')
    body = body.replace(SEG_OLD, SEG_NEW)

    # ---- logic ----
    def rep(old, new):
        nonlocal logic
        assert logic.count(old) >= 1, (name, old[:60])
        logic = logic.replace(old, new)
    rep("this.state = { sell: '', photoIdx: 0, step: 1,",
        "this.state = { ready: (() => { try { if (/[?&]kr=reset\\b/.test(location.search)) localStorage.removeItem('kr_noready'); "
        "const t = +localStorage.getItem('kr_noready') || 0; return Date.now() - t < 864e5 ? false : null; } catch (e) { return null; } })(), "
        "sell: '', photoIdx: 0, step: 1,")
    rep("formOn: !st.sent && !blocked,", "formOn: !st.sent && !blocked && st.ready === true,")
    rep("lineReady: !!(st.brand && st.year && st.mile) && !blocked,", "lineReady: false,")
    rep("lineLocked: !(st.brand && st.year && st.mile) || blocked,", "lineLocked: true,")
    rep("[['7d', 'ภายใน 7 วัน'], ['month', 'ภายในเดือนนี้'], ['price', 'แค่อยากรู้ราคา']]",
        "[['now', 'ตอนนี้'], ['7d', 'ภายใน 7 วัน'], ['month', 'ภายในเดือนนี้']]")
    # ส่งเข้าระบบ: สำเร็จ -> หน้าขอบคุณ + ปุ่มถ่ายรูป; ล้มเหลว (เน็ตหลุด/หมดเวลา 20 วิ) -> อยู่หน้าเดิม บอกให้กดใหม่
    rep("else this.setState({ sent: true, missing: false });",
        "else if (!st.sending) { this.setState({ sending: true, missing: false, failed: false }); "
        "window.KR.lead(st, MILES).then((r) => { "
        "if (r && r.ok) this.setState({ sending: false, sent: true, refNo: r.ref || '', "
        "photoHref: r.t ? '/line/?t=' + r.t + '&ref=' + encodeURIComponent(r.ref || '') : '' }); "
        "else this.setState({ sending: false, sent: false, failed: true, missing: true }); }); }")
    rep("(st.step < 3 ? 'ต่อไป' : 'ขอราคา')", "(st.step < 3 ? 'ต่อไป' : (st.sending ? 'กำลังส่ง…' : 'ขอราคา'))")
    rep("missingText: st.step === 1 ?", "missingText: st.failed ? 'ส่งไม่สำเร็จ สัญญาณอาจหลุด กดขอราคาอีกครั้งได้เลย' : st.step === 1 ?")
    rep("    return {\n      brands:", LOGIC_VALS)
    rep("send: () => { if (!blocked) this.setState({ sent: true }); },", "send: () => {},")
    return body, logic
