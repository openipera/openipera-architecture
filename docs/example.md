---
layout: default
section: architecture
title: Worked Example
---

# A request is more than a workflow

## Example: provision a virtual machine as an operational service

Imagine a consumer requesting a Linux virtual machine.

A conventional provisioning workflow might create the VM, assign CPU and memory, attach storage, and configure networking. Those operations matter—but they may not fulfill the service contract.

The complete obligation set could also include identity integration, security policy, secrets handling, CMDB registration, monitoring, centralized logging, validation, and an authorized acceptance decision. The actual requirements come from the organization's authoritative service knowledge and the specific request.

## How OpenIPERA approaches the request

**1. Model service knowledge.** The SM-DAG describes the applicable services and their decomposition. Companion Lifecycle Cards declare dependencies and realization obligations. A VM service may depend on a storage service without storage being modeled as a child of the VM.

**2. Validate the knowledge.** The SMV checks node and LC relationships, dependency integrity, cycles, and resolvable automation capability references. It reports gaps or inconsistencies rather than inventing missing knowledge.

**3. Compile the request.** The Compiler applies the validated model to the request context and produces a SOG representing the obligations needed for *this* VM. The SOG records its compilation provenance.

**4. Orchestrate realization.** A consuming Orchestrator interprets the SOG, selects identifiable automation implementations, and builds an executable workflow appropriate to its execution environment.

**5. Establish operational outcomes.** Execution and organizational systems provide evidence of what was actually performed and what currently exists. Applicable governance determines whether the service may be accepted.

## Why the distinction matters

The service model can remain stable while automation engines change. Conversely, changes in service obligations can be validated and compiled without manually reconstructing a static workflow as the source of truth.

Not every obligation is an automation action. Some are external approvals, policy decisions, or ongoing operational conditions. OpenIPERA represents those obligations without claiming that its Compiler performs or authorizes them.

> **The SOG describes what must be accomplished. Orchestration determines how to coordinate its realization.**

[See the architecture](architecture.html) · [Read the specifications](documentation.html)
