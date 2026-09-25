"""Preserve reproducible mutation evidence from isolated committed Git fixtures."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

from test_smv import ROOT, command, commit, fixture_repo, edge_set
from smv import Denied, derive, load_registry, read_json, render


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args(); args.out.mkdir(parents=True,exist_ok=False)
    model=read_json((ROOT/'model/sm-dag.json').read_bytes())
    cards=read_json((ROOT/'model/lifecycle-cards.json').read_bytes())
    fingerprints={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
                  for directory in ('runtime','model','automation') for p in sorted((ROOT/directory).rglob('*'))
                  if p.is_file() and '__pycache__' not in p.parts}
    records=[]
    with tempfile.TemporaryDirectory() as folder:
        repo=Path(folder); fixture_repo(repo)
        # Save the Git snapshots, including the replacement implementation, as a bundle.
        def run(name,m,c,policy=None):
            registry=load_registry(repo)
            try: result=derive(m,c,registry,policy)
            except Denied as exc: result=dict(status='DENIED',diagnostics=[exc.diagnostic])
            target=args.out/name; target.mkdir()
            save(target/'sm-dag.json',m);save(target/'lifecycle-cards.json',c)
            save(target/'policy.json',policy or {'block_on': []})
            save(target/'registry.json',registry);save(target/'result.json',result)
            (target/'review.md').write_text(render(result))
            records.append(dict(case=name,status=result['status'],registry_commit=command(repo,'rev-parse','HEAD')))
            return result
        baseline=run('baseline',model,cards)
        states={(f['source'],f['target']):f['status'] for f in baseline['findings']}
        assert states['gpc','compute']=='CORROBORATED'
        assert states['gpc','vm']=='UNCORROBORATED'
        assert states['vm','storage']=='UNMODELED'
        assert ('storage','domain') not in states
        policy_denied=run('policy-block-unmodeled',model,cards,{'block_on':['UNMODELED']})
        assert policy_denied['status']=='DENIED' and policy_denied['model_valid']
        assert 'nodes' not in policy_denied
        oracle=read_json((ROOT/'tests/oracle.json').read_bytes())
        assert edge_set(baseline)=={tuple(e) for e in oracle['edges']}
        assert baseline['layers']==oracle['layers']
        changed=copy.deepcopy(cards)
        next(c for c in changed if c['node_id']=='register-ci')['service_dependencies']=['cyberark']
        primary=run('lc-only',model,changed)
        assert edge_set(primary)-edge_set(baseline)=={('cyberark','register-ci'),('cyberark','an-register-ci')}
        assert edge_set(baseline)-edge_set(primary)=={('validate','register-ci'),('validate','an-register-ci')}
        m=copy.deepcopy(model); c=copy.deepcopy(cards)
        m['nodes'].append(dict(node_id='an-audit',name='Additional audit',node_type='atomic',lc_id='lc-audit'))
        m['decomposition'].append(['cmdb','an-audit'])
        c.append(dict(next(c for c in cards if c['node_id']=='an-register-ci'),node_id='an-audit',lc_id='lc-audit'))
        secondary=run('structure-and-lc',m,c)
        assert edge_set(secondary)-edge_set(baseline)=={('an-audit','cmdb')}
        bad=copy.deepcopy(cards)
        next(c for c in bad if c['node_id']=='an-disk')['automation_id']='11111111-2222-3333-4444-555555555555'
        denied=run('unresolved-uuid',model,bad)
        assert denied['diagnostics'][0]['code']=='UNRESOLVED_AUTOMATION'
        record_path=next((repo/'poc-04/automation/records').glob('*.json'))
        record=read_json(record_path.read_bytes()); uid=record['automation_id']
        path='poc-04/automation/artifacts/replacement.py'
        (repo/path).write_text('print("replacement demonstration implementation")\n')
        record['artifact_path']=path;save(record_path,record);commit(repo)
        binding=run('binding-only',model,cards)
        assert edge_set(binding)==edge_set(baseline)
        old=next(n['automation'] for n in baseline['nodes'] if n.get('automation',{}).get('automation_id')==uid)
        new=next(n['automation'] for n in binding['nodes'] if n.get('automation',{}).get('automation_id')==uid)
        assert old==new
        old_e=next(x for x in baseline['binding_evidence'] if x['automation_id']==uid)
        new_e=next(x for x in binding['binding_evidence'] if x['automation_id']==uid)
        assert old_e['artifact_sha256']!=new_e['artifact_sha256']
        command(repo,'bundle','create',str((args.out/'automation-snapshots.bundle').resolve()),'--all')
    for name,digest in fingerprints.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, name
    save(args.out/'summary.json',dict(result='PASS',cases=records,unchanged_source_sha256=fingerprints,
         note='Registry commits are isolated test commits preserved in automation-snapshots.bundle.'))
    print('PASS: comparison states, permissive compilation, blocking policy, three mutations, unresolved UUID; source fingerprints unchanged')


if __name__=='__main__':main()
