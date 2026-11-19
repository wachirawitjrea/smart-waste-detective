"""Create portable source and model-inclusive ZIPs, excluding local runtimes and caches."""
from pathlib import Path
import argparse, hashlib, json, zipfile

parser=argparse.ArgumentParser()
parser.add_argument('--github-only',action='store_true',help='Build only the small GitHub repository archive')
args=parser.parse_args()

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'deliverables'; OUT.mkdir(exist_ok=True)
root_files=['app.py','asgi.py','pyproject.toml','vercel.json','requirements.txt','requirements-lock.txt','README.md','.gitignore','.gitattributes','.env.example','setup.ps1','run.bat']
folders=['.streamlit','config','services','assets','tests','scripts','docs','data']
files=[ROOT/name for name in root_files]
for folder in folders:
    for file in sorted((ROOT/folder).rglob('*')):
        if not file.is_file() or '__pycache__' in file.parts: continue
        if file.name.startswith('.') or file.suffix=='.log': continue
        files.append(file)
files+=[ROOT/'database/schema.sql',ROOT/'models/model_metadata.json']
if (ROOT/'database/waste.db').is_file(): files.append(ROOT/'database/waste.db')

required=['docs/Project_Proposal.docx','docs/Project_Proposal.pdf','docs/Final_Presentation.pptx',
          'docs/Project_Report.docx','docs/Project_Report.pdf','asgi.py','pyproject.toml','vercel.json',
          'docs/Presentation_Script.md','docs/Demo_Guide.md','docs/Test_Report.md',
          'docs/Workflow_Diagram.png','docs/Workflow_Diagram.svg','docs/System_Architecture.png',
          'docs/System_Architecture.svg','docs/evaluation.json','docs/pytest_results.xml']
for rel in required:
    if not (ROOT/rel).is_file(): raise FileNotFoundError(rel)
manifest=OUT/'package_manifest.json'
entries=json.loads(manifest.read_text(encoding='utf-8')) if args.github_only and manifest.is_file() else []
packages=[(False,'Smart_Waste_Detective_GitHub_Ready.zip')] if args.github_only else [(False,'Smart_Waste_Detective_Source.zip'),(True,'Smart_Waste_Detective_With_Model.zip'),(False,'Smart_Waste_Detective_GitHub_Ready.zip')]
for with_model,name in packages:
    selected=list(files)
    github_ready='GitHub_Ready' in name
    if github_ready:
        selected=[f for f in selected if f.relative_to(ROOT).as_posix()!='database/waste.db']
    if with_model:
        if not (ROOT/'models/clip/pytorch_model.bin').is_file():
            print('Skipped model-inclusive archive: download the model first',flush=True)
            continue
        selected += [f for f in sorted((ROOT/'models/clip').glob('*')) if f.is_file()]
    if github_ready and any(f.stat().st_size>=25*1024**2 for f in selected):
        raise RuntimeError('A GitHub-ready file exceeds the browser upload limit')
    target=OUT/name
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=3) as z:
        for file in selected:
            z.write(file,'Smart-Waste-Detective/'+file.relative_to(ROOT).as_posix())
    with zipfile.ZipFile(target) as z:
        bad=z.testzip()
        if bad: raise RuntimeError('Corrupt ZIP entry '+bad)
        names=z.namelist()
        for rel in required:
            if 'Smart-Waste-Detective/'+rel not in names: raise RuntimeError('Missing '+rel)
        if any('/.venv/' in x or '/.cache/' in x or '/tmp/' in x for x in names):
            raise RuntimeError('Private build path in archive')
    digest=hashlib.file_digest(target.open('rb'),'sha256').hexdigest()
    entries=[r for r in entries if r['name']!=name]
    entries.append({'name':name,'bytes':target.stat().st_size,'sha256':digest,'files':len(selected),'includes_model':with_model})
    print(name,round(target.stat().st_size/1024**2,1),'MiB',len(selected),'files',flush=True)
manifest.write_text(json.dumps(entries,indent=2),encoding='utf-8')
print('ZIP CRC and required files verified',flush=True)
