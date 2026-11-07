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

The Service Object Graph (SOG) identifies the service realization obligations derived by the Compiler. Atomic automation obligations reference stable automation capability identities (`automation_id`), not necessarily particular implementation revisions.

The Orchestrator consumes the SOG and resolves applicable automation capabilities through the Automation Registry when constructing an executable workflow.

```text
SOG ATOMIC OBLIGATION
     automation_id
          |
          v
     ORCHESTRATOR
          |
          v
   AUTOMATION REGISTRY
          |
          v
  SELECTED IMPLEMENTATION
    + artifact identity
    + implementation revision
          |
          v
   EXECUTABLE WORKFLOW
```

The Automation Registry maintains the relationship between stable capability identities and their available implementations. An implementation may change without requiring a new automation capability identity, provided the capability contract remains valid.

Linking **MUST** establish the identity of the implementation actually selected for each automation obligation. That identity **MUST** be sufficient to distinguish the selected implementation from subsequent changes to registry bindings or implementation artifacts.

A mutable reference alone, such as a repository branch name, is insufficient to establish immutable implementation identity.

Changes to Automation Registry bindings after compilation do not retroactively change the SOG. Selection of an implementation revision and its continued eligibility for execution remain subject to applicable governance policy.

The mandatory internal versioning scheme for the SM-DAG, Lifecycle Cards, and validation identities does not prescribe versioning mechanisms for external automation implementation artifacts. Those artifacts remain governed by their respective automation authorities.

> **OpenIPERA defines the automation capability reference. The Orchestrator resolves the implementation. The Execution Capability performs the work.**

---

## 5. Compilation Provenance and Native Observability

**OpenIPERA is instrumented for observability by design, from its inception.** Observability is a foundational capability of OpenIPERA, distinct from the broader IPERA Observability pillar responsible for organizational service assurance.

The Compiler **MUST** embed a provenance manifest in every successfully compiled Service Object Graph (SOG). The manifest **MUST** identify the compilation, its request context reference, the SMV validation identity and validated input-version set, and the identities and exact revisions of every service-model component actually used to derive the SOG. This includes applicable Service DAGs, Service Nodes (SNs), Atomic Nodes (ANs), Lifecycle Cards (LCs), and stable automation capability identities (`automation_id`). The manifest **MUST** distinguish the complete validated input set from the components actually consumed in that compilation.

The SOG's automation capability references do not assert which implementation revisions will execute. Implementation selection occurs downstream during orchestration and linking, as described in Section 4.

```text
OPENIPERA SERVICE KNOWLEDGE
  SM-DAG / Service DAGs / SNs / ANs / LCs
                 |
                 v
          SMV VALIDATION
       Validation ID + Input Versions
                 |
                 v
             COMPILER <--- Request Context
                 |
          +------+------+
          |             |
          v             v
         SOG      PROVENANCE EVENT
    + Provenance     + Compilation ID
      Manifest       + Validation ID
                     + Component Versions
                           |
                           v
                  INTERNAL EVENT COLLECTOR
                           |
                           v
                    DURABLE BUFFER
                           |
                           v
                  CONFIGURABLE EXPORT
                           |
                           v
                 ORGANIZATIONAL TELEMETRY

DOWNSTREAM: ORCHESTRATION / EXECUTION
  Implementation selections, outcomes, and
  operational evidence are established outside
  OpenIPERA's compilation provenance.
```

Every OpenIPERA component **MUST** be instrumented to emit structured, correlated observability events appropriate to its responsibilities. At minimum, validation and compilation events **MUST** expose the relevant operation identity, component identities and revisions, outcomes, and actionable failure or rejection reasons. Events **MUST** be correlatable through validation, compilation, and applicable request identities. Sensitive request content, credentials, and secrets **MUST NOT** be included merely to satisfy provenance requirements.

OpenIPERA **MUST** provide an internal event collection and durable buffering capability for mandatory provenance events, with configurable asynchronous export and retry to organizational observability systems. Successful SOG publication **MUST NOT** be reported until its mandatory provenance event has been durably accepted by the internal buffer. External delivery confirmation is not a prerequisite for publication when durable internal acceptance succeeds. Failure to accept a mandatory event **MUST** be reported and **MUST** prevent successful publication.

The internal collector **MUST** support identifiable events, delivery tracking, retry behavior, and a defined buffer-retention and failure-handling policy. The architecture does not prescribe a specific collector product, telemetry destination, transport, Kubernetes workload type, or storage implementation. The reference deployment may leverage Kubernetes-native constructs.

OpenIPERA **MUST NOT** silently alter the provenance of an existing compilation when authoritative service knowledge changes. Its obligation to identify and durably record compilation provenance does not impose long-term storage of complete SOGs or historical model content. Organizations determine external collection, long-term retention, audit, replay, and operational evidence policies. Logging component versions does not by itself guarantee that historical component contents remain available for reconstruction.

The detailed provenance manifest, event schema, buffer durability/recovery semantics, and exporter contract remain implementation specifications to be defined consistently with OpenIPERA's mandatory internal versioning model.

> **The SOG carries its provenance. OpenIPERA durably records that provenance. Organizational observability systems retain and use it.**

---

## 6. OpenIPERA State vs. Operational State

OpenIPERA maintains internal state necessary to validate service knowledge, compile request-specific Service Object Graphs (SOGs), and establish the provenance of those compilations.

This includes component identities and revisions, validation identities and results, compilation identities, and mandatory observability records.

**This internal state must not be confused with the operational state of the infrastructure and services represented by the Service Model.**

OpenIPERA does not maintain authoritative desired configuration, realized infrastructure configuration, or observed runtime state merely by compiling a SOG.

Those responsibilities belong to the organization's operational systems and the broader IPERA Governance and Observability architecture.

The SOG carries its provenance, and OpenIPERA durably records mandatory provenance events; this does not require OpenIPERA to persist every complete SOG.

> **OpenIPERA knows what knowledge it used and what obligations it derived. Operational systems establish what was authorized, executed, and actually exists.**

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