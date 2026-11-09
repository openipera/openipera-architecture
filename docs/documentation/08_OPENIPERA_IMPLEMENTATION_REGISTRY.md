---
layout: documentation
title: "OpenIPERA Implementation Registry"
documentation_order: 8
---

# OpenIPERA Implementation Registry

**Document:** 08 — OpenIPERA Implementation Registry  
**Status:** Initial public baseline — living record  
**Scope:** Reference and anonymized field implementations

## 1. Purpose

This registry records **what was selected, how it was implemented, and what was learned** when realizing the capabilities defined in [02 — IPERA Functional Capabilities and Tooling Requirements](02_IPERA_FUNCTIONAL_CAPABILITIES_AND_TOOLING_REQUIREMENTS.md).

Document 02 defines architectural responsibilities, explicit non-responsibilities, and qualification of candidate tooling. **This document does not redefine those requirements or certify a product.** It records implementation-specific choices, integration boundaries, deployment progress, observed results, evidence, and gaps. A technology can be architecturally *Vetted* without being deployed, and an implementation can be operational without establishing general architectural conformance.

OpenIPERA is not a workflow engine. Implementations must preserve the separation between authoritative service knowledge, validation and compilation, orchestration, atomic automation execution, and operational evidence.

## 2. Publication and identification

Public records may describe real implementations, including named technologies, architectural patterns, interfaces, integration choices, tests, and lessons learned. Customer or organization identity and identifying operational data must be removed or generalized before publication.

- **RI-001** identifies the publicly reproducible OpenIPERA Reference Implementation.
- **IMP-001**, **IMP-002**, etc. identify distinct field implementations without encoding customer, industry, geography, or engagement names.
- A mapping from public identifiers to customer identities, if maintained, belongs in a separately access-controlled private repository and is **not required** to interpret this public registry.
- Do not publish customer names, identifying IP addresses, hostnames, internal domains, tenant or account identifiers, credentials, confidential diagrams, or distinctive metadata that would defeat anonymization.
- Product names and architecture are not inherently identifying, but combinations of facts should still be reviewed for re-identification risk and applicable contractual exceptions.
- Publish only evidence suitable for public disclosure; retain sensitive source artifacts privately and summarize findings without exposing identifying data.

An implementation record is evidence of that implementation's behavior, **not** a vendor endorsement, partnership statement, or assertion that its tooling is mandatory for IPERA conformance.

## 3. Record model and status

Each implementation entry should contain:

| Field | Required meaning |
|---|---|
| Public ID and profile | Stable opaque ID; reference or anonymized field implementation |
| Scope and context | Service scenarios, environment class, and architectural boundaries, without identifying information |
| Architecture baseline | Applicable numbered OpenIPERA document revisions or commit identifiers |
| Capability mapping | All nine Document 02 capabilities, including intentionally external or unimplemented capabilities |
| Selection and integration | Selected product/component, responsibility, interfaces, dependencies, and alternatives where relevant |
| Implementation state | Planned, In Progress, Validated, or Production for each capability |
| Verification and evidence | Test or operational evidence, reproducible references where public, and precise scope of claims |
| Gaps and decisions | Missing functionality, deviations, risks, and next verification steps |
| Revision history | Dated material changes to the implementation record |

**Implementation state** is separate from Document 02's architectural qualification (*Vetting*, *Provisional*, *Vetted*):

| State | Meaning |
|---|---|
| **Planned** | Candidate or intended approach; no deployment or successful integration claimed |
| **In Progress** | Implementation or integration work underway; end-to-end validation not established |
| **Validated** | Defined tests passed for the recorded scope, with traceable evidence; not necessarily production |
| **Production** | In operational use within the recorded scope; production status alone does not imply general architectural conformance |

Use **Not Recorded** where evidence or status has not been established. Do not infer *Validated* from a working demonstration, a repository artifact, or a vendor's published capabilities alone. When evidence supports only a component-level test, state that narrower scope.

## 4. RI-001 — OpenIPERA Reference Implementation

**Purpose:** Provide a modular, reproducible realization of IPERA's nine capabilities that can run on a lightweight Kubernetes host and be adapted to other Kubernetes distributions or VM-based packaging. The reference deployment direction is k3s; this is an implementation choice, not an architectural dependency.

**Baseline:** Document 02 and the numbered service-model, authoring, compilation, and deterministic-realization documents. Pin exact revisions when a release is published.

The table below is an **initial mapping of discussed directions and existing proof-of-concept work**. Entries are not claims of completed deployment or validation. No unverified maturity status is assigned.

| Document 02 capability | Reference selection / direction | Implementation state | Evidence and open work |
|---|---|---|---|
| **Service Catalog** | Lightweight demonstration request interface; interchangeable with an enterprise catalog through a defined request contract | Planned | Specify the public request/API contract and test catalog-to-model handoff |
| **Service Model Repository** | Demonstration etcd-backed authoritative model store; external model authorities remain supported | Planned | Define model CRUD, identity, revision/snapshot semantics, and LC references |
| **Version Control System (VCS)** | Git-based versioning for source, automation artifacts, and implementation evidence; GitHub is the current project host | In Progress | Repository and POC history exist; verify release provenance and artifact-resolution contracts |
| **Service Model Compiler (including SMV)** | OpenIPERA independent validator and compiler | In Progress | POC-03 validator and POC-04 compilation work provide prior evidence; reconcile their precise tested behavior against current Documents 03–06 before claiming validation |
| **CI/CD Platform** | GitHub Actions is a possible implementation for testing and packaging; CI/CD remains distinct from runtime orchestration | Planned | Define quality gates and reproducible validation pipeline; no pipeline is asserted here |
| **DAG Orchestrator** | Engine-neutral SOG consumer and linker; Airflow and Argo are candidate adapters, not required engines | Planned | Select or prototype an adapter and verify dependency, obligation, failure, and replay semantics |
| **Automation Execution Capability** | Atomic automation via external executors (for example Ansible/AAP, Python, Terraform/OpenTofu), resolved by governed registry identity | Planned | Verify registry binding, invocation, return values, failure handling, and evidence |
| **State / Evidence Capability** | Implementation to be selected; must correlate realization evidence to request, SOG, atomic action, and provenance | Not Recorded | Define evidence schema, storage and retention interfaces, and acceptance tests |
| **Operational Feedback / Observability** | Pluggable telemetry and assurance integrations; no required monitoring vendor | Not Recorded | Define expected-state/observed-state correlation and lifecycle assurance tests |

### 4.1 Architectural boundaries to verify

A conforming reference demonstration must show that:

1. The Service Catalog submits a request without owning the authoritative SM-DAG.
2. The Service Model Repository supplies an identifiable, consistent model revision.
3. The independently callable SMV validates the applicable scope; compilation validates the same model snapshot before SOG generation.
4. The compiler derives a deterministic, request-specific SOG without creating an engine-native workflow or executing automation.
5. An orchestrator/linker consumes the SOG without independently redefining service composition.
6. Automation is resolved at Atomic Nodes through governed bindings and executed by external capabilities.
7. Results and evidence are attributable to the request, model revision, SOG, and atomic actions.
8. Operational feedback can be evaluated against declared lifecycle obligations without turning the model repository into a monitoring system.
9. Components can be replaced at their published boundaries without rewriting the authoritative service model.

These are **verification objectives**, not a declaration that all nine have passed.

### 4.2 Existing proof-of-concept evidence

The repository contains POC-01 through POC-04 artifacts. Earlier work includes an independently callable SMV and a compiler that derives execution structure from service dependencies. Those artifacts are useful evidence sources, but each must be assessed against the **current** architecture baseline and its actual test scope before a capability receives *Validated* status. Do not equate POC completion with production readiness.

## 5. IMP-xxx — Anonymized field implementation template

Create a separate subsection for each publicly releasable implementation. No customer implementation is asserted in this initial edition.

### IMP-xxx — [Non-identifying implementation description]

**Scope:** [Generalized service scenarios and deployment context]  
**Architecture baseline:** [Document revisions / commit]  
**Overall maturity:** [Descriptive summary; avoid one status that obscures capability gaps]

| Capability (Document 02) | Selected tooling | Integration and responsibility boundary | State | Public evidence / gaps |
|---|---|---|---|---|
| Service Catalog | TBD | TBD | Not Recorded | TBD |
| Service Model Repository | TBD | TBD | Not Recorded | TBD |
| Version Control System (VCS) | TBD | TBD | Not Recorded | TBD |
| Service Model Compiler (including SMV) | TBD | TBD | Not Recorded | TBD |
| CI/CD Platform | TBD | TBD | Not Recorded | TBD |
| DAG Orchestrator | TBD | TBD | Not Recorded | TBD |
| Automation Execution Capability | TBD | TBD | Not Recorded | TBD |
| State / Evidence Capability | TBD | TBD | Not Recorded | TBD |
| Operational Feedback / Observability | TBD | TBD | Not Recorded | TBD |

**Realization narrative:** [How service intent was modeled, validated, compiled, linked, executed, and assured.]  
**Demonstrated outcomes:** [Tests and observed results with their limits.]  
**Known deviations and unresolved work:** [Explicit gaps.]  
**Lessons learned:** [Transferable engineering conclusions.]  
**Publication review:** [Record review outcome without publishing customer identity.]

## 6. Evidence and conformance rules

- **Separate observation from inference.** Cite specific tests, artifacts, revisions, and observed results for claims of validation.
- **Scope every claim.** Passing a validator unit test is not proof of complete service realization; an operational workflow is not proof of model-driven compilation.
- **Preserve negative results.** Failures, unsupported obligations, manual gates, and missing capabilities are part of the implementation record.
- **Distinguish selection from qualification.** Document 02 governs candidate architectural fit; this registry governs implementation evidence and state.
- **Distinguish service-model authority from runtime tools.** Service catalogs, model stores, orchestrators, executors, and evidence systems may be supplied by different products.
- **Do not silently revise history.** Material changes should identify the previous implementation baseline and explain what changed.

## 7. Maintenance

The registry is version-controlled with the architecture documentation. New implementation records use the next opaque `IMP-xxx` identifier; identifiers are never recycled. Changes to capability mappings should reference the corresponding Document 02 baseline. Where a reference implementation evolves, retain enough revision and evidence provenance to distinguish prior verified behavior from new, untested functionality.

**Next steps for this initial baseline:** confirm the RI-001 selections against the current repository, attach exact POC evidence and commit references, establish an implementation-specific verification matrix, and add anonymized field records only when their technical details and publication scope have been reviewed.
