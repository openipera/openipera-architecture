"""Deterministic stand-in for an infrastructure action."""
import json
import sys

print(json.dumps({'action': sys.argv[1], 'result': 'ok'}, sort_keys=True))
