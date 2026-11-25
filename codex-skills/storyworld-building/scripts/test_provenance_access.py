from fractions import Fraction as F
from io import StringIO
import json
import unittest
from provenance_access import AccessSession, LAW, root, legal, grant, step, posterior, evaluate, utility
from provenance_session import serve


class AccessTests(unittest.TestCase):
    def test_law_and_revision(self):
        self.assertEqual(sum(w for w,_ in LAW),1)
        self.assertEqual(posterior((('A',1),('B',0),('shared',0))),F(1,2))
        self.assertEqual(posterior((('A',1),('B',0),('shared',0),('valid_A',0))),F(1,6))

    def test_access_chain_and_refusal(self):
        s=AccessSession(5,0)
        with self.assertRaises(ValueError):s.act('brief')
        with self.assertRaises(ValueError):s.act('registry')
        s.act('apply'); self.assertNotIn('registry',s.legal())
        s.act('seals');s.act('brief');self.assertNotIn('apply',s.legal())
        self.assertNotIn('registry',s.legal())
        t=AccessSession(4,0)
        for q in ('seals','brief','apply','registry'):t.act(q)
        self.assertEqual(t.public()['remaining'],0)
        self.assertEqual(set(t.legal()),{'publish_accusation','publish_clearance','defer'})
        self.assertFalse(grant(F(1,8)));self.assertTrue(grant(F(1,4)))

    def test_actor_local_knowledge(self):
        i=next(i for i,(_,w) in enumerate(LAW) if w['A']==1 and w['B']==0 and not w['shared'] and not w['valid_A'])
        s=AccessSession(5,i)
        s.act('consult');s.act('seals')
        self.assertEqual(s.private_projection()['registrar'],'2/3')
        s.act('brief');self.assertEqual(s.private_projection()['registrar'],'0')
        s.act('apply');s.act('registry')
        self.assertEqual(s.private_projection()['editor'],'-2/3')
        self.assertEqual(s.private_projection()['registrar'],'0')

    def test_packet_privacy_and_terminal(self):
        pair=[next(i for i,(_,w) in enumerate(LAW) if w['truth']==h and w['A']==1 and w['B']==1 and w['shared'] and not w['valid_A'] and w['C']==0) for h in (0,1)]
        a,b=[AccessSession(5,i) for i in pair]
        self.assertEqual(a.public(),b.public())
        for q in ('consult','seals','brief','apply','registry','publish_accusation'):
            self.assertEqual(a.act(q),b.act(q))
        self.assertNotEqual(a.grade(),b.grade())

    def test_jsonl_and_illegal_action(self):
        sink=StringIO();g=serve(AccessSession(4,0),StringIO('{"action":"registry"}\n'+''.join(json.dumps({'action':x})+'\n' for x in ('seals','brief','apply','registry','defer'))),sink)
        messages=[json.loads(x) for x in sink.getvalue().splitlines()]
        self.assertEqual(messages[1]['error'],'invalid action')
        self.assertTrue(messages[-1]['terminal']);self.assertNotIn('utility',messages[-1]);self.assertEqual(g['registry'],1)

    def test_controls_and_budget(self):
        for mode in ('social','blocked','ungated'):
            v=evaluate(root(1,5),'full',mode)
            self.assertEqual(sum(v[:3]),1);self.assertLessEqual(v[3],5)
        self.assertEqual(utility(evaluate(root(1,5),'full','social')),F(25,36))
        self.assertEqual(utility(evaluate(root(1,5),'full','blocked')),F(11,24))
        self.assertEqual(utility(evaluate(root(1,5),'full','ungated')),F(13,18))


if __name__=='__main__':unittest.main()
