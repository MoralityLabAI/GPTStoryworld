// Run from an environment with playwright-core and a local Chromium binary.
// npm install --no-save --prefix storyworlds/balance_of_reason playwright-core@1.56.1
// node storyworlds/balance_of_reason/browser-smoke.mjs
import assert from 'node:assert/strict';
import {spawn} from 'node:child_process';
import {setTimeout as sleep} from 'node:timers/promises';
import {chromium} from 'playwright-core';

const hostname='127.0.0.1';
const port=8765;
const base='http://'+hostname+':'+port+'/';
const server=spawn('python3',['-m','http.server',String(port),'--bind',hostname],{
 cwd:new URL('.',import.meta.url).pathname,stdio:'ignore'
});
let browser;
const errors=[];
async function findBrowser(){
  for(const path of [process.env.CHROME_EXECUTABLE,'/usr/bin/google-chrome','/usr/bin/chromium','/usr/bin/chromium-browser'].filter(Boolean)){
    try{
      const {accessSync}=await import('node:fs');
      accessSync(path);return path;
    }catch{}
  }
  throw Error('Install Chrome or Chromium to run the browser smoke test');
}
async function untilUp(){
  for(let i=0;i<35;i++){
    try{const r=await fetch(base);if(r.ok)return;}catch{}
    await sleep(200);
  }
  throw Error('Test HTTP server unavailable');
}
async function run(){
  await untilUp();
  browser=await chromium.launch({executablePath:await findBrowser(),headless:true,args:['--no-sandbox','--disable-dev-shm-usage']});
  const page=await browser.newPage({viewport:{width:1380,height:940},reducedMotion:'reduce'});
  page.on('pageerror',error=>errors.push(error.message));
  const res=await page.goto(base,{waitUntil:'networkidle',timeout:25000});
  assert.equal(res.status(),200);
  await page.locator('#visual-intro').waitFor({state:'visible'});
  assert.equal(await page.locator('#visual-intro .intro-stage').count(),1);
  await page.getByRole('button',{name:/new campaign/i}).click();
  await page.locator('#visual-intro').waitFor({state:'hidden'});
  await page.locator('#scene-title').waitFor({state:'visible'});
  assert.equal(await page.locator('#visual-speaker svg').count(),1);
  assert.equal(await page.locator('#coalitions .portrait-chip svg').count(),11);

  await page.getByRole('button',{name:'World atlas'}).click();
  await page.locator('#visual-modal').waitFor({state:'visible'});
  await page.getByRole('button',{name:'Inspect Manila'}).click();
  assert.ok((await page.locator('.map-caption').innerText()).includes('Manila'));
  await page.getByRole('button',{name:/Close ×/}).click();

  await page.getByRole('button',{name:'Diplomacy'}).click();
  assert.equal(await page.locator('.faction-list button').count(),11);
  await page.getByRole('button',{name:/Close ×/}).click();

  const first=await page.locator('#scene-title').innerText();
  await page.locator('#choices .choice').first().click();
  const second=await page.locator('#scene-title').innerText();
  assert.notEqual(first,second);
  const autosave=await page.evaluate(()=>localStorage.getItem('balance-of-reason/autosave-v1'));
  assert.ok(autosave&&JSON.parse(autosave).actions.length===1);
  assert.equal(await page.locator('#share-campaign').count(),1);
  const shareUrl=await page.evaluate(async()=>{
    const source=await (await fetch('./source_cards.json')).json();
    const {initial,choose}=await import('./engine.mjs');
    const {makeCampaignUrl}=await import('./share_route.mjs');
    const state=initial(source);choose(source,state,0);
    return makeCampaignUrl(location.href,source,state);
  });
  assert.ok(shareUrl.includes('#campaign='));
  const shared=await browser.newPage({viewport:{width:1200,height:800}});
  shared.on('pageerror',error=>errors.push(error.message));
  await shared.goto(shareUrl,{waitUntil:'networkidle',timeout:25000});
  await shared.locator('#visual-intro').waitFor({state:'hidden'});
  assert.equal(await shared.locator('#scene-title').innerText(),second);
  assert.equal(JSON.parse(await shared.evaluate(()=>localStorage.getItem('balance-of-reason/autosave-v1'))).actions.length,1);
  await shared.close();


  await page.getByRole('button',{name:'Main menu'}).click();
  await page.locator('#visual-intro').waitFor({state:'visible'});
  await page.getByRole('button',{name:/Resume campaign/i}).click();
  await page.locator('#visual-intro').waitFor({state:'hidden'});
  assert.equal(await page.locator('#scene-title').innerText(),second);

  await page.getByRole('button',{name:'Institutions'}).click();
  assert.ok(await page.locator('.research-grid button').count()>=10);
  await page.getByRole('button',{name:/Close ×/}).click();
  await page.getByRole('button',{name:'Feedback'}).click();
  assert.equal(await page.locator('.feedback-form textarea').count(),5);
  await page.getByRole('button',{name:/Close ×/}).click();

  await page.setViewportSize({width:390,height:780});
  assert.ok(await page.locator('#scene-title').isVisible());
  const overflow=await page.evaluate(()=>document.documentElement.scrollWidth-document.documentElement.clientWidth);
  assert.ok(overflow<15,'unexpected horizontal overflow '+overflow);
  assert.deepEqual(errors,[]);
  console.log('Browser smoke: PASS | title, event, atlas, factions, autosave, resume, mobile, share URLs, feedback');
}
try{await run();}finally{await browser?.close();server.kill('SIGTERM');}
