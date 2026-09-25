# POC-03 validation record — 2026-09-25

## Environment and baseline

- Repository: `steve-jones62/ipera-demonstration-project`, existing branch `main`.
- Pre-implementation commit: `f8d49cc` (updated MVM).
- Python 3.14.2, macOS, standard library and installed Git; no new dependencies.
- Git fetch succeeded using the existing macOS Keychain helper. The additional
  configured `store` helper could not acquire its credential-storage lock in this
  sandbox; disabling that helper for the Git operation avoided changing credentials.

## Recorded checks

| Check | Actual result |
|---|---|
| POC-03 unit/integration/CLI suite | 39 tests PASS; [transcript](unit-tests.txt) |
| POC-03 conformance | 5 cases PASS; [manifest](conformance/summary.json) |
| Baseline expected graph | 28 nodes, 47 edges, 17 layers; exact independent oracle match |
| LC-only mutation | CI registration prerequisite changes Validate → CyberArk; exactly 2 edges replaced, layers change |
| Structural mutation | Additional terminal AN and LC under CMDB; 1 node and 1 edge added |
| Binding mutation | UUID and model unchanged; committed implementation path/content/hash changes |
| Well-formed absent UUID | DENIED, `UNRESOLVED_AUTOMATION`, no partial execution graph |
| POC-01 unit regression | All 6 tests PASS; [transcript](regression/poc-01-unit.txt) |
| POC-02 unit regression | All 12 tests PASS; [transcript](regression/poc-02-unit.txt) |
| POC-01 live HTTP conformance | PASS: baseline, model-only E mutation, original model restored |
| POC-02 live HTTP conformance | PASS: baseline, new AN, cross-service dependency, missing reference, cycle; original model restored |
| Compose configuration | `docker compose -f poc-01/docker-compose.yml config --quiet` and POC-02 equivalent both PASS |
| Historical preservation | `git diff --exit-code f8d49cc -- poc-01 poc-02` PASS; no edits to either experiment |

Historical live tests ran unchanged servers and conformance clients in disposable
copies, including real subprocess execution of those POCs' demonstration artifacts.
Only their new regression results are stored here. Original historical evidence
was neither replaced nor reclassified. POC-03 itself never executes automation.

The Docker client could not connect to `/Users/stevjon/.orbstack/run/docker.sock`
(the socket was absent). Container startup was **not** validated in this run.
Successful host execution and Compose parsing do not establish container startup.

## Reproducible evidence and boundaries

Each conformance case saves exact model/LC inputs, resolved committed registry,
JSON result and human review Markdown. `automation-snapshots.bundle` retains the
isolated test repository's commits and artifacts, including the binding mutation.
These are explicitly test commits, not the application repository's commits.
The conformance manifest fingerprints unchanged production runtime, fixture and
automation source files. Unit tests also cover staged/untracked binding rejection,
old-commit resolution, nonunique names and model identity renaming.

The baseline graph's Mermaid edges and readable layers are generated from its JSON
result. The Markdown source was inspected for node roles, labels, edges and binding
provenance; no separate browser-rendered visual layout test was performed.

## Architectural items returned for validation

1. **MVM documentation defects:** Section 14 references an AN through
   `service_dependencies`; sections 12/14 repeat decomposition as dependencies.
   POC-03 enforces service-only targets and rejects descendant targets. No architecture
   document was silently rewritten.
2. **Derivation interpretation:** Service vertices mean completion. Child completion
   precedes parent completion. LC dependencies gate the service's own direct ANs and
   completion; nested services use their own LCs, without implicit inheritance.
   This rule needs architectural confirmation beyond this bounded experiment.
3. **Additional choices:** Whole-model validation; empty services denied; shared ANs
   represented once with the union of prerequisites; multiple roots supported.
4. **Proven:** Independent validation, committed automation resolution, fail-closed
   denial, and generic derivation under those semantics, including all three mutations.
5. **Not proven:** Provisioning or automation execution, production artifact quality,
   operational success, historical immutability enforcement, scale, reconciliation,
   request/instance lifecycle handling, or production registry security.

Changes are confined to the root README and the new independent `poc-03/` tree.
The final implementation commit and push result are reported with the handoff, since
embedding a commit's own SHA in its contents would create a circular reference.
