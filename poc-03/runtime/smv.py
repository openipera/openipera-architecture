"""Independent POC-03 validator. No automation is executed by this module."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
from uuid import UUID


class Denied(ValueError):
    def __init__(self, code, message, **context):
        super().__init__(message)
        self.diagnostic = dict(code=code, message=message, **context)


def require(condition, code, message, **context):
    if not condition:
        raise Denied(code, message, **context)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def fields(value, expected, context):
    require(isinstance(value, dict) and set(value) == set(expected),
            'SCHEMA', 'Expected exactly these fields: ' + ', '.join(sorted(expected)), context=context)


def uuid_key(value):
    require(isinstance(value, str), 'INVALID_UUID', 'automation_id must be a UUID', automation_id=value)
    try:
        parsed = UUID(value)
    except (ValueError, AttributeError):
        raise Denied('INVALID_UUID', 'automation_id must be a UUID', automation_id=value)
    require(str(parsed) == value.lower(), 'INVALID_UUID',
            'UUID must use hyphenated UUID notation', automation_id=value)
    return str(parsed)


def read_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, 'DUPLICATE_JSON_KEY', 'Duplicate JSON key', key=key)
            result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=unique)
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise Denied('JSON', str(exc)) from exc


def git(repo, *args):
    process = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    require(process.returncode == 0, 'VCS', 'Cannot read authoritative Git snapshot',
            detail=process.stderr.decode(errors='replace').strip())
    return process.stdout


def load_registry(repo, ref='HEAD', prefix='poc-03/automation'):
    """Read committed blobs only. Untracked, staged and dirty files are not authority."""
    require(text(prefix) and not prefix.startswith('/') and
            all(p not in ('', '.', '..') for p in prefix.split('/')),
            'REGISTRY_PATH', 'Registry path must be a repository-relative directory')
    commit = git(repo, 'rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()
    entries = {}
    for row in git(repo, 'ls-tree', '-r', '-z', commit, '--', prefix + '/').split(b'\0'):
        if row:
            header, name = row.split(b'\t', 1)
            mode, kind, oid = header.decode().split()
            entries[name.decode()] = (mode, kind, oid)
    registry = {}
    for name in sorted(entries):
        if not name.startswith(prefix + '/records/') or not name.endswith('.json'):
            continue
        mode, kind, oid = entries[name]
        require(mode in ('100644', '100755') and kind == 'blob',
                'REGISTRY_RECORD', 'Registry record must be a regular Git blob', path=name)
        record = read_json(git(repo, 'cat-file', 'blob', oid))
        fields(record, ('automation_id', 'automation_name', 'artifact_path', 'execution_type'), name)
        key = uuid_key(record['automation_id'])
        require(key not in registry, 'DUPLICATE_AUTOMATION_ID', 'Duplicate automation UUID', automation_id=key)
        require(text(record['automation_name']) and text(record['execution_type']),
                'REGISTRY_RECORD', 'Registry metadata must be populated', path=name)
        path = record['artifact_path']
        require(text(path) and not PurePosixPath(path).is_absolute() and
                all(p not in ('', '.', '..') for p in path.split('/')),
                'ARTIFACT_PATH', 'Artifact path must be repository-relative', path=path)
        require(path in entries and entries[path][0] in ('100644', '100755')
                and entries[path][1] == 'blob', 'MISSING_ARTIFACT',
                'Artifact must be a regular committed blob inside the automation directory', path=path)
        artifact = git(repo, 'cat-file', 'blob', entries[path][2])
        registry[key] = dict(record, commit=commit, record_path=name,
                             artifact_sha256=hashlib.sha256(artifact).hexdigest())
    require(bool(registry), 'EMPTY_REGISTRY', 'No committed automation records found', commit=commit)
    return registry


def layers(nodes, edges, code):
    incoming = {n: set() for n in nodes}
    for source, target in edges:
        incoming[target].add(source)
    result = []
    while incoming:
        ready = sorted(n for n, deps in incoming.items() if not deps)
        require(bool(ready), code, 'Cycle prevents resolution', blocked_nodes=sorted(incoming))
        result.append(ready)
        for n in ready:
            del incoming[n]
        for deps in incoming.values():
            deps.difference_update(ready)
    return result


def derive(model, cards, registry):
    """Validate the whole supplied model, then derive completion/action vertices."""
    fields(model, ('nodes', 'decomposition'), 'SM-DAG')
    require(isinstance(model['nodes'], list) and bool(model['nodes']) and
            isinstance(model['decomposition'], list) and isinstance(cards, list),
            'SCHEMA', 'Nodes, decomposition and Lifecycle Cards must be lists; nodes cannot be empty')
    nodes, lc_ids = {}, set()
    for node in model['nodes']:
        fields(node, ('node_id', 'name', 'node_type', 'lc_id'), 'SM-DAG node')
        require(all(text(node[k]) for k in node), 'SCHEMA', 'Node fields must be nonempty strings')
        nid = node['node_id']
        require(node['node_type'] in ('service', 'atomic'), 'NODE_TYPE', 'Unknown node type', node_id=nid)
        require(nid not in nodes, 'DUPLICATE_NODE_ID', 'Duplicate node identity', node_id=nid)
        require(node['lc_id'] not in lc_ids, 'DUPLICATE_LC_REFERENCE', 'Companion LC must be unique', node_id=nid)
        nodes[nid] = node
        lc_ids.add(node['lc_id'])
    lcs, owners = {}, set()
    for card in cards:
        fields(card, ('lc_id', 'node_id', 'service_dependencies', 'automation_name', 'automation_id'), 'LC')
        require(text(card['lc_id']) and text(card['node_id']), 'SCHEMA', 'LC identities must be nonempty strings')
        require(card['lc_id'] not in lcs, 'DUPLICATE_LC_ID', 'Duplicate LC identity', lc_id=card['lc_id'])
        require(card['node_id'] not in owners, 'DUPLICATE_LC_OWNER', 'More than one LC describes a node', node_id=card['node_id'])
        lcs[card['lc_id']] = card
        owners.add(card['node_id'])
    children = {n: [] for n in nodes}
    decomposition = set()
    for edge in model['decomposition']:
        require(isinstance(edge, list) and len(edge) == 2 and all(text(n) for n in edge),
                'SCHEMA', 'Decomposition edge must be [parent, child]')
        parent, child = edge
        require(parent in nodes and child in nodes, 'MISSING_NODE', 'Unknown decomposition endpoint', edge=edge)
        require(tuple(edge) not in decomposition, 'DUPLICATE_EDGE', 'Duplicate decomposition edge', edge=edge)
        require(nodes[parent]['node_type'] == 'service', 'ATOMIC_CHILDREN', 'Atomic Nodes must be terminal', node_id=parent)
        decomposition.add(tuple(edge))
        children[parent].append(child)
    structural_layers = layers(nodes, decomposition, 'DECOMPOSITION_CYCLE')
    descendants = {n: set() for n in nodes}
    for layer in reversed(structural_layers):
        for nid in layer:
            for child in children[nid]:
                descendants[nid].add(child)
                descendants[nid].update(descendants[child])
    dependencies, bindings = {}, {}
    for nid, node in nodes.items():
        require(node['lc_id'] in lcs, 'MISSING_LC', 'SM-DAG node has no companion LC', node_id=nid, lc_id=node['lc_id'])
        card = lcs[node['lc_id']]
        require(card['node_id'] == nid, 'LC_NODE_MISMATCH', 'LC does not describe referencing node', node_id=nid, lc_id=node['lc_id'])
        deps = card['service_dependencies']
        require(isinstance(deps, list) and all(text(d) for d in deps), 'SCHEMA', 'service_dependencies must be a list of identities', node_id=nid)
        require(len(deps) == len(set(deps)), 'DUPLICATE_DEPENDENCY', 'Repeated service dependency', node_id=nid)
        dependencies[nid] = deps
        name, identity = card['automation_name'], card['automation_id']
        if node['node_type'] == 'atomic':
            require(not deps, 'ATOMIC_DEPENDENCIES', 'Atomic Nodes may not declare service dependencies', node_id=nid)
            require(text(name) and identity is not None, 'ATOMIC_BINDING',
                    'Atomic Node requires both automation_name and automation_id', node_id=nid, automation_name=name, automation_id=identity)
            key = uuid_key(identity)
            require(key in registry, 'UNRESOLVED_AUTOMATION', 'Atomic Node automation binding unresolved in VCS',
                    node_id=nid, automation_name=name, automation_id=identity)
            bindings[nid] = registry[key]
        else:
            require(name is None and identity is None, 'SERVICE_BINDING', 'Service Node may not bind to automation', node_id=nid)
            require(children[nid] or deps, 'EMPTY_SERVICE', 'Service must resolve through children or dependencies', node_id=nid)
        for dep in deps:
            require(dep in nodes, 'MISSING_DEPENDENCY', 'Unknown service dependency', node_id=nid, dependency=dep)
            require(dep not in descendants[nid], 'REDUNDANT_DECOMPOSITION_DEPENDENCY',
                    'Service dependencies must not restate decomposition', node_id=nid, dependency=dep)
            require(nodes[dep]['node_type'] == 'service', 'NON_SERVICE_DEPENDENCY', 'Dependency must identify a Service Node', node_id=nid, dependency=dep)
    require(set(lcs) == lc_ids, 'ORPHAN_LC', 'LC registry contains cards with no companion node', lc_ids=sorted(set(lcs) - lc_ids))
    dep_edges = {(dep, nid) for nid, deps in dependencies.items() for dep in deps}
    layers(nodes, dep_edges, 'SERVICE_DEPENDENCY_CYCLE')
    # A service vertex is a completion milestone, not executable automation.
    reasons = {}
    def edge(source, target, reason):
        reasons.setdefault((source, target), set()).add(reason)
    for parent, child in decomposition:
        edge(child, parent, 'child completion')
    for dep, nid in dep_edges:
        edge(dep, nid, 'required service completion')
        for child in children[nid]:
            if nodes[child]['node_type'] == 'atomic':
                edge(dep, child, 'prerequisite for terminal action of ' + nid)
    execution_layers = layers(nodes, reasons, 'REALIZATION_CYCLE')
    parents = {n: [] for n in nodes}
    for parent, child in decomposition:
        parents[child].append(parent)
    paths = {}
    for layer in structural_layers:
        for nid in layer:
            paths[nid] = sorted([p + [nid] for parent in sorted(parents[nid]) for p in paths[parent]] or [[nid]])
    return dict(status='VALID', nodes=[dict(nodes[n], role='action' if nodes[n]['node_type'] == 'atomic' else 'service_complete',
                architectural_paths=paths[n], **({'automation': bindings[n]} if n in bindings else {})) for n in sorted(nodes)],
                edges=[dict(source=a, target=b, reasons=sorted(reasons[a, b])) for a, b in sorted(reasons)], layers=execution_layers)


def easter_egg(status):
    """Inert console flourish; never a validation result or assurance claim."""
    if status == 'VALID':
        return 'AN-FMT-001: Validation: No human intervened.'
    return 'AN-FMT-001: Human intervention may now be required.'


def render(result):
    if result['status'] == 'DENIED':
        return '# SMV: DENIED\n\n```json\n' + json.dumps(result['diagnostics'], indent=2) + '\n```\n'
    lines = ['# SMV: VALID — derived Execution DAG', '',
             'Service vertices are completion milestones; Atomic Nodes are actions. No automation was executed.', '', '```mermaid', 'flowchart TD']
    ids = {n['node_id']: 'n' + str(i) for i, n in enumerate(result['nodes'])}
    for n in result['nodes']:
        label = n['name'] + ' / ' + n['node_id'] + ' (' + n['role'] + ')'
        label = ''.join(c if c.isalnum() or c in ' /_()-' else '&#' + str(ord(c)) + ';' for c in label)
        lines.append(f'  {ids[n["node_id"]]}["{label}"]')
    for e in result['edges']:
        lines.append(f'  {ids[e["source"]]} --> {ids[e["target"]]}')
    lines += ['```', '', '## Derived parallel layers', '']
    lines += [f'{i}. ' + ', '.join(layer) for i, layer in enumerate(result['layers'], 1)]
    lines += ['', '## Resolved automation (not executed)', '']
    for n in result['nodes']:
        if 'automation' in n:
            a = n['automation']
            lines.append(f'- {n["node_id"]}: `{a["automation_id"]}` → `{a["artifact_path"]}` at `{a["commit"]}`; SHA-256 `{a["artifact_sha256"]}`')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--lcs', type=Path, required=True)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--ref', default='HEAD')
    parser.add_argument('--registry-path', default='poc-03/automation')
    parser.add_argument('--out', type=Path, required=True, help='New output directory; existing paths are refused')
    args = parser.parse_args()
    # Refuse existing output so a failed run cannot leave a previous VALID DAG in place.
    args.out.mkdir(parents=True, exist_ok=False)
    try:
        model_raw, lcs_raw = args.model.read_bytes(), args.lcs.read_bytes()
        registry = load_registry(args.repo, args.ref, args.registry_path)
        result = derive(read_json(model_raw), read_json(lcs_raw), registry)
        result['provenance'] = dict(model_sha256=hashlib.sha256(model_raw).hexdigest(),
                                    lcs_sha256=hashlib.sha256(lcs_raw).hexdigest(),
                                    registry_commit=next(iter(registry.values()))['commit'])
    except Denied as exc:
        result = dict(status='DENIED', diagnostics=[exc.diagnostic])
    except OSError as exc:
        result = dict(status='DENIED', diagnostics=[dict(code='IO', message=str(exc))])
    (args.out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.out / 'review.md').write_text(render(result))
    print(result['status'])
    print(easter_egg(result['status']))
    return 0 if result['status'] == 'VALID' else 2


if __name__ == '__main__':
    sys.exit(main())
