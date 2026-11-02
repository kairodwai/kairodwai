/* ขายรถไว — ส่งฟอร์มเข้าระบบ + เก็บที่มาของลูกค้า (แอดไหน) */
(function () {
  // ลิงก์เก่าจากปุ่มในไลน์ (index.html?v=9) ส่งไปหน้าถ่ายรูป
  if ((location.pathname === '/' || location.pathname === '/index.html') && /[?&](v=|liff\.state=|t=)/.test(location.search)) { location.replace('/line/' + location.search); return; }
  var API = 'https://script.google.com/macros/s/AKfycbxNPhptcN66kGl4Bm6eiwsQSp-TrAnTsCn3GDosZFSn0Q5XYKdPozMqyXEBrHLWrxS_/exec';
  var KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid', 'ttclid'];

  function store(k, v) { try { if (v == null) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }

  // จำที่มาครั้งแรก (first touch) ไว้ 30 วัน
  var q = new URLSearchParams(location.search), src = {};
  KEYS.forEach(function (k) { if (q.get(k)) src[k] = q.get(k).slice(0, 200); });
  if (Object.keys(src).length) {
    src.landing = location.pathname; src.ref = document.referrer.slice(0, 200); src.at = Date.now();
    var old = null; try { old = JSON.parse(store('kr_src') || 'null'); } catch (e) {}
    if (!old || Date.now() - old.at > 30 * 864e5) store('kr_src', JSON.stringify(src));
  } else if (!store('kr_src') && document.referrer && document.referrer.indexOf(location.host) < 0) {
    store('kr_src', JSON.stringify({ ref: document.referrer.slice(0, 200), landing: location.pathname, at: Date.now() }));
  }

  var STD = ['Lead', 'Contact', 'ViewContent', 'CompleteRegistration', 'SubmitApplication'];
  function track(name, data) {
    try { if (window.fbq) window.fbq(STD.indexOf(name) >= 0 ? 'track' : 'trackCustom', name, data || {}); } catch (e) {}
    try { if (window.gtag) window.gtag('event', name, data || {}); } catch (e) {}
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
    var ctl = window.AbortController ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) ctl.abort(); }, 20000);
    return fetch(API, { method: 'POST', headers: { 'Content-Type': 'text/plain;charset=utf-8' }, body: JSON.stringify(body), signal: ctl ? ctl.signal : undefined })
      .then(function (r) { return r.json(); })
      .then(function (r) { clearTimeout(timer); if (r && r.ok) track('Lead', { content_name: car }); return r; })
      .catch(function () { clearTimeout(timer); return null; });
  }

  window.KR = { lead: lead, track: track };
})();
