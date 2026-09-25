import copy
import json
from pathlib import Path
import random
import sys
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from engine import ResolutionError, derive, execute_dag
from execution import execute
from evidence import render
from conformance import compare


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((ROOT / 'model/service-model.json').read_bytes())
        self.oracle = json.loads((ROOT / 'tests/oracle.json').read_bytes())
        self.entry = 'Compute.AN-ValidateVM'
        self.binding = json.loads((ROOT / 'artifacts/binding.json').read_bytes())

    def test_independent_oracle(self):
        compare(derive(self.model, self.entry), self.oracle)

    def test_shuffled_declarations_and_dependencies(self):
        rng = random.Random(7)
        rng.shuffle(self.model['nodes'])
        for node in self.model['nodes']:
            rng.shuffle(node['dependencies'])
        compare(derive(self.model, self.entry), self.oracle)

    def test_selected_dependency_closure(self):
        dag = derive(self.model, 'Compute.AN-ConfigureDisk')
        self.assertEqual(set(dag['nodes']), {'Compute.AN-ConfigureDisk', 'Compute.AN-DeployVM', 'Storage.AN-ProvisionDisk'})
        self.assertEqual(len(dag['edges']), 2)

    def test_domain_names_are_not_built_in(self):
        model = {'nodes': [
            {'service': 'Other', 'node': 'AN-Start', 'dependencies': []},
            {'service': 'Elsewhere', 'node': 'AN-Finish', 'dependencies': ['Other.AN-Start']}]}
        self.assertEqual(derive(model, 'Elsewhere.AN-Finish')['layers'], [['Other.AN-Start'], ['Elsewhere.AN-Finish']])

    def test_invalid_schema_and_service_nodes(self):
        for change in ({'command': 'echo bad'}, {'node': 'S-Compute'}, {'dependencies': ['unqualified']},
                       {'dependencies': 'Compute.AN-DeployVM'}):
            model = copy.deepcopy(self.model)
            model['nodes'][0].update(change)
            with self.assertRaises(ResolutionError):
                derive(model, self.entry)

    def test_duplicate_and_unknown_entry(self):
        with self.assertRaisesRegex(ResolutionError, 'Unknown entry'):
            derive(self.model, 'Unknown.AN-Entry')
        self.model['nodes'].append(copy.deepcopy(self.model['nodes'][0]))
        with self.assertRaisesRegex(ResolutionError, 'Duplicate'):
            derive(self.model, self.entry)

    def test_missing_and_cycle_details(self):
        self.model['nodes'][0]['dependencies'] = ['Unknown.AN-Missing']
        with self.assertRaises(ResolutionError) as error:
            derive(self.model, self.entry)
        self.assertFalse(error.exception.details['dependencies_resolved'])
        self.model['nodes'][0]['dependencies'] = [self.entry]
        with self.assertRaises(ResolutionError) as error:
            derive(self.model, self.entry)
        self.assertTrue(error.exception.details['cycle_detected'])
        self.assertIn(self.entry, error.exception.details['cycle'])

    def test_oracle_detects_extra_edges_even_with_same_layers(self):
        dag = derive(self.model, self.entry)
        dag['edges'].append(['Storage.AN-ProvisionDisk', 'Compute.AN-ConfigureCPU'])
        with self.assertRaises(AssertionError):
            compare(dag, self.oracle)

    def test_concurrent_ready_nodes(self):
        dag = derive(self.model, self.entry)
        barrier = threading.Barrier(3)
        def succeed(node, binding):
            if node in self.oracle['layers'][0]:
                barrier.wait(timeout=5)  # Serial scheduling would fail this run.
            return {'returncode': 0}
        execute_dag(dag, self.binding, succeed, lambda *args, **kwargs: None)

    def test_failure_blocks_later_layers(self):
        dag = derive(self.model, self.entry)
        called = []
        def fail(node, binding):
            called.append(node)
            return {'returncode': 1}
        with self.assertRaises(RuntimeError):
            execute_dag(dag, self.binding, fail, lambda *args, **kwargs: None)
        self.assertEqual(set(called), set(self.oracle['layers'][0]))

    def test_artifact_integrity_and_path(self):
        binding = dict(self.binding, sha256='0' * 64)
        with self.assertRaisesRegex(ValueError, 'content'):
            execute(ROOT / 'artifacts', self.entry, binding)
        binding['artifact'] = '../runtime/server.py'
        with self.assertRaisesRegex(ValueError, 'within'):
            execute(ROOT / 'artifacts', self.entry, binding)

    def test_execution_failure_preserves_valid_graph_in_report(self):
        dag = derive(self.model, self.entry)
        report = render('test', [{'event': 'resolution_succeeded', 'dag': dag},
                                {'event': 'request_finished', 'status': 'failed', 'error': 'Action failed'}])
        self.assertIn('Derived graph valid: yes', report)
        self.assertIn('Execution completed successfully: no', report)
        self.assertIn('```mermaid', report)


if __name__ == '__main__':
    unittest.main()
