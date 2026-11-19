# นำ Smart Waste Detective ขึ้น GitHub

โค้ดชุดนี้นำขึ้น repository เพื่อแชร์ ส่งงาน และให้ผู้อื่นดาวน์โหลดไปรันได้ การอัปโหลดโค้ดไม่ได้ทำให้มีลิงก์เว็บออนไลน์ทันที เว็บต้องมี Python, dependency และโมเดล CLIP ก่อนรัน

## ใช้ไฟล์ชุดไหน

แนะนำ `Smart_Waste_Detective_GitHub_Ready.zip` ซึ่งรวมโค้ดและเอกสารทั้งหมดที่จำเป็นสำหรับ repository ไม่รวม `.venv`, cache, ประวัติฐานข้อมูล และน้ำหนักโมเดลขนาดใหญ่ มี `.gitignore`, `.gitattributes` และ `.streamlit/config.toml` อยู่ในชุดด้วย

แตก ZIP ก่อน แล้วเปิดโฟลเดอร์ `Smart-Waste-Detective` ให้เห็น `app.py`, `requirements.txt`, `README.md`, `config`, `services`, `models` และ `docs` อย่าอัปเฉพาะ ZIP เป็นไฟล์เดียว หากต้องการให้ GitHub แสดงโค้ดและใช้งานต่อได้

## วิธีอัปโหลดผ่านหน้าเว็บ

1. สร้าง repository ใหม่ใน GitHub เลือก Public หรือ Private ตามที่กลุ่มต้องการ
2. เลือก Add file แล้ว Upload files
3. อัปโหลดไฟล์และโฟลเดอร์ที่อยู่ข้างใน `Smart-Waste-Detective` ให้ `app.py` อยู่ที่ระดับบนสุดของ repository
4. ตรวจว่า `models/model_metadata.json`, `config`, `services` และ `requirements.txt` มาครบ
5. ไฟล์ที่ขึ้นต้นด้วยจุดอาจถูกซ่อนใน File Explorer ตรวจว่า `.gitignore`, `.gitattributes` และ `.streamlit/config.toml` ถูกอัปโหลดด้วย หากไม่พบให้เปิดการแสดง hidden files หรือใช้ GitHub Desktop/Git
6. ใส่ข้อความ commit เช่น `Add Smart Waste Detective project` แล้วบันทึก

ไฟล์แต่ละไฟล์ในชุด GitHub Ready มีขนาดต่ำกว่า 1 MB จึงไม่จำเป็นต้องใช้ Git LFS กับชุดนี้ อย่าอัปโหลดไฟล์จาก `Smart_Waste_Detective_With_Model.zip` เป็นไฟล์โค้ดใน repository ปกติ

## วิธีใช้ Git ถ้าติดตั้งไว้แล้ว

เปิด terminal ในโฟลเดอร์ `Smart-Waste-Detective` ที่แตกไฟล์แล้ว สร้าง repository ว่างบน GitHub ก่อน และแทน URL ตัวอย่างด้วย URL ของ repository จริง

```powershell
git init
git add .
git status
git commit -m "Add Smart Waste Detective project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
git push -u origin main
```

ตรวจ `git status` ว่าไม่มี `.venv`, `.cache`, `models/clip`, `.env` หรือไฟล์ฐานข้อมูลก่อน commit `.gitignore` จะกันไฟล์เหล่านี้สำหรับไฟล์ที่ยังไม่เคยถูก track

## คนอื่นดาวน์โหลดแล้วรันอย่างไร

ติดตั้ง Python 3.11 แบบ 64-bit จากนั้น clone หรือดาวน์โหลด ZIP จาก GitHub แล้วเปิด terminal ในโฟลเดอร์ที่มี app.py

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/download_model.py
.venv\Scripts\python.exe -m streamlit run app.py
```

เปิด http://localhost:8501 การดาวน์โหลดโมเดลครั้งแรกต้องมีอินเทอร์เน็ตและใช้พื้นที่ประมาณ 600 MB สำหรับไฟล์น้ำหนัก โมเดลรันบน CPU ได้และไม่ต้องมี API key เมื่อเปิดเว็บ ฐานข้อมูลใหม่จะถูกสร้างอัตโนมัติจากโค้ด ไม่จำเป็นต้องนำฐานข้อมูลผู้ใช้ขึ้น GitHub

บนเครื่องที่ติดตั้งครบแล้ว ใช้ `run.bat` ในครั้งต่อไปได้ ดูวิธีแก้ปัญหาเพิ่มเติมใน README

## ถ้าต้องการเว็บออนไลน์

GitHub Pages รองรับเว็บไซต์แบบ static และไม่รันเซิร์ฟเวอร์ Python จึงใช้เปิด Streamlit app นี้โดยตรงไม่ได้ ต้อง deploy บนบริการที่รัน Streamlit เช่น Streamlit Community Cloud หรือเซิร์ฟเวอร์ของกลุ่ม

ก่อน deploy ต้องจัดขั้นตอนดาวน์โหลดโมเดลบนเซิร์ฟเวอร์ ตั้งค่า address/port ให้ตรงกับบริการ ตรวจ RAM/พื้นที่จัดเก็บของ CLIP และเลือกที่เก็บข้อมูลถาวร เพราะ SQLite บนดิสก์ชั่วคราวของ cloud อาจหายเมื่อ restart หรือ redeploy การรันออนไลน์ยังไม่ได้ทดสอบในรอบนี้

สคริปต์สร้างเอกสารและสไลด์ใน `scripts` เป็นเครื่องมือผู้พัฒนาเสริม ไม่ต้องรันเพื่อเปิดเว็บ หากต้องสร้างสไลด์ใหม่ด้วยสคริปต์ ต้องมี Codex bundled runtime และตั้งค่า `CODEX_RUNTIME_DEPENDENCIES` กับ `PRESENTATIONS_SKILL_DIR` ให้ตรงกับเครื่อง ส่วน Word และ PowerPoint ที่ส่งมาเปิดแก้ไขได้ตามปกติ

## อ้างอิงที่ตรวจสอบ

- GitHub จำกัดขนาดไฟล์ทั่วไป: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- GitHub Pages ไม่รองรับ Python ฝั่งเซิร์ฟเวอร์: https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site
- การ deploy จาก repository ไป Streamlit Community Cloud: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

ตรวจเอกสารออนไลน์วันที่ 15 พฤศจิกายน 2569

## ผลตรวจชุดไฟล์ก่อนส่ง

ตรวจ ZIP ว่ามีไฟล์ตั้งค่าที่ขึ้นต้นด้วยจุด มี metadata สำหรับดาวน์โหลดโมเดล ไม่มีน้ำหนักโมเดลหรือฐานข้อมูล และไฟล์แต่ละไฟล์ไม่เกินขีดจำกัดอัปโหลดผ่านเบราว์เซอร์ จากนั้นแตกไฟล์ไปโฟลเดอร์ใหม่และรัน pytest ผ่าน 17 รายการ โดยใช้ dependency ใน virtual environment ที่ติดตั้งไว้แล้ว การตรวจนี้ไม่ได้หมายถึงการ deploy หรือการติดตั้ง dependency ใหม่บนเครื่องอื่นสำเร็จแล้ว
