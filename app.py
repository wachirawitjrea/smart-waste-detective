from pathlib import Path
import os
import base64
import time
import uuid
import pandas as pd
import plotly.express as px
import streamlit as st
from services.engine import CATEGORIES, SETTINGS, WasteEngine
from services.images import validate_image
from services.storage import history, save, export_csv, clear_test

st.set_page_config(page_title='Waste Detective • IT232', page_icon='♻️', layout='wide')
st.markdown('''<style>
html,body,[data-testid="stApp"],button,input,[data-testid="stMarkdownContainer"],label,[data-testid="stMetricValue"] {font-family:"Leelawadee UI",sans-serif}
.block-container {max-width:1280px;padding:3rem clamp(1.1rem,3vw,3rem) 3rem}
h1,h2,h3 {letter-spacing:-.035em}
[data-testid="stSidebar"] {background:#eaf2ec;border-right:1px solid #d9e6dd}
[data-testid="stMetric"] {background:white;border:1px solid #dce8df;border-radius:18px;padding:18px}
.st-key-home_banner {background:linear-gradient(115deg,#163e30,#225944);padding:0;border-radius:22px;margin-bottom:12px}
.st-key-home_banner .st-key-start_analysis {width:100%}
.st-key-home_banner [data-testid="stButton"] button {
    position:relative;isolation:isolate;overflow:hidden;width:100%;min-height:96px;
    padding:18px 24px;border-radius:22px;border:1px solid #d7ffe7b3;
    background:linear-gradient(135deg,#caffddd9,#72e1a6c7 55%,#4abe87d9);
    color:#073b25;backdrop-filter:blur(18px) saturate(180%);-webkit-backdrop-filter:blur(18px) saturate(180%);
    box-shadow:inset 0 1px 0 #ffffffb3,inset 0 -1px 0 #207e5940,0 10px 26px #082a1d52,0 0 0 5px #a0f7bf0d;
    cursor:pointer;touch-action:manipulation;
    transition:transform 220ms cubic-bezier(.2,.8,.2,1),box-shadow 220ms ease,background 220ms ease,border-color 220ms ease;
}
.st-key-home_banner [data-testid="stButton"] button p {
    position:relative;z-index:2;font-family:"Leelawadee UI",sans-serif;font-size:clamp(21px,2.4vw,27px)!important;font-weight:700;line-height:1.4;white-space:nowrap;
}
.st-key-home_banner [data-testid="stButton"] button::before {
    content:"";position:absolute;inset:1px;border-radius:20px;pointer-events:none;
    background:linear-gradient(180deg,#ffffff4d,transparent 50%,#ffffff0d);z-index:0;
}
.st-key-home_banner [data-testid="stButton"] button::after {
    content:"";position:absolute;top:-80%;left:0;width:45%;height:260%;pointer-events:none;z-index:1;
    background:linear-gradient(90deg,transparent,#ffffff80,transparent);opacity:0;
    transform:translateX(-220%) rotate(24deg);animation:liquid-glint 5.5s ease-in-out infinite;
}
@keyframes liquid-glint {
    0%,60% {transform:translateX(-220%) rotate(24deg);opacity:0}
    67% {opacity:.85}
    85%,100% {transform:translateX(430%) rotate(24deg);opacity:0}
}
@media(hover:hover) {
    .st-key-home_banner [data-testid="stButton"] button:hover {
        color:#073b25;transform:translateY(-3px) scale(1.025);border-color:#effff4;
        background:linear-gradient(135deg,#ddffece6,#8af0b9d9 55%,#60d79cde);
        box-shadow:inset 0 1px 0 #ffffffd9,inset 0 -1px 0 #207e5940,0 15px 34px #06281b66,0 0 0 6px #a0f7bf14;
    }
}
.st-key-home_banner [data-testid="stButton"] button:active {
    transform:translateY(1px) scale(.975);color:#073b25;
    box-shadow:inset 0 2px 7px #0e59352b,0 3px 10px #082a1d40;
}
.st-key-home_banner [data-testid="stButton"] button:focus-visible {outline:3px solid #ecffdf;outline-offset:5px}
@media(prefers-reduced-motion:reduce) {
    .st-key-home_banner [data-testid="stButton"] button {transition:none!important;transform:none!important}
    .st-key-home_banner [data-testid="stButton"] button::after {animation:none!important;opacity:0}
}
.home-stats {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:4px 0 10px}
.home-stat {background:white;border:1px solid #dce8df;border-radius:18px;padding:19px 21px;box-shadow:0 4px 18px #183e3004}
.home-stat:first-child {background:#e7f0e6;border-color:#cadfc6}
.home-stat-label {font-size:13px;color:#667e6e;line-height:1.5;min-height:20px}
.home-stat-value {font-size:42px;font-weight:700;line-height:1.15;color:#173e2d;letter-spacing:-1.5px;margin-top:8px}
.home-stat-unit {font-size:12px;color:#6e8376;font-weight:400;letter-spacing:0;margin-left:8px}
.home-data-note {font-size:11px;color:#7b8c81;margin:0 2px 23px;line-height:1.6}
.home-section-heading {display:flex;justify-content:space-between;align-items:center;gap:12px;margin:0 0 14px}
.home-section-heading h2 {font-size:25px;margin:0;padding:0;color:#183e30;line-height:1.4}
.home-section-heading > span {color:#6e8376;font-size:12px;white-space:nowrap}
.category-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:30px}
.category {background:white;border:1px solid #dce8df;border-radius:20px;padding:21px 18px 18px;min-width:0;border-top:3px solid var(--category-color);box-shadow:0 6px 20px #173e3005}
.category-icon {display:flex;align-items:center;justify-content:center;width:51px;height:51px;border-radius:15px;background:var(--category-tint);color:var(--category-color);margin-bottom:18px}
.category-icon svg {width:29px;height:29px;display:block}
.category h3 {font-size:21px;line-height:1.45;margin:0;min-height:61px;padding:0;color:#183e30}
.category-en {font-size:11px;letter-spacing:1.2px;text-transform:uppercase;color:var(--category-color);margin-top:5px;font-weight:600}
.category-examples {font-size:12px;line-height:1.7;color:#7a8b80;border-top:1px solid #eef2ed;padding-top:12px;margin-top:14px;min-height:41px}
.process-heading {font-size:22px!important;margin:0 0 16px!important;padding:0!important;line-height:1.5!important}
.process-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px}
.process-step {padding:20px;background:#eff4ee;border:1px solid #e1e9df;border-radius:17px;min-width:0}
.step-number {display:flex;align-items:center;justify-content:center;width:33px;height:33px;border-radius:10px;background:white;color:#27734f;font-size:13px;font-weight:700;margin-bottom:14px}
.process-step h3 {font-size:16px;line-height:1.5;color:#214633;margin:0 0 6px;padding:0}
.process-step p {font-size:12px;line-height:1.8;color:#748477;margin:0}
[data-testid="stButton"] button {border-radius:12px;min-height:44px}
.csv-download {display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:8px 18px;background:#18845D;color:white!important;border-radius:12px;text-decoration:none!important;font-weight:600}
.csv-download:hover {background:#116b49}
.csv-download:focus-visible {outline:3px solid #18845D;outline-offset:3px}
@media(max-width:700px){.category-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.home-stat{padding:15px 12px}.home-stat-value{font-size:32px}.home-stat-label{font-size:11px;min-height:33px}.home-stat-unit{display:none}.home-stats{gap:9px}.home-section-heading h2{font-size:22px}.home-section-heading > span{font-size:10px}.category h3{min-height:31px;font-size:20px}.process-grid{grid-template-columns:1fr}.process-step{display:grid;grid-template-columns:34px 1fr;column-gap:14px;padding:17px}.step-number{grid-row:1/3;margin:0}.process-step h3,.process-step p{grid-column:2}.block-container{padding-top:3rem}}
</style>''', unsafe_allow_html=True)

@st.cache_resource
def engine():
    return WasteEngine()

def go_detect():
    st.session_state.page = 'วิเคราะห์ขยะ'

NAV_PAGES = ['หน้าแรก','วิเคราะห์ขยะ','Dashboard','ประวัติ']
if st.session_state.get('page') not in NAV_PAGES:
    st.session_state.page = 'หน้าแรก'

with st.sidebar:
    st.markdown('## ♻ Waste Detective')
    st.caption('SMART SORTING · IT232')
    st.radio('เมนูหลัก', NAV_PAGES, key='page')

page = st.session_state.page
rows = history()
colors = {k:v['color'] for k,v in CATEGORIES.items()}

def metrics():
    cols = st.columns(3)
    cols[0].metric('การวิเคราะห์ทั้งหมด', len(rows))
    cols[1].metric('ระบุประเภทได้', sum(r['status']=='classified' for r in rows))
    cols[2].metric('ต้องตรวจสอบเพิ่มเติม', sum(r['category']=='Unknown' for r in rows))

if page == 'หน้าแรก':
    with st.container(key='home_banner'):
        st.button('เริ่มวิเคราะห์ขยะ  →', type='primary', on_click=go_detect, key='start_analysis', width='stretch')

    stats = [('การวิเคราะห์ทั้งหมด',len(rows)),
             ('ระบุประเภทได้',sum(r['status']=='classified' for r in rows)),
             ('ต้องตรวจสอบเพิ่มเติม',sum(r['category']=='Unknown' for r in rows))]
    stat_cards = ''.join(f'<div class="home-stat"><div class="home-stat-label">{label}</div><div class="home-stat-value">{value:,}<span class="home-stat-unit">ครั้ง</span></div></div>' for label,value in stats)
    st.markdown(f'<section aria-label="สถิติการวิเคราะห์"><div class="home-stats">{stat_cards}</div><p class="home-data-note">นับครั้งที่วิเคราะห์ภาพ ไม่ใช่จำนวนขยะที่รีไซเคิลจริง · ไม่รวมรายการทดสอบ</p></section>', unsafe_allow_html=True)

    category_paths = {
        'Plastic':'<path d="M10 3h4v4l2 3v10a1 1 0 0 1-1 1H9a1 1 0 0 1-1-1V10l2-3V3Z"/><path d="M10 5h4M8 12h8M8 17h8"/>',
        'Paper':'<path d="M7 3h8l4 4v14H5V5a2 2 0 0 1 2-2Z"/><path d="M14 3v5h5M8 12h8M8 16h8"/>',
        'Glass':'<path d="M7 3h10v3H7zM8 6v3l-2 3v8a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-8l-2-3V6"/><path d="M6 13h12"/>',
        'Hazardous':'<path d="M9 3h6v3H9zM7 6h10v15H7z"/><path d="m13 9-3 5h4l-3 4"/>'
    }
    examples = {'Plastic':'ขวดน้ำ · ถุง · แก้วพลาสติก','Paper':'กระดาษ · กล่อง · หนังสือพิมพ์',
                'Glass':'ขวดแก้ว · โหลแก้ว','Hazardous':'ถ่านไฟฉาย · แบตเตอรี่'}
    category_cards = []
    for key,cat in list(CATEGORIES.items())[:4]:
        icon = f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{category_paths[key]}</svg>'
        category_cards.append(f'<article class="category" style="--category-color:{cat["color"]};--category-tint:{cat["color"]}14"><div class="category-icon">{icon}</div><h3>{cat["th"]}</h3><div class="category-en">{key}</div><div class="category-examples">{examples[key]}</div></article>')
    st.markdown('<section aria-label="ประเภทขยะ"><div class="home-section-heading"><h2>เริ่มจากขยะใกล้ตัว</h2><span>4 ประเภทที่ AI ช่วยแยกได้</span></div><div class="category-grid">'+''.join(category_cards)+'</div></section>', unsafe_allow_html=True)

    steps = [('01','ถ่ายหรืออัปโหลด','วางวัตถุหนึ่งชิ้นให้เห็นชัด'),
             ('02','ดูผลจาก AI','ดูประเภทและคะแนน หากไม่แน่ใจระบบจะแจ้งให้ทราบ'),
             ('03','ตรวจสอบและคัดแยก','อ่านคำแนะนำ แล้วตรวจเงื่อนไขจุดรับในพื้นที่')]
    step_cards = ''.join(f'<article class="process-step"><span class="step-number">{number}</span><h3>{title}</h3><p>{body}</p></article>' for number,title,body in steps)
    st.markdown('<section aria-label="ขั้นตอนการใช้งาน"><h2 class="process-heading">จากภาพหนึ่งภาพ สู่การคัดแยกที่เข้าใจง่าย</h2><div class="process-grid">'+step_cards+'</div></section>', unsafe_allow_html=True)

elif page == 'วิเคราะห์ขยะ':
    st.caption('DETECT / LEARN / SORT')
    st.title('ให้ภาพช่วยบอกประเภทขยะ')
    st.write('ถ่ายวัตถุครั้งละหนึ่งชิ้น บนพื้นหลังเรียบและมีแสงเพียงพอ')
    left, right = st.columns([1.1,1], gap='large')
    with left:
        source = st.radio('วิธีเพิ่มภาพ', ['อัปโหลดภาพ','ถ่ายจากกล้อง'], horizontal=True)
        if os.environ.get('VERCEL') == '1':
            from services.browser_input import browser_image
            try:
                file=browser_image(source)
            except ValueError as exc:
                file=None
                st.error(str(exc))
        elif source == 'อัปโหลดภาพ':
            file = st.file_uploader('เลือก JPG หรือ PNG ไม่เกิน 10 MB', type=['jpg','jpeg','png'])
        else:
            file = st.camera_input('ถ่ายภาพขยะ')
            st.caption('กล้องต้องได้รับอนุญาตจากเบราว์เซอร์ ใช้ localhost หรือ HTTPS')
        is_test = st.checkbox('บันทึกเป็นข้อมูลทดสอบ', value=False)
        image, image_id = None, None
        if file:
            try:
                image, image_id = validate_image(file.getvalue())
                if os.environ.get('VERCEL') == '1':
                    import io
                    preview=io.BytesIO();image.save(preview,format='JPEG',quality=85)
                    preview_b64=base64.b64encode(preview.getvalue()).decode('ascii')
                    st.markdown(f'<img alt="ภาพที่เลือก" style="width:100%;max-height:360px;object-fit:contain;border-radius:12px" src="data:image/jpeg;base64,{preview_b64}">',unsafe_allow_html=True)
                else:
                    st.image(image, caption='ภาพที่เลือก', width='stretch')
            except ValueError as exc:
                st.error(str(exc))
        signature = (image_id, source, is_test)
        if st.session_state.get('image_signature') != signature:
            st.session_state.pop('result', None)
            st.session_state.image_signature = signature
        if st.button('Analyze Waste', type='primary', disabled=image is None):
            st.session_state.pop('result', None)
            try:
                with st.spinner('กำลังวิเคราะห์ภาพด้วย CLIP… การโหลดครั้งแรกอาจใช้เวลาสักครู่'):
                    result = engine().predict(image)
                    event_id = str(uuid.uuid4())
                    save(result, image_id, source, is_test, event_id=event_id)
                    st.session_state.result = result
            except Exception as exc:
                st.error(f'วิเคราะห์หรือบันทึกไม่สำเร็จ: {exc}')
                st.caption('ไม่มีการสร้างผลทดแทน กรุณาตรวจโมเดลและสิทธิ์เขียนฐานข้อมูลแล้วลองใหม่')
    with right:
        result = st.session_state.get('result')
        if result:
            cat = CATEGORIES[result['category']]
            st.subheader(f'{cat["icon"]} {cat["th"]}')
            st.caption(result['category'] + ' • ' + result['status'])
            st.metric('คะแนนอันดับหนึ่งของโมเดล', f'{result["confidence"]:.1%}')
            st.progress(result['confidence'])
            st.caption('คะแนน softmax เปรียบเทียบระหว่าง 5 กลุ่มคำอธิบาย ไม่ใช่ความน่าจะเป็นที่สอบเทียบแล้วหรือค่าความแม่นยำ')
            if result['status'] == 'uncertain':
                st.warning('AI ยังไม่แน่ใจ กรุณาถ่ายใหม่หรือให้เจ้าหน้าที่ตรวจสอบ')
            st.markdown('### ควรจัดการอย่างไร')
            st.write(cat['advice'])
            st.caption(f'ประมวลผล {result["elapsed_ms"]:,.0f} ms · บันทึกผลแล้ว')
            with st.expander('รายละเอียดผลและข้อจำกัด'):
                st.write(f'กลุ่มคำอธิบายอันดับหนึ่ง: {result["candidate"]}')
                st.write(f'เกณฑ์คะแนน {result["threshold"]:.0%} และส่วนต่าง {result["margin_threshold"]:.0%} (ค่าเริ่มต้น ยังไม่ผ่าน calibration)')
                st.dataframe(pd.DataFrame(result['scores'].items(), columns=['Category','Score']), hide_index=True)
                st.write('CLIP เปรียบเทียบภาพกับคำอธิบาย ไม่ได้สร้างเหตุผลจากวัตถุที่ตรวจพบจริง ภาพหลายชิ้น ภาพเบลอ และวัตถุนอกกลุ่มยังอาจได้คะแนนสูงผิดพลาด')
        else:
            st.markdown('### พร้อมเมื่อคุณพร้อม')
            st.write('ผลวิเคราะห์และคำแนะนำจะปรากฏตรงนี้ หลังจากเลือกภาพและกด Analyze Waste')
        st.warning('ภาพเพียงอย่างเดียวระบุสารเคมีหรือยืนยันว่าไม่เป็นอันตรายไม่ได้ หากสงสัย ให้แยกไว้และสอบถามเจ้าหน้าที่')

elif page == 'Dashboard':
    st.caption('OVERVIEW')
    st.title('ภาพรวมการวิเคราะห์')
    metrics()
    st.caption('ข้อมูลจริงจาก SQLite ไม่รวมข้อมูลทดสอบ ไม่ใช่ปริมาณขยะที่เก็บหรือรีไซเคิลแล้ว')
    counts = pd.DataFrame([{'Category':k,'Count':sum(r['category']==k for r in rows)} for k in CATEGORIES])
    for col, (_, row) in zip(st.columns(5), counts.iterrows()):
        col.metric(CATEGORIES[row['Category']]['th'], int(row['Count']))
    if rows:
        a,b = st.columns(2)
        a.plotly_chart(px.pie(counts[counts.Count>0], names='Category',values='Count',hole=.65,color='Category',color_discrete_map=colors), use_container_width=True)
        b.plotly_chart(px.bar(counts,x='Category',y='Count',color='Category',color_discrete_map=colors), use_container_width=True)
        df = pd.DataFrame(rows)
        dates = pd.to_datetime(df.created_at, utc=True).dt.tz_convert('Asia/Bangkok').dt.date
        daily = dates.value_counts().sort_index().rename_axis('Date').reset_index(name='Count')
        st.plotly_chart(px.line(daily,x='Date',y='Count',markers=True,title='จำนวนการวิเคราะห์รายวัน (เวลาไทย)'), use_container_width=True)
        st.subheader('รายการล่าสุด')
        st.dataframe(df[['created_at','category','confidence','status']].head(10), hide_index=True)
        st.caption('เวลาในตารางเป็น UTC ตามข้อมูลที่บันทึก')
    else:
        st.info('ยังไม่มีการวิเคราะห์ เริ่มจากภาพแรกของคุณ แล้วกราฟจะปรากฏที่นี่')
        st.button('เพิ่มการวิเคราะห์แรก', on_click=go_detect)

elif page == 'ประวัติ':
    st.title('ประวัติการวิเคราะห์')
    if os.environ.get('VERCEL') == '1':
        st.caption('โหมดสาธิตออนไลน์: ประวัติเป็นข้อมูลชั่วคราวของเซิร์ฟเวอร์ อาจไม่ครบหรือหายเมื่อเปลี่ยนเซิร์ฟเวอร์ กรุณาส่งออก CSV หากต้องการเก็บไว้')
    show_test = st.checkbox('รวมข้อมูลทดสอบ')
    all_rows = history(include_test=show_test)
    a,b = st.columns([1,2])
    category = a.selectbox('ประเภท', ['ทั้งหมด',*CATEGORIES])
    query = b.text_input('ค้นหาด้วย Image ID หรือวันที่ UTC').strip().lower()
    filtered = [r for r in all_rows if (category=='ทั้งหมด' or r['category']==category) and (query in r['image_id'].lower() or query in r['created_at'].lower())]
    st.caption(f'{len(filtered)} รายการ • เก็บรหัสภาพ SHA-256 แทนชื่อไฟล์หรือภาพส่วนบุคคล • เวลา UTC')
    st.dataframe(pd.DataFrame(filtered), hide_index=True, use_container_width=True)
    # The CSV is encoded in the download link itself, so it cannot be lost
    # when a separate HTTP request reaches another serverless instance.
    csv_payload = base64.b64encode(export_csv(filtered)).decode('ascii')
    st.markdown(f'<a class="csv-download" role="button" download="waste_history.csv" '
                f'href="data:text/csv;base64,{csv_payload}">ส่งออก CSV</a>', unsafe_allow_html=True)
    with st.expander('ล้างเฉพาะข้อมูลทดสอบ'):
        confirm = st.checkbox('ยืนยันลบข้อมูลที่มีป้ายกำกับทดสอบทั้งหมด')
        if st.button('ลบข้อมูลทดสอบ', disabled=not confirm):
            count = clear_test()
            st.session_state.pop('result', None)
            st.success(f'ลบแล้ว {count} รายการ')
            st.rerun()

