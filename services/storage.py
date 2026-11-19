import csv
import io
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def connect(path=None):
    path = Path(path or os.environ.get('WASTE_DB', ROOT / 'database/waste.db'))
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute('''CREATE TABLE IF NOT EXISTS detections (
       id TEXT PRIMARY KEY, created_at TEXT NOT NULL, image_id TEXT NOT NULL,
       category TEXT NOT NULL, candidate TEXT NOT NULL, confidence REAL NOT NULL,
       status TEXT NOT NULL, source TEXT NOT NULL, elapsed_ms REAL NOT NULL,
       model TEXT NOT NULL, prompt_version TEXT NOT NULL, threshold REAL NOT NULL,
       margin_threshold REAL NOT NULL, scores_json TEXT NOT NULL,
       is_test INTEGER NOT NULL DEFAULT 0)''')
    conn.commit()
    return conn

def save(result, image_id, source, is_test=False, path=None, event_id=None):
    event_id = event_id or str(uuid.uuid4())
    with connect(path) as conn:
        conn.execute('INSERT OR IGNORE INTO detections VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
            (event_id, datetime.now(timezone.utc).isoformat(), image_id,
             result['category'], result['candidate'], result['confidence'], result['status'],
             source, result['elapsed_ms'], result['model'], result['prompt_version'],
             result['threshold'], result['margin_threshold'], json.dumps(result['scores']), int(is_test)))
    return event_id

def history(path=None, include_test=False):
    with connect(path) as conn:
        rows = conn.execute('SELECT * FROM detections ' + ('' if include_test else 'WHERE is_test=0 ') + 'ORDER BY created_at DESC').fetchall()
    return [dict(row) for row in rows]

def clear_test(path=None):
    with connect(path) as conn:
        return conn.execute('DELETE FROM detections WHERE is_test=1').rowcount

def export_csv(rows):
    fields = ['id','created_at','image_id','category','candidate','confidence','status','source','elapsed_ms','model','prompt_version','threshold','margin_threshold','is_test']
    out = io.StringIO(newline='')
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    for row in rows:
        writer.writerow({k: "'"+str(v) if isinstance(v,str) and v.startswith(('=','+','-','@')) else v for k,v in row.items()})
    return out.getvalue().encode('utf-8-sig')
