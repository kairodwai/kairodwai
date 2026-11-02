// ทดสอบ flow ถ่ายทีหลัง: ถ่าย 2 รูป → แผ่น 'ถ่ายทีหลัง' + คัดลอกลิงก์ → หน้าแรกขึ้นการ์ด 'ถ่ายรูปรถต่อ' → กลับมารูปเดิมยังอยู่ → ครบแล้วล้างความจำ — node src/tools/resume.js
const { chromium } = require('playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..','..');  // repo root const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p.endsWith('/'))p+='index.html'; fs.readFile(path.join(ROOT,p),(e,d)=>{if(e){r.writeHead(404);r.end();return;} r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'}); r.end(d);});}).listen(8066);
(async()=>{const b=await chromium.launch(); const errs=[]; const ctx=await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2}); const p=await ctx.newPage(); p.on('pageerror',e=>errs.push(String(e)));
await p.addInitScript(()=>{window.fbq=()=>{};});
await p.route(/script\.google\.com/, r=>r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({ok:true})}));
await p.route(/static\.line-scdn\.net/, r=>r.fulfill({status:200,contentType:'text/javascript',body:'window.liff={}'}));
await p.route(/line\.me/, r=>r.fulfill({status:200,contentType:'text/html',body:'ok'}));
// photo page: take 2 photos, open later panel
await p.goto('http://localhost:8066/line/?t=tok123&ref=KR-77'); await p.waitForTimeout(400);
for (let i=0;i<2;i++){ const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot'+(i+1)).click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(300); }
await p.waitForTimeout(600); console.log('later btn visible:', await p.locator('#laterBtn').isVisible());
await p.locator('#laterBtn').click(); await p.waitForTimeout(300); await p.screenshot({path:'shots/later-panel.png'});
await p.locator('#copyBtn').click(); await p.waitForTimeout(200); console.log('copy btn:', await p.locator('#copyBtn').innerText());
await p.locator('#laterClose').click(); await p.waitForTimeout(200);
console.log('stored:', await p.evaluate(()=>({resume: localStorage.getItem('kr_resume'), slots: (JSON.parse(localStorage.getItem('kr_photos_tok123')||'[]')).map(x=>x?x.length:0)})));
// go home → resume card
await p.goto('http://localhost:8066/'); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(400);
const f=p.locator('form'); console.log('resume card:', (await f.innerText()).includes('เหลือแค่ถ่ายรูปรถ'), '| ref shown:', (await f.innerText()).includes('KR-77'), '| gate hidden:', !(await f.innerText()).includes('พร้อมขายรถตอนนี้ไหม'));
await f.screenshot({path:'shots/resume-card.png'});
const href=await f.locator('a', {hasText:'ถ่ายรูปรถต่อ'}).getAttribute('href'); console.log('resume href:', href);
// back to photo page → 2 slots restored
await p.goto('http://localhost:8066'+href); await p.waitForTimeout(500); console.log('restored count:', await p.locator('#count').innerText());
await p.screenshot({path:'shots/resume-photos.png'});
// finish → forget
for (let i=2;i<5;i++){ const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot'+(i+1)).click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(300); }
await p.waitForTimeout(900); await p.locator('#readyBtn').click(); await p.waitForURL(/line\.me/,{timeout:5000});
console.log('after done → kr_resume:', await p.evaluate(()=>localStorage.getItem('kr_resume')), '| photos key:', await p.evaluate(()=>localStorage.getItem('kr_photos_tok123')));
// reset path
await p.goto('http://localhost:8066/'); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(300); console.log('home after done shows gate:', (await p.locator('form').innerText()).includes('พร้อมขายรถตอนนี้ไหม'));
console.log('errors', errs); await b.close(); srv.close();})();
