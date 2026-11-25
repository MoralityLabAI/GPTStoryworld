from itertools import combinations,product
import unittest
from spiral_ln.hypergames_sparse_certificate import decode,first_unique_prefix
from spiral_ln.hypergames_observation_certificate import certify


class SparseCertificateTests(unittest.TestCase):
    def test_matches_exhaustive_small_family(self):
        goals=[sum(1<<i for i in xs) for xs in combinations(range(5),2)]
        for truth in goals:
            for a,b in product(range(32),repeat=2):
                history=[(a,[(a&truth).bit_count()%2]),(b,[(b&truth).bit_count()%2])]
                compatible={p for p in goals if all((m&p).bit_count()%2==y[0] for m,y in history)}
                found=decode(5,1,history,2)
                self.assertEqual(found['status']=='unique',len(compatible)==1)
                witnesses={sum(1<<i for i in xs) for xs in found['outputs'][0]['witness_supports']}
                self.assertTrue(witnesses<=compatible)
                self.assertEqual(len(witnesses),min(2,len(compatible)))

    def test_nonlinear_cardinality_information(self):
        history=[(0b011,[0])]
        self.assertFalse(certify(3,1,history,None,2)['complete_support_forced'])
        self.assertEqual(decode(3,1,history,2)['outputs'][0]['witness_supports'],[[0,1]])
        self.assertEqual(first_unique_prefix(3,1,history+[(0b100,[0])],2),1)

    def test_caps_and_boundaries(self):
        self.assertEqual(decode(512,1,[],6)['status'],'unavailable_enumeration_cap')
        self.assertEqual(decode(1024,2,[],6)['status'],'unavailable_enumeration_cap')
        self.assertEqual(decode(6,1,[],6)['status'],'unique')
        self.assertEqual(first_unique_prefix(6,1,[],6),0)
        self.assertEqual(decode(3,1,[],0)['outputs'][0]['witness_supports'],[[]])
        self.assertEqual(decode(3,1,[(1,[0]),(1,[1])],1)['status'],'inconsistent')
        with self.assertRaises(ValueError):decode(3,1,[(8,[0])],1)
