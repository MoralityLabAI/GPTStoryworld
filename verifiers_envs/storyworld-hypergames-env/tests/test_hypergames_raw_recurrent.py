"""HG-07 raw input and inference separation, deterministic CPU smoke tests."""
import unittest
from fractions import Fraction as Q
# Legacy exact-CPU workflows intentionally run without neural dependencies.
# The dedicated HG-07 workflow installs NumPy and CPU PyTorch and exercises
# this entire test class; keep older exact-Python suites independent.
try:
    import numpy as np
    from spiral_ln import hypergames_raw_recurrent as h
except ModuleNotFoundError as exc:
    if exc.name not in ("numpy", "torch"):
        raise
    np = h = None


@unittest.skipUnless(h is not None, "HG-07 neural tests require NumPy and PyTorch")
class RawStateTraining(unittest.TestCase):
    def test_goal_and_fragments_six_sparse(self):
        for cohort in h.COHORTS:
            for k in h.RANKS:
                task=h.task_for(2026111771,cohort,k)
                self.assertEqual(len(task.goal_masks),k)
                for goal,fragments in zip(task.goal_masks,task.fragment_masks):
                    self.assertEqual(tuple(m.bit_count() for m in fragments),(2,2,2))
                    self.assertEqual(goal,fragments[0]^fragments[1]^fragments[2])
                    self.assertEqual(goal.bit_count(),6)

    def test_same_goal_for_padding(self):
        a=h.task_for(2026111771,'core_140',2)
        b=h.task_for(2026111771,'padded_512',2)
        self.assertEqual(a.goal_masks,b.goal_masks)
        self.assertEqual(a.fragment_masks,b.fragment_masks)

    def test_native_512_uses_extra_support(self):
        x=h.task_for(2026111771,'native_512',2)
        self.assertTrue(any(mask>>140 for mask in x.goal_masks))

    def test_low_coordinate_sampling_invariance(self):
        for split in ('train','calibration','test'):
            a=h.split_input_masks(2026111771,split,32,140)
            b=h.split_input_masks(2026111771,split,32,512)
            self.assertEqual(a,tuple(x&((1<<140)-1) for x in b))

    def test_fragment_and_goal_data_consistency(self):
        s=h.task_for(2026111771,'core_140',2)
        for split in ('train','calibration','test'):
            data=h.split_data(s,split,32)
            for row in range(32):
                f=data['fragment'][row].reshape(2,3)
                self.assertTrue(np.array_equal(np.mod(f.sum(axis=1),2),data['y'][row]))

    def test_separate_data_splits(self):
        s=h.task_for(2026111771,'core_140',1)
        a=h.split_data(s,'train',128)['masks']
        b=h.split_data(s,'calibration',128)['masks']
        c=h.split_data(s,'test',128)['masks']
        self.assertEqual(len(set((*a,*b,*c))),384)

    def test_all_neural_arms_hold_same_param_shapes(self):
        import torch
        torch.manual_seed(17)
        a=h.RawNet(140,2,False); b=h.RawNet(140,2,True)
        self.assertEqual(sum(x.numel() for x in a.parameters()),sum(x.numel() for x in b.parameters()))
        x=torch.zeros(7,140)
        self.assertEqual(a(x)[0].shape,(7,2))
        self.assertEqual(b(x)[1].shape,(7,6))

    def test_calibration_threshold_and_negative_reward(self):
        z=np.zeros((256,1),dtype=bool)
        y=np.zeros((256,1),dtype=np.float32)
        yes=h.measure_and_gate(z,z,y,y)
        self.assertEqual(yes['true_utility'],'10')
        self.assertEqual(yes['false_accept'],0)
        other=np.ones((256,1),dtype=bool)
        fail=h.measure_and_gate(other,other,y,y)
        self.assertEqual(fail['true_utility'],'0')
        self.assertEqual(fail['release'],0)
        # Fully convincing calibration can still yield an unsafe test release.
        bad=h.measure_and_gate(z,other,y,y)
        self.assertEqual(bad['true_utility'],'-15')
        self.assertEqual(bad['false_accept'],256)

    def test_exact_raw_GF2_upper_bound(self):
        for cohort in h.COHORTS:
            t=h.task_for(2026111771,cohort,2)
            train=h.split_data(t,'train',2048)
            cal=h.split_data(t,'calibration',256)
            test=h.split_data(t,'test',256)
            r=h.f2_reference(t,train,cal,test)
            self.assertEqual(r['f2_rank'],t.dimension)
            self.assertEqual(r['f2_test_correct_if_determined'],256)
            self.assertEqual(r['f2_release'],1)

    def test_uniform_rank_matched_random_baseline(self):
        t=h.task_for(2026111701,'core_140',2)
        train=h.split_data(t,'train',2048)
        cal=h.split_data(t,'calibration',256)
        test=h.split_data(t,'test',256)
        r=h.random_reference(t,512,train,cal,test)
        self.assertEqual(len(r['random_scores']),100)
        self.assertTrue(all(0<=x<=256 for x in r['random_scores']))

    def test_recurrent_task_only_deterministic_smoke(self):
        t=h.task_for(2026111701,'core_140',1)
        train=h.split_data(t,'train',2048)
        cal=h.split_data(t,'calibration',256)
        test=h.split_data(t,'test',256)
        saved=h.STEPS
        try:
            h.STEPS=4
            left=h.train_neural(t,'loop_task',512,train,cal,test)
            right=h.train_neural(t,'loop_task',512,train,cal,test)
            self.assertEqual(left['direct'],right['direct'])
            self.assertEqual(left['train_loss'],right['train_loss'])
        finally:h.STEPS=saved

    def test_true_aux_and_shuffled_control_shapes(self):
        t=h.task_for(2026111701,'core_140',1)
        train=h.split_data(t,'train',2048)
        cal=h.split_data(t,'calibration',256)
        test=h.split_data(t,'test',256)
        saved=h.STEPS
        try:
            h.STEPS=2
            for arm in ('loop_true_fragment_aux','loop_shuffled_fragment_aux'):
                r=h.train_neural(t,arm,512,train,cal,test)
                self.assertEqual(set(r['composed']),{'cal_joint_correct','test_joint_correct','test_bit_correct','release','false_accept','true_utility'})
        finally:h.STEPS=saved

    def test_seed_stable_and_cohort_validation(self):
        self.assertEqual(h.seed_int('x',5),h.seed_int('x',5))
        self.assertNotEqual(h.seed_int('x',5),h.seed_int('x',6))
        with self.assertRaises(ValueError):h.task_for(123,'unknown',1)
        with self.assertRaises(ValueError):h.task_for(123,'core_140',16)

if __name__=='__main__':unittest.main()
