# IPERA Service Model Authoring Rules

## 1. Purpose

This document defines the normative construction rules for the three authoritative structures used by the IPERA Service Model:

```text
SM-DAG                 LC REGISTRY              AUTOMATION REGISTRY
   │                        │                          │
   │ decomposition          │ realization              │ implementation
   │ knowledge              │ knowledge                │ resolution
   └────────────────────────┴──────────────────────────┘
                            │
                            ▼
                           SMV
```

The Minimum Viable Service Model defines what a valid model contains. This document defines **how that model is constructed while preserving distributed authorship, catalog governance, and identity integrity**.

Service Owners and Domain SMEs author service knowledge and realization assertions within their respective areas of responsibility. Platform Engineering (PE) governs acceptance and publication of the Application Service Catalog; Infrastructure Platform Engineering (IPE) governs acceptance and publication of the Infrastructure Service Catalog. Catalog governance does not automatically confer authorship authority over domain assertions.

These rules are intentionally independent of any product or persistence technology.

---

## 2. Governing Principles

### 2.1 Construction Has Precedence

A Lifecycle Card cannot describe the lifecycle of a service-model construct that does not exist.

Therefore:

> **A service-model node MUST exist before realization content is authored in its companion Lifecycle Card.**

The required construction precedence is:

```text
1. DEFINE
   Responsible Service Owner / Domain SME creates an SM-DAG node.
             │
             ▼
2. INSTANTIATE
   Node creation atomically creates exactly one companion LC stub.
             │
             ▼
3. AUTHOR
   Responsible SMEs author decomposition and LC realization
   assertions within their respective areas of responsibility.
             │
             ▼
4. BIND
   When a node is atomic, its companion LC identifies the
   required automation capability.
             │
             ▼
5. RESOLVE
   automation_id resolves through the
   authoritative Automation Registry.
             │
             ▼
6. VALIDATE
   SMV independently validates authored service knowledge.
             │
             ▼
7. GOVERN
   Applicable PE or IPE catalog authority controls acceptance,
   publication, and authoritative catalog state.
```

The sequence expresses required precedence and distinct responsibilities, not a requirement that the entire SM-DAG hierarchy be completed before LC authoring begins. Decomposition and LC authoring may progress incrementally across responsible SMEs, provided each node and companion LC retain their identity association and the model satisfies validation requirements before publication or compilation.

SMV validation establishes model integrity; catalog governance determines whether validated service knowledge is accepted and published. Neither substitutes for the other.

### 2.2 Creation Authority Is Not Assertion Authority

> **Authority over an assertion is not authority over creation of the object containing that assertion.**

A responsible Service Owner or Domain SME creates an SM-DAG node, which atomically instantiates its companion LC stub. Creating that stub does **not** make the node creator authoritative for every realization assertion later placed in the LC.

The responsible Domain or Service SME remains authoritative for the realization assertions within their domain, subject to applicable catalog acceptance and publication governance.

Likewise, PE or IPE catalog publication authority does not, by itself, make that catalog authority the author of underlying service decomposition or realization assertions.

### 2.3 Identity Is Established Before Independent Assertions

The node-to-LC association MUST NOT depend upon human-readable names, later discovery, or fuzzy matching.

When an SM-DAG node is created, a unique `lc_id` MUST be created and:

1. stored on the SM-DAG node; and
2. used to instantiate exactly one companion LC stub.

For example:

```json
{
  "node_id": "storage",
  "name": "Storage",
  "node_type": "service",
  "lc_id": "lc-storage"
}
```

creates:

```json
{
  "lc_id": "lc-storage"
}
```

The LC stub establishes identity only. It is not a complete, compile-valid Lifecycle Card.

---

## 3. SM-DAG Authoring Rules

**Service Owners and Domain SMEs are authoritative for the service decomposition assertions within their respective domains, subject to acceptance and publication governance by the applicable Service Catalog authority.**

The following rules are normative:

1. An SM-DAG node MUST represent a service-model construct that the responsible service owner or SME asserts exists.
2. Every node MUST have a unique `node_id`.
3. Every node MUST have an explicit `node_type`: `service` or `atomic`.
4. Every node MUST reference exactly one unique companion `lc_id`.
5. Creation of a node MUST instantiate the companion LC stub before realization content is authored.
6. An SM-DAG edge means only **decomposes into**.
7. The SM-DAG MUST NOT encode execution order, workflow predecessors, workflow successors, or runtime sequencing.
8. A Service Node MAY decompose into additional Service Nodes or Atomic Nodes.
9. An Atomic Node is terminal with respect to SM-DAG decomposition; its Lifecycle Card may still declare service dependencies.
10. Decomposition MUST NOT be changed merely to make another independently authored Lifecycle Card assertion agree with it. Disagreement is preserved for SMV evaluation and applicable governance.

The responsible service owner or SME asks:

> **What does this service decompose into?**

They do not ask:

> What should execute next?

---

## 4. Lifecycle Card Registry Authoring Rules

The LC Registry contains companion Lifecycle Cards for SM-DAG nodes.

A Domain or Service SME is authoritative for the realization assertions placed in the LC, but the SME does not independently create the LC object.

The following rules are normative:

1. An LC MUST originate as the companion stub of an existing SM-DAG node.
2. An LC MUST NOT be created independently and later associated to a node by name.
3. Every completed LC MUST contain the `lc_id` established when its node was created.
4. Every completed LC MUST contain `node_id` as an independent assertion of the node it describes.
5. The LC `node_id` MUST match the node that references its `lc_id`.
6. A Lifecycle Card for either a Service Node or an Atomic Node MAY declare `service_dependencies`.
7. Every dependency target MUST identify an existing service-model node, whether Service Node or Atomic Node.
8. A service dependency declares a realization requirement, not execution sequencing.
9. An Atomic Node MUST NOT have further SM-DAG decomposition, but its Lifecycle Card MAY declare dependencies.
10. Dependency resolution MUST traverse applicable LC-declared dependencies regardless of the source node's type, subject to SMV cycle and reference validation.
11. A Service Node LC MUST have `automation_name: null` and `automation_id: null`.
12. An Atomic Node LC MUST provide both `automation_name` and immutable UUID `automation_id`.
13. An SME MUST NOT alter SM-DAG decomposition merely to eliminate disagreement with LC realization knowledge.
14. An SME MUST NOT silently omit a known dependency merely because it is absent from the SM-DAG.
15. Differences between decomposition assertions and LC-declared realization assertions MUST be preserved and reported by the SMV. Their disposition is determined by applicable governance policy; the SMV MUST NOT silently modify either authoritative source.

The SME asks:

> **What existing services are required to realize this service?**

The SME does not ask:

> What workflow should I build?

---

## 5. Automation Registry Authoring Rules

The Automation Registry is authoritative for resolving automation capability identity to implementation.

The following rules are normative:

1. Every automation capability referenced by an Atomic Node LC MUST have an immutable UUID `automation_id`.
2. `automation_id` is the authoritative machine identity of the automation capability.
3. `automation_name` is human-readable metadata and MUST NOT be used as authoritative identity.
4. Each registered `automation_id` MUST resolve to an identifiable, version-controlled automation artifact. The SMV MUST verify that the registry entry and its referenced artifact exist and are resolvable. This verification does not establish the artifact's operational correctness or executability.
5. Registry implementation attributes MAY include repository, version or commit, artifact path, execution type, entrypoint, and artifact hash.
6. Physical implementation attributes MUST NOT be embedded in the SM-DAG merely to locate automation.
7. Physical implementation attributes MUST NOT be embedded in an LC as substitutes for `automation_id`.
8. Moving an implementation, changing its path, or changing its version MUST NOT require changing `automation_id` when the same automation capability contract is preserved.
9. A materially different automation capability MUST receive a distinct automation identity.

**Automation identity represents a stable capability contract, not a particular implementation, version, repository, or execution technology.**
10. The Automation Registry MUST NOT define service decomposition, service dependencies, or execution order.

The Automation Registry answers:

> **What implementation currently satisfies this automation identity?**

It does not answer:

> What service requires this automation?

---

## 6. Required Construction State Transitions

A model may exist in an incomplete authoring state before it is valid for compilation.

```text
NODE CREATED
     │
     ├── SM-DAG node exists
     └── LC stub exists with lc_id only
              │
              ▼
LC AUTHORED
     │
     ├── node_id asserted
     ├── service_dependencies authored
     └── automation fields completed as required by node_type
              │
              ▼
AUTOMATION RESOLVED
     │
     └── Atomic automation_id resolves
              │
              ▼
SMV VALIDATION
     │
     ├── structure
     ├── identity
     ├── reconciliation
     ├── automation resolution
     └── policy
              │
              ▼
COMPILABLE MODEL
```

The existence of an LC stub does not imply that the model is ready to compile.

The SMV MUST reject incomplete companion LCs when compilation is attempted.

---

## 7. Prohibited Construction Patterns

The following patterns are non-conforming:

### Free-Standing LC Creation

```text
SME creates "Storage LC"
        │
        ▼
later searches for a matching graph node
```

**Prohibited.** Identity is established by node creation, not inferred later.

### Name-Based Association

```text
SM-DAG: "Storage"
LC:     "Storage"
        │
        ▼
assume they are the same object
```

**Prohibited.** Human-readable names are not authoritative identity.

### Workflow Leakage

```text
LC dependency:
"Run Network before Compute"
```

**Prohibited.** LCs describe service requirements, not execution sequence.

### Implementation Leakage

```text
Atomic Node:
repo/path/template-id/runtime-endpoint
```

**Prohibited.** The Atomic Node LC references the automation capability by identity. The Automation Registry resolves implementation.

### Agreement by Mutation

```text
SM-DAG and LC disagree
        │
        ▼
silently change one source until validation passes
```

**Prohibited.** Disagreement is evidence. The SMV reports it; governance determines disposition.

---

## 8. Minimum Authoring Invariants

Before a model is eligible for compilation:

- every SM-DAG node MUST have exactly one companion LC;
- every completed LC MUST correspond to exactly one SM-DAG node;
- no orphan LC may exist;
- node/LC identity bindings MUST be internally consistent;
- every LC service dependency MUST resolve to an existing Service Node;
- Atomic Node LCs MUST terminate service dependency resolution;
- every Atomic Node LC MUST reference a valid automation UUID;
- every referenced automation UUID MUST resolve through the authoritative Automation Registry;
- no authored structure may encode execution order as service-model truth.

These invariants establish construction integrity. Reconciliation between independently authored architectural and realization assertions remains a separate SMV responsibility.

---

## 9. Authoring Model Summary

```text
                  SERVICE ARCHITECT
                         │
                         │ creates
                         ▼
                      SM-DAG
                         │
                         │ node creation
                         ▼
                  COMPANION LC STUB
                         │
                         │ populated by
                         ▼
                DOMAIN / SERVICE SME
                         │
                         ▼
                    LC REGISTRY
                         │
                         │ Atomic Node automation_id
                         ▼
                AUTOMATION REGISTRY
                         │
                         ▼
                         SMV
                VALIDATE + RECONCILE
                     + COMPILE
```

The ownership boundaries are therefore:

```text
Service Architect       → decomposition assertions
Domain / Service SME    → realization assertions
Automation Registry     → implementation resolution
SMV                     → validation, reconciliation, compilation
```

The construction rule is:

> **Define the service first. Instantiate its companion Lifecycle Card with it. Then let the appropriate SME describe how that existing service is realized.**
