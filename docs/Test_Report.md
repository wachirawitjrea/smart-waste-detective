# รายงานผลทดสอบ Smart Waste Detective

เอกสารนี้เก็บผลรอบแรก 44/50 (88%) ไว้เป็นหลักฐานเดิม ผลจากภาพใหม่อีก 50 ภาพอยู่ใน [รายงานรอบเพิ่มเติม](Round2_Test_Report.md) ซึ่งได้ 42/50 (84%) และอัปเดต Proposal ตามรอบเพิ่มเติมแล้ว สถานะออนไลน์ล่าสุดดู deployment_validation.json

วันที่ 15 พฤศจิกายน 2569 • Python 3.11 CPU • ดูเวอร์ชันจริงใน requirements-lock.txt

Automated functional tests: 17/17 ผ่าน รายละเอียดจาก pytest_results.xml
ผลการประเมินโมเดลและการทดสอบฟังก์ชันเป็นคนละส่วน ไม่ใช้จำนวน unit tests แทน accuracy

## Functional testing

| ID | Scenario | Expected | Actual | Status | หมายเหตุ |
|---|---|---|---|---|---|
| F01 | test_valid_image[PNG] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F02 | test_valid_image[JPEG] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F03 | test_invalid_file[] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F04 | test_invalid_file[not an image] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F05 | test_invalid_file[\x89PNG\r\n\x1a\ncorrupt] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F06 | test_invalid_file[data3] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F07 | test_actual_type_checked | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F08 | test_tiny_image | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F09 | test_large_pixel_limit | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F10 | test_decision[scores0-Plastic] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F11 | test_decision[scores1-Unknown] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F12 | test_decision[scores2-Unknown] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F13 | test_decision[scores3-Hazardous] | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F14 | test_margin_rejects_ambiguous | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F15 | test_storage_csv_and_test_deletion | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F16 | test_csv_formula_neutralized | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |
| F17 | test_ui_navigation | Assertion ที่ระบุใน tests/test_core.py ผ่าน | ผ่าน assertion | Pass | Fixture แยกจากฐานข้อมูลผู้ใช้ |

## Model evaluation

ใช้ภาพ 50 ภาพ กลุ่มละ 10 จากชุดข้อมูลสาธารณะ seed 232 ป้ายกำกับจากผู้เผยแพร่ ไม่มีการฝึกหรือปรับ threshold จากชุดนี้
Accuracy = 88.0% (44/50), macro F1 = 0.8706, coverage = 74.0%

| ID | Scenario | Expected | Actual | Status | หมายเหตุ |
|---|---|---|---|---|---|
| M01 | Plastic | ตรง label 10/10 | 5/10 | Fail | Pass หมายถึงชุดย่อยนี้เท่านั้น |
| M02 | Paper | ตรง label 10/10 | 9/10 | Fail | Pass หมายถึงชุดย่อยนี้เท่านั้น |
| M03 | Glass | ตรง label 10/10 | 10/10 | Pass | Pass หมายถึงชุดย่อยนี้เท่านั้น |
| M04 | Hazardous | ตรง label 10/10 | 10/10 | Pass | Pass หมายถึงชุดย่อยนี้เท่านั้น |
| M05 | Unknown | ตรง label 10/10 | 10/10 | Pass | Pass หมายถึงชุดย่อยนี้เท่านั้น |

| ประเภท | Precision | Recall | F1 | n |
|---|---:|---:|---:|---:|
| Plastic | 1.000 | 0.500 | 0.667 | 10 |
| Paper | 1.000 | 0.900 | 0.947 | 10 |
| Glass | 0.769 | 1.000 | 0.870 | 10 |
| Hazardous | 1.000 | 1.000 | 1.000 | 10 |
| Unknown | 0.769 | 1.000 | 0.870 | 10 |

Confusion matrix แถวจริง คอลัมน์ทาย ลำดับ Plastic Paper Glass Hazardous Unknown

```text
 5  0  3  0  2
 0  9  0  0  1
 0  0 10  0  0
 0  0  0 10  0
 0  0  0  0 10
```

ข้อผิดพลาด 6 ภาพ:
- samples/plastic/plastic_2045.jpg: label=Plastic, predicted=Glass, top score=0.9681
- samples/plastic/plastic_2173.jpg: label=Plastic, predicted=Glass, top score=0.8853
- samples/plastic/plastic_1548.jpg: label=Plastic, predicted=Unknown, top score=0.5311
- samples/plastic/plastic_1821.jpg: label=Plastic, predicted=Glass, top score=0.7169
- samples/plastic/plastic_79.jpg: label=Plastic, predicted=Unknown, top score=0.6057
- samples/paper/paper_1568.jpg: label=Paper, predicted=Unknown, top score=0.6037

## Diagnostic stress cases

ภาพดัดแปลงเพื่อวินิจฉัย ไม่ใช่ตัวอย่างอิสระเพิ่มจากชุดทดสอบ และไม่คิดรวมใน accuracy 50 ภาพ

| ID | Scenario | Expected | Actual | Status | หมายเหตุ |
|---|---|---|---|---|---|
| R01 | blurred_plastic | Unknown | Unknown, top score 0.551 | Pass | ไม่ยืนยันผลกับภาพทุกแบบ |
| R02 | multiple_objects | แสดงประเภทเดียวพร้อมข้อจำกัด | Glass, top score 0.675 | Observed limitation | ไม่ยืนยันผลกับภาพทุกแบบ |
| R03 | no_waste_blank | Unknown | Unknown, top score 0.452 | Pass | ไม่ยืนยันผลกับภาพทุกแบบ |

## Threshold sensitivity

Rescore จากคะแนนเดิมบนชุด diagnostic test เท่านั้น ไม่ได้ใช้เลือกค่าใหม่ และไม่ใช่ calibration

| Threshold | Margin | Accuracy | Coverage |
|---:|---:|---:|---:|
| 0.50 | 0.15 | 90% | 78% |
| 0.65 | 0.15 | 88% | 74% |
| 0.80 | 0.15 | 76% | 60% |

## Performance testing

เวลา CPU inference median 52.15 ms, p95 63.06 ms จาก 50 ภาพ รวม preprocessing แต่ไม่รวม model load, UI และฐานข้อมูล
ค่าขึ้นกับเครื่องและภาระงาน ไม่ใช่คำรับประกัน latency เมื่อนำไป deploy

## Browser testing

ดู browser_e2e.json และ qa_export.csv เป็นหลักฐาน อัปโหลดกระดาษกับแบตเตอรี่จริง เปิด Dashboard และกรอง CSV ในฐานข้อมูล QA แยก ภาพหน้าจอ result และ dashboard_data มาจากรอบทดสอบนี้ ไม่ใช่ขยะที่คัดแยกในสถานที่จริง
การทดสอบต้องเทียบ QA database ว่ามี 2 event เท่านั้น เพื่อป้องกันตัวทดสอบอ่านผลเก่า การเปิดรายละเอียดหรือเปลี่ยนหน้าไม่ควรเพิ่ม event
ความกว้าง 390 px ตรวจ page horizontal overflow แล้ว กล้องทดสอบเพียงการ render widget

## ส่วนที่ยังไม่ได้ทดสอบ

- การถ่ายจากกล้องอุปกรณ์จริงและการอนุญาตกล้อง
- User testing, feedback, การลดเวลาคัดแยก และปริมาณรีไซเคิลจริง
- การใช้งานหลายคน ระบบสมาชิก และ public deployment
- การประเมินกับขยะอันตรายทุกชนิด รวมถึงวัตถุที่ไม่เห็นแบตเตอรี่ภายใน

## การทำซ้ำ

```powershell
.venv\Scripts\python.exe -m pytest -q --junitxml=docs/pytest_results.xml
.venv\Scripts\python.exe scripts/evaluate.py data/sample_manifest.csv --output docs/evaluation.json
.venv\Scripts\python.exe scripts/robustness_checks.py
```

แหล่งข้อมูล: data/sample_manifest.csv, data/sample_provenance.json, data/DATASET_SOURCE.md และเอกสารโมเดล https://huggingface.co/openai/clip-vit-base-patch32
ยังต้องตรวจ label โดยคน แบ่ง validation/test ภาพหน้างานตามวัตถุ และ calibrate ก่อนอ้างความเหมาะสมสำหรับการใช้งานจริง
