"""HTTP graph conformance: test-only oracle, model-only mutations, no runtime imports."""
import copy
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ENTRY = 'Compute.AN-ValidateVM'


def fingerprints():
    paths = [p for folder in ('runtime', 'artifacts') for p in (ROOT / folder).rglob('*')
             if p.is_file() and '__pycache__' not in p.parts]
    paths += [ROOT / 'Dockerfile', ROOT / 'docker-compose.yml']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def request(url, payload=None):
    data = json.dumps(payload or {'entry_point': ENTRY}).encode()
    try:
        response = urlopen(Request(url + '/requests', data=data,
                                   headers={'Content-Type': 'application/json'}), timeout=30)
    except HTTPError as exc:
        response = exc
    with response:
        return response.status, json.load(response)


def compare(actual, expected):
    assert actual['valid'] and actual['dependencies_resolved'] and not actual['cycle_detected']
    assert set(actual['nodes']) == set(expected['nodes']), 'Node set mismatch'
    assert len(actual['nodes']) == len(set(actual['nodes'])), 'Duplicate nodes'
    assert {tuple(e) for e in actual['edges']} == {tuple(e) for e in expected['edges']}, 'Edge set mismatch'
    assert len(actual['edges']) == len({tuple(e) for e in actual['edges']}), 'Duplicate edges'
    assert [set(layer) for layer in actual['layers']] == [set(layer) for layer in expected['layers']], 'Layers differ'
    flattened = [n for layer in actual['layers'] for n in layer]
    assert len(flattened) == len(set(flattened)) == len(actual['nodes'])


def check_evidence(run, model_bytes):
    run_id = run['run_id']
    saved = (ROOT / 'evidence' / (run_id + '-model.json')).read_bytes()
    assert saved == model_bytes, 'Snapshot is not the requested model'
    snapshot = next(e for e in run['events'] if e['event'] == 'model_snapshot')
    assert snapshot['model_sha256'] == hashlib.sha256(saved).hexdigest()
    report = (ROOT / 'evidence' / run['evidence']).read_text(encoding='utf-8')
    for heading in ('Request', 'Model Snapshot', 'Resolved Nodes', 'Dependency Edges',
                    'Derived Execution Layers', 'Visual Execution DAG', 'Resolution Result'):
        assert '## ' + heading in report
    assert run_id in report and snapshot['model_sha256'] in report
    dag = run['dag']
    if dag:
        # Check that the rendered Mermaid encodes precisely the actual graph.
        mermaid = report.split('```mermaid\n')[1].split('```')[0]
        names = dict(re.findall(r'(n\d+)\["([^"]+)"\]', mermaid))
        edges = {(names[a], names[b]) for a, b in re.findall(r'(n\d+) --> (n\d+)', mermaid)}
        assert set(names.values()) == set(dag['nodes'])
        assert edges == {tuple(edge) for edge in dag['edges']}
        for a, b in dag['edges']:
            assert f'{a} -> {b}' in report
    else:
        assert 'No DAG diagram' in report
    return report


def verify_success(code, run, expected):
    assert code == 200 and run['status'] == 'succeeded', run
    compare(run['dag'], expected)
    starts = {e['node']: e['sequence'] for e in run['events'] if e['event'] == 'action_started'}
    ends = [e for e in run['events'] if e['event'] == 'action_finished']
    assert set(starts) == {e['node'] for e in ends} == set(expected['nodes'])
    assert len(ends) == len(expected['nodes'])
    finished = {e['node']: e['sequence'] for e in ends}
    for a, b in expected['edges']:
        assert finished[a] < starts[b], 'Execution violated a derived edge'
    for e in ends:
        assert e['returncode'] == 0
        assert json.loads(e['stdout']) == {'action': e['node'], 'result': 'ok'}


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:18081'
    path = ROOT / 'model/service-model.json'
    original = path.read_bytes()
    baseline = json.loads(original)
    oracle = json.loads((ROOT / 'tests/oracle.json').read_bytes())
    before = fingerprints()
    runs = {}

    def node(model, name):
        return next(n for n in model['nodes'] if n['service'] + '.' + n['node'] == name)

    def run_case(label, model, expected=None, failure=None):
        data = original if label == 'baseline' else (json.dumps(model, indent=2) + '\n').encode()
        path.write_bytes(data)
        code, run = request(url)
        report = check_evidence(run, data)
        if expected:
            verify_success(code, run, expected)
        else:
            assert code == 422 and run['status'] == 'failed' and run['dag'] is None
            assert not any(e['event'].startswith('action_') for e in run['events'])
            error = next(e for e in run['events'] if e['event'] == 'resolution_failed')
            if failure == 'missing':
                assert error['dependencies_resolved'] is False
                assert 'Storage.AN-MissingDisk' in error['error']
                assert 'All dependencies resolved: no' in report
            else:
                assert error['cycle_detected'] is True
                assert error['cycle'][0] == error['cycle'][-1]
                assert 'Cycle detected: yes' in report
        assert before == fingerprints(), 'Runtime/artifacts/bindings changed'
        runs[label] = run
        print(f'PASS {label}: {run["run_id"]} -> {run["evidence"]}')

    try:
        run_case('baseline', baseline, oracle)
        added = copy.deepcopy(baseline)
        added['nodes'].append({'service': 'Compute', 'node': 'AN-ConfigureMemory',
                               'dependencies': ['Compute.AN-DeployVM']})
        node(added, ENTRY)['dependencies'].append('Compute.AN-ConfigureMemory')
        expected = copy.deepcopy(oracle)
        expected['nodes'].append('Compute.AN-ConfigureMemory')
        expected['edges'] += [['Compute.AN-DeployVM', 'Compute.AN-ConfigureMemory'],
                              ['Compute.AN-ConfigureMemory', ENTRY]]
        expected['layers'][1].append('Compute.AN-ConfigureMemory')
        run_case('new_atomic_node', added, expected)

        crossed = copy.deepcopy(baseline)
        node(crossed, 'Network.AN-RegisterDNS')['dependencies'].append('Compute.AN-ConfigureCPU')
        expected = copy.deepcopy(oracle)
        expected['edges'].append(['Compute.AN-ConfigureCPU', 'Network.AN-RegisterDNS'])
        expected['layers'] = [oracle['layers'][0], ['Compute.AN-ConfigureCPU', 'Compute.AN-ConfigureDisk'],
                              ['Network.AN-RegisterDNS'], oracle['layers'][2], oracle['layers'][3]]
        run_case('new_cross_service_dependency', crossed, expected)

        missing = copy.deepcopy(baseline)
        node(missing, 'Compute.AN-ConfigureDisk')['dependencies'].append('Storage.AN-MissingDisk')
        run_case('missing_reference', missing, failure='missing')
        cycle = copy.deepcopy(baseline)
        node(cycle, 'Compute.AN-DeployVM')['dependencies'].append(ENTRY)
        run_case('cycle', cycle, failure='cycle')
    finally:
        path.write_bytes(original)
    assert path.read_bytes() == original
    report = {'result': 'PASS', 'baseline_restored': True, 'runs': runs,
              'unchanged_files_sha256': before}
    (ROOT / 'evidence/poc02-conformance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('PASS: all graph and mutation checks; exact baseline restored; runtime and bindings unchanged')


if __name__ == '__main__':
    main()
