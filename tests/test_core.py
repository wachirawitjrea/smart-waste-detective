import io
from pathlib import Path
import pytest
from PIL import Image
from services.images import validate_image, MAX_BYTES
from services.engine import decide
from services.storage import save, history, clear_test, export_csv

def picture(fmt='PNG', size=(64,64)):
    stream = io.BytesIO()
    Image.new('RGB',size,'green').save(stream,format=fmt)
    return stream.getvalue()

@pytest.mark.parametrize('fmt',['PNG','JPEG'])
def test_valid_image(fmt):
    im, digest = validate_image(picture(fmt))
    assert im.mode=='RGB' and len(digest)==64

@pytest.mark.parametrize('data',[b'',b'not an image',b'\x89PNG\r\n\x1a\ncorrupt',b'x'*(MAX_BYTES+1)])
def test_invalid_file(data):
    with pytest.raises(ValueError): validate_image(data)

def test_actual_type_checked():
    with pytest.raises(ValueError): validate_image(picture('GIF'))

def test_tiny_image():
    with pytest.raises(ValueError): validate_image(picture(size=(12,12)))

def test_large_pixel_limit():
    with pytest.raises(ValueError): validate_image(picture(size=(5000,4100)))

@pytest.mark.parametrize('scores,expected',[
    ({'Plastic':.8,'Paper':.1,'Glass':.03,'Hazardous':.04,'Unknown':.03},'Plastic'),
    ({'Plastic':.4,'Paper':.35,'Glass':.1,'Hazardous':.1,'Unknown':.05},'Unknown'),
    ({'Plastic':.03,'Paper':.03,'Glass':.03,'Hazardous':.01,'Unknown':.9},'Unknown'),
    ({'Plastic':.05,'Paper':.05,'Glass':.05,'Hazardous':.8,'Unknown':.05},'Hazardous')])
def test_decision(scores,expected):
    assert decide(scores)['category']==expected

def test_margin_rejects_ambiguous():
    assert decide({'Plastic':.51,'Glass':.49},.5,.15)['category']=='Unknown'

def test_storage_csv_and_test_deletion(tmp_path):
    path=tmp_path/'test.db'
    r=decide({'Plastic':.9,'Unknown':.1})
    r.update(elapsed_ms=10,model='unit-test-fixture',prompt_version='fixture')
    save(r,'a'*64,'upload',path=path,event_id='one')
    save(r,'a'*64,'upload',path=path,event_id='one')
    save(r,'b'*64,'camera',path=path,is_test=True,event_id='two')
    assert len(history(path))==1
    assert len(history(path,include_test=True))==2
    assert 'Plastic' in export_csv(history(path)).decode('utf-8-sig')
    assert clear_test(path)==1 and len(history(path,True))==1

def test_csv_formula_neutralized():
    assert "'=cmd" in export_csv([{'id':'=cmd'}]).decode('utf-8-sig')

def test_ui_navigation(tmp_path,monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv('WASTE_DB',str(tmp_path/'ui.db'))
    at=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py',default_timeout=30).run()
    assert not at.exception
    for page in ['วิเคราะห์ขยะ','Dashboard','ประวัติ','หน้าแรก']:
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception, page
