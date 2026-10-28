const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||(process.platform==='linux'?'/usr/bin/chromium':undefined),headless:true,args:['--no-sandbox']});
 const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));const results=[];
 try{
  await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>document.querySelector('#cpu').textContent!=='—');
  // Resize the same page: CSS must react without reload or losing form content.
  for(const [width,height] of [[1366,768],[1920,1080],[1366,650],[1093,614],[800,600],[390,844]]){
   await page.setViewportSize({width,height});await page.locator('[data-page="Dashboard"]').click();
   await page.evaluate(()=>document.fonts.ready);await page.waitForTimeout(100);
   const layout=await page.evaluate(()=>{
    const rect=e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height,right:r.right,bottom:r.bottom};};
    const selectors=['.hero-grid','.module-tiles','.lower-grid','.chat-panel','.monitor-panel','.safety-panel'];
    const boxes=Object.fromEntries(selectors.map(s=>[s,rect(document.querySelector(s))]));
    const scene=rect(document.querySelector('.core-scene'));
    const orbit=document.querySelector('.orbit-outer');
    // Animated rotation changes bounding boxes; use its untransformed diameter.
    const diameter=parseFloat(getComputedStyle(orbit).width);
    return {viewport:{width:innerWidth,height:innerHeight},documentWidth:document.documentElement.scrollWidth,
     dashboardActions:[...document.querySelectorAll('.quick-panel button,.optimizer-panel>button,.safety-panel button,#chat-form button')].map(e=>({text:e.textContent,box:rect(e),panel:rect(e.closest('.panel'))})),
     dashboardScroll:document.querySelector('#dashboard').scrollHeight>document.querySelector('#dashboard').clientHeight+2,
     scene,coreDiameter:diameter,boxes,background:getComputedStyle(document.body).getPropertyValue('--bg').trim(),cyan:getComputedStyle(document.body).getPropertyValue('--cyan').trim()};
   });
   assert(layout.documentWidth<=width+1,`Horizontal overflow at ${width}x${height}`);
   assert.equal(layout.background,'#030d18');assert.equal(layout.cyan,'#00dbf6');
   if(width>1100){
    for(const [name,r] of Object.entries(layout.boxes)){assert(r.x>=0&&r.right<=width+1,`${name} outside width`);}
    assert(layout.coreDiameter+30<=Math.min(layout.scene.width,layout.scene.height)+2,'AI ring/outline clipped');
    if(height>=768){for(const action of layout.dashboardActions)assert(action.box.bottom<=action.panel.bottom+1&&action.box.y>=action.panel.y,`Clipped dashboard button: ${action.text}`);assert(!layout.dashboardScroll,'Dashboard should fit full desktop viewport');for(const [name,r]of Object.entries(layout.boxes))assert(r.bottom<=height+1,`${name} below viewport`);}
   }
   await page.screenshot({path:path.join(root,'docs',`autofit-${width}x${height}.png`),fullPage:true});
   await page.locator('#settings-shortcut').click();
   const appName=page.getByLabel('Application name',{exact:true});await appName.fill('Unsaved fit check');
   const settings=await page.evaluate(()=>{const w=document.querySelector('#workspace');return {overflow:getComputedStyle(w).overflowY,clientHeight:w.clientHeight,scrollHeight:w.scrollHeight};});
   const save=page.getByRole('button',{name:'Save all providers',exact:true});await save.scrollIntoViewIfNeeded();
   if((width===1366&&height===768)||(width===1920&&height===1080))await page.screenshot({path:path.join(root,'docs',`autofit-settings-${width}x${height}.png`)});
   const b=await save.boundingBox();assert(b&&b.y>=0&&b.y+b.height<=height+2,'Settings bottom save button inaccessible');
   if(width>1100){assert.equal(settings.overflow,'auto');assert(settings.scrollHeight>settings.clientHeight,'Settings lost its scroll area');}
   await page.setViewportSize({width:width-20,height:height-20});assert.equal(await appName.inputValue(),'Unsaved fit check','Resize discarded form input');
   await page.setViewportSize({width,height});
   results.push({size:`${width}x${height}`,horizontalOverflow:false,coreDiameter:layout.coreDiameter,dashboardFits:width>1100&&height>=768?!layout.dashboardScroll:'vertical scrolling allowed',settingsScrollable:true,settingsBottomButtonAccessible:true,unsavedInputPreserved:true});
  }
  assert.deepEqual(errors,[]);fs.writeFileSync(path.join(root,'docs/autofit-results.json'),JSON.stringify({results,jsErrors:errors},null,2));console.log(JSON.stringify(results));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1);});
