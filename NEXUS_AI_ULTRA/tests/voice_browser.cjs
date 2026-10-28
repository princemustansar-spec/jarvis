// Explicit browser/API transport doubles, not a real microphone/model acceptance test.
const {chromium}=require('playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||(process.platform==='linux'?'/usr/bin/chromium':undefined),headless:true,args:['--no-sandbox']});
try{const page=await browser.newPage({viewport:{width:1366,height:768}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.addInitScript(()=>{window.browserMicCalls=0;window.SpeechRecognition=window.webkitSpeechRecognition=class{constructor(){window.browserMicCalls++;throw Error('Browser recognizer must never be used');}};});
let operation='capture',stopped=false,phase=0,payload;
const respond=(route,body)=>route.fulfill({contentType:'application/json',body:JSON.stringify(body)});
await page.route('**/api/voice/start',async route=>{payload=route.request().postDataJSON();operation='capture';stopped=false;phase=0;await respond(route,{job_id:'voice-fixture',phase:'starting',operation});});
await page.route('**/api/voice/stop',async route=>{stopped=true;await respond(route,{stopping:true});});
await page.route('**/api/voice/diagnostics',async route=>{operation='diagnostics';await respond(route,{job_id:'voice-fixture',phase:'starting',operation});});
await page.route('**/api/voice/status',async route=>{
 if(operation==='diagnostics')return respond(route,{job_id:'voice-fixture',phase:'done',model_ready:true,result:{devices:[{id:2,name:'Explicit test input',host_api:'WASAPI'}],permission_tested:false}});
 if(!stopped)return respond(route,{job_id:'voice-fixture',phase:'listening',model_ready:true,message:'Listening locally',level_dbfs:-20});
 if(phase++===0)return respond(route,{job_id:'voice-fixture',phase:'transcribing',model_ready:true});
 return respond(route,{job_id:'voice-fixture',phase:'done',model_ready:true,result:{text:'Mera CPU check karo.',original_text:'میرا سی پی یو چیک کرو',romanized:true,offline:true}});
});
await page.goto('http://127.0.0.1:8765');await page.waitForFunction(()=>document.querySelector('#cpu').textContent!=='—');
const chatBefore=await page.evaluate(()=>state.chat.length);
await page.locator('[data-page="Voice Assistant"]').click();await page.locator('#voice-language').selectOption('ur');
await page.locator('#voice-record-button').click();await page.waitForFunction(()=>document.querySelector('#voice-record-button').textContent==='Stop & transcribe');
assert.equal(payload.language,'ur');assert.equal(payload.consent,true);
// Simulate reloading while the Python worker is still recording.
let injectResume=true;
await page.route('**/api/state',async route=>{const response=await route.fetch();const data=await response.json();if(injectResume){data.voice={phase:'listening',job_id:'voice-fixture',operation:'capture',model_ready:true};injectResume=false;}await respond(route,data);});
await page.reload();await page.waitForFunction(()=>document.querySelector('#mic-button').textContent==='Stop & transcribe');
await page.locator('#mic-button').click();await page.waitForFunction(()=>document.querySelector('#chat-input').value==='Mera CPU check karo.');
assert.equal(await page.evaluate(()=>window.browserMicCalls),0);assert.equal(await page.evaluate(()=>state.chat.length),chatBefore,'Transcript was automatically sent');
await page.locator('[data-page="Voice Assistant"]').click();await page.getByRole('button',{name:'Microphone diagnostics',exact:true}).click();await page.locator('#result-dialog').waitFor();assert((await page.locator('#result-content').textContent()).includes('WASAPI'));await page.locator('#close-result').click();assert(await page.locator('#voice-device option').filter({hasText:'Explicit test input'}).count());
await page.screenshot({path:path.join(__dirname,'../docs/voice-python-1366x768.png')});
assert.deepEqual(errors,[]);const report={transportDoubles:true,browserSpeechRecognitionCalls:0,englishAndUrduOptions:true,pythonConsentPayload:true,stopThenTranscribe:true,reconnectAfterReload:true,romanTranscriptReview:true,noAutomaticChatSend:true,diagnosticDevicePicker:true,speakerFunctionPreserved:'covered by Python hash test',jsErrors:errors};fs.writeFileSync(path.join(__dirname,'../docs/voice-browser-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exit(1)});
