# OpenIPE Architecture

## Infrastructure Platform Engineering Reference Architecture (IPERA)

**OpenIPE Architecture** is the working home of the **Infrastructure Platform Engineering Reference Architecture (IPERA)**.

IPERA explores a simple architectural question:

> **Can the knowledge required to realize infrastructure services be modeled independently from the automation that implements them, then compiled into an executable realization when the service is requested?**

The reference architecture separates **service knowledge**, **compilation**, **governance and orchestration**, and **execution** so that infrastructure services can evolve without encoding their end-to-end coordination in hand-built pipelines.

> **The Service Model is knowledge, not workflow. If you want the workflow, compile it.**

---

## IPERA at a Glance

<!-- Planned graphic: docs/images/ipera-overview.png -->
<!--
When available:

![IPERA at a Glance](docs/images/ipera-overview.png)
-->

```text
        SERVICE REQUEST
              │
              ▼
        SERVICE MODEL
         SM-DAG + LCs
              │
              ▼
           COMPILE
              │
              ▼
            EX-DAG
              │
              ▼
   GOVERN / ORCHESTRATE
              │
              ▼
          AUTOMATION
              │
              ▼
       REALIZED SERVICE
              │
              ▼
      STATE / EVIDENCE
```

The end-to-end realization is an **output** of the Service Model, not an input to it.

IPERA does not require the Service Model to contain a manually maintained workflow. Instead, it captures the distributed, local knowledge needed to derive one.

---

## The Core Idea: Model How We Reason About Services

When someone asks:

> *What do you need to do to make my application run on PCI-compliant infrastructure?*

an experienced engineer does not begin with a pipeline. The engineer recursively reasons about what is required:

```text
Application requires PCI-compliant infrastructure
        │
        ▼
PCI-compliant cluster
        │
        ├── PCI-compliant compute
        ├── PCI-compliant storage
        └── PCI-compliant network
                │
                ▼
              ...
```

Each service needs to know only its **local relationships and realization requirements**.

A parent service does not need to know the internals of the services it requires.

Think of the Service Model as a box of compatible Lego pieces:

> **Blue knows it connects to Red. Red knows it connects to Yellow and Green. Blue does not need to know Yellow and Green exist.**

The compiler recursively resolves those local relationships into the complete proposed realization.

If the requested service cannot be resolved through known services to realizable capabilities, compilation fails because the model does not know how to build it.

That is different from a valid realization being rejected by governance, and different again from an execution failure.

---

## Service Knowledge

At the current stage of the architecture, service knowledge is separated into complementary structures.

### Service Model DAG (SM-DAG)

The **SM-DAG** expresses architectural decomposition.

It answers:

> **What does this service decompose into?**

Its relationships are local and explicit. A Service Node knows what it directly decomposes into; it does not restate the internal decomposition of its children.

The SM-DAG is not an execution workflow.

### Lifecycle Card (LC)

The **Lifecycle Card** contains the realization knowledge associated with a Service Model node.

It answers:

> **What is required to realize this service?**

The LC is the connective tissue between the fully abstract service and the fully concrete automation.

A requirement in an LC may constrain which services can satisfy a realization. For example, a service requiring PCI compliance cannot simply be decomposed into ordinary infrastructure and labeled PCI afterward. The model must contain service capabilities capable of satisfying that requirement.

Lifecycle Cards describe **current realization knowledge**. They do not preserve historical realizations by pinning every live service definition to old implementation revisions.

### Atomic Node (AN)

An **Atomic Node** marks the boundary at which further service decomposition stops and the required capability can be bound to automation.

The Atomic Node identifies the automation capability required to perform the work without embedding the implementation itself into the Service Model.

### Automation Identity and Implementation

Automation identity remains separate from automation implementation.

Conceptually:

```text
SERVICE
   │
   │ decomposes into / requires
   ▼
SERVICE
   │
   ▼
ATOMIC NODE
   │
   │ symbolic automation identity
   ▼
AUTOMATION CAPABILITY
   │
   ▼
AUTOMATION IMPLEMENTATION
```

Changing an automation implementation should not require rewriting service intent.

---

## Compilation and the EX-DAG

The Service Model contains the knowledge necessary to reason about realization.

The compiler uses that knowledge to derive a complete realization for a requested service.

```text
REQUEST + SERVICE KNOWLEDGE
            │
            ▼
         COMPILER
            │
            ▼
          EX-DAG
   DERIVED REALIZATION
```

The **Execution DAG (EX-DAG)** is a compiled representation of the proposed realization.

It is:

- derived rather than independently authored;
- explicit enough for downstream systems to consume without rediscovering service semantics;
- a point-in-time representation of the realization that was derived; and
- the place where immutable provenance can identify the exact source states and automation implementations associated with that realization.

The live Service Model remains current and can continue to evolve.

> **IPERA does not freeze the Service Model. It freezes the provenance of each realization.**

Or, more simply:

> **The deck can change. The deck used for a realization cannot.**

---

## Governance Is Not Service Decomposition

IPERA distinguishes between knowing **how** to realize a service and determining whether a proposed realization is **permitted**.

A Service Model may successfully compile a complete EX-DAG and still be rejected by governance.

Conversely, governance cannot make an unrealizable service realizable. If the Service Model cannot resolve a requested capability, there is no valid realization to govern.

The architecture therefore treats the EX-DAG as a contract boundary for governance integration:

> **Is the EX-DAG sufficient for the selected governance mechanism to evaluate the proposed realization? If not, what additional context must accompany it?**

IPERA does not prescribe a particular policy engine, policy language, approval mechanism, or evaluation timing.

Governance requirements should not be embedded into the SM-DAG merely to compensate for insufficient information at the governance boundary.

---

## Architectural Separation

The current architectural model can be summarized as:

```text
SERVICE REQUEST
      │
      ▼
SERVICE KNOWLEDGE
SM-DAG + Lifecycle Cards
      │
      ▼
COMPILATION
Resolve + Validate + Derive
      │
      ▼
EX-DAG
Compiled Realization + Provenance
      │
      ▼
GOVERNANCE / ORCHESTRATION
Evaluate + Link + Coordinate
      │
      ▼
EXECUTION
Automation + APIs + Platforms
      │
      ▼
STATE / EVIDENCE
```

This produces a foundational separation:

> **IPERA separates service knowledge from compilation, compilation from orchestration and governance, and derived intent from execution.**

A product may implement more than one architectural role. The roles remain distinct even when their implementations are combined.

---

## Functional Architecture Requirements

<!-- Planned graphic: docs/images/ipera-requirements-layers.png -->
<!--
When available:

![IPERA Requirements Layers](docs/images/ipera-requirements-layers.png)
-->

The IPERA requirements are organized around architectural responsibilities rather than products:

```text
┌─────────────────────────────────────────┐
│          SERVICE CONSUMPTION            │
│      Request • Intent • Context         │
├─────────────────────────────────────────┤
│            SERVICE KNOWLEDGE            │
│       SM-DAG • Lifecycle Cards          │
├─────────────────────────────────────────┤
│              COMPILATION                │
│   Resolution • Validation • EX-DAG      │
├─────────────────────────────────────────┤
│       GOVERNANCE & ORCHESTRATION        │
│     Policy • Linking • Coordination     │
├─────────────────────────────────────────┤
│              EXECUTION                  │
│     Automation • APIs • Platforms       │
├─────────────────────────────────────────┤
│       EVIDENCE & OBSERVED STATE         │
│    Provenance • Results • Telemetry     │
└─────────────────────────────────────────┘
```

The normative architecture belongs in the requirements and specification documents under `docs/`.

The experiments and reference implementations exist to test those architectural assertions, not to define them accidentally.

---

## Architecture Through Experimentation

IPERA is being developed using an evidence-driven process:

```text
ARCHITECTURAL HYPOTHESIS
          │
          ▼
        MODEL
          │
          ▼
         POC
          │
          ▼
       EVIDENCE
          │
          ▼
       LEARNING
          │
          ├──────────────► validates the model
          │
          └──────────────► changes the model
                              │
                              ▼
                       NEXT HYPOTHESIS
```

A completed POC is an **experimental record**, not a software release.

When evidence changes the architecture, the earlier experiment is preserved rather than rewritten to agree with the new model.

> **The model drives the experiments. The experiments produce evidence. The evidence refines the model.**

### Experimental Record

| Experiment | Architectural question / evidence |
|---|---|
| [POC-01](poc-01/README.md) | Can an external service model drive execution without a hard-coded workflow? |
| [POC-02](poc-02/README.md) | Can distributed dependency declarations dynamically derive an inspectable Execution DAG? |
| [POC-03](poc-03/README.md) | Can an independent validator verify decomposition, Lifecycle Cards, and automation bindings while deriving execution structure? |
| [POC-04](poc-04/README.md) | What happens when architect decomposition and SME realization assertions are treated as independent authorities and compared during compilation? |

POC-04 remains evidence from a particular architectural hypothesis. Subsequent architectural reasoning may refine or reject assumptions tested by that experiment without changing its historical record.

### Experimental Record Principle

> **A completed POC is an experimental record. A new architectural hypothesis creates a new POC rather than rewriting the previous experiment.**

Documentation corrections and broken-reference fixes are acceptable. Later discoveries must not be backported in ways that change what an earlier experiment actually tested.

---

## IPERA Engine

The repository intentionally reserves space for an **IPERA Engine**: an experimental implementation of architectural capabilities such as service resolution, validation, compilation, EX-DAG generation, and related functions.

The exact scope and name of the engine are intentionally not fixed yet.

> **The engine implements the architecture. The engine does not define the architecture.**

This distinction allows implementation ideas to evolve rapidly without turning implementation choices into architectural requirements.

---

## Repository Organization

The repository is evolving toward the following structure:

```text
openipe-architecture/
│
├── README.md
│
├── docs/
│   ├── architecture requirements
│   ├── service model specifications
│   ├── compilation architecture
│   └── images/
│
├── poc-01/
├── poc-02/
├── poc-03/
├── poc-04/
├── ...
│
├── engine/                 # future experimental IPERA Engine
│
└── demonstration/          # future integrated reference demonstration
```

Current architecture and specification documents include:

- [Functional Architecture Requirements](docs/IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md)
- [Minimum Viable Service Model](docs/IPERA_Minimum_Viable_Service_Model.md)
- [Service Model Authoring Rules](docs/IPERA_SERVICE_MODEL_AUTHORING_RULES.md)
- [Service Model Compilation Architecture](docs/IPERA_Service_Model_Compilation_Architecture.md)

Document filenames may remain stable while Git records their evolution.

---

## What IPERA Is Not

IPERA is not:

- another infrastructure automation product;
- a requirement to replace existing tools;
- a prescribed orchestrator;
- a prescribed policy engine;
- a manually authored universal workflow;
- an AI dependency; or
- an excuse to hide coordination inside a box labeled *automation happens here*.

IPERA is a reference architecture for making the knowledge required to deliver infrastructure services **explicit, composable, compilable, governable, and executable** using replaceable implementation technologies.

---

## Current Status

The architecture is under active development.

The existing POCs establish an experimental lineage. The next phase is to rebuild the functional architecture requirements around the refined model described here, then use new experiments to challenge those requirements.

The architecture should be considered provisional wherever evidence has not yet validated an assertion.

That is intentional.

**OpenIPE treats architecture as a hypothesis to be tested, not a diagram to be defended.**
