# OpenIPE Architecture

## Infrastructure Platform Engineering Reference Architecture (IPERA)

**OpenIPE Architecture** is the working home of the **Infrastructure Platform Engineering Reference Architecture (IPERA)**.

IPERA separates the knowledge required to realize infrastructure services from the automation that implements them. That knowledge can then be compiled into a complete realization when a service is requested.

> **The Service Model is knowledge, not workflow. If you want the workflow, compile it.**

---

## Architecture at a Glance

**<<<<<<<<<< IPERA ARCHITECTURE GRAPHIC HERE >>>>>>>>>>**

The end-to-end realization is an **output** of the Service Model, not an input to it.

IPERA separates service knowledge, compilation, governance and orchestration, execution, and evidence into distinct architectural responsibilities. Products may implement more than one responsibility without changing those boundaries.

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

## Compilation and the EX-DAG

**<<<<<<<<<< COMPILATION / EX-DAG GRAPHIC HERE >>>>>>>>>>**

A service request is resolved through the Service Model and compiled into an **Execution DAG (EX-DAG)**.

The EX-DAG is a derived, point-in-time representation of the proposed realization. It is not independently authored architectural truth.

If the Service Model cannot resolve the requested service to realizable capabilities, compilation fails.

> **IPERA does not freeze the Service Model. It freezes the provenance of each realization.**

---

## Governance, Orchestration, and Execution

The EX-DAG provides the derived realization to downstream governance and orchestration capabilities.

Governance determines whether a valid proposed realization may proceed. Orchestration coordinates the permitted realization. Execution capabilities perform the work.

IPERA defines these architectural responsibilities and integration boundaries without prescribing a particular policy engine, orchestrator, automation platform, or implementation technology.

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

```text
HYPOTHESIS → MODEL → POC → EVIDENCE → LEARNING → NEXT HYPOTHESIS
```

A completed POC is an **experimental record**, not a software release. When evidence changes the architecture, the earlier experiment is preserved rather than rewritten to agree with the new model.

> **The model drives the experiments. The experiments produce evidence. The evidence refines the model.**

| Experiment | Architectural question |
|---|---|
| [POC-01](poc-01/README.md) | Can an external service model drive execution without a hard-coded workflow? |
| [POC-02](poc-02/README.md) | Can distributed dependency declarations dynamically derive an inspectable Execution DAG? |
| [POC-03](poc-03/README.md) | Can an independent validator verify decomposition, Lifecycle Cards, and automation bindings while deriving execution structure? |
| [POC-04](poc-04/README.md) | What happens when architect decomposition and SME realization assertions are treated as independent authorities and compared during compilation? |

> **A completed POC is an experimental record. A new architectural hypothesis creates a new POC rather than rewriting the previous experiment.**

---

## IPERA Engine

The repository reserves space for an experimental **IPERA Engine** exploring service resolution, validation, compilation, EX-DAG generation, and related architectural capabilities.

Its exact scope and name remain intentionally open.

> **The engine implements the architecture. The engine does not define the architecture.**

---

## Repository Organization

```text
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
```

---

## What IPERA Is Not

IPERA is not another infrastructure automation product, a requirement to replace existing tools, a prescribed orchestrator or policy engine, a manually authored universal workflow, or an AI dependency.

It is a reference architecture for making infrastructure service knowledge **explicit, composable, compilable, governable, and executable** using replaceable implementation technologies.

---

## Status

IPERA is under active development. Architectural assertions are expected to be challenged through experimentation and refined when the evidence requires it.

**OpenIPE treats architecture as a hypothesis to be tested, not a diagram to be defended.**
