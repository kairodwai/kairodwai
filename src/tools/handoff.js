const { chromium, devices } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const url = 'http://localhost:8090/line/?t=abcdef0123456789abcd&ref=KR-2500';
  const block = async (p) => { await p.route(/script\.google\.com|line-scdn|liff/, r => r.abort()); };
  const d = await b.newPage({ viewport: { width: 1280, height: 860 } }); await block(d);
  await d.goto(url); await d.waitForTimeout(1200); await d.screenshot({ path: 'shots/handoff-desktop.png' });
  console.log('desktop qr svg:', await d.locator('#hoQrBox svg').count(), 'btn hidden', await d.locator('#hoBtn').isHidden());
  const ctx = await b.newContext({ ...devices['iPhone 13'] }); const m = await ctx.newPage(); await block(m);
  await m.goto(url); await m.waitForTimeout(800); await m.screenshot({ path: 'shots/handoff-iphone.png' });
  console.log('iphone btn href:', await m.locator('#hoBtn').getAttribute('href'), 'qr hidden', await m.locator('#hoQr').isHidden());
  const a = await (await b.newContext({ ...devices['Pixel 7'] })).newPage(); await block(a);
  await a.goto(url); await a.waitForTimeout(800); console.log('android href:', (await a.locator('#hoBtn').getAttribute('href')).slice(0, 60));
  await b.close();
})();
