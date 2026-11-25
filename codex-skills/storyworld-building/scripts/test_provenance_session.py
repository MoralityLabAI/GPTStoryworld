from fractions import Fraction as F
from io import StringIO
import json
import unittest
from provenance_design_audit import Audit, north_quay
from provenance_session import Session, serve


class SessionTest(unittest.TestCase):
    def test_private_and_public_equivalence(self):
        spec = list(north_quay())[0]
        a, b = Session(spec, 0), Session(spec, 1)
        self.assertEqual(a.public(), b.public())
        self.assertEqual(a.act('inspect_seals'), b.act('inspect_seals'))
        self.assertEqual(a.act('publish_accusation'), b.act('publish_accusation'))
        self.assertNotEqual(a.grade(), b.grade())
        self.assertNotIn('truth', a.public().keys())
        self.assertFalse(a.public()['actions'])

    def test_prerequisites_budget_and_replay(self):
        s = Session(list(north_quay())[1], 0)
        start = s.public()
        with self.assertRaises(ValueError):
            s.act('inspect_seals')
        self.assertEqual(start, s.public())
        s.act('catalogue')
        with self.assertRaises(ValueError):
            s.act('catalogue')
        s.act('inspect_seals')
        self.assertEqual(s.public()['remaining'], 0)
        self.assertEqual(len(s.public()['actions']), 3)
        s.act('defer')
        with self.assertRaises(ValueError):
            s.act('publish_clearance')
        self.assertEqual(s.grade()['cost'], 2)

    def test_full_policy_rollout_matches_oracle(self):
        for spec in north_quay():
            audit = Audit(spec)
            for mode in ('one', 'two', 'macro', 'full'):
                total = [F(0)] * 4
                for i, w in enumerate(audit.weights):
                    s = Session(spec, i)
                    mask = tuple(range(len(audit.w)))
                    used = frozenset()
                    while not s.public()['terminal']:
                        budget = s.public()['remaining']
                        a = audit.choose(mask, used, budget, mode)
                        state = s.act(a)
                        if a in audit.q:
                            outcome = state['ledger'][-1]['outcome']
                            mask = tuple(j for j in mask if audit.w[j]['observations'][a] == outcome)
                            used |= {a}
                    score = s.grade()
                    total = [x + w * score[k] for x, k in zip(total, ('correct', 'false', 'defer', 'cost'))]
                self.assertEqual(tuple(total), audit.evaluate(tuple(range(len(audit.w))), frozenset(), audit.b, mode))

    def test_jsonl_no_grade_and_recovery(self):
        s = Session(list(north_quay())[1], 0)
        out = StringIO()
        grade = serve(s, StringIO('{"action":"inspect_seals"}\n{"action":"catalogue"}\n{"action":"inspect_seals"}\n{"action":"publish_accusation"}\n'), out)
        messages = [json.loads(x) for x in out.getvalue().splitlines()]
        self.assertEqual(messages[1]['error'], 'invalid action')
        self.assertEqual(messages[1]['state'], messages[0])
        self.assertTrue(messages[-1]['terminal'])
        self.assertNotIn('utility', messages[-1])
        self.assertEqual(grade['utility'], 1)

    def test_every_public_history(self):
        # Replay every legal prefix in every latent world. Histories shared by
        # distinct worlds must produce byte-identical player packets.
        count = 0
        for spec in north_quay():
            seen = {}
            for i in range(len(spec['worlds'])):
                def walk(path):
                    nonlocal count
                    s = Session(spec, i)
                    for a in path:
                        s.act(a)
                    v = s.public()
                    key = (tuple(path), tuple((x['query'], x['outcome']) for x in v['ledger']))
                    blob = json.dumps(v, sort_keys=True)
                    self.assertEqual(seen.setdefault(key, blob), blob)
                    count += 1
                    for a in v['actions']:
                        walk(path + [a['id']])
                walk([])
        self.assertGreater(count, 100)


if __name__ == '__main__':
    unittest.main()
