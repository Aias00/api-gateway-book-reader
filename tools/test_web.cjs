const {chromium} = require(process.env.PLAYWRIGHT_MODULE || '/Users/aias/.local/node/lib/node_modules/@jackwener/opencli/node_modules/playwright');
const assert=require('node:assert/strict'); const fs=require('node:fs');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:process.env.CHROMIUM_PATH||'/Users/aias/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'});
 try {
  const base=process.env.BOOK_URL||'http://127.0.0.1:8878/';
  const page=await browser.newPage({viewport:{width:1440,height:1000},permissions:['clipboard-read','clipboard-write']});
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base);await page.waitForSelector('#content > section');
  assert.equal(await page.locator('#chapters>a').count(),27);
  assert.equal(await page.locator('#content > section.level1').count(),27);
  assert(await page.locator('.hero img').evaluate(i=>i.complete&&i.naturalWidth>0));
  await page.screenshot({path:'dist/在线阅读-桌面.png'});
  const sections=await page.locator('#content > section.level1').evaluateAll(ss=>ss.map(s=>({id:s.id,title:s.querySelector('h1').textContent})));
  await page.locator('.start').click();
  assert.equal(decodeURIComponent(new URL(page.url()).hash.slice(1)),sections[0].id);
  await page.locator('#search').fill('动态配置');
  assert(await page.locator('#results a').count()>0);
  await page.locator('#results a').first().click();
  assert(await page.evaluate(()=>scrollY)>0);
  await page.locator('#search').fill('<img src=x onerror=alert(1)>');
  assert.equal(await page.locator('#results a').count(),0);assert.equal(await page.locator('#results img').count(),0);
  await page.locator('#search').fill('');
  await page.locator('#theme').selectOption('paper');
  await page.locator('#font-size').selectOption('22');
  await page.reload();
  assert.equal(await page.locator('html').getAttribute('data-theme'),'paper');
  assert.equal(await page.locator('#font-size').inputValue(),'22');
  await page.locator('#theme').selectOption('dark');
  assert.equal(await page.locator('html').getAttribute('data-theme'),'dark');
  await page.locator('#font-size').selectOption('19');
  await page.locator('#theme').selectOption('light');
  await page.evaluate(id=>document.getElementById(id).scrollIntoView(),sections[10].id);await page.waitForTimeout(350);
  await page.goto(base);assert(await page.locator('#resume').isVisible());
  await page.locator('#resume').click();
  assert(await page.evaluate(()=>Math.abs(document.querySelector('#content > section:nth-child(11)').getBoundingClientRect().top))<150);
  const copied=await page.locator('pre code').first().textContent();
  await page.locator('pre .copy').first().click();
  assert.equal(await page.evaluate(()=>navigator.clipboard.readText()),copied);
  const download=await page.request.get(base+'book.epub');assert.equal(download.status(),200);assert.equal((await download.body()).subarray(0,2).toString(),'PK');
  for(const width of [390,768,1440]){
   await page.setViewportSize({width,height:900});
   for(const section of sections){
    await page.evaluate(id=>document.getElementById(id).scrollIntoView(),section.id);
    const box=await page.evaluate(()=>({w:innerWidth,sw:document.documentElement.scrollWidth}));
    assert(box.sw<=box.w,JSON.stringify({section,width,...box}));
   }
  }
  await page.setViewportSize({width:390,height:844});
  await page.evaluate(()=>scrollTo(0,0));
  await page.locator('#menu').click();assert.equal(await page.locator('#menu').getAttribute('aria-expanded'),'true');
  await page.locator('#search').fill('限流');await page.locator('#results a').first().click();
  assert.equal(await page.locator('#menu').getAttribute('aria-expanded'),'false');
  await page.evaluate(()=>scrollTo(0,0));await page.screenshot({path:'dist/在线阅读-手机.png'});
  assert(await page.locator('#content img').evaluateAll(imgs=>imgs.every(i=>i.complete&&i.naturalWidth>0)));
  assert.deepEqual(errors,[]);
  const noJS=await browser.newPage({javaScriptEnabled:false});await noJS.goto(base);
  assert.equal(await noJS.locator('#content > section.level1').count(),27);
  assert.equal(await noJS.locator('#chapters>a').count(),27);
  assert((await noJS.locator('#content').innerText()).includes('gateway_core.py'));
  await noJS.close();
  const report={url:base,sections:27,widths:[390,768,1440],checks:['complete static text without JavaScript','chapter anchors','safe full text search','four reading themes','font persistence','explicit resume reading','clipboard copy','EPUB download','mobile menu','all images loaded','no horizontal page overflow','no browser errors']};
  fs.writeFileSync('research/web-audit.json',JSON.stringify(report,null,2));console.log(report);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
