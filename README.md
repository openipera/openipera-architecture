# IPERA Demonstration Project

This repository preserves a progression of IPERA architectural experiments. POC-01,
POC-02, and subsequent POCs test distinct hypotheses; they are **not successive
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
