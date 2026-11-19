"""Real local CLIP inference. No synthetic predictions or fallback labels."""
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = json.loads((ROOT / 'config/categories.json').read_text(encoding='utf-8'))
SETTINGS = json.loads((ROOT / 'config/settings.json').read_text(encoding='utf-8'))

def decide(scores, threshold=0.65, margin=0.15):
    if not 0 <= threshold <= 1 or not 0 <= margin <= 1:
        raise ValueError('Invalid threshold')
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    top, confidence = ordered[0]
    gap = confidence - ordered[1][1]
    accepted = top != 'Unknown' and confidence >= threshold and gap >= margin
    return {'category': top if accepted else 'Unknown', 'candidate': top,
            'confidence': confidence, 'margin': gap,
            'status': 'classified' if accepted else 'uncertain',
            'scores': scores, 'threshold': threshold, 'margin_threshold': margin}

class WasteEngine:
    def __init__(self):
        import torch
        from transformers import CLIPModel, CLIPProcessor
        self.torch = torch
        torch.set_num_threads(min(4, torch.get_num_threads()))
        local = ROOT / 'models/clip'
        if not (local / 'config.json').exists():
            raise RuntimeError('ยังไม่มีโมเดล กรุณารัน python scripts/download_model.py ก่อน')
        self.processor = CLIPProcessor.from_pretrained(local, local_files_only=True, use_fast=False)
        self.model = CLIPModel.from_pretrained(local, local_files_only=True).eval()
        self.labels = list(CATEGORIES)
        prompts = [p for item in CATEGORIES.values() for p in item['prompts']]
        with torch.inference_mode():
            tokens = self.processor(text=prompts, return_tensors='pt', padding=True)
            vectors = self.model.get_text_features(**tokens)
            vectors = vectors / vectors.norm(dim=-1, keepdim=True)
            # Equal-size prompt ensemble per category avoids prompt-count bias.
            vectors = vectors.reshape(len(self.labels), 3, -1).mean(dim=1)
            self.text_features = vectors / vectors.norm(dim=-1, keepdim=True)

    def predict(self, image, threshold=None, margin=None):
        start = time.perf_counter()
        torch = self.torch
        with torch.inference_mode():
            inputs = self.processor(images=image, return_tensors='pt')
            features = self.model.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)
            logits = self.model.logit_scale.exp() * features @ self.text_features.T
            values = logits.softmax(dim=-1)[0].tolist()
        result = decide(dict(zip(self.labels, values)),
                        SETTINGS['threshold'] if threshold is None else threshold,
                        SETTINGS['margin'] if margin is None else margin)
        result.update(elapsed_ms=round((time.perf_counter()-start)*1000, 1),
                      model=SETTINGS['model_id'], prompt_version=SETTINGS['prompt_version'])
        return result
