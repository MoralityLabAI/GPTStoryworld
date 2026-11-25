import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from spiral_ln.hg09_frontier import ModelSpec, parse_hg02_action, parse_hg08_action, strict_json_answer, hg02_episode, hg08_episode, price_ceiling, call_model, run_cli

M=ModelSpec('fake','openai','gpt-6.1-sol',input_usd_per_m=1,output_usd_per_m=5)

def mocked(spec,prompt,*_):
    obj=json.loads(prompt)
    if obj['task']=='HG-02':
        obs=obj['observation']
        phase=obs['visible_state']['phase']
        if obs['visible_state']['remaining']==4 and phase=='route':a='abstain'
        elif phase=='route':a='audit' if not obs['visible_state']['audited'] else 'route_0'
        elif phase=='verify':a='verify_0'
        elif phase=='authorize':a='authorize_0'
        else:a='publish'
        ans={'action':a}
    else:
        ans={'abstain':True}
    return {'answer':json.dumps(ans),'reasoning_summary':['summary, not raw thought'],
            'reasoning_type':'provider_exposed_summary_or_field',
            'usage':{'input_tokens':100,'output_tokens':20},'latency_s':0.1,'response_id':'mock','finish_reason':'completed'}

class HG09Tests(unittest.TestCase):
    def test_json_exact(self):
        self.assertEqual(strict_json_answer('```json\n{"action":"abstain"}\n```'),{'action':'abstain'})
        for bad in ('blah {"action":"abstain"}', '[1]', '{"action":1,"action":2}', '{invalid}', '"text"'):
            with self.assertRaises(ValueError):strict_json_answer(bad)
    def test_fail_closed_hg02(self):
        for bad in ('{"action":"shortcut","foo":2}', '{"action":"publish"}', 'oops','{"action":3}'):
            self.assertEqual(parse_hg02_action(bad,['abstain','audit']),'abstain')
        self.assertEqual(parse_hg02_action('{"action":"audit"}',['abstain','audit']),'audit')
    def test_hg08_strict(self):
        self.assertEqual(parse_hg08_action('{"query_indices":[1,2]}',140,140),('query',6))
        self.assertEqual(parse_hg08_action('{"release_support":[[1,2,3,4,5,6]]}',140,140)[0],'release')
        for bad in ('{"query_indices":[1,1]}','{"query_indices":[-1]}','{"release_support":[[1,1,1,1,1,1]]}', '{"query_indices":[],"abstain":true}', '{"query_indices":[true]}'):
            self.assertEqual(parse_hg08_action(bad,140,140),('abstain',None))
    def test_model_metadata(self):
        self.assertAlmostEqual(price_ceiling(M,1_000_000,2_000_000),11.0)
        with self.assertRaises(ValueError):ModelSpec('bad name','openai','x')
        with self.assertRaises(ValueError):ModelSpec('good','badprovider','x')
    def test_hg02_no_private_leak(self):
        prompts=[]
        def call(model,prompt,*x):
            prompts.append(prompt)
            return mocked(model,prompt)
        out=hg02_episode(M,10,140,1,4,call)
        self.assertEqual(out['ending'],'abstained')
        self.assertEqual(len(out['turns']),1)
        self.assertNotIn('private_bit',prompts[0])
        self.assertNotIn('hidden_state_reveal',prompts[0])
        self.assertEqual(out['usage']['input_tokens'],100)
    def test_hg08_abstains(self):
        out=hg08_episode(M,202611170801,'core_140',1,4,mocked)
        self.assertEqual(out['query_count'],0)
        self.assertEqual(out['true_utility'],0)
        self.assertEqual(out['false_accept'],0)
    def test_api_openai_response_summary(self):
        raw={'id':'abc','status':'completed','output':[{'type':'reasoning','summary':[{'type':'summary_text','text':'summary only'}]},{'type':'message','content':[{'type':'output_text','text':'{"action":"audit"}'}]}],'usage':{'input_tokens':10,'output_tokens':40}}
        with patch.dict('os.environ',{'OPENAI_API_KEY':'fake'}), patch('spiral_ln.hg09_frontier._request',return_value=raw):
            got=call_model(M,'prompt')
        self.assertEqual(got['reasoning_summary'],['summary only'])
        self.assertEqual(got['answer'],'{"action":"audit"}')
    def test_api_openrouter_reasoning(self):
        model=ModelSpec('router','openrouter','some/model')
        raw={'choices':[{'message':{'content':'{"action":"abstain"}','reasoning':'provider text'}}],'usage':{'prompt_tokens':12,'completion_tokens':5}}
        with patch.dict('os.environ',{'OPENROUTER_API_KEY':'fake'}), patch('spiral_ln.hg09_frontier._request',return_value=raw):
            self.assertEqual(call_model(model,'prompt')['reasoning_summary'],['provider text'])
    def test_api_gemini_summary(self):
        model=ModelSpec('gemini','gemini','gemini-3.0-pro')
        raw={'candidates':[{'content':{'parts':[{'thought':True,'text':'provider summary'},{'text':'{"abstain":true}'}]}}]}
        with patch.dict('os.environ',{'GEMINI_API_KEY':'fake'}),patch('spiral_ln.hg09_frontier._request',return_value=raw):
            got=call_model(model,'prompt')
            self.assertEqual(got['answer'],'{"abstain":true}')
            self.assertEqual(got['reasoning_summary'],['provider summary'])
    def test_api_anthropic_summary(self):
        model=ModelSpec('claude','anthropic','claude-test')
        raw={'content':[{'type':'thinking','thinking':'provider summary'},{'type':'text','text':'{"abstain":true}'}]}
        with patch.dict('os.environ',{'ANTHROPIC_API_KEY':'fake'}),patch('spiral_ln.hg09_frontier._request',return_value=raw):
            got=call_model(model,'prompt')
            self.assertEqual(got['answer'],'{"abstain":true}')
    def test_dry_run_no_credits(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'models.json';p.write_text(json.dumps({'models':[{'tag':'one','provider':'openai','model':'gpt-6.1-sol'}]}))
            self.assertEqual(run_cli(['--config',str(p),'--out',str(Path(d)/'out.json')]),0)
            self.assertFalse((Path(d)/'out.json').exists())
    def test_paid_live_requires_budget(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'models.json';p.write_text(json.dumps({'models':[{'tag':'one','provider':'openai','model':'gpt-6.1-sol'}]}))
            with self.assertRaises(SystemExit):run_cli(['--config',str(p),'--out',str(Path(d)/'out.json'),'--live'])

if __name__=='__main__':unittest.main()

class SummaryTests(unittest.TestCase):
    def test_summary_counts_and_usage(self):
        from spiral_ln.hg09_scores import summarize
        got=summarize({'schema':'HG-09/frontier-crossmodel-v1','results':[
            {'model_tag':'fake','provider':'openai','model':'id','task':'HG-02','true_utility':9,
             'safe_success':True,'false_accept':False,'usage':{'input_tokens':5,'output_tokens':6},'errors':[],
             'turns':[{'format_valid':True,'provider_output':{'reasoning_summary':['summarized']}}]},
            {'model_tag':'fake','provider':'openai','model':'id','task':'HG-02','true_utility':-15,
             'safe_success':False,'false_accept':True,'usage':{'input_tokens':7,'output_tokens':8},'errors':['bad'],
             'turns':[{'format_valid':True,'provider_output':{'reasoning_summary':[]}}]}
        ]})
        self.assertEqual(got[0]['mean_true_utility_valid'],9)
        self.assertEqual(got[0]['false_accepts_valid'],0)
        self.assertEqual(got[0]['episodes_with_errors'],1)
        self.assertEqual(got[0]['reasoning_artifacts'],1)
        self.assertEqual(got[0]['input_tokens'],12)
