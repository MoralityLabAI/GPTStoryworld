"""Tests for all 3 compiled SweepWeave 0.1.9 storyworlds, quality gates, and Monte Carlo balance."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest

CARBON_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CARBON_DIR.parent
sys.path.insert(0, str(CARBON_DIR / "src"))
sys.path.insert(0, str(REPO_ROOT / "codex-skills" / "storyworld-building" / "scripts"))

from carbon_hypergames.storyworld_compiler import write_compiled_world_bundle  # noqa: E402
from carbon_hypergames.worlds_spec import WORLD_SPECS  # noqa: E402
from monte_carlo_rehearsal import run_monte_carlo  # noqa: E402
from storyworld_quality_gate import evaluate_storyworld  # noqa: E402
from sweepweave_validator import validate_storyworld  # noqa: E402


class TestStoryworldsAndQualityGates(unittest.TestCase):
    def test_all_three_storyworlds_pass_strict_gates_and_rehearsal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            for world_id in WORLD_SPECS:
                paths = write_compiled_world_bundle(world_id, tmp_root / world_id)
                sw_path = paths["storyworld_json"]
                errs = validate_storyworld(str(sw_path))
                self.assertEqual(errs, [], f"{world_id} validator errors: {errs}")

                data = json.loads(sw_path.read_text(encoding="utf-8"))
                q_rep = evaluate_storyworld(data, errs)
                self.assertTrue(
                    q_rep["pass"],
                    f"{world_id} failed strict quality checks: {q_rep['failures']}",
                )

                mc = run_monte_carlo(data, num_runs=2000, seed=42)
                self.assertEqual(mc["dead_ends"], 0)
                secret_pct = 100.0 * sum(mc["secret_hits"].values()) / 2000.0
                self.assertGreater(secret_pct, 5.0, f"{world_id} secret reachability {secret_pct}% <= 5%")

                swmd_text = paths["swmd_min"].read_text(encoding="utf-8")
                self.assertTrue(swmd_text.startswith("---\n"))
                self.assertIn("endings:", swmd_text)
                self.assertIn("state_variables:", swmd_text)


if __name__ == "__main__":
    unittest.main()
