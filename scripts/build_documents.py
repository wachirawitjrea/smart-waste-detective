"""Legacy proposal builder. Default execution delegates to the current report builder.

Pass --legacy only to reproduce the historical four-member draft.
"""
from pathlib import Path
import sys, runpy
if '--legacy' not in sys.argv:
    sys.argv=[str(Path(__file__).with_name('build_formal_report.py')),'--proposal']
    runpy.run_path(sys.argv[0],run_name='__main__')
    raise SystemExit(0)
import json, xml.etree.ElementTree as ET
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'docs'
evaluation=json.loads((OUT/'evaluation.json').read_text(encoding='utf-8'))
robust=json.loads((OUT/'robustness.json').read_text(encoding='utf-8'))
tests=ET.parse(OUT/'pytest_results.xml').getroot().findall('.//testcase')
passed=sum(not any(t.find(tag) is not None for tag in ['failure','error','skipped']) for t in tests)
doc=Document(); section=doc.sections[0]
section.page_width=Inches(8.27); section.page_height=Inches(11.69)
section.top_margin=Inches(.7); section.bottom_margin=Inches(.65)
section.left_margin=section.right_margin=Inches(.8)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Header','Footer']:
    st=doc.styles[name]; st.font.name='Leelawadee UI'; st.font.color.rgb=RGBColor(0,0,0)
    st._element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Leelawadee UI')
    st._element.get_or_add_rPr().rFonts.set(qn('w:cs'),'Leelawadee UI')
doc.styles['Normal'].font.size=Pt(11)
doc.styles['Normal'].paragraph_format.line_spacing=1.15
doc.styles['Normal'].paragraph_format.space_after=Pt(7)
doc.styles['Title'].font.size=Pt(27)
for style in doc.styles:
    for border in list(style.element.iter(qn('w:pBdr'))):
        border.getparent().remove(border)
doc.styles['Heading 1'].font.size=Pt(17)
doc.styles['Heading 2'].font.size=Pt(13)
for n in ['Heading 1','Heading 2']:
    doc.styles[n].paragraph_format.space_before=Pt(12)
    doc.styles[n].paragraph_format.space_after=Pt(7)
header=section.header.paragraphs[0]
header.text='IT232    Smart Waste Detective for Recycling Center'
header.runs[0].font.size=Pt(8)
footer=section.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
footer.add_run('หน้า ')
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)

def p(text): return doc.add_paragraph(text)
def h(text): return doc.add_heading(text,level=1)
def sub(text): return doc.add_heading(text,level=2)
def page(): doc.add_page_break()
def table(headers,rows,widths=None):
    t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
    for i,x in enumerate(headers):t.rows[0].cells[i].text=str(x)
    for row in rows:
        cells=t.add_row().cells
        for i,x in enumerate(row): cells[i].text=str(x)
    if widths:
        for row in t.rows:
            for cell,width in zip(row.cells,widths):cell.width=Inches(width)
    for ri,row in enumerate(t.rows):
        for cell in row.cells:
            props=cell._tc.get_or_add_tcPr()
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'33483E' if ri==0 else ('F2F4F3' if ri%2==0 else 'FFFFFF'));props.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge); e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
            props.append(borders)
            margins=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');margins.append(e)
            props.append(margins)
            for para in cell.paragraphs:
                para.paragraph_format.space_after=Pt(3);para.paragraph_format.line_spacing=1.08
                for run in para.runs:
                    run.font.size=Pt(9.5)
                    if ri==0:run.font.bold=True;run.font.color.rgb=RGBColor(255,255,255)
        if ri==0:
            repeat=OxmlElement('w:tblHeader');row._tr.get_or_add_trPr().append(repeat)
    p('')
    return t

# 1 Cover
p('PROJECT PROPOSAL')
doc.add_paragraph('ระบบ AI ตรวจจับและแยกประเภท\nขยะอัจฉริยะ',style='Title')
doc.add_paragraph('Smart Waste Detective\nfor Recycling Center',style='Subtitle')
p('รายวิชา IT232 Artificial Intelligence for Information Technology')
p('มหาวิทยาลัยกรุงเทพ  Bangkok University')
p('ระยะเวลาโครงการ 6 สัปดาห์    คะแนนรวม 30 คะแนน')
doc.add_picture(str(ROOT/'assets/screenshots/home.png'),width=Inches(5.35))
p('ภาพหน้าจอจากเว็บที่พัฒนาจริง ข้อมูลเริ่มต้นยังไม่มีรายการวิเคราะห์')
sub('สมาชิกกลุ่ม')
for i in range(1,5):p(f'{i}. ชื่อและนามสกุล ____________________  รหัสนักศึกษา ____________________')
p('ฉบับต้นแบบเพื่อการศึกษา 15 พฤศจิกายน 2569')

# 2 Contents and background
page();h('สารบัญ')
contents=[('1 หน้าปก',1),('2 บทนำและความเป็นมา',2),('3 ปัญหาที่ต้องการแก้ไข',3),('4 วัตถุประสงค์ของโครงการ',3),('5 กลุ่มเป้าหมายและประโยชน์',3),('6 แนวคิดของระบบ',3),('7 ขอบเขตของระบบ',4),('8 เทคโนโลยีที่ใช้',4),('9 การจัดเตรียมข้อมูลและปรับแต่ง AI',5),('10 การออกแบบ Workflow',6),('11 System Architecture',7),('12 แผนการพัฒนา 6 สัปดาห์',8),('13 แผนการทดสอบและผลเบื้องต้น',8),('14 ผลที่คาดว่าจะได้รับ',9),('15 ข้อจำกัดและแนวทางพัฒนา',10),('16 เอกสารอ้างอิง',10)]
for title,n in contents:
    para=p(f'{title}    {n}');para.paragraph_format.space_after=Pt(3)
h('2 บทนำและความเป็นมา')
p('พวกเราเลือกปัญหาการคัดแยกขยะ เพราะผู้ใช้ต้องตัดสินใจจากรูปลักษณ์ของสิ่งของและข้อมูลบนฉลาก บางครั้งขวดใสดูคล้ายกันแต่ทำจากวัสดุต่างกัน หรือไม่แน่ใจว่าควรแยกแบตเตอรี่อย่างไร การค้นหาคำแนะนำทีละชิ้นยังไม่สะดวก และข้อมูลว่าผู้ใช้ลองวิเคราะห์อะไรบ้างมักไม่ได้เก็บเป็นระบบ')
p('โครงการนี้จึงนำ Computer Vision มาช่วยเสนอประเภทจากภาพ แล้วแสดงคำแนะนำที่จัดเตรียมไว้ให้ตรวจสอบต่อ ผู้ใช้ถ่ายภาพหรืออัปโหลดได้ในเว็บเดียว ขณะที่ผู้ดูแลดูประวัติและสถิติการวิเคราะห์ได้ เป้าหมายในระยะแรกคือสร้างต้นแบบที่สาธิตได้และตรวจผลย้อนหลังได้ โดยยังไม่ใช้ AI แทนเจ้าหน้าที่ในการตัดสินใจด้านความปลอดภัย')

# 3 Problem, objectives, audience, concept
page();h('3 ปัญหาที่ต้องการแก้ไข')
p('ผู้ใช้บางคนยังไม่แน่ใจว่าขยะเข้ากลุ่มพลาสติก กระดาษ แก้ว หรืออันตราย เมื่อคัดแยกผิด วัสดุที่ควรแยกเก็บอาจปะปนกับของเปื้อนหรือสิ่งที่ต้องรับเฉพาะ ป้ายหน้าถังช่วยได้แต่ไม่สามารถอธิบายตัวอย่างทุกชนิด ผู้ใช้จึงยังต้องอ่านฉลากหรือสอบถามเจ้าหน้าที่เพิ่มเติม')
p('ระบบเดิมที่อาศัยความจำและการค้นหาเองยังไม่เชื่อมกับประวัติการใช้งาน โครงการนี้จึงแก้ทั้งขั้นตอนให้คำแนะนำและการบันทึกข้อมูล โดยไม่กล่าวอ้างว่าจำนวนการวิเคราะห์เท่ากับจำนวนขยะที่รีไซเคิลสำเร็จ')
h('4 วัตถุประสงค์ของโครงการ')
for text in ['พัฒนา AI ที่เปรียบเทียบภาพกับคำอธิบายขยะเฉพาะกลุ่ม และมีเส้นทาง Unknown เมื่อผลยังไม่ชัดเจน','พัฒนาเว็บที่รับภาพจากไฟล์และกล้อง แสดงผลภาษาไทยและคำแนะนำในการจัดการขยะ','บันทึกผลพร้อมรุ่นโมเดลและเกณฑ์ที่ใช้ เพื่อค้นหา ส่งออก CSV และแสดง Dashboard','ทดสอบการทำงานและวัดผลจากภาพที่มีป้ายกำกับจริง พร้อมรายงานกรณีที่โมเดลผิด']:
    p('• '+text)
h('5 กลุ่มเป้าหมายและประโยชน์')
p('กลุ่มเป้าหมายคือ นักศึกษา บุคลากร และผู้ใช้ทั่วไปที่ต้องการคำแนะนำเบื้องต้น จุดรับขยะหรือผู้จัดกิจกรรมในมหาวิทยาลัยสามารถใช้ข้อมูลการวิเคราะห์เพื่อดูว่าคนถามถึงประเภทใดบ่อย แล้วนำไปวางแผนสื่อความรู้ได้ ประโยชน์ส่วนนี้เป็นสิ่งที่คาดหวัง ยังไม่มีการทดลองกับผู้ใช้จริงเพื่อยืนยันผล')
h('6 แนวคิดของระบบ')
table(['ประเด็น','ก่อนใช้ AI','หลังใช้ต้นแบบ'],[
('การระบุประเภท','อ่านป้าย ค้นหา หรือถามเจ้าหน้าที่','รับข้อเสนอจากภาพ พร้อมคะแนนและ Unknown'),
('คำแนะนำ','ผู้ใช้หาเองตามชนิดสิ่งของ','แสดงแนวทางตามกลุ่มและให้ตรวจจุดรับจริง'),
('การเก็บข้อมูล','อาจไม่มีประวัติการค้นหา','เก็บผลวิเคราะห์และดู Dashboard จาก SQLite')],[1,2.7,2.9])
p('AI มีบทบาทในขั้นตอนจำแนกภาพ ส่วนคำแนะนำเป็นข้อความที่จัดเตรียมไว้ตามประเภท ไม่ใช่เหตุผลที่โมเดลเห็นจากภาพ และยังต้องตรวจฉลากกับเงื่อนไขของจุดรับในพื้นที่')

# 4 Scope and technology
page();h('7 ขอบเขตของระบบ')
p('ต้นแบบรองรับภาพ JPG และ PNG ไม่เกิน 10 MB และไม่เกิน 20 ล้านพิกเซล รับจากไฟล์หรือ Streamlit Camera Input แล้วจำแนกทั้งภาพเป็น Plastic, Paper, Glass, Hazardous หรือ Unknown ครั้งละหนึ่งประเภท ผู้ใช้เห็นภาพเดิม คะแนนอันดับหนึ่ง คำแนะนำ และเวลาที่ใช้ประมวลผล')
p('หน้า Home แสดงภาพรวม หน้า Dashboard แสดงจำนวนการวิเคราะห์ สัดส่วน กราฟแท่งและแนวโน้มรายวัน หน้า History ค้นหาด้วยรหัสภาพหรือเวลา กรองประเภท ส่งออก CSV และล้างเฉพาะข้อมูลทดสอบหลังยืนยันได้ รายละเอียดโมเดลและข้อจำกัดอ่านได้ในหน้าผลวิเคราะห์ ส่วนข้อมูลโครงการจัดเก็บในเอกสารส่งงาน')
p('ระบบยังไม่รองรับการตรวจหลายวัตถุแบบแยกกรอบ การชั่งน้ำหนัก การนับชิ้นจริง การยืนยันสารเคมีภายใน การคิดมูลค่ารับซื้อ และระบบสมาชิก เว็บนี้เปิดบน localhost สำหรับสาธิต หากจะให้หลายคนใช้ผ่านอินเทอร์เน็ตต้องเพิ่มระบบสิทธิ์และกำหนดวิธีดูแลข้อมูลก่อน')
h('8 เทคโนโลยีที่ใช้')
table(['เครื่องมือ','หน้าที่ในระบบ'],[
('Python 3.11','ภาษาหลักสำหรับเว็บ ประมวลผลภาพ และสคริปต์ทดสอบ'),
('Streamlit','หน้าเว็บ Upload กล้อง ผลวิเคราะห์ และประวัติ'),
('CLIP ViT B 32 และ PyTorch','แปลงภาพและคำอธิบายเป็นเวกเตอร์เพื่อเทียบความคล้าย'),
('Hugging Face Transformers','โหลดโมเดลและ image processor จากไฟล์ในเครื่อง'),
('Pillow','ตรวจชนิดไฟล์ แก้ทิศตาม EXIF แปลง RGB และลดขนาด'),
('SQLite และ Plotly','เก็บผลจริงและสร้างกราฟแบบโต้ตอบ'),
('pytest และ Playwright','ตรวจฟังก์ชันหลักและทดสอบเส้นทางผ่านเบราว์เซอร์')],[2.15,4.45])
sub('การจัดเก็บข้อมูล')
p('ระบบประมวลผลภาพในเครื่องและไม่เก็บภาพต้นฉบับลงฐานข้อมูล เก็บรหัส SHA 256 เวลา UTC ประเภทที่สรุป ประเภทอันดับหนึ่ง คะแนน สถานะ แหล่งรับภาพ เวลา inference รุ่นโมเดล รุ่น prompts และเกณฑ์ที่ใช้ Dashboard ไม่รวมรายการที่ผู้ใช้ทำเครื่องหมายว่าทดสอบโดยปริยาย และแสดงวันตามเวลาไทย')

# 5 Data and AI
page();h('9 การจัดเตรียมข้อมูลและปรับแต่ง AI')
sub('ข้อมูลที่ใช้จริง')
p('โมเดลตั้งต้นคือ openai/clip-vit-base-patch32 การปรับแต่งรอบนี้ใช้ Prompt Engineering โดยกำหนดคำอธิบายภาษาอังกฤษกลุ่มละ 3 ข้อ เช่น ขวดพลาสติก ถุงพลาสติก และแก้วพลาสติก เก็บใน config/categories.json ยังไม่มีการ fine-tune น้ำหนักโมเดล และไม่มีผล training หรือ validation loss')
p('การประเมินเบื้องต้นใช้ชุดข้อมูลของ Suman Kunwar และ D.Waste.app ที่เผยแพร่ผ่าน Hugging Face โดย dataset card ระบุ MIT สคริปต์สุ่มแบบทำซ้ำได้ด้วย seed 232 เลือก Plastic, Paper, Glass, Battery และ Biological กลุ่มละ 10 ภาพ รวม 50 ภาพ เก็บ revision และ URL ของแต่ละภาพไว้ใน manifest พร้อมสำเนา dataset card')
p('Battery ถูกจัดเข้า Hazardous เฉพาะในขอบเขตตัวอย่างแบตเตอรี่ ส่วน Biological ใช้เป็น Unknown เพราะอยู่นอกสี่กลุ่มเป้าหมาย ป้ายกำกับสืบทอดจากแหล่งข้อมูล ยังต้องให้สมาชิกกลุ่มตรวจภาพรายชิ้น และไม่ควรสรุปว่าเป็นตัวแทนขยะอันตรายหรือภาพนอกกลุ่มทั้งหมด')
sub('วิธีปรับแต่งและการตรวจคะแนน')
p('นำเวกเตอร์ข้อความแต่ละคำอธิบายมาทำ normalize แล้วเฉลี่ยภายในกลุ่ม จากนั้น normalize อีกครั้ง ภาพผ่านตัวประมวลผลของ CLIP แล้วนำเวกเตอร์ภาพไปเทียบกับทั้งห้ากลุ่ม คำนวณ softmax โดยใช้ logit scale จากโมเดล ค่าเหล่านี้เป็นคะแนนเปรียบเทียบ ไม่ใช่ค่าความแม่นยำหรือความน่าจะเป็นที่สอบเทียบแล้ว')
p('ระบบยอมรับผลเมื่อกลุ่มอันดับหนึ่งไม่ใช่ Unknown คะแนนไม่น้อยกว่า 0.65 และต่างจากอันดับสองไม่น้อยกว่า 0.15 ค่าเริ่มต้นนี้กำหนดก่อนดูชุดตัวอย่างและยังไม่ผ่าน calibration การลองเกณฑ์อื่นในรายงานเป็นการดูความไวของผลเท่านั้น ไม่ได้นำชุด test มาปรับค่าระบบ')
sub('แผนข้อมูลและการฝึกเพิ่มเติม')
p('กลุ่มควรถ่ายภาพในพื้นที่จริงอย่างน้อยกลุ่มละ 100 ภาพ โดยขออนุญาตและไม่ติดข้อมูลส่วนบุคคล ให้สองคนตรวจป้ายกำกับ แบ่งตามวัตถุและรอบถ่ายเป็น train 60% validation 20% test 20% ก่อนแปลงภาพ ภาพขวดใบเดียวกันต้องอยู่ split เดียวกัน ตรวจ hash และภาพคล้ายกันเพื่อลดข้อมูลรั่ว')
p('หากเลือกฝึก classification head หรือ fine-tune จริง ให้ใช้ train เท่านั้นและบันทึก seed ค่าที่ฝึก loss และ checkpoint ใช้ validation เลือก prompts และเกณฑ์ แล้วตรึงค่าก่อนประเมิน test แก้ข้อมูลไม่สมดุลด้วยการเก็บเพิ่มหรือ class weight และรายงาน macro F1 กับ recall ของขยะอันตรายแยกจากค่าเฉลี่ย')

# 6 Workflow
page();h('10 การออกแบบ Workflow')
p('ผู้ใช้เพิ่มภาพจากไฟล์หรือกล้อง ระบบตรวจชนิด ขนาด และความสมบูรณ์ของภาพก่อน หากไม่ผ่านจะแจ้งให้แก้ไขโดยไม่บันทึกเป็นผล AI เมื่อผ่านแล้วจึงปรับทิศ แปลง RGB ลดขนาด และส่งเข้า CLIP')
doc.add_picture(str(OUT/'Workflow_Diagram.png'),width=Inches(5.4))
p('ภาพที่ 1 Workflow จากระบบที่พัฒนา แยกเส้นทางผลที่ผ่านเกณฑ์และ Unknown')
p('เมื่อคำนวณคะแนนแล้ว ระบบตรวจเกณฑ์และแสดงประเภทหรือ Unknown พร้อมคำแนะนำ จากนั้นบันทึกผลลง SQLite เพื่อให้ Dashboard และ History อ่านได้ หากโหลดโมเดลหรือบันทึกข้อมูลไม่สำเร็จจะแสดงข้อผิดพลาดและไม่สร้างผล AI ทดแทน')

# 7 Architecture
page();h('11 System Architecture')
p('เบราว์เซอร์ติดต่อกับ Streamlit ซึ่งเป็นศูนย์กลางรับภาพและแสดงผล AI Engine โหลด CLIP จาก models/clip ในเครื่อง การดาวน์โหลดจาก Hugging Face ทำในขั้นตอนติดตั้ง หลังจากมีโมเดลครบ การวิเคราะห์ไม่ต้องเรียก inference API ภายนอก')
doc.add_picture(str(OUT/'System_Architecture.png'),width=Inches(6.55))
p('ภาพที่ 2 ส่วนประกอบของระบบและทิศทางข้อมูล')
sub('หน้าที่ของแต่ละส่วน')
p('services/images.py ตรวจข้อมูลภาพ services/engine.py สร้างคะแนนและตัดสินผล services/storage.py จัดการ SQLite และ CSV ส่วน app.py ใช้ผลเหล่านี้ประกอบหน้าเว็บ แยกส่วนเพื่อให้ทดสอบกติกาและฐานข้อมูลได้โดยไม่ต้องโหลดโมเดลทุกครั้ง')
p('แต่ละการวิเคราะห์มี event ID ป้องกันการบันทึกซ้ำจากการรันหน้าใหม่โดยไม่ตั้งใจ ข้อมูลทดสอบมีป้ายกำกับแยกจากการใช้งานทั่วไป การทดสอบเบราว์เซอร์ใช้ฐานข้อมูล QA อีกไฟล์หนึ่งเพื่อไม่ให้ตัวเลขสาธิตปะปนในฐานข้อมูลหลัก')
p('ภาพผลวิเคราะห์แบตเตอรี่และ Dashboard จาก session ทดสอบจริงอยู่ใน assets/screenshots และสไลด์นำเสนอ ภาพเหล่านี้เป็นหลักฐานการทดสอบระบบ ไม่ได้ยืนยันความปลอดภัยหรือชนิดสารเคมีภายใน')

# 8 Plan/testing
page();h('12 แผนการพัฒนา 6 สัปดาห์')
p('ตารางนี้เป็นกรอบจัดงานสำหรับกลุ่ม ไม่ใช่บันทึกว่าผ่านไปแล้วหกสัปดาห์ ให้สมาชิกเติมผู้รับผิดชอบและปรับวันจริงตามกำหนดส่งของรายวิชา')
table(['สัปดาห์','งานหลัก','หลักฐานที่ควรได้'],[
('1','วิเคราะห์ปัญหาและขอบเขต','Proposal และ Workflow ฉบับแรก'),
('2','เก็บภาพ ตรวจสิทธิ์ และตรวจ label','Manifest และ split ที่ไม่ซ้ำวัตถุ'),
('3','ปรับ prompts หรือฝึกโมเดล','Config และผล validation ที่ตรวจซ้ำได้'),
('4','พัฒนาเว็บและฐานข้อมูล','Upload กล้อง ผลวิเคราะห์ และกราฟ'),
('5','ทดสอบระบบและกับผู้ใช้','ผล test ภาพผิด และ feedback จริง'),
('6','ปรับปรุงเอกสารและซ้อมนำเสนอ','ZIP สไลด์ บทพูด และแผนสำรอง demo')],[.65,2.75,3.2])
h('13 แผนการทดสอบและผลเบื้องต้น')
sub('Functional testing')
p('ตรวจไฟล์ JPG และ PNG ที่ถูกต้อง ไฟล์ผิดประเภท ไฟล์เสีย ไฟล์เกินขนาด ภาพเล็กและภาพเกินจำนวนพิกเซล ตรวจเกณฑ์ Unknown การบันทึกซ้ำ การกรองข้อมูลทดสอบ การส่งออก CSV และการเปิดครบทุกหน้า ชุด pytest ปัจจุบันผ่าน '+str(passed)+' รายการ ผลจริงอยู่ใน pytest_results.xml')
sub('Model evaluation และ performance')
p('ใช้ scripts/evaluate.py อ่านภาพกับ label จาก manifest ตรวจข้อมูลซ้ำข้าม split แล้วรายงาน accuracy precision recall F1 confusion matrix และเวลา inference วัดเวลาหลังโหลดโมเดลแล้ว จึงไม่รวมเวลาเริ่มโปรแกรม โหลดโมเดล หรือรอผู้ใช้')
sub('Browser และ user testing')
p('ทดสอบอัปโหลดกระดาษและแบตเตอรี่จริงในเบราว์เซอร์ ตรวจผลใหม่ กราฟ ประวัติและ CSV ในฐานข้อมูล QA แยกจากข้อมูลหลัก ตรวจการแสดงผลที่ความกว้าง 390 px แล้ว กล้องตรวจได้เพียงการแสดง widget ยังไม่ได้ถ่ายจากอุปกรณ์จริง และยังไม่มีผู้ทดลองใช้งานหรือผลตอบรับที่นำมาอ้างได้')
p('แผนทดสอบผู้ใช้คือให้ผู้สมัครใจลองงานเดียวกันทั้งแบบอ่านป้ายและแบบใช้เว็บ บันทึกเวลาที่ใช้ ความถูกต้องของการเลือกจุดรับ และความคิดเห็นโดยไม่เก็บชื่อ เปรียบเทียบผลเมื่อมีข้อมูลจริงเท่านั้น')

# 9 Results/expected
page();sub('ผลประเมินภาพตัวอย่าง 50 ภาพ')
p(f'ระบบจำแนกถูกต้อง 44 จาก 50 ภาพ หรือ {evaluation["accuracy"]:.0%} ค่า macro F1 เท่ากับ {evaluation["classification_report"]["macro avg"]["f1-score"]:.3f} และ coverage เท่ากับ {evaluation["coverage"]:.0%} ซึ่งหมายถึงสัดส่วนที่ระบบยอมรับเป็นหนึ่งในสี่กลุ่มเป้าหมาย การงดตอบภาพเป้าหมายนับว่าทำนายผิดในการคำนวณ accuracy')
table(['ประเภท','Precision','Recall','F1','จำนวน'],[(k,f'{evaluation["classification_report"][k]["precision"]:.2f}',f'{evaluation["classification_report"][k]["recall"]:.2f}',f'{evaluation["classification_report"][k]["f1-score"]:.2f}',10) for k in evaluation['label_order']],[1.75,1.2,1.2,1.2,.65])
sub('Confusion matrix')
p('แถวคือ label จริง คอลัมน์คือผลที่ระบบสรุป ลำดับ P พลาสติก Pa กระดาษ G แก้ว H อันตราย U Unknown')
table(['จริง / ทาย','P','Pa','G','H','U'],[(k,*row) for k,row in zip(['P','Pa','G','H','U'],evaluation['confusion_matrix'])],[1.6,1,1,1,1,1])
p('พลาสติกถูก 5 จาก 10 ภาพ โดยผิดเป็นแก้ว 3 ภาพและ Unknown 2 ภาพ กระดาษถูก 9 จาก 10 ภาพ ส่วนแก้ว แบตเตอรี่ และ Biological ในชุดนี้ถูกกลุ่มละ 10 ภาพ ผลแบตเตอรี่ 10 ภาพยังไม่ยืนยันว่าตรวจขยะอันตรายชนิดอื่นได้')
p(f'เวลา inference บน CPU ในรอบประเมินนี้มี median {evaluation["latency_ms_median"]:.1f} ms และ p95 {evaluation["latency_ms_p95"]:.1f} ms ไม่รวมเวลาโหลดโมเดลและหน้าเว็บ ผลจากภาพเบลอที่สร้างเพื่อทดสอบได้ Unknown ส่วนภาพผสมสองวัตถุได้เพียง Glass จึงยืนยันข้อจำกัดด้านหลายวัตถุ')
h('14 ผลที่คาดว่าจะได้รับ')
p('คาดว่าผู้ใช้จะเข้าถึงแนวทางคัดแยกได้สะดวกขึ้น และกลุ่มมีข้อมูลสำหรับปรับสื่อความรู้หรือพัฒนาโมเดลต่อ สิ่งที่ยืนยันได้ในรอบนี้คือเว็บทำงานเชื่อมถึงฐานข้อมูลและมีผลทดสอบจริง ส่วนการลดเวลา ลดขยะปนเปื้อน หรือเพิ่มอัตรารีไซเคิลยังต้องวัดจากการทดลองในพื้นที่')

# 10 Limitations and refs
page();h('15 ข้อจำกัดและแนวทางพัฒนา')
p('ผล 88% มาจากชุดตัวอย่างขนาดเล็กที่เลือกจากแหล่งเดียว ยังไม่มีการตรวจ label โดยสมาชิกสองคน ไม่ทราบการซ้ำกับข้อมูล pretraining และภาพ Biological เป็นเพียงส่วนหนึ่งของ Unknown จึงไม่ใช้ค่านี้รับประกันผลในมหาวิทยาลัยหรือศูนย์รีไซเคิล')
p('ขวดพลาสติกและขวดแก้วยังสับสนกันได้ แม้คะแนนสูง ผู้ใช้ต้องตรวจวัสดุและฉลากก่อนคัดแยก ส่วน Hazardous เป็นหมวดคำอธิบายจากภาพ ไม่ได้ตรวจสารเคมี โมเดลอาจมองไม่เห็นแบตเตอรี่ที่อยู่ภายในเครื่อง หรือภาชนะอันตรายที่ไม่มีฉลากชัดเจน')
p('ขั้นต่อไปคือเก็บภาพหน้างาน ตรวจ label ให้ครบ แบ่งข้อมูลตามวัตถุ ทดลอง prompts และเกณฑ์บน validation แล้วประเมิน test ที่แยกไว้ หากผลยังไม่พอจึงพิจารณาฝึกโมเดลเพิ่มเติม ทดสอบกล้องจริงและผู้ใช้ก่อนนำไปใช้ในกิจกรรมจริง')
p('เอกสารโจทย์ระบุการนำเสนอ 10 นาที แต่ rubric มีข้อความ 5 นาที จึงจัดบทพูดฉบับ 10 นาทีและแนวตัดเหลือ 5 นาทีไว้ ให้กลุ่มซ้อมจับเวลาจริงและใช้เวลาตามที่อาจารย์ยืนยัน ชื่อและรหัสสมาชิกยังเว้นให้กรอกก่อนส่ง')
h('16 เอกสารอ้างอิง')
refs=[
('โจทย์รายวิชา IT232','AI Transformation Project AI to the Rescue เอกสาร PDF ที่ผู้ใช้แนบ ใช้อ้างอิงขอบเขต งานส่ง และเกณฑ์ 30 คะแนน'),
('CLIP model card','https://huggingface.co/openai/clip-vit-base-patch32'),
('Suman Kunwar และ D.Waste.app Dataset card ระบุ MIT','https://huggingface.co/datasets/omasteam/waste-garbage-management-dataset'),
('Streamlit Camera Input','https://docs.streamlit.io/develop/api-reference/widgets/st.camera_input'),
('Streamlit File Uploader','https://docs.streamlit.io/develop/api-reference/widgets/st.file_uploader'),
('U S EPA Common recyclables','https://www.epa.gov/recycle/how-do-i-recycle-common-recyclables'),
('U S EPA Used household batteries','https://www.epa.gov/recycle/used-household-batteries')]
for title,url in refs:
    p(title+'\n'+url)
p('แหล่งออนไลน์ตรวจวันที่ 15 พฤศจิกายน 2569 คำแนะนำทั่วไปใช้ประกอบการเรียนรู้ โดยตรวจเงื่อนไขจุดรับในประเทศไทยอีกครั้งก่อนใช้งานจริง ภาพอ้างอิง Dribbble และ Behance ใช้เป็นแนวทางสีและลำดับเนื้อหา ภาพหน้าจอในเอกสารมาจากระบบที่พัฒนาจริง')
doc.core_properties.title='Smart Waste Detective Project Proposal'
doc.core_properties.author='กลุ่มนักศึกษา IT232'
doc.save(OUT/'Project_Proposal.docx')

# Evidence-based test report
lines=['# รายงานผลทดสอบ Smart Waste Detective','',
'วันที่ 15 พฤศจิกายน 2569 • Python 3.11 CPU • ดูเวอร์ชันจริงใน requirements-lock.txt','',
f'Automated functional tests: {passed}/{len(tests)} ผ่าน รายละเอียดจาก pytest_results.xml',
'ผลการประเมินโมเดลและการทดสอบฟังก์ชันเป็นคนละส่วน ไม่ใช้จำนวน unit tests แทน accuracy','',
'## Functional testing','',
'| ID | Scenario | Expected | Actual | Status | หมายเหตุ |','|---|---|---|---|---|---|']
for i,t in enumerate(tests,1):
    ok=not any(t.find(tag) is not None for tag in ['failure','error','skipped'])
    lines.append(f'| F{i:02} | {t.attrib["name"]} | Assertion ที่ระบุใน tests/test_core.py ผ่าน | '+('ผ่าน assertion' if ok else 'ดู XML')+' | '+('Pass' if ok else 'Fail')+' | Fixture แยกจากฐานข้อมูลผู้ใช้ |')
lines+=['','## Model evaluation','',
'ใช้ภาพ 50 ภาพ กลุ่มละ 10 จากชุดข้อมูลสาธารณะ seed 232 ป้ายกำกับจากผู้เผยแพร่ ไม่มีการฝึกหรือปรับ threshold จากชุดนี้',
f'Accuracy = {evaluation["accuracy"]:.1%} (44/50), macro F1 = {evaluation["classification_report"]["macro avg"]["f1-score"]:.4f}, coverage = {evaluation["coverage"]:.1%}',
'','| ID | Scenario | Expected | Actual | Status | หมายเหตุ |','|---|---|---|---|---|---|']
for i,k in enumerate(evaluation['label_order'],1):
    matching=[r for r in evaluation['results'] if r['label']==k]
    correct=sum(r['category']==k for r in matching)
    lines.append(f'| M{i:02} | {k} | ตรง label 10/10 | {correct}/10 | '+('Pass' if correct==10 else 'Fail')+' | Pass หมายถึงชุดย่อยนี้เท่านั้น |')
lines+=['','| ประเภท | Precision | Recall | F1 | n |','|---|---:|---:|---:|---:|']
for k in evaluation['label_order']:
    r=evaluation['classification_report'][k]
    lines.append(f'| {k} | {r["precision"]:.3f} | {r["recall"]:.3f} | {r["f1-score"]:.3f} | 10 |')
lines+=['','Confusion matrix แถวจริง คอลัมน์ทาย ลำดับ Plastic Paper Glass Hazardous Unknown','',
'```text',*[' '.join(f'{n:2}' for n in r) for r in evaluation['confusion_matrix']],'```','',
'ข้อผิดพลาด 6 ภาพ:']
for r in evaluation['results']:
    if r['label']!=r['category']:lines.append(f'- {r["path"]}: label={r["label"]}, predicted={r["category"]}, top score={r["confidence"]:.4f}')
lines+=['','## Diagnostic stress cases','',
'ภาพดัดแปลงเพื่อวินิจฉัย ไม่ใช่ตัวอย่างอิสระเพิ่มจากชุดทดสอบ และไม่คิดรวมใน accuracy 50 ภาพ','',
'| ID | Scenario | Expected | Actual | Status | หมายเหตุ |','|---|---|---|---|---|---|']
for i,r in enumerate(robust['cases'],1):
    multi=r['case']=='multiple_objects'
    expected='แสดงประเภทเดียวพร้อมข้อจำกัด' if multi else 'Unknown'
    status='Observed limitation' if multi else ('Pass' if r['category']=='Unknown' else 'Fail')
    lines.append(f'| R{i:02} | {r["case"]} | {expected} | {r["category"]}, top score {r["confidence"]:.3f} | {status} | ไม่ยืนยันผลกับภาพทุกแบบ |')
lines+=['','## Threshold sensitivity','',
'Rescore จากคะแนนเดิมบนชุด diagnostic test เท่านั้น ไม่ได้ใช้เลือกค่าใหม่ และไม่ใช่ calibration',
'','| Threshold | Margin | Accuracy | Coverage |','|---:|---:|---:|---:|']
for r in robust['sensitivity']:lines.append(f'| {r["threshold"]:.2f} | {r["margin"]:.2f} | {r["accuracy"]:.0%} | {r["coverage"]:.0%} |')
lines+=['','## Performance testing','',f'เวลา CPU inference median {evaluation["latency_ms_median"]:.2f} ms, p95 {evaluation["latency_ms_p95"]:.2f} ms จาก 50 ภาพ รวม preprocessing แต่ไม่รวม model load, UI และฐานข้อมูล',
'ค่าขึ้นกับเครื่องและภาระงาน ไม่ใช่คำรับประกัน latency เมื่อนำไป deploy','',
'## Browser testing','',
'ดู browser_e2e.json และ qa_export.csv เป็นหลักฐาน อัปโหลดกระดาษกับแบตเตอรี่จริง เปิด Dashboard และกรอง CSV ในฐานข้อมูล QA แยก ภาพหน้าจอ result และ dashboard_data มาจากรอบทดสอบนี้ ไม่ใช่ขยะที่คัดแยกในสถานที่จริง',
'การทดสอบต้องเทียบ QA database ว่ามี 2 event เท่านั้น เพื่อป้องกันตัวทดสอบอ่านผลเก่า การเปิดรายละเอียดหรือเปลี่ยนหน้าไม่ควรเพิ่ม event',
'ความกว้าง 390 px ตรวจ page horizontal overflow แล้ว กล้องทดสอบเพียงการ render widget','',
'## ส่วนที่ยังไม่ได้ทดสอบ','',
'- การถ่ายจากกล้องอุปกรณ์จริงและการอนุญาตกล้อง',
'- User testing, feedback, การลดเวลาคัดแยก และปริมาณรีไซเคิลจริง',
'- การใช้งานหลายคน ระบบสมาชิก และ public deployment',
'- การประเมินกับขยะอันตรายทุกชนิด รวมถึงวัตถุที่ไม่เห็นแบตเตอรี่ภายใน','',
'## การทำซ้ำ','',
'```powershell',
'.venv\\Scripts\\python.exe -m pytest -q --junitxml=docs/pytest_results.xml',
'.venv\\Scripts\\python.exe scripts/evaluate.py data/sample_manifest.csv --output docs/evaluation.json',
'.venv\\Scripts\\python.exe scripts/robustness_checks.py','```','',
'แหล่งข้อมูล: data/sample_manifest.csv, data/sample_provenance.json, data/DATASET_SOURCE.md และเอกสารโมเดล https://huggingface.co/openai/clip-vit-base-patch32',
'ยังต้องตรวจ label โดยคน แบ่ง validation/test ภาพหน้างานตามวัตถุ และ calibrate ก่อนอ้างความเหมาะสมสำหรับการใช้งานจริง']
(OUT/'Test_Report.md').write_text('\n'.join(lines),encoding='utf-8')
(OUT/'Setup_Guide.md').write_text('# คู่มือติดตั้ง\n\n'+(ROOT/'README.md').read_text(encoding='utf-8'),encoding='utf-8')
print('Created Project_Proposal.docx, Test_Report.md and Setup_Guide.md')
