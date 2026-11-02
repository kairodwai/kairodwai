// ทดสอบหน้า /line/ แบบมาจากเว็บ: เลือกรูป 5 มุม → ส่งทีเดียว → เด้งไปไลน์ (mock backend) — node src/tools/photos.js
const { chromium } = require('playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..','..');  // repo root
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p.endsWith('/'))p+='index.html'; fs.readFile(path.join(ROOT,p),(e,d)=>{if(e){r.writeHead(404);r.end();return;} r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'}); r.end(d);});}).listen(8082);
(async()=>{const b=await chromium.launch(); const errs=[]; const posts=[];
const p=await(await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage(); p.on('pageerror',e=>errs.push(String(e)));
await p.route(/script\.google\.com/, r=>{const body=JSON.parse(r.request().postData()); posts.push(body.type+(body.slot!==undefined?':'+body.slot:'')); r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({ok:true})});});
await p.route(/line\.me/, r=>r.fulfill({status:200,contentType:'text/html',body:'<title>LINE</title>ok'}));
await p.route(/static\.line-scdn\.net/, r=>r.fulfill({status:200,contentType:'text/javascript',body:'window.liff={}'}));
await p.goto('http://localhost:8082/line/?t=abcdef0123456789abcd&ref=KR-2481'); await p.waitForTimeout(500);
console.log('title:', await p.locator('#hdTitle').innerText(), '| btn:', await p.locator('#sendBtn').innerText());
await p.screenshot({path:'shots/photo-0.png'});
for (let i=0;i<5;i++){ const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot'+(i+1)).click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(400); }
await p.waitForTimeout(800);
console.log('after 5 photos → btn:', await p.locator('#sendBtn').innerText(), '| disabled:', await p.locator('#sendBtn').isDisabled());
await p.screenshot({path:'shots/photo-1-ready.png'});
await p.locator('#sendBtn').click(); await p.waitForURL(/line\.me/, {timeout:5000});
console.log('after send → url:', decodeURIComponent(p.url()));
console.log('posts:', posts.join(' '), '| errors:', errs);
await b.close(); srv.close();})();
