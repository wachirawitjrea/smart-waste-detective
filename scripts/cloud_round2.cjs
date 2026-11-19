// Repeat the same 50-image set on the deployed app, in ten-image sessions.
// Supply a temporary access URL in tmp/cloud_config.json. Never commit it.
const {chromium}=require(process.env.RUNTIME_MODULES+'/playwright');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const config=JSON.parse(fs.readFileSync('tmp/cloud_ws_config.json'));
 const evaluation=JSON.parse(fs.readFileSync('docs/evaluation_round2.json'));
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const context=await browser.newContext({viewport:{width:1440,height:1100},acceptDownloads:true});
 const errors=[],rows=[],retries=[];let csvChecked=false,page;
 const previous=fs.existsSync('docs/cloud_round2.json')?JSON.parse(fs.readFileSync('docs/cloud_round2.json')):null;
 if(previous?.source_commit===config.source_commit)rows.push(...previous.rows);
 async function openSession(){
  if(page)await page.close();page=await context.newPage();
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(config.shareableUrl,{timeout:90000,waitUntil:'domcontentloaded'});
  await page.getByRole('button',{name:/เริ่มวิเคราะห์ขยะ/}).click({timeout:120000});
  await page.getByText('บันทึกเป็นข้อมูลทดสอบ',{exact:true}).click();
 }
 try{
  for(let index=rows.length;index<evaluation.results.length;index++){
   const sample=evaluation.results[index];
   if(!page||index%10===0)await openSession();
   for(let attempt=1;attempt<=3;attempt++){
    try{
    await page.locator('input[type=file]').first().setInputFiles(path.resolve('data',sample.path));
    const status=page.getByText(/^(Plastic|Paper|Glass|Hazardous|Unknown) • (classified|uncertain)$/);
    await status.waitFor({state:'hidden',timeout:45000});
    await page.waitForFunction(()=>Array.from(document.querySelectorAll('button')).some(b=>b.innerText==='Analyze Waste'&&!b.disabled),null,{timeout:20000});
    await page.getByRole('button',{name:'Analyze Waste',exact:true}).click();
    await status.waitFor({timeout:120000});
    const prediction=(await status.innerText()).split(' • ')[0];
    rows.push({path:sample.path,label:sample.label,prediction,engine_match:prediction===sample.category,correct:prediction===sample.label});
    fs.writeFileSync('docs/cloud_round2.json',JSON.stringify({status:'running',url:'https://smartwaste-2plus3.vercel.app',deployment:config.deployment,source_commit:config.source_commit,checked_at:new Date().toISOString(),rows,retries,page_errors:errors},null,2));
    break;
    }catch(error){
     retries.push({path:sample.path,attempt,reason:error.message.slice(0,180),recovery:'reload a fresh app session'});
     if(attempt===3){await page.screenshot({path:'tmp/cloud_round2_failure.png',fullPage:true});fs.writeFileSync('tmp/cloud_round2_failure.txt',await page.locator('body').innerText());throw error;}
     await openSession();
    }
   }
   if(rows.length%10===0)console.log(`Cloud ${rows.length}/50 scanned; retries=${retries.length}`);
   if(index===49){
    await page.screenshot({path:'assets/screenshots/cloud_round2_unknown.png',fullPage:true});
    await page.getByText('ประวัติ',{exact:true}).click();
    await page.getByText('รวมข้อมูลทดสอบ',{exact:true}).click();
    await page.getByText(/^[1-9]\d* รายการ •/).waitFor();
    const button=page.getByRole('button',{name:'ส่งออก CSV'});
    const href=await button.getAttribute('href');
    if(!href?.startsWith('data:text/csv;base64,'))throw Error('Cloud download still uses server media');
    const dlPromise=page.waitForEvent('download');await button.click();
    const dl=await dlPromise;await dl.saveAs('tmp/cloud_round2_export.csv');
    const csv=fs.readFileSync('tmp/cloud_round2_export.csv','utf8');
    if(!csv.includes('Unknown'))throw Error('Cloud CSV missing current results');
    csvChecked=true;await page.screenshot({path:'assets/screenshots/cloud_round2_history.png',fullPage:true});
   }
  }
  if(errors.length||rows.some(r=>!r.engine_match))throw Error('Cloud differs from local engine or page errors occurred');
  fs.writeFileSync('docs/cloud_round2.json',JSON.stringify({status:retries.length?'completed_with_retries':'pass',url:'https://smartwaste-2plus3.vercel.app',deployment:config.deployment,source_commit:config.source_commit,checked_at:new Date().toISOString(),n:rows.length,correct:rows.filter(r=>r.correct).length,engine_matches:rows.filter(r=>r.engine_match).length,csv_download:csvChecked,rows,retries,page_errors:errors,storage:'Temporary instance SQLite; cloud export is not asserted to contain all 50 events across sessions'},null,2));
  console.log('Cloud 50 uploads/inferences and client-side CSV passed');
 } finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1)});
