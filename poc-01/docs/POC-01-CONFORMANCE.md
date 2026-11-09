# POC-01 architecture and conformance boundary

> Historical POC-01 record. POC-02 supersedes this schema and test. See
> [POC-02](../../poc-02/docs/POC-02-CONFORMANCE.md): the persistent Service Dependency Model and
> the dynamically derived Execution DAG are distinct artifacts.

Baseline: the repository's unchanged [IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md](https://github.com/openipera/openipera-architecture/blob/fa0bfcd10de70be07315b4c7dd758d3248f6237a/docs/IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md),
draft v0.3. This is an executable reference experiment, not a new IPERA product or a
claim to implement every v0.3 capability.

| Responsibility | Location / contract |
|---|---|
| Authoritative persistent Service Dependency Graph | `model/service-model.json`, host-backed read-only mount in the independent HTTP model container |
| Model access | HTTP GET returns one JSON snapshot per request; no authoritative model mount or copy in orchestrator image |
| Orchestration | `runtime/engine.py`: reachable-node traversal, validation, Python `graphlib.TopologicalSorter`, parallel execution of each ready layer |
| AN binding | Each atomic model node's `binding`: external artifact path plus SHA-256 content version |
| Executable automation | Separate Git-versionable `artifacts/v1/record.py`; deterministic action result; no service topology |
| Execution capability | `runtime/execution.py`: path/digest validation and bounded Python subprocess, no dependency knowledge |
| Evidence | Host-backed `evidence/`: append/flush/fsync per event; request ID, sequence, times, model snapshot/hash, plan, action outputs and exit codes |

JSON and HTTP are standard encodings/protocols; the tiny node vocabulary is a documented
POC contract, **not an IPERA standard or native Backstage schema**. The model file and
artifacts live in separate directories in the same Git repository for ease of review.
Artifact hashes pin exact bytes, independently of mutable filenames or branch names.
Commit the delivered files together to establish their Git history; no remote VCS is required.

Backstage is deferred because its generated application, Node/Yarn build, and catalog
setup are disproportionate to proving four actions. This is a scope judgment based on
the [official standalone setup](https://backstage.io/docs/getting-started/) and
[container build](https://backstage.io/docs/deployment/docker/) instructions, not a
claim that Backstage cannot satisfy the role. A future Backstage/ServiceNow adapter can
return this snapshot contract at `MODEL_URL`, preserving authority in that repository.
It must map model relationships and AN bindings without maintaining a second static workflow.

The orchestrator contains no A/B/C/D/E identifiers or service-specific plan. Its plan
is derived afresh and is evidence of one request, never input to a future request.
The E test demonstrates external composition authority: identical runtime and artifact
bytes produce a new action set solely because persistent model knowledge changed.
It establishes this narrow reference behavior; it does not yet prove replacement by
another orchestrator, full v0.3 conformance, or AAP suitability.

Minimal scope: one request shape, one lifecycle realization, no elaborate LCs, no input
propagation, no retries/rollback/recovery, no deduplication across requests. Layer barriers
can wait for unrelated actions; they preserve correctness without an optimized scheduler.
Invalid reachable graphs fail before any automation. Action failures block later layers;
siblings already running finish. Processes killed abruptly may leave incomplete evidence.
Trusted local demo only; standard-library HTTP server and script execution are not a
production security boundary. No new enterprise services or licenses are required.

`tests/conformance.py` freezes the observable model-only-change contract for subsequent
product evaluations. `tests/test_engine.py` covers invalid graphs, failed prerequisites,
non-callable ANs, embedded-command rejection, and artifact integrity/path boundaries.
