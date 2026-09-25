# IPERA POC-01: external model, dynamically derived execution

Reference behavior for the provisional v0.3 architecture. No AAP, real infrastructure,
catalog UI, reconciliation, or product-specific service workflow.

## Run

From this repository, with Docker Engine and Compose available:

```sh
docker compose up
```

This builds the small runtime and starts the external model server and orchestrator.
The first run needs access to the public Python image; no cloud account is needed.
Docker Engine on Linux is sufficient; Docker Desktop is optional.
Wait for both containers to be healthy (`docker compose ps`). In another terminal:

### Windows Command Prompt (cmd.exe)

```bat
curl -X POST http://localhost:18081/requests -H "Content-Type: application/json" -d "{\"service\":\"A\"}"
```

The backslashes preserve the JSON double quotes when passed to curl. Copy this
command into cmd.exe; single quotes do not quote arguments in that shell.

### PowerShell

Use `Invoke-RestMethod` to avoid the version-dependent `curl` alias and native
command argument quoting differences:

```powershell
Invoke-RestMethod http://localhost:18081/requests -Method Post -ContentType application/json -Body '{"service":"A"}' | ConvertTo-Json -Depth 20
```

### bash/zsh

```sh
curl -X POST http://localhost:18081/requests -H 'Content-Type: application/json' -d '{"service":"A"}'
```

Inspect the authoritative model at http://localhost:18080/service-model.json.
Each response contains ordered events, results, model snapshot and hash, and resolved
artifact hashes. The same events persist in `evidence/<run_id>.jsonl` and container logs.
Evidence survives container removal. Stop with `docker compose down`.

## Edge semantics and expected evidence

`X.requires = [Y]` means **X depends on Y**, so Y completes before X.
The baseline dependency arrows are `A -> {B,C} -> D`; execution runs in the reverse
direction: **D, then B/C concurrently, then A completes**. A is a callable service
with no automation of its own. B, C and D are ANs. Dependencies between ANs express
prerequisites, not further service decomposition. Shared D executes once per request.
This convention avoids conflating dependency arrows with execution arrows.

## Critical frozen conformance test: model-only E change

With Compose running, Python 3.13+ on the host can run:

```sh
python tests/conformance.py
```

The test requests A, verifies D precedes B/C, edits **only**
`model/service-model.json` to add atomic E (same existing external artifact binding,
`requires: ["D"]`) and adds E to A's requirements. It requests A again from the
same running orchestrator. It verifies D precedes B/C/E and all finish before A.
No container rebuild, restart, new artifact, binding registry, or workflow edit occurs.
It checks unchanged runtime/artifact/Compose fingerprints and records both complete
runs in `evidence/conformance.json`. It restores the exact original model afterward.
Run against the idle demo; the temporary model edit affects concurrent requests.

Without host Python, use the runtime image as a test client (runtime containers stay up):

```sh
docker compose run --rm --no-deps -v .:/test -w /test orchestrator python tests/conformance.py http://orchestrator:8080
docker compose run --rm --no-deps -v .:/test -w /test orchestrator python -m unittest discover -s tests -v
```

For a manual demonstration, make the same two model edits, invoke A again, and inspect
the evidence. Keep the existing `binding` from B when creating E; executable code is
not added to the model. A different implementation would require a separately versioned
artifact, but E deliberately reuses an already available implementation.

See [architecture and limits](docs/POC-01-CONFORMANCE.md) and
[actual validation results](docs/VALIDATION.md).
