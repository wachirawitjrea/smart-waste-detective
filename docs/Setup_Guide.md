# คู่มือติดตั้ง

# Smart Waste Detective for Recycling Center

ระบบ AI ตรวจจับและแยกประเภทขยะอัจฉริยะ สำหรับ IT232 มหาวิทยาลัยกรุงเทพ

## เปิดเว็บบนเครื่องนี้
ดับเบิลคลิก `run.bat` แล้วเปิด http://localhost:8501
เครื่องนี้เตรียม `.venv` และโมเดลไว้แล้ว หากย้ายเครื่องให้ติดตั้งตามขั้นตอนด้านล่าง

## ติดตั้งบน Windows
แนะนำ Python 3.11 แบบ 64-bit และพื้นที่ว่างประมาณ 3 GB สำหรับ dependencies กับโมเดล
เปิด PowerShell ในโฟลเดอร์โปรเจกต์:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/download_model.py
.venv\Scripts\python.exe -m streamlit run app.py
```

หรือรัน `powershell -ExecutionPolicy Bypass -File setup.ps1` เฉพาะสคริปต์ติดตั้งนี้
การดาวน์โหลดครั้งแรกต้องมีอินเทอร์เน็ต หลังมีโมเดลครบแล้ววิเคราะห์แบบ offline ได้ ไม่ต้องใช้ API key
PyTorch CPU ใช้ได้ ไม่ต้องมี GPU หากไม่ต้องการ CUDA ใช้ `pip install torch --index-url https://download.pytorch.org/whl/cpu`
ใช้ `requirements-lock.txt` เพื่ออ้างอิงเวอร์ชันที่ทดสอบจริงใน Windows CPU

## วิธีใช้
1. กดเริ่มวิเคราะห์ เลือกอัปโหลดหรือถ่ายจากกล้อง วางวัตถุหนึ่งชิ้นให้เห็นชัด
2. หากเป็นการลองระบบให้เลือก “บันทึกเป็นข้อมูลทดสอบ” ก่อนกด Analyze Waste
3. อ่านประเภท คะแนน และคำแนะนำ หาก Unknown ให้ถ่ายใหม่หรือสอบถามเจ้าหน้าที่
4. เปิด Dashboard ดูสถิติจริง หรือ History เพื่อกรองและส่งออก CSV
5. ลบเฉพาะรายการทดสอบใน History โดยกดยืนยันก่อน

## AI ที่ใช้จริง
CLIP ViT-B/32 เปรียบเทียบภาพกับ prompt ensemble เฉพาะ Plastic, Paper, Glass, Hazardous และ Unknown
ปรับแต่ง prompts และกติกาการยอมรับผล ไม่ได้ fine-tune น้ำหนัก ค่าเริ่มต้น threshold=0.65, margin=0.15 ยังไม่ calibrate
คะแนนโมเดลไม่ใช่ accuracy และไม่ยืนยันความปลอดภัยของวัตถุ Hazardous มีขอบเขตหลักเป็นแบตเตอรี่และภาพภาชนะที่มีฉลากอันตราย
AI จำแนกทั้งภาพหนึ่งประเภท ไม่มี bounding boxes ไม่แยกหลายวัตถุ และอาจมั่นใจผิดกับภาพเบลอ/นอกกลุ่ม

## ทดสอบและประเมิน
```powershell
.venv\Scripts\python.exe -m pytest -q --junitxml=docs/pytest_results.xml
.venv\Scripts\python.exe scripts/download_samples.py
.venv\Scripts\python.exe scripts/evaluate.py data/sample_manifest.csv --output docs/evaluation.json
```
ดู `docs/Test_Report.md`, `docs/Dataset_Plan.md` และผล JSON/XML จริง
ชุดข้อมูลตัวอย่างใช้เพื่อวินิจฉัยเบื้องต้น ต้องเก็บภาพในพื้นที่จริงเพิ่มก่อนอ้างผลการใช้งานทั่วไป

## โครงสร้าง
`app.py` หน้าเว็บ • `services/engine.py` AI • `services/images.py` ตรวจภาพ • `services/storage.py` SQLite/CSV
`config/` prompts และเกณฑ์ • `scripts/` ดาวน์โหลด/ประเมิน • `tests/` automated tests
`docs/` เอกสารและผลทดสอบ • `assets/screenshots/` ภาพจากระบบจริง • `data/` manifest/ตัวอย่าง

## ข้อมูลและความเป็นส่วนตัว
รูปไม่ถูกส่งไป API และไม่เก็บถาวร เก็บ SHA-256, เวลา UTC, ประเภท, คะแนน, รุ่น prompts และเกณฑ์ที่ใช้
ไฟล์ SQLite อยู่ `database/waste.db` เว็บเป็น local demo ไม่มี login หรือการแบ่งสิทธิ์ ห้ามเปิดเป็นบริการสาธารณะโดยไม่เพิ่มการควบคุมสิทธิ์
Dashboard แสดงวันตาม Asia/Bangkok ตาราง/CSV เก็บเวลา UTC และนับครั้งวิเคราะห์ ไม่ใช่ปริมาณรีไซเคิล

## ปัญหาที่พบบ่อย
- `python` เปิด Microsoft Store: ติดตั้ง Python 3.11 จาก python.org แล้วเปิด terminal ใหม่
- ไม่มีโมเดล: รัน `scripts/download_model.py` จนจบก่อนเปิดวิเคราะห์
- ดาวน์โหลดไม่ได้: ตรวจอินเทอร์เน็ต/พื้นที่ว่าง แล้วลองใหม่ ไฟล์ที่เสร็จแล้วจะใช้ต่อได้
- กล้องไม่ขึ้น: ใช้ localhost/HTTPS และอนุญาตกล้องในเบราว์เซอร์ หรืออัปโหลดภาพแทน
- port 8501 ถูกใช้: เพิ่ม `--server.port 8502` ในคำสั่ง Streamlit
- คะแนนสูงแต่ผิด: บันทึกเป็น failure case ปรับจาก validation set และตรวจฉลากจริง ห้ามเชื่อคะแนนแทนความปลอดภัย

## ก่อนส่งอาจารย์
เติมชื่อ/รหัสสมาชิก ตรวจภาพและ label ของ dataset ทดสอบกล้องจริง เก็บ feedback ผู้ใช้ และซ้อมสาธิต
ยังไม่มีลิงก์ deploy สาธารณะ ไม่ได้ส่งข้อความใน Teams หรือ push repository ที่ไม่ได้ระบุ
Canva สร้างดีไซน์ไม่ได้เนื่องจากเครดิตบัญชีหมด ใช้ไฟล์ PPTX ที่แก้ไขได้ใน docs แทน

## แหล่งอ้างอิง
- https://huggingface.co/openai/clip-vit-base-patch32
- https://huggingface.co/datasets/omasteam/waste-garbage-management-dataset
- https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input
- https://www.epa.gov/recycle/how-do-i-recycle-common-recyclables
- https://www.epa.gov/recycle/used-household-batteries

รูป Dribbble/Behance ที่ผู้ใช้แนบใช้เป็นแรงบันดาลใจด้านสีและโครงหน้า ไม่ได้นำงานออกแบบมาอ้างเป็นผลงานของกลุ่ม
