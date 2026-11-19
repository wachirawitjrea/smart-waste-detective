# ข้อมูลและการปรับแต่ง AI

## สิ่งที่ใช้จริง
โมเดล CLIP ViT-B/32 จาก openai/clip-vit-base-patch32 ประมวลผลภายในเครื่อง
ปรับแต่งคำอธิบาย 15 ข้อใน config/categories.json กลุ่มละ 3 ข้อ แล้วเฉลี่ยเวกเตอร์ข้อความที่ normalize แล้ว
คะแนนมาจาก softmax ของ similarity ที่คูณ logit scale ของโมเดล ไม่ใช่ calibrated probability
ค่า threshold 0.65 และ margin 0.15 เป็นค่าเริ่มต้น กำหนดก่อนดูผลชุดตัวอย่าง ไม่ได้ปรับจากผล test
ไม่มีการฝึกน้ำหนักโมเดลและไม่มี training accuracy

## ชุดตัวอย่างวินิจฉัย
scripts/download_samples.py เลือกแบบกำหนด seed 232 จำนวน 10 ภาพต่อกลุ่มจากชุดข้อมูลของ Suman Kunwar / D.Waste.app บน Hugging Face
ใช้ Plastic, Paper, Glass, Battery -> Hazardous และ Biological -> Unknown รวม 50 ภาพ
แหล่งข้อมูลระบุ MIT ใน dataset card เก็บสำเนา card, revision, URL และไฟล์ manifest เพื่ออ้างอิง
ผลชุดนี้เป็น diagnostic sample ขนาดเล็ก ป้ายกำกับสืบทอดจากผู้เผยแพร่ ต้องตรวจด้วยคนอีกครั้ง
Battery ไม่ครอบคลุมสารเคมีหรือขยะอันตรายทุกชนิด Biological ไม่ครอบคลุมภาพที่ไม่มีขยะทุกกรณี
ชื่อไฟล์เป็น object_id ชั่วคราว ยังไม่ยืนยันว่าเป็นวัตถุคนละชิ้นจริง และอาจมีภาพคล้ายกัน
ไม่ทราบการซ้ำกับ pretraining ของ CLIP จึงไม่กล่าวอ้างว่าเป็น benchmark อิสระสมบูรณ์

## แผนเก็บข้อมูลของกลุ่มใน 6 สัปดาห์
ถ่ายขยะจริงที่ได้รับอนุญาตโดยไม่ติดใบหน้าหรือข้อมูลส่วนบุคคล ห้ามเปิดหรือทำลายขยะอันตรายเพื่อถ่ายภาพ
ตั้งเป้าอย่างน้อยกลุ่มละ 100 ภาพ รวม Unknown ที่หลากหลาย ใช้สองคนตรวจ label และให้คนที่สามตัดสินกรณีไม่ตรงกัน
แบ่งตามวัตถุและรอบถ่ายเป็น train 60%, validation 20%, test 20% ก่อนทำ augmentation
ไม่ให้ภาพขวดใบเดียวกันหรือภาพแปลงจากต้นฉบับเดียวกันอยู่หลาย split ตรวจ hash และทบทวนภาพคล้ายกัน
ใช้ train เฉพาะเมื่อเลือกฝึก classification head หรือ fine-tune จริง บันทึก seed, hyperparameters, loss, checkpoint และ license
ใช้ validation เลือก prompts/threshold ดู macro F1, coverage และ hazardous recall แล้วตรึงค่าก่อนทดสอบ test
จัดจำนวนตัวอย่างสมดุล หรือใช้ class-weight และรายงานผลแยกประเภท เพื่อไม่ให้ class ใหญ่กลบ class เล็ก
ห้ามรายงานผล test เป็น validation และห้ามอ้าง fine-tuning จนกว่าจะรันฝึกจริง

## วิธีรันประเมิน
เติม manifest ตาม data/manifest_template.csv แล้วรัน
`python scripts/evaluate.py data/manifest.csv --split test --output docs/evaluation.json`
สคริปต์ตรวจไฟล์ซ้ำข้าม split และ object_id ซ้ำข้าม split ก่อนรัน
รายงาน accuracy, precision/recall/F1, confusion matrix, coverage, median/p95 latency และทุก prediction
Unknown ที่เกิดจากการงดตอบกับภาพเป้าหมายจะนับว่าทำนายผิดในการคำนวณ accuracy
