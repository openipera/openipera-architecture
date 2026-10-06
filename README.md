# OpenIPE Architecture

## Infrastructure Platform Engineering Reference Architecture (IPERA)

**OpenIPE Architecture** is the working home of the **Infrastructure Platform Engineering Reference Architecture (IPERA)**.

IPERA separates the knowledge required to realize infrastructure services from the automation that implements them, and defines the capabilities that turn enterprise intent into governed, consumable infrastructure services.

> **The Service Model is knowledge, not workflow. If you want the workflow, compile it.**

---

## IPERA Reference Architecture

**<<<<<<<<<< IPERA REFERENCE ARCHITECTURE GRAPHIC HERE >>>>>>>>>>**

The **IPERA Reference Architecture** is the capability view: **what must exist**.

Its central capability stack is:

- **Enterprise Services** — governed service catalog offerings and service contracts.
- **Service Realization** — Service Model, dependency resolution, compilation, and the Service Object Graph (SOG).
- **Orchestration** — consumes the SOG, links it into the native pipeline semantics of the selected orchestration platform, and coordinates execution.
- **Automation** — reusable automation capabilities, automation engines, and APIs that perform discrete infrastructure operations.
- **Control Planes** — management interfaces to infrastructure and platform services.
- **Infrastructure Domains** — consumable resources including compute, network, storage, virtualization, hyperscalers, GPU infrastructure, and future technologies.

**Governance, Security & Compliance** and **Observability** are cross-cutting capabilities spanning the architecture.

Products may implement more than one IPERA capability. The architectural responsibilities remain distinct even when a product spans them.

---

## IPE Model

**<<<<<<<<<< IPE MODEL GRAPHIC HERE >>>>>>>>>>**

The **IPE Model** is the behavioral view: **how the capabilities work together to realize a service**.

    Enterprise Intent / Service Contract
                  ↓
             Service Model
                  ↓
           Resolve (Compile)
                  ↓
       Service Object Graph (SOG)
                  ↓
          Orchestrate (Link)
                  ↓
          Executable Pipeline
                  ↓
               Execute

### Compile

Compilation recursively resolves the requested service and its dependencies into a fully realized, ordered **Service Object Graph (SOG)**.

The compiler determines what must execute and the dependency-constrained order in which it may execute, including opportunities for parallel execution.

### Service Object Graph

The **SOG** is the platform-independent, point-in-time compiled representation of a specific service realization. It contains the fully resolved service graph, execution dependencies, symbolic automation calls, and realization provenance.

### Link

The orchestrator consumes the SOG and dynamically constructs an executable pipeline by translating the SOG's already-derived execution semantics into the native semantics of the selected orchestration platform.

**Linking does not determine service dependencies or execution order; it translates them.**

### Execute

The selected platform executes the dynamically constructed pipeline and dispatches the realizing automation.

> **The compiler determines what must execute and the dependency-constrained order in which it may execute. The linker determines how that already-compiled graph is represented and executed by a particular orchestration platform.**

---

## Service Model

**<<<<<<<<<< SERVICE MODEL GRAPHIC HERE — SM-DAG / LC / AUTOMATION REGISTRY >>>>>>>>>>**

The Service Model separates three forms of knowledge.

### SM-DAG

The **Service Model DAG (SM-DAG)** expresses architectural decomposition. It contains two node types:

- **Service Node (SN)** — represents a service capability and may decompose into other SNs or ANs.
- **Atomic Node (AN)** — terminal point in service decomposition and the boundary to an automation capability.

SM-DAG relationships are local. A node knows its direct relationships, not the internal decomposition of the services to which it connects.

### Lifecycle Card

A **Lifecycle Card (LC)** is the companion realization knowledge associated with every SN and AN.

The LC describes what is required to realize its service. At an AN, that knowledge terminates in a symbolic automation identity.

### Automation Registry

The **Automation Registry** resolves symbolic automation identity to a concrete automation implementation.

This keeps service knowledge independent of implementation details and allows automation to evolve without rewriting service intent.

---

## Realization Provenance

The Service Model is living, current knowledge. A compiled realization is a point-in-time artifact.

The SOG preserves the exact source and implementation provenance required to understand the realization that was compiled, even as the live Service Model and automation implementations continue to evolve.

> **IPERA does not freeze the Service Model. It freezes the provenance of each realization.**

If the Service Model cannot resolve a requested service to realizable capabilities, compilation fails.

---

## Governance

Governance evaluates whether a valid proposed realization may proceed. It does not define Service Model decomposition or rediscover execution dependencies.

The SOG must therefore be consumable by external governance mechanisms and expose, or provide references to, sufficient context for the proposed realization to be evaluated.

IPERA defines this architectural contract without prescribing a particular policy engine, approval mechanism, policy language, or implementation technology.

---

## Functional Architecture

**<<<<<<<<<< LAYERED REQUIREMENTS GRAPHIC HERE >>>>>>>>>>**

The normative architecture is defined in the architecture and specification documents under `docs/`.

Current documents include:

- [Functional Architecture Requirements](docs/IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md)
- [Minimum Viable Service Model](docs/IPERA_Minimum_Viable_Service_Model.md)
- [Service Model Authoring Rules](docs/IPERA_SERVICE_MODEL_AUTHORING_RULES.md)
- [Service Model Compilation Architecture](docs/IPERA_Service_Model_Compilation_Architecture.md)

The demonstration and experiments test the architecture. They do not define it.

---

## Architecture Through Experimentation

IPERA is developed as an evidence-driven reference architecture:

    HYPOTHESIS → MODEL → POC → EVIDENCE → LEARNING → NEXT HYPOTHESIS

A completed POC is an **experimental record**, not a software release. When evidence changes the architecture, the earlier experiment is preserved rather than rewritten to agree with the new model.

> **The model drives the experiments. The experiments produce evidence. The evidence refines the model.**

| Experiment | Architectural question |
|---|---|
| [POC-01](poc-01/README.md) | Can an external service model drive execution without a hard-coded workflow? |
| [POC-02](poc-02/README.md) | Can distributed dependency declarations dynamically derive an inspectable execution graph? |
| [POC-03](poc-03/README.md) | Can an independent validator verify decomposition, Lifecycle Cards, and automation bindings while deriving execution structure? |
| [POC-04](poc-04/README.md) | What happens when architect decomposition and SME realization assertions are treated as independent authorities and compared during compilation? |

> **A completed POC is an experimental record. A new architectural hypothesis creates a new POC rather than rewriting the previous experiment.**

---

## IPERA Engine

The repository reserves space for an experimental **IPERA Engine** exploring Service Model resolution, validation, compilation, SOG generation, and related architectural capabilities.

Its exact scope and name remain intentionally open.

> **The engine implements the architecture. The engine does not define the architecture.**

---

## Repository Organization

    openipe-architecture/
    │
    ├── README.md
    ├── docs/                   # architecture and specifications
    ├── poc-01/                 # preserved experimental records
    ├── poc-02/
    ├── poc-03/
    ├── poc-04/
    ├── ...
    ├── engine/                 # future IPERA Engine
    └── demonstration/          # future integrated reference demonstration

---

## What IPERA Is Not

IPERA is not another infrastructure automation product, a requirement to replace existing tools, a prescribed orchestrator or policy engine, a manually authored universal workflow, or an AI dependency.

It is a reference architecture for making infrastructure service knowledge **explicit, composable, compilable, governable, and executable** using replaceable implementation technologies.

---

## Status

IPERA is under active development. Architectural assertions are expected to be challenged through experimentation and refined when the evidence requires it.

**OpenIPE treats architecture as a hypothesis to be tested, not a diagram to be defended.**
