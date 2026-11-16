import json
import unittest
from pathlib import Path

from spiral_ln.hypergames_qwen_analysis import geometry_checks, replay

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'output/evaluation_hypergames/hg03_local_dev_20261116_v1/results.json'


class LocalAnalysisTests(unittest.TestCase):
    def test_exact_padding_transition_closure_and_rank(self):
        geometry = geometry_checks((101,))
        self.assertGreater(geometry[0]['legal_edges_checked'], 100)
        core, padded, native = geometry[0]['layouts']
        self.assertEqual(core['real_gram_diagonal'], padded['real_gram_diagonal'])
        self.assertEqual(core['real_unreduced_gate_rank'], native['real_unreduced_gate_rank'])
        self.assertEqual(native['gate_input_coordinates'], 144)

    def test_rejects_tampered_visible_state_before_decoding(self):
        if not REPORT.is_file():
            self.skipTest('Detailed replay artifact retained locally pending publication approval')
        report = json.loads(REPORT.read_text('utf-8'))
        qwen = next(r for r in report['rows'] if r['policy'] == 'qwen')
        qwen['trace'][0]['observed_state']['visible_state']['remaining'] = 99
        with self.assertRaisesRegex(ValueError, 'visible observation'):
            replay(report)

    def test_rejects_missing_world_instead_of_zero_filling(self):
        if not REPORT.is_file():
            self.skipTest('Detailed replay artifact retained locally pending publication approval')
        report = json.loads(REPORT.read_text('utf-8'))
        report['rows'].pop()
        with self.assertRaisesRegex(ValueError, 'incomplete'):
            replay(report)

    def test_rejects_duplicate_baseline_even_when_count_is_unchanged(self):
        if not REPORT.is_file():
            self.skipTest('Detailed replay artifact retained locally pending publication approval')
        report = json.loads(REPORT.read_text('utf-8'))
        report['rows'][1] = report['rows'][0]
        with self.assertRaisesRegex(ValueError, 'baseline grid'):
            replay(report)


if __name__ == '__main__':
    unittest.main()
