import tempfile
import unittest
from pathlib import Path

from spiral_ln.hg09_session import run_episode, read_journal, Journal
from spiral_ln.hg09_replay import replay


class ReplayTests(unittest.TestCase):
    def test_replays_saved_response_and_rejects_regraded_trace(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'a.jsonl'
            spec={'task':'HG-02','seed':17,'dimension':140,'horizon':4,'hidden_mode':0}
            run_episode(spec,'test','direct',p,lambda *a:{'answer':'{"action":"abstain"}',
                         'valid_transport':True,'usage':{'input_tokens':11,'output_tokens':5}})
            r=replay(p)
            self.assertTrue(r['replay_verified'])
            self.assertEqual(r['true_utility'],'0')
            self.assertEqual(r['model_calls'],1)
            rows=read_journal(p)
            altered=Path(td)/'altered.jsonl'
            journal=Journal(altered)
            for row in rows:
                row={k:v for k,v in row.items() if k not in ('previous_sha256','record_sha256')}
                if row['type']=='final_grade':row['true_utility']='10'
                journal.write(row)
            journal.close()
            with self.assertRaisesRegex(ValueError,'grade replay'):replay(altered)

    def test_incomplete_request_never_acquires_synthetic_grade(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'interrupted.jsonl'
            journal=Journal(p)
            journal.write({'type':'episode_start','task':'HG-02','seed':17,'dimension':140,
                           'horizon':4,'hidden_mode':0,'model':'test','condition':'direct','effort':'low'})
            journal.write({'type':'request','turn':1,'prompt':'public'})
            journal.write({'type':'response','turn':1,'answer':'','valid_transport':False,'usage':None})
            journal.close()
            result=replay(p)
            self.assertEqual(result['status'],'interrupted')
            self.assertNotIn('true_utility',result)
            self.assertEqual(result['requests_without_reported_usage'],1)

    def test_wrong_rank_release_is_blocked_and_counted_invalid(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'wrong-rank.jsonl'
            spec={'task':'HG-08','seed':202611170801,'dimension':140,'cohort':'core_140',
                  'goal_rank':2,'budget':64}
            run_episode(spec,'test','direct',p,lambda *a:{
                'answer':'{"release_support":[[0,1,2,3,4,5]]}',
                'valid_transport':True,'usage':{'input_tokens':1,'output_tokens':1}})
            result=replay(p)
            self.assertFalse(result['released'])
            self.assertEqual(result['true_utility'],'0')
            self.assertEqual(result['invalid_actions'],1)
            self.assertEqual(result['failure_taxonomy']['invalid_release_rank'],1)


if __name__=='__main__':unittest.main()
