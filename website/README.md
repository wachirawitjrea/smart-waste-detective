# Waste Detective — Cloudflare

เว็บภาษาไทยสำหรับอัปโหลด/ถ่ายภาพขยะ จำแนก Plastic, Paper, Glass, Hazardous และ Unknown พร้อมคำแนะนำ Dashboard ประวัติในอุปกรณ์ และส่งออก CSV

## โครงสร้าง

โฟลเดอร์นี้มีเฉพาะโค้ดเว็บ การตั้งค่า dependencies และชุดตรวจตรรกะเว็บ ไม่มี Proposal รายงาน สไลด์ ชุดภาพทดสอบ ข้อมูลผู้ใช้ หรือโมเดล PyTorch

```text
package.json / package-lock.json   dependencies และคำสั่ง build
wrangler.jsonc                    Cloudflare Worker waste-detective
cloudflare/index.html             หน้าจอหลัก
cloudflare/src/                   UI, AI Web Worker, history และ CSV
cloudflare/public/config.json     prompts, vectors และรุ่นโมเดลที่ pin ไว้
cloudflare/public/_headers        headers สำหรับ static assets
cloudflare/tests/                 ทดสอบการตัดสินผลและ CSV
```

## เริ่มใช้งาน

ใช้ Node.js 24 และ npm

```sh
npm ci
npm test
npm run dev
```

## Deploy บน Cloudflare เท่านั้น

```sh
npx wrangler login
npm run deploy:cloudflare
```

`wrangler.jsonc` ตั้งชื่อ Worker และ account ID ของเจ้าของโปรเจกต์ไว้แล้ว การ deploy จะ build ด้วย Vite โดยอัตโนมัติ หากนำไปใช้ในบัญชีอื่นให้แก้ account ID ก่อน

สำหรับ Cloudflare Workers Builds ให้ตั้ง Root directory เป็นราก repository และ Deploy command เป็น `npx wrangler deploy` ไม่จำเป็นต้องสั่ง build แยก เพราะ Wrangler เรียก custom build ให้แล้ว

## การประมวลผลและโควตา

- Cloudflare ให้บริการ static assets โดยตั้ง `run_worker_first: false` ไม่มี API สำหรับประมวลผลภาพ ไม่มีการเรียก Vercel หรือ Workers AI
- CLIP ViT-B/32 รุ่น ONNX q8 ทำงานใน Web Worker ของเบราว์เซอร์ผ่าน Transformers.js ภาพไม่ถูกส่งไปประมวลผลบนเซิร์ฟเวอร์
- ครั้งแรกดาวน์โหลดโมเดลภาพประมาณ 90 MB จาก Hugging Face revision ที่ pin ไว้ เบราว์เซอร์อาจแคชไว้ ความเร็วและหน่วยความจำขึ้นกับอุปกรณ์
- ใช้เวกเตอร์ข้อความจาก prompt ensemble เดิม เกณฑ์คะแนน 0.65 และส่วนต่าง 0.15 ไม่มีการฝึกน้ำหนักใหม่
- ผล q8 อาจต่างจาก PyTorch เดิม ห้ามถือว่าเป็นผลเดียวกันทุกภาพ การตรวจภาพชุดเดิมเพิ่มเติม 50 ภาพใน Chrome ได้ 42/50 (84%) แต่ตรงกับประเภทจาก PyTorch 46/50 ภาพ ยังไม่ได้ประเมินขยะจริงในมหาวิทยาลัย
- ประวัติเก็บใน localStorage เฉพาะเบราว์เซอร์ ไม่เก็บภาพ เก็บล่าสุดไม่เกิน 500 รายการ ไม่รวมข้อมูลระหว่างอุปกรณ์ ควรส่งออก CSV ก่อนล้างข้อมูลเว็บไซต์
- การตรวจกล้องใช้กล้องจำลองใน Chrome ยังต้องทดสอบกับกล้องมือถือจริง

แหล่งอ้างอิง: [Cloudflare Static Assets](https://developers.cloudflare.com/workers/static-assets/), [Transformers.js](https://huggingface.co/docs/transformers.js/v3.8.1/index), [ONNX CLIP model](https://huggingface.co/Xenova/clip-vit-base-patch32), [OpenAI CLIP](https://github.com/openai/CLIP)
