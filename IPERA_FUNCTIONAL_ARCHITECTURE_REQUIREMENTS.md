# IPERA Functional Architecture Requirements
**Draft v0.2 — Discussion Draft**

## 1. Purpose

IPERA defines an architectural model for realizing and operating enterprise services through declarative service models, dependency-aware orchestration, and reusable automation.

IPERA specifies **functional capabilities and contracts rather than mandatory products**. An implementation may use any technology that satisfies the functional requirements and architectural boundaries defined here.

Opinionated solutions identify technologies believed capable of satisfying a particular IPERA role. They are implementation options, not architectural dependencies.

IPERA intentionally applies established architectural patterns—including declarative intent, abstraction through contracts, dependency graphs, reconciliation, desired versus observed state, and separation of intent from implementation—at the enterprise-service level.

Kubernetes and Kubernetes Resource Orchestrator (KRO) provide useful contemporary examples of these patterns at the resource-composition level. IPERA applies analogous patterns at a broader service abstraction.

---

## 2. Core Architectural Principles

### 2.1 Service Dependency DAG

The decomposed enterprise service model forms a persistent **Service Dependency DAG**.

The DAG exists independently of any individual service request or execution pipeline.

The DAG represents:

- service decomposition;
- dependencies between services;
- Lifecycle Cards associated with services;
- Atomic Nodes associated with lifecycle actions;
- callable service contracts where applicable;
- bindings between Atomic Nodes and automation artifacts.

The Service Dependency DAG is **not an execution workflow**.

---

### 2.2 Dynamic Execution

When a service is requested, the orchestrator:

```text
Service Request
      │
      ▼
Service Dependency DAG
      │
      │ navigate
      ▼
Relevant Services / LCs / ANs
      │
      │ resolve
      ▼
Automation Bindings
      │
      ▼
Dynamic Execution Pipeline
      │
      ▼
Execution
```

The orchestrator **navigates an existing DAG**. It does not construct the Service Dependency DAG.

The resulting execution pipeline is an ephemeral realization of a particular request and must not become the authoritative representation of the service.

---

### 2.3 Service Contracts

Not every node in the Service Dependency DAG must be independently callable.

A non-Atomic service node that is intended to be independently consumed MUST define a machine-consumable **Service Contract**.

The contract defines, at minimum:

- input specification/schema;
- required and optional parameters;
- parameter constraints/defaults where appropriate;
- outputs/status;
- contract version;
- invocation/interface binding.

Different abstraction levels may therefore expose different contracts.

For example:

```text
General Purpose Compute
    │
    │ Consumer-facing contract
    │ "Give me compute suitable for this workload"
    ▼
Compute Service
    │
    │ Infrastructure-facing contract
    │ "Give me a VM with these specifications"
    ▼
Lifecycle Cards
    │
    ▼
Atomic Nodes
```

A caller entering the graph at `Compute Service` may therefore supply implementation-specific parameters that a consumer entering at `General Purpose Compute` neither knows nor needs to know.

---

### 2.4 Atomic Nodes

An **Atomic Node (AN)** is the lowest-level service construct within IPERA.

> **The Atomic Node is the last service construct before automation begins.**

An AN represents a discrete lifecycle action and binds that action to an external, version-controlled automation artifact.

An Atomic Node:

- describes the modeled action;
- contains the binding/reference necessary to locate its automation implementation;
- does **not** contain executable automation.

Conceptually:

```text
Lifecycle Card
      │
      ▼
Atomic Node
      │
      │ automation binding
      ▼
Versioned Artifact
      │
      ▼
Executable Command / Automation
      │
      ▼
Execution Capability
```

The automation artifact may contain something as simple as a command or as complex as Terraform/OpenTofu, Ansible content, Python, PowerShell, or domain-specific automation.

---

### 2.5 Programmatic Interfaces

Any IPERA component or service capability that must be invoked by another component MUST expose an appropriate machine-consumable interface.

Such interfaces may include:

- REST APIs;
- GraphQL;
- event/message interfaces;
- SDKs;
- CLIs;
- providers/plugins;
- other deterministic programmatic mechanisms.

Participation in the Service Dependency DAG does **not** itself require a service node to expose an API.

Callable service nodes must expose a Service Contract and invocation binding.

Atomic Nodes do not themselves expose service APIs. They bind modeled lifecycle actions to automation artifacts that are executed through an appropriate execution capability.

---

## 3. Functional Components

| Component | Functional Requirements | Explicit Non-Responsibilities | Opinionated Solutions |
|---|---|---|---|
| **Service Catalog** | Expose services available for consumption; present appropriate service contracts; collect required request inputs; associate requests with the corresponding service model entry point; submit requests through a machine-consumable interface | Does not define the Service Dependency DAG; does not contain automation; does not construct execution pipelines | Backstage; ServiceNow Service Catalog |
| **Service Model Repository** | Maintain the authoritative decomposed service model and persistent Service Dependency DAG; represent Service Decks, Lifecycle Cards, Atomic Nodes and dependency relationships; define/discover Service Contracts for independently callable non-AN nodes; maintain interface bindings; maintain AN automation bindings; expose the model programmatically for query and traversal; support identity/versioning of modeled objects | Does not execute automation; does not construct runtime execution pipelines; does not replace execution engines or CI/CD | Backstage*; ServiceNow CSDM/CMDB* |
| **Version Control System (VCS)** | Maintain authoritative versions of executable and declarative artifacts referenced by AN bindings; preserve history and provenance; support branching/review/change control; provide uniquely identifiable artifact versions | Does not determine service composition; does not determine execution order; does not decide when an artifact executes | GitHub; GitLab; Bitbucket; other Git-compatible platforms |
| **CI/CD Platform** | Validate, test, package and promote executable/declarative artifacts; enforce appropriate quality/governance gates; produce known and deployable artifact versions suitable for AN binding | Does not own the Service Dependency DAG; does not determine runtime service composition; build/deployment pipelines must not become the authoritative service model | GitHub Actions; GitLab CI/CD; Jenkins; Tekton; other compliant CI/CD platforms |
| **Orchestrator** | Accept a service request at a valid service-model entry point; interrogate the Service Model Repository; navigate the existing Service Dependency DAG; resolve dependencies, LCs, ANs and bindings; dynamically construct the required execution pipeline; pass required context/parameters between service levels; coordinate dependency-aware execution; consume execution results/status | Does not own or redefine the authoritative Service Dependency DAG; does not embed service composition in predefined end-to-end workflows; does not contain domain automation | Apache Airflow; AAP*; other compliant orchestrators |
| **Execution Capability** | Execute the automation action referenced by an AN binding; resolve/use the specified versioned artifact; accept defined execution inputs/context; invoke target/control-plane interfaces as required; return deterministic status, outputs and evidence | Does not determine which ANs constitute a service; does not determine service dependencies; does not construct the overall service realization pipeline | Ansible/AAP; Terraform/OpenTofu; Python; PowerShell; domain-specific execution tooling |
| **State / Evidence Capability** | Capture execution results and evidence necessary to establish realized state; correlate evidence to service request, modeled service and AN where appropriate; expose state for lifecycle evaluation and subsequent orchestration decisions | Does not define desired service state; does not independently define service composition | Existing enterprise state/data platforms; implementation-dependent |
| **Operational Feedback / Observability** | Provide runtime health, events, state changes and operational evidence; enable detection of drift or conditions requiring lifecycle reevaluation; correlate operational information with modeled services where possible | Does not own the Service Dependency DAG; does not define service composition; does not independently determine the realization pipeline | Existing enterprise observability/event platforms |

`*` **Conditional fit:** The product can potentially fulfill the IPERA role, but compliance depends upon architecture, implementation and configuration.

---

## 4. Separation of Service Model and Automation

```text
                 SERVICE DOMAIN

                Service Deck
                     │
              Lifecycle Card
                     │
                Atomic Node
                     │
             automation binding
                     │
─────────────────────┼────────────────────
                     │
              AUTOMATION DOMAIN
                     │
                     ▼
          Version-Controlled Artifact
                     │
              Execution Contract
                     │
                     ▼
            Execution Capability
                     │
        API / CLI / SDK / Provider
                     │
                     ▼
            Target / Control Plane
```

The AN crosses the boundary **by reference**, not by containing automation.

---

## 5. Service Invocation Model

The same Service Dependency DAG may support multiple entry points.

For example:

```text
                  General Purpose Compute
                    [Callable Contract]
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Compute       Network     Identity
        [Callable]      [Callable]    [Internal]
              │
              ▼
        Lifecycle Cards
              │
              ▼
         Atomic Nodes
              │
              ▼
          Automation
```

A general consumer may request **General Purpose Compute** using a high-level contract.

An infrastructure team may independently request **Compute** using a lower-level contract containing CPU, memory, operating system, network, location and other domain-specific parameters.

Both requests enter the **same service model at different abstraction levels**.

A node need not be callable merely because it participates in the DAG.

---

## 6. Architectural Invariants

1. **The Service Dependency DAG exists independently of a service request.**

2. **The orchestrator navigates the Service Dependency DAG; it does not create it.**

3. **The execution pipeline is dynamically derived from the service model and is not itself the authoritative service definition.**

4. **The Atomic Node is the final service-model construct before automation.**

5. **Atomic Nodes bind to externally versioned automation artifacts; they do not contain executable automation.**

6. **A callable non-AN service node exposes a versioned Service Contract appropriate to its level of abstraction.**

7. **Not every node in the Service Dependency DAG must be callable.**

8. **Any capability that is invoked programmatically must provide an appropriate machine-consumable interface.**

9. **Execution mechanisms execute modeled intent; they do not determine service composition.**

10. **IPERA defines functional contracts, not mandatory products.**

---

## 7. Open Architectural Question: State / Evidence / Observability / Reconciliation

This area remains open for architecture review with Rob. The KRO comparison highlights the need for further consideration of:

```text
SPEC
What was requested?

STATUS
What currently exists?

READINESS
Does observed state satisfy modeled intent?

RECONCILIATION
If not, what should happen?
```

> **Open architectural question: determine whether desired-state evaluation and reconciliation constitute a separate IPERA functional component or responsibilities distributed among the Service Model, Orchestrator, and Operational Feedback capabilities.**

