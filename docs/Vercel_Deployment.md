# Deploy บน Vercel

ข้อผิดพลาดเดิม `PYTHON_ENTRYPOINT_NOT_FOUND` เกิดจาก `app.py` เป็นสคริปต์หน้าเว็บ Streamlit จึงไม่ได้ export ASGI application ให้ Vercel เรียก

ฉบับนี้ใช้ Streamlit 1.67 ขึ้นไป และ `st.App` ใน `asgi.py` โดยกำหนด `[tool.vercel] entrypoint = "asgi:app"` ใน `pyproject.toml` หน้าเว็บเดิมยังรันผ่าน `streamlit run app.py` ได้

## ตั้งค่าโครงการ

1. เชื่อม Git repository `wachirawitjrea/-Waste-Detective` และใช้ branch `main` โดย Root Directory เป็นราก repository
2. ใช้ Python 3.12 หรือ 3.13 และ Fluid compute ที่รองรับ ASGI/WebSocket
3. Build Command ใช้ `python scripts/download_model.py` ตาม `vercel.json` เพื่อดาวน์โหลด CLIP รุ่นที่ตรึงไว้เข้า bundle ก่อนเริ่มเว็บ ไม่ต้อง commit น้ำหนักโมเดลลง GitHub
4. requirements เลือก PyTorch CPU จึงไม่ติดตั้ง CUDA หากระบบต้องการเปิด large functions ให้ตั้ง `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` ตามความสามารถของบัญชี ไม่จำเป็นต้องเปิดบริการเสียเงินเพื่อใช้ไฟล์ต้นแบบนี้
5. ลบ Output Directory หรือคำสั่ง Build เดิมที่ตั้งเองหากขัดกับ `vercel.json` แล้ว Redeploy commit ล่าสุด

## ขอบเขตของโหมดออนไลน์

- น้ำหนัก CLIP ประมาณ 605 MB รวมกับ dependency ต้องใช้ function bundle ขนาดใหญ่และมีช่วง cold start จึงต้องตรวจผล build ของบัญชีจริง
- Streamlit ใช้ WebSocket; การเชื่อมต่อมีอายุจำกัดตามแพลตฟอร์ม ผู้ใช้อาจต้องเปิดหน้าเว็บใหม่เมื่อหมดเวลา
- SQLite ใน `/tmp` เป็นข้อมูลชั่วคราวเฉพาะ instance ไม่ใช่ฐานข้อมูลกลาง ประวัติและสถิติอาจแตกต่างกันระหว่าง instance และหายเมื่อ redeploy ควรใช้การส่งออก CSV หรือพัฒนาฐานข้อมูลภายนอกสำหรับงานจริง
- เครื่อง local เก็บ SQLite ใน `database/waste.db` ตามเดิม
- การเพิ่ม config แก้ปัญหา entrypoint ไม่ใช่หลักฐานว่าการ deploy ออนไลน์สำเร็จ ต้องตรวจสถานะและทดสอบอัปโหลดภาพจริงก่อนรายงานผล

## ทดสอบ ASGI ในเครื่อง

```powershell
.venv\Scripts\python.exe -m uvicorn asgi:app --host 127.0.0.1 --port 8503
```

เปิด `http://localhost:8503` แล้วทดลองกดเริ่มวิเคราะห์ อัปโหลดภาพ และดูประวัติ

แหล่งอ้างอิง: [Python entrypoints](https://vercel.com/docs/functions/runtimes/python), [WebSocket functions](https://vercel.com/docs/functions/websockets), [Streamlit releases](https://docs.streamlit.io/develop/quick-reference/release-notes/2026)

## ผลตรวจ deployment ครั้งแรกหลังแก้โค้ด

Vercel อ่าน `asgi:app` ได้และดาวน์โหลดโมเดลสำเร็จแล้ว แต่ bundle มีขนาด 1,797.23 MB เกินเพดาน 500 MB ของโครงการเดิม จึงต้องเปิด Fluid compute และ `VERCEL_SUPPORT_LARGE_FUNCTIONS=1` ก่อน redeploy ผู้ใช้อนุญาตการตั้งค่านี้แล้วเมื่อ 15 พฤศจิกายน 2569 โดยไม่ได้อัปเกรดแผนหรือซื้อบริการเพิ่ม ผลสุดท้ายให้ดู `docs/deployment_validation.json`
