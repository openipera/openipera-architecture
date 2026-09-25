"""Human-readable evidence generated exclusively from this request's actual results."""
import json
import re


def fenced(value, language='text'):
    # A malformed request/model cannot terminate its evidence code block.
    fence = '`' * max(3, max((len(part) for part in re.findall(r'`+', value)), default=0) + 1)
    return f'{fence}{language}\n{value}\n{fence}'


def render(run_id, events):
    def event(kind):
        return next((e for e in events if e['event'] == kind), {})

    request = event('request_started')
    snapshot = event('model_snapshot')
    resolved = event('resolution_succeeded')
    failed = event('resolution_failed')
    finished = event('request_finished')
    dag = resolved.get('dag')
    lines = ['# Derived Execution DAG', '', '## Request', '', f'Run ID: `{run_id}`', '',
             fenced(request.get('request', 'Request unavailable.'), 'json'), '',
             'The entry point selects an AN dependency closure; it does not define Service Node semantics.', '',
             '## Model Snapshot', '',
             f"Source: `{snapshot.get('source', 'not fetched')}`", '',
             f"Content version (SHA-256 of exact source bytes): `{snapshot.get('model_sha256', 'unavailable')}`", '',
             f"Exact source bytes: `{run_id}-model.json` (when fetched).", '',
             fenced(snapshot.get('model_text', 'No model snapshot available.'), 'json'), '',
             '## Resolved Nodes', '']
    if dag:
        lines += [f'- `{node}`' for node in dag['nodes']]
    else:
        lines += ['No valid execution graph was produced. See the resolution error below.']
    lines += ['', '## Dependency Edges', '',
              '`A -> B` means **A must complete before B may execute.**', '']
    if dag:
        lines += [fenced('\n'.join(f'{a} -> {b}' for a, b in dag['edges']) or '(no edges)')]
    lines += ['', '## Derived Execution Layers', '',
              'Nodes in a layer may execute concurrently. Layers are derived, not model input.', '']
    if dag:
        lines += [fenced('\n\n'.join(f'Layer {i}\n' + '\n'.join('  ' + n for n in layer)
                                     for i, layer in enumerate(dag['layers'])))]
    lines += ['', '## Visual Execution DAG', '']
    if dag:
        ids = {name: f'n{i}' for i, name in enumerate(dag['nodes'])}
        mermaid = ['flowchart LR']
        services = sorted({name.split('.')[0] for name in dag['nodes']})
        for i, service in enumerate(services):
            mermaid.append(f'    subgraph s{i}["{service}"]')
            for name in dag['nodes']:
                if name.split('.')[0] == service:
                    mermaid.append(f'        {ids[name]}["{name}"]')
            mermaid.append('    end')
        mermaid += [f'    {ids[a]} --> {ids[b]}' for a, b in dag['edges']]
        lines += [fenced('\n'.join(mermaid), 'mermaid')]
    else:
        lines += ['No DAG diagram: resolution did not succeed.']
    result = dag or failed
    def flag(key):
        value = result.get(key)
        return 'not determined' if value is None else ('yes' if value else 'no')
    lines += ['', '## Resolution Result', '',
              f"- Derived graph valid: {flag('valid')}",
              f"- All dependencies resolved: {flag('dependencies_resolved')}",
              f"- Cycle detected: {flag('cycle_detected')}",
              f"- Execution completed successfully: {'yes' if finished.get('status') == 'succeeded' else 'no'}", '']
    if finished.get('error'):
        lines += [fenced(finished['error'])]
    if failed.get('cycle'):
        lines += ['', 'Cycle path below uses **prerequisite -> dependent** semantics:', '',
                  fenced(' -> '.join(failed['cycle']))]
    actions = [e for e in events if e['event'] == 'action_finished']
    lines += ['', '## Execution Results', '', fenced(json.dumps(actions, indent=2), 'json'), '',
              f'Ordered detailed events: `{run_id}.jsonl`.', '']
    return '\n'.join(lines)
