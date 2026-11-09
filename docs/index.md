---
layout: default
title: OpenIPERA
---

# OpenIPERA

## Model the system. Derive the obligations. Use the tools you already have.

**OpenIPERA models the system. Orchestration and automation operate the system.**

Modern IT organizations have powerful automation platforms, but the knowledge needed to deliver a complete operational service is often scattered across service catalogs, architecture diagrams, scripts, teams, and policies.

Automating a task is not the same as understanding the service that task supports.

**OpenIPERA is an open, implementation-independent architecture for representing, validating, and compiling service knowledge into the obligations required to realize an enterprise service.** It is not another workflow engine or automation framework.

## From intent to realization

A request for a service—whether a simple Virtual Machine or a complex Electronic Medical Record (EMR) system—requires more than provisioning infrastructure or installing software. Both require the identification and satisfaction of dependencies, operational requirements, security controls, governance obligations, monitoring, and acceptance criteria necessary to deliver a fully operational service.

The complexity differs, but the underlying principle does not: every service must be modeled in terms of what must be true, what must happen, and what must remain true throughout its operational lifecycle.

OpenIPERA makes those relationships explicit:

```text
Authoritative service knowledge
   SM-DAG + Lifecycle Cards
             |
     Service Model Validator
             |
Compiler + request context
             |
  Service Object Graph (SOG)
             |
       Orchestrator
             |
     Execution capabilities
             |
     Outcomes and evidence
```

The **Service Object Graph (SOG)** is a request-specific mathematical representation of the obligations and dependencies required to operationalize a need. It expresses **what must be accomplished**, not a prescribed sequence of automation commands.

[Explore the architecture](architecture.html) · [Walk through an example](example.html)

## What makes this different?

**Knowledge is not workflow.** Service definitions and dependencies remain independent of the execution engine. A change in orchestration technology should not force the enterprise to reconstruct its service model.

**Validation precedes compilation.** The Service Model Validator (SMV) identifies structural and referential inconsistencies. The Compiler verifies that the knowledge it actually uses matches the referenced validation result.

**Provenance is built in.** Each compiled SOG carries a manifest identifying the service knowledge used. OpenIPERA durably accepts mandatory compilation provenance events internally before reporting successful SOG publication.

**Responsibilities remain distinct.** OpenIPERA models and compiles obligations. Orchestration constructs executable workflows; automation performs actions. The consuming organization's governance and operational systems determine authorization, acceptance, runtime state, and evidence retention.

## An architecture tested through experiments

OpenIPERA is an evolving, evidence-driven architecture. Its proof-of-concept implementations test architectural hypotheses; they are **not** presented as production-ready releases.

[Read the technical documentation](documentation.html) · [Explore the GitHub repository](https://github.com/openipera/openipera-architecture)

> **Workflows are derived from knowledge of the system. Knowledge of the system is not derived from workflows.**
