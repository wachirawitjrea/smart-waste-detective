"""Export the existing prompt ensemble; no training or threshold tuning."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from services.engine import WasteEngine, CATEGORIES, SETTINGS

engine = WasteEngine()
out = ROOT / 'cloudflare/public/config.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({
    'categories': CATEGORIES, 'settings': SETTINGS,
    'labels': engine.labels,
    'text_features': engine.text_features.tolist(),
    'logit_scale': engine.model.logit_scale.exp().item(),
    'original_model_revision': '3d74acf9a28c67741b2f4f2ea7635f0aaf6f0268',
    'prompt_sha256': hashlib.sha256((ROOT/'config/categories.json').read_bytes()).hexdigest(),
    'browser_model': 'Xenova/clip-vit-base-patch32',
    'browser_revision': '6b7c523703ae26e39be4b03774966f8571c7f523',
    'dtype': 'q8',
}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print('Exported five prompt vectors and original logit scale to', out)
