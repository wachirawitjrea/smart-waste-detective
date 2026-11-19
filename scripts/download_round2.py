"""Download a second diagnostic set, excluding every original file and hash."""
import csv, hashlib, json, random, shutil
from pathlib import Path
from datetime import datetime, timezone
from huggingface_hub import HfApi, hf_hub_download

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
REPO='omasteam/waste-garbage-management-dataset'
REVISION='1022529d853bd0b86025876e3c2daee5d2357235'
mapping={'plastic':'Plastic','paper':'Paper','glass':'Glass','battery':'Hazardous','biological':'Unknown'}
original=list(csv.DictReader((DATA/'sample_manifest.csv').open(encoding='utf-8-sig')))
excluded_sources={r['source'] for r in original}
seen={hashlib.sha256((DATA/r['path']).read_bytes()).hexdigest() for r in original}
api=HfApi();rows=[]
for folder,label in mapping.items():
    files=sorted(f.path for f in api.list_repo_tree(REPO,repo_type='dataset',path_in_repo=folder,revision=REVISION)
                 if f.path.lower().endswith(('.jpg','.jpeg','.png')))
    random.Random(233).shuffle(files)
    selected=0
    for file in files:
        source=f'https://huggingface.co/datasets/{REPO}/blob/{REVISION}/{file}'
        if source in excluded_sources:continue
        cached=Path(hf_hub_download(REPO,file,repo_type='dataset',revision=REVISION))
        digest=hashlib.sha256(cached.read_bytes()).hexdigest()
        if digest in seen:continue
        seen.add(digest)
        dest=DATA/'samples_round2'/folder/Path(file).name
        dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(cached,dest)
        rows.append({'path':dest.relative_to(DATA).as_posix(),'label':label,'split':'test',
                     'source':source,'license':'MIT per dataset card','object_id':folder+'_'+Path(file).stem,'sha256':digest})
        selected+=1
        if selected==10:break
    if selected!=10:raise RuntimeError('Not enough unique samples: '+folder)
    print(label,selected,flush=True)
with (DATA/'round2_manifest.csv').open('w',newline='',encoding='utf-8') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
(DATA/'round2_provenance.json').write_text(json.dumps({'repo':REPO,'revision':REVISION,'seed':233,
    'downloaded_at':datetime.now(timezone.utc).isoformat(),'n':len(rows),'excluded_original_images':len(original),
    'unique_hashes':len({r['sha256'] for r in rows}),'original_hash_overlap':0,
    'selection':'Sorted source files, seeded shuffle, first 10 per group after source and SHA-256 exclusions',
    'limitations':'Same source as round one; source labels; no independent human annotation. Battery-only Hazardous and biological-only Unknown. Not used to tune prompts or thresholds.'},indent=2),encoding='utf-8')
print('Downloaded 50 new diagnostic images',flush=True)
