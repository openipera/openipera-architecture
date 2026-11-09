# POC-04 — Independent authority comparison and compilation

## Hypothesis

The Service Architect's SM-DAG and Domain/Service SMEs' Lifecycle Cards (LCs)
can be independently authored, compared in both directions, and compiled into an
Execution DAG when a separate policy permits. An LC dependency that matches
architectural decomposition is meaningful corroboration, not an invalid duplicate.

This new experiment follows [POC-03](../poc-03/README.md), which rejected such
overlap. POC-03 remains an unchanged experimental record. POC-04 uses its useful
General Purpose Compute shape and an independent local implementation; it imports
no earlier POC code or shared framework.

The [Compilation Architecture](https://github.com/openipera/openipera-architecture/blob/a6bfc122a9c8793ac0249645f6bf7691b3f1f5a5/docs/IPERA_Service_Model_Compilation_Architecture.md)
defines the larger source → compile → link → execute pattern. POC-04 tests its
model comparison and compilation semantics. It does not select or evaluate a
production platform, and does not execute automation.

## Inputs and output

| Path | Role |
|---|---|
| `model/sm-dag.json` | Architect's persistent decomposition; never execution order |
| `model/lifecycle-cards.json` | SME assertions about Service Node requirements and AN automation identity |
| `model/policy-*.json` | Explicit POC policy listing discrepancy classes that block compilation |
| `automation/records/*.json` and `automation/artifacts/*` | UUID identities and example implementations in committed Git |
| `runtime/smv.py` | Validates, compares, applies policy, and compiles |
| `tests/oracle.json` | Test-only expected graph, never loaded by the compiler |
| `evidence/` | Saved source pairs, policy, findings, compiled outputs and historical regressions |

Every SM-DAG node has one separate companion LC. Only Service Node LCs may list
`service_dependencies`, and each target must be a Service Node. AN LCs terminate
service resolution and carry a human-readable `automation_name` plus UUID
`automation_id`; Service Node automation fields are null. SMV verifies each AN
UUID against regular committed Git records and artifacts. It ignores staged,
untracked and dirty registry content. Friendly names are not lookup keys. The
compiled graph carries **symbolic UUIDs**; separate `binding_evidence` documents
what committed implementation the validator verified. Runtime implementation
selection and executable pipeline assembly belong to the later linker role.

## Forward and reverse comparison

For each Service Node LC, the SMV compares the SME's dependency targets with the
Service Nodes reachable by **direct or transitive** decomposition from that node.
Atomic descendants are excluded from this comparison. Each unioned pair receives
one status:

| SM-DAG | LC | Status |
|---|---|---|
| Yes | Yes | `CORROBORATED` |
| Yes | No | `UNCORROBORATED` |
| No | Yes | `UNMODELED` |
| No | No | No finding |

The SMV reports what each authority asserted and does not infer why they differ.
The baseline deliberately contains all three reported states: GPC → Compute is
corroborated; GPC → VM is uncorroborated; VM → Storage is unmodeled. Storage →
Domain is asserted by neither and produces no finding.

This comparison scope is an explicit POC choice. It treats transitive
architectural membership as an assertion about a relationship. A future
architecture decision may refine which levels are considered comparable. No
final governance policy is selected here.

## Validity, agreement, policy and compilation

Structural failures, bad LC bindings, unknown references, invalid or unresolved
UUIDs, and cycles deny the model regardless of policy. A structurally valid model
may have findings: `model_valid: true` and `model_agreement: DISCREPANCIES` can
coexist. The default demonstration policy `{ "block_on": [] }` permits compilation
and reports all findings. The blocking example `{ "block_on": ["UNMODELED"] }`
denies compilation because the baseline contains that class; its result retains
`model_valid: true` and findings but contains no partial DAG. A policy can also
block `UNCORROBORATED`. `CORROBORATED` cannot be treated as a blocking discrepancy.

In a compiled result, Service vertices represent completion milestones and ANs
represent actions. Child completion precedes parent completion. An LC dependency
gates the dependent service's completion and its direct terminal ANs; nested
services use their own LCs. Decomposition is not authored execution order. These
realization choices were inherited from POC-03 where compatible and remain an
explicit interpretation for architecture review. An overlap between decomposition
and LC dependency may create the same completion edge for two reasons; the output
records both reasons without duplicating the edge. Cycles from either source or
from their combination still deny compilation.

## Running and reviewing

Python 3.14 and Git are sufficient. From the repository root:

```sh
python3 -m unittest discover -s poc-04/tests -v
python3 poc-04/runtime/smv.py \
  --model poc-04/model/sm-dag.json \
  --lcs poc-04/model/lifecycle-cards.json \
  --policy poc-04/model/policy-permissive.json \
  --repo . --ref HEAD --out /tmp/ipera-poc04-permissive
python3 poc-04/runtime/smv.py \
  --model poc-04/model/sm-dag.json \
  --lcs poc-04/model/lifecycle-cards.json \
  --policy poc-04/model/policy-block-unmodeled.json \
  --repo . --ref HEAD --out /tmp/ipera-poc04-blocked
```

Use fresh output paths. A successful compilation exits 0 and writes `result.json`
and `review.md`; denied compilation exits 2 and writes diagnostics and findings
without a DAG. The selected Git ref is pinned to a commit and reported with
input hashes. The Markdown review includes a forward/reverse comparison table,
Mermaid graph and parallel layers. The graph is derived at run time, never stored
as an authoritative input.

For reproducible saved evidence, use fresh paths:

```sh
python3 poc-04/tests/conformance.py --out /tmp/ipera-poc04-conformance
python3 poc-04/tests/regression.py --out /tmp/ipera-poc04-regression
```

The committed [conformance evidence](evidence/conformance/summary.json) includes
baseline, blocking policy, LC-only mutation, structure-plus-LC mutation,
unresolved UUID denial, and implementation-only binding mutation. Each case
saves its exact model, LCs, policy, registry snapshot, JSON result and SME review.
The isolated registry commits are retained in `automation-snapshots.bundle`.
The test-only oracle checks exact nodes, edges and layers; runtime logic has no
service names or expected order baked in. Unit tests additionally cover all
requested invariants, neither-asserted pairs, nonmutation of both sources,
policy selection, CLI denial, cycle checks and Git snapshot behavior.

See [validation record](evidence/VALIDATION.md).

## Limits and architectural questions

The POC demonstrates semantic comparison, policy gating, fail-closed validation
and graph compilation. It does not provision infrastructure, run automation,
implement the linker/runtime, prove implementation quality, or define production
governance. The current comparison treats every transitive service descendant as
an architect assertion. The MVM does not prescribe exactly how that scope should
be narrowed for large models; the choice is documented for Chat review rather
than silently generalized. Compilation results are whole-model results, not
per-request instances. Shared nodes are compiled once, without a separate
instance model.
