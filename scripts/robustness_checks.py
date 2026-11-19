"""Diagnostic stress cases, explicitly separate from the labeled benchmark."""
import json, sys
from pathlib import Path
from PIL import Image, ImageFilter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.engine import WasteEngine, decide

root=Path(__file__).resolve().parents[1]
evaluation=json.loads((root/'docs/evaluation.json').read_text(encoding='utf-8'))
def pick(label):
    r=next(r for r in evaluation['results'] if r['label']==label)
    return Image.open(root/'data'/r['path']).convert('RGB')
engine=WasteEngine()
plastic=pick('Plastic'); glass=pick('Glass')
mixed=Image.new('RGB',(800,400),'white')
for i,im in enumerate([plastic,glass]):
    im.thumbnail((400,400)); mixed.paste(im,(i*400,0))
cases={'blurred_plastic':plastic.resize((400,400)).filter(ImageFilter.GaussianBlur(15)),
       'multiple_objects':mixed,'no_waste_blank':Image.new('RGB',(400,400),'white')}
results=[]
for name,image in cases.items():
    result=engine.predict(image)
    result.update(case=name,kind='derived diagnostic input, not a new independent test sample')
    results.append(result)
sensitivity=[]
for threshold in [.5,.65,.8]:
    predictions=[decide(r['scores'],threshold,.15)['category'] for r in evaluation['results']]
    sensitivity.append({'threshold':threshold,'margin':.15,
       'accuracy':sum(p==r['label'] for p,r in zip(predictions,evaluation['results']))/len(predictions),
       'coverage':sum(p!='Unknown' for p in predictions)/len(predictions)})
out={'cases':results,'sensitivity':sensitivity,'note':'Exploratory rescoring of same diagnostic test set. No threshold selection or calibration. Production settings remain 0.65 / 0.15.'}
(root/'docs/robustness.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
