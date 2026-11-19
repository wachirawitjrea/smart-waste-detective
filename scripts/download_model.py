from pathlib import Path
import json
from huggingface_hub import snapshot_download

if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    metadata=json.loads((root/'models/model_metadata.json').read_text(encoding='utf-8'))
    path = snapshot_download(metadata['model_id'], revision=metadata['revision'], local_dir=root/'models/clip',
        allow_patterns=['config.json','preprocessor_config.json','tokenizer.json',
                        'tokenizer_config.json','special_tokens_map.json','vocab.json',
                        'merges.txt','pytorch_model.bin','README.md'])
    print(f'Model downloaded to {path}')
