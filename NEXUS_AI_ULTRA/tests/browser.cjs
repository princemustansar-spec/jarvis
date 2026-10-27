const {chromium}=require('playwright');
const fs=require('fs');
const path=require('path');
const root=path.resolve(__dirname,'..');
const memoryText='Browser persistence '+Date.now();
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||(process.platform==='linux'?'/usr/bin/chromium':undefined),headless:true,args:['--no-sandbox']});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));const results=[];
for(const [width,height] of [[1366,768],[1536,1024],[1920,1080],[390,844]]){await page.setViewportSize({width,height});await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>document.querySelector('#cpu').textContent!=='—');await page.screenshot({path:path.join(root,`docs/dashboard-${width}.png`),fullPage:true});const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);results.push({viewport:`${width}x${height}`,horizontalOverflow:overflow});if(overflow)throw Error('Horizontal overflow '+width);}
await page.setViewportSize({width:1536,height:1024});
const nav=page.locator('#navigation button');for(let i=0;i<await nav.count();i++){await nav.nth(i).click();if(i>1)await page.locator('#workspace').waitFor({state:'visible'});}
await page.getByRole('button',{name:'Knowledge & Memory',exact:false}).first().click();await page.locator('#workspace textarea').fill(memoryText);await page.getByRole('button',{name:'Approve & save memory'}).click();await page.waitForTimeout(200);await page.reload();await page.waitForFunction(()=>document.querySelector('#cpu').textContent!=='—');await page.locator('[data-page="Knowledge & Memory"]').click();await page.getByText(memoryText,{exact:true}).first().waitFor();
await page.locator('[data-page="AI Tools Center"]').click();const system=page.locator('.card').filter({has:page.locator('strong',{hasText:'system info'})});await system.getByRole('button',{name:'Run tool'}).click();await page.locator('#result-dialog').waitFor();if(!(await page.locator('#result-content').textContent()).includes('ram_total'))throw Error('Missing actual tool result');await page.locator('#close-result').click();
await page.locator('[data-page="Safety Center"]').click();await page.getByRole('button',{name:'EMERGENCY STOP',exact:true}).click();await page.getByRole('button',{name:'Resume automation'}).waitFor();await page.getByRole('button',{name:'Resume automation'}).click();
const previousRoots=await page.evaluate(()=>state.roots);
const approvalDir=fs.mkdtempSync(path.join(require('os').tmpdir(),'nexus-ui-'));
const file=path.join(approvalDir,'approved.txt');
await page.evaluate(async roots=>{await api('settings',{roots});await refresh();},[approvalDir]);
await page.locator('[data-page="Computer Control"]').click();
const create=page.locator('.card').filter({has:page.locator('strong',{hasText:'create text'})});
await create.getByLabel('path',{exact:true}).fill(file);await create.getByLabel('text',{exact:true}).fill('UI-approved file');await create.getByRole('button',{name:'Run tool'}).click();
await page.getByRole('button',{name:'Approve this action'}).last().waitFor();if(fs.existsSync(file))throw Error('File created before approval');
await page.getByRole('button',{name:'Approve this action'}).last().click();await page.locator('#result-dialog').waitFor();if(fs.readFileSync(file,'utf8')!=='UI-approved file')throw Error('Approval did not execute');await page.locator('#close-result').click();
await page.evaluate(async roots=>{await api('settings',{roots});await refresh();},previousRoots);fs.unlinkSync(file);fs.rmdirSync(approvalDir);
results.push({navigationSections:await nav.count(),memoryPersistence:true,systemTool:true,emergencyStopResume:true,fileApproval:true,jsErrors:errors});fs.writeFileSync(path.join(root,'docs/browser-results.json'),JSON.stringify(results,null,2));await browser.close();if(errors.length)throw Error(errors.join('\n'));console.log(JSON.stringify(results));})().catch(e=>{console.error(e);process.exit(1)});
