import './style.css';
import {getRows,saveRow,clearTests,csv} from './storage.js';
const $=selector=>document.querySelector(selector), $$=selector=>[...document.querySelectorAll(selector)];
const config=await fetch('/config.json').then(r=>{if(!r.ok)throw Error('โหลดการตั้งค่าไม่สำเร็จ');return r.json();});
const escape=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels=config.categories;
const symbols={Plastic:'♧',Paper:'▤',Glass:'♙',Hazardous:'ϟ',Unknown:'?'};
const examples={Plastic:'ขวดน้ำ · ถุง · แก้วพลาสติก',Paper:'กระดาษ · กล่อง · หนังสือพิมพ์',Glass:'ขวดแก้ว · โหลแก้ว',Hazardous:'ถ่านไฟฉาย · แบตเตอรี่'};
let selected=null,stream=null,previewUrl=null,worker=null,busy=false,imageGeneration=0;
function showPage(){
  const page=['home','scan','dashboard','history'].includes(location.hash.slice(1))?location.hash.slice(1):'home';
  if(page!=='scan')stopCamera();
  $$('.page').forEach(el=>el.hidden=el.id!==page);
  $$('nav a').forEach(el=>{if(el.dataset.page===page)el.setAttribute('aria-current','page');else el.removeAttribute('aria-current');});
  updateData();window.scrollTo(0,0);
}
$$('[data-go]').forEach(el=>el.addEventListener('click',()=>location.hash=el.dataset.go));
window.addEventListener('hashchange',showPage);
$('#categories').innerHTML=Object.entries(labels).filter(([key])=>key!=='Unknown').map(([key,c])=>`<article class="category" style="--accent:${c.color}"><div class="category-icon" aria-hidden="true">${symbols[key]}</div><h3>${c.th}</h3><p class="category-en">${key}</p><div class="category-examples">${examples[key]}</div></article>`).join('');
function updateData(){
  const real=getRows().filter(r=>!r.is_test),accepted=real.filter(r=>r.category!=='Unknown');
  $$('[data-stats]').forEach(el=>el.innerHTML=[['การวิเคราะห์ทั้งหมด',real.length],['ระบุประเภทได้',accepted.length],['ต้องตรวจสอบเพิ่มเติม',real.length-accepted.length]].map(([label,n])=>`<div class="stat"><span class="stat-label">${label}</span><strong>${n}</strong><small>ครั้ง</small></div>`).join(''));
  $('#chart').innerHTML=real.length?Object.entries(labels).map(([key,c])=>{const count=real.filter(r=>r.category===key).length;return `<div class="chart-row" style="--accent:${c.color}"><span>${c.th}</span><div class="chart-bar"><span style="width:${count/real.length*100}%"></span></div><b>${count}</b></div>`;}).join(''):'<p class="note">ยังไม่มีข้อมูล เริ่มสแกนขยะชิ้นแรกได้เลย</p>';
  const rows=getRows().filter(r=>$('#include-test').checked||!r.is_test);
  $('#history-list').innerHTML=rows.length?rows.map(r=>`<article class="history-card"><div><h3>${escape(labels[r.category]?.th||r.category)} ${r.is_test?'<span class="badge">ทดสอบ</span>':''}</h3><p>${escape(new Date(r.created_at).toLocaleString('th-TH'))} · ${r.source==='camera'?'กล้อง':'อัปโหลด'}</p><p>${escape(r.category)} · ${escape(r.status)} · ${escape(r.elapsed_ms)} ms</p></div><strong>${(r.confidence*100).toFixed(1)}%</strong></article>`).join(''):'<div class="panel empty-result"><h2>ยังไม่มีประวัติ</h2><p>ผลวิเคราะห์ของคุณจะแสดงที่นี่</p></div>';
  $('#export').disabled=!rows.length;
}
$('#include-test').addEventListener('change',updateData);
$('#export').addEventListener('click',()=>{const rows=getRows().filter(r=>$('#include-test').checked||!r.is_test);const url=URL.createObjectURL(new Blob([csv(rows)],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='waste-detective-history.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),3000);});
$('#clear-tests').addEventListener('click',()=>{if(!getRows().some(r=>r.is_test))return;if(confirm('ลบข้อมูลทดสอบทั้งหมดในอุปกรณ์นี้หรือไม่?')){$('#storage-message').textContent=clearTests()?'ลบข้อมูลทดสอบแล้ว':'เบราว์เซอร์ไม่อนุญาตให้บันทึกการเปลี่ยนแปลง';updateData();}});
function error(message){$('#input-error').textContent=message;$('#input-error').hidden=!message;}
function resetResult(){$('#result-panel').innerHTML='<div class="empty-result"><span>✧</span><h2>พร้อมช่วยคัดแยก</h2><p>เลือกภาพ แล้วกด Analyze Waste</p></div>';}
function stopCamera(){if(stream){stream.getTracks().forEach(t=>t.stop());stream=null;}$('#camera').srcObject=null;$('#camera').hidden=true;$('#capture').disabled=true;$('#close-camera').hidden=true;$('#open-camera').disabled=false;}
function mode(camera){if(busy)return;$('#upload-panel').hidden=camera;$('#camera-panel').hidden=!camera;$('#upload-tab').classList.toggle('selected',!camera);$('#camera-tab').classList.toggle('selected',camera);$('#upload-tab').setAttribute('aria-pressed',String(!camera));$('#camera-tab').setAttribute('aria-pressed',String(camera));if(!camera)stopCamera();}
$('#upload-tab').onclick=()=>mode(false);$('#camera-tab').onclick=()=>mode(true);
$('#close-camera').onclick=stopCamera;
$('#open-camera').onclick=async()=>{try{error('');stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:{ideal:'environment'}},audio:false});$('#camera').srcObject=stream;$('#camera').hidden=false;await $('#camera').play();$('#capture').disabled=false;$('#close-camera').hidden=false;$('#open-camera').disabled=true;}catch{stopCamera();error('เปิดกล้องไม่ได้ กรุณาอนุญาตสิทธิ์กล้อง หรือใช้ปุ่มถ่ายภาพด้วยกล้องมือถือ');}};
$('#capture').onclick=()=>{const video=$('#camera');if(!video.videoWidth)return;const canvas=document.createElement('canvas');const scale=Math.min(1,1600/video.videoWidth,1600/video.videoHeight);canvas.width=Math.round(video.videoWidth*scale);canvas.height=Math.round(video.videoHeight*scale);canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);canvas.toBlob(blob=>{if(blob)selectImage(new File([blob],'camera.jpg',{type:'image/jpeg'}),'camera');stopCamera();},'image/jpeg',.92);};
async function selectImage(file,source){
  if(busy||!file)return;
  const generation=++imageGeneration;selected=null;$('#analyze').disabled=true;$('#preview-box').hidden=true;error('');resetResult();if(previewUrl)URL.revokeObjectURL(previewUrl);
  try{
    if(file.size>10*1024*1024)throw Error('ภาพใหญ่เกิน 10 MB กรุณาเลือกภาพที่เล็กลง');
    const sig=new Uint8Array(await file.slice(0,8).arrayBuffer());const jpeg=sig[0]===255&&sig[1]===216&&sig[2]===255;const png=[137,80,78,71,13,10,26,10].every((v,i)=>sig[i]===v);
    if(!jpeg&&!png)throw Error('กรุณาเลือกไฟล์ JPG หรือ PNG ที่เปิดอ่านได้');
    const bitmap=await createImageBitmap(file,{imageOrientation:'from-image'});
    if(generation!==imageGeneration){bitmap.close();return;}
    if(bitmap.width*bitmap.height>20000000){bitmap.close();throw Error('ภาพมีขนาดเกิน 20 ล้านพิกเซล กรุณาลดขนาดภาพก่อน');}
    const canvas=document.createElement('canvas'),scale=Math.min(1,1600/bitmap.width,1600/bitmap.height);canvas.width=Math.round(bitmap.width*scale);canvas.height=Math.round(bitmap.height*scale);
    const ctx=canvas.getContext('2d',{willReadFrequently:true});ctx.fillStyle='#fff';ctx.fillRect(0,0,canvas.width,canvas.height);ctx.drawImage(bitmap,0,0,canvas.width,canvas.height);bitmap.close();
    const rgba=ctx.getImageData(0,0,canvas.width,canvas.height).data,pixels=new Uint8ClampedArray(canvas.width*canvas.height*3);for(let i=0,j=0;i<rgba.length;i+=4){pixels[j++]=rgba[i];pixels[j++]=rgba[i+1];pixels[j++]=rgba[i+2];}
    const hash=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',await file.arrayBuffer())),x=>x.toString(16).padStart(2,'0')).join('');
    if(generation!==imageGeneration)return;
    selected={pixels,width:canvas.width,height:canvas.height,source,hash};previewUrl=URL.createObjectURL(file);$('#preview').src=previewUrl;$('#filename').textContent=file.name;$('#preview-box').hidden=false;$('#analyze').disabled=false;
  }catch(e){if(generation===imageGeneration)error(e.message||'อ่านภาพไม่ได้ กรุณาเลือกภาพใหม่');}
}
$('#file').onchange=e=>selectImage(e.target.files[0],'upload');$('#camera-file').onchange=e=>selectImage(e.target.files[0],'camera');
function setBusy(value){busy=value;['#file','#camera-file','#upload-tab','#camera-tab','#open-camera','#is-test'].forEach(id=>$(id).disabled=value);$('#analyze').disabled=value||!selected;}
function showResult(result){
  const c=labels[result.category];$('#result-panel').innerHTML=`<p class="eyebrow">ผลการวิเคราะห์</p><div class="result-category"><div class="category-icon" style="--accent:${c.color}">${symbols[result.category]}</div><h2>${c.th}</h2></div><div class="result-code" data-result-category="${result.category}">${result.category} • ${result.status}</div><div class="confidence">${(result.confidence*100).toFixed(1)}<small>%</small></div><p class="note">คะแนนของประเภทที่โมเดลให้อันดับหนึ่ง${result.category==='Unknown'?' · ระบบยังไม่มั่นใจ กรุณาตรวจสอบเพิ่มเติม':''}</p><div class="advice">${c.advice}</div><h3>คะแนนแต่ละประเภท</h3>${Object.entries(result.scores).map(([key,score])=>`<div class="score-row"><span>${labels[key].th}</span><div class="score-bar" style="--accent:${labels[key].color}"><span style="width:${score*100}%"></span></div><span>${(score*100).toFixed(1)}%</span></div>`).join('')}<p class="note">ประมวลผลภาพ ${result.elapsed_ms.toLocaleString('th-TH')} ms · CLIP q8 ในอุปกรณ์<br>คะแนนยังไม่ได้ปรับเทียบกับขยะในสถานที่จริง</p>`;
}
$('#analyze').onclick=()=>{
  if(!selected||busy)return;stopCamera();setBusy(true);error('');
  const current=selected,isTest=$('#is-test').checked;
  $('#result-panel').innerHTML='<div class="loading"><div class="spinner"></div><h2>กำลังเตรียม AI ในอุปกรณ์</h2><p id="loading-text">ครั้งแรกอาจใช้เวลาสักครู่ ขึ้นกับอินเทอร์เน็ตและอุปกรณ์</p><div class="progress-track"><span id="progress"></span></div></div>';
  if(!worker)worker=new Worker(new URL('./ai-worker.js',import.meta.url),{type:'module'});
  function failed(){setBusy(false);worker?.terminate();worker=null;$('#result-panel').innerHTML='<div class="empty-result"><h2>ยังวิเคราะห์ภาพไม่ได้</h2><p>ตรวจอินเทอร์เน็ตแล้วลองใหม่ หากเครื่องมีหน่วยความจำไม่พอ ให้ปิดแท็บอื่นหรือลองอุปกรณ์อีกเครื่อง</p></div>';}
  worker.onerror=failed;
  worker.onmessage=({data})=>{
    if(data.type==='progress'){$('#progress')?.style.setProperty('width',`${Math.max(0,Math.min(100,data.value||0))}%`);}
    if(data.type==='ready'&&$('#loading-text')){$('#loading-text').textContent='กำลังวิเคราะห์ภาพ กรุณารอสักครู่';$('.loading h2').textContent='AI กำลังดูภาพของคุณ';}
    if(data.type==='error'){console.error('Browser AI error:',data.message);failed();}
    if(data.type==='result'){
      const row={...data.result,id:crypto.randomUUID(),created_at:new Date().toISOString(),image_id:current.hash,source:current.source,is_test:isTest?1:0};
      const stored=saveRow(row);showResult(data.result);if(!stored)$('#result-panel').insertAdjacentHTML('beforeend','<p class="error">แสดงผลสำเร็จ แต่บันทึกประวัติถาวรไม่ได้ กรุณาส่งออก CSV ก่อนปิดหน้าเว็บ</p>');setBusy(false);updateData();
    }
  };
  // Do not transfer selected's buffer: it must stay available for an explicit retry.
  const copy=current.pixels.slice();worker.postMessage({...current,pixels:copy.buffer,config},[copy.buffer]);
};
window.addEventListener('pagehide',stopCamera);window.addEventListener('storage',updateData);showPage();
$$('[data-go]').forEach(el=>el.disabled=false);
