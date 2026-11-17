"""Verify exact HG-05 public CPU output and source digests."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
expected=json.loads((ROOT/'output/evaluation_hypergames/hg05_expected_sha256.json').read_text('utf8'))
out=ROOT/'output/evaluation_hypergames/hg05'

for rel,digest in expected['source_sha256'].items():
    actual=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    if actual!=digest:
        raise SystemExit(f'stale source: {rel}: {actual}')
for rel,digest in expected['result_sha256'].items():
    actual=hashlib.sha256((out/rel).read_bytes()).hexdigest()
    if actual!=digest:
        raise SystemExit(f'nonreproducible HG-05 output: {rel}: {actual}')

z=json.loads((out/'hg05_summary_v1.json').read_text('utf8'))
assert z['all_passed'] and z['counts']['seed_arm_rows']==expected['rows']
assert z['counts']['random_base_draws']==expected['random_draws']
assert all(v['passes_20_of_24_gate'] for v in z['registered_direction_counts'].values())
print('HG-05 source hashes, exact CPU replay and registered direction gates reproduced')
