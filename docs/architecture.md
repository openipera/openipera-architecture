---
layout: default
title: Architecture
---

# Architecture

## From authoritative knowledge to executable realization

OpenIPERA separates the **description of a service** from the **mechanisms that realize it**.

<div class="journey-callout" markdown="1">
**Follow the architecture:** explore the two views below, then [walk through a virtual machine request](example.md) to see the model in context. Continue with the [technical specifications](documentation.md) for detailed semantics.
</div>

## Two complementary architectural views

<div class="architecture-comparison">
  <article class="architecture-panel">
    <h3>Reference Architecture — What</h3>
    <a class="architecture-image-link" href="{{ '/architecture/reference-architecture/' | relative_url }}" aria-label="View the IPERA Reference Architecture">
      <img src="{{ '/images/ipera-reference-architecture.png' | relative_url }}" alt="IPERA Reference Architecture showing architectural capabilities and relationships" loading="lazy">
    </a>
    <p>The architectural capabilities, responsibilities, and relationships that define IPERA.</p>
    <p><a href="{{ '/architecture/reference-architecture/' | relative_url }}">Explore the Reference Architecture</a></p>
  </article>
  <article class="architecture-panel">
    <h3>Functional Architecture — How</h3>
    <a class="architecture-image-link" href="{{ '/architecture/execution-layers/' | relative_url }}" aria-label="View the IPERA Functional Architecture">
      <img src="{{ '/images/ipe-model.png' | relative_url }}" alt="IPERA Functional Architecture showing execution layers and tooling abstractions" loading="lazy">
    </a>
    <p>The execution layers and tooling abstractions through which architectural responsibilities are realized.</p>
    <p><a href="{{ '/architecture/execution-layers/' | relative_url }}">Explore the Functional Architecture</a></p>
  </article>
</div>

These are **complementary views, not two versions of the same diagram**. The reference architecture defines the architectural model; the functional architecture describes realization abstractions without making any specific tooling the architecture itself.

### The Service Model

The **Service Model DAG (SM-DAG)** represents service decomposition through **Service Nodes (SNs)** and terminal **Atomic Nodes (ANs)**. Each node has a companion **Lifecycle Card (LC)** expressing realization knowledge, such as service dependencies and obligations. An Atomic Node's LC references a stable automation capability identity; it does not contain executable automation.

A service dependency is not necessarily a decomposition relationship or an execution-order instruction. Dependencies may cross service domains, and some obligations are fulfilled by external processes rather than directly executable automation.

### Validate, then compile

The **Service Model Validator (SMV)** independently evaluates model integrity, references, dependencies, cycles, and automation-binding resolvability. It reports findings; it does not silently repair authoritative knowledge or authorize a service.

The **Compiler** combines applicable validated service knowledge with a particular request context to produce a **Service Object Graph (SOG)**. The Compiler must establish that its actual inputs correspond to the referenced SMV validation result and reject inconsistent inputs.

The SOG is a derived, request-specific representation of service obligations and their dependencies. **It is not an executable workflow or a replacement for the authoritative Service Model.**

### Link and execute

An **Orchestrator** consumes the SOG, resolves stable automation capability identities to identifiable implementation revisions through the Automation Registry, and constructs executable workflows. Execution capabilities perform the selected operations and produce outcomes and evidence.

OpenIPERA does not mandate an orchestration engine, automation product, organizational team structure, or persistent storage of complete SOGs.

### Provenance and observability by design

OpenIPERA requires internal hierarchical component identities and revisions, uniquely identifiable SMV validation results, and compilation consistency checks.

Every compiled SOG carries a **provenance manifest** identifying the request context, validation reference, and exact service-model components and revisions consumed. OpenIPERA components emit structured, correlated observability events; mandatory compilation provenance events must be durably accepted internally before SOG publication succeeds.

This **native OpenIPERA instrumentation** is distinct from the broader **IPERA Observability** pillar, which concerns operational assurance and evidence. Similarly, **IPERA Governance** establishes organizational policy and authorization; SMV validation alone is not governance approval.

## Architectural boundaries

| Responsibility | Architectural role |
|---|---|
| Describe services and dependencies | SM-DAG and Lifecycle Cards |
| Validate authoritative knowledge | SMV |
| Derive request-specific obligations | Compiler and SOG |
| Construct and coordinate workflows | Orchestrator |
| Perform operations | Execution capabilities |
| Govern, observe, and accept operational services | Organizational systems and broader IPERA pillars |

For detailed semantics, see [Document 05 — Service Model Compilation Architecture](documentation/05_IPERA_SERVICE_MODEL_COMPILATION_ARCHITECTURE.md) and [Document 06 — Deterministic Service Realization](documentation/06_IPERA_DETERMINISTIC_SERVICE_REALIZATION.md).
