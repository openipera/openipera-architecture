import copy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'runtime'))
from engine import derive, realize
from execution import execute


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.model = json.loads((ROOT / 'model/service-model.json').read_bytes())

    def test_shared_dependency_executes_once(self):
        self.assertEqual(derive(self.model, 'A'), [['D'], ['B', 'C'], ['A']])

    def test_cycle_and_missing_reference_rejected(self):
        self.model['nodes']['D']['requires'] = ['A']
        with self.assertRaises(ValueError):
            derive(self.model, 'A')
        self.model['nodes']['D']['requires'] = ['missing']
        with self.assertRaises(KeyError):
            derive(self.model, 'A')

    def test_atomic_node_is_not_callable(self):
        with self.assertRaises(ValueError):
            derive(self.model, 'B')

    def test_no_embedded_commands(self):
        self.model['nodes']['B']['command'] = 'echo bad'
        with self.assertRaises(ValueError):
            derive(self.model, 'A')

    def test_failed_dependency_blocks_dependents(self):
        called = []
        def fail(node, binding):
            called.append(node)
            return {'returncode': 1}
        with patch('engine.urlopen') as opened:
            opened.return_value.__enter__.return_value.read.return_value = json.dumps(self.model).encode()
            with self.assertRaises(RuntimeError):
                realize('http://model', 'A', fail, lambda *args, **kwargs: None)
        self.assertEqual(called, ['D'])

    def test_hash_mismatch_and_escape_rejected(self):
        binding = copy.deepcopy(self.model['nodes']['B']['binding'])
        binding['sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            execute(ROOT / 'artifacts', 'B', binding)
        binding['artifact'] = '../runtime/server.py'
        with self.assertRaises(ValueError):
            execute(ROOT / 'artifacts', 'B', binding)


if __name__ == '__main__':
    unittest.main()
