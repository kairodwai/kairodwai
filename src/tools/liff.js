// ทดสอบโหมดเปิดในไลน์ (?via=liff): ซ่อนปุ่มแอดไลน์, ส่ง uid/lname ไปกับลีด, พาไป /line/ พร้อม via=liff, หน้ารูปจบด้วย doneView
// node src/tools/liff.js  (จำลอง LIFF SDK)
const { chromium } = require('playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..','..'); const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p.endsWith('/'))p+='index.html'; fs.readFile(path.join(ROOT,p),(e,d)=>{if(e){r.writeHead(404);r.end();return;} r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'}); r.end(d);});}).listen(8078);
const SDK = "window.liff={init:()=>Promise.resolve(),isLoggedIn:()=>true,isInClient:()=>true,getProfile:()=>Promise.resolve({userId:'U'+'a'.repeat(32),displayName:'mOs'}),closeWindow:()=>{window.__closed=true},login:()=>{}}";
(async()=>{const b=await chromium.launch(); const errs=[]; let lead=null; const posts=[];
 const p=await(await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage(); p.on('pageerror',e=>errs.push(String(e)));
 await p.addInitScript(() => { Object.defineProperty(window, 'KR_LIFF_ID', { get: () => '2012318037-test', set(){}, configurable: true }); });
 await p.route(/static\.line-scdn\.net/, r=>r.fulfill({status:200,contentType:'text/javascript',body:SDK}));
 await p.route(/script\.google\.com/, r=>{const body=JSON.parse(r.request().postData()); posts.push(body.type); if(body.type==='lead') lead=body; r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify(body.type==='lead'?{ok:true,t:'abcdef0123456789abcd',ref:'KR-2500'}:{ok:true})});});
 await p.goto('http://localhost:8078/?via=liff&utm_source=facebook'); await p.waitForSelector('html.dc-ready'); await p.waitForTimeout(900);
 console.log('via-liff class:', await p.evaluate(()=>document.documentElement.className), '| line buttons visible:', await p.locator('.kr-line:visible').count(), '| kr_line:', await p.evaluate(()=>localStorage.getItem('kr_line')));
 console.log('scrolled to card (scrollY>200):', await p.evaluate(()=>scrollY) > 200);
 await p.screenshot({path:'shots/liff-1-gate.png'});
 const f=p.locator('form'); await f.getByRole('button',{name:/รถพร้อมขายทันที/}).click(); await p.waitForTimeout(200);
 const sels=p.locator('form select'); await sels.nth(0).selectOption('2020'); await sels.nth(1).selectOption('Toyota'); await sels.nth(2).selectOption('Yaris ATIV'); await p.waitForTimeout(100); if(await sels.count()>4) await sels.nth(3).selectOption({index:1}); await sels.last().selectOption({index:3});
 await f.getByRole('button',{name:'ต่อไป'}).click(); await p.waitForTimeout(150); await f.getByRole('button',{name:'ต่อไป'}).click(); await p.waitForTimeout(150);
 await p.locator('form input').last().fill('0812345678'); await f.getByRole('button',{name:'ยืนยัน'}).click();
 await p.waitForURL(/\/line\//,{timeout:5000}); await p.waitForTimeout(500);
 console.log('lead uid/lname:', lead && lead.uid, lead && lead.lname, '| src:', lead && lead.src, '| url:', new URL(p.url()).pathname+new URL(p.url()).search);
 for (let i=0;i<5;i++){ const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot'+(i+1)).click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(250); }
 await p.waitForTimeout(1500);
 console.log('doneView shown:', !(await p.locator('#doneView').isHidden()), '| readyView hidden:', await p.locator('#readyView').isHidden(), '| h2:', await p.locator('#doneView h2').textContent());
 await p.screenshot({path:'shots/liff-2-done.png'}); console.log('going visible:', await p.locator('#going').isVisible(), '| closeBtn hidden:', await p.locator('#closeBtn').isHidden()); await p.waitForTimeout(2600); console.log('after 3.6s closeBtn visible:', await p.locator('#closeBtn').isVisible()); await p.screenshot({path:'shots/liff-3-done-fallback.png'});
 console.log('ads conversion:', await p.evaluate(()=>(window.dataLayer||[]).some(a=>a[0]==='event'&&a[1]==='conversion'&&a[2]&&a[2].send_to===window.KR_AW)));
 console.log('closeWindow called:', await p.evaluate(()=>!!window.__closed), '| posts:', posts.join(' '), '| errors:', errs);
 await b.close(); srv.close();})();
