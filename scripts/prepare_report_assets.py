from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/report_bw';OUT.mkdir(parents=True,exist_ok=True)
for original,name in [('Workflow_Diagram','workflow_bw'),('System_Architecture','architecture_bw')]:
    tree=ET.parse(ROOT/'docs'/f'{original}.svg')
    for el in tree.iter():
        tag=el.tag.split('}')[-1]
        for attr in ['fill','stroke']:
            value=el.get(attr,'')
            if value.startswith('#'):
                el.set(attr,'#FFFFFF' if attr=='fill' and tag=='rect' else '#000000')
    tree.write(OUT/f'{name}.svg',encoding='utf-8',xml_declaration=True)
for original,name in [('result_hazardous.png','result_report_bw.png'),('dashboard_data.png','dashboard_report_bw.png'),('history_filtered.png','history_report_bw.png')]:
    im=Image.open(ROOT/'assets/screenshots'/original).convert('RGB')
    # Keep only the main work area of the original, genuine QA screenshot.
    im=im.crop((300,60,im.width,im.height))
    ImageOps.grayscale(im).save(OUT/name)
print('Prepared monochrome diagrams and genuine QA screenshots')
