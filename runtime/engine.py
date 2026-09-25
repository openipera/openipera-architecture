"""Generic model consumer; no service-specific workflow or automation."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from graphlib import TopologicalSorter
from urllib.request import urlopen


def digest(data):
    return hashlib.sha256(data).hexdigest()


def derive(model, service):
    nodes = model['nodes']
    entry = nodes.get(service, {})
    if entry.get('kind') != 'service' or not entry.get('contract'):
        raise ValueError('Entry must be a callable service')
    graph = {}

    def visit(name):
        if name in graph:
            return
        node = nodes[name]
        kind = node['kind']
        if kind not in ('service', 'atomic'):
            raise ValueError('Unknown node kind')
        allowed = {'kind', 'requires', 'contract'} if kind == 'service' else {'kind', 'requires', 'binding'}
        if set(node) - allowed:
            raise ValueError('Unexpected model fields; automation is external')
        deps = node['requires']
        if not isinstance(deps, list) or not all(isinstance(d, str) for d in deps):
            raise ValueError('requires must be a list of node references')
        if kind == 'atomic' and set(node['binding']) != {'artifact', 'sha256'}:
            raise ValueError('Atomic binding must identify artifact and content digest')
        graph[name] = deps
        for dep in deps:
            visit(dep)

    visit(service)
    sorter = TopologicalSorter(graph)
    sorter.prepare()  # Validate the complete reachable graph before any execution.
    layers = []
    while sorter.is_active():
        ready = sorted(sorter.get_ready())
        layers.append(ready)
        sorter.done(*ready)
    return layers


def realize(model_url, service, execute, emit):
    with urlopen(model_url, timeout=10) as response:
        raw = response.read()
    model = json.loads(raw)
    layers = derive(model, service)
    emit('plan', model_sha256=digest(raw), model=model, layers=layers)

    def action(name):
        node = model['nodes'][name]
        if node['kind'] == 'service':
            emit('service_complete', node=name)
            return True
        emit('action_started', node=name, binding=node['binding'])
        try:
            result = execute(name, node['binding'])
        except Exception as exc:
            result = {'returncode': -1, 'stderr': str(exc), 'stdout': ''}
        emit('action_finished', node=name, **result)
        return result['returncode'] == 0

    for layer in layers:
        with ThreadPoolExecutor(max_workers=min(8, len(layer))) as pool:
            outcomes = list(pool.map(action, layer))
        if not all(outcomes):
            raise RuntimeError('Action failed; dependent layers were not executed')
    return layers
