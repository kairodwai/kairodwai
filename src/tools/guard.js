// ทดสอบกันหลุด: back ครั้งแรกขึ้นแผ่น 'ถ่ายทีหลัง', เตือนก่อนปิดแท็บตอนยังไม่ครบ, ครบแล้ว done ส่งเอง + ไม่เตือน, Add LINE เปิดทันที — node src/tools/guard.js
const { chromium } = require('playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..','..');  // repo root const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p.endsWith('/'))p+='index.html'; fs.readFile(path.join(ROOT,p),(e,d)=>{if(e){r.writeHead(404);r.end();return;} r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'}); r.end(d);});}).listen(8065);
(async()=>{const b=await chromium.launch(); const errs=[]; const posts=[]; const p=await(await b.newContext({viewport:{width:390,height:844}})).newPage(); p.on('pageerror',e=>errs.push(String(e)));
await p.addInitScript(()=>{window.fbq=()=>{};});
await p.route(/script\.google\.com/, r=>{const body=JSON.parse(r.request().postData()); posts.push(body.type); r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({ok:true})});});
await p.route(/static\.line-scdn\.net/, r=>r.fulfill({status:200,contentType:'text/javascript',body:'window.liff={}'}));
await p.route(/line\.me/, r=>r.fulfill({status:200,contentType:'text/html',body:'ok'}));
await p.goto('http://localhost:8065/'); await p.waitForSelector('html.dc-ready');
await p.goto('http://localhost:8065/line/?t=tokG&ref=KR-9'); await p.waitForTimeout(400);
// back button → panel opens, still on page
await p.goBack(); await p.waitForTimeout(300); console.log('after back #1: url', new URL(p.url()).pathname, '| panel open:', !(await p.locator('#laterPanel').isHidden()));
// beforeunload registered?
const hasBU = await p.evaluate(()=>{ let fired=false; const e=new Event('beforeunload',{cancelable:true}); window.dispatchEvent(e); return e.defaultPrevented; }); console.log('leave warning armed (not done):', hasBU);
await p.locator('#laterClose').click(); await p.waitForTimeout(200);
// complete 5 photos → done auto-posted, no warning
for (let i=0;i<5;i++){ const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot'+(i+1)).click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(200); }
await p.waitForTimeout(900); console.log('posts:', posts.join(' '), '| ready view:', !(await p.locator('#readyView').isHidden()));
const bu2 = await p.evaluate(()=>{ const e=new Event('beforeunload',{cancelable:true}); window.dispatchEvent(e); return e.defaultPrevented; }); console.log('leave warning after done:', bu2, '| kr_resume:', await p.evaluate(()=>localStorage.getItem('kr_resume')));
await p.locator('#readyBtn').click(); await p.waitForURL(/line\.me/,{timeout:5000}); console.log('CTA → LINE instantly, extra posts:', posts.filter(x=>x==='done').length);
console.log('errors', errs); await b.close(); srv.close();})();
