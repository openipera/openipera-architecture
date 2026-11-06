# OpenIPERA — Proof-of-Concept Historical Retrospective

**Status:** Historical record, not a normative architecture specification or a POC-05 test plan.

## Purpose and evidence boundary

This document records the questions, implementation choices, demonstrated results, and limitations of POC-01 through POC-04. It is based on each experiment's committed README and its links to validation and conformance evidence. The original POC directories remain the authoritative experimental records; this retrospective does not revise their claims to match subsequent architectural decisions.

The experiments used terminology and semantics current at the time, including **Execution DAG**, and in some cases assigned compilation or graph derivation to the **SMV**. The current OpenIPERA architecture distinguishes **SMV validation**, **Compiler derivation of the Service Object Graph (SOG)**, **Orchestrator linking**, and **Execution Capability runtime**. Historical implementation behavior must not be mistaken for present normative requirements.

## POC-01 — External model-driven execution

**Question:** Can an external service model drive execution without a hard-coded service workflow?

**Implemented:** A Docker Compose demonstration with an external model server, a generic orchestrator, and separate artifact binding. A request for service A resolved prerequisites B, C, and shared D; the model declared dependencies rather than a fixed execution sequence. The conformance test changed only the external model to add atomic E, then reissued the request without rebuilding or restarting the orchestrator.

**Evidence reported:** The POC README describes ordered events, results, model snapshot/hash, resolved artifact hashes, persisted evidence, and a conformance test verifying D precedes B/C/E and A completes after its prerequisites. Shared D executes once per request.

**Limits:** Provisional v0.3 behavior; no real infrastructure, AAP, service catalog UI, reconciliation, or product-specific workflow. The experiment does not establish the later SM-DAG/LC/SOG architecture.

**Original record:** [POC-01 README](../poc-01/README.md), [conformance description](../poc-01/docs/POC-01-CONFORMANCE.md), [validation results](../poc-01/docs/VALIDATION.md).

## POC-02 — Distributed dependencies and inspectable graph derivation

**Question:** Can independently supplied dependency facts produce a derived, inspectable execution graph without an authored workflow?

**Implemented:** A generic resolver for fully qualified Atomic Node entry points, returning a derived DAG with nodes, edges, and parallel layers. The runtime generated Markdown/Mermaid evidence from resolver output. Test-only graph oracles were excluded from the runtime.

**Evidence reported:** Model-only mutations added an Atomic Node, introduced a cross-service prerequisite, and tested rejection of a missing dependency and a cycle. Conformance compared exact node, edge, and layer sets and checked that runtime and artifact fingerprints remained unchanged.

**Limits:** Only Atomic Nodes were resolved; Service Node semantics were deliberately rejected/deferred. A shared demonstration artifact/binding was not a production per-AN registry. No real infrastructure or production security was introduced.

**Original record:** [POC-02 README](../poc-02/README.md), [conformance description](../poc-02/docs/POC-02-CONFORMANCE.md), [validation results](../poc-02/docs/POC-02-VALIDATION.md).

## POC-03 — Independent Service Model Validator

**Question:** Can an independently callable validator consume an SM-DAG, companion Lifecycle Cards, and Git-backed UUID automation records to validate a model and derive realization relationships?

**Implemented:** A separate Python/Git experiment with SM-DAG decomposition, one companion LC per node, committed UUID-to-artifact registry records, strict validation, and derived graph output. The experiment's SMV also performed graph derivation, an historical combination of responsibilities that the current architecture separates.

**Evidence reported:** The README records a fixture of **28 nodes (17 Service Nodes, 11 Atomic Nodes)**, **28 LCs**, **11 automation identities**, and a derived graph of **47 edges in 17 parallel layers**. Reported tests included LC-only dependency changes, structure-plus-LC changes, implementation changes behind a stable UUID, unresolved UUID denial, cycle rejection, and deterministic derivation independent of input order.

**Limits and historical assumptions:** The experiment did **not** execute automation. Its implementation rejected AN service dependencies, constrained LC dependency targets to Service Nodes, and rejected some overlapping decomposition/dependency assertions. These were POC-03 interpretation choices, **not enduring architectural prohibitions**. Successful Git resolution did not establish artifact correctness, runtime success, or production governance.

**Original record:** [POC-03 README](../poc-03/README.md), [validation record](../poc-03/evidence/VALIDATION.md), [conformance summary](../poc-03/evidence/conformance/summary.json).

## POC-04 — Independent assertion comparison and compilation

**Question:** Can separately authored SM-DAG decomposition and SME Lifecycle Card assertions be compared, classified, policy-gated, and compiled without a hard-coded workflow?

**Implemented:** A separate experiment comparing LC service dependencies against direct/transitive decomposition relationships. It classified pairs as `CORROBORATED`, `UNCORROBORATED`, or `UNMODELED`, applied explicit policy to findings, and compiled a graph with service-completion milestones and Atomic Node action vertices. Symbolic automation UUIDs remained distinct from runtime implementation selection.

**Evidence reported:** The README describes permissive and blocking policy tests, LC-only and structure-plus-LC mutations, unresolved UUID denial, implementation-only binding changes, independent graph oracles, and cycle detection. The experiment showed that an overlapping decomposition/dependency assertion could be recorded as corroboration rather than automatically rejected.

**Limits and historical assumptions:** Comparison of *all transitive descendants* was an explicit experiment choice, not a settled universal semantic rule. Compilation was whole-model rather than request-specific. The POC did not implement a linker, runtime automation execution, service instance model, or production governance. Its source-authority terminology and prohibition on AN LC dependencies reflect the experimental design, not the current architecture.

**Original record:** [POC-04 README](../poc-04/README.md), [validation record](../poc-04/evidence/VALIDATION.md), [conformance summary](../poc-04/evidence/conformance/summary.json).

## Architectural learning across the experiments

| Experiment | Demonstrated progression | Boundary not yet established |
|---|---|---|
| POC-01 | Model-driven execution from externally maintained dependencies | Formal service knowledge model and lifecycle obligations |
| POC-02 | Derived and inspectable dependency graph, with model-only mutations | Service Node semantics and lifecycle cards |
| POC-03 | Independent validation of SM-DAG, LCs, and Git-resolvable automation identities | Clean validator/compiler responsibility split and revised dependency semantics |
| POC-04 | Comparison, policy gating, and compiled realization graph | Request-specific contract-bearing SOG, linking/runtime, and current governance semantics |

The sequence is evidence of architectural learning, not evidence that every later architectural property was implemented in an earlier POC. In particular, **a derived execution graph is not by itself proof of the full contract-bearing SOG now specified**.

## Unresolved questions carried forward

The current architecture and any subsequent conformance experiment should independently test:

- SMV validation separated from Compiler generation of a request-specific SOG.
- Valid AN Lifecycle Card service dependencies, including cross-domain relationships.
- Cycle detection across the combined decomposition and LC dependency constraints.
- Registry-to-artifact resolvability without equating validation with operational correctness.
- Service obligations beyond executable actions: governance, approvals, verification, evidence, and lifecycle conditions.
- Reuse of a cataloged service such as General Purpose Compute both directly and as a dependency of a higher-level service.
- Clear distinction among architecture ambiguity, incomplete implementation, and implementation defects.

These are **open conformance objectives**, not claims that POC-01 through POC-04 already demonstrated them. A future POC-05 plan and its actual results should be maintained separately from this retrospective.

## Preservation principle

**Do not rewrite historical POCs to make them appear compliant with a later architecture.** Preserve their inputs, hypotheses, code, test oracles, evidence, and documented limits. Use new experiments to test revised hypotheses.
