# POC-03 — Independent Service Model Validator

## Hypothesis and result

An SM-DAG containing decomposition only, separate Lifecycle Cards (LCs), and
UUID-identified automation held in Git are sufficient for an independent Service
Model Validator (SMV) to validate the model and derive its Execution DAG.

**Demonstrated for this fixture and the documented realization interpretation:**
28 model nodes (17 services and 11 Atomic Nodes), 28 companion LCs, 11 committed
automation identities, and a derived graph of 47 edges in 17 parallel layers.
No Execution DAG is stored in the authoritative inputs or predefined in the SMV.
Expected graphs exist only in tests. This experiment does not execute automation.

POC-01 established external model-driven execution. POC-02 established distributed
dependency derivation. Those completed experimental records are unchanged. This is
a new independent experiment with no imports from either POC and no shared framework.

## Inputs, implementation and outputs

| Path | Responsibility |
|---|---|
| `model/sm-dag.json` | Nodes and `[parent, child]` decomposition edges; no execution order |
| `model/lifecycle-cards.json` | One LC per node; service dependencies and atomic automation references |
| `automation/records/*.json` | Git-held UUID → implementation records, implementing the registry capability |
| `automation/artifacts/*.py` | Small simulated automation implementations; never executed by SMV |
| `runtime/smv.py` | Strict validation, Git resolution, generic graph derivation, JSON and Markdown output |
| `tests/oracle.json` | Independently authored expected baseline; never consumed by production code |
| `tests/test_smv.py` | Invariants, mutations, generic identities, Git and CLI tests |
| `tests/conformance.py` | Reproducible saved inputs, derived outputs and mutation evidence |
| `tests/regression.py` | Historical unit/live HTTP checks in disposable copies |
| `evidence/` | Recorded POC-03 results and this run's historical regression evidence |

Only Python's standard library and Git are required. Tested with Python 3.14.2 on
macOS. From the **repository root**:

```sh
python3 -m unittest discover -s poc-03/tests -v
python3 poc-03/runtime/smv.py \
  --model poc-03/model/sm-dag.json \
  --lcs poc-03/model/lifecycle-cards.json \
  --repo . --ref HEAD --out /tmp/ipera-poc03-review
```

The output directory must not already exist. Each invocation writes `result.json`
and `review.md`. Success exits 0; DENIED exits 2 and emits diagnostics without a
partial graph. An existing output directory is refused, preventing a new failed
run from being confused with an old VALID graph. Review Markdown contains Mermaid,
readable parallel layers, and the resolved UUID/artifact/commit/SHA-256 bindings.

The registry reads a **committed Git snapshot**, resolved once to a commit SHA.
Untracked, dirty and staged registry/artifact files cannot satisfy a binding. Commit
a registry change before selecting it with `--ref`. Model and LC input files may
be edited independently; their exact byte hashes are recorded by the CLI. Registry
records and artifacts must be ordinary committed blobs inside the automation
directory; symlinks, absent blobs and duplicate UUID records are denied. Git does
not need network access during validation. No separate database or etcd is used.

## Exact realization semantics tested

An SM-DAG edge means only *decomposes into*. List position does not imply order.
The SMV derives the following execution consequences, rather than copying
structural edges into a workflow:

1. An Atomic Node becomes an action vertex with its resolved UUID binding.
2. A Service Node becomes a **service completion milestone**, with no automation.
3. Every decomposed child must complete before its parent service is complete.
4. Each LC service dependency must complete before the dependent service completes
   and before that service's **direct terminal Atomic Nodes** can act.
5. Nested services have their own LCs. Dependencies are not implicitly inherited
   down an entire subtree. Sibling Atomic Nodes are unordered unless another
   modeled service relationship creates an ordering consequence.
6. The validator checks the complete supplied model and registry. It rejects
   decomposition cycles, service dependency cycles, and cycles produced by their
   combined realization consequences. No repair, pruning or arbitrary cycle break
   occurs. Topological layers group eligible vertices; they do not prescribe order
   within a layer.

The fixture places CPU, Memory and VM as siblings beneath Compute. VM depends on
CPU, Memory, Storage and Network and decomposes into Deploy VM. Network decomposes
into Allocate IP and Register DNS services; Register DNS depends on Allocate IP.
Both services terminate in their own AN. Boot depends on VM; Validate depends on
Boot; Domain and CI registration depend on Validate; CyberArk depends on Domain.
The baseline has no intentional cycle.

A service dependency **must target a Service Node**, never an Atomic Node. It
**must not restate decomposition**: a direct or transitive descendant is rejected
as a dependency target. Empty services with neither children nor dependencies are
also rejected in this experiment. Shared children/multiple parents and multiple
roots are supported; all architectural paths are derived from decomposition.
The implementation resolves the entire supplied graph, not a selected request.

`node_id`, companion `lc_id`, LC identity and LC ownership are unique. Registry
UUIDs are unique; UUID comparison is case-insensitive. Multiple ANs may reuse one
automation UUID. Friendly names need not be unique and are never lookup keys.
Fixture UUIDs are fixed constants: moving a node or changing an artifact does not
recompute them. Implementation paths and commit/hash metadata live in Git records
and derived outputs, not in LCs or the SM-DAG.

## Tests and evidence

Run the reproducible conformance and historical regression clients into fresh paths:

```sh
python3 poc-03/tests/conformance.py --out /tmp/ipera-poc03-conformance
python3 poc-03/tests/regression.py --out /tmp/ipera-poc03-regression
```

The conformance run saves each input pair, resolved registry, JSON result and SME
review. Its temporary Git snapshots are preserved in `automation-snapshots.bundle`,
so the test commit identities in results remain retrievable. To inspect them:

```sh
git clone poc-03/evidence/conformance/automation-snapshots.bundle /tmp/ipera-poc03-registry
# Select a recorded registry_commit from evidence/conformance/summary.json with --ref.
```

| Check | Evidence / result |
|---|---|
| Baseline | Exact test-only node, edge and layer oracle matches |
| Primary mutation | Only CI-registration LC dependency changes from Validate to CyberArk; exactly two edges removed and two added; layers change |
| Secondary mutation | New terminal AN and companion LC added under CMDB; existing automation UUID reused; graph gains node and completion edge |
| Binding mutation | Same LC and UUID, new committed implementation path/content; graph structure unchanged, resolved implementation/hash changes |
| Key negative case | Valid UUID `11111111-2222-3333-4444-555555555555` absent from Git → `UNRESOLVED_AUTOMATION`, DENIED |
| Generic derivation | Shuffled inputs produce identical results; renamed opaque identities and nonunique names preserve graph relationships |
| Snapshot authority | Dirty and staged bindings ignored; old commit still resolves old implementation |
| Preservation | POC-01/02 tracked files identical to pre-implementation commit `f8d49cc` |

All requested negative invariants have tests: missing LC; LC/node mismatch; missing
service target; duplicate node/LC/registry identities; service cycle; both atomic
binding fields null; name-only; ID-only; invalid UUID; unresolved valid UUID;
service binding populated; atomic dependencies nonempty. Additional tests cover
atomic dependency targets, decomposition-restating dependencies, malformed fields,
unknown children, duplicate edges/owners/dependencies, orphan LCs, atomic children,
decomposition and combined cycles, empty services, duplicate JSON keys and
missing/symlink artifacts. Invalid models remain byte-for-byte unmodified in memory.

See [validation record](evidence/VALIDATION.md),
[baseline review](evidence/conformance/baseline/review.md),
[unresolved UUID result](evidence/conformance/unresolved-uuid/result.json), and
[conformance manifest](evidence/conformance/summary.json).

## Architecture reconciliation and limits

The committed [MVM](https://github.com/openipera/openipera-architecture/blob/f8d49cc901726cbe097ba0c913c60bdd83bfc43d/docs/IPERA_Minimum_Viable_Service_Model.md) at `f8d49cc`
contains the agreed UUID semantics. Two example defects are **not propagated**:

- Section 14 makes `lc-storage.service_dependencies` refer to `an-provision-disk`.
  This violates the clarified service-only rule. Decomposition reaches that AN.
- Sections 12/14 repeat decomposition in service dependencies (for example GPC
  depending on its own decomposed services). The clarified rule separates those
  relationships; POC-03 rejects such redundant descendant references.

The older [functional requirements](https://github.com/openipera/openipera-architecture/blob/53ac73f967cb949b794eb2a4f20275b9f817e1e2/docs/IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md)
use the broader “Service Dependency DAG” terminology and describe derivation in
the orchestrator. POC-03 follows the later MVM's independent SMV and decomposition/
LC separation. Neither architecture document nor prior POC was rewritten here.

**For architectural validation:** the MVM does not fully specify prerequisite
inheritance, service completion milestones, empty services or multi-parent action
reuse. This POC makes its choices explicit above. In particular, a parent's LC
dependency gates its own terminal actions and completion, not every nested child
service's internal actions. Confirm this rule before treating the POC as a general
execution contract. An AN shared by multiple parents is one vertex with the union
of those parents' direct-action prerequisites, not multiple service instances.

Successful resolution proves an identifiable committed implementation exists.
It does not prove artifact correctness, infrastructure provisioning, runtime
success, access control, signature trust, lifecycle execution, reconciliation,
production scalability, or historical enforcement of identity immutability.
The binding mutation demonstrates identity stability; it does not prevent a human
from editing UUIDs in a future commit. No Ansible/Terraform/AAP/Airflow execution,
shared framework, database, deployment or production registry is introduced.
