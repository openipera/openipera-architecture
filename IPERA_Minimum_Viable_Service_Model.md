# IPERA Minimum Viable Service Model

## 1. Purpose

This document defines the minimum logical structures and semantic rules required to represent an IPERA Service Model.

The Minimum Viable Service Model (MVM) consists of two related constructs:

1. **Service Model DAG (SM-DAG)** — defines how a service decomposes into constituent services and Atomic Nodes.
2. **Lifecycle Card (LC) Registry** — defines the service dependencies and automation bindings associated with nodes in the Service Model.

Together, these constructs provide sufficient information for the **Service Model Validator (SMV)** to validate the Service Model and derive an Execution DAG.

The MVM is intentionally implementation-neutral. It defines a logical and semantic contract, not a storage technology.

An implementation may persist the model using JSON, YAML, relational tables, a graph database, a CMDB, a service catalog, or another structured repository provided that the semantics defined here are preserved.

> **Model what is true about the service. Derive what must happen from that truth.**

---

## 2. The Three Relationships

IPERA distinguishes three relationships that must not be conflated.

| Construct | Relationship | Meaning |
|---|---|---|
| SM-DAG edge | **decomposes into** | This service is composed of these subordinate service-model constructs. |
| LC service dependency | **depends upon service** | Realization of this service requires realization of another service. |
| Execution DAG edge | **must be realized before** | The derived execution dependency requires one operation to precede another. |

The first two relationships are authored.

The third is derived.

The Service Model therefore describes architectural truth without prescribing workflow.

---

# 3. Service Model DAG

The **Service Model DAG (SM-DAG)** is the persistent architectural decomposition of a service.

It answers:

> **What is this service made of?**

An SM-DAG edge means only:

> **decomposes into**

An SM-DAG edge MUST NOT represent execution order.

An SM-DAG edge MUST NOT be interpreted as "execute before," "depends upon," or "requires."

Execution semantics are derived separately by the Service Model Validator.

---

## 3.1 Minimum SM-DAG Node

Every SM-DAG node MUST contain:

```json
{
  "node_id": "vm",
  "name": "Virtual Machine",
  "node_type": "service",
  "lc_id": "lc-vm"
}
```

The minimum fields are:

| Field | Purpose |
|---|---|
| `node_id` | Unique identity of the service-model node |
| `name` | Human-readable name |
| `node_type` | `service` or `atomic` |
| `lc_id` | Unique identifier of the companion Lifecycle Card |

`node_type` is intentionally explicit.

Although information in the companion Lifecycle Card independently corroborates whether a node is atomic, retaining `node_type` makes the Service Model immediately understandable to both humans and machines.

It also allows the SMV to validate independently authored assertions about the node.

---

# 4. Node Types

The Minimum Viable Service Model defines two node types.

## 4.1 Service

```text
node_type: service
```

A service node represents a service-model construct that remains within the architectural model.

A service may represent a resource, capability, grouping, or lifecycle action.

Examples include:

- General Purpose Compute
- Virtual Machine
- Storage
- Network
- Boot VM
- Validate VM
- Register with Domain

A service does not directly bind to executable automation.

---

## 4.2 Atomic Node

```text
node_type: atomic
```

An **Atomic Node (AN)** is the lowest-level service-model construct in IPERA.

An Atomic Node represents a discrete lifecycle action and binds that action to an external, version-controlled automation artifact.

The Atomic Node does not contain executable automation.

The Atomic Node is the last service construct before automation begins.

Conceptually:

```text
Service
   ↓
Service
   ↓
Service
   ↓
Atomic Node
   ↓
Automation
```

---

# 5. Lifecycle Cards

Every node in the SM-DAG MUST have exactly one companion **Lifecycle Card**.

The relationship is established through `lc_id`.

For example:

```json
{
  "node_id": "vm",
  "name": "Virtual Machine",
  "node_type": "service",
  "lc_id": "lc-vm"
}
```

binds to:

```json
{
  "lc_id": "lc-vm",
  "node_id": "vm",
  "service_dependencies": [
    "storage",
    "network",
    "cpu",
    "memory"
  ],
  "automation_id": null
}
```

Lifecycle Cards are **not nodes in the SM-DAG**.

They are companion records that describe realization semantics associated with SM-DAG nodes.

---

# 6. Minimum Lifecycle Card

Every Lifecycle Card MUST contain:

```json
{
  "lc_id": "lc-example",
  "node_id": "example",
  "service_dependencies": [],
  "automation_id": null
}
```

The minimum fields are:

| Field | Purpose |
|---|---|
| `lc_id` | Unique LC identifier matching the SM-DAG node |
| `node_id` | Node to which this LC belongs |
| `service_dependencies` | Services required to realize this service |
| `automation_id` | Logical identifier of automation associated with an Atomic Node |

The `automation_id` key is mandatory in every Lifecycle Card.

Its value may be null or populated depending upon node type.

---

# 7. Service Dependencies

Lifecycle Cards declare **service dependencies**.

They do not declare execution dependencies.

For example:

```json
{
  "lc_id": "lc-vm",
  "node_id": "vm",
  "service_dependencies": [
    "storage",
    "network",
    "cpu",
    "memory"
  ],
  "automation_id": null
}
```

means:

> To realize the VM service, the Storage, Network, CPU, and Memory services must be realized.

It does **not** mean:

> Execute Storage, then Network, then CPU, then Memory.

No workflow ordering is being authored.

The Service Model Validator determines the resulting execution relationships.

---

# 8. Cross-Branch Dependencies

Service dependencies are independent of SM-DAG decomposition.

A VM may depend upon Storage even though Storage is not decomposed beneath VM.

For example:

```text
General Purpose Compute
   ├── Compute
   │    └── VM
   ├── Storage
   └── Network
```

The VM Lifecycle Card may still declare:

```json
"service_dependencies": [
  "storage",
  "network"
]
```

This is intentional.

The SM-DAG says:

> Storage and Network are constituent services of General Purpose Compute.

The VM Lifecycle Card says:

> Realization of VM requires those services.

Storage and Network SHOULD NOT be duplicated beneath VM merely to express this dependency.

---

# 9. Atomic Nodes and Automation

An Atomic Node MUST have a populated `automation_id`.

Example SM-DAG node:

```json
{
  "node_id": "an-provision-disk",
  "name": "Provision Disk",
  "node_type": "atomic",
  "lc_id": "lc-an-provision-disk"
}
```

Companion Lifecycle Card:

```json
{
  "lc_id": "lc-an-provision-disk",
  "node_id": "an-provision-disk",
  "service_dependencies": [],
  "automation_id": "auto-provision-disk"
}
```

`automation_id` is a logical identifier.

It SHOULD NOT require the Service Model to know whether the automation is stored in GitHub, GitLab, a filesystem, or another VCS implementation.

A separate automation registry or binding mechanism may resolve:

```text
auto-provision-disk
```

to implementation information such as:

```text
repository
version / commit
artifact path
execution type
entrypoint
hash
```

This preserves separation between service architecture and automation implementation.

---

# 10. Intentional Validation Redundancy

The MVM intentionally contains independently authored information that can be cross-validated.

For example:

```text
SM-DAG:
node_type = atomic

Lifecycle Card:
automation_id = auto-configure-cpu
```

These assertions are consistent.

The explicit `node_type` is therefore not unnecessary duplication.

It expresses architectural intent while the Lifecycle Card provides independent evidence that the node satisfies the requirements of that type.

The Service Model Validator MUST reject inconsistencies between them.

---

# 11. Minimum SMV Invariants

The Service Model Validator MUST validate the Service Model before deriving an executable graph.

At minimum, the following invariants apply.

### Atomic Node without automation

```text
node_type: atomic
automation_id: null
```

Result:

```text
DENIED

Atomic Node has no automation binding.
```

---

### Service node with automation

```text
node_type: service
automation_id: auto-something
```

Result:

```text
DENIED

Service node may not bind directly to automation.
Declare an Atomic Node.
```

---

### Atomic Node with further service dependencies

```text
node_type: atomic
service_dependencies:
  - another-service
```

Result:

```text
DENIED

Atomic Node declares further service dependencies.
Atomic Nodes terminate service-model resolution.
```

---

### Missing Lifecycle Card

```text
SM-DAG node:
lc_id: lc-vm

LC Registry:
lc-vm not found
```

Result:

```text
DENIED

SM-DAG node references a nonexistent Lifecycle Card.
```

---

### Mismatched node binding

```text
SM-DAG:
node_id: vm
lc_id: lc-vm

Lifecycle Card:
lc_id: lc-vm
node_id: storage
```

Result:

```text
DENIED

Lifecycle Card does not correspond to the SM-DAG node
that references it.
```

---

### Missing dependency target

```text
service_dependencies:
  - nonexistent-service
```

Result:

```text
DENIED

Lifecycle Card references a service that does not exist
in the authoritative Service Model.
```

---

### Duplicate identifiers

Duplicate `node_id` or `lc_id` values MUST be rejected.

```text
DENIED

Service Model identifiers must be unique.
```

---

### Dependency cycle

If service dependencies resolve to:

```text
Service-A
   ↓
Service-B
   ↓
Service-C
   ↓
Service-A
```

the SMV MUST reject the model.

```text
DENIED

Service dependency cycle detected.
An Execution DAG cannot be derived from a cyclic dependency model.
```

The SMV MUST report the cycle rather than silently altering the Service Model.

---

# 12. Worked Example: General Purpose Compute

The following model illustrates the Minimum Viable Service Model.

This is an illustrative POC model, not a claim that every enterprise must decompose General Purpose Compute in this manner.

## 12.1 SM-DAG

```text
General Purpose Compute
   ├── Compute
   │    └── VM
   │         ├── CPU
   │         └── Memory
   │
   ├── Storage
   │    └── Provision Disk
   │
   ├── Network
   │    ├── Allocate IP
   │    └── Register DNS
   │
   ├── Identity
   │    └── Register with Domain
   │         └── Join Domain
   │
   ├── Security
   │    └── Register with CyberArk
   │         └── Onboard Account
   │
   ├── CMDB
   │    └── Register CI in CMDB
   │         └── Create CI
   │
   ├── Boot VM
   │    └── Power On VM
   │
   └── Validate VM
        └── Run VM Validation
```

In this example:

- `CPU`, `Memory`, `Provision Disk`, `Allocate IP`, and `Register DNS` may be represented as Atomic Nodes where they correspond directly to automation.
- `Join Domain`, `Onboard Account`, `Create CI`, `Power On VM`, and `Run VM Validation` are terminal Atomic Nodes.
- `Boot VM`, `Validate VM`, `Register with Domain`, `Register with CyberArk`, and `Register CI in CMDB` demonstrate that a service may describe an action without requiring a separate action node type.

The exact decomposition remains an architectural decision made by the responsible SMEs.

---

# 13. Concrete SM-DAG Representation

One JSON representation of part of the preceding SM-DAG could be:

```json
{
  "service_model": {
    "root": "gpc",
    "nodes": [
      {
        "node_id": "gpc",
        "name": "General Purpose Compute",
        "node_type": "service",
        "lc_id": "lc-gpc"
      },
      {
        "node_id": "compute",
        "name": "Compute",
        "node_type": "service",
        "lc_id": "lc-compute"
      },
      {
        "node_id": "vm",
        "name": "Virtual Machine",
        "node_type": "service",
        "lc_id": "lc-vm"
      },
      {
        "node_id": "storage",
        "name": "Storage",
        "node_type": "service",
        "lc_id": "lc-storage"
      },
      {
        "node_id": "network",
        "name": "Network",
        "node_type": "service",
        "lc_id": "lc-network"
      },
      {
        "node_id": "cpu",
        "name": "CPU",
        "node_type": "atomic",
        "lc_id": "lc-cpu"
      },
      {
        "node_id": "memory",
        "name": "Memory",
        "node_type": "atomic",
        "lc_id": "lc-memory"
      }
    ],
    "edges": [
      {
        "from": "gpc",
        "to": "compute"
      },
      {
        "from": "gpc",
        "to": "storage"
      },
      {
        "from": "gpc",
        "to": "network"
      },
      {
        "from": "compute",
        "to": "vm"
      },
      {
        "from": "vm",
        "to": "cpu"
      },
      {
        "from": "vm",
        "to": "memory"
      }
    ]
  }
}
```

Every edge in this structure has exactly one semantic meaning:

```text
decomposes into
```

No execution semantics are encoded in these edges.

---

# 14. Concrete Lifecycle Card Registry

A corresponding LC Registry may contain:

```json
{
  "lifecycle_cards": [
    {
      "lc_id": "lc-gpc",
      "node_id": "gpc",
      "service_dependencies": [
        "compute",
        "storage",
        "network",
        "identity",
        "security",
        "cmdb"
      ],
      "automation_id": null
    },
    {
      "lc_id": "lc-compute",
      "node_id": "compute",
      "service_dependencies": [
        "vm"
      ],
      "automation_id": null
    },
    {
      "lc_id": "lc-vm",
      "node_id": "vm",
      "service_dependencies": [
        "storage",
        "network",
        "cpu",
        "memory"
      ],
      "automation_id": null
    },
    {
      "lc_id": "lc-cpu",
      "node_id": "cpu",
      "service_dependencies": [],
      "automation_id": "auto-configure-cpu"
    },
    {
      "lc_id": "lc-memory",
      "node_id": "memory",
      "service_dependencies": [],
      "automation_id": "auto-configure-memory"
    },
    {
      "lc_id": "lc-storage",
      "node_id": "storage",
      "service_dependencies": [
        "provision-disk"
      ],
      "automation_id": null
    },
    {
      "lc_id": "lc-provision-disk",
      "node_id": "provision-disk",
      "service_dependencies": [],
      "automation_id": "auto-provision-disk"
    },
    {
      "lc_id": "lc-network",
      "node_id": "network",
      "service_dependencies": [
        "allocate-ip",
        "register-dns"
      ],
      "automation_id": null
    },
    {
      "lc_id": "lc-allocate-ip",
      "node_id": "allocate-ip",
      "service_dependencies": [],
      "automation_id": "auto-allocate-ip"
    },
    {
      "lc_id": "lc-register-dns",
      "node_id": "register-dns",
      "service_dependencies": [
        "allocate-ip"
      ],
      "automation_id": "auto-register-dns"
    }
  ]
}
```

This example deliberately exposes an important modeling issue.

`register-dns` is shown as an Atomic Node with both:

```text
automation_id = populated
```

and:

```text
service_dependencies = [allocate-ip]
```

Under the MVM invariants defined above, that model is invalid.

The SMV therefore returns:

```text
DENIED

Atomic Node declares further service dependencies.
```

The SME must resolve the modeling error rather than the SMV silently changing the model.

For example, the SME might determine that `Register DNS` is actually a service containing an Atomic Node that performs the registration. That decision belongs to the Service Model author—not to the validator.

This illustrates an important purpose of the MVM:

> The model is allowed to be wrong. The validator is not allowed to pretend that it is right.

---

# 15. Action-Oriented Services

Services are not limited to persistent infrastructure objects.

A service may represent an action within the lifecycle of another service.

For example:

```text
Boot VM
   └── Power On VM
```

could be represented as:

```json
{
  "node_id": "boot-vm",
  "name": "Boot VM",
  "node_type": "service",
  "lc_id": "lc-boot-vm"
}
```

with a terminal child:

```json
{
  "node_id": "an-power-on-vm",
  "name": "Power On VM",
  "node_type": "atomic",
  "lc_id": "lc-an-power-on-vm"
}
```

The Atomic Node LC might contain:

```json
{
  "lc_id": "lc-an-power-on-vm",
  "node_id": "an-power-on-vm",
  "service_dependencies": [],
  "automation_id": "auto-power-on-vm"
}
```

No special `action` node type is required by the Minimum Viable Service Model.

---

# 16. Service Model Validator

The **Service Model Validator (SMV)** is a reusable IPERA capability that independently evaluates an authoritative Service Model, derives the resulting Execution DAG, identifies structural inconsistencies, and renders the graph for SME review and validation before runtime orchestration.

The SMV:

1. Reads the SM-DAG.
2. Reads the Lifecycle Card Registry.
3. Validates node-to-LC relationships.
4. Validates architectural invariants.
5. Resolves service dependencies recursively.
6. Detects invalid references and cycles.
7. Determines service versus Atomic Node semantics.
8. Derives the Execution DAG.
9. Renders the result for human inspection.

The SMV consumes the model.

It does not own the model.

It does not silently repair semantic errors.

---

# 17. Execution DAG

The Execution DAG is a **derived artifact**.

It MUST NOT be authored as part of the authoritative Service Model.

It answers:

> **What must happen, and in what dependency order, to realize this request?**

The resulting graph may contain both service nodes and Atomic Nodes.

The SMV derives those relationships from:

```text
SM-DAG
   +
Lifecycle Cards
   ↓
Service Model Validator
   ↓
Execution DAG
```

Or, more succinctly:

> **Service Model DAG: decomposition of intent.**

> **Execution DAG: realization of intent.**

The Service Model describes what is true.

The Execution DAG describes what must happen.

---

# 18. Authoring Rule

The distinction between service truth and execution prescription is fundamental.

An author SHOULD NOT write:

```text
Execute Validate VM before Register Domain.
```

That statement prescribes workflow.

Instead, the model should declare:

```text
Register Domain
    service_dependencies:
        - Validate VM
```

That statement expresses service truth:

> Registration with the domain requires a validated VM.

The SMV derives the execution consequence.

This is the fundamental IPERA authoring rule:

> **Model what is true about the service. Derive what must happen from that truth.**

---

# 19. Persistence Independence

The MVM defines semantics, not storage.

The same LC could be represented in YAML:

```yaml
lc_id: lc-vm
node_id: vm
service_dependencies:
  - storage
  - network
  - cpu
  - memory
automation_id:
```

or relationally:

```text
LIFECYCLE_CARD
----------------------------------------
lc_id       | node_id | automation_id
lc-vm       | vm      | NULL
```

with dependencies represented separately:

```text
SERVICE_DEPENDENCY
----------------------------------------
lc_id       | depends_on_node_id
lc-vm       | storage
lc-vm       | network
lc-vm       | cpu
lc-vm       | memory
```

A graph database, CMDB, service catalog, or other structured platform may represent the same relationships differently.

Those implementations conform to the MVM if the same semantic assertions can be recovered without embedding execution workflow into the persistent Service Model.

---

# 20. POC-03 Conformance Test

POC-03 should demonstrate that the SM-DAG and Lifecycle Cards remain independent sources of architectural truth while the Execution DAG remains derived.

The primary mutation test is:

```text
1. Create valid SM-DAG.
2. Create valid LC Registry.
3. Derive Execution DAG.
4. Change ONLY a service dependency in an LC.
5. Do not change the SM-DAG.
6. Do not change SMV logic.
7. Derive Execution DAG again.
```

The resulting Execution DAG MUST reflect the changed service dependency.

A secondary mutation test is:

```text
1. Add or modify SM-DAG decomposition.
2. Add the corresponding valid LC.
3. Do not modify SMV logic.
4. Derive Execution DAG.
```

The resulting graph MUST incorporate the changed model.

If application logic must be modified to accommodate either mutation, the model is not authoritative.

---

# 21. Deliberate Cycle Test

The following dependency declarations illustrate a useful negative test:

```text
General Purpose Compute
    depends upon Identity

Identity
    depends upon Register Domain

Register Domain
    depends upon Validate VM

Validate VM
    depends upon Boot VM

Boot VM
    depends upon General Purpose Compute
```

This produces:

```text
GPC
 ↓
Identity
 ↓
Register Domain
 ↓
Validate VM
 ↓
Boot VM
 ↓
GPC
```

The SMV MUST reject this model.

```text
DENIED

Service dependency cycle detected.
```

The validator MUST NOT decide which dependency the architect "probably meant."

The responsible SME must correct the Service Model.

This test is particularly useful because each individual dependency can appear reasonable when viewed locally while producing an impossible realization graph when evaluated globally.

---

# 22. Minimum Viable Model Principle

An IPERA Service Model does not need to encode a workflow.

It needs only enough structured architectural truth for a conforming implementation to derive one.

At minimum:

```text
SM-DAG
    defines decomposition

Lifecycle Cards
    define service dependencies
    and Atomic Node automation bindings

Service Model Validator
    validates both
    and derives execution semantics

Execution DAG
    represents the resulting realization path
```

The architecture therefore maintains a deliberate separation between:

```text
WHAT THE SERVICE IS
        ↓
WHAT THE SERVICE REQUIRES
        ↓
WHAT MUST HAPPEN
        ↓
HOW THE WORK IS EXECUTED
```

That separation is the foundation of the IPERA Minimum Viable Service Model.