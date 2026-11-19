from pathlib import Path
import csv, json, sqlite3, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
ROOT=Path(__file__).resolve().parents[1]
suite=ET.parse(ROOT/'docs/pytest_results.xml').getroot()
cases=suite.findall('.//testcase')
assert len(cases)==17 and not suite.findall('.//failure') and not suite.findall('.//error')
evaluation=json.loads((ROOT/'docs/evaluation.json').read_text(encoding='utf-8'))
assert evaluation['n']==50
correct=sum(r['label']==r['category'] for r in evaluation['results'])
assert correct==44 and evaluation['accuracy']==correct/50
e2e=json.loads((ROOT/'docs/browser_e2e.json').read_text(encoding='utf-8'))
assert not e2e['pageErrors'] and all(r['status']=='pass' for r in e2e['checks'])
with sqlite3.connect(ROOT/'.cache/browser_qa.db') as conn:
    rows=conn.execute('SELECT category,image_id FROM detections').fetchall()
assert len(rows)==2 and {r[0] for r in rows}=={'Paper','Hazardous'} and len({r[1] for r in rows})==2
with (ROOT/'docs/qa_export.csv').open(encoding='utf-8-sig',newline='') as stream: csv_rows=list(csv.DictReader(stream))
assert len(csv_rows)==1 and csv_rows[0]['category']=='Paper'
with sqlite3.connect(ROOT/'database/waste.db') as conn:
    main_count=conn.execute('SELECT COUNT(*) FROM detections').fetchone()[0]
receipt=json.loads((ROOT/'tmp/slides/validation.json').read_text(encoding='utf-8'))
assert receipt['packageIntegrity']['status']=='pass' and receipt['presentationLayout']['finding_count']==0
out={'checked_at_bangkok':datetime.now(timezone(timedelta(hours=7))).isoformat(),
     'functional_tests_passed':17,'model_sample_n':50,'model_sample_correct':44,
     'browser_checks_passed':len(e2e['checks']),'qa_database_events':2,
     'qa_distinct_images':2,'filtered_csv_rows':1,'filtered_csv_category':'Paper',
     'main_database_events':main_count,'pptx_slides':12,
     'pptx_package_and_layout':'pass','pptx_native_powerpoint_test':'not performed',
     'proposal_pages':10,'proposal_visual_review':'all pages reviewed after rendering',
     'slides_visual_review':'all 12 slide PNGs reviewed',
     'physical_camera':'not tested','user_testing':'not performed',
     'customization':'prompt engineering, no weight fine-tuning',
     'deployment':'localhost only'}
(ROOT/'docs/final_validation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
