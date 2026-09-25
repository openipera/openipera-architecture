# IPERA Demonstration Project

## What This Repository Is

This repository is not a collection of independent automation experiments.

It is the working architectural record of the **IPERA Service Model** as that model is developed, challenged, experimentally validated, and refined.

The architecture is being developed iteratively:

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

A completed POC is therefore an **experimental record**, not a software release. When an experiment exposes a new architectural question, the previous POC is preserved and a new experiment tests the refined hypothesis.

**The model drives the experiments. The experiments produce evidence. The evidence refines the model.**

### The Service Model

At its current stage of development, the IPERA Service Model separates architectural decomposition, service realization knowledge, and automation implementation identity into distinct structures:

```text
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│         SM-DAG          │   │      LC REGISTRY        │   │   AUTOMATION REGISTRY   │
│                         │   │                         │   │                         │
│ Service Architect       │   │ Domain / Service SME    │   │ Automation Capability   │
│                         │   │                         │   │                         │
│ Service                 │   │ lc_id                   │   │ automation_id (UUID)    │
│   │                     │   │ node_id                 │   │                         │
│   ├── Service           │   │ service_dependencies    │   │ implementation          │
│   │     │               │   │                         │   │ version / commit        │
│   │     └── Atomic Node │   │ automation_name         │   │ path / entrypoint       │
│   │                     │   │ automation_id           │   │ provenance              │
│   └── Service           │   │                         │   │                         │
│                         │   │                         │   │                         │
│ "What does the service  │   │ "What is required to   │   │ "What implementation   │
│  decompose into?"       │   │  realize the service?" │   │  satisfies this ID?"    │
└────────────┬────────────┘   └────────────┬────────────┘   └────────────┬────────────┘
             │                             │                             │
             │ node_id / lc_id             │ automation_id               │
             └──────────────┬──────────────┴─────────────────────────────┘
                            │
                            ▼
                   SERVICE MODEL VALIDATOR
                            SMV
```

These structures have deliberately different responsibilities.

The **SM-DAG** expresses architectural decomposition: what the Service Architect believes the service consists of. Its edges mean **decomposes into**. It contains Service Nodes down to Atomic Nodes and does not encode execution workflow.

The **Lifecycle Card Registry** expresses realization knowledge authored by Domain and Service SMEs. Service-node Lifecycle Cards identify `service_dependencies`. Atomic-node Lifecycle Cards terminate service dependency resolution and instead bind the Atomic Node to an automation capability through an immutable `automation_id`.

The **Automation Registry** resolves that symbolic automation identity to an external implementation. The Service Model therefore identifies the required automation capability without embedding executable automation or its physical implementation into the model.

Conceptually:

```text
SERVICE
   │
   │ decomposes into
   ▼
SERVICE
   │
   │ decomposes into
   ▼
ATOMIC NODE
   │
   │ automation_id
   ▼
AUTOMATION REGISTRY
   │
   ▼
AUTOMATION IMPLEMENTATION
```

### Two Independent Authorities

The SM-DAG and Lifecycle Cards are independently authored.

```text
       SERVICE ARCHITECT                DOMAIN / SERVICE SME
              │                                │
              │ decomposes                     │ composes
              ▼                                ▼
           SM-DAG                        Lifecycle Cards
              \                                /
               \                              /
                └────────────┬───────────────┘
                             ▼
                            SMV
                    Validate + Reconcile
                         + Compile
                             │
                             ▼
                       Execution DAG
                      Derived Realization
```

The Service Architect works **top-down**, decomposing cross-domain service intent.

Domain and Service SMEs work **bottom-up**, describing what is required to realize capabilities within their domains.

Where those independently authored assertions meet, the SMV can compare them:

```text
SM-DAG        Lifecycle Card        Result
------        --------------        ------

 YES               YES             CORROBORATED

 YES                NO             UNCORROBORATED

  NO               YES             UNMODELED

  NO                NO             No asserted relationship
```

Agreement provides corroboration.

Disagreement provides information.

**A discrepancy is information before it is an error.**

The SMV does not silently modify either authoritative source to make the model agree. Policy and governance determine the disposition of reported discrepancies.

### From Service Knowledge to Execution

The Service Model is **source**, not workflow.

The SMV validates the independently authored model, resolves its symbolic references, reports discrepancies, and compiles a derived Execution DAG.

The resulting architecture follows a deliberate separation:

```text
SM-DAG + Lifecycle Cards
          SOURCE
             │
             ▼
            SMV
          COMPILE
             │
             ▼
       Execution DAG
  COMPILED REPRESENTATION
             │
             ▼
        Orchestrator
           LINK
             │
             ▼
    Executable Pipeline
             │
             ▼
    Execution Capability
           RUN
             │
             ▼
      State / Evidence
```

The **Execution DAG is derived output**, not persistent architectural truth and not the executable pipeline itself.

The Orchestrator performs the linker responsibility, resolving the symbolic automation identities to implementations and assembling the executable pipeline.

Execution capabilities then run that linked work.

This produces the foundational IPERA separation:

> **IPERA separates service knowledge from compilation, compilation from linking, and linking from execution.**

The POCs in this repository exist to determine whether these architectural assertions survive implementation.

They should therefore be read as a progression of architectural experiments:

```text
HYPOTHESIS → POC → EVIDENCE → LEARNING → NEXT HYPOTHESIS
```

Earlier POCs are intentionally preserved when later experiments refine or invalidate an earlier assumption. The history of the experiments is part of the architectural evidence.  POC-01, POC-02, and subsequent POCs test distinct hypotheses; they are **not successive
software releases**. Each experiment keeps its own model, runtime, tests, artifacts,
configuration, documentation, and available evidence.

```text
POC-01 — demonstrated by its recorded validation
External model drives execution without hard-coded workflow.
        ↓
POC-02 — demonstrated by its recorded validation
Distributed dependency declarations dynamically derive an Execution DAG.
        ↓
POC-03 — demonstrated within its documented realization semantics
Independent SMV validates decomposition, Lifecycle Cards and Git-held UUID bindings
and derives an Execution DAG without executing automation.
        ↓
POC-04 — independent-authority compilation experiment
SM-DAG and Lifecycle Cards are compared in both directions; policy gates compilation.
```

## Experiments

| Experiment | Record | Learning / boundary |
|---|---|---|
| [POC-01](poc-01/README.md) | External model drives execution; model-only changes alter the derived plan. | Preserves its original schema, service request, automation bindings, and tests. |
| [POC-02](poc-02/README.md) | Distributed dependency declarations derive an inspectable Execution DAG. | Demonstrated dependency derivation; later review identified that decomposition and dependency semantics were not sufficiently separated. Its original model is preserved. |
| [POC-03](poc-03/README.md) | Independent SMV validates separate decomposition, LCs and VCS automation UUIDs, then derives execution structure. | Retains its original overlap-as-redundancy assumption as experimental evidence. |
| [POC-04](poc-04/README.md) | Compares architect decomposition and SME LC requirements as independent authorities, then compiles when policy permits. | Preserves corroboration and reports disagreement without editing either source. |

## Experimental record principle

> **A completed POC is an experimental record. A new architectural hypothesis creates a new POC rather than rewriting the previous experiment.**

Documentation corrections, broken-reference fixes, and similar maintenance are
acceptable. Later discoveries must not be backported in ways that change what an
earlier experiment actually tested. Similar code remains local to each experiment;
there is no shared framework at this stage.

```text
Hypothesis → POC → Evidence → Learning → Next Hypothesis
```

## Repository organization and architecture

- `docs/` contains architecture and specifications that apply across experiments:
  - [Functional Architecture Requirements](docs/IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md)
  - [Minimum Viable Service Model](docs/IPERA_Minimum_Viable_Service_Model.md)
  - [Service Model Compilation Architecture](docs/IPERA_Service_Model_Compilation_Architecture.md)
- `poc-01/`, `poc-02/`, `poc-03/`, and `poc-04/` each contain their own independent experiment and documentation.
- Evidence remains with its generating POC. Historical validation notes are preserved
  as records of their original runs, including statements about the checkout at that time.
- [Reorganization record](docs/REPOSITORY_REORGANIZATION.md) identifies source commits,
  preservation checks, validation results, and evidence unavailable in Git.

Document filenames remain stable; versions belong inside documents and Git records changes.

## Running an experiment

Follow the README inside the selected POC. Start from that directory, for example:

```sh
cd poc-01
# Follow poc-01/README.md, then stop its services before switching experiments.
docker compose up --build
```

For POC-02, use `cd poc-02` from the repository root and follow its README.
Both historical Compose definitions publish ports 18080 and 18081, so run one POC
at a time and run `docker compose down` in its directory before starting the other.
Each POC retains its own build context and model/artifact/evidence mounts.

## Git branching policy

Branches may be used temporarily for normal development, including a branch such as
`poc-03-development`. The permanent record of each completed POC belongs in its own
directory on `main`, so a person cloning `main` receives the complete tracked IPERA
experimental lineage. Historical branches must not be deleted merely for reorganization.

Git history records how files changed. POC directories record what each architectural
experiment consisted of. Both are preserved.
