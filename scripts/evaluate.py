"""Evaluate a labeled CSV without inventing labels or modifying the app database.
CSV columns: path,label,split,source,license,object_id
Use validation for threshold tuning, then freeze settings before test.
"""
import argparse
import csv
import json
import sys
from pathlib import Path
from collections import Counter
import hashlib
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.engine import WasteEngine, CATEGORIES, SETTINGS
from services.images import validate_image
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

def main():
    p=argparse.ArgumentParser()
    p.add_argument('manifest',type=Path)
    p.add_argument('--split',choices=['validation','test'],default='test')
    p.add_argument('--output',type=Path,default=Path('docs/evaluation.json'))
    args=p.parse_args()
    all_rows=list(csv.DictReader(args.manifest.open(encoding='utf-8-sig')))
    rows=[r for r in all_rows if r['split']==args.split]
    if not rows: raise SystemExit('No labeled images for requested split; no metrics produced.')
    seen_hashes={}; seen_objects={}
    for r in all_rows:
        if r['label'] not in CATEGORIES: raise ValueError('Unknown label: '+r['label'])
        if not r.get('source') or not r.get('license') or not r.get('object_id'):
            raise ValueError('Each image needs source, license and object_id')
        digest=hashlib.sha256((args.manifest.parent/r['path']).read_bytes()).hexdigest()
        for key,registry in [(digest,seen_hashes),(r['object_id'],seen_objects)]:
            if key in registry and registry[key]!=r['split']:
                raise ValueError('Data leakage between splits')
            registry[key]=r['split']
    engine=WasteEngine(); results=[]
    for row in rows:
        image,_=validate_image((args.manifest.parent/row['path']).read_bytes())
        result=engine.predict(image)
        results.append(dict(row,**result))
    true=[r['label'] for r in results]; pred=[r['category'] for r in results]
    labels=list(CATEGORIES)
    output={'split':args.split,'n':len(results),'class_counts':dict(Counter(true)),
      'settings':SETTINGS,'accuracy':accuracy_score(true,pred),
      'coverage':sum(r['status']=='classified' for r in results)/len(results),
      'classification_report':classification_report(true,pred,labels=labels,output_dict=True,zero_division=0),
      'confusion_matrix':confusion_matrix(true,pred,labels=labels).tolist(),'label_order':labels,
      'latency_ms_median':float(np.median([r['elapsed_ms'] for r in results])),
      'latency_ms_p95':float(np.percentile([r['elapsed_ms'] for r in results],95)),
      'timing_note':'CPU inference including preprocessing, excluding model load and UI',
      'results':results}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'Wrote {args.output}, n={len(results)}, accuracy={output["accuracy"]:.3f}')

if __name__=='__main__': main()
