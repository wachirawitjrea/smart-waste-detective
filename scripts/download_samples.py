"""Small deterministic diagnostic sample; not a representative benchmark."""
from huggingface_hub import HfApi, hf_hub_download
from pathlib import Path
import random, csv, shutil, json

repo='omasteam/waste-garbage-management-dataset'
root=Path(__file__).resolve().parents[1]/'data'
mapping={'plastic':'Plastic','paper':'Paper','glass':'Glass','battery':'Hazardous','biological':'Unknown'}
api=HfApi(); revision='1022529d853bd0b86025876e3c2daee5d2357235'
rows=[]
for folder,label in mapping.items():
    files=[f.path for f in api.list_repo_tree(repo,repo_type='dataset',path_in_repo=folder,revision=revision) if f.path.lower().endswith(('.jpg','.jpeg','.png'))]
    random.Random(232).shuffle(files)
    if len(files)<10: raise RuntimeError(f'Missing samples in {folder}')
    for i,file in enumerate(files[:10]):
        cached=hf_hub_download(repo,file,repo_type='dataset',revision=revision)
        dest=root/'samples'/folder/Path(file).name
        dest.parent.mkdir(parents=True,exist_ok=True); shutil.copyfile(cached,dest)
        rows.append({'path':str(dest.relative_to(root)).replace('\\','/'),'label':label,'split':'test',
          'source':f'https://huggingface.co/datasets/{repo}/blob/{revision}/{file}',
          'license':'MIT per dataset card','object_id':folder+'_'+Path(file).stem})
with (root/'sample_manifest.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
card=hf_hub_download(repo,'README.md',repo_type='dataset',revision=revision)
shutil.copyfile(card,root/'DATASET_SOURCE.md')
(root/'sample_provenance.json').write_text(json.dumps({'repo':repo,'revision':revision,'seed':232,'sampling':'10 per folder after seeded shuffle, test only, no training or calibration','limitations':'Labels inherited from source. Hazardous represents batteries only. Unknown represents biological only. Object grouping inferred from filenames and requires human review.'},indent=2),encoding='utf-8')
print('Downloaded',len(rows),'diagnostic images')
