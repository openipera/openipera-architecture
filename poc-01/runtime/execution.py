"""Local execution capability; knows artifacts, not service composition."""
import subprocess
import sys
from pathlib import Path
from engine import digest


def execute(root, node, binding):
    root = Path(root).resolve()
    artifact = (root / binding['artifact']).resolve()
    if not artifact.is_relative_to(root) or artifact.suffix != '.py':
        raise ValueError('Artifact must be a Python file within the artifact repository')
    if digest(artifact.read_bytes()) != binding['sha256']:
        raise ValueError('Artifact content does not match pinned binding')
    completed = subprocess.run([sys.executable, str(artifact), node],
                               capture_output=True, text=True, timeout=10)
    return {'returncode': completed.returncode, 'stdout': completed.stdout,
            'stderr': completed.stderr, 'artifact_sha256': binding['sha256']}
