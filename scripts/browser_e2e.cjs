// Runs against the isolated QA server on 8502, never the user's main database.
const { chromium } = require(process.env.RUNTIME_MODULES + '/playwright');
const fs = require('node:fs');
const path = require('node:path');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 let page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true});
 const errors=[], checks=[]; page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('http://127.0.0.1:8502');
 await page.getByRole('button',{name:/เริ่มวิเคราะห์ขยะ/}).waitFor({timeout:30000});
 await page.getByRole('button',{name:/เริ่มวิเคราะห์ขยะ/}).click();
 const manifest=JSON.parse(fs.readFileSync('docs/evaluation.json')).results;
 for(const label of ['Paper','Hazardous']){
   if(label==='Hazardous'){
     await page.close();
     page=await browser.newPage({viewport:{width:1440,height:1100},acceptDownloads:true});
     page.on('pageerror',e=>errors.push(String(e)));
     await page.goto('http://127.0.0.1:8502');
     await page.getByRole('button',{name:/เริ่มวิเคราะห์ขยะ/}).click();
   }
   const sample=manifest.find(r=>r.label===label && r.category===label);
   await page.locator('input[type=file]').setInputFiles(path.resolve('data',sample.path));
   const button=page.getByRole('button',{name:'Analyze Waste',exact:true});
   await page.getByText(/ประมวลผล .*บันทึกผลแล้ว/).waitFor({state:'hidden'});
   await button.click();
   await page.getByText(/ประมวลผล .*บันทึกผลแล้ว/).waitFor({timeout:60000});
   await page.getByRole('heading',{name:label==='Paper'?'📄 กระดาษ':'🔋 ขยะอันตราย',exact:true}).waitFor();
   console.log('Verified inference:',label);
   await page.screenshot({path:`assets/screenshots/result_${label.toLowerCase()}.png`,fullPage:true});
   checks.push({action:'real upload and inference',label,path:sample.path,status:'pass'});
 }
 // A rerun caused by opening details must not insert another result.
 await page.getByText('รายละเอียดผลและข้อจำกัด',{exact:true}).click();
 await page.getByText('Dashboard',{exact:true}).click();
 await page.getByRole('heading',{name:'ภาพรวมการวิเคราะห์'}).waitFor();
 await page.getByText('รายการล่าสุด',{exact:true}).waitFor();
 await page.screenshot({path:'assets/screenshots/dashboard_data.png',fullPage:true});
 checks.push({action:'populated dashboard after actual inference',status:'pass'});
 await page.getByText('ประวัติ',{exact:true}).click();
 await page.getByRole('heading',{name:'ประวัติการวิเคราะห์'}).waitFor();
 await page.getByLabel('ประเภท',{exact:true}).click();
 await page.getByRole('option',{name:'Paper',exact:true}).click();
 await page.getByText('1 รายการ',{exact:false}).waitFor();
 // Streamlit updates caption and download payload in separate frontend patches.
 await page.waitForTimeout(750);
 await page.screenshot({path:'assets/screenshots/history_filtered.png',fullPage:true});
 const downloadPromise=page.waitForEvent('download');
 await page.getByRole('button',{name:'ส่งออก CSV',exact:true}).click();
 const download=await downloadPromise; await download.saveAs('docs/qa_export.csv');
 const csv=fs.readFileSync('docs/qa_export.csv','utf8');
 if(!csv.includes('Paper')||csv.includes(',Hazardous,')) throw Error('CSV filter mismatch');
 checks.push({action:'category filter and CSV download',status:'pass'});
 await page.getByText('วิเคราะห์ขยะ',{exact:true}).click();
 await page.getByText('ถ่ายจากกล้อง',{exact:true}).click();
 await page.getByText('กล้องต้องได้รับอนุญาตจากเบราว์เซอร์',{exact:false}).waitFor();
 checks.push({action:'camera widget rendered',status:'pass',note:'No physical camera capture or permissions tested'});
 await page.getByText('หน้าแรก',{exact:true}).click();
 await page.setViewportSize({width:390,height:844});
 await page.screenshot({path:'assets/screenshots/mobile.png',fullPage:true});
 const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>window.innerWidth);
 if(overflow) throw Error('Mobile horizontal overflow');
 checks.push({action:'390px viewport without page horizontal overflow',status:'pass'});
 fs.writeFileSync('docs/browser_e2e.json',JSON.stringify({checks,pageErrors:errors,database:'isolated QA database',screenshotNote:'dashboard_data and result screenshots are real QA sessions, not live recycling activity'},null,2));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
