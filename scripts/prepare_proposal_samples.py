"""Lay out the unmodified color test images with black result captions."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'assets/proposal_color';out.mkdir(parents=True,exist_ok=True)
evaluation=json.loads((ROOT/'docs/evaluation_round2.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
for label in evaluation['label_order']:
    rows=[r for r in evaluation['results'] if r['label']==label]
    canvas=Image.new('RGB',(1500,2000),'white');draw=ImageDraw.Draw(canvas)
    for i,row in enumerate(rows):
        x=(i%2)*750;y=(i//2)*400
        im=Image.open(ROOT/'data'/row['path']).convert('RGB')
        im=ImageOps.contain(im,(680,292))
        canvas.paste(im,(x+(750-im.width)//2,y+(292-im.height)//2))
        draw.text((x+18,y+302),Path(row['path']).name,font=font,fill='black')
        draw.text((x+18,y+343),f"{label} > {row['category']}  ({row['confidence']:.3f})",font=font,fill='black')
    target=out/f'round2_color_{label.lower()}.png';canvas.save(target)
    print(target.name)
