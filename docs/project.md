---
layout: default
title: Project
section: project
---

# The OpenIPERA project

OpenIPERA is an open, implementation-independent architecture developed through technical specifications and experimental implementations. This website is the reading home for the architecture; GitHub hosts its source, collaboration, and experimental evidence.

## Implementation and evidence

Start with the [Implementation Registry](documentation/08_OPENIPERA_IMPLEMENTATION_REGISTRY.md) for implementation selections and progress. The [historical retrospective](documentation/POC_HISTORICAL_RETROSPECTIVE.md) explains what the experiments established and their limits.

| Experiment | Question explored | Source and evidence |
| --- | --- | --- |
| POC-01 | Can an external service model drive execution without a hard-coded workflow? | [Experiment](https://github.com/openipera/openipera-architecture/tree/main/poc-01) · [Validation](https://github.com/openipera/openipera-architecture/blob/main/poc-01/docs/VALIDATION.md) |
| POC-02 | Can distributed dependencies derive an inspectable execution graph? | [Experiment](https://github.com/openipera/openipera-architecture/tree/main/poc-02) · [Validation](https://github.com/openipera/openipera-architecture/blob/main/poc-02/docs/POC-02-VALIDATION.md) |
| POC-03 | Can an independent validator verify decomposition, Lifecycle Cards, and automation bindings? | [Experiment](https://github.com/openipera/openipera-architecture/tree/main/poc-03) · [Validation](https://github.com/openipera/openipera-architecture/blob/main/poc-03/evidence/VALIDATION.md) |
| POC-04 | What happens when decomposition and realization assertions are compared during compilation? | [Experiment](https://github.com/openipera/openipera-architecture/tree/main/poc-04) · [Validation](https://github.com/openipera/openipera-architecture/blob/main/poc-04/evidence/VALIDATION.md) |

These experiments test architectural hypotheses. They are not production-ready releases. **Architectural specifications take precedence over examples and experimental implementations.**

## Source and contribution

[Browse the source repository](https://github.com/openipera/openipera-architecture), [review project history](https://github.com/openipera/openipera-architecture/commits/main/), or [open an issue](https://github.com/openipera/openipera-architecture/issues) to discuss a correction, question, or proposed improvement. Propose reviewed changes through [pull requests](https://github.com/openipera/openipera-architecture/pulls).

For architecture discussions, reference the relevant [numbered document](documentation.md) and distinguish architectural requirements from implementation choices. Individual documents provide a discreet source link for inspecting their Markdown.

## Licensing and identity

Software uses Apache 2.0. Original documentation and diagrams use CC BY 4.0; OpenIPERA branding is reserved. Read [licensing and attribution](licensing.md) for the scope and links to the authoritative license and branding files.
