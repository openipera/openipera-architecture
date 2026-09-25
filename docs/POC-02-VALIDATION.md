# Actual POC-02 validation

Executed on the user's Windows laptop on 2026-09-24 (2026-09-25 UTC), in the existing
`F:\Programming\IPERA\ipera-demonstration-project` repository.

## Live Compose results

`docker compose up --build -d --wait` rebuilt the runtime and started healthy services.
The model stayed in its independent HTTP container, with no authoritative model or
test oracle mounted into the resolver. Runtime inspection found only `engine.py`,
`evidence.py`, `execution.py`, and `server.py` in `/app`; only `/artifacts` (read-only)
and `/evidence` (read/write) were mounted.

`tests/conformance.py` ran from a separate test-client container against the live
resolver. It compares exact node and edge sets, topological layers (unordered within
each layer), execution prerequisites, exact model snapshots and generated Mermaid
node/edge semantics.

| Case | Actual result | Generated Markdown evidence |
|---|---|---|
| Baseline | PASS: 9 nodes, 12 edges, layer sizes 3 / 3 / 2 / 1; all actions exit 0 | [Baseline DAG](../evidence/ef35ec33ba8a4e28bf471fb6f6f51e19-execution-dag.md) |
| Add ConfigureMemory | PASS: 10 nodes, 14 edges, sizes 3 / 4 / 2 / 1; new AN executed | [New AN DAG](../evidence/f1b7e1bb214c420b84b1a0d96f3929a3-execution-dag.md) |
| RegisterDNS also requires ConfigureCPU | PASS: 9 nodes, 13 edges, sizes 3 / 2 / 1 / 2 / 1 | [Cross-service DAG](../evidence/1ab117827805422aad67a34422aa96cd-execution-dag.md) |
| Missing Storage.AN-MissingDisk | PASS: HTTP 422, identifies missing reference and owning node, no actions | [Missing-reference report](../evidence/573bb388f68c4278af802341fa75d000-execution-dag.md) |
| DeployVM requires ValidateVM | PASS: HTTP 422, identifies a closed cycle path, no actions | [Cycle report](../evidence/323b3f2bc4d14fd88bcfc11d9b7a20a2-execution-dag.md) |

Full responses and unchanged runtime/artifact/binding/Compose fingerprints are in
`evidence/poc02-conformance.json`. All model mutations used the same running resolver:
container ID `ab09da499a039c1d6553342ac3c90c72e66ab16f88ec26b49dac381efe17dae4`,
started at `2026-09-25T03:37:05.176885062Z`, restart count **0** before and after.

The exact baseline model was restored, SHA-256:
`87f428a1ba6cc40da5e71dcd224fd9f5c4f35c65919d9a88addf04422d6e56fb`.
The expected oracle was neither copied into the image nor sent with any request.
The baseline and cycle Markdown reports were also inspected directly: arrows, layers,
service grouping and resolution flags matched the actual graph and failure diagnostics.

## Supporting checks

All **12 unit tests passed** on the host and in the actual Python 3.13 runtime image:
oracle equivalence, declaration reordering, closure selection, unfamiliar domain names,
schema/S-node rejection, duplicate/unknown identities, missing/cycle diagnostics,
extra-edge detection even with unchanged layers, concurrent eligibility, failure
blocking, artifact hash/path checks, and valid-graph evidence after execution failure.

Both README Windows commands were exercised against the baseline:

- cmd.exe curl: `93c80ebc68fd462c9a25a343582ab271`, succeeded.
- PowerShell Invoke-RestMethod: `59d102f4ddd24fa68152780a0fa6f6d9`, succeeded.

Both executed all nine ANs successfully. An additional malformed-JSON request returned
HTTP 400, ran no actions and saved `66613bbc1db04a779483e973c788342a-execution-dag.md`.
The bash/zsh command is documented but was not separately exercised in those shells.

## Scope and remaining questions

No architecture-source edits, new platforms, external services or AN implementation
changes were needed. The existing artifact is reused through a separate generic binding.
The requested three-field model is expressed in JSON rather than YAML, preserving the
POC-01 parser and keeping dependencies small. `S-*` Service Node semantics and distinct
per-AN bindings remain future design questions; no behavior was invented for them.

The active API/schema/tests now target POC-02; POC-01 remains historical in Git and its
existing evidence. The new changes are uncommitted and unpushed. Both demo containers
are left running with the restored baseline for inspection.

Generated reports are local, Git-ignored files. Their links work in this checkout;
include chosen evidence files when sharing these results outside the laptop. Mermaid
source and graph semantics were checked; GitHub's remote rendering was not exercised.
