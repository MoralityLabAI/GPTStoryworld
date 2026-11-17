from itertools import combinations,product
import unittest
from spiral_ln.hypergames_observation_certificate import certify, earliest_certificate


def mask(xs):return sum(1 << i for i in xs)


def enumerated_small_domain_certificate_has_no_false_accept():
    # Enumerate all 2-sparse goals in d=5 and all pairs of group queries.
    supports=[mask(xs) for xs in combinations(range(5),2)]
    for truth in supports:
        for a,b in product(range(32),repeat=2):
            history=[(a,[(a & truth).bit_count()%2]),(b,[(b & truth).bit_count()%2])]
            compatible=[p for p in supports if all((q&p).bit_count()%2==y[0] for q,y in history)]
            result=certify(5,1,history,[truth],2)
            if result['release_certified_by_public_transcript']:
                assert compatible==[truth]


def inferred_singleton_without_direct_singleton_probe():
    # The complement of the observed zero pair is positive by known odd weight.
    result=certify(3,1,[(0b011,[0])],[0b100],1)
    assert result['release_certified_by_public_transcript']
    assert result['linearly_forced_positive_counts']==[1]
    assert not certify(3,1,[],[0b100],1)['release_certified_by_public_transcript']


def multioutput_and_invalid_claims():
    history=[(1,[1,0]),(2,[0,1])]
    assert certify(3,2,history,[1,2],1)['release_certified_by_public_transcript']
    assert not certify(3,2,history,[2,1],1)['claim_matches_all_observed_deltas']
    for history in ([(1,[0]),(1,[1])],[(8,[0])]):
        try:certify(3,1,history,[1],1)
        except ValueError:pass
        else:raise AssertionError('invalid equations accepted')


class CertificateTests(unittest.TestCase):
    def test_enumerated_domain(self):enumerated_small_domain_certificate_has_no_false_accept()
    def test_inferred_positive(self):inferred_singleton_without_direct_singleton_probe()
    def test_multioutput(self):multioutput_and_invalid_claims()
    def test_earliest_prefix(self):
        self.assertEqual(earliest_certificate(3,1,[(0b011,[0]),(0b111,[1])],1),1)
        self.assertIsNone(earliest_certificate(3,1,[],1))
        self.assertEqual(earliest_certificate(5,1,[(1,[1]),(2,[1])],2),2)
