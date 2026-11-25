from fractions import Fraction as F
from io import StringIO
import json
import unittest
from provenance_characters import LAW, CouncilSession, posterior, reaction, transfer
from provenance_session import serve
from verify_provenance_characters import audit


class CouncilTest(unittest.TestCase):
    def test_exact_beliefs_and_copies(self):
        self.assertEqual(sum(w for w, _ in LAW), 1)
        self.assertEqual(posterior({'A':1}), F(5,6))
        self.assertEqual(posterior({'A':1,'B':1,'shared':1}), F(5,6))
        self.assertEqual(posterior({'A':1,'B':1,'shared':0}), F(25,26))
        self.assertEqual(posterior({'A':1,'B':1,'valid_A':0}), F(11,18))
        self.assertEqual(posterior({'A':1,'B':1,'valid_A':0,'shared':1}), F(1,2))
        self.assertEqual(posterior({'A':1,'B':1,'valid_A':0,'shared':0}), F(5,6))

    def test_transfer_is_idempotent_and_consistent(self):
        self.assertEqual(transfer({'A':1}, {'A':1}), {'A':1})
        with self.assertRaises(ValueError): transfer({'A':1}, {'A':0})
        with self.assertRaises(ValueError): transfer({}, {'truth':1})
        with self.assertRaises(ValueError): posterior({'truth':1})
        with self.assertRaises(ValueError): posterior({'A':True})
        with self.assertRaises(ValueError): transfer({'A':1,'B':0}, {'shared':1})

    def test_actors_know_different_things_then_reconcile(self):
        i = next(i for i, (_, x) in enumerate(LAW) if x['A']==1 and x['B']==0 and not x['valid_A'])
        s = CouncilSession(4, i)
        before = s.private_projection()
        self.assertEqual(before['magistrate']['value'], '-2/3')
        self.assertEqual(before['registrar']['value'], '2/3')
        self.assertEqual(reaction(before['magistrate']['evidence']), 'publish_clearance')
        self.assertEqual(reaction(before['registrar']['evidence']), 'publish_accusation')
        s.act('consult'); s.act('seals'); s.act('registry')
        self.assertEqual(s.private_projection()['magistrate'], before['magistrate'])
        self.assertEqual(s.private_projection()['registrar'], before['registrar'])
        s.act('brief')
        after = s.private_projection()
        self.assertEqual(after['magistrate']['value'], '-2/3')
        self.assertEqual(after['registrar']['value'], '-2/3')
        self.assertEqual(after['registrar']['trust_editor'], '1/4')
        self.assertEqual(s.public()['ledger'][-1]['outcome'], 'publish_clearance|publish_clearance')

    def test_private_truth_not_leaked(self):
        i,j = [next(i for i,(_,x) in enumerate(LAW) if x['truth']==h and x['A']==1 and x['B']==1 and x['shared'] and not x['valid_A']) for h in (0,1)]
        a,b = CouncilSession(4,i), CouncilSession(4,j)
        self.assertEqual(a.public(), b.public())
        for q in ('consult','seals','registry','brief','publish_accusation'):
            self.assertEqual(a.act(q),b.act(q))
        self.assertNotEqual(a.grade(), b.grade())

    def test_legal_budget_and_protocol(self):
        s=CouncilSession(2,0); start=s.public()
        with self.assertRaises(ValueError): s.act('brief')
        self.assertEqual(start,s.public())
        sink=StringIO()
        score=serve(s,StringIO('{"action":"consult"}\n{"action":"brief"}\n{"action":"registry"}\n{"action":"defer"}\n'),sink)
        packets=[json.loads(x) for x in sink.getvalue().splitlines()]
        self.assertEqual(packets[-2]['error'],'invalid action')
        self.assertTrue(packets[-1]['terminal']); self.assertNotIn('utility',packets[-1])
        self.assertEqual(score['cost'],2)

    def test_exhaustive_audit(self):
        for b in (2,3,4):
            row=audit(b)
            self.assertGreater(row['world_prefixes'],100)
            self.assertGreater(row['investigation_opportunities'],0)
            self.assertGreaterEqual(F(row['policies']['full']['utility']),F(row['policies']['no_brief']['utility']))


if __name__ == '__main__':
    unittest.main()
