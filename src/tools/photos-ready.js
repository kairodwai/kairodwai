// ทดสอบหน้า /line/ (มาจากเว็บ): ครบ 5 มุม → หน้า ready เต็มจอ → แก้ไขรูป → กลับมา ready → Add LINE — node src/tools/photos-ready.js
const { chromium } = require('playwright'); const http=require('http'),fs=require('fs'),path=require('path');
const ROOT=path.join(__dirname,'..','..');  // repo root
const MIME={'.html':'text/html; charset=utf-8','.js':'text/javascript','.png':'image/png','.jpg':'image/jpeg'};
const srv=http.createServer((q,r)=>{let p=decodeURIComponent(q.url.split('?')[0]); if(p.endsWith('/'))p+='index.html'; fs.readFile(path.join(ROOT,p),(e,d)=>{if(e){r.writeHead(404);r.end();return;} r.writeHead(200,{'content-type':MIME[path.extname(p)]||'application/octet-stream'}); r.end(d);});}).listen(8075);
(async()=>{const b=await chromium.launch(); const errs=[]; const posts=[];
 const p=await(await b.newContext({viewport:{width:390,height:844},deviceScaleFactor:2})).newPage(); p.on('pageerror',e=>errs.push(String(e)));
 await p.route(/script\.google\.com/, async r=>{const body=JSON.parse(r.request().postData()); posts.push(body.type); await new Promise(res=>setTimeout(res,150)); r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:JSON.stringify({ok:true})});});
 await p.route(/line\.me/, r=>r.fulfill({status:200,contentType:'text/html',body:'<title>LINE</title>ok'}));
 await p.route(/static\.line-scdn\.net/, r=>r.fulfill({status:200,contentType:'text/javascript',body:'window.liff={}'}));
 await p.goto('http://localhost:8075/line/?t=abc&ref=KR-1'); await p.waitForTimeout(400);
 await p.screenshot({path:'shots/rv-0.png'});
 for (let i=0;i<5;i++){ const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot'+(i+1)).click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(250); }
 await p.waitForTimeout(1500);
 console.log('ready view shown:', !(await p.locator('#readyView').isHidden()), '| app hidden:', await p.locator('#app').isHidden());
 await p.screenshot({path:'shots/rv-1-ready.png'});
 await p.locator('#editBtn').click(); await p.waitForTimeout(200); console.log('edit → grid shown:', !(await p.locator('#app').isHidden()), '| ready hidden:', await p.locator('#readyView').isHidden());
 const [fc]=await Promise.all([p.waitForEvent('filechooser'), p.locator('#slot2').click()]); await fc.setFiles(path.join(__dirname,'car.jpg')); await p.waitForTimeout(800);
 console.log('after re-upload → ready again:', !(await p.locator('#readyView').isHidden()));
 await p.locator('#readyBtn').click(); await p.waitForURL(/line\.me/, {timeout:5000}); console.log('cta → url:', decodeURIComponent(p.url()), '| posts:', posts.join(' '), '| errors:', errs);
 await b.close(); srv.close();})();
