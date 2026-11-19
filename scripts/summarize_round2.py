"""Audit and summarize the second evaluation without overwriting the first."""
from pathlib import Path
import csv,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
E=json.loads((ROOT/'docs/evaluation_round2.json').read_text(encoding='utf-8'))
UI=json.loads((ROOT/'docs/browser_round2.json').read_text(encoding='utf-8'))
old=list(csv.DictReader((ROOT/'data/sample_manifest.csv').open(encoding='utf-8-sig')))
new=list(csv.DictReader((ROOT/'data/round2_manifest.csv').open(encoding='utf-8-sig')))
old_hash={hashlib.sha256((ROOT/'data'/r['path']).read_bytes()).hexdigest() for r in old}
new_hash={hashlib.sha256((ROOT/'data'/r['path']).read_bytes()).hexdigest() for r in new}
assert len(new)==50 and len(new_hash)==50 and not old_hash&new_hash
assert UI['status']=='pass' and UI['n']==50 and UI['csv_events']==50
assert len(UI['rows'])==50 and all(a['prediction']==b['category'] for a,b in zip(UI['rows'],E['results']))
fields=['path','label','category','candidate','confidence','status','elapsed_ms','correct']
with (ROOT/'docs/round2_predictions.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for r in E['results']:w.writerow({k:(r['category']==r['label'] if k=='correct' else r[k]) for k in fields})
audit={'n':50,'unique_images':50,'original_image_hash_overlap':0,'per_class':E['class_counts'],
 'correct':sum(r['label']==r['category'] for r in E['results']),'accuracy':E['accuracy'],
 'macro_f1':E['classification_report']['macro avg']['f1-score'],'coverage':E['coverage'],
 'browser_uploads':50,'browser_engine_matches':50,'csv_events':50,'javascript_errors':UI['page_errors'],
 'model_revision':json.loads((ROOT/'models/model_metadata.json').read_text())['revision'],
 'categories_sha256':hashlib.sha256((ROOT/'config/categories.json').read_bytes()).hexdigest(),
 'settings_sha256':hashlib.sha256((ROOT/'config/settings.json').read_bytes()).hexdigest(),
 'manifest_sha256':hashlib.sha256((ROOT/'data/round2_manifest.csv').read_bytes()).hexdigest(),
 'threshold':E['settings']['threshold'],'margin':E['settings']['margin'],
 'scope':'New diagnostic images from the same source; original prompts/thresholds unchanged. No independent field or user validation.'}
(ROOT/'docs/round2_validation.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
lines=['# ผลทดสอบภาพชุดเพิ่มเติม 50 ภาพ','',
 'ทดสอบด้วย CLIP จริง โดยคง prompts และเกณฑ์ 0.65 / 0.15 เดิม ภาพใหม่ไม่ซ้ำ SHA-256 กับชุดแรก กลุ่มละ 10 ภาพ จากแหล่งข้อมูลเดิม',
 '',f'- ตรงกับป้ายกำกับ {audit["correct"]}/50 ภาพ ({E["accuracy"]:.0%})',f'- Macro F1 {audit["macro_f1"]:.3f}; coverage {E["coverage"]:.0%}',
 '- อัปโหลดและสแกนผ่านหน้าเว็บ local ครบ 50 ภาพ ผลประเภทตรงกับ engine ทั้ง 50 ภาพ',
 '- ฐานข้อมูล QA มี 50 ภาพไม่ซ้ำ เป็นข้อมูลทดสอบทั้งหมด และ CSV มี 50 รายการ',
 '- กล้องจริงและการทดลองกับผู้ใช้ยังไม่ได้ยืนยัน ไม่ได้ fine-tune น้ำหนักโมเดล','',
 '| กลุ่ม | ตรง | Precision | Recall | F1 |','|---|---:|---:|---:|---:|']
for i,label in enumerate(E['label_order']):
 r=E['classification_report'][label];lines.append(f'| {label} | {E["confusion_matrix"][i][i]}/10 | {r["precision"]:.3f} | {r["recall"]:.3f} | {r["f1-score"]:.3f} |')
lines+=['','## สิ่งที่พบ','',
 'พลาสติกตรง 3/10 ภาพ สับสนเป็นแก้ว 3 ภาพ และตอบ Unknown 4 ภาพ กระดาษตอบ Unknown 1 ภาพ จึงควรเก็บข้อมูล Plastic/Glass เพิ่มและใช้ validation แยกสำหรับปรับโมเดล ไม่แก้ prompts โดยใช้ชุดทดสอบนี้แล้วนับเป็นผล test ใหม่',
 '', 'Hazardous ใช้เฉพาะแบตเตอรี่ ส่วน Unknown ใช้ biological บางภาพเป็นสินค้า/อาหารหรือมีลายน้ำ ผลนี้ไม่รับรองความแม่นยำในสถานที่จริง และไม่ทราบข้อมูลซ้ำกับ CLIP pretraining',
 '', 'รอบแรก 44/50 (88%) และรอบเพิ่มเติม 42/50 (84%) เป็นคนละภาพจากแหล่งเดียวกัน ไม่ใช่ผลก่อน/หลังการฝึกโมเดล',
 '', '## หลักฐาน','',
 '- data/round2_manifest.csv และ round2_provenance.json: รายการภาพ แหล่งที่มา SHA-256 และวิธีสุ่ม',
 '- docs/evaluation_round2.json และ round2_predictions.csv: คะแนนและผลรายภาพ',
 '- docs/browser_round2.json และ round2_ui_export.csv: ผล workflow และการส่งออกจากหน้าเว็บ',
 '- docs/cloud_round2.json: ผลทดสอบออนไลน์ชุดเดียวกัน หากมีไฟล์สถานะ pass แล้ว',
 '- assets/proposal_color/: ภาพตัวอย่างสีทั้ง 50 ภาพพร้อมชื่อไฟล์และผล',
 '- docs/Project_Proposal.docx และ PDF: ข้อเสนอฉบับปรับปรุงหลังผลทดสอบนี้']
(ROOT/'docs/Round2_Test_Report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps(audit,ensure_ascii=False))
