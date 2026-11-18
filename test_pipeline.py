import json
from pathlib import Path
import joblib
import pandas as pd

config = json.loads(Path('config.json').read_text())
metrics = json.loads(Path('artifacts/metrics.json').read_text())

required = {'student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha'}
assert required.issubset(metrics), 'metrics.json is missing fields'
assert metrics['student_id'] == config['student_id'], 'student_id mismatch'

rows = len(pd.read_csv('dataset/train.csv'))
assert metrics['training_rows'] == rows, 'training_rows does not match dataset'
assert 0.5 < metrics['accuracy'] <= 1.0, 'accuracy is out of range'

bundle = joblib.load('artifacts/model.joblib')
sample = pd.DataFrame([{f: 0.0 for f in bundle['features']}])
assert len(bundle['model'].predict(sample)) == 1, 'model cannot predict'

print('All tests passed:', metrics)