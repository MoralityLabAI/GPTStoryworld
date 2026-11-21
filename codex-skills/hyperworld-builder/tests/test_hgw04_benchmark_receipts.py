"""HGW-04 paired model-eval manifests and equal-root calibration tests."""
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from benchmark_receipts import audit, SCHEMA


def example():
    return json.loads((ROOT / "fixtures" / "hgw04_policy_development.json").read_text())


class BenchmarkReceiptTests(unittest.TestCase):
    def test_export_root_clusters_and_safety_gates(self):
        report = audit(example())
        self.assertEqual(report["schema"], SCHEMA)
        self.assertEqual((report["units"], report["cases"]), (4, 8))
        manifest = report["fsi_01_manifest"]
        self.assertFalse(manifest["sealed_readout"])
        self.assertEqual({row["cluster_id"] for row in manifest["cases"]},
                         {"dev-root-a", "dev-root-b", "dev-root-c", "dev-root-d"})
        self.assertEqual(manifest["cases"][0]["candidate"], 0)  # unsafe action fails
        self.assertEqual(report, audit(example()))
        self.assertIn("confirmation blocked", report["evidence_class"])

    def test_equal_root_calibration_and_invalid_inputs(self):
        report = audit(example())
        self.assertEqual(report["per_arm"]["candidate"]["brier_macro_mean"], "3/16")
        d = example()
        d["paired_rows"][1]["case_id"] = d["paired_rows"][0]["case_id"]
        with self.assertRaisesRegex(ValueError, "reused"):
            audit(d)
        d = example()
        d["paired_rows"][0]["candidate"]["belief_probability"] = "6/5"
        with self.assertRaisesRegex(ValueError, "probability"):
            audit(d)
        d = example()
        d["source_locks"]["generator_sha256"] = "unverified"
        with self.assertRaisesRegex(ValueError, "64 hex"):
            audit(d)


if __name__ == "__main__":
    unittest.main()
