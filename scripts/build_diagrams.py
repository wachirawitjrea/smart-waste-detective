from pathlib import Path
from html import escape

OUT=Path(__file__).resolve().parents[1]/'docs'

def start(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><defs><marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#47745e"/></marker></defs><rect width="100%" height="100%" fill="#f7faf7"/><text x="40" y="50" font-family="Arial" font-weight="bold" font-size="27" fill="#183e30">{title}</text>']
def box(s,x,y,w,h,text,fill='#e6f0e8'):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="{fill}" stroke="#9ab6a3"/>')
    lines=text.split('|')
    for i,line in enumerate(lines):
        s.append(f'<text x="{x+w/2}" y="{y+h/2+(i-(len(lines)-1)/2)*24+7}" text-anchor="middle" font-family="Arial" font-size="18" fill="#183e30">{escape(line)}</text>')
def arrow(s,x,y,xx,yy,label=''):
    s.append(f'<path d="M{x},{y} L{xx},{yy}" stroke="#47745e" stroke-width="2.3" fill="none" marker-end="url(#a)"/>')
    if label:s.append(f'<text x="{(x+xx)/2+10}" y="{(y+yy)/2-8}" font-family="Arial" font-size="16" fill="#47745e">{label}</text>')

s=start(1000,1030,'Smart Waste Detective / Workflow')
for y,t in [(85,'Start'),(175,'Upload image / Camera capture'),(265,'Validate format, bytes and pixels'),(355,'EXIF transpose / RGB / Resize'),(445,'CLIP image and text encoders'),(535,'Class scores / Confidence checks')]:
    box(s,270,y,460,65,t)
    if y<535:arrow(s,500,y+65,500,y+90)
arrow(s,270,297,90,297,'Invalid');box(s,20,330,185,70,'Show error|Retry','#f8e5df');arrow(s,90,297,90,330)
arrow(s,380,600,250,655,'Accepted');arrow(s,620,600,750,655,'Uncertain')
box(s,60,655,380,85,'Show waste category|Show disposal guidance')
box(s,560,655,380,85,'Unknown / Uncertain|Retake or check manually','#f8ead6')
arrow(s,250,740,250,780);arrow(s,750,740,750,780)
box(s,60,780,380,70,'Save result to SQLite');box(s,560,780,380,70,'Save uncertain status to SQLite')
arrow(s,250,850,380,900);arrow(s,750,850,620,900)
box(s,270,900,460,70,'Dashboard / History / End')
s.append('</svg>');(OUT/'Workflow_Diagram.svg').write_text(''.join(s),encoding='utf-8')
s=start(1100,650,'Smart Waste Detective / System architecture')
box(s,40,120,245,100,'Browser|Upload / Camera')
box(s,405,120,270,100,'Streamlit app.py|Validation / Results')
box(s,795,120,265,100,'Local CLIP model|Prompt ensemble')
arrow(s,285,170,405,170,'Image');arrow(s,675,150,795,150,'Pixels');arrow(s,795,195,675,195,'Scores')
box(s,405,340,270,100,'SQLite|Metadata and predictions')
arrow(s,540,220,540,340,'Save')
box(s,40,340,245,100,'Plotly Dashboard|Counts and trends')
box(s,795,340,265,100,'History / CSV|Search and test cleanup')
arrow(s,405,390,285,390,'Read');arrow(s,675,390,795,390,'Read')
box(s,260,510,580,80,'No external inference API / No original image storage|Test data excluded from dashboard by default','#f0f2ea')
s.append('</svg>');(OUT/'System_Architecture.svg').write_text(''.join(s),encoding='utf-8')
print('SVG diagrams created')
