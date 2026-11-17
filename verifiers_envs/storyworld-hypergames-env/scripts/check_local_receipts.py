"""Regenerate and compare HG-01/02/03 source-hashed synthetic receipts."""
import json
from pathlib import Path
from verify_evaluation_hypergames import verify as verify_hg01
from verify_hypergames_single_player import verify as verify_hg02
from verify_hypergames_qwen_eval import verify as verify_hg03

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = (
    ("hg01", verify_hg01, "hg01.json"),
    ("hg02", verify_hg02, "hg02_single_player_v1.json"),
    ("hg03", verify_hg03, "hg03_qwen_preflight_v1.json"),
)

def main():
    for label, verifier, filename in RECEIPTS:
        actual = json.loads(json.dumps(verifier()))
        expected = json.loads((ROOT / "output/evaluation_hypergames" / filename).read_text("utf-8"))
        actual.pop("generated_at_utc", None)
        expected.pop("generated_at_utc", None)
        if actual != expected:
            raise SystemExit(f"{label}: regenerated receipt differs")
        if actual.get("all_passed") is not True:
            raise SystemExit(f"{label}: failed check")
        print(f"{label}: {len(actual['checks'])} checks; receipt identical")

if __name__ == "__main__":
    main()
