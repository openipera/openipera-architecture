"""Independent oracles, mutations and committed-Git integration checks."""
import copy
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from smv import Denied, derive, load_registry, read_json, render


def command(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True, capture_output=True).stdout.decode().strip()


def commit(repo):
    command(repo, 'add', '.')
    command(repo, '-c', 'user.name=POC-04 Test', '-c', 'user.email=poc03@example.invalid',
            '-c', 'commit.gpgsign=false', 'commit', '-qm', 'Test snapshot')
    return command(repo, 'rev-parse', 'HEAD')


def fixture_repo(path):
    command(path, 'init', '-q')
    shutil.copytree(ROOT / 'automation', path / 'poc-04/automation')
    commit(path)


def edge_set(dag):
    return {(e['source'], e['target']) for e in dag['edges']}


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.repo = Path(cls.temp.name)
        fixture_repo(cls.repo)
        cls.registry = load_registry(cls.repo)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.model = read_json((ROOT / 'model/sm-dag.json').read_bytes())
        self.cards = read_json((ROOT / 'model/lifecycle-cards.json').read_bytes())

    def lc(self, nid):
        return next(c for c in self.cards if c['node_id'] == nid)

    def run_model(self):
        return derive(self.model, self.cards, self.registry)

    def denied(self, code):
        with self.assertRaises(Denied) as exc:
            self.run_model()
        self.assertEqual(exc.exception.diagnostic['code'], code, exc.exception.diagnostic)

    def test_baseline_independent_oracle(self):
        dag = self.run_model()
        oracle = read_json((ROOT / 'tests/oracle.json').read_bytes())
        self.assertEqual(edge_set(dag), {tuple(e) for e in oracle['edges']})
        self.assertEqual(dag['layers'], oracle['layers'])
        self.assertEqual({n['node_id'] for n in dag['nodes']}, set(oracle['nodes']))
        self.assertIn('flowchart TD', render(dag))
        self.assertEqual(len([n for n in dag['nodes'] if n['role'] == 'action']), 11)

    def test_lc_only_mutation(self):
        before = self.run_model(); model = copy.deepcopy(self.model); registry = copy.deepcopy(self.registry)
        original = copy.deepcopy(self.cards)
        runtime_hash = hashlib.sha256((ROOT/'runtime/smv.py').read_bytes()).hexdigest()
        self.lc('register-ci')['service_dependencies'] = ['cyberark']
        after = self.run_model()
        self.assertEqual(edge_set(after) - edge_set(before), {('cyberark','register-ci'), ('cyberark','an-register-ci')})
        self.assertEqual(edge_set(before) - edge_set(after), {('validate','register-ci'), ('validate','an-register-ci')})
        self.assertNotEqual(before['layers'], after['layers'])
        self.assertEqual(self.model, model); self.assertEqual(self.registry, registry)
        self.assertEqual(sum(a != b for a,b in zip(original, self.cards)), 1)
        self.assertEqual(runtime_hash, hashlib.sha256((ROOT/'runtime/smv.py').read_bytes()).hexdigest())

    def test_structure_and_lc_mutation(self):
        before = self.run_model(); cards = copy.deepcopy(self.cards)
        self.model['nodes'].append(dict(node_id='an-audit', name='Additional audit', node_type='atomic', lc_id='lc-audit'))
        self.model['decomposition'].append(['cmdb', 'an-audit'])
        self.cards.append(dict(self.lc('an-register-ci'), node_id='an-audit', lc_id='lc-audit'))
        after = self.run_model()
        self.assertEqual(edge_set(after) - edge_set(before), {('an-audit','cmdb')})
        self.assertEqual(edge_set(before) - edge_set(after), set())
        self.assertEqual(self.cards[:-1], cards)
        # UUID reuse by multiple ANs is valid; uniqueness belongs to registry records.
        self.assertEqual(next(n for n in after['nodes'] if n['node_id']=='an-audit')['architectural_paths'], [['gpc','cmdb','an-audit']])

    def test_shuffling_is_invariant(self):
        before = self.run_model(); rng=random.Random(3)
        rng.shuffle(self.model['nodes']); rng.shuffle(self.model['decomposition']); rng.shuffle(self.cards)
        for c in self.cards: rng.shuffle(c['service_dependencies'])
        self.assertEqual(before, self.run_model())

    def test_generic_names(self):
        ids = {n['node_id']: 'opaque-'+str(i) for i,n in enumerate(self.model['nodes'])}
        before = self.run_model()
        for n in self.model['nodes']:
            n.update(node_id=ids[n['node_id']], name='Same friendly name', lc_id='card-'+n['lc_id'])
        self.model['decomposition'] = [[ids[a],ids[b]] for a,b in self.model['decomposition']]
        for c in self.cards:
            c.update(node_id=ids[c['node_id']], lc_id='card-'+c['lc_id'], service_dependencies=[ids[d] for d in c['service_dependencies']])
            if c['automation_name']: c['automation_name']='Same automation name'
        self.assertEqual(edge_set(self.run_model()), {(ids[a],ids[b]) for a,b in edge_set(before)})

    def test_missing_lc(self):
        self.cards.remove(self.lc('an-disk')); self.denied('MISSING_LC')

    def test_mismatch(self):
        self.lc('an-disk')['node_id']='wrong'; self.denied('LC_NODE_MISMATCH')

    def test_missing_dependency(self):
        self.lc('boot')['service_dependencies']=['absent']; self.denied('MISSING_DEPENDENCY')

    def test_atomic_dependency_target(self):
        self.lc('boot')['service_dependencies']=['an-disk']; self.denied('NON_SERVICE_DEPENDENCY')

    def test_forward_reverse_classification(self):
        findings={(f['source'],f['target']):f['status'] for f in self.run_model()['findings']}
        self.assertEqual(findings['gpc','compute'],'CORROBORATED')
        self.assertEqual(findings['gpc','vm'],'UNCORROBORATED')
        self.assertEqual(findings['vm','storage'],'UNMODELED')
        self.assertNotIn(('storage','domain'),findings)  # Neither source asserts it.

    def test_corroboration_of_direct_and_transitive_decomposition(self):
        self.lc('gpc')['service_dependencies'].append('vm')
        result=self.run_model()
        self.assertEqual(result['status'],'VALID')
        self.assertIn(dict(source='gpc',target='vm',status='CORROBORATED',sm_dag=True,lc=True),result['findings'])

    def test_policy_is_separate_from_model_validity(self):
        before=copy.deepcopy((self.model,self.cards,self.registry))
        permissive=self.run_model()
        self.assertTrue(permissive['model_valid'])
        self.assertEqual(permissive['model_agreement'],'DISCREPANCIES')
        blocked=derive(self.model,self.cards,self.registry,{'block_on':['UNMODELED']})
        self.assertEqual(blocked['status'],'DENIED')
        self.assertTrue(blocked['model_valid'])
        self.assertEqual(blocked['diagnostics'][0]['code'],'POLICY_BLOCK')
        self.assertNotIn('nodes',blocked)
        self.assertEqual(before,(self.model,self.cards,self.registry))
        self.assertEqual(edge_set(permissive),edge_set(derive(self.model,self.cards,self.registry,{'block_on':[]})))

    def test_block_selected_class_only(self):
        self.assertEqual(derive(self.model,self.cards,self.registry,{'block_on':['UNCORROBORATED']})['status'],'DENIED')
        self.lc('vm')['service_dependencies']=['cpu','memory']
        self.assertEqual(derive(self.model,self.cards,self.registry,{'block_on':['UNMODELED']})['status'],'DENIED')
        self.assertEqual(self.run_model()['status'],'VALID')

    def test_policy_schema(self):
        for policy in ({'block_on':['CORROBORATED']},{'block_on':['UNMODELED','UNMODELED']},
                       {'block_on':'UNMODELED'}, {'block_on':[{}]}, {'other':[]}):
            with self.subTest(policy=policy), self.assertRaises(Denied) as exc:
                derive(self.model,self.cards,self.registry,policy)
            self.assertEqual(exc.exception.diagnostic['code'],'POLICY') if 'block_on' in policy else self.assertEqual(exc.exception.diagnostic['code'],'SCHEMA')

    def test_lc_mutation_changes_finding_and_graph(self):
        before=self.run_model()
        self.lc('register-ci')['service_dependencies']=['cyberark']
        after=self.run_model()
        self.assertNotEqual(edge_set(before),edge_set(after))
        self.assertIn(dict(source='register-ci',target='cyberark',status='UNMODELED',sm_dag=False,lc=True),after['findings'])

    def test_structure_mutation_changes_finding(self):
        before=self.run_model()
        self.model['decomposition'].append(['compute','storage'])
        after=self.run_model()
        self.assertNotEqual(edge_set(before),edge_set(after))
        self.assertIn(dict(source='compute',target='storage',status='UNCORROBORATED',sm_dag=True,lc=False),after['findings'])

    def test_duplicate_node(self):
        self.model['nodes'].append(copy.deepcopy(self.model['nodes'][0])); self.denied('DUPLICATE_NODE_ID')

    def test_duplicate_lc(self):
        self.cards.append(copy.deepcopy(self.cards[0])); self.denied('DUPLICATE_LC_ID')

    def test_duplicate_lc_reference(self):
        self.model['nodes'][1]['lc_id']=self.model['nodes'][0]['lc_id']; self.denied('DUPLICATE_LC_REFERENCE')

    def test_duplicate_lc_owner(self):
        self.cards.append(dict(self.cards[0], lc_id='extra')); self.denied('DUPLICATE_LC_OWNER')

    def test_orphan_lc(self):
        self.cards.append(dict(self.cards[0],lc_id='extra',node_id='extra')); self.denied('ORPHAN_LC')

    def test_dependency_cycle(self):
        self.lc('storage')['service_dependencies']=['vm']; self.denied('SERVICE_DEPENDENCY_CYCLE')

    def test_combined_cycle(self):
        self.lc('boot')['service_dependencies']=['gpc']; self.denied('REALIZATION_CYCLE')

    def test_no_binding(self):
        self.lc('an-disk').update(automation_name=None,automation_id=None); self.denied('ATOMIC_BINDING')

    def test_missing_identity(self):
        self.lc('an-disk')['automation_id']=None; self.denied('ATOMIC_BINDING')

    def test_missing_name(self):
        self.lc('an-disk')['automation_name']=None; self.denied('ATOMIC_BINDING')

    def test_bad_uuid(self):
        for value in ('not-a-uuid', 42, '', 'a'*32):
            with self.subTest(value=value):
                self.lc('an-disk')['automation_id']=value; self.denied('INVALID_UUID')

    def test_unresolved_valid_uuid(self):
        self.lc('an-disk')['automation_id']='11111111-2222-3333-4444-555555555555'
        self.denied('UNRESOLVED_AUTOMATION')

    def test_service_binding(self):
        for name, uid in [('bad',None),(None,self.lc('an-disk')['automation_id']),('bad',self.lc('an-disk')['automation_id'])]:
            with self.subTest(name=name,uid=uid):
                self.lc('storage').update(automation_name=name,automation_id=uid); self.denied('SERVICE_BINDING')

    def test_atomic_dependencies(self):
        self.lc('an-disk')['service_dependencies']=['network']; self.denied('ATOMIC_DEPENDENCIES')

    def test_atomic_children(self):
        self.model['decomposition'].append(['an-disk','an-ip']); self.denied('ATOMIC_CHILDREN')

    def test_decomposition_cycle(self):
        self.model['decomposition'].append(['vm','compute']); self.denied('DECOMPOSITION_CYCLE')

    def test_unknown_child(self):
        self.model['decomposition'].append(['vm','missing']); self.denied('MISSING_NODE')

    def test_duplicate_edge(self):
        self.model['decomposition'].append(self.model['decomposition'][0]); self.denied('DUPLICATE_EDGE')

    def test_duplicate_dependency(self):
        self.lc('boot')['service_dependencies']=['vm','vm']; self.denied('DUPLICATE_DEPENDENCY')

    def test_unknown_fields_and_missing_keys(self):
        self.model['nodes'][0]['execute_after']='storage'; self.denied('SCHEMA')
        del self.model['nodes'][0]['execute_after']; del self.cards[0]['automation_id']; self.denied('SCHEMA')

    def test_empty_service(self):
        self.model['decomposition']=[e for e in self.model['decomposition'] if e[0]!='storage']
        self.denied('EMPTY_SERVICE')

    def test_multiple_parents(self):
        self.model['decomposition'].append(['security','storage'])
        n=next(n for n in self.run_model()['nodes'] if n['node_id']=='an-disk')
        self.assertEqual(n['architectural_paths'], [['gpc','security','storage','an-disk'],['gpc','storage','an-disk']])

    def test_no_input_repair(self):
        self.lc('boot')['service_dependencies']=['gpc']
        before = copy.deepcopy((self.model,self.cards,self.registry))
        self.denied('REALIZATION_CYCLE')
        self.assertEqual(before,(self.model,self.cards,self.registry))

    def test_json_duplicate_keys(self):
        with self.assertRaises(Denied) as exc: read_json('{"x":1,"x":2}')
        self.assertEqual(exc.exception.diagnostic['code'],'DUPLICATE_JSON_KEY')


class GitTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.repo=Path(self.temp.name); fixture_repo(self.repo)
        self.records=self.repo/'poc-04/automation/records'
        self.record=next(self.records.glob('*.json'))

    def test_binding_mutation_and_snapshot_isolation(self):
        first=load_registry(self.repo); old=command(self.repo,'rev-parse','HEAD')
        model=read_json((ROOT/'model/sm-dag.json').read_bytes()); cards=read_json((ROOT/'model/lifecycle-cards.json').read_bytes())
        inputs=copy.deepcopy((model,cards)); before=derive(model,cards,first)
        record=read_json(self.record.read_bytes()); uid=record['automation_id']
        replacement='poc-04/automation/artifacts/replacement.py'
        (self.repo/replacement).write_text('print("replacement demo implementation")\n')
        record['artifact_path']=replacement; self.record.write_text(json.dumps(record))
        self.assertEqual(first,load_registry(self.repo))  # Dirty or untracked is not authority.
        command(self.repo,'add','.')
        self.assertEqual(first,load_registry(self.repo))  # Staging is not a commit either.
        commit(self.repo); second=load_registry(self.repo); after=derive(model,cards,second)
        self.assertEqual(first,load_registry(self.repo,old))
        self.assertEqual(set(first),set(second)); self.assertEqual(edge_set(before),edge_set(after))
        self.assertNotEqual(first[uid]['artifact_sha256'],second[uid]['artifact_sha256'])
        self.assertEqual(second[uid]['artifact_path'],replacement); self.assertEqual(inputs,(model,cards))
        self.assertEqual([(n['node_id'],n.get('automation')) for n in before['nodes']],
                         [(n['node_id'],n.get('automation')) for n in after['nodes']])
        self.assertNotIn('artifact_path', next(n['automation'] for n in after['nodes'] if n['node_id']=='an-disk'))

    def test_duplicate_registry_uuid(self):
        (self.records/'duplicate.json').write_bytes(self.record.read_bytes()); commit(self.repo)
        with self.assertRaises(Denied) as exc:load_registry(self.repo)
        self.assertEqual(exc.exception.diagnostic['code'],'DUPLICATE_AUTOMATION_ID')

    def test_missing_committed_artifact(self):
        record=read_json(self.record.read_bytes()); (self.repo/record['artifact_path']).unlink(); commit(self.repo)
        with self.assertRaises(Denied) as exc:load_registry(self.repo)
        self.assertEqual(exc.exception.diagnostic['code'],'MISSING_ARTIFACT')

    def test_symlink_is_not_automation(self):
        record=read_json(self.record.read_bytes()); p=self.repo/record['artifact_path'];p.unlink();p.symlink_to('/etc/passwd');commit(self.repo)
        with self.assertRaises(Denied) as exc:load_registry(self.repo)
        self.assertEqual(exc.exception.diagnostic['code'],'MISSING_ARTIFACT')

    def test_cli_valid_denied_and_fresh_output(self):
        base=[sys.executable,str(ROOT/'runtime/smv.py'),'--model',str(ROOT/'model/sm-dag.json'),
              '--repo',str(self.repo)]
        out=self.repo/'valid'
        run=subprocess.run(base+['--lcs',str(ROOT/'model/lifecycle-cards.json'),'--out',str(out)],capture_output=True)
        self.assertEqual(run.returncode,0,run.stderr); self.assertEqual(read_json((out/'result.json').read_bytes())['status'],'VALID')
        blocked=self.repo/'blocked'
        run=subprocess.run(base+['--lcs',str(ROOT/'model/lifecycle-cards.json'),
                                 '--policy',str(ROOT/'model/policy-block-unmodeled.json'),'--out',str(blocked)],capture_output=True)
        self.assertEqual(run.returncode,2)
        result=read_json((blocked/'result.json').read_bytes())
        self.assertTrue(result['model_valid']);self.assertEqual(result['diagnostics'][0]['code'],'POLICY_BLOCK')
        self.assertNotIn('nodes',result)
        cards=read_json((ROOT/'model/lifecycle-cards.json').read_bytes())
        next(c for c in cards if c['node_id']=='an-disk')['automation_id']='11111111-2222-3333-4444-555555555555'
        bad=self.repo/'bad.json';bad.write_text(json.dumps(cards));denied=self.repo/'denied'
        run=subprocess.run(base+['--lcs',str(bad),'--out',str(denied)],capture_output=True)
        self.assertEqual(run.returncode,2);result=read_json((denied/'result.json').read_bytes())
        self.assertEqual(result['diagnostics'][0]['code'],'UNRESOLVED_AUTOMATION');self.assertNotIn('nodes',result)
        run=subprocess.run(base+['--lcs',str(bad),'--out',str(out)],capture_output=True)
        self.assertNotEqual(run.returncode,0)
        self.assertEqual(read_json((out/'result.json').read_bytes())['status'],'VALID')


if __name__ == '__main__':
    unittest.main()
