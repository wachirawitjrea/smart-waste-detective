"""Run real inference on a provided image; no accuracy claims."""
import json
import sys
import time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from services.engine import WasteEngine
from services.images import validate_image

if __name__=='__main__':
    image,digest=validate_image(Path(sys.argv[1]).read_bytes())
    start=time.perf_counter(); engine=WasteEngine(); load=time.perf_counter()-start
    result=engine.predict(image)
    result.update(image_sha256=digest,load_seconds=load,
        note='Real inference smoke test only. Not model accuracy evaluation. Input is a user-provided design reference image.')
    Path('docs/model_smoke.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
