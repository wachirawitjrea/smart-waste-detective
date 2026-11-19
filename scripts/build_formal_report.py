"""Build the monochrome report with the Codex bundled Python runtime.

Run once, render to PDF, then pass --page-map <rendered.pdf> and render again
to populate the contents and figure/table lists with verified page numbers.
"""
import argparse
import re
from pathlib import Path
from docx import Document
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.section import WD_SECTION_START
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/report_bw'
parser = argparse.ArgumentParser()
parser.add_argument('--page-map', type=Path)
parser.add_argument('--proposal', action='store_true', help='Build the revised proposal with the new 50-image results')
args = parser.parse_args()
if args.proposal:
    from proposal_content import BLOCKS, ABSTRACT, PREFACE
else:
    from report_content import BLOCKS, ABSTRACT, PREFACE

def norm(s): return re.sub(r'\s+', '', s)
pages = {}
if args.page_map:
    from pypdf import PdfReader
    reader = PdfReader(args.page_map)
    def walk(nodes):
        for item in nodes:
            if isinstance(item, list): walk(item)
            else: pages[norm(item.title)] = reader.get_destination_page_number(item) + 1
    walk(reader.outline)
first_body_heading=next(b['text'] for b in BLOCKS if b['kind']=='h1')
start_page = pages.get(norm(first_body_heading), 1)
def page_of(title):
    value = pages.get(norm(title))
    return str(value - start_page + 1) if value else '…'

doc = Document()
sec = doc.sections[0]
sec.page_width = Cm(21); sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.5); sec.bottom_margin = Cm(2.5)
sec.left_margin = Cm(3.5); sec.right_margin = Cm(2.5)
sec.header_distance = Cm(1.2); sec.footer_distance = Cm(1.2)

for style in doc.styles:
    if style.type == 1:
        style.font.name = 'Angsana New'
        style.font.color.rgb = RGBColor(0,0,0)
        props = style.element.get_or_add_rPr()
        fonts = props.find(qn('w:rFonts'))
        if fonts is None: fonts = OxmlElement('w:rFonts'); props.append(fonts)
        for key in ['ascii','hAnsi','eastAsia','cs']: fonts.set(qn('w:'+key),'Angsana New')
        for border in list(style.element.iter(qn('w:pBdr'))): border.getparent().remove(border)

normal = doc.styles['Normal']
normal.font.size = Pt(16)
normal.paragraph_format.line_spacing = 1.15
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.widow_control = True
normal.paragraph_format.first_line_indent = Cm(1.25)
for name, size in [('Title',24),('Heading 1',20),('Heading 2',18),('Heading 3',14)]:
    style = doc.styles[name]; style.font.size = Pt(size); style.font.bold = name != 'Heading 3'
    style.paragraph_format.first_line_indent = Cm(0)
    style.paragraph_format.space_before = Pt(12 if name == 'Heading 2' else 6)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.keep_with_next = True

def plain(text='', center=False, size=None, bold=False):
    p = doc.add_paragraph(text)
    p.paragraph_format.first_line_indent = Cm(0)
    if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for r in p.runs:
        if size: r.font.size = Pt(size)
        r.bold = bold
    return p

def body(text):
    p = doc.add_paragraph(text)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p

def heading(text, level=1):
    p = doc.add_paragraph(text, style='Heading '+str(level))
    if level == 1: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p

def section_numbering(section, fmt):
    section.footer.is_linked_to_previous = False
    section.header.is_linked_to_previous = False
    num = OxmlElement('w:pgNumType'); num.set(qn('w:fmt'),fmt); num.set(qn('w:start'),'1')
    section._sectPr.append(num)
    footer = section.footer.paragraphs[0]; footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.first_line_indent = Cm(0)
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'),'PAGE')
    footer._p.append(field)

def index_line(title, number, indent=0):
    p = plain(title.replace('\n',' '))
    p.paragraph_format.left_indent = Cm(indent)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.tab_stops.add_tab_stop(Cm(15-indent),WD_TAB_ALIGNMENT.RIGHT,WD_TAB_LEADER.DOTS)
    p.add_run('\t'+number)

# Plain academic cover with exactly three unnamed members.
plain('ข้อเสนอโครงการฉบับปรับปรุง' if args.proposal else 'รายงานโครงการ', True, 24, True).paragraph_format.space_before = Pt(20)
title = doc.add_paragraph('ระบบ AI ตรวจจับและแยกประเภทขยะอัจฉริยะ', style='Title')
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
plain('Smart Waste Detective for Recycling Center', True, 20, True)
plain('')
plain('จัดทำโดย', True, 18, True)
for i in range(1,4):
    p = plain(f'{i}. ชื่อและนามสกุล ______________________________',False,16)
    p.paragraph_format.left_indent = Cm(1)
    p = plain('รหัสนักศึกษา ______________________________',False,16)
    p.paragraph_format.left_indent = Cm(1.6)
plain('')
plain('เสนอ', True, 18, True)
plain('อาจารย์ __________________________________', True)
plain('')
plain('เอกสารนี้เป็นส่วนหนึ่งของรายวิชา',True)
plain('IT232 Artificial Intelligence for Information Technology',True)
plain('สาขาวิชาเทคโนโลยีสารสนเทศ',True)
plain('มหาวิทยาลัยกรุงเทพ',True)
plain('ภาคการศึกษา __________  ปีการศึกษา __________',True)

front = doc.add_section(WD_SECTION_START.NEW_PAGE)
section_numbering(front,'lowerRoman')
heading('บทสรุปข้อเสนอโครงการ' if args.proposal else 'บทคัดย่อ')
for text in ABSTRACT: body(text)
plain('คำสำคัญ  การคัดแยกขยะ  ปัญญาประดิษฐ์  CLIP  Streamlit',size=16)
doc.add_page_break(); heading('คำนำ')
for text in PREFACE: body(text)
p=plain('คณะผู้จัดทำ'); p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
doc.add_page_break(); heading('สารบัญ')
for b in BLOCKS:
    if b['kind'] in ('h1','h2'):
        index_line(b['text'],page_of(b['text']),0 if b['kind']=='h1' else .65)
doc.add_page_break(); heading('สารบัญภาพ')
for b in BLOCKS:
    if b['kind']=='figure': index_line(b['title'],page_of(b['title']))
doc.add_page_break(); heading('สารบัญตาราง')
for b in BLOCKS:
    if b['kind']=='table': index_line(b['title'],page_of(b['title']))

main=doc.add_section(WD_SECTION_START.NEW_PAGE)
section_numbering(main,'decimal')

def table(b):
    caption = doc.add_paragraph(b['title'],style='Heading 3')
    caption.paragraph_format.keep_with_next=True
    count=len(b['headers'])
    widths=b.get('widths') or ([3.6,10.9] if count==2 else [14.5/count]*count)
    # Contents use a 15 cm text block. Normalize supplied widths consistently.
    widths=[w/sum(widths)*15 for w in widths]
    t=doc.add_table(rows=1,cols=count); t.autofit=False; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for col,w in zip(t.columns,widths): col.width=Cm(w)
    for i,txt in enumerate(b['headers']): t.rows[0].cells[i].text=str(txt)
    for values in b['rows']:
        row=t.add_row()
        for i,txt in enumerate(values): row.cells[i].text=str(txt)
    for ri,row in enumerate(t.rows):
        pr=row._tr.get_or_add_trPr(); no_split=OxmlElement('w:cantSplit');pr.append(no_split)
        if ri==0: pr.append(OxmlElement('w:tblHeader'))
        for ci,cell in enumerate(row.cells):
            cell.width=Cm(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            props=cell._tc.get_or_add_tcPr()
            shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEEEEE' if ri==0 else 'FFFFFF');props.append(shade)
            borders=OxmlElement('w:tcBorders')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single');el.set(qn('w:sz'),'4');el.set(qn('w:color'),'D9D9D9');borders.append(el)
            props.append(borders)
            margins=OxmlElement('w:tcMar')
            for edge in ['top','left','bottom','right']:
                el=OxmlElement('w:'+edge);el.set(qn('w:w'),'85');el.set(qn('w:type'),'dxa');margins.append(el)
            props.append(margins)
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent=Cm(0)
                p.paragraph_format.line_spacing=1.0
                p.paragraph_format.space_after=Pt(2)
                p.paragraph_format.keep_with_next=(len(t.rows)<=8 and ri<len(t.rows)-1)
                short=len(p.text)<18 and count>2
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER if short else WD_ALIGN_PARAGRAPH.LEFT
                for run in p.runs: run.font.size=Pt(14);run.bold=ri==0
    spacer=plain('');spacer.paragraph_format.space_after=Pt(0);spacer.paragraph_format.line_spacing=.2

first=True
for b in BLOCKS:
    kind=b['kind']
    if kind=='h1':
        p=heading(b['text'])
        if not first: p.paragraph_format.page_break_before=True
        first=False
    elif kind=='h2': heading(b['text'],2)
    elif kind=='p': body(b['text'])
    elif kind=='table': table(b)
    elif kind=='code':
        p=plain(b['text']);p.paragraph_format.line_spacing=1.0
        for r in p.runs: r.font.name='Consolas';r.font.size=Pt(9)
    elif kind=='figure':
        p=doc.add_paragraph();p.paragraph_format.first_line_indent=Cm(0)
        p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
        asset_dir=ROOT/'assets/proposal_color' if b['name'].startswith('round2_color_') else ASSETS
        p.add_run().add_picture(str(asset_dir/b['name']),width=Cm(b['width']))
        cap=doc.add_paragraph(b['title'],style='Heading 3');cap.alignment=WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.keep_with_next=False

doc.core_properties.title=('ข้อเสนอโครงการ' if args.proposal else 'รายงานโครงการ')+'ระบบ AI ตรวจจับและแยกประเภทขยะอัจฉริยะ'
doc.core_properties.author='คณะผู้จัดทำ'
doc.core_properties.subject='IT232 Artificial Intelligence for Information Technology'
doc.core_properties.keywords='Smart Waste Detective, IT232, รายงานโครงการ'
doc.core_properties.comments=''
target=ROOT/('docs/Project_Proposal.docx' if args.proposal else 'docs/Project_Report.docx')
doc.save(target)
print(target)
print('Blocks:',len(BLOCKS),'page-map entries:',len(pages))
