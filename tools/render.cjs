const {chromium}=require('/Users/aias/.local/node/lib/node_modules/@jackwener/opencli/node_modules/playwright');
const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Users/aias/Library/Caches/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-mac-arm64/chrome-headless-shell'});
 const page=await browser.newPage();const base=path.resolve('.preview/EPUB/text');const report=[];
 for(const width of [800,390]){
  await page.setViewportSize({width,height:1100});
  for(const file of fs.readdirSync(base).filter(x=>x.endsWith('.xhtml'))){
   await page.goto(pathToFileURL(path.join(base,file)).href);
   report.push({width,file,...await page.evaluate(()=>({scrollWidth:document.documentElement.scrollWidth,images:[...document.images].every(i=>i.complete&&i.naturalWidth>0),heading:document.querySelector('h1')?.textContent}))});
   if(width===800&&['ch004.xhtml','ch011.xhtml'].includes(file))await page.screenshot({path:`dist/${file}.png`});
  }
 }
 fs.writeFileSync('research/render-audit.json',JSON.stringify(report,null,2));
 console.log(JSON.stringify(report.filter(x=>x.scrollWidth>x.width||!x.images)));
 await browser.close();
})();
