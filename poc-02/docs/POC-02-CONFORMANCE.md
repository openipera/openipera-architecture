# POC-02: persistent knowledge versus derived execution

> **The Service Dependency Model contains persistent dependency knowledge. The
> Execution DAG is derived dynamically for a particular realization. They are not
> the same artifact.**

POC-01 demonstrated that model edits change execution, but its representation and
terminology did not make this distinction clear enough. POC-02 exposes the derivation
as a separately inspectable, request-scoped graph with an independent test oracle.
The provisional v0.3 source document is preserved; these notes record the POC-02 refinement.

## Three fields, no service-node semantics

The authoritative `model/service-model.json` is a list of individually declared facts.
Each node has exactly `service`, `node`, and `dependencies`. A qualified reference is
`<Service>.<Node>`; declarations may refer across service boundaries. Declaration order
has no execution meaning. ANs contain neither code nor layers. No fields were added.
The exact-source SHA-256 serves as the content version, without a new version field.

The generic request `{"entry_point":"<Service>.AN-<Node>"}` selects a target and its
transitive prerequisites. It does not declare an AN service API or assign behavior
to `S-*` nodes. Service Node semantics remain an explicit next architectural question;
the current resolver rejects those nodes. All declarations receive schema/identity
validation; missing references and cycles are checked in the selected closure. Nodes
outside that closure are not executed. This does not certify unrelated subgraphs.

Names use simple letters, digits, underscores and hyphens; dots separate service and
node. Duplicate identities are rejected. Repeated identical dependency declarations
have set semantics. A failed closure cannot produce an execution plan or run actions.

## Logical and runtime separation

| Responsibility | Implementation |
|---|---|
| Persistent authoritative dependency facts | Host `model/service-model.json`, read-only in a separate HTTP container |
| Request snapshot | Fresh HTTP GET per request; exact bytes/hash saved before resolution |
| Resolver | `runtime/engine.py`: qualified identity indexing, recursive closure, missing-reference checking, cycle detection and topological layers |
| Derived Execution DAG | Fresh output: selected nodes, prerequisite-to-dependent edges, layers; never authoritative input for another request |
| Binding/version verification | Separate `artifacts/binding.json` plus existing SHA-256 validation in `runtime/execution.py` |
| Automation | Existing external Git-versioned `artifacts/v1/record.py`; receives a node name and returns a deterministic result |
| Evidence | Host `evidence/`: exact snapshot, JSONL events, Markdown with generated Mermaid |
| Expected DAG | `tests/oracle.json` only; absent from runtime image and absent from the server's mounts |

The three-field schema has no per-node implementation binding field. For this uniform
simulation, one external execution binding applies to every resolved AN, so extending
the model schema is unnecessary. The execution capability owns this stand-in binding;
it contains no composition facts. Artifact hash verification remains enforced for every
action. Distinct AN implementations would require a later explicit binding design; this
iteration does not invent it. The record script and Docker separation are unchanged.

The scheduler runs each computed layer concurrently (up to eight workers) and waits
before advancing. This is conservative scheduling: it may wait for unrelated work in
the current layer, but does not add those waits to the derived edge set. The full node,
edge and concurrency structure is available even before execution. No layer/order is
encoded in the model or runtime source.

## Conformance proof

The hand-authored oracle contains nine nodes, twelve directed edges, and four layers.
The HTTP test client loads the oracle separately; it never submits it to the server.
It compares exact node/edge sets and layer membership. Serial event order is insufficient:
an extra edge between existing layers can leave chronology unchanged and must fail the test.

All four mutations run against the same live resolver with unchanged runtime, artifact,
binding and Compose fingerprints. A new AN and new cross-service edge must change graph
semantics as expected. Missing references and cycles must return explicit diagnostics,
emit no action events and still produce Markdown evidence. Baseline model bytes are
restored even after test failure. The report's Mermaid node/edge sets are checked against
actual resolver output, preventing a hand-maintained picture from masking a wrong graph.

Model facts are not intrinsically free of graph structure: declared dependencies are
the source knowledge. The distinction is ownership, scope and artifact identity. The
resolver selects a realization closure, resolves cross-service identities, validates it,
reorients prerequisites into execution edges and computes concurrency. It is never given
precomputed layers, an execution workflow, or the expected output graph.

## Evidence and limits

Every handled realization request produces `<run_id>-execution-dag.md`, including
invalid JSON/request shapes and model-resolution failures. A fetched model also produces
an exact byte snapshot. Reports distinguish a valid derived graph from failed automation.
Missing-reference failures report cycle status as not determined, rather than claiming
cycle validation succeeded. A cycle path uses prerequisite-to-dependent arrow semantics.

Evidence survives container restarts via the host mount. Abrupt process termination or
an unwritable/full evidence directory can prevent a complete report; crash recovery is
outside this POC. No retries, rollback, desired-state evaluation, infrastructure targets,
production security, service contracts, or `S-*` lifecycle semantics are implemented.
POC-02 supersedes POC-01's active schema/request/test rather than maintaining two runtime
implementations. Original POC-01 evidence and historical notes remain available.
