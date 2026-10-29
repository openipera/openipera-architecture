# IPERA Functional Architecture Requirements — Draft v0.3 — Discussion Draft

## 1. Purpose

**OpenIPERA is an open implementation of the Infrastructure Platform Engineering Reference Architecture (IPERA)**, an architectural approach to engineering enterprise infrastructure services as explicit, dependency-aware operational systems.

The idea behind IPERA is straightforward: enterprise infrastructure services should be defined by what they require, how they depend on one another, and what obligations must be satisfied to make them operational—not by the workflows someone happened to write to provision them. IPERA is designed to simplify enterprise infrastructure automation by eliminating the need to manually construct and maintain complex, service-specific workflows and pipelines, making complete service realization derivable from authoritative service knowledge.

Consider Kubernetes Resource Orchestrator (KRO). KRO demonstrates how complex resource requirements can be abstracted behind a declarative interface, allowing the underlying system to resolve and manage the necessary resource relationships. IPERA builds on similar architectural principles but applies them at the enterprise infrastructure service level, where realizing a service may involve multiple technology domains, operational control planes, governance requirements, and automation platforms.

IPERA accomplishes this by separating authoritative service knowledge from the mechanisms used to execute it. Service models describe composition, dependencies, and operational obligations. A Service Model Compiler validates and resolves those models into a request-specific **Service Object Graph (SOG)**, representing what must be accomplished to fully operationalize the requested service. Orchestration and automation platforms then determine how to carry out that realization.

This distinction is fundamental. **OpenIPERA is not another workflow engine or automation framework.** Its purpose is to make enterprise service realization a consequence of an authoritative service model rather than a collection of independently maintained workflows.

This document identifies the functional capabilities required to implement IPERA, establishes the responsibilities and boundaries of those capabilities, and maps them to opinionated tooling choices. These choices are examples of technologies that may fulfill the requirements, not mandatory architectural dependencies. Existing enterprise tooling can participate wherever it satisfies the defined capabilities and contracts.

## IPERA Functional Architecture

![IPERA Functional Architecture](../images/ipe-model.png)

The diagram illustrates the functional capabilities and architectural boundaries of IPERA, from the authoritative Service Model DAG (SM-DAG) through compilation, orchestration, and automation execution. Each capability has a distinct responsibility, allowing existing enterprise tooling to participate without assuming ownership of the service model or redefining its semantics. Section 3 identifies these capabilities, their responsibilities, and their architectural boundaries.

---

## Critical Architectural Distinction: Service Model ≠ Execution Model

The **Service Model DAG (SM-DAG)** is authoritative service knowledge, not an orchestration workflow. It describes how services are composed and decomposed into Service Nodes (SNs) and terminal Atomic Nodes (ANs), and which services depend on others. Lifecycle Cards (LCs) and the automation registry supply the associated obligations, governance context, and executable bindings. None of these structures should be confused with a workflow authored for a particular execution engine.

When a service is requested, the **Service Model Compiler**, including its Service Model Validator (SMV), validates the relevant model, resolves its dependency closure, and derives a request-specific **Service Object Graph (SOG)**. The SOG expresses what must be accomplished to operationalize the service: dependencies, obligations, service-completion milestones, ordering constraints, and allowable parallelism. It is a compiled representation of the required realization, **not an executable workflow**.

The **DAG orchestrator** consumes the SOG and translates its semantics into an executable pipeline for its chosen engine. Automation execution capabilities then perform the bound actions against the appropriate control planes and return results and evidence. The orchestrator does not need to interpret the authoritative service model or invent service dependencies; that work belongs to the compiler.

```text
AUTHORITATIVE SERVICE KNOWLEDGE          COMPILED CONTRACT              RUNTIME REALIZATION

Service Model Repository
  ├── Service Model DAG (SM-DAG)
  │     ├── Service Nodes (SNs)
  │     └── Atomic Nodes (ANs)
  ├── Lifecycle Cards (LCs)
  └── Automation Registry
               │
               │ authoritative inputs
               ▼
       Service Model Compiler
         (including SMV)
       Validate • Resolve • Compile
               │
               │ produces
               ▼
       Service Object Graph (SOG) ───────► DAG Orchestrator
       Request-specific obligations       Translate SOG into
       and dependency semantics           engine-native pipeline
                                                 │
                                                 ▼
                                        Automation Execution
                                                 │
                                                 ▼
                                        Control Planes / Services
                                                 │
                                                 ▼
                                        Results / Evidence / Feedback
```

The distinction matters because the service model can evolve independently of any particular orchestration or automation product. A compiled SOG captures the obligations and dependency semantics for a specific request at a particular point in time; the execution pipeline is the engine-specific realization of that compiled contract.

The following requirements apply to every IPERA implementation:

- The Service Model Repository remains authoritative for service composition and dependencies. Neither the compiler nor an orchestration or execution platform may silently redefine them.
- The compiler is responsible for validating the relevant service knowledge and producing the SOG. The orchestrator must not assume those compilation responsibilities.
- The orchestrator consumes the SOG and builds or coordinates an executable pipeline without becoming the authoritative owner of service definitions.
- Workflows in AAP, Airflow, Argo, or another platform must not become the authoritative definition of a service.
- Replacing an orchestration or automation product must not require redefining the SM-DAG or changing the architectural semantics of the SOG.
- The orchestrator's internal pipeline representation and the execution capability's implementation mechanisms remain product-specific choices.

### Architectural Conformance Test

> **If replacing the orchestration platform requires rebuilding the authoritative service model or changing the meaning of the compiled SOG, orchestration-specific concerns have leaked across the architectural boundary. The implementation does not conform to IPERA's separation of responsibilities.**

---

## 2. Service Model Constructs and Properties

The IPERA Service Model describes enterprise infrastructure services through explicit constructs and relationships. The **Service Model DAG (SM-DAG)** consists of Service Nodes (SNs), terminal Atomic Nodes (ANs), and directed structural relationships. Lifecycle Cards (LCs), Service Contracts, and automation registry entries provide associated service knowledge; they are not vertices in the SM-DAG.

**The DAG is fundamental:** an upper-level Service Node depends on subordinate nodes by virtue of the directed graph itself. Structural dependencies are inherent in those edges and are not restated in Lifecycle Cards. Separately, an LC may declare dependencies on other modeled services outside its node's structural decomposition. The Service Model Compiler resolves both forms of dependency when deriving the Service Object Graph (SOG). Neither form of dependency requires a referenced service to be independently callable.

```text
                         Create VM (SN) -------- Lifecycle Card (LC)
                         /            \                  |
                        v              v                 +-- Service Dependencies
              Provision VM (SN)    Configure OS (SN)     |    +-- Allocate IP (SN)
                  /      \                |              |    +-- Configure DNS (SN)
                 v        v               v              |    +-- Storage (SN)
           Create VM   Attach Disk    Configure OS       |    +-- Network (SN)
              (AN)        (AN)           (AN)            |
                                                         +-- Operational Obligations
                                                              +-- Observability
                                                              +-- Health Verification
                                                              +-- Governance / Approvals
```

### 2.1 Service Model Constructs

| Construct | Definition | Architectural characteristics |
|---|---|---|
| **Service Model DAG (SM-DAG)** | Directed acyclic graph of service composition and structural dependencies. | Authoritative service knowledge, not an executable workflow or pipeline. |
| **Service Node (SN)** | A service construct that may decompose into subordinate SNs or ANs. | May be independently callable or participate only as part of another service. |
| **Atomic Node (AN)** | Terminal service construct representing an obligation fulfilled through automation. | Last service construct before automation; has no subordinate nodes or independent service dependencies. |
| **Lifecycle Card (LC)** | Governs the realization, verification, and continuing operational obligations of its associated SN or AN. | Gives service structure operational meaning; defines satisfaction criteria and evidence requirements without itself executing or adjudicating outcomes. Not a graph vertex. |
| **Service Contract** | Machine-consumable definition of how an independently callable SN can be requested. | Defines consumption semantics, distinct from catalog publication and authorization. |
| **Automation Registry Entry** | Maps a governed automation identity to its current implementation. | Implementation remains external to the Service Model and is not embedded in an AN. |

### 2.2 Service Model Properties and Constraints

| Property | Applies to | Requirement |
|---|---|---|
| **Persistent identity** | SN, AN | A stable identity distinguishes the logical construct from its name, placement, or implementation. |
| **Node type** | SN, AN | Distinguishes decomposable SNs from terminal ANs. |
| **Structural dependencies** | SM-DAG, SN | Directed parent-to-subordinate edges inherently express the parent's dependencies. This is why the Service Model is a DAG. |
| **LC-declared service dependencies** | LC | An LC may reference additional required services elsewhere in the model. These references are distinct from structural decomposition and do not make referenced services callable. |
| **Terminality** | AN | An AN has no children or independently declared service dependencies; its associated LC identifies its automation binding. |
| **Lifecycle association** | SN, AN, LC | Every modeled node has exactly one associated LC, and each LC belongs to one node. |
| **Callability** | SN | Explicit property determining whether a service can be requested independently; participation in the graph does not imply callability. |
| **Service Contract** | Callable SN | Required for independent consumption; specifies inputs, outputs/status, parameters and constraints, contract version, and invocation/interface binding. |
| **Governance properties** | LC | May declare approval, authorization, policy, and observability requirements without assigning enforcement to IPERA. |
| **Automation binding** | AN-associated LC | References automation by governed identity; the registry resolves its current implementation. Executable code is not embedded in an AN. |
| **Object evolution** | SN, AN, LC, Service Contract | Definitions can evolve while preserving logical identity. Detailed versioning and compatibility requirements remain to be defined. |
| **Model integrity** | SM-DAG and associated knowledge | Structural graph must be acyclic; references and node/LC associations must resolve; terminal paths must end in ANs with valid automation bindings. |

### 2.3 Service Consumption and Authority

**Not every Service Node is independently callable.** A non-Atomic Service Node intended for independent consumption **MUST** define a machine-consumable Service Contract. Other Service Nodes can participate in decomposition or satisfy LC-declared dependencies without exposing a callable interface. A request for a callable service through IPERA still requires the compiler to derive its complete modeled obligations; callability does not permit substituting a manually assembled workflow for model resolution.

Callability, catalog publication, and authorization are distinct. The Service Model describes whether a service is callable and defines its contract. An enterprise catalog may publish that capability through a governed interface, including a catalog intended only for IT Operations. Enterprise catalog, identity, and governance systems control exposure and determine who may invoke it. Lifecycle Cards may declare authorization requirements, but **IPERA does not adjudicate authorization**.

A capability becomes a Service Catalog offering when it is exposed through a governed catalog interface. Publication does not alter its structural or LC-declared dependencies.

---

## 3. Required Tooling Capabilities

### 3.1 Architectural Boundaries and Capability Separation

OpenIPERA defines tooling capabilities according to distinct architectural responsibilities and authority boundaries, rather than products, deployment components, or implementation technologies. This separation preserves the independence of service modeling, compilation, orchestration, and execution while allowing individual products to fulfill multiple capabilities. **Nine required capabilities do not imply nine separate tools.**

Governance, security, approvals, control planes, and infrastructure domains are cross-cutting architectural obligations and integration boundaries, as shown in the functional architecture diagram, rather than additional tooling capabilities. Kubernetes packaging, northbound APIs, SOM adapters, and deployment topology are implementation concerns and do not independently constitute tooling capabilities.

### 3.2 Compiler / Linker / Loader / Runtime Analogy

Traditional computing architectures separate the transformation of source code into executable instructions into distinct responsibilities. A **compiler** translates source code into an intermediate representation, a **linker** assembles the required components into an executable, a **loader** prepares that executable for execution, and the **runtime** provides the environment in which it operates. Although modern development platforms frequently combine these functions, their separation remains a useful architectural principle.

OpenIPERA applies a similar separation of responsibilities to enterprise infrastructure service realization:

| Traditional Computing | OpenIPERA | Architectural Responsibility |
|---|---|---|
| **Compiler** | Service Model Compiler | Transforms authoritative service knowledge into a Service Object Graph (SOG). |
| **Linker** | DAG Orchestrator | Transforms the compiled SOG into an executable realization pipeline. |
| **Loader** | CI/CD Platform | Qualifies, packages, and deploys automation implementations for execution. |
| **Runtime** | Automation Execution Capability | Executes automation implementations against infrastructure and domain control planes. |

The analogy illustrates **architectural responsibilities, not a mandatory execution sequence or a one-to-one mapping of products**. A single technology may implement multiple responsibilities without eliminating the boundaries between them.

### 3.3 Required Tooling Capabilities and Opinionated Solutions

The following table identifies the tooling capabilities required to implement IPERA. **Functional Responsibilities** define what each capability must accomplish; **Explicit Non-Responsibilities** establish its architectural boundary. A product may provide multiple capabilities, but doing so does not transfer authority between them. APIs, adapters, validation modes, and deployment topology are features or implementation details of these capabilities, not additional tooling categories.

**Required assessment guidance.** This table identifies candidate solutions and records **capability-specific architectural qualification**, not deployment status. Assess each candidate against both its **Functional Responsibilities** and **Explicit Non-Responsibilities**, using demonstrated behavior or independently verifiable evidence. A product's presence, reputation, or advertised features alone do not establish conformance. Status definitions: **Vetting** (blue) — candidate under evaluation; evidence is insufficient to establish fit. **Provisional** (yellow) — credible capability fit, with specific outstanding architectural verification. **Vetted** (green) — evidence establishes fit for the stated capability and boundaries. Qualification is specific to each candidate-capability pairing. Identify capability gaps before assuming new products are needed; configuration, integration, extension, or development may close them. Actual solution selections, implementation progress, and production validation belong in the separately maintained [OpenIPERA Implementation Registry](08_OPENIPERA_IMPLEMENTATION_REGISTRY.md), organized by implementation beginning with the Reference Implementation.

| Tooling Capability | Functional Responsibilities | Explicit Non-Responsibilities | Opinionated Solutions<br><sub>![Vetting](../images/status-vetting-blue.svg) Vetting · ![Provisional](../images/status-provisional.svg) Provisional<br>![Vetted](../images/status-vetted.svg) Vetted</sub> |
|---|---|---|---|
| **Service Catalog** | • Publish governed service offerings.<br>• Expose applicable Service Contracts.<br>• Collect service-request parameters.<br>• Submit requests against a defined service-model entry point. | Does not author the service dependency model, compile SOGs, or construct execution pipelines. | ![Vetting](../images/status-vetting-blue.svg) ServiceNow Service Catalog<br>![Vetting](../images/status-vetting-blue.svg) Backstage |
| **Service Model Repository** | • Maintain authoritative SM-DAGs and node definitions.<br>• Maintain associated Lifecycle Cards.<br>• Maintain declared service dependencies and Service Contracts.<br>• Maintain governed automation binding references.<br>• Preserve stable model identities and revision information. | Does not compile a request-specific SOG, execute automation, or become the orchestration engine. | ![Vetting](../images/status-vetting-blue.svg) ServiceNow (subject to model fit)<br>![Vetting](../images/status-vetting-blue.svg) demonstration etcd-backed repository |
| **Version Control System (VCS)** | • Version automation and declarative implementation artifacts.<br>• Preserve artifact provenance and change history.<br>• Support review and controlled changes to artifacts.<br>• Provide resolvable artifact identities. | Does not define service composition, derive dependency order, or determine when automation executes. | ![Vetted](../images/status-vetted.svg) GitHub<br>![Vetted](../images/status-vetted.svg) GitLab<br>![Vetted](../images/status-vetted.svg) Bitbucket |
| **Service Model Compiler (including SMV)** | • Validate service-model structural and semantic integrity.<br>• Validate Lifecycle Card associations and references.<br>• Resolve applicable service dependency closure.<br>• Resolve applicable Lifecycle Card operational obligations.<br>• Derive the deterministic, request-specific Service Object Graph (SOG).<br>• Identify invalid references and unmet realization requirements distinctly.<br>• Produce diagnostics and preserve compilation provenance. | Does not author the authoritative service model, construct engine-native workflows, execute automation, or reconcile observed infrastructure state. | ![Provisional](../images/status-provisional.svg) OpenIPERA Compiler |
| **CI/CD Platform** | • Validate automation and platform implementation artifacts.<br>• Test implementation artifacts.<br>• Package and publish qualified artifacts.<br>• Promote approved implementations.<br>• Enforce engineering quality gates. | Does not own the service model, compile request-specific SOGs, or serve as the runtime service orchestrator. | ![Vetted](../images/status-vetted.svg) GitHub Actions<br>![Vetted](../images/status-vetted.svg) GitLab CI/CD<br>![Vetted](../images/status-vetted.svg) Jenkins<br>![Vetted](../images/status-vetted.svg) Tekton |
| **DAG Orchestrator** | • Consume the compiled SOG.<br>• Construct an engine-native executable pipeline.<br>• Preserve compiled dependency and obligation semantics.<br>• Coordinate execution progress, failures, and outcomes.<br>• Report realization execution status and results. | Does not independently rediscover or redefine service composition, alter the SOG's dependency semantics, or own domain automation. | ![Provisional](../images/status-provisional.svg) Apache Airflow<br>![Provisional](../images/status-provisional.svg) Argo<br>![Vetting](../images/status-vetting-blue.svg) Spacelift (integration fit to be verified) |
| **Automation Execution Capability** | • Accept resolved automation bindings and execution context.<br>• Invoke automation implementations against target control planes.<br>• Return execution status and outputs.<br>• Produce execution evidence. | Does not determine service composition, compile SOGs, or independently construct the end-to-end realization plan. | ![Vetted](../images/status-vetted.svg) Ansible/AAP<br>![Vetted](../images/status-vetted.svg) Terraform/OpenTofu<br>![Vetting](../images/status-vetting-blue.svg) Spacelift execution facilities<br>![Vetted](../images/status-vetted.svg) Python<br>![Vetted](../images/status-vetted.svg) PowerShell |
| **State / Evidence Capability** | • Record service-realization outcomes.<br>• Preserve execution evidence and realization provenance.<br>• Correlate evidence with requests, services, and atomic actions.<br>• Support verification of completed realization obligations. | Does not define the authoritative service model or independently determine required service dependencies. | ![Vetting](../images/status-vetting-blue.svg) Existing enterprise state and evidence platforms |
| **Operational Feedback / Observability** | • Collect operational telemetry.<br>• Observe service health and availability.<br>• Detect operational events and state changes.<br>• Identify deviations from expected operational conditions.<br>• Supply evidence for ongoing lifecycle assurance. | Does not author the SM-DAG, compile SOGs, or independently define service composition. | ![Vetting](../images/status-vetting-blue.svg) Existing enterprise monitoring, telemetry, and AIOps platforms |

## 4. Service Model Compiler — Functional Requirements

The preceding section identifies nine distinct tooling capabilities required to implement OpenIPERA. Most can be fulfilled by existing technologies, subject to their conformance with defined architectural responsibilities and boundaries. One capability, however, distinguishes OpenIPERA from conventional infrastructure automation architectures: the **Service Model Compiler**.

Three foundational principles establish its purpose and architectural position.

**1. OpenIPERA bridges documented service intent and service realization. Nothing more.**

OpenIPERA provides the architectural mechanism for translating authoritative, documented service intent into the operational obligations necessary to realize that intent. The Service Model Compiler is central to this translation, producing a deterministic, request-specific Service Object Graph (SOG) from the Service Model DAG (SM-DAG) and its associated Lifecycle Cards.

**OpenIPERA does not replace service catalogs, orchestration engines, automation platforms, or infrastructure control planes.** It connects these capabilities through explicit architectural contracts, allowing each to retain its existing responsibilities.

**2. To our knowledge, no equivalent implementation is currently under development.**

Existing technologies provide sophisticated service catalogs, infrastructure automation, workflow orchestration, and operational management. However, we have not identified an independently available implementation—or a publicly documented development effort—that performs the specific translation required by OpenIPERA: compiling authoritative service intent into a deterministic representation of the operational obligations necessary for service realization.

This is a statement of our present knowledge, not a claim that no comparable technology could exist.

**3. The Service Model Compiler is not special infrastructure. It is another interchangeable architectural component.**

Although the compiler is essential to OpenIPERA's architectural proposition, **its implementation has no privileged status**. It is designed to be modular, replaceable, and independently implementable—another building block within Infrastructure Platform Engineering (IPE), IPERA, and OpenIPERA.

Any implementation that satisfies the compiler's published functional contracts and architectural boundaries should be capable of replacing the OpenIPERA Compiler reference implementation without requiring changes to the authoritative service model or downstream realization capabilities.

**OpenIPERA's value lies in the architectural contracts and the separation of responsibilities—not in ownership of a particular compiler implementation.**

### 4.1 Stage 1 — Service Model Validation (SMV)

The **Service Model Validator (SMV) is Stage 1 of the Service Model Compiler**. Validation is intrinsic to compilation, not an optional preliminary step. As with classical FORTRAN, Pascal, C, and C++ compilers, source checking can be invoked independently without producing object code; a subsequent compilation nevertheless performs its own validation before code generation. Similarly, OpenIPERA supports independent SMV invocation without generating a Service Object Graph (SOG), but **every Compile invocation MUST perform Stage 1 validation before Stage 2 SOG generation**, regardless of any previous validation result.

The SMV is a named, independently callable **logical component of the compiler**, not a required separate deployment or peer microservice. It performs one operation: **validate a caller-specified scope of the Service Model DAG (SM-DAG) against published OpenIPERA rules and return a structured Validation Result**. The caller decides when to invoke it. The SMV does not monitor edits, initiate validation, define the rules, or modify the model.

#### 4.1.1 Validation Scopes

| Validation Scope | Scope | Invocation (illustrative) | Responsibility | Output |
|---|---|---|---|---|
| **Object Validation** | **Single Object Only** — one SN, AN, or LC | `SMV.Validate(OBJECT, object_id)` | Check the specified object's internal structure, required attributes, and local semantic consistency. No calling context or external reference resolution is implied. | Validation Result |
| **Service Validation** | Complete service dependency closure rooted at `SERVICE_ID` | `SMV.Validate(SERVICE, service_id)` | Apply object validation throughout the resolved closure **and** verify applicable references, object associations, dependencies, and graph constraints. | Validation Result |
| **SM-DAG Validation** | Entire authoritative SM-DAG | `SMV.Validate(ALL)` | Apply the same published rules to all authoritative objects and relationships, including graph-wide integrity. | Validation Result |

These invocations illustrate a functional contract, not a prescribed API syntax or transport. **Scope determines what is examined; it does not select a different validator or a different rule set.** Rules involving relationships become evaluable as the selected scope expands. For example, a locally consistent SN may pass Object Validation even if a declared external dependency does not exist; this PASS makes no claim about graph integrity.

A service closure is a **graph**, not necessarily a tree: dependencies may be shared. The SMV must detect invalid references and cycles while resolving and validating the requested closure, rather than assuming that the closure is already valid.

#### 4.1.2 Validation Result

Every invocation returns the same structured Validation Result contract, including the requested scope and target (where applicable), authoritative model revision or snapshot identity, evaluated objects and relationships, applicable rules, status, and actionable diagnostics identifying affected objects, references, or relationships.

| Status | Meaning |
|---|---|
| **PASS** | Validation completed for the identified scope and model revision with no applicable rule violations. |
| **FAIL** | Validation completed and identified one or more violations of published OpenIPERA rules. |
| **ERROR** | Validation could not be completed reliably, such as because an authoritative source was unavailable or validation itself failed. Conformance has **not** been established. |

An incomplete evaluation MUST NOT return PASS. A PASS certifies **only the evaluated scope at the identified model revision**; Object Validation does not certify a service closure, and Service Validation does not certify the entire SM-DAG. An ERROR is not evidence that the model itself violates a rule.

#### 4.1.3 Compilation Gate and Boundaries

The compiler exposes two conceptual operations:

- **Validate:** Invoke Stage 1 for a caller-specified scope and return its Validation Result; do not generate a SOG.
- **Compile:** Resolve a consistent authoritative model snapshot for the requested service, invoke Stage 1 **Service Validation** against that snapshot, and proceed to Stage 2 SOG generation **only on PASS**. Stage 2 MUST consume the same model snapshot validated by Stage 1. A FAIL or ERROR prevents SOG generation and returns a structured diagnostic.

**Automation-binding boundary:** The SMV validates the structural and semantic integrity of automation bindings declared by Atomic Nodes, including required Lifecycle Card fields, identifier format, and any required authoritative registry relationship. It does **not** resolve, inspect, or verify the existence, availability, correctness, or executability of the referenced automation code or artifacts. Those checks belong to subsequent realization stages. **Model validity does not establish implementation availability or execution success.**

The SMV enforces published service-model rules but neither authors nor relaxes them. It does not approve changes, orchestrate workflows, execute automation, or silently repair invalid input. The compiler must distinguish **invalid model references** from **validly modeled but unavailable or unimplemented capabilities**, reporting the latter as realization gaps rather than silently treating them as implemented.

### 4.2 Stage 2 — Service Object Graph (SOG) Generation

**Stage 2 transforms the validated, request-specific service dependency closure into a Service Object Graph (SOG).** It consumes the same authoritative SM-DAG snapshot and associated Lifecycle Cards that passed Stage 1; it does not independently redefine service composition or repeat model validation.

The compiler resolves both structural SM-DAG dependencies and additional service dependencies declared by Lifecycle Cards. It derives the **complete set of obligations necessary to operationalize the requested service**, not merely the provisioning sequence. These obligations include realization, governance, operational readiness, monitoring, metrics, verification, and continuing assurance where required by the applicable Service Contracts, Lifecycle Cards, and policies.

The resulting SOG MUST:

- Represent the required service obligations and their dependency ordering, including shared dependencies.
- Preserve the provenance of obligations and their applicable acceptance criteria and evidence requirements.
- Identify governed automation bindings at terminal AN obligations without embedding executable code.
- Distinguish obligations that can be bound for realization from validly modeled capabilities whose implementation is unavailable or unresolved.
- Remain independent of any particular orchestration engine or automation platform.

**The SOG specifies what must be accomplished and demonstrated; it does not itself execute work or certify successful realization.** The DAG Orchestrator consumes the SOG to construct an executable workflow. Execution and assurance capabilities subsequently produce and evaluate evidence against the declared obligations.

Stage 2 returns the SOG together with its source model revision and any structured realization-gap diagnostics. The SOG is a derived artifact, never an alternate authority for service composition.

`*` **Conditional fit:** Named products are examples, not declarations of conformance. Actual suitability depends on supported interfaces, integration semantics, and deployment configuration.

---

## 5. Separation of Service Model and Automation

The Service Model defines service intent, composition, dependencies, and operational obligations. The Automation Domain maintains the implementations that fulfill terminal obligations. **The Atomic Node (AN) and its associated specialized Lifecycle Card (LC) establish the governed interface between these domains.** The AN remains a terminal service-model node; its LC declares an automation binding by reference, without embedding executable code.

```text
                                     SERVICE MODEL DOMAIN

       STRUCTURAL DECOMPOSITION                              ASSOCIATED SERVICE KNOWLEDGE
              (North–South)                                         (East–West)


                         Create VM (SN) ------------------------ Lifecycle Card (LC)
                         /            \                                   |
                        v              v                                  +-- Service Dependencies
              Provision VM (SN)    Configure OS (SN)                      |    +-- Allocate IP (SN)
                  /      \                |                               |    +-- Configure DNS (SN)
                 v        v               v                               |    +-- Storage (SN)
           Create VM   Attach Disk    Configure OS                        |    +-- Network (SN)
              (AN)        (AN)           (AN)                             |
                |                                                         +-- Operational Obligations
                |                                                              +-- Observability
                |                                                              +-- Health Verification
                |                                                              +-- Governance / Approvals
                |
                |  Terminal service obligation
                |
                v
SERVICE MODEL   |
========================== AN Lifecycle Card (LC) =================================================
AUTOMATION      |            Governed Automation Binding
                |                    (UUID)
                |
                v
         Automation Registry
                |
                |  Resolves governed identity
                v
      Version-Controlled Artifact
                |
                v
     Automation Execution Capability
                |
                v
        Target / Control Plane


                                     AUTOMATION DOMAIN
```

**North–south** edges express structural decomposition of Service Nodes into subordinate SNs and terminal ANs. **East–west** associations connect nodes to their Lifecycle Cards and associated service knowledge. Every SN and AN has its own LC; only the representative **Create VM (AN)** is traced through the automation boundary in this diagram.

**The AN Lifecycle Card is a specialized LC.** Unlike an SN's LC, it declares the governed automation binding for a terminal service obligation. Its placement *on* the boundary expresses its interface role, not a transfer of metadata ownership: the AN and its LC remain authoritative Service Model constructs.

The Automation Registry resolves the governed automation identity to an independently maintained implementation. Neither the AN nor its LC contains executable automation. Consistent with Section 4.1, SMV validation establishes the binding's model conformance, **not** the existence, availability, correctness, or executability of the referenced automation implementation.

---

## 6. Service Invocation Model

**Callability defines where a consumer may enter the authoritative Service Model DAG (SM-DAG).** It does not define service decomposition, alter dependencies, or establish an alternate execution path. A Service Node (SN) is independently callable only when it exposes an appropriate machine-consumable Service Contract.

The same SM-DAG can support multiple independent entry points:

```text
                  General Purpose Compute (SN)
                      [Callable Contract]
                               |
                 +-------------+-------------+
                 |             |             |
                 v             v             v
             Compute        Network       Identity
               (SN)           (SN)          (SN)
            [Callable]      [Internal]    [Internal]
                 |
                 v
          Subordinate SNs / ANs
```

A general consumer may request **General Purpose Compute** through its high-level Service Contract. An infrastructure team may independently request **Compute** through a lower-level Service Contract with its own appropriate inputs and constraints. Both requests enter the **same authoritative SM-DAG** at different abstraction levels; each is compiled from the dependencies applicable to its requested service.

**Internal** means that an SN does not expose an independent consumer-facing invocation contract; it does **not** mean the node cannot participate in decomposition or satisfy another service's dependencies. Participation in the graph does not imply independent callability.

Invoking a callable SN submits a request under its Service Contract. It does not directly execute automation, bypass SMV validation, or authorize a manually assembled workflow in place of the compiler-derived Service Object Graph (SOG). Catalog publication and authorization remain separate from the model's callability property, as defined in Section 2.3.

---

## 7. Architectural Invariants

### Service Model Authority

1. **The SM-DAG is authoritative and exists independently of service requests.**
   - No other IPERA component may define, modify, or supersede its service composition or dependencies.
2. **The SM-DAG defines service-realization obligations; it does not guarantee successful realization.**
3. **Service decomposition terminates at Atomic Nodes (ANs).**
4. **Every SN and AN has an associated Lifecycle Card (LC).**
5. **AN Lifecycle Cards declare governed automation bindings; executable code remains external.**
6. **Only AN Lifecycle Cards may reference external automation implementations.**

### Invocation and APIs

7. **Independent service callability requires a versioned, machine-consumable Service Contract.**
   - Every independently callable service MUST expose a governed service API.
8. **Invocation selects an SM-DAG entry point; it does not alter dependencies.**
9. **IPERA components MUST expose versioned APIs at their defined architectural interfaces.**

### Validation and Compilation

10. **Every compilation MUST pass SMV validation before SOG generation.**
11. **SMV results apply only to the evaluated scope and model revision.**
12. **Validation and compilation MUST use the same model snapshot.**
13. **SMV validates binding conformance, not automation availability or correctness.**
14. **The SOG represents service-realization obligations independently of orchestration engines.**

### Orchestration and Execution

15. **Orchestrators consume SOGs; they do not derive service composition from the SM-DAG.**
16. **Execution pipelines are derived artifacts, never authoritative service definitions.**
17. **Automation executes governed obligations; it does not define service composition.**

### Implementation Independence

18. **IPERA defines functional contracts, not mandatory products.**

---

## 8. Open Architectural Question: State / Evidence / Observability / Reconciliation

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

