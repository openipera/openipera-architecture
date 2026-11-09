---
layout: documentation
title: "IPERA Minimum Viable Service Model"
documentation_order: 3
---

# IPERA Minimum Viable Service Model

## 1. Purpose

This document defines the Minimum Viable Service Model (MVM) required to represent a service in IPERA.

The objective is not to define a complete enterprise service ontology. The objective is to establish the minimum architectural constructs necessary to:

1. Describe how a service decomposes.
2. Describe what other services are required to realize it.
3. Identify where service-model resolution terminates and automation begins.
4. Validate the model independently of any orchestration platform.
5. Compile the validated Service Model and its associated Lifecycle Cards into a Service Object Graph (SOG) representing the obligations necessary to fully operationalize the requested service.

The central principle is:

> **Model what is true about the service. Derive what must happen from that truth.**

The Service Model describes the structure and relationships of services. Lifecycle Cards define their operational obligations.

The compiled Service Object Graph represents the obligations necessary to fully operationalize a requested service. It is not an executable workflow.

---

## 2. Two Authored Relationships

The Minimum Viable Service Model distinguishes two independently authored relationships.

| Source | Relationship | Meaning |
|---|---|---|
| Service Model DAG edge | **decomposes into** | Defines the structural decomposition of a service. |
| Lifecycle Card service dependency | **depends upon service** | Declares another service required to fulfill the node's obligations. |

The SMV validates the consistency of these independently authored assertions. The compiler consumes the validated model and produces the Service Object Graph (SOG) for a particular realization.

The SOG is a derived, ephemeral compilation artifact, not a third authored relationship or an authoritative source of service knowledge. A compiled SOG and its provenance may be retained for audit without changing that distinction.

Neither authored relationship prescribes execution sequencing.

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

A simplified example of independently modeled service hierarchies:

```text
                         ENTERPRISE SERVICE MODEL

  Compute              Storage              Network              Identity
     |                    |                    |                     |
     VM              Provision Disk        Allocate IP        Register with
     |                    (AN)                (AN)               Domain
     |                                         |                     |
     +-- CPU                               Register DNS          Join Domain
     |                                         (AN)                  (AN)
     +-- Memory


  Security                         CMDB
     |                              |
  Register with                Register CI
    CyberArk                     in CMDB
     |                              |
  Onboard Account                Create CI
      (AN)                         (AN)
```

The columns depict independent service hierarchies, retaining the original example's decomposition relationships. The layout is illustrative; node classifications not explicitly shown are not established by this diagram. Dependencies between these services are declared in their Lifecycle Cards, not by their placement in the diagram. Boot VM and Validate VM are omitted pending separate examination of their appropriate modeling.

**OpenIPERA models service boundaries, not organizational boundaries.** These service hierarchies may resemble existing infrastructure ownership stacks, but their structure does not prescribe which teams, providers, or platforms fulfill them. Organizational responsibility remains relevant to governance and accountability without defining service decomposition.

---

## 4. Node Types

Every node in the SM-DAG has an explicit `node_type`.

The Minimum Viable Service Model defines two node types:

```text
service
atomic
```

A **Service Node** may decompose into additional service-model constructs.

An **Atomic Node** is a terminal service-model construct with no further service decomposition. Its companion Lifecycle Card declares the binding to an external atomic automation capability.

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

Node identity is established by identifiers, not by human-readable names. Identifier collisions and invalid references are model-integrity failures; duplicate or inconsistent names do not, by themselves, invalidate a model. The SMV MAY report naming ambiguities or inconsistencies as nonfatal diagnostic warnings, taking naming scope into account. A valid model may therefore pass validation with warnings.

The examples above use descriptive `node_id` values. This section does not impose UUID formatting on `node_id`; UUID-based automation binding integrity is specified separately.

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
Service owner / Domain SME
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
Validated Lifecycle Card
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

Service owners and Domain SMEs are authoritative for the service knowledge, decompositions, and realization assertions they author. Catalog publication authority is distinct from authorship: Platform Engineering (PE) governs the Application Service Catalog, while Infrastructure Platform Engineering (IPE) governs the Infrastructure Service Catalog. Each catalog authority controls acceptance, publication, and authoritative catalog state within its scope; it does not thereby become the author of the underlying domain assertions. These assertions remain independent even though the companion LC object is instantiated as a consequence of node creation.

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

`service_dependencies` may be populated on LCs for either Service Nodes or Atomic Nodes and may reference any valid service-model node, including Atomic Nodes. It records the responsible service owner or SME's independent assertion of what modeled services are required for realization. A service dependency does not constitute SM-DAG decomposition: an Atomic Node remains terminal in the decomposition hierarchy even when its LC declares dependencies on other modeled services. The SMV validates these relationships independently.

Service decompositions are authored by their responsible service owners or Domain SMEs, subject to the acceptance and authoritative-state governance of the applicable catalog. Companion LC objects are instantiated atomically with their SM-DAG nodes; realization assertions within those LCs are independently authored by the responsible SMEs. A dependency that matches direct or transitive decomposition may be intentional corroboration, not redundant data.

`automation_name` provides the human-readable name of automation associated with an Atomic Node.

`automation_id` provides the immutable machine identity of that automation. The SMV validates the binding's structural and referential integrity, including resolution of the UUID in the automation registry. This validation does not establish that the external automation is operational, executable, or able to satisfy the service obligations. If a valid UUID resolves but `automation_name` differs from the registry's descriptive name, the SMV reports a nonfatal diagnostic warning rather than failing validation.

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

For a non-atomic Service Node, automation binding is absent. For an Atomic Node, further SM-DAG decomposition terminates and the automation binding is required. Either node type may declare service dependencies in its LC; dependency resolution and automation binding are not mutually exclusive. An LC may also declare lifecycle obligations independently of decomposition and dependencies.

LC completeness is a derived, version-specific result of successful SMV validation of all mandatory fields, assertions, and references applicable to its node type; it is not an authored completion status. A validated LC is not thereby operationally ready or proof of service realization.

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

### Valid Atomic Node Lifecycle Card with a Service Dependency

The following is a **valid** Atomic Node Lifecycle Card. Although an Atomic Node is terminal in the SM-DAG decomposition hierarchy, its Lifecycle Card may declare dependencies on other modeled services, including other Atomic Nodes. These dependencies do not constitute further decomposition and are not required for every Atomic Node.

```json
{
  "lc_id": "lc-an-create-vm",
  "node_id": "an-create-vm",
  "service_dependencies": [
    "an-allocate-ip-address"
  ],
  "automation_name": "create-vm",
  "automation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

The dependency target and automation UUID shown here are illustrative; in an actual model they must resolve to a valid service-model node and registered automation capability, respectively.

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

The service dependency does not prescribe an execution sequence. The Service Model Validator validates the dependency, and the Compiler incorporates it into the derived Service Object Graph (SOG). The Orchestrator subsequently determines how the service requirements are realized through executable workflows.

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

For example, Compute and Network are independent service hierarchies:

```text
Compute                    Network
   |                          |
Virtual Machine (SN)     Allocate IP (AN)
   |
Create VM (AN)
```

The Create VM Lifecycle Card may declare:

```text
Create VM [Allocate IP]
```

Create VM remains under Compute, and Allocate IP remains under Network. The dependency is declared in the Create VM Lifecycle Card, not as a decomposition edge. The Compiler resolves this cross-branch dependency into the derived Service Object Graph (SOG).

The SM-DAG describes decomposition.

Lifecycle Cards describe service dependencies.

This separation allows architectural decomposition and realization dependencies to evolve independently.

---

## 9. Atomic Nodes and Automation

An Atomic Node is the lowest-level service-model construct in IPERA.

An Atomic Node is a terminal service-model construct representing a discrete atomic capability. Its companion Lifecycle Card binds that capability to an external, version-controlled automation implementation.

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

The `automation_id` MUST resolve to an existing Automation Registry entry. The registry entry MUST reference an artifact that exists and can be resolved by the Service Model Validator.

The SMV validates reference integrity and artifact existence. It does not interpret, validate, or execute the artifact's contents. Artifact suitability and operational correctness are responsibilities of subsequent realization and execution capabilities.

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
Storage (SN)
   |
   +-- Provision Disk (AN)
```

with:

```text
automation_name: provision-disk
automation_id:   a8f21764-9e31-4e8c-91a5-3c572cb614ef
```

A human-facing canonical representation such as:

```text
storage.provision-disk.provision-disk-a8f21764-9e31-4e8c-91a5-3c572cb614ef
```

can be derived when useful.

It need not be stored.

This avoids duplicating architectural context and prevents an automation identity from changing merely because an Atomic Node is moved within the Service Model.

### Resolution Is Not Execution

Successful resolution of an `automation_id` and verification that its referenced artifact exists establish binding integrity at validation time. The artifact may be an ordinary text file; its contents are not evaluated by the SMV.

It does not establish that the automation will execute successfully.

The Service Model Validator can establish:

```text
Atomic Node exists
        ↓
automation_name exists
        ↓
automation_id is a valid UUID
        ↓
automation_id resolves to an existing registry entry
        ↓
referenced artifact exists and can be resolved
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

An empty `service_dependencies` collection is valid for an Atomic Node but is not required; atomicity is determined by the absence of further SM-DAG decomposition, not by the absence of service dependencies.

However, structural consistency does not yet establish realizability.

The `automation_id` MUST resolve through the authoritative Automation Registry to its referenced automation artifact. The SMV MUST reject unresolved bindings and distinguish resolution failures by their cause. It does not inspect or evaluate the artifact's contents.

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

This includes duplicate SM-DAG node identities and Lifecycle Card identities. Each automation UUID uniquely identifies a registry entry, but multiple Atomic Node Lifecycle Cards MAY reference the same automation UUID to reuse an automation implementation. Such shared references are not duplicate identities.

### Service Dependency Cycle

A service dependency graph containing a cycle MUST be rejected.

The model is allowed to be wrong.

The validator is not allowed to pretend that it is right.

### Circular Service-Realization Dependency

The SMV MUST detect and reject circular service-realization dependencies, including cycles arising from the combination of SM-DAG decomposition relationships and Lifecycle Card service dependencies.

The SMV MUST identify the participating nodes and relationships in its validation report so the model author can locate and correct the circular reference. For example, a report may show `A → B → C → A` and identify each relationship as decomposition or service dependency.

Cycle detection establishes logical consistency. It does not prescribe execution order or construct an executable workflow.

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

### Unresolved Automation Artifact

```text
Automation Registry:
UUID found
Referenced artifact: NOT RESOLVABLE

DENIED:
Automation binding does not resolve to its referenced artifact.
```

The SMV verifies resolvability, not the artifact's contents or operational correctness.

### Service Node Bound Directly to Automation

```text
node_type: service
automation_name: provision-disk
automation_id: a8f21764-9e31-4e8c-91a5-3c572cb614ef

DENIED:
Service Node may not bind directly to automation.
Declare an Atomic Node.
```

### Atomic Node With Further Decomposition

```text
node_type: atomic
SM-DAG children:
  - another-node

DENIED:
Atomic Node cannot have decomposition children.
```

Atomic Nodes may declare service dependencies through their companion Lifecycle Cards; atomicity prohibits further SM-DAG decomposition, not service dependencies.

For an Atomic Node to be realizable, its companion Lifecycle Card MUST contain both an `automation_name` and a valid UUID `automation_id`, and that `automation_id` MUST resolve through the authoritative Automation Registry or equivalent binding mechanism.

---

## 12. Worked Example: General Purpose Compute

**General Purpose Compute (GPC)** is a reusable, cataloged Service Node with its own Lifecycle Card. It can be requested directly by an authorized consumer, such as IT Operations, or referenced as a service dependency by a higher-level service, such as an application deployment.

Both paths use the same authoritative GPC service definition. A request supplies the parameters needed for a particular realization; it does not create a new GPC service definition.

Conceptually:

```text
Higher-Level Service Request       Direct IT Ops Request
       (e.g., Epic)                       |
            |                             |
            v                             |
     General Purpose Compute <------------+
            |
            v
      GPC Lifecycle Card
            |
            +-- Compute services
            +-- Storage services
            +-- Network services
            +-- Other required services
```

GPC is **not** the decomposition parent of Compute, Storage, Network, Identity, Security, or CMDB. Those capabilities remain in their own service hierarchies. GPC's Lifecycle Card declares the services required to realize GPC.

For example, the SM-DAG may contain independent service hierarchies:

```text
General Purpose Compute (SN)

Compute (SN)                 Storage (SN)
   └── VM (SN)                  └── Provision Disk (AN)
        ├── CPU (AN)
        └── Memory (AN)

Network (SN)                 Identity (SN)
   ├── Allocate IP (AN)         └── Register with Domain (SN)
   └── Register DNS (AN)             └── Join Domain (AN)

Security (SN)                CMDB (SN)
   └── Register with CyberArk (SN)  └── Register CI in CMDB (SN)
        └── Onboard Account (AN)         └── Create CI (AN)
```

Representative Lifecycle Card service dependencies may include:

```text
General Purpose Compute [VM, Provision Disk, Allocate IP,
                         Register with Domain, Register with CyberArk,
                         Register CI in CMDB]

Create VM [Allocate IP]
```

These are illustrative assertions, not a mandatory dependency list for every GPC contract. Dependencies are declared in Lifecycle Cards; they do not turn independently governed service hierarchies into decomposition children of GPC.

The Service Model Validator checks the authored decomposition and dependencies for validity, including circular realization requirements and resolvable atomic automation bindings. The Compiler resolves the validated service model into a Service Object Graph (SOG). The Orchestrator consumes the SOG to construct executable workflows.

The authored assertions describe service knowledge and realization obligations, **not a prescribed workflow**.

---
## 13. Concrete SM-DAG Representation

The Storage service hierarchy introduced in Section 12 can be represented as:

```json
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
```

The SM-DAG says:

```text
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
      "vm",
      "an-provision-disk",
      "an-allocate-ip",
      "register-with-domain",
      "register-with-cyberark",
      "register-ci-in-cmdb"
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

The Lifecycle Cards describe realization semantics. The GPC dependencies above are illustrative service identifiers; each must correspond to an existing node in a complete, validated service model.

An empty `service_dependencies` collection means the Lifecycle Card declares no additional service dependencies; it does not negate decomposition relationships in the SM-DAG.

The SM-DAG and Lifecycle Cards together provide the authored service knowledge validated by the Service Model Validator. The Compiler uses the validated model to derive the Service Object Graph (SOG), which represents the service-realization obligations.

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

An action-oriented capability is a Service Node when it has further SM-DAG decomposition, or an Atomic Node when it is terminal and has an automation binding.

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

Power On VM is terminal in the SM-DAG decomposition. Its companion Lifecycle Card identifies the automation binding and may also declare service dependencies:

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

## 16. Independent Validation of Service Knowledge

The SM-DAG and Lifecycle Cards provide complementary assertions, not competing representations of the same relationships. Domain and service authors or SMEs contribute service-model decomposition, Lifecycle Card requirements, and automation knowledge under the governance of the appropriate service catalog authority (PE or IPE, as applicable).

**A Lifecycle Card's association with its Service Node is established by identity. Its service dependencies need not repeat the node's SM-DAG decomposition. The SMV validates both relationships independently and evaluates their combined consistency.**

The SMV validates at least these distinct aspects:

| Validation area | SMV responsibility |
|---|---|
| Node/LC association | Every service-model node has exactly one corresponding Lifecycle Card, with matching identities. |
| Decomposition integrity | SM-DAG decomposition relationships are structurally valid; Atomic Nodes have no decomposition children. |
| Dependency integrity | LC service dependencies reference valid services and do not create circular service-realization requirements, including when combined with decomposition relationships. |
| Binding integrity | Atomic Node automation references resolve through the authoritative Automation Registry to their referenced artifacts. |

A decomposition child need not be repeated in the parent node's LC `service_dependencies` collection. Conversely, an LC dependency on a service in another hierarchy does not imply that the service is a decomposition child.

These checks preserve independent validation without treating the absence of duplicated assertions as a discrepancy.

---
## 17. Service Model Validator

The Service Model Validator (SMV) is an independently callable, reusable OpenIPERA capability that evaluates an authoritative Service Model for structural and semantic consistency before compilation.

The SMV consumes the independently authored SM-DAG and companion Lifecycle Cards. It validates node identities and types, node/LC associations, decomposition relationships, service dependencies, automation bindings, and the resolvability of referenced automation artifacts.

The SMV MUST detect circular service-realization requirements, including cycles arising from the combination of SM-DAG decomposition and LC service dependencies.

The SMV produces structured validation results identifying inconsistencies, affected nodes, relationships, and failure causes. Those results may be rendered for human review.

The SMV does not own or silently repair the authoritative model. Service authors and domain SMEs are responsible for authored service knowledge under the applicable catalog governance authority.

**The SMV validates; the Compiler derives the SOG; the Orchestrator constructs executable workflows.**

The SMV remains independent of the eventual orchestration platform and can serve as a vendor-neutral model-conformance capability.

---
## 18. Service Object Graph (SOG)

The Service Object Graph (SOG) is a derived, request-specific representation of the obligations necessary to realize and operationalize a service.

It is compiled from the validated Service Model, including SM-DAG decomposition, Lifecycle Card service dependencies, and applicable lifecycle obligations.

The SOG is not an authored service model, a persistent source of architectural truth, or an executable workflow.

It answers:

> **What must be satisfied to fully realize and operationalize this service request?**

The Compiler produces the SOG. The Orchestrator consumes it and constructs executable workflows using the available execution capabilities.

The SOG may represent service dependencies, atomic automation bindings, governance requirements, approvals, verification, and evidence obligations. Not every obligation must correspond to an independently executable automation step.

The SOG's realization dependency relationships MUST be acyclic. The SMV detects circular requirements in the authored model before compilation; the Compiler does not silently correct them.

The SMV verifies that atomic automation bindings are resolvable at validation time. The Orchestrator and execution layer resolve or retrieve the referenced implementations as needed for runtime execution. Successful validation does not guarantee runtime availability or operational correctness.

The SOG may be retained as a derived artifact for provenance, audit, and replay without becoming an authoritative source of service-model truth.

**Architectural separation does not require product separation.** The SMV, Compiler, Orchestrator, and execution capabilities are distinct functional responsibilities, but an implementation may combine them within one platform while preserving their boundaries and authoritative sources.

---
## 19. Authoring Rule

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
VALIDATE SERVICE MODEL (SMV)
    ↓
COMPILE SERVICE OBJECT GRAPH (SOG)
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

The model author should also ask:

```text
What governance, verification, evidence, and other lifecycle obligations apply to this service?
```

The model author should not ask:

```text
What step should execute next?
```

That is a derived concern.

The distinction can be summarized as:

> **The SM-DAG describes service decomposition. Lifecycle Cards declare service dependencies and realization obligations. The SOG represents the complete set of obligations derived from that service knowledge for a particular request.**

---

## 20. Persistence Independence

The Minimum Viable Service Model does not prescribe a particular persistence technology.

The authoritative model could be maintained in a platform capable of representing the required semantics.

The SM-DAG and Lifecycle Cards may be maintained in separate authoritative systems, provided their identities, relationships, and required semantics remain resolvable to the SMV and Compiler.

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

MUST uniquely and immutably identify an Automation Registry entry. That entry MUST resolve to its referenced automation artifact. The SMV validates resolvability without interpreting or evaluating the artifact's contents.

Each service-model construct MUST have an identifiable authoritative source. Persistence independence does not eliminate source authority or version provenance.

OpenIPERA-conformant implementations MUST also preserve the mandatory hierarchical component identity, revision, and SMV validation-state semantics defined in [Document 06](06_IPERA_DETERMINISTIC_SERVICE_REALIZATION.md). These requirements apply independently of the chosen persistence technology.

Products are implementations of architectural capabilities.

They are not architectural prerequisites.

---

## 21. Deliberate Cycle Test

A useful negative test deliberately introduces a logically plausible cycle that spans SM-DAG decomposition and Lifecycle Card service dependencies.

For example:

```text
SM-DAG decomposition:

General Purpose Compute
    └── Boot VM
          └── Validate VM
```

```text
Lifecycle Card service dependencies (A → B means A requires B):

Validate VM             → Identity
Identity                → General Purpose Compute
```

Decomposition requires Validate VM to complete before General Purpose Compute can complete. The Lifecycle Cards also require Identity before Validate VM, and General Purpose Compute before Identity. Together, these relationships impose a circular realization requirement:

```text
General Purpose Compute
    requires completion of Validate VM       [decomposition]
Validate VM
    requires Identity                        [LC dependency]
Identity
    requires General Purpose Compute         [LC dependency]
```

The SMV MUST detect and reject circular realization requirements arising from decomposition, LC-declared service dependencies, or their combination.

Validation findings MUST identify the participating nodes, the cycle path, and the relationship types involved.

The SMV MUST NOT silently remove dependencies, select an arbitrary ordering, or otherwise repair the model to make it executable.

This is an important architectural property:

> **The model is allowed to be wrong. The validator is not allowed to pretend that it is right.**

---

## 22. Minimum Viable Model Principle

The Minimum Viable Service Model preserves the knowledge required to describe a service, its decomposition, dependencies, lifecycle obligations, and atomic automation bindings. It does not prescribe an execution workflow.

The distinction between authored service knowledge and derived realization can be summarized as:

```text
SERVICE KNOWLEDGE

WHAT THE SERVICE IS
        ↓
HOW THE SERVICE DECOMPOSES
        ↓
WHAT THE SERVICE DEPENDS UPON
        ↓
WHAT OBLIGATIONS MUST BE SATISFIED
        ↓
WHERE ATOMIC AUTOMATION BINDINGS EXIST


DERIVED REALIZATION

VALIDATE SERVICE KNOWLEDGE
        ↓
COMPILE SERVICE OBJECT GRAPH
        ↓
ORCHESTRATE SATISFACTION OF OBLIGATIONS
        ↓
EXECUTE REQUIRED AUTOMATION
        ↓
COLLECT STATE AND EVIDENCE
```

These arrows express conceptual progression, not a mandatory sequential execution workflow.

The Service Model should not become an orchestration workflow.

The Lifecycle Card should not become an automation artifact.

The Atomic Node should not contain executable code.

The automation name should not masquerade as machine identity.

The automation UUID should not encode architectural location or implementation details.

The Automation Registry should resolve identity to implementation without changing service-model truth.

The SOG may be retained as a point-in-time realization artifact, but it must not replace the authoritative Service Model.

The SMV must not assume the Compiler's responsibility.

The Compiler must not assume the Orchestrator's responsibility.

These are functional boundaries, not mandatory product boundaries: one implementation may provide multiple architectural capabilities while preserving their distinct responsibilities.

**The Service Model preserves knowledge of the system. The SOG represents the obligations required to realize that knowledge for a particular request. Orchestration and automation satisfy those obligations.**

**OpenIPERA models the system. Orchestration and automation operate the system.**
