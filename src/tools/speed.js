// วัดความเร็วโหลดทุกหน้าบนเว็บจริง แบบมือถือ + เน็ต 4G ธรรมดา (1.6Mbps/150ms เหมือน Lighthouse "Slow 4G")
// node src/tools/speed.js [base]   → ตาราง: bytes ที่โหลด, จำนวนไฟล์, DOMContentLoaded, LCP, รูปใหญ่สุด
const { chromium, devices } = require('playwright');
const BASE = process.argv[2] || 'https://kairodwai.com';
const PAGES = ['/', '/toyota/', '/chiang-mai/', '/portfolio/', '/finance/', '/documents/', '/privacy/', '/go/', '/line/?t=x&ref=KR-0'];
(async () => {
  const b = await chromium.launch();
  for (const path of PAGES) {
    const ctx = await b.newContext({ ...devices['iPhone 13'] });
    const p = await ctx.newPage();
    const cdp = await ctx.newCDPSession(p);
    await cdp.send('Network.enable');
    await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6e6 / 8, uploadThroughput: 750e3 / 8 });
    await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    const reqs = [];
    p.on('response', async r => { try { const h = r.headers(); const len = Number(h['content-length'] || 0); reqs.push({ url: r.url(), type: (h['content-type'] || '').split(';')[0], len }); } catch (e) {} });
    const t0 = Date.now();
    await p.goto(BASE + path + (path.includes('?') ? '&' : '?') + 'spd=' + Date.now(), { waitUntil: 'load', timeout: 60000 });
    const t = await p.evaluate(() => new Promise(res => {
      const nav = performance.getEntriesByType('navigation')[0];
      let lcp = 0; try { new PerformanceObserver(l => { l.getEntries().forEach(e => lcp = e.startTime); }).observe({ type: 'largest-contentful-paint', buffered: true }); } catch (e) {}
      setTimeout(() => res({ dcl: Math.round(nav.domContentLoadedEventEnd), load: Math.round(nav.loadEventEnd), lcp: Math.round(lcp), res: performance.getEntriesByType('resource').map(r => ({ n: r.name.replace(/^https?:\/\/[^/]+/, ''), b: r.transferSize || r.encodedBodySize, t: Math.round(r.responseEnd) })) }), 1500);
    }));
    const total = t.res.reduce((s, r) => s + r.b, 0);
    const big = t.res.slice().sort((a, c) => c.b - a.b).slice(0, 4).map(r => r.n.slice(0, 48) + ' ' + Math.round(r.b / 1024) + 'k@' + r.t + 'ms').join(' | ');
    console.log(path.padEnd(20), 'files', String(t.res.length + 1).padStart(3), 'KB', String(Math.round(total / 1024)).padStart(4), 'DCL', String(t.dcl).padStart(5), 'load', String(t.load).padStart(5), 'LCP', String(t.lcp).padStart(5), '|', big);
    await ctx.close();
  }
  await b.close();
})();
