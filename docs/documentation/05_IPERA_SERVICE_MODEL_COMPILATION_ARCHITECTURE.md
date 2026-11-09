---
layout: documentation
title: "IPERA Service Model Compilation Architecture"
documentation_order: 5
---

# IPERA Service Model Compilation Architecture

## 1. Executive Architecture Summary (TL;DR)

**Quick read:** This section summarizes the architecture and its boundaries. **Deep read:** Continue with Section 2 and the remaining sections for the detailed service-model, validation, compilation, orchestration, and governance semantics.

**OpenIPERA models the knowledge required to realize an enterprise service. It is not another workflow engine.**

The authoritative **Service Model** combines the service definitions and decomposition expressed in the **SM-DAG** with the realization knowledge captured in **Lifecycle Cards**. The **Service Model Validator (SMV)** validates those assertions and reports discrepancies. Given applicable validated service knowledge and **request context**, the **Compiler** derives a request-specific **Service Object Graph (SOG)**: a mathematical representation of the obligations and dependencies required to fulfill that request.

A consuming **Orchestrator** interprets the SOG and constructs an executable workflow; **Execution Capabilities** perform assigned actions and report outcomes and evidence. Within the broader **IPERA** architecture, the **Observability** and **Governance** pillars provide operational assurance, policy, and acceptance authority. These are distinct architectural responsibilities, not mandated products, teams, or deployment boundaries.

```text
       AUTHORITATIVE SERVICE KNOWLEDGE
         SM-DAG        Lifecycle Cards
            \              /
             +------+-----+
                    |
                    v
                   SMV
           Validate + Report
                    |
                    v
                 COMPILER <----- Request Context
                    |
                    v
                   SOG
       Request-Specific Obligations
                    |
                    v
               ORCHESTRATOR
          Construct / Coordinate
                    |
                    v
           EXECUTABLE WORKFLOW
                    |
                    v
           EXECUTION CAPABILITIES
                    |
                    v
             STATE / EVIDENCE
                    |
                    v
       IPERA OBSERVABILITY / GOVERNANCE
          Assurance / Acceptance
```

The SOG represents **what must be accomplished**, not engine-specific instructions. OpenIPERA does not prescribe an orchestrator, execution technology, organizational operating model, or SOG retention mechanism. The consuming organization determines applicable operational and retention policies.

> **OpenIPERA models the system. Orchestration and automation operate the system.**

**Deep read begins below.** The following sections explain the source authorities, validation rules, compilation semantics, linking and runtime boundaries, and governance interfaces in detail.

---

## 2. Purpose and Foundational Principle

OpenIPERA treats the **Service Model as authoritative source knowledge**, not as workflow.

The Service Model describes the services that exist, their decomposition, and their realization requirements. Given a specific request, the Compiler derives a **Service Object Graph (SOG)** representing the obligations required to fulfill that request. Execution workflows are constructed downstream by orchestration rather than independently authored as persistent service-model truth.

This establishes the fundamental OpenIPERA transformation:

```text
SERVICE MODEL + REQUEST CONTEXT
       Authoritative Knowledge
                 |
                 v
       SERVICE MODEL VALIDATOR
          Validate + Report
                 |
                 v
              COMPILER
       Derive Service Obligations
                 |
                 v
                SOG
     Request-Specific Realization
                 |
                 v
            ORCHESTRATOR
       Construct Execution Workflow
                 |
                 v
         EXECUTION CAPABILITY
                 |
                 v
           STATE / EVIDENCE
```

The distinction is foundational:

- **Service Model:** Describes the services that exist, their decomposition, and their realization requirements.
- **Service Object Graph (SOG):** Represents the complete set of service obligations and their relationships required to fulfill a specific request.
- **Execution workflow:** Represents how an orchestration engine coordinates fulfillment of those obligations.

The SOG describes **what must be accomplished**, not the engine-specific instructions for accomplishing it. It is derived output, not independently maintained architectural truth.

When the authoritative Service Model changes, subsequent compilations use the updated, validated knowledge under applicable policy. An existing approved realization and its execution evidence MUST NOT be silently mutated merely because the Service Model changed.

This gives OpenIPERA a familiar and deliberate architectural pattern:

```text
SOURCE → VALIDATE → COMPILE → LINK → EXECUTE
```

The remainder of this document defines how OpenIPERA applies that pattern to service realization.

---
## 3. Two Independent Authorities

The OpenIPERA Service Model represents **two distinct, independently maintained forms of authoritative service knowledge**.

The **Service Model DAG (SM-DAG)** represents service decomposition: what a service consists of.

The **Lifecycle Card (LC)** represents realization requirements: what a service requires to be fulfilled, including dependencies and, for Atomic Nodes, automation capability bindings.

Independence belongs to the **assertions**, not necessarily to different people, teams, or reporting structures. The same contributor may author both perspectives, or different contributors may do so.

```text
                  SERVICE KNOWLEDGE
                         |
                +--------+--------+
                |                 |
                v                 v
              SM-DAG        LIFECYCLE CARDS
           Decomposition     Requirements
                |                 |
                +--------+--------+
                         |
                         v
                        SMV
                 Validate + Report
```

For example:

```text
SM-DAG assertion:
    "General Purpose Compute decomposes into Storage."

Lifecycle Card assertion:
    "General Purpose Compute requires Storage."
```

These are related but **not equivalent** assertions. The first describes composition; the second describes a realization dependency. Their coexistence may provide corroborating evidence, but the absence of one does not automatically invalidate the other. LC-declared dependencies may reference modeled Service Nodes or Atomic Nodes, or explicitly identified external processes.

Agreement provides evidence. Disagreement provides information. The SMV MUST preserve the distinction between the assertions, report discrepancies, and MUST NOT silently change either authoritative source to force agreement.

### Ownership and Organizational Neutrality

**OpenIPERA requires explicit ownership and accountability wherever authoritative decisions are made. It does not prescribe organizational structures, job titles, reporting relationships, or operating models through which those responsibilities are exercised.**

Ownership boundaries matter even when the organizational arrangement varies:

- **The Business owns the business requirement and its acceptance criteria.** Technical implementation authorities cannot unilaterally redefine the required business outcome.
- **An accountable service authority owns the service definition and its obligations.** The enterprise determines how that accountability is assigned.
- **The responsible capability authority owns the correctness of its realization assertions.** The enterprise determines which people or groups exercise that responsibility.
- **The designated governance authority determines whether service knowledge is authorized for its intended use.** Validation alone does not confer authorization.

Ownership of a business requirement does not automatically grant authority over technical implementation; technical implementation ownership does not grant authority to redefine the business requirement.

### An Illustrative Top-Down / Bottom-Up Relationship

One possible operating model develops decomposition top-down and realization knowledge bottom-up:

```text
        ARCHITECTURAL DECOMPOSITION
                 top-down
                    |
                    v
             ---------------
                MEET HERE
             ---------------
                    ^
                    |
                 bottom-up
              SME COMPOSITION
```

This is an **illustrative collaboration pattern**, not a required organizational structure. An enterprise may distribute or combine authoring responsibilities differently while preserving the same independently represented assertions and accountability.

**OpenIPERA is opinionated about the structure and integrity of service knowledge, not about the organizational structure responsible for producing it.**

---
## 4. Forward and Reverse Validation

Forward and reverse validation ensure that **every declared service capability and realization dependency is accounted for**. Their purpose is to detect gaps and inconsistencies in independently represented service knowledge, not to require SM-DAG decomposition edges and LC dependencies to mirror one another.

**Forward validation** begins with the SM-DAG and asks whether each capability declared through service decomposition exists and has a companion Lifecycle Card describing its realization requirements.

**Reverse validation** begins with Lifecycle Card requirements and asks whether every declared service dependency resolves to **EITHER** a modeled Service Node or Atomic Node **OR** an explicitly identified external process responsible for satisfying the obligation.

```text
                 FORWARD VALIDATION

       SM-DAG ─────────────────────► Lifecycle Cards
       Every modeled capability       Companion LC exists;
       is accounted for               realization is described


                 REVERSE VALIDATION

       SM-DAG / EXTERNAL PROCESS ◄── Lifecycle Cards
       Every declared requirement     Dependency is declared
       is accounted for
```

The SMV distinguishes these outcomes:

| Observation | SMV finding |
|---|---|
| SM-DAG node has its required companion LC | Modeled capability accounted for |
| SM-DAG node lacks its companion LC | Authoring integrity violation |
| LC dependency resolves to an existing SN or AN | Internal dependency resolved |
| LC dependency explicitly identifies an external process | External obligation identified; fulfillment remains outstanding until evidenced |
| LC dependency resolves to neither | Unresolved dependency; actionable capability gap |

A decomposition relationship and a realization dependency are **different kinds of assertions**. An LC requirement need not appear as a decomposition edge, and the absence of a matching edge is not by itself a discrepancy. Likewise, an external process need not be represented as an internal service node.

### Findings as Service Decomposition Project Candidates

An unresolved LC dependency is more than a validation failure: it identifies a possible gap in the enterprise's modeled service capabilities.

```text
LC: General Purpose Compute
    |
    +-- Compute       RESOLVED
    +-- Network       RESOLVED
    +-- Storage       RESOLVED
    +-- Capability E  UNRESOLVED
                           |
                           v
                      SMV FINDING
                           |
                           v
             SERVICE DECOMPOSITION
                PROJECT CANDIDATE
```

**The SMV MUST identify unresolved service dependencies and report them as actionable capability gaps. Such findings MAY produce Service Decomposition Project candidates**, preserving the originating Lifecycle Card, required capability, and relevant dependency context.

The accountable authority determines disposition: model the missing capability (potentially through a Service Decomposition Project), explicitly designate an external process, or correct the originating assertion. A missing model entry does not prove that an implementation or automation is absent; the capability may exist but remain undocumented.

The SMV does not create or authorize projects, infer missing service knowledge, silently repair authoritative sources, or treat external obligations as already satisfied.

> **A discrepancy is information before it is an error.**

A Service Model can be structurally valid yet contain unresolved realization requirements. The SMV reports the distinction; applicable policy and governance determine whether a finding blocks compilation or production realization.

The resulting feedback loop is:

```text
SERVICE KNOWLEDGE
       |
       v
   SMV FINDINGS
       |
       v
SERVICE DECOMPOSITION PROJECT CANDIDATES
       |
       v
AUTHORIZED MODEL DEVELOPMENT
       |
       v
EXPANDED SERVICE KNOWLEDGE
```

This enables OpenIPERA to identify what the enterprise needs before every capability has been modeled or automated, while preserving explicit accountability for resolving the gap.

---
## 5. Service Model Validation and Compilation Boundaries

The **Service Model Validator (SMV)** and **Compiler** have separate responsibilities. The SMV evaluates the integrity of authoritative service knowledge and reports findings; the Compiler derives a request-specific **Service Object Graph (SOG)** from service knowledge that satisfies applicable validation and policy requirements.

```text
           AUTHORITATIVE SERVICE KNOWLEDGE
        SM-DAG + Lifecycle Cards + Automation Registry
                          |
                          v
                         SMV
                  Validate + Report
                          |
                          v
                VALIDATION RESULTS
              Findings + Model Status
                          |
                          v
                COMPILER + REQUEST
                     CONTEXT
                          |
                          v
                         SOG
          Derived Realization Obligations
```

The software compiler analogy remains useful, provided that validation and compilation are not conflated:

| Software compilation concept | OpenIPERA responsibility |
|---|---|
| Source parsing and syntax checks | SMV: validate schemas and structure |
| Type and identity checks | SMV: validate node/LC semantics and identities |
| Reference resolution | SMV: verify modeled dependencies, external declarations, automation registry entries, and referenced artifacts |
| Semantic analysis | SMV: detect inconsistent relationships and cycles |
| Diagnostics | SMV: report findings, including potential Service Decomposition Project candidates |
| Compilation | Compiler: derive the request-specific SOG |
| Linking | Orchestrator: construct the executable workflow |

The Automation Registry is authoritative for automation identity and implementation resolution. SMV verification of a resolvable reference does **not** establish that the implementation will execute successfully.

### Validation, Authorization, and Compilation

These are distinct decisions:

- **Validation:** The SMV establishes structural and referential integrity and reports discrepancies, unresolved dependencies, and other findings.
- **Authorization:** Applicable governance and policy determine whether the service knowledge may be used for the intended purpose.
- **Compilation:** Given a model satisfying applicable validation and policy requirements and a specific request context, the Compiler derives the SOG representing realization obligations.

Validated but unpublished service knowledge MAY be compiled for testing or proof-of-concept purposes when policy permits. Production realization requires appropriate authorization; successful validation alone does not grant it.

**The SMV MUST be independently callable without invoking the Compiler. Compilation MUST consume service knowledge that has satisfied applicable validation requirements. Neither component may silently modify authoritative service knowledge.**

### Findings and Revalidation

```text
SMV FINDING
     |
     v
ACCOUNTABLE AUTHORITY
Determines Disposition
     |
     +-- Correct Source Knowledge
     |
     +-- Model Missing Capability
     |      (Service Decomposition Project)
     |
     +-- Identify External Process
     |
     v
SMV REVALIDATION
     |
     v
COMPILATION ELIGIBILITY
     |
     v
REQUEST-SPECIFIC SOG
```

The SMV detects and reports malformed structures, unresolved references, cycles, inconsistent assertions, and unresolved automation identities. It MUST NOT silently repair the model or choose a governance disposition. Corrections and additions occur in the authoritative sources, followed by revalidation. Findings may identify Service Decomposition Project candidates, but the SMV does not authorize projects.

> **Source knowledge is authoritative. Validation reports its integrity. Governance determines permissible use. Compilation derives the request-specific obligations.**

---
## 6. Service Object Graph as Compiled Output

The **Service Object Graph (SOG) is the Compiler's derived output**.

It represents the service obligations and dependency relationships required to fulfill a specific request, based on the applicable validated Service Model and request context.

```text
VALIDATED SERVICE MODEL
          +
     REQUEST CONTEXT
          |
          v
       COMPILER
          |
          v
         SOG
   Compiled Output
          |
          v
     ORCHESTRATOR
          |
          v
   EXECUTION WORKFLOW
```

The SOG is **not independently authored architectural truth** and is **not an engine-specific executable workflow**. It describes what must be accomplished; the consuming orchestrator determines how to construct the executable realization.

OpenIPERA produces an identifiable, request-specific SOG with provenance sufficient to relate the compiled output to its source knowledge and request context. **Identifiability does not imply persistence.**

**OpenIPERA does not prescribe or require retention of compiled SOGs.** The consuming organization establishes retention, audit, provenance, and replay requirements, and its orchestration and operational systems implement those requirements. OpenIPERA does not mandate a SOG repository, retention period, or persistence mechanism.

As specified in [Document 06](06_IPERA_DETERMINISTIC_SERVICE_REALIZATION.md), the Compiler **MUST** verify that the service knowledge actually consumed corresponds to the referenced SMV validation identity and evaluated input-version set; it **MUST** reject compilation when consistency cannot be established. Every successfully compiled SOG **MUST** include a provenance manifest identifying the exact component versions used. OpenIPERA is natively instrumented for observability and **MUST** durably accept mandatory compilation provenance events internally before reporting successful SOG publication. These records do not require retention of complete SOGs and are distinct from the broader IPERA Observability pillar's operational assurance responsibilities.

Changes to authoritative service knowledge require revalidation. Subsequent compilations use the applicable validated model version. Previously compiled SOGs and their associated execution evidence, where retained by downstream systems, MUST NOT be silently modified as a consequence of later service-model changes.

---
## 7. Orchestration and Link-Time Realization

The **Orchestrator acts as a linker** between the compiled **Service Object Graph (SOG)** and the execution capabilities required to fulfill its obligations.

The SOG represents request-specific realization obligations, including Atomic Nodes and their automation capability identities, service-completion obligations, dependency relationships, and explicitly identified external processes. It is **not** an executable pipeline.

For example:

```text
AN-A (UUID-A) ─────┐
                   ├──► AN-C (UUID-C)
AN-B (UUID-B) ─────┘
                          |
                          v
                 SERVICE COMPLETE
```

The dependency relationships express what must be satisfied before downstream obligations can be fulfilled. The Orchestrator translates these obligations into an executable workflow appropriate to the consuming environment.

### Registry-Backed Implementation Binding

The responsibilities remain separate:

- **Automation Registry:** Maintains the authoritative mapping from stable automation capability UUIDs to their implementations.
- **SMV:** Verifies that the registry entry and referenced version-controlled artifact exist and are resolvable; this is not a runtime execution guarantee.
- **Orchestrator:** Uses registry-backed binding information to construct executable actions for the selected execution environment, without independently redefining automation capability identity.
- **Execution Capability:** Executes the bound actions and produces state and evidence.

```text
AUTOMATION CAPABILITY UUID
            |
            v
     AUTOMATION REGISTRY
     Authoritative Binding
            |
            v
        ORCHESTRATOR
       Link / Plan Actions
            |
            v
     EXECUTION CAPABILITY
```

An explicitly identified **external process** is also a realization obligation. The Orchestrator MUST account for its required fulfillment and evidence rather than silently treating it as complete merely because no internal automation binding exists. The fulfillment mechanism may involve a person, an external system, or another process, as determined by the consuming organization.

### Architectural Pipeline

```text
SM-DAG + LIFECYCLE CARDS
           |
           v
          SMV
     Validate + Report
           |
           v
        COMPILER
           |
           v
          SOG
           |
           v
      ORCHESTRATOR
        Link / Plan
           |
           v
    EXECUTABLE WORKFLOW
           |
           v
    EXECUTION CAPABILITY
           |
           v
      STATE / EVIDENCE
```

The Service Model does not embed physical implementation details, and the executable workflow does not become authoritative service knowledge. The consuming organization chooses its orchestration and execution technologies and determines applicable SOG, workflow, audit, and replay retention policies. OpenIPERA defines SOG semantics and interfaces; it does not mandate a workflow engine or persistence mechanism.

Two architectural tests follow:

> **If replacing an automation implementation that satisfies the same stable capability contract requires changing the Service Model, the compile/link boundary has been violated.**

> **If a change to service intent requires manually editing the generated executable workflow rather than updating authoritative service knowledge and compiling a new realization, the compile/link boundary has been violated.**

---
## 8. Execution Capability as Runtime

Once the Orchestrator has constructed an executable workflow, the **Execution Capability** performs the assigned actions and reports their outcomes. It does not establish service intent, derive the realization graph, select the obligations to fulfill, or independently authorize service completion.

```text
VALIDATED SERVICE MODEL
          |
          v
       COMPILER
          |
          v
         SOG
          |
          v
     ORCHESTRATOR
          |
          v
   EXECUTABLE WORKFLOW
          |
          v
   EXECUTION CAPABILITY
          |
          v
    STATE / EVIDENCE
```

The responsibility boundaries are:

| Component | Responsibility |
| --- | --- |
| **SMV** | Validate service knowledge and report discrepancies. |
| **Compiler** | Derive the obligations required to fulfill a specific request. |
| **Orchestrator** | Coordinate and construct the executable realization of those obligations. |
| **Execution Capability** | Execute assigned actions and report outcomes and supporting evidence. |

Execution Capabilities are analogous to a **runtime environment**. A workflow may invoke multiple execution mechanisms, including Terraform, Ansible, API invocations, scripts, platform-native automation, or other technologies. These are illustrative, not prescribed; OpenIPERA requires neither a single execution technology nor a single execution platform.

```text
           EXECUTABLE WORKFLOW
                    |
          +---------+---------+
          |         |         |
          v         v         v
      Terraform   Ansible     API
          |         |         |
          +---------+---------+
                    |
                    v
             STATE / EVIDENCE
```

### Execution Success Versus Service Completion

**Execution success does not establish service completion.** An automation action can succeed while the resulting service fails its operational assurance or acceptance requirements.

Execution Capabilities report action outcomes and evidence. Within the broader **IPERA** architecture—not OpenIPERA—the **Observability pillar** supplies the operational evidence necessary to assess whether service obligations have been satisfied, while the **Governance pillar** establishes the policies, controls, acceptance criteria, and decision authority governing that determination. Observability provides evidence; it does not by itself authorize acceptance.

**OpenIPERA represents required service obligations but does not independently assume responsibility for operational assurance, governance decisions, or acceptance of service completion.** The consuming organization and its operational systems determine execution evidence retention and audit policy.

This yields an architectural test:

> **Replacing an execution technology should not require redefining the Service Model, provided the replacement satisfies the same automation capability contract.**

**Execution technologies implement the realization. They do not define the service.**

---
## 9. Governance and Remediation

The **SMV detects, classifies, and reports** discrepancies. It does not determine how findings are resolved and MUST NOT silently modify authoritative service knowledge.

The disposition of an SMV finding is governed by the policies and decision authorities established through the **Governance pillar of IPERA**, not by OpenIPERA or the SMV itself. This responsibility does not prescribe a particular organizational structure, committee, role title, or approval workflow.

Three responsibilities are distinct:

| Responsibility | Architectural boundary |
| --- | --- |
| **Identify and classify findings** | The SMV validates service knowledge and reports discrepancies and their implications. |
| **Establish policy-driven disposition and eligibility** | IPERA Governance establishes which findings require review, remediation, an authorized exception where supported, or prohibit compilation or realization. |
| **Enforce compilation eligibility** | The Compiler and its integration boundary respect applicable validation requirements and governance decisions; blocking findings are not silently bypassed. |

Some conditions violate mandatory structural or semantic requirements of the Service Model. Governance cannot simply declare an invalid graph valid; it can direct correction, authorize an explicitly supported exception, or select a different realization approach. Other findings are informational or subject to deployment-specific policy. **Not every finding necessarily blocks compilation.**

Depending on the applicable requirements and policy, a finding may:

- be reported for information;
- require review by an accountable authority;
- prevent compilation or realization;
- trigger a defined manual or external process; or
- identify a candidate **Service Decomposition Project** when a required capability or dependency is not adequately represented.

The SMV may report a Service Decomposition Project candidate but does **not** initiate or authorize that project. The accountable authority determines whether to extend the model, identify an external process, correct an assertion, or take another permitted action. A knowledge gap is not automatically an error in existing knowledge.

Remediation changes the appropriate authoritative source through its authorized process. The Service Model is then reevaluated by the SMV; findings are not silently repaired during validation or compilation.

> **Evolution Note:** OpenIPERA defines validation findings and the information needed to support governance decisions. The broader IPERA Governance pillar establishes the applicable policies and decision framework. Specific severity classifications, routing mechanisms, approval workflows, and remediation processes remain deployment-dependent and are not prescribed by OpenIPERA.

**Validation establishes what the Service Model asserts and whether it satisfies applicable structural and semantic requirements. Governance determines what the organization is permitted to do in response.**

---