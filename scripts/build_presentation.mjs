import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
import os from 'node:os';
const runtime=process.env.CODEX_RUNTIME_DEPENDENCIES || 'C:/Program Files/WindowsApps/OpenAI.CodexPrimaryRuntime.v26-1112-737-0_26.1112.737.0_x64__3k8sg7r9htsxt/dependencies';
process.env.RUNTIME_NODE_MODULES=runtime+'/node/node_modules';
const require=createRequire(runtime+'/node/noop.cjs');
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const root=process.cwd(); const tmp=path.join(root,'tmp/slides');
const skill=process.env.PRESENTATIONS_SKILL_DIR || path.join(os.homedir(),'.codex/plugins/cache/openai-primary-runtime/presentations/26.1112.11217/skills/presentations');
await fs.mkdir(tmp,{recursive:true});
const evaluation=JSON.parse(await fs.readFile('docs/evaluation.json','utf8'));
const pres=Presentation.create({slideSize:{width:1280,height:720}});
const ink='#183E30',green='#21835C',muted='#687F72',pale='#F6F9F5';
const font='Leelawadee UI';
function text(s,content,x,y,w,h,size=28,color=ink,bold=false){
 const shape=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
 shape.text=content;shape.text.style={typeface:font,fontSize:size,color,bold,verticalAlignment:'top',wrap:'square',autoFit:'none',insets:0};
 return shape;
}
function slide(title,num,{dark=false,kicker='SMART WASTE DETECTIVE'}={}){
 const s=pres.slides.add();s.background.fill=dark?ink:pale;
 const color=dark?'#FFFFFF':ink;
 text(s,kicker,64,34,1100,28,15,dark?'#BADDAC':green,true);
 text(s,title,64,91,1152,92,44,color,true);
 text(s,'IT232   Bangkok University',64,676,800,22,14,dark?'#C5DCCF':muted);
 text(s,String(num).padStart(2,'0'),1160,672,55,28,17,dark?'#C5DCCF':muted);
 return s;
}
async function image(s,filename,x,y,w,h,alt){
 const bytes=await fs.readFile(path.join(root,filename));
 return s.images.add({blob:new Uint8Array(bytes),contentType:'image/'+(filename.endsWith('.jpg')?'jpeg':'png'),alt,fit:'contain',position:{left:x,top:y,width:w,height:h}});
}
function flow(s,label,x,y,w=220,h=75,fill='#E3EFE5'){
 const sh=s.shapes.add({geometry:'roundRect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'#A7C6AF',width:1}});
 sh.text=label;sh.text.style={typeface:font,fontSize:23,color:ink,bold:false,alignment:'center',verticalAlignment:'middle',insets:10};
 return sh;
}
function arrow(s,x,y,w=45,h=22){s.shapes.add({geometry:'rightArrow',position:{left:x,top:y,width:w,height:h},fill:green,line:{fill:'none',width:0}})}
function table(s,values,x,y,w,h,widths){
 const t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});
 t.borders.assign({style:'solid',fill:'#D9E2DA',width:1});
 for(let r=0;r<values.length;r++)for(let c=0;c<values[0].length;c++){
   const cell=t.getCell(r,c);cell.fill=r===0?ink:(r%2?'#FFFFFF':'#EAF1E9');
   cell.text.style={typeface:font,fontSize:24,color:r===0?'#FFFFFF':ink,bold:r===0,verticalAlignment:'middle',insets:15};
 }
 return t;
}
let s=slide('ระบบ AI คัดแยกขยะ',1,{dark:true,kicker:'AI TRANSFORMATION PROJECT'});
text(s,'Smart Waste Detective\nfor Recycling Center',64,203,1100,155,57,'#FFFFFF',true);
text(s,'ถ่ายภาพเพื่อเรียนรู้ประเภทขยะ\nพร้อมคำแนะนำและประวัติการวิเคราะห์',64,382,1000,98,30,'#D6E7DA');
text(s,'สมาชิกกลุ่ม 4 คน',64,507,1100,30,22,'#BADDAC',true);
text(s,'1. ชื่อ __________________ รหัส __________    2. ชื่อ __________________ รหัส __________\n3. ชื่อ __________________ รหัส __________    4. ชื่อ __________________ รหัส __________',64,551,1152,82,21,'#FFFFFF');
s.speakerNotes.text='ชื่อสมาชิกและรหัสยังเว้นให้กลุ่มกรอก โครงการวิชา IT232 ตามเอกสารโจทย์ที่ผู้ใช้แนบ ต้นแบบเพื่อการศึกษา';

s=slide('ปัญหาการคัดแยกขยะ',2);
text(s,'รูปลักษณ์อาจคล้ายกัน\nแต่วัสดุและจุดรับต่างกัน',64,222,510,110,35,ink,true);
text(s,'ผู้ใช้ยังต้องอ่านฉลากและสอบถาม\nขยะอันตรายต้องแยกจากถังรวม\nข้อมูลการขอคำแนะนำมักไม่ถูกเก็บ',64,365,500,185,29,muted);
const sample=(label)=>evaluation.results.find(r=>r.label===label).path;
await image(s,'data/'+sample('Plastic'),620,209,255,320,'ขวดพลาสติกในชุดข้อมูลตัวอย่าง');
await image(s,'data/'+sample('Glass'),922,209,255,320,'วัตถุแก้วในชุดข้อมูลตัวอย่าง');
text(s,'พลาสติก',660,551,230,40,27);text(s,'แก้ว',1001,551,150,40,27);
s.speakerNotes.text='ภาพจากชุดข้อมูล Suman Kunwar / D.Waste.app, MIT ตาม dataset card https://huggingface.co/datasets/omasteam/waste-garbage-management-dataset แหล่งรายภาพใน data/sample_manifest.csv ปัญหาขยะปนเปื้อนเป็นเหตุผลของโครงการ ยังไม่ได้วัดปริมาณที่ลดลง';

s=slide('วัตถุประสงค์ของโครงการ',3);
for(const [i,title,body] of [
 [1,'ช่วยระบุประเภทจากภาพ','พลาสติก กระดาษ แก้ว และตัวอย่างขยะอันตราย'],
 [2,'ให้คำแนะนำที่ตรวจสอบต่อได้','อธิบายการแยกเก็บและให้ตรวจเงื่อนไขจุดรับจริง'],
 [3,'รวบรวมประวัติการวิเคราะห์','Dashboard และ CSV จากข้อมูลใน SQLite'],
 [4,'วัดผลพร้อมรายงานข้อผิดพลาด','แยกผลทดสอบระบบออกจากความสามารถของโมเดล']]){
 const y=203+(i-1)*107;text(s,String(i).padStart(2,'0'),64,y,85,60,41,green,true);
 text(s,title,172,y,1030,48,31,ink,true);text(s,body,172,y+47,1030,46,25,muted);
}
s.speakerNotes.text='วัตถุประสงค์ตรงกับฟังก์ชันที่พัฒนาจริง ข้อมูลนับครั้งการวิเคราะห์ ไม่ใช่จำนวนขยะที่รีไซเคิล';

s=slide('แนวคิดของระบบ',4,{dark:true});
text(s,'ภาพหนึ่งภาพเป็นจุดเริ่มต้นของคำแนะนำ',64,207,1150,65,35,'#FFFFFF');
for(const [label,x] of [['รับภาพ',64],['CLIP',366],['ผลและคำแนะนำ',668],['ประวัติและกราฟ',970]])flow(s,label,x,333,246,95);
arrow(s,320,369,36);arrow(s,622,369,36);arrow(s,924,369,36);
text(s,'Upload / Camera',64,454,246,55,23,'#D6E7DA');
text(s,'Prompt ensemble',366,454,246,55,23,'#D6E7DA');
text(s,'มีเส้นทาง Unknown',668,454,246,55,23,'#D6E7DA');
text(s,'SQLite / Plotly',970,454,246,55,23,'#D6E7DA');
text(s,'ประมวลผลในเครื่อง  เก็บผลและรหัสภาพ  ไม่เก็บภาพต้นฉบับถาวร',64,575,1150,55,24,'#BADDAC');
s.speakerNotes.text='สถาปัตยกรรมจาก app.py และ services/ ในโครงการ ไม่มี external inference API ขั้นติดตั้งต้องดาวน์โหลดโมเดลก่อน';

s=slide('ก่อนและหลังใช้ AI',5);
table(s,[['ขั้นตอน','วิธีเดิม','ต้นแบบที่พัฒนา'],['ระบุประเภท','อ่านป้ายหรือค้นหาเอง','AI เสนอประเภทจากภาพ'],['ตรวจสอบ','ถามเจ้าหน้าที่เมื่อไม่แน่ใจ','คะแนนและ Unknown ช่วยเตือน'],['ให้ความรู้','ค้นคำแนะนำแยกจากกัน','คำแนะนำปรากฏพร้อมผล'],['เก็บข้อมูล','อาจไม่มีประวัติ','History และ Dashboard']],64,205,1152,365,[220,430,502]);
text(s,'ยังต้องวัดเวลาและผลกับผู้ใช้จริง เพื่อยืนยันว่าช่วยงานได้มากเพียงใด',64,595,1150,52,25,muted);
s.speakerNotes.text='เป็นการเปรียบเทียบ workflow ไม่ได้มีข้อมูลทดลองลดเวลา ยังไม่มี user feedback';

s=slide('Workflow ของระบบ',6);
for(const [label,x] of [['Start และรับภาพ',64],['ตรวจไฟล์',366],['Preprocessing',668],['CLIP และคะแนน',970]])flow(s,label,x,204,246,78);
arrow(s,320,233,36);arrow(s,622,233,36);arrow(s,924,233,36);
text(s,'ตรวจคะแนน ≥ 0.65 และส่วนต่าง ≥ 0.15',64,320,1150,42,27,green,true);
flow(s,'ผ่านเกณฑ์\nประเภทและวิธีจัดการ',100,402,430,93);
flow(s,'ไม่ผ่านเกณฑ์\nUnknown และให้ถ่ายใหม่',750,402,430,93,'#F5EBD9');
text(s,'ทั้งสองเส้นทางบันทึกผลลงฐานข้อมูล',64,537,1150,45,29,ink,true);
text(s,'History และ Dashboard อ่านข้อมูลล่าสุด แล้วจบการวิเคราะห์',64,594,1150,45,25,muted);
s.speakerNotes.text='แผนผังฉบับเต็มใน docs/Workflow_Diagram.svg และ PNG ไฟล์เสียไม่เข้าขั้น inference เกณฑ์เริ่มต้นยังไม่ผ่าน calibration และอาจมั่นใจผิด';

s=slide('AI และการปรับแต่ง',7);
text(s,'CLIP ViT B 32',64,210,600,70,44,green,true);
text(s,'ภาพและข้อความถูกแปลงเป็นเวกเตอร์\nแล้วเปรียบเทียบความคล้ายกัน',64,301,1050,96,32);
text(s,'3 คำอธิบายต่อกลุ่ม',64,435,550,48,30,ink,true);
text(s,'รวมเวกเตอร์เป็น prompt ensemble\nPlastic / Paper / Glass / Hazardous / Unknown',64,491,1100,86,27,muted);
text(s,'เป็น Prompt Engineering ยังไม่มีการ fine-tune น้ำหนักโมเดล',64,604,1150,40,25,green,true);
s.speakerNotes.text='https://huggingface.co/openai/clip-vit-base-patch32 ใช้ prompt_version waste-v1 ใน config/categories.json คะแนน softmax ไม่ใช่ calibrated probability ภาพ Hazardous ครอบคลุมตัวอย่างแบตเตอรี่และภาชนะฉลากอันตราย ไม่ระบุสารภายใน';

s=slide('Web Application ที่พัฒนา',8);
text(s,'Upload หรือถ่ายภาพ',64,216,360,60,30,ink,true);
text(s,'เห็นภาพก่อนวิเคราะห์\nกด Analyze Waste\nดูประเภท คะแนน และคำแนะนำ\nบันทึกลงฐานข้อมูลอัตโนมัติ',64,304,363,228,27,muted);
await image(s,'assets/screenshots/result_hazardous.png',452,189,764,430,'ผลวิเคราะห์แบตเตอรี่จากการทดสอบเว็บจริง');
text(s,'ภาพหน้าจอจริงจาก session ทดสอบแบตเตอรี่',452,630,760,30,21,muted);
s.speakerNotes.text='ภาพจาก Playwright ทดสอบเว็บ localhost จริง ใช้ไฟล์ data/samples/battery/battery_268.jpg ที่อยู่ใน manifest เปิดในฐานข้อมูล QA แยกจากฐานข้อมูลหลัก กล้องยังไม่ได้ถ่ายจากอุปกรณ์จริง';

s=slide('Dashboard จากข้อมูลจริง',9);
await image(s,'assets/screenshots/dashboard_data.png',64,185,740,440,'Dashboard จากผลกระดาษและแบตเตอรี่ที่วิเคราะห์ใน QA จริง');
text(s,'นับครั้งวิเคราะห์',850,222,360,60,31,ink,true);
text(s,'สัดส่วนแต่ละประเภท\nกราฟเปรียบเทียบจำนวน\nแนวโน้มรายวัน\nประวัติล่าสุดและ CSV',850,310,360,220,28,muted);
text(s,'ตัวอย่าง 2 รายการจาก QA จริง ไม่ใช่ปริมาณขยะที่รีไซเคิลแล้ว',64,630,1150,35,23,green);
s.speakerNotes.text='ภาพหน้าจอจริงจากการอัปโหลด Paper และ Hazardous ในฐานข้อมูล QA ชื่อไฟล์ .cache/browser_qa.db ภาพนี้ไม่ใช่ข้อมูลจากสถานที่รีไซเคิลจริง ฐานข้อมูลหลักเริ่มว่าง ค่ากราฟมาจาก SQLite';

s=slide('ผลทดสอบเบื้องต้น',10);
text(s,'44 / 50 ภาพ',64,203,560,85,56,green,true);
text(s,'Accuracy 88%  และ macro F1 0.871',64,300,1100,46,30,ink,true);
table(s,[['กลุ่ม','ทายถูก / ภาพ'],['Plastic','5 / 10'],['Paper','9 / 10'],['Glass','10 / 10'],['Hazardous เฉพาะแบตเตอรี่','10 / 10'],['Unknown เฉพาะ Biological','10 / 10']],64,370,710,253,[490,220]);
text(s,'17 functional tests ผ่าน',821,381,390,70,29,ink,true);
text(s,`CPU median ${evaluation.latency_ms_median.toFixed(1)} ms\nไม่รวมเวลาโหลดโมเดล`,821,472,390,92,25,muted);
text(s,'ชุดตัวอย่างแหล่งเดียว ยังใช้รับประกันผลหน้างานไม่ได้',821,577,390,65,23,green);
s.speakerNotes.text='ค่าจาก docs/evaluation.json และ pytest_results.xml แหล่งภาพ https://huggingface.co/datasets/omasteam/waste-garbage-management-dataset seed232 กลุ่มละ10 ตั้ง threshold=.65 margin=.15 ก่อนดู test ผล Plastic ผิดเป็น Glass3 และ Unknown2, Paper Unknown1 Coverage74% คะแนน label จากผู้เผยแพร่ ยังต้องตรวจด้วยคน ไม่ทราบ pretraining overlap';

s=slide('ประโยชน์และข้อจำกัด',11);
text(s,'สิ่งที่ต้นแบบช่วยได้',64,215,550,55,33,green,true);
text(s,'คำแนะนำอยู่กับผลวิเคราะห์\nเก็บประวัติและตรวจผลย้อนหลัง\nมีข้อมูลสำหรับพัฒนาระบบต่อ',64,301,540,197,29);
text(s,'สิ่งที่ต้องพัฒนาต่อ',684,215,532,55,33,green,true);
text(s,'พลาสติกยังสับสนกับแก้ว\nภาพหลายวัตถุได้เพียงประเภทเดียว\nภาพบอกสารเคมีภายในไม่ได้\nต้องทดสอบกล้องและผู้ใช้จริง',684,301,530,260,28,muted);
text(s,'เก็บภาพหน้างาน  ตรวจ label  แยก validation และ test  แล้วปรับเกณฑ์',64,594,1152,57,26,ink,true);
s.speakerNotes.text='ข้อผิดพลาดจาก evaluation.json และ robustness.json คำแนะนำการแยกแบตเตอรี่อ้างอิง https://www.epa.gov/recycle/used-household-batteries และตรวจเงื่อนไขจุดรับท้องถิ่น ไม่มีการอ้างว่าลดเวลา ลดปริมาณขยะ หรือได้ feedback แล้ว';

s=slide('สรุปและคำถาม',12,{dark:true});
text(s,'ต้นแบบที่สาธิตได้\nพร้อมหลักฐานทดสอบ',64,223,1120,165,58,'#FFFFFF',true);
text(s,'AI ช่วยเสนอประเภท  ผู้ใช้ตรวจสอบก่อนคัดแยก\nขั้นต่อไปคือทดสอบกับภาพและผู้ใช้ในพื้นที่จริง',64,432,1100,105,31,'#D6E7DA');
text(s,'Q&A',64,583,600,60,42,'#BADDAC',true);
s.speakerNotes.text='สาธิตตาม docs/Demo_Guide.md ข้อเสนอแนะที่ต้องการคือปรับ prompts หรือเตรียม fine-tuning กับข้อมูลหน้างาน ไม่มี public demo URL ในรอบนี้';

for(const [i,slide] of pres.slides.items.entries()){
 const png=await pres.export({slide,format:'png',scale:1});
 await fs.writeFile(path.join(tmp,`slide-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await png.arrayBuffer()));
}
const candidate=path.join(tmp,'candidate.pptx');
await (await PresentationFile.exportPptx(pres)).save(candidate);
const {finalizePresentation}=await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')).href);
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,
 finalPath:path.join(root,'docs/Final_Presentation.pptx'),
 pythonExecutable:runtime+'/python/python.exe',
 integrityValidatorPath:skill+'/container_tools/inspect_presentation_package_integrity.py',
 layoutValidatorPath:skill+'/container_tools/inspect_presentation_layout_geometry.py',
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','5','--require-native-table-slide','10'],
 explicitTotalSlideCount:12,requiredNativeTableOwnerSlides:[5,10],requiredNativeChartOwnerSlides:[],
 fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,
 receiptPath:path.join(tmp,'validation.json')});
console.log(JSON.stringify(result));
