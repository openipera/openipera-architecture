# IPERA — Deterministic Realization from a Dynamic Service Model

## The Question

OpenIPERA treats the Service Model as evolving authoritative knowledge. The SM-DAG, Lifecycle Cards, and automation bindings may change independently, potentially through the actions of multiple concurrent authors.

This raises a fundamental question:

> **How can OpenIPERA establish that a request-specific Service Object Graph (SOG) was compiled from consistent, validated service knowledge when that knowledge may change during validation or compilation?**

OpenIPERA is responsible for identifying the knowledge being validated and compiled, detecting inconsistencies between those inputs, and rejecting compilation when consistency cannot be established.

**OpenIPERA neither imposes nor prescribes a particular concurrency-control mechanism**, including locking, snapshots, transactional repositories, or authoring serialization.

Control over concurrent modifications, publication of authoritative revisions, and operational change approval belongs to **IPERA Governance**, implemented according to the consuming organization's change-control policies.

### Open Architectural Concern — Concurrent Authoring and Change Control

The implications of multiple authors concurrently modifying the SM-DAG and Lifecycle Cards require further examination. It remains to be established whether the existing validation and compilation integrity checks are sufficient, or whether particular operational environments require stronger change-control guarantees.

OpenIPERA must expose detectable inconsistencies. It must not silently assume that the consuming organization's change-control processes eliminate concurrency risks. In particular, comparing revision identifiers alone does not prove that all inputs were consistent throughout compilation.

> **Foundational principle: OpenIPERA verifies the consistency of the knowledge it compiles. IPERA Governance determines how that knowledge is changed, published, and authorized.**

---

## 1. The Service Model Is Living Knowledge

The authoritative Service Model represents the organization's current understanding of how services are defined, decomposed, and realized.

Its knowledge evolves as service requirements, dependencies, and realization capabilities change.

The principal architectural constructs are:

- **SM-DAG:** Expresses service definitions and decomposition relationships.
- **Lifecycle Cards:** Express service realization knowledge, including dependencies, lifecycle obligations, and references to atomic automation capabilities.
- **Automation Registry:** Independently maps stable automation capability identities to implementation references. It supports realization but is not itself part of the Service Model.

Changes to the SM-DAG, Lifecycle Cards, or automation implementations do not retroactively modify previously compiled SOGs or the historical evidence of completed realizations.

Such changes may, however, affect whether a previous realization remains operationally acceptable under current governance policy.

Multiple authors may contribute to this evolving knowledge. OpenIPERA does not prescribe their organizational roles, authoring workflow, or concurrency-control mechanisms.

> **The Service Model is living knowledge. A change to that knowledge must not silently rewrite the historical basis of an earlier realization.**

---

## 2. Identity, Revision, and Validation State

OpenIPERA mandates an internal versioning and validation schema for identifying and verifying the **state of its internal versions**. This is Service Model version state, not infrastructure runtime state or operationally approved state.

The schema distinguishes:

- **Stable object identity:** Which architectural construct is represented, independently of revisions to its definition.
- **Object revision identity:** Which version of that construct's authoritative definition is represented.
- **Aggregate revision identity:** Which combination of constituent revisions is represented by a Service DAG, the complete SM-DAG, or the Lifecycle Card Registry.
- **Validation-run identity:** Which SMV evaluation occurred, including the exact input-version set evaluated and its validation findings and status.

The mandatory versioning hierarchy covers:

| Construct | Required identity and revision semantics |
|---|---|
| Complete SM-DAG | Stable graph identity and a revision identity that changes when its constituent structure or represented revisions change |
| Constituent Service DAG (e.g., Networking, Storage, Application) | Stable identity and a revision reflecting its structure and constituent revisions |
| Service Node or Atomic Node | Stable `node_id` and independently identifiable revision of its authoritative definition |
| Lifecycle Card Registry | Stable registry identity and a revision reflecting the set and revisions of its cards |
| Individual Lifecycle Card | Stable `lc_id` and independently identifiable revision of its realization knowledge |
| Automation capability | Stable `automation_id` distinct from the revision of its implementation; automation binding resolution remains an independent registry responsibility |
| SMV validation run | Unique run identity, exact evaluated input-version identities, and validation result |

Changing an individual object advances the applicable object revision and the revisions of aggregates whose represented contents have changed. It does not automatically revise unrelated objects.

**The SMV MUST associate each validation result with the exact combination of authoritative input revisions it evaluated.** The Compiler MUST reference the applicable SMV validation identity and establish that the actual compilation inputs correspond to the validated input-version set. It MUST reject compilation when that correspondence cannot be established.

Version identifiers alone do not prove that underlying content is unchanged. Implementations must provide sufficient integrity verification for the revision identities to be meaningful. The specific version-number format, repository technology, content-verification technique, and concurrency-control mechanism are not prescribed here; detailed schema and integrity mechanics remain to be specified.

### OpenIPERA Conformance Requirement

OpenIPERA's internal versioning and validation schema is mandatory, not an optional organizational governance feature.

A conformant implementation **MUST** maintain and enforce the prescribed identity, revision, and validation-state semantics. Organizations **MAY** use these identities and results within their own governance, change-control, publication, and operational processes.

Organizations may extend the schema or use different underlying technologies provided the mandatory semantics remain intact. An implementation that disables, bypasses, or materially alters those semantics **MUST NOT** be represented as an **OpenIPERA-conformant implementation**.

This conformance requirement does not prescribe organizational change-control procedures or imply that OpenIPERA owns operational state, historical SOG retention, or execution evidence retention.

> **Identity establishes what an object is. Revision establishes which definition is represented. Validation identity establishes which combination of internal versions was evaluated.**

---

## 3. Validation and Compilation Consistency

OpenIPERA separates Service Model validation from request-specific compilation.

The Service Model Validator (SMV) evaluates authoritative service knowledge and produces a uniquely identifiable validation result associated with the exact internal version state evaluated.

The Compiler consumes applicable validated service knowledge together with request context to derive a request-specific Service Object Graph (SOG).

```text
AUTHORITATIVE SERVICE KNOWLEDGE
    SM-DAG + Lifecycle Cards
              |
              v
      INTERNAL VERSION STATE
              |
              v
             SMV
      Validate + Report
              |
              v
      VALIDATION IDENTITY
      + Input Version Set
      + Validation Results
              |
              v
           COMPILER <---- Request Context
              |
              v
             SOG
      Request-Specific Obligations
```

The Compiler **MUST** establish that the actual service knowledge used for compilation corresponds to the input-version set associated with the referenced SMV validation result.

If the versions or their underlying contents cannot be reconciled with the validated inputs, compilation **MUST** be rejected and the inconsistency reported.

Changes to the authoritative SM-DAG or Lifecycle Cards during validation or compilation must not silently alter the knowledge used to produce a SOG.

OpenIPERA does not prescribe locking, snapshots, authoring serialization, or another specific concurrency-control mechanism. Organizations determine their change-control procedures through IPERA Governance.

A compilation may reference an earlier validated version set if the required knowledge remains available and applicable governance policy permits its use. A successful SMV validation alone does not grant governance authorization.

> **The SOG represents obligations derived from identifiable, validated service knowledge—not a continuously changing view of the live Service Model.**

---

## 4. Linking Resolves Automation Implementations

The Execution DAG contains stable automation capability identities:

    automation_uuid

At link time, the orchestrator resolves those identities against the Automation Registry to concrete implementations.

    automation_uuid X
            │
            ▼
    Automation Registry
            │
            ▼
      repo / artifact
            │
            ▼
    immutable implementation revision
    93fc27c...

A branch such as `main` is insufficient for deterministic reconstruction because it can move.

The linked realization therefore records the immutable implementation revision actually selected.

---

## 5. A Realization Has Immutable Provenance

The resulting chain is:

    APPROVED CHANGE
          │
          ▼
    SERVICE MODEL REVISION
          │
          ├── exact SM-DAG
          │
          └── exact LC deck
          │
          ▼
    SMV COMPILATION
          │
          ▼
    EXECUTION DAG
          │
          ▼
    AUTOMATION UUIDs
          │
          ▼
    LINK / RESOLUTION
          │
          ▼
    IMMUTABLE AUTOMATION REVISIONS
          │
          ▼
    EXECUTION
          │
          ▼
    REALIZED SERVICE INSTANCE

The realization record therefore needs sufficient provenance to answer:

> **Exactly what knowledge and automation produced this service instance?**

Conceptually:

    Realization
    ────────────────────────────────────

    instance_uuid
    request/change identity

    service_model_revision
            │
            └── reconstructs exact
                SM-DAG + LC deck

    execution_dag / compilation identity

    automation bindings
            │
            ├── automation_uuid A
            │      └── implementation revision X
            │
            ├── automation_uuid B
            │      └── implementation revision Y
            │
            └── automation_uuid C
                   └── implementation revision Z

    execution evidence

---

## 6. Git Is an Implementation, Not an Architectural Requirement

Git happens to satisfy these requirements extremely well.

A Git commit naturally represents an immutable point-in-time version of a collection of related artifacts. If the SM-DAG and Lifecycle Cards reside together under version control, a single Service Model commit can identify the exact mutually consistent deck used by a compilation.

For example:

    Service Model @ 7f31c8a
            │
            ├── SM-DAG
            ├── LC-A
            ├── LC-B
            ├── LC-C
            └── ...

Reconstructing the Service Model used for that realization becomes conceptually equivalent to retrieving revision `7f31c8a`.

But IPERA should specify the **capability**, not Git:

> **The authoritative Service Model Repository MUST provide immutable point-in-time revisioning sufficient to reconstruct the exact Service Model inputs used for a realization.**

Git is one implementation capable of satisfying that requirement. Another repository technology could satisfy it if it provides equivalent semantics.

The same principle applies to automation implementations.

---

## 7. Relationship to State

This also helps separate the different meanings of **state** that prompted the discussion.

    MODEL STATE
    "What knowledge did IPERA use?"

            │
            │ realization
            ▼

    APPROVED STATE
    "What configuration was approved
    and successfully realized?"

            │
            │ compare with
            ▼

    OBSERVED STATE
    "What exists right now?"

            │
            ▼

    CONFORMANCE / DRIFT
    "Does what exists correspond to
    what was approved?"

The LC deck is therefore **not itself current infrastructure state**.

It is the versioned service knowledge used to derive a particular realization.

The CMDB may maintain Approved State and Observed State, while the realization provenance provides the immutable connection back to the Service Model and automation that produced the Approved State.

This distinction is also important because different execution technologies have different notions of state.

Terraform maintains its own persistent implementation state. Ansible does not maintain state in the same sense; with Ansible, the governed workflow and its inputs establish what was intended to be realized.

IPERA therefore cannot define Approved State in terms of an execution technology's native state mechanism.

Instead, IPERA must maintain the architectural distinction between:

- what was approved,
- what realization knowledge was used,
- what automation implementation was executed,
- what was successfully realized,
- and what is subsequently observed.

---

# Architectural Principles

**1. The Service Model is mutable knowledge; realization provenance is immutable.**

**2. Identity and revision are separate concerns. Identity establishes what an architectural object is; revision establishes which version participated in a realization.**

**3. Every realization MUST identify an immutable Service Model revision sufficient to reconstruct the exact SM-DAG and LC deck from which it was compiled.**

**4. Every linked automation capability MUST resolve to an immutable implementation revision sufficient to reconstruct the implementation that was executed.**

**5. Deterministic reconstruction does not require freezing the live Service Model. It requires preserving immutable references to the knowledge and implementations used at the time of realization.**

**6. Version-control technologies such as Git are implementations of these requirements, not architectural prerequisites.**

---

## Short Answer to the Original Question

> **The deck can change. The deck used for a realization cannot.**

Or, stated more formally:

> **IPERA does not freeze the Service Model. It freezes the provenance of each realization.**