"""Frozen POC-01 HTTP conformance: change only model, never restart runtime."""
import copy
import hashlib
import json
from pathlib import Path
import sys
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]


def fingerprints():
    paths = [p for folder in ('runtime', 'artifacts') for p in (ROOT / folder).rglob('*.py')]
    paths += [ROOT / 'Dockerfile', ROOT / 'docker-compose.yml']
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def request(url):
    with urlopen(Request(url + '/requests', data=b'{"service":"A"}',
                         headers={'Content-Type': 'application/json'}), timeout=30) as r:
        return json.load(r)


def verify(run, expected):
    assert run['status'] == 'succeeded', run
    events = run['events']
    starts = {e['node']: e['sequence'] for e in events if e['event'] == 'action_started'}
    ends = {e['node']: e['sequence'] for e in events if e['event'] == 'action_finished'}
    assert set(starts) == set(ends) == expected
    assert len([e for e in events if e['event'] == 'action_finished']) == len(expected)
    for node in expected - {'D'}:
        assert ends['D'] < starts[node]
    complete = next(e['sequence'] for e in events if e['event'] == 'service_complete' and e['node'] == 'A')
    assert all(end < complete for end in ends.values())
    for e in events:
        if e['event'] == 'action_finished':
            assert e['returncode'] == 0
            assert json.loads(e['stdout']) == {'action': e['node'], 'result': 'ok'}


def main():
    url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:18081'
    model_path = ROOT / 'model/service-model.json'
    original = model_path.read_bytes()
    before = fingerprints()
    baseline = json.loads(original)
    assert 'E' not in baseline['nodes'], 'Start with the baseline model'
    try:
        first = request(url)
        verify(first, {'B', 'C', 'D'})
        changed = copy.deepcopy(baseline)
        changed['nodes']['E'] = copy.deepcopy(changed['nodes']['B'])
        changed['nodes']['A']['requires'].append('E')
        model_path.write_text(json.dumps(changed, indent=2) + '\n', encoding='utf-8')
        second = request(url)
        verify(second, {'B', 'C', 'D', 'E'})
        plans = [next(e for e in r['events'] if e['event'] == 'plan') for r in (first, second)]
        assert plans[0]['model_sha256'] != plans[1]['model_sha256']
        assert before == fingerprints(), 'Runtime/artifacts changed!'
        report = {'result': 'PASS', 'baseline': first, 'model_only_E': second,
                  'unchanged_files_sha256': before}
        (ROOT / 'evidence/conformance.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
        print('PASS: D -> {B,C} -> A; model-only edit; D -> {B,C,E} -> A')
        print('Runtime/artifact fingerprints unchanged; evidence/conformance.json written')
    finally:
        model_path.write_bytes(original)


if __name__ == '__main__':
    main()
