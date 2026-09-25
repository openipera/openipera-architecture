# Actual POC-01 validation

Executed 2026-09-24 on the user's Windows laptop, from the existing repository
`F:\Programming\IPERA\ipera-demonstration-project`.

Docker Desktop's Linux engine was initially stopped/unavailable. After starting it,
Docker Engine 29.7.2 and Compose 5.5.1 ran the POC successfully. The public Python
3.13-slim image was pulled without a cloud account; the runtime has no pip dependencies.

| Acceptance criterion | Observed result |
|---|---|
| 1. Persistent external model | PASS: host JSON file served by independent model container over HTTP; orchestrator has no model mount |
| 2. Dynamic traversal/execution | PASS: request for A derived layers D / B,C / A and executed each shared prerequisite once |
| 3. External automation binding | PASS for execution boundary: AN path and SHA-256 resolved separate artifact bytes, ran deterministic subprocess, returned exit 0; files are delivered as uncommitted Git working-tree additions |
| 4. Observable evidence | PASS: response events and host JSONL include snapshot, digest, layers, action start/finish, artifact digest, stdout/stderr and exit code |
| 5. Model-only E change | PASS: same running containers discovered E, derived D / B,C,E / A; runtime/artifact/Compose hashes unchanged |
| 6. One Compose startup | PASS: `docker compose up -d --wait` built and started both services; both healthy after tests |

Baseline run: `857686487a4d45e988d1ec98bec2a863`.
Model-only E run: `d1857c0f05fd477f9723d36ebb3bd03c`.
Detailed evidence: `evidence/conformance.json` plus the two corresponding `.jsonl`
files. These local generated results are intentionally ignored by Git.

Baseline event sequence: D start 2 / finish 3; B start 4 / finish 6;
C start 5 / finish 7; A complete 8. Modified event sequence: D start 2 / finish 3;
B start 4 / finish 9; C start 5 / finish 7; E start 6 / finish 8; A complete 10.
Every action returned exit code 0 and the expected `{action: <node>, result: ok}` output.

Six unit tests passed on host Python 3.14 and again inside the actual Python 3.13
runtime image: shared dependency, cycle/missing reference, non-callable AN,
embedded command, failed prerequisite, and artifact hash/path checks.

The test restored the exact baseline model bytes (SHA-256
`4a2681182c1771335779240e811fcfd291dab1b2738b175356e3a1e4b552439b`).
The original v0.3 architecture file has no changes. Both containers are left running
for inspection, with the baseline model active.

Limits/deviations: Backstage is deferred with rationale in the conformance note;
the model uses a small POC vocabulary over JSON/HTTP. Tests establish this reference
behavior only; no AAP or replacement-orchestrator assessment was performed. Git
history for the new artifacts remains to be established by committing the changes;
no commit or push was made. Exact artifact content versions are already enforced
by SHA-256 bindings. No production readiness or full v0.3 conformance is claimed.
