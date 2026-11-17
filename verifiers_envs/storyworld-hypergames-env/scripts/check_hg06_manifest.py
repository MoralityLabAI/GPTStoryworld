"""Check regenerated HG-06 public CPU evidence against committed SHA-256 receipts.

Never touches the private HG-03 manifest. Suitable for GitHub Actions.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EXPECTED=ROOT/'output/evaluation_hypergames/hg06_compact_receipt_v1.json'
MATH_EXPECTED=ROOT/'output/evaluation_hypergames/hg06_math_v1.json'

def _sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    folder=args.out if args.out.is_absolute() else ROOT/args.out
    expected=json.loads(EXPECTED.read_text('utf8'))
    generated=json.loads((folder/'hg06_compact_receipt_v1.json').read_text('utf8'))
    if generated!=expected:
        raise SystemExit('regenerated HG-06 receipt differs from committed version')
    if not expected['all_passed'] or any(x is not True for x in expected['checks'].values()):
        raise SystemExit('registered HG-06 integrity checks failed')
    for path,digest in expected['source_sha256'].items():
        if _sha(ROOT/path)!=digest:
            raise SystemExit(f'source SHA-256 mismatch: {path}')
    for filename,digest in expected['seed_csv_sha256'].items():
        if _sha(folder/filename)!=digest:
            raise SystemExit(f'per-seed CSV SHA-256 mismatch: {filename}')
    math=json.loads(MATH_EXPECTED.read_text('utf8'))
    if not math['all_passed']:
        raise SystemExit('HG-06 math verifier has failing checks')
    for path,digest in math['source_sha256'].items():
        if _sha(ROOT/path)!=digest:
            raise SystemExit(f'HG-06 math source SHA-256 mismatch: {path}')
    print(f"HG-06: {generated['counts']['rows']} public seed-arm records, {len(expected['seed_csv_sha256'])} source-matched CSVs, math source hashes match")
    return 0

if __name__=='__main__':raise SystemExit(main())
