# IPERA Minimum Viable Service Model

## 1. Purpose

This document defines the Minimum Viable Service Model (MVM) required to represent a service in IPERA.

The objective is not to define a complete enterprise service ontology. The objective is to establish the minimum architectural constructs necessary to:

1. Describe how a service decomposes.
2. Describe what other services are required to realize it.
3. Identify where service-model resolution terminates and automation begins.
4. Validate the model independently of any orchestration platform.
5. Derive an Execution DAG without authoring the Execution DAG itself.

The central principle is:

> **Model what is true about the service. Derive what must happen from that truth.**

The Service Model describes architectural truth.

The Execution DAG describes the operational consequence of that truth.

They are not the same artifact.

---

## 2. Three Relationships

The Minimum Viable Service Model distinguishes three fundamentally different relationships.

| Construct | Relationship | Meaning |
|---|---|---|
| Service Model DAG edge | **decomposes into** | This service is structurally composed of these subordinate service-model constructs. |
| Lifecycle Card service dependency | **depends upon service** | Realizing this service requires another service to be realized. |
| Execution DAG edge | **must be realized before** | One realization activity must precede another as a consequence of the model. |

The first two relationships are authored.

The third is derived.

This distinction is fundamental to IPERA.

A service author describes decomposition and service dependencies. The Service Model Validator derives the resulting execution relationships.

---

## 3. Service Model DAG

The Service Model DAG (SM-DAG) is the persistent architectural decomposition of a service.

It answers:

> **What does this service decompose into?**

An SM-DAG edge means only:

> **decomposes into**

It MUST NOT mean:

- execute before,
- execute after,
- requires completion of,
- workflow predecessor,
- workflow successor.

Execution ordering does not belong in the SM-DAG.

A simplified example:

```text
General Purpose Compute
   ├── Compute
   │    └── VM
   │         ├── CPU
   │         └── Memory
   ├── Storage
   │    └── Provision Disk
   ├── Network
   │    ├── Allocate IP
   │    └── Register DNS
   ├── Identity
   │    └── Register with Domain
   │         └── Join Domain
   ├── Security
   │    └── Register with CyberArk
   │         └── Onboard Account
   ├── CMDB
   │    └── Register CI in CMDB
   │         └── Create CI
   ├── Boot VM
   │    └── Power On VM
   └── Validate VM
        └── Run VM Validation
```

This representation says nothing about execution order.

It describes decomposition only.

---

## 4. Node Types

Every node in the SM-DAG has an explicit `node_type`.

The Minimum Viable Service Model defines two node types:

```text
service
atomic
```

A **Service Node** may decompose into additional service-model constructs.

An **Atomic Node** is the lowest-level service-model construct. It represents the boundary at which service-model resolution terminates and executable automation begins.

Every SM-DAG node also contains a unique `lc_id` identifying its companion Lifecycle Card.

Example Service Node:

```json
{
  "node_id": "storage",
  "name": "Storage",
  "node_type": "service",
  "lc_id": "lc-storage"
}
```

Example Atomic Node:

```json
{
  "node_id": "an-provision-disk",
  "name": "Provision Disk",
  "node_type": "atomic",
  "lc_id": "lc-an-provision-disk"
}
```

`node_type` is intentionally explicit.

The model does not attempt to infer whether a node is atomic merely by examining other attributes. Explicit node typing improves human readability and provides an independent assertion that can be validated against the companion Lifecycle Card.

---

## 5. Lifecycle Cards

Every SM-DAG node has exactly one companion Lifecycle Card (LC).

Lifecycle Cards are not nodes in the SM-DAG.

The relationship is:

```text
SM-DAG Node
     │
     │ lc_id
     ▼
Lifecycle Card
```

### Creation Precedence

Service-model construction has an explicit precedence.

> **A Service Model node MUST exist before realization knowledge for that node can be authored. Creation of an SM-DAG node MUST instantiate exactly one companion Lifecycle Card stub identified by the same `lc_id` referenced by the node.**

At creation time, the companion LC is intentionally only a stub:

```json
{
  "lc_id": "lc-storage"
}
```

The stub establishes identity and association only. It does not yet assert realization semantics and is not yet a compile-valid Lifecycle Card.

A Domain or Service SME subsequently authors the realization content of that already-created companion LC. The SME does not independently create an LC and then attempt to associate it with a Service Node by name.

Conceptually:

```text
Service Architect
      │
      │ creates node
      ▼
SM-DAG Node
      │
      │ atomically instantiates lc_id
      ▼
Companion LC Stub
      │
      │ SME authors realization knowledge
      ▼
Completed Lifecycle Card
```

This establishes the governing precedence:

```text
SERVICE EXISTS
      ↓
COMPANION LC EXISTS
      ↓
REALIZATION KNOWLEDGE IS AUTHORED
```

There is no Lifecycle Card, in the architectural sense, for a service-model construct that does not exist.

The Service Architect is authoritative for decomposition. Domain and Service SMEs are authoritative for realization assertions. Those assertions remain independent even though the companion LC object is instantiated as a consequence of node creation.

> **Authority over an assertion is not authority over creation of the object containing that assertion.**

The LC describes realization semantics associated with the node.

In the Minimum Viable Service Model, the LC contains:

```text
lc_id
node_id
service_dependencies
automation_name
automation_id
```

The `lc_id` associates the Lifecycle Card with the SM-DAG node.

The `node_id` provides an independent assertion of which SM-DAG node the card describes.

`service_dependencies` is populated only on LCs for Service Nodes and may reference
Service Nodes only. It records the Domain or Service SME's independent assertion of
what services are required for realization. Atomic Node LCs contain an empty list;
service dependency resolution terminates at their automation boundary.

The SM-DAG is authored by the Service Architect from the top down. Companion LC
objects are instantiated with their SM-DAG nodes; the realization assertions within
those LCs are authored by Domain or Service SMEs from the bottom up. A dependency
that matches direct or transitive decomposition may be intentional corroboration,
not redundant data.

`automation_name` provides the human-readable name of automation associated with an Atomic Node.

`automation_id` provides the immutable machine identity of that automation.

Every Lifecycle Card MUST contain both the `automation_name` and `automation_id` keys.

For a Service Node:

```text
automation_name = null
automation_id   = null
```

For an Atomic Node:

```text
automation_name = populated
automation_id   = populated UUID
```

The architectural location of the Atomic Node is not encoded in either automation field. That context is already represented by the Atomic Node's location in the SM-DAG and can therefore be derived.

---

## 6. Minimum Lifecycle Card

A minimum Service Node Lifecycle Card is:

```json
{
  "lc_id": "lc-storage",
  "node_id": "storage",
  "service_dependencies": [],
  "automation_name": null,
  "automation_id": null
}
```

A minimum Atomic Node Lifecycle Card is:

```json
{
  "lc_id": "lc-an-provision-disk",
  "node_id": "an-provision-disk",
  "service_dependencies": [],
  "automation_name": "provision-disk",
  "automation_id": "a8f21764-9e31-4e8c-91a5-3c572cb614ef"
}
```

### `automation_name`

`automation_name` is a human-readable name for the automation capability.

It is intended for:

- human recognition,
- logs,
- visualization,
- troubleshooting,
- documentation,
- operational presentation.

It is not required to be globally unique.

It MUST NOT be treated as the authoritative identity of the automation.

### `automation_id`

`automation_id` is the immutable machine identity of the automation capability.

It MUST be represented as a UUID.

The UUID is the authoritative identifier used to resolve the automation through the Automation Registry or equivalent binding mechanism.

The automation name and automation identity are deliberately independent.

For example, multiple automation capabilities could legitimately have:

```text
automation_name: provision-disk
```

while having different:

```text
automation_id
```

values.

Uniqueness is established by the UUID, not by the friendly name.

---

## 7. Service Dependencies

Lifecycle Cards declare **service dependencies**.

A service dependency means:

> **To realize this service, these other services must be realized.**

It does not mean:

> Execute this node after that node.

The distinction matters.

For example:

```text
Register with Domain [Validate VM]
```

means:

> Register with Domain depends upon the Validate VM service.

The model does not prescribe the resulting execution sequence.

The Service Model Validator determines the operational consequence of that assertion when it derives the Execution DAG.

The author therefore describes service truth rather than workflow.

Wrong:

```text
Execute Validate VM before Register with Domain.
```

Correct:

```text
Register with Domain [Validate VM]
```

The first authors execution.

The second authors a service dependency.

---

## 8. Cross-Branch Dependencies

Service dependencies may cross SM-DAG decomposition branches.

For example:

```text
General Purpose Compute
   ├── Compute
   │    └── VM
   ├── Storage
   └── Network
```

The VM Lifecycle Card may declare:

```text
VM [Storage, Network, CPU, Memory]
```

This does not require Storage or Network to be duplicated beneath VM in the SM-DAG.

The SM-DAG describes decomposition.

Lifecycle Cards describe service dependencies.

This separation allows architectural decomposition and realization dependencies to evolve independently.

---

## 9. Atomic Nodes and Automation

An Atomic Node is the lowest-level service-model construct in IPERA.

An Atomic Node represents a discrete lifecycle action and binds that action to an external, version-controlled automation artifact.

The Atomic Node does not contain executable automation.

The Atomic Node is the last service construct before automation begins.

Conceptually:

```text
Service
   ↓
Service
   ↓
Atomic Node
   ↓
Automation
```

The companion Lifecycle Card identifies the required automation using two independent attributes:

```text
automation_name
automation_id
```

`automation_name` is human-readable.

`automation_id` is an immutable UUID and is authoritative for machine identity.

For example:

```json
{
  "lc_id": "lc-an-provision-disk",
  "node_id": "an-provision-disk",
  "service_dependencies": [],
  "automation_name": "provision-disk",
  "automation_id": "a8f21764-9e31-4e8c-91a5-3c572cb614ef"
}
```

The `automation_id` MUST resolve through an Automation Registry or equivalent binding mechanism to a valid, version-controlled automation implementation.

Conceptually:

```text
Atomic Node
     ↓
Lifecycle Card
     ├── automation_name
     └── automation_id (UUID)
                  ↓
          Automation Registry
                  ↓
       Version-Controlled Automation
                  ↓
          Execution Capability
```

The Automation Registry may resolve the UUID to implementation attributes such as:

```text
repository
version / commit
artifact path
execution type
entrypoint
artifact hash
```

These attributes describe the implementation of the automation.

They are not the automation's identity.

They MUST NOT be embedded in the Service Model merely to locate the automation.

This allows the implementation to move between repositories, change versions, change paths, or potentially change execution technologies without changing the immutable automation identity referenced by the Lifecycle Card.

### Derived Architectural Context

The SM-DAG already establishes the architectural location of the Atomic Node.

Therefore, the full architectural context of an automation reference does not need to be persisted in `automation_id`.

For example, the model may contain:

```text
General Purpose Compute
   └── Storage
        └── Provision Disk
```

with:

```text
automation_name: provision-disk
automation_id:   a8f21764-9e31-4e8c-91a5-3c572cb614ef
```

A human-facing canonical representation such as:

```text
general-purpose-compute.storage.provision-disk.provision-disk-a8f21764-9e31-4e8c-91a5-3c572cb614ef
```

can be derived when useful.

It need not be stored.

This avoids duplicating architectural context and prevents an automation identity from changing merely because an Atomic Node is moved within the Service Model.

### Resolution Is Not Execution

Successful resolution of an `automation_id` establishes that the Atomic Node has an identifiable automation implementation.

It does not establish that the automation will execute successfully.

The Service Model Validator can establish:

```text
Atomic Node exists
        ↓
automation_name exists
        ↓
automation_id is a valid UUID
        ↓
automation_id resolves
        ↓
binding identifies automation implementation
```

Runtime execution establishes whether:

```text
automation executes successfully
```

Execution success and resulting evidence remain responsibilities of the execution capability and operational layers.

---

## 10. Intentional Validation Redundancy

The Minimum Viable Service Model intentionally contains independently asserted information.

This is not accidental duplication.

It allows the Service Model Validator to detect inconsistencies rather than silently infer architectural intent.

For example:

```text
node_type: service
automation_name: null
automation_id: null
```

is consistent.

Likewise:

```text
node_type: atomic
service_dependencies: []
automation_name: provision-disk
automation_id: a8f21764-9e31-4e8c-91a5-3c572cb614ef
```

is structurally consistent.

However, structural consistency does not yet establish realizability.

The UUID must also resolve through the authoritative Automation Registry or equivalent binding mechanism.

The governing rule is:

> **`node_type` expresses architectural intent. The companion Lifecycle Card provides independent evidence that the node satisfies the requirements of that type. The Service Model Validator MUST reject inconsistencies between the two.**

---

## 11. Minimum SMV Invariants

The Service Model Validator MUST reject structurally or semantically invalid models.

At minimum, the following conditions are invalid.

### Orphan Lifecycle Card

```text
Lifecycle Card exists
No SM-DAG node references its lc_id

DENIED:
Lifecycle Card has no corresponding Service Model node.
```

A Lifecycle Card MUST NOT be independently created for a service-model construct that does not exist.

### Missing Lifecycle Card

```text
SM-DAG node references lc_id
Lifecycle Card does not exist

DENIED:
SM-DAG node has no corresponding Lifecycle Card.
```

### Lifecycle Card / Node Mismatch

```text
SM-DAG node:
node_id = storage
lc_id   = lc-storage

Lifecycle Card:
lc_id   = lc-storage
node_id = network

DENIED:
Lifecycle Card does not describe the node that references it.
```

### Missing Service Dependency Target

```text
service_dependencies:
  - nonexistent-service

DENIED:
Lifecycle Card references an unknown service.
```

### Duplicate Identity

Duplicate identifiers that are required to be unique within their authoritative namespace MUST be rejected.

This includes duplicate SM-DAG node identities, Lifecycle Card identities, and automation UUIDs where the registry requires uniqueness.

### Service Dependency Cycle

A service dependency graph containing a cycle MUST be rejected.

The model is allowed to be wrong.

The validator is not allowed to pretend that it is right.

### Atomic Node With No Automation Binding

```text
node_type: atomic
automation_name: null
automation_id: null

DENIED:
Atomic Node has no automation binding.
```

### Atomic Node With Name But No Identity

```text
node_type: atomic
automation_name: provision-disk
automation_id: null

DENIED:
Atomic Node has an automation name but no immutable automation identity.
```

### Atomic Node With Identity But No Name

```text
node_type: atomic
automation_name: null
automation_id: a8f21764-9e31-4e8c-91a5-3c572cb614ef

DENIED:
Atomic Node has an automation identity but no human-readable automation name.
```

### Invalid Automation UUID

```text
node_type: atomic
automation_name: provision-disk
automation_id: not-a-valid-uuid

DENIED:
Atomic Node automation_id is not a valid UUID.
```

### Unresolved Automation Identity

```text
node_type: atomic
automation_name: provision-disk
automation_id: a8f21764-9e31-4e8c-91a5-3c572cb614ef

Automation Registry:
NOT FOUND

DENIED:
Atomic Node automation_id does not resolve to a registered automation binding.
```

### Service Node Bound Directly to Automation

```text
node_type: service
automation_name: provision-disk
automation_id: a8f21764-9e31-4e8c-91a5-3c572cb614ef

DENIED:
Service Node may not bind directly to automation.
Declare an Atomic Node.
```

### Atomic Node With Service Dependencies

```text
node_type: atomic
service_dependencies:
  - storage

DENIED:
Atomic Node declares further service dependencies.
Atomic Nodes terminate service-model resolution.
```

For an Atomic Node to be realizable, its companion Lifecycle Card MUST contain both an `automation_name` and a valid UUID `automation_id`, and that `automation_id` MUST resolve through the authoritative Automation Registry or equivalent binding mechanism.

---

## 12. Worked Example: General Purpose Compute

Consider the following decomposition:

```text
General Purpose Compute
   ├── Compute
   │    └── VM
   │         ├── CPU
   │         └── Memory
   ├── Storage
   │    └── Provision Disk
   ├── Network
   │    ├── Allocate IP
   │    └── Register DNS
   ├── Identity
   │    └── Register with Domain
   │         └── Join Domain
   ├── Security
   │    └── Register with CyberArk
   │         └── Onboard Account
   ├── CMDB
   │    └── Register CI in CMDB
   │         └── Create CI
   ├── Boot VM
   │    └── Power On VM
   └── Validate VM
        └── Run VM Validation
```

This is the SM-DAG.

It describes decomposition only.

Representative service dependencies might include:

```text
General Purpose Compute [Compute, Storage, Network, Identity, Security, CMDB]

Compute [VM]

VM [Storage, Network, CPU, Memory]

Identity [Register with Domain]

Security [Register with CyberArk]

CMDB [Register CI in CMDB]

Register with Domain [Validate VM]

Register with CyberArk [Register with Domain]

Register CI in CMDB [Validate VM]
```

These assertions still do not define a workflow.

They define service dependencies.

The Service Model Validator determines the resulting Execution DAG.

---

## 13. Concrete SM-DAG Representation

A portion of the preceding SM-DAG could be represented as:

```json
{
  "node_id": "general-purpose-compute",
  "name": "General Purpose Compute",
  "node_type": "service",
  "lc_id": "lc-general-purpose-compute",
  "children": [
    {
      "node_id": "storage",
      "name": "Storage",
      "node_type": "service",
      "lc_id": "lc-storage",
      "children": [
        {
          "node_id": "an-provision-disk",
          "name": "Provision Disk",
          "node_type": "atomic",
          "lc_id": "lc-an-provision-disk"
        }
      ]
    }
  ]
}
```

The SM-DAG says:

```text
General Purpose Compute
decomposes into
Storage
decomposes into
Provision Disk
```

It says nothing about when Provision Disk executes.

---

## 14. Concrete Lifecycle Card Registry

The corresponding Lifecycle Cards could include:

```json
[
  {
    "lc_id": "lc-general-purpose-compute",
    "node_id": "general-purpose-compute",
    "service_dependencies": [
      "compute",
      "storage",
      "network",
      "identity",
      "security",
      "cmdb"
    ],
    "automation_name": null,
    "automation_id": null
  },
  {
    "lc_id": "lc-storage",
    "node_id": "storage",
    "service_dependencies": [],
    "automation_name": null,
    "automation_id": null
  },
  {
    "lc_id": "lc-an-provision-disk",
    "node_id": "an-provision-disk",
    "service_dependencies": [],
    "automation_name": "provision-disk",
    "automation_id": "a8f21764-9e31-4e8c-91a5-3c572cb614ef"
  }
]
```

The Lifecycle Cards describe realization semantics.

The SM-DAG and Lifecycle Cards together constitute the minimum information required by the Service Model Validator to derive execution consequences.

---

## 15. Action-Oriented Services

Not every service-model construct represents a persistent infrastructure resource.

A service may represent an action or lifecycle operation.

Examples include:

```text
Boot VM
Validate VM
Register with Domain
Register with CyberArk
Register CI in CMDB
```

These remain Service Nodes when they have subordinate service-model constructs.

For example:

```text
Boot VM
   └── Power On VM
```

where:

```text
Boot VM       = service
Power On VM   = atomic
```

The Boot VM Lifecycle Card may declare service dependencies.

The Power On VM Lifecycle Card terminates service-model resolution and identifies automation:

```json
{
  "lc_id": "lc-an-power-on-vm",
  "node_id": "an-power-on-vm",
  "service_dependencies": [],
  "automation_name": "power-on-vm",
  "automation_id": "6e6c0e74-3dd8-48cf-8ea5-8939287c2648"
}
```

No additional `action` node type is required by the Minimum Viable Service Model.

---

## 15A. Independent Authority Comparison

The Service Architect authors the SM-DAG decomposition. Domain or Service SMEs
author LC realization requirements. These are independent authorities: the same
Service Node relationship may appear in both without being an invalid duplicate.

| SM-DAG | LC | SMV status | Meaning |
|---|---|---|---|
| YES | YES | CORROBORATED | Architecture and SME both assert the relationship. |
| YES | NO | UNCORROBORATED | Architecture asserts a relationship the SME did not. |
| NO | YES | UNMODELED | SME asserts a requirement absent from decomposition. |
| NO | NO | No finding | Neither authority asserts the relationship. |

The SMV compares architectural decomposition with the corresponding Service Node
LC in both directions. It reports discrepancies without inferring their cause or
altering either source. A discrepancy is information before it is an error. A
structurally valid model can contain unresolved disagreement. Governing policy
separately determines whether a finding is informational, requires review, or
blocks compilation. IPERA does not yet prescribe that governance policy.

---

## 16. Service Model Validator

The Service Model Validator (SMV) is a reusable IPERA capability that independently evaluates an authoritative Service Model, derives the resulting Execution DAG, identifies structural inconsistencies, and renders the graph for SME review and validation before runtime orchestration.

The SMV is the compiler of the Service Model. It reads the independently authored
SM-DAG and LCs, validates references and semantics, performs forward and reverse
comparison, diagnoses disagreements, and compiles the Execution DAG when policy
permits. It does not silently repair either authoritative source.

The SMV:

- consumes the model,
- does not own the model,
- validates SM-DAG structure,
- validates Lifecycle Card bindings,
- validates node-type invariants,
- validates service dependencies,
- validates automation identity structure,
- validates automation binding resolution,
- detects missing references,
- detects cycles,
- derives execution relationships,
- renders the result for human review.

The SMV MUST NOT silently repair semantic model errors.

Subject Matter Experts own domain truth.

The validator determines whether the supplied model is internally consistent and whether its declared Atomic Nodes can be resolved to identifiable automation implementations.

The SMV is independent of the eventual orchestration platform.

This makes it useful both as a model-validation capability and as a vendor-neutral conformance oracle.

---

## 17. Execution DAG

The Execution DAG is compiled output from the validated Service Model. It is derived.

It is not authored, persistent architectural truth, or itself an executable
pipeline. It contains derived realization relationships and symbolic automation
identities for later linking.

It answers:

> **What must happen, and in what dependency order, to realize this request?**

The SMV derives the Execution DAG from:

```text
Service Model DAG
        +
Lifecycle Cards
        +
validated automation bindings
```

The resulting graph may contain both Service Nodes and Atomic Nodes.

Execution relationships are consequences of:

- decomposition,
- service dependencies,
- Atomic Node boundaries,
- valid automation bindings.

The Execution DAG must be acyclic.

The persistent model may contain errors, including cycles.

Those errors are detected during validation.

The Orchestrator consumes the compiled Execution DAG, resolves the symbolic
automation identities to implementations, links the required modules into an
executable pipeline, and dispatches runnable work. The Execution Capability runs
that work and returns state and evidence. The SMV validates that an automation
identity resolves to a version-controlled capability; physical runtime linking
is the Orchestrator's responsibility. Changing the implementation behind the same
identity does not change Service Model truth.

**Architectural separation does not require product separation. The compiler,
linker, and runtime are distinct functional responsibilities, but a conforming
implementation may provide multiple responsibilities within a single platform,
provided the architectural boundaries and authoritative sources remain preserved.**

---

## 18. Authoring Rule

Service-model construction MUST follow the precedence defined in Section 5:

```text
DEFINE NODE
    ↓
INSTANTIATE COMPANION LC STUB
    ↓
AUTHOR LC REALIZATION CONTENT
    ↓
BIND ATOMIC NODE TO AUTOMATION, WHEN APPLICABLE
    ↓
VALIDATE / COMPILE
```

An SME populates the companion LC created for an existing node; the SME does not create a free-standing LC and rely on naming conventions or later matching to associate it with the graph.

The governing semantic authoring rule is:

> **Model service truth. Do not author execution order.**

A model author should ask:

```text
What is this service made of?
```

and:

```text
What other services must exist or be realized for this service to be realized?
```

The model author should not ask:

```text
What step should execute next?
```

That is a derived concern.

The distinction can be summarized as:

> **Service Model DAG: decomposition of intent. Execution DAG: realization of intent.**

Or:

> **The Service Model describes what is true. The Execution DAG describes what must happen.**

---

## 19. Persistence Independence

The Minimum Viable Service Model does not prescribe a particular persistence technology.

The authoritative model could be maintained in a platform capable of representing the required semantics.

Examples may include:

- an enterprise service-model repository,
- a CMDB with sufficient relationship semantics,
- a service catalog/model platform,
- Backstage or a similar extensible platform,
- another authoritative model repository.

Likewise, the Automation Registry is a logical architectural capability.

The MVM does not require a specific product or persistence implementation for that registry.

The requirement is semantic:

```text
automation_id
```

must uniquely and immutably identify an automation capability and must resolve to an identifiable version-controlled implementation.

Products are implementations of architectural capabilities.

They are not architectural prerequisites.

---

## 20. POC-03 Conformance Test

POC-03 should demonstrate the separation established by this model.

At minimum:

1. Construct an SM-DAG.
2. Construct a separate Lifecycle Card Registry.
3. Bind every SM-DAG node to exactly one LC using `lc_id`.
4. Populate `automation_name` and UUID `automation_id` for every Atomic Node.
5. Provide resolvable Automation Registry entries for those UUIDs.
6. Leave both automation fields null for Service Nodes.
7. Have the SMV consume the SM-DAG, Lifecycle Cards, and Automation Registry.
8. Validate structural and semantic invariants.
9. Derive an Execution DAG containing appropriate Service and Atomic Nodes.
10. Demonstrate that the Execution DAG was not predefined in resolver logic.

The primary mutation test should modify only an LC service dependency.

The following remain unchanged:

```text
SM-DAG
SMV
automation bindings
```

The derived Execution DAG must change correctly.

A secondary mutation should modify the SM-DAG and add the corresponding Lifecycle Card while leaving the SMV unchanged.

The derived graph must incorporate the new structure.

An automation-binding mutation should modify the implementation resolved by an existing `automation_id` while leaving the SM-DAG and Lifecycle Card unchanged.

The automation identity must remain stable while the resolved implementation changes.

Negative tests should include:

- missing LC,
- mismatched LC/node binding,
- missing service dependency target,
- duplicate identifiers,
- invalid UUID,
- missing automation name,
- unresolved automation UUID,
- service node bound directly to automation,
- atomic node with service dependencies,
- service dependency cycle.

---

## 21. Deliberate Cycle Test

A useful negative test is to deliberately introduce a logically plausible but cyclic set of service dependencies.

For example:

```text
Boot VM [General Purpose Compute]

Validate VM [Boot VM]

Register with Domain [Validate VM]
```

while General Purpose Compute itself requires Identity and Identity requires Register with Domain.

This creates a cycle through the model.

The SMV MUST detect and reject the cycle.

It MUST NOT choose an arbitrary ordering merely to make the model executable.

This is an important architectural property:

> **The model is allowed to be wrong. The validator is not allowed to pretend that it is right.**

---

## 22. Minimum Viable Model Principle

The Minimum Viable Service Model intentionally contains only enough information to describe:

```text
WHAT THE SERVICE IS
        ↓
WHAT THE SERVICE REQUIRES
        ↓
WHERE SERVICE RESOLUTION TERMINATES
        ↓
WHICH AUTOMATION CAPABILITY IS REQUIRED
        ↓
WHAT MUST HAPPEN
        ↓
HOW THE WORK IS EXECUTED
```

The Service Model should not become an orchestration workflow.

The Lifecycle Card should not become an automation artifact.

The Atomic Node should not contain executable code.

The automation name should not masquerade as machine identity.

The automation UUID should not encode architectural location or implementation details.

The Automation Registry should resolve identity to implementation without changing service-model truth.

The Execution DAG should not become persistent architectural truth.

Each construct has one job.

That separation is the foundation of the IPERA Minimum Viable Service Model.