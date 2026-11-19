// Full upload-to-result workflow on an isolated ASGI test server, 50 new images.
const {chromium}=require(process.env.RUNTIME_MODULES+'/playwright');
const fs=require('node:fs'),path=require('node:path');
(async()=>{
 const evaluation=JSON.parse(fs.readFileSync('docs/evaluation_round2.json'));
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true});
 const errors=[],rows=[];page.on('pageerror',e=>errors.push(e.message));
 const csvOnly=process.argv.includes('--csv-only');
 try {
  await page.goto('http://127.0.0.1:8504');
  if(csvOnly){
   rows.push(...JSON.parse(fs.readFileSync('docs/browser_round2.json')).rows);
   if(rows.length!==50)throw Error('CSV-only mode requires the completed 50-image workflow evidence');
  } else {
   await page.getByRole('button',{name:/เริ่มวิเคราะห์ขยะ/}).click({timeout:60000});
   await page.getByText('บันทึกเป็นข้อมูลทดสอบ',{exact:true}).click();
  }
  for(const [index,sample] of (csvOnly?[]:evaluation.results).entries()){
   await page.locator('input[type=file]').first().setInputFiles(path.resolve('data',sample.path));
   // A new upload clears the preceding result, preventing stale assertions.
   const status=page.getByText(/^(Plastic|Paper|Glass|Hazardous|Unknown) • (classified|uncertain)$/);
   await status.waitFor({state:'hidden',timeout:30000});
   await page.getByRole('button',{name:'Analyze Waste',exact:true}).click();
   await status.waitFor({timeout:90000});
   const category=(await status.innerText()).split(' • ')[0];
   const score=await page.locator('[data-testid=stMetricValue]').innerText();
   if(category!==sample.category)throw Error(`Engine/UI mismatch ${sample.path}: ${category} vs ${sample.category}`);
   rows.push({index:index+1,path:sample.path,label:sample.label,prediction:category,score_display:score,correct:category===sample.label});
   fs.writeFileSync('docs/browser_round2.json',JSON.stringify({endpoint:'localhost:8504',status:'running',checked_at:new Date().toISOString(),rows,page_errors:errors},null,2));
   if(index%10===9){
    await page.screenshot({path:`assets/screenshots/round2_${sample.label.toLowerCase()}.png`,fullPage:true});
    console.log(`${index+1}/50 workflows passed`);
   }
  }
  await page.getByText('ประวัติ',{exact:true}).click();
  await page.getByText('รวมข้อมูลทดสอบ',{exact:true}).click();
  await page.getByText(/^50 รายการ •/).waitFor({timeout:30000});
  const download=page.waitForEvent('download');
  const button=page.getByRole('button',{name:'ส่งออก CSV'});
  const href=await button.getAttribute('href');
  if(!href?.startsWith('data:text/csv;base64,'))throw Error('CSV is not self-contained');
  await button.click();const file=await download;await file.saveAs('docs/round2_ui_export.csv');
  const csv=fs.readFileSync('docs/round2_ui_export.csv','utf8');
  if(csv.trim().split(/\r?\n/).length!==51)throw Error('Expected CSV header and 50 events');
  if(errors.length)throw Error('Browser page errors: '+errors.join('; '));
  fs.writeFileSync('docs/browser_round2.json',JSON.stringify({endpoint:'localhost:8504',status:'pass',checked_at:new Date().toISOString(),n:rows.length,correct:rows.filter(r=>r.correct).length,rows,csv_events:50,csv_download:'self-contained data URI',page_errors:errors},null,2));
  console.log('All 50 real upload/inference workflows and CSV passed');
 } catch(e){await page.screenshot({path:'tmp/round2_failure.png',fullPage:true});throw e;}
 finally{await browser.close();}
})().catch(e=>{console.error(e.message);process.exit(1)});
