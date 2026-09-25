"""Resolve persistent dependency facts into a request-scoped execution DAG."""
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from graphlib import CycleError, TopologicalSorter


def digest(data):
    return hashlib.sha256(data).hexdigest()


class ResolutionError(ValueError):
    def __init__(self, message, *, dependencies_resolved=None, cycle_detected=None,
                 missing_references=None, cycle=None):
        super().__init__(message)
        self.details = dict(valid=False, dependencies_resolved=dependencies_resolved,
                            cycle_detected=cycle_detected,
                            missing_references=missing_references or [], cycle=cycle or [])


def derive(model, entry_point):
    """Resolve the entry point's transitive prerequisites; edges run prerequisite -> node."""
    if not isinstance(model, dict) or set(model) != {'nodes'} or not isinstance(model['nodes'], list):
        raise ResolutionError('Model must contain only a nodes list')
    nodes = {}
    for node in model['nodes']:
        if not isinstance(node, dict) or set(node) != {'service', 'node', 'dependencies'}:
            raise ResolutionError('Every node requires exactly service, node, dependencies')
        service, name, deps = node['service'], node['node'], node['dependencies']
        if not isinstance(service, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*', service):
            raise ResolutionError('Invalid service name')
        if isinstance(name, str) and name.startswith('S-'):
            raise ResolutionError('S-* Service Node semantics are undefined in POC-02')
        if not isinstance(name, str) or not re.fullmatch(r'AN-[A-Za-z0-9_-]+', name):
            raise ResolutionError('Expected an AN-* Atomic Node name')
        if not isinstance(deps, list) or not all(
            isinstance(dep, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]*\.AN-[A-Za-z0-9_-]+', dep)
            for dep in deps
        ):
            raise ResolutionError(f'{service}.{name}: dependencies must be fully qualified AN references')
        qualified = f'{service}.{name}'
        if qualified in nodes:
            raise ResolutionError(f'Duplicate node: {qualified}')
        nodes[qualified] = node
    if entry_point not in nodes:
        raise ResolutionError(f'Unknown entry point: {entry_point}', dependencies_resolved=False,
                              missing_references=[entry_point])

    graph, missing = {}, []

    def visit(name):
        if name in graph:
            return
        graph[name] = sorted(set(nodes[name]['dependencies']))
        for dep in graph[name]:
            if dep not in nodes:
                missing.append(f'{name} depends on missing {dep}')
            else:
                visit(dep)

    visit(entry_point)
    if missing:
        raise ResolutionError('; '.join(missing), dependencies_resolved=False,
                              missing_references=missing)
    sorter = TopologicalSorter(graph)
    try:
        sorter.prepare()
    except CycleError as exc:
        cycle = exc.args[1]
        raise ResolutionError('Dependency cycle (prerequisite -> dependent): ' + ' -> '.join(cycle),
                              dependencies_resolved=True, cycle_detected=True, cycle=cycle) from exc
    layers = []
    while sorter.is_active():
        ready = sorted(sorter.get_ready())
        layers.append(ready)
        sorter.done(*ready)
    return {'entry_point': entry_point, 'nodes': sorted(graph),
            'edges': sorted([[dep, name] for name, deps in graph.items() for dep in deps]),
            'layers': layers, 'valid': True, 'dependencies_resolved': True,
            'cycle_detected': False}


def execute_dag(dag, binding, execute, emit):
    """Barrier per derived layer; no domain names or model facts live here."""
    def action(name):
        emit('action_started', node=name, binding=binding)
        try:
            result = execute(name, binding)
        except Exception as exc:
            result = {'returncode': -1, 'stderr': str(exc), 'stdout': ''}
        emit('action_finished', node=name, **result)
        return result['returncode'] == 0

    for layer in dag['layers']:
        with ThreadPoolExecutor(max_workers=min(8, len(layer))) as pool:
            outcomes = list(pool.map(action, layer))
        if not all(outcomes):
            raise RuntimeError('Action failed; dependent layers were not executed')
