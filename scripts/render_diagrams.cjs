const { chromium }=require(process.env.RUNTIME_MODULES+'/playwright');
const path=require('path');
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
for(const [name,w,h] of [['Workflow_Diagram',1000,1030],['System_Architecture',1100,650]]){
 const p=await b.newPage({viewport:{width:w,height:h},deviceScaleFactor:1.5});
 await p.goto('file:///'+path.resolve('docs/'+name+'.svg').replaceAll('\\','/'));
 await p.screenshot({path:'docs/'+name+'.png'});await p.close();
}await b.close();})();
