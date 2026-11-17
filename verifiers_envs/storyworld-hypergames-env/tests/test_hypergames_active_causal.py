"""Public, pick-time-only HG-08 causal intervention mechanic checks."""
import json
import unittest
from spiral_ln.hypergames_active_causal import (
    SEEDS, COHORTS, RANKS, POLICIES, BUDGETS, N_TEST,
    make_problem, _private_goal, discover, grade, InterventionOracle,
    independent_test_masks, evaluate, run, summarize, symbolic_recurrent_code,
)
from spiral_ln.hypergames_active_neural import choose_support, data, RawNet, NEURAL_ARMS


class ActiveMechanicTests(unittest.TestCase):
    def test_padded_worlds_same_targets(self):
        for seed in SEEDS[:3]:
            for k in RANKS:
                masks=tuple(_private_goal(make_problem(seed,c,k)) for c in COHORTS[:2])
                self.assertEqual(masks[0],masks[1])
                self.assertEqual(masks[0],_private_goal(make_problem(seed,'padded_1024',k)))

    def test_distinct_goal_support_and_width(self):
        for c in COHORTS:
            for k in RANKS:
                p=make_problem(SEEDS[0],c,k)
                goal=_private_goal(p)
                self.assertEqual([mask.bit_count() for mask in goal],[6]*k)
                if k==2:self.assertEqual(goal[0]&goal[1],0)

    def test_padded_inputs_share_low_bits(self):
        a=independent_test_masks(make_problem(SEEDS[0],'core_140',1))
        b=independent_test_masks(make_problem(SEEDS[0],'padded_512',1))
        c=independent_test_masks(make_problem(SEEDS[0],'padded_1024',1))
        self.assertEqual(a,tuple(z&((1<<140)-1) for z in b))
        self.assertEqual(a,tuple(z&((1<<140)-1) for z in c))

    def test_intervention_budget_and_no_future_fields(self):
        p=make_problem(SEEDS[0],'core_140',1)
        o=InterventionOracle(p,2)
        self.assertEqual(len(o.query(0)),1)
        self.assertEqual(len(o.query(1)),1)
        with self.assertRaises(Exception):o.query(2)
        self.assertEqual(o.calls,2)
        self.assertNotIn('goal_mask',json.dumps(o.transcript))

    def test_zero_budget_abstention(self):
        p=make_problem(SEEDS[0],'core_140',2)
        for policy in POLICIES:
            z=discover(p,0,policy)
            self.assertEqual(z.queries,0)
            self.assertFalse(z.completed)
            self.assertEqual(grade(p,z)['true_utility'],'0')

    def test_all_policies_respect_query_cap(self):
        p=make_problem(SEEDS[0],'native_1024',2)
        for b in (1,10,64,128):
            for arm in POLICIES:
                z=discover(p,b,arm)
                self.assertLessEqual(z.queries,b)
                self.assertEqual(len(z.transcript),z.queries)
                if z.completed:self.assertEqual(grade(p,z)['test_correct'],N_TEST)

    def test_completed_sparse_support_exact(self):
        for cohort in COHORTS:
            for k in RANKS:
                p=make_problem(SEEDS[0],cohort,k)
                z=discover(p,512,'adaptive_hash')
                self.assertTrue(z.completed)
                self.assertEqual(tuple(sum(1<<i for i in row) for row in z.known),_private_goal(p))
                self.assertEqual(grade(p,z)['false_accept'],0)

    def test_random_singleton_exhaustive(self):
        p=make_problem(SEEDS[0],'core_140',2)
        z=discover(p,140,'random_singletons')
        self.assertTrue(z.completed)
        self.assertLessEqual(z.queries,140)

    def test_fixed_partition_never_miraculously_recovers(self):
        p=make_problem(SEEDS[0],'native_512',2)
        z=discover(p,512,'fixed_partition')
        self.assertFalse(z.completed)
        self.assertEqual(grade(p,z)['false_accept'],0)

    def test_progressive_budget_prefix(self):
        p=make_problem(SEEDS[0],'native_1024',2)
        for arm in POLICIES:
            a=discover(p,64,arm)
            b=discover(p,256,arm)
            self.assertEqual(a.transcript,b.transcript[:len(a.transcript)])

    def test_group_and_singleton_use_same_oracle(self):
        p=make_problem(SEEDS[0],'native_512',1)
        m=_private_goal(p)[0]
        o=InterventionOracle(p,100)
        for mask in (0,1,3,5,255,(1<<512)-1):
            self.assertEqual(o.query(mask)[0],(m&mask).bit_count()&1)

    def test_random_dense_full_rank_solver(self):
        p=make_problem(SEEDS[0],'core_140',2)
        z=discover(p,256,'random_dense')
        self.assertTrue(z.completed)
        self.assertEqual(tuple(sum(1<<i for i in row) for row in z.known),_private_goal(p))

    def test_registration_grid_size(self):
        subset=run(seeds=SEEDS[:1],cohorts=COHORTS[:1],ranks=RANKS[:1],budgets=(64,))
        self.assertEqual(len(subset),len(POLICIES))
        self.assertEqual({r['budget'] for r in subset},{64})

    def test_symbolic_recurrent_xor_matches_direct_parity(self):
        for cohort in COHORTS:
            p=make_problem(SEEDS[0],cohort,2)
            z=discover(p,512,'adaptive_hash')
            self.assertTrue(z.completed)
            for state in independent_test_masks(p)[:24]:
                expected=tuple((state&m).bit_count()&1 for m in _private_goal(p))
                self.assertEqual(symbolic_recurrent_code(state,z.known,p.dimension),expected)

    def test_neural_support_selection_not_test_dependent(self):
        p=make_problem(SEEDS[0],'core_140',1)
        causal,complete,q=choose_support(p,'causal_masked_loop')
        privileged,_,_=choose_support(p,'privileged_true_support_masked_loop')
        self.assertTrue(complete)
        self.assertEqual(causal,privileged)
        self.assertGreater(q,0)
        self.assertEqual(len(choose_support(p,'random_six_masked_loop')[0]),6)

    def test_neural_data_split_shape_and_labels(self):
        p=make_problem(SEEDS[0],'native_512',1)
        x,y=data(p.seed,p.dimension,_private_goal(p)[0],'train',16)
        self.assertEqual(x.shape,(16,512))
        self.assertEqual(y.shape,(16,1))
        self.assertTrue(set(x.flat)=={-1,1})

    def test_neural_arms_identical_parameter_shapes(self):
        p=make_problem(SEEDS[0],'core_140',1)
        model=RawNet(p.dimension,1)
        n=sum(v.numel() for v in model.parameters())
        self.assertGreater(n,0)
        self.assertEqual(len(NEURAL_ARMS),4)

    def test_invalid_problem_rejected(self):
        with self.assertRaises(ValueError):make_problem(SEEDS[0],'wrong',1)
        with self.assertRaises(ValueError):make_problem(SEEDS[0],'core_140',0)
        with self.assertRaises(ValueError):discover(make_problem(SEEDS[0],'core_140',1),10,'unknown')
        with self.assertRaises(ValueError):InterventionOracle(make_problem(SEEDS[0],'core_140',1),-1)


if __name__=='__main__':unittest.main()
