# POC-04 validation — 2026-09-25

The repository's already-committed
[Service Model Compilation Architecture](../../docs/IPERA_Service_Model_Compilation_Architecture.md)
matched the handoff text verbatim. The MVM was revised surgically. POC-01,
POC-02 and POC-03 have no tracked changes from the starting commit `a3b69d5`.

| Check | Result |
|---|---|
| POC-04 unit, integration and CLI tests | 45 passed; [transcript](unit-tests.txt) |
| POC-04 conformance | Six cases passed; [manifest](conformance/summary.json) |
| Baseline graph | 28 nodes, 47 edges, 17 layers; exact independent test oracle match |
| Baseline comparison | 2 CORROBORATED, 22 UNCORROBORATED, 10 UNMODELED |
| Neither asserted | Storage → Domain produces no finding |
| Permissive policy | VALID with findings and compiled graph |
| Block UNMODELED | DENIED with `model_valid: true`, findings, no graph |
| Missing automation UUID | DENIED; valid UUID absent from Git cannot compile |
| LC mutation | Two prerequisite edges replaced, graph layers change |
| Structure-plus-LC mutation | New terminal AN and completion edge, SMV unchanged |
| Binding mutation | Same model, LC and symbolic UUID graph; committed implementation hash changes |
| POC-01 regression | 6 unit tests and live HTTP conformance pass in disposable copy |
| POC-02 regression | 12 unit tests and live HTTP conformance pass in disposable copy |
| POC-03 preservation | Tracked tree identical to `a3b69d5:poc-03` |

No new Docker stack exists for POC-04 because it validates and compiles without
running automation. POC-01/02 Docker builds, health checks, container unit tests
and container-to-container HTTP conformance were already captured in the unchanged
[POC-03 follow-up record](../../poc-03/evidence/docker-validation/README.md).
The POC-04 regression re-ran both historical suites on the host in disposable
copies; it did not edit or reclassify their original evidence.

The SM-DAG and LC comparison uses direct or transitive Service Node descendants.
That scope and the inherited service-completion semantics are the architectural
choices to validate before treating the POC as a general compilation contract.
Governance remains intentionally unresolved: `block_on` is only a demonstration
policy, not an IPERA production rule. The compiler verifies UUID presence and a
committed implementation but does not execute or link it. These limits are
explained in the [POC-04 README](../README.md).
