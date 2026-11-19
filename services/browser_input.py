"""Send image bytes on the active Streamlit WebSocket on serverless hosts.

Native file/camera HTTP uploads can reach a different Vercel instance from the
session holding the model. Inline component v2 state stays on that session.
"""
import base64
import binascii
import io
import streamlit as st

HTML = '''<section class="image-input">
<div class="upload"><label for="waste-file">เลือก JPG หรือ PNG ไม่เกิน 10 MB</label>
<input id="waste-file" type="file" accept="image/jpeg,image/png" /></div>
<div class="camera" hidden><button id="camera-start" type="button">เปิดกล้อง</button>
<video autoplay playsinline muted hidden aria-label="ภาพจากกล้อง"></video>
<button id="camera-snap" type="button" hidden>ถ่ายภาพ</button>
<button id="camera-stop" type="button" hidden>ปิดกล้อง</button></div>
<p class="status" role="status" aria-live="polite"></p>
</section>'''
CSS = '''.image-input{font-family:"Leelawadee UI",sans-serif;color:#18392D;padding:16px;border:1px dashed #aac8b7;border-radius:14px;background:#f0f6f1}
label{display:block;margin-bottom:10px;font-size:14px}input{max-width:100%;font:inherit;font-size:14px}
button,input::file-selector-button{border:0;border-radius:9px;padding:10px 14px;background:#18845D;color:white;font:inherit;cursor:pointer;min-height:44px}
button{margin:4px 6px 4px 0}button:focus-visible,input:focus-visible{outline:3px solid #166445;outline-offset:3px}
video{display:block;width:100%;max-height:320px;margin-top:10px;border-radius:10px}.status{font-size:13px;margin:8px 0 0}
[hidden]{display:none!important}'''
JS = '''export default function({parentElement,data,setStateValue}) {
 const root=parentElement; const input=root.querySelector('input');
 const status=root.querySelector('.status');const camera=root.querySelector('.camera');
 const video=root.querySelector('video');const start=root.querySelector('#camera-start');
 const snap=root.querySelector('#camera-snap');const stop=root.querySelector('#camera-stop');
 let stream=null,disposed=false;
 const reject=message=>{status.textContent=message;setStateValue('image',{error:true});};
 root.querySelector('.upload').hidden=data.mode==='camera';camera.hidden=data.mode!=='camera';
 const stopCamera=()=>{if(stream)stream.getTracks().forEach(t=>t.stop());stream=null;video.srcObject=null;video.hidden=true;snap.hidden=true;stop.hidden=true;start.hidden=false;};
 async function publish(file){
  if(!file)return;
  if(!['image/jpeg','image/png'].includes(file.type)){reject('กรุณาเลือกภาพ JPG หรือ PNG');return;}
  if(file.size>10*1024*1024){reject('ภาพเกิน 10 MB กรุณาลดขนาดภาพ');return;}
  status.textContent='กำลังเตรียมภาพ…';
  const reader=new FileReader();
  reader.onload=()=>{if(disposed)return;status.textContent='เลือกภาพแล้ว: '+file.name;setStateValue('image',{name:file.name,base64:String(reader.result).split(',')[1]});};
  reader.onerror=()=>reject('อ่านภาพไม่สำเร็จ กรุณาเลือกใหม่');reader.readAsDataURL(file);
 }
 input.onchange=()=>publish(input.files?.[0]);
 start.onclick=async()=>{
  try{stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:'environment'},audio:false});
   if(disposed){stopCamera();return;}video.srcObject=stream;await video.play();video.hidden=false;snap.hidden=false;stop.hidden=false;start.hidden=true;status.textContent='วางขยะให้เห็นชัดแล้วกดถ่ายภาพ';
  }catch(e){status.textContent='เปิดกล้องไม่ได้ กรุณาอนุญาตกล้อง หรือเลือกอัปโหลดภาพ';}
 };
 snap.onclick=()=>{if(!video.videoWidth)return;const canvas=document.createElement('canvas');
  const scale=Math.min(1,1600/video.videoWidth);canvas.width=Math.round(video.videoWidth*scale);canvas.height=Math.round(video.videoHeight*scale);
  canvas.getContext('2d').drawImage(video,0,0,canvas.width,canvas.height);
  canvas.toBlob(blob=>{if(blob){stopCamera();publish(new File([blob],'camera.jpg',{type:'image/jpeg'}));}},'image/jpeg',.9);
 };
 stop.onclick=stopCamera;
 return ()=>{disposed=true;stopCamera();input.onchange=null;start.onclick=null;snap.onclick=null;stop.onclick=null;};
}'''

_image_component=st.components.v2.component('waste_browser_image',html=HTML,css=CSS,js=JS)

def browser_image(source):
    mode='camera' if source=='ถ่ายจากกล้อง' else 'upload'
    result=_image_component(data={'mode':mode},default={'image':None},
                           key='browser_image_'+mode,on_image_change=lambda:None)
    payload=result.image
    if not payload:return None
    if isinstance(payload,dict) and payload.get('error'):
        raise ValueError('อ่านภาพไม่ได้ กรุณาเลือก JPG หรือ PNG ไม่เกิน 10 MB อีกครั้ง')
    encoded=payload.get('base64') if isinstance(payload,dict) else None
    if not isinstance(encoded,str) or len(encoded)>14*1024*1024:
        raise ValueError('ข้อมูลภาพไม่ถูกต้องหรือภาพมีขนาดเกินกำหนด')
    try:raw=base64.b64decode(encoded,validate=True)
    except (ValueError,binascii.Error) as exc:raise ValueError('อ่านข้อมูลภาพไม่สำเร็จ กรุณาเลือกใหม่') from exc
    if len(raw)>10*1024*1024:raise ValueError('ภาพเกิน 10 MB กรุณาลดขนาดภาพ')
    return io.BytesIO(raw)
