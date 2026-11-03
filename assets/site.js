/* ขายรถไว — ส่งฟอร์มเข้าระบบ + เก็บที่มาของลูกค้า (แอดไหน) */
(function () {
  var isRoot = location.pathname === '/' || location.pathname === '/index.html';
  var liffState = new URLSearchParams(location.search).get('liff.state');   // LIFF app "kairodwai-web" เปิดมาที่ root พร้อม liff.state → ให้ SDK แปลงเป็น URL จริง (/?via=liff&…) เอง ห้าม redirect แทรก
  // ลิงก์เก่าจากปุ่มในไลน์ (index.html?v=9) และลิงก์ "ถ่ายรูปต่อ" (t=…) ส่งไปหน้าถ่ายรูป
  if (isRoot && !liffState && /[?&](v=|t=)/.test(location.search)) { location.replace('/line/' + location.search); return; }
  var API = 'https://script.google.com/macros/s/AKfycbxNPhptcN66kGl4Bm6eiwsQSp-TrAnTsCn3GDosZFSn0Q5XYKdPozMqyXEBrHLWrxS_/exec';
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid', 'ttclid'];
  // เปิดในไลน์ผ่าน LIFF app "kairodwai-web" (endpoint = https://kairodwai.com/) → รู้ตัวตนไลน์ตั้งแต่จอแรก ไม่ต้อง Add LINE/ส่งรหัสทีหลัง
  var LIFF_WEB_ID = window.KR_LIFF_ID || '';   // ค่าจริงใส่ใน build.py (KR_LIFF_ID) — ว่าง = โหมดเว็บธรรมดา
  var VIA_LIFF = (/[?&]via=liff(&|$)/.test(location.search) || (isRoot && !!liffState)) && !!LIFF_WEB_ID;
  var LINE_ME = null;   // { uid, name } หลัง liff.getProfile()
  var webMode = function () { VIA_LIFF = false; document.documentElement.classList.remove('via-liff'); };   // ไม่ได้อยู่ในแอปไลน์จริง → กลับเป็นเว็บธรรมดา (ไม่บังคับล็อกอิน)
  if (VIA_LIFF) {
    document.documentElement.classList.add('via-liff');
    var sdk = document.createElement('script'); sdk.src = 'https://static.line-scdn.net/liff/edge/2/sdk.js';
    sdk.onload = function () {
      liff.init({ liffId: LIFF_WEB_ID }).then(function () {
        if (liffState) return;                                   // SDK กำลังพาไป URL จริงจาก liff.state
        if (!liff.isInClient() && !liff.isLoggedIn()) { webMode(); return; }
        return liff.getProfile().then(function (p) { LINE_ME = { uid: p.userId, name: p.displayName || '' }; store('kr_line', JSON.stringify(LINE_ME)); });
      }).catch(function (e) { webMode(); try { console.warn('liff', e); } catch (x) {} });
    };
    sdk.onerror = webMode;
    document.head.appendChild(sdk);
    // คนจากโฆษณารู้แล้วว่าเรารับซื้อรถ → เปิดมาให้เห็นกล่องคำถาม "พร้อมขายรถตอนนี้ไหม?" เลย
    window.addEventListener('load', function () { setTimeout(function () { var f = document.querySelector('form'); if (f) window.scrollTo({ top: f.getBoundingClientRect().top + window.scrollY - 16 }); }, 500); });
  }

  function store(k, v) { try { if (v == null) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  // จำที่มาครั้งแรก (first touch) ไว้ 30 วัน
  var q = new URLSearchParams(location.search), src = {};
  KEYS.forEach(function (k) { if (q.get(k)) src[k] = q.get(k).slice(0, 200); });
  if (Object.keys(src).length) {
    src.landing = location.pathname; src.ref = document.referrer.slice(0, 200); src.at = Date.now(); if (VIA_LIFF) src.via = 'liff';
    var old = null; try { old = JSON.parse(store('kr_src') || 'null'); } catch (e) {}
    if (!old || Date.now() - old.at > 30 * 864e5) store('kr_src', JSON.stringify(src));
  } else if (!store('kr_src') && document.referrer && document.referrer.indexOf(location.host) < 0) {
    store('kr_src', JSON.stringify({ ref: document.referrer.slice(0, 200), landing: location.pathname, at: Date.now() }));
  }

  var STD = ['Lead', 'Contact', 'ViewContent', 'CompleteRegistration', 'SubmitApplication'];
  function track(name, data, eid) {
    try { if (window.fbq) window.fbq(STD.indexOf(name) >= 0 ? 'track' : 'trackCustom', name, data || {}, eid ? { eventID: eid } : undefined); } catch (e) {}
    try { if (window.gtag) window.gtag('event', name, data || {}); } catch (e) {}
  }

  // Advanced matching (Meta) + Enhanced conversions (Google): ส่งเบอร์ให้แพลตฟอร์มจับคู่ผู้ใช้ — ตัว SDK hash (SHA-256) ก่อนส่งเอง
  function matchUser(phone) {
    var d = String(phone || '').replace(/\D/g, ''); if (d.charAt(0) === '0') d = '66' + d.slice(1); if (d.length < 11) return;
    try { if (window.fbq && window.KR_PX) window.fbq('init', window.KR_PX, { ph: d, country: 'th' }); } catch (e) {}
    try { if (window.gtag) window.gtag('set', 'user_data', { phone_number: '+' + d }); } catch (e) {}
  }

  function lead(st, MILES) {
    var mile = st.mile ? ((MILES.find(function (m) { return m[0] === st.mile; }) || [0, ''])[1] + ' กม.') : '';
    var car = [st.brand === 'ยี่ห้ออื่น' ? (st.other || 'ยี่ห้ออื่น') : st.brand, st.model === 'รุ่นอื่น' ? st.other : st.model,
      st.trim && st.trim !== 'ไม่แน่ใจรุ่นย่อย' ? (st.model && st.trim.indexOf(st.model + ' ') === 0 ? st.trim.slice(st.model.length + 1) : st.trim) : ''].filter(Boolean).join(' ');
    var fin = st.financed ? ['ยังผ่อนอยู่', st.price ? 'ราคาซื้อ ' + st.price : '', st.term ? 'สัญญา ' + st.term : '',
      st.paid ? 'ผ่อนแล้ว ' + st.paid + ' งวด' : '', st.monthly ? 'งวดละ ' + st.monthly : ''].filter(Boolean).join(' · ') : 'ไม่ติดไฟแนนซ์';
    var when = { ready: 'พร้อมขายทันที (1-7 วัน)', now: 'ตอนนี้', '7d': 'ภายใน 7 วัน', month: 'ภายในเดือนนี้' }[st.sell] || '';
    var s = null; try { s = JSON.parse(store('kr_src') || 'null'); } catch (e) {}
    var body = { type: 'lead', car: car, year: st.year, mile: mile, finance: fin, when: when, phone: st.phone,
      page: location.pathname, src: s ? JSON.stringify(s) : '' };
    if (LINE_ME && LINE_ME.uid) { body.uid = LINE_ME.uid; body.lname = LINE_ME.name; }   // เปิดในไลน์: ผูกลีดกับไลน์เค้าตั้งแต่กรอกฟอร์ม
    var ctl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 20000);
    return fetch(API, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(body), signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.json(); })
      .then(function (r) { clearTimeout(timer); if (r && r.ok) { matchUser(st.phone); track('Lead', { content_name: car }, r.t ? 'lead_' + r.t : undefined); } return r; })
      .catch(function () { clearTimeout(timer); return null; });
  }

  window.KR = { lead: lead, track: track, get viaLiff() { return VIA_LIFF; } };
})();
