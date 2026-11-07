# IPERA Service Model Compilation Architecture

## 1. Purpose and Foundational Principle

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
## 2. Two Independent Authorities

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
## 3. Forward and Reverse Validation

Because the SM-DAG and Lifecycle Cards are independently authored, the SMV can validate the Service Model in **both directions**.

**Forward validation** begins with architectural intent and asks whether the capabilities identified through SM-DAG decomposition are corroborated by the Lifecycle Cards.

**Reverse validation** begins with SME realization knowledge and asks whether the capabilities identified by the Lifecycle Cards are represented in the architectural model.

```text
                 FORWARD VALIDATION

        SM-DAG ─────────────────────► Lifecycle Cards

     "Architecture says               "Does the SME
      this is needed."                 corroborate it?"


                 REVERSE VALIDATION

        SM-DAG ◄───────────────────── Lifecycle Cards

     "Does architecture               "The SME says
      represent this?"                 this is needed."
```

The comparison produces meaningful model states:

```text
SM-DAG       LC          SMV STATUS
------       --          ----------

 YES         YES         CORROBORATED

 YES          NO         UNCORROBORATED
                         Architectural expectation exists,
                         but is not represented by the SME.

  NO         YES         UNMODELED
                         SME requirement exists,
                         but is not represented in the
                         architectural decomposition.

  NO          NO         No asserted relationship.
```

A discrepancy does **not necessarily mean that either source is invalid**.

For example, an architectural relationship that is not corroborated by the LC might indicate that the capability has not yet been implemented, has not yet been automated, has been omitted from the LC, or is no longer actually required.

Likewise, a requirement asserted by an SME but absent from the SM-DAG might identify a missing architectural relationship, an implementation-specific requirement, or new domain knowledge not yet incorporated into the architecture.

The SMV does not infer which explanation is correct.

```text
            DISCREPANCY
                 │
                 ▼
              ┌─────┐
              │ SMV │
              └─────┘
                 │
                 ▼
       DETECT + CLASSIFY + REPORT
                 │
                 X
                 │
          DO NOT GUESS
```

This distinction is important:

> **A discrepancy is information before it is an error.**

The SMV reports the observed difference between the independently authored sources. The disposition of that difference is determined separately through policy and governance.

This allows IPERA to distinguish **model validity** from **model agreement**.

A Service Model may be syntactically and structurally valid while still containing unresolved disagreement between architectural intent and SME realization knowledge.

Forward and reverse validation therefore turn the overlap between the SM-DAG and Lifecycle Cards into an intentional **reconciliation mechanism**, rather than treating the overlap as redundant information.

---

## 4. The Service Model Validator as Compiler

The **Service Model Validator (SMV)** is the semantic compiler for the IPERA Service Model.

It consumes the independently authored SM-DAG and Lifecycle Cards, evaluates whether those sources form a coherent and realizable Service Model, and derives the Execution DAG required to realize the service.

```text
            AUTHORITATIVE SOURCE

          SM-DAG          Lifecycle Cards
             \                /
              \              /
               ▼            ▼
                ┌──────────┐
                │   SMV    │
                │ COMPILER │
                └──────────┘
                      │
                      ▼
              VALIDATED MODEL
                      │
                      ▼
               EXECUTION DAG
              Compiled Output
```

The compiler analogy is intentional.

A conventional compiler does not merely determine whether source text is syntactically valid. It evaluates references, types, relationships, and semantic consistency before producing executable output.

The SMV performs the equivalent functions for a Service Model:

```text
SOFTWARE COMPILER                 IPERA SMV
-----------------                 ---------

Parse source                      Read SM-DAG + LCs

Syntax checking                   Validate schemas,
                                  identifiers and structure

Type checking                     Validate node and
                                  LC semantics

Symbol resolution                 Resolve referenced services
                                  and automation identities

Semantic analysis                 Evaluate decomposition,
                                  dependencies and model
                                  consistency

Cross-source analysis             Forward + reverse validation
                                  of SM-DAG and LC assertions

Diagnostics                       Report errors, warnings,
                                  discrepancies and evidence

Compilation                       Derive Execution DAG
```

The SMV therefore evaluates several different questions before compilation can complete:

```text
Is the model structurally valid?
            │
            ▼
Do all referenced objects exist?
            │
            ▼
Are node and LC semantics valid?
            │
            ▼
What does forward validation reveal?
            │
            ▼
What does reverse validation reveal?
            │
            ▼
Are required automation identities resolvable?
            │
            ▼
Does policy permit compilation?
            │
            ▼
DERIVE EXECUTION DAG
```

The distinction between the last two stages is important.

The **SMV identifies facts about the model**. It detects malformed structures, unresolved references, cycles, disagreements between authoritative sources, and unresolved automation identities.

The **governance policy determines the disposition** of those findings.

For example, a forward-validation discrepancy might be configured as informational during early model development, require human review in a controlled environment, or prevent compilation in production.

The SMV itself does not redefine architectural truth in order to obtain a successful result.

```text
INPUT
  │
  ▼
SMV
  │
  ├── VALIDATE
  ├── RECONCILE
  ├── RESOLVE
  ├── DIAGNOSE
  │
  └── COMPILE ─────────► Execution DAG
           only when permitted
           by governing policy
```

Most importantly:

> **The SMV MUST NOT silently repair the Service Model.**

If the SM-DAG and Lifecycle Cards disagree, the compiler reports the disagreement. If an automation identity cannot be resolved, it reports the unresolved binding. If the model contains a semantic or structural inconsistency, it reports that inconsistency.

Correction occurs at the **authoritative source**.

The Service Model is then evaluated again.

```text
SMV diagnostic
      │
      ▼
Authoritative source corrected
      │
      ▼
SMV rerun
      │
      ▼
Model validated
      │
      ▼
Execution DAG recompiled
```

This gives IPERA the same fundamental discipline found in software compilation:

> **Source is authoritative. Compiled output is derived. Diagnostics do not rewrite source.**

---

## 5. Execution DAG as Compiled Output

The **Execution DAG is compiled output**.

It represents what must happen, and in what dependency relationship, to realize the validated Service Model.

It is not independently authored and is not persistent architectural truth.

```text
SM-DAG + Lifecycle Cards
        │
        ▼
       SMV
     COMPILE
        │
        ▼
  Execution DAG
COMPILED OUTPUT
```

When architectural intent or SME realization knowledge changes, the Service Model is reevaluated and the Execution DAG is **recompiled**.

The Execution DAG is therefore not the executable pipeline itself. It is the compiled representation from which an executable pipeline can be linked.

---

## 6. Orchestrator as Linker

The **Orchestrator acts as the linker** between the compiled Execution DAG and the automation modules required to realize it.

The Execution DAG identifies the Atomic Nodes that must be realized, their dependency relationships, and the symbolic automation identities associated with them.

For example:

```text
AN-A ─────► AN-C
             ▲
AN-B ────────┘
```

with automation identities:

```text
AN-A → automation_id: UUID-A
AN-B → automation_id: UUID-B
AN-C → automation_id: UUID-C
```

This is a compiled representation of the required realization, but it is not yet an executable pipeline.

The Orchestrator resolves those automation identities to their implementations and **links the required automation modules together according to the compiled Execution DAG**.

```text
              EXECUTION DAG
                   │
                   ▼
              ORCHESTRATOR
                 LINKER
                   │
          ┌────────┼────────┐
          ▼        ▼        ▼
       UUID-A    UUID-B    UUID-C
          │        │        │
          ▼        ▼        ▼
       Module A  Module B  Module C
          \        /
           \      /
            ▼    ▼
            Module C
               │
               ▼
        EXECUTABLE PIPELINE
```

This establishes a deliberate separation between **compile-time validation** and **link-time implementation binding**.

The SMV can determine that an automation identity exists and that the Service Model is realizable without embedding the physical implementation of that capability into the Service Model.

The Orchestrator subsequently resolves that symbolic identity to the implementation that will satisfy it for execution.

```text
SMV
automation_id
     │
     ▼
"Does this capability exist
and can the model reference it?"
     │
     ▼
VALIDATED SYMBOL


ORCHESTRATOR
automation_id
     │
     ▼
"Which implementation satisfies
this capability for execution?"
     │
     ▼
RUNTIME BINDING
```

The resulting architectural pipeline is:

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
```

This separation means that the Service Model does not need to know the physical details of every automation implementation.

Likewise, the executable pipeline does not become the authoritative definition of the service. It is dynamically assembled from compiled service knowledge.

Two architectural tests follow from this separation:

> **If changing an automation implementation requires changing the Service Model, the compile/link boundary has been violated.**

> **If changing service intent requires manually rebuilding the executable pipeline, the compile/link boundary has been violated.**

---

## 7. Execution Capability as Runtime

Once the Orchestrator has linked the automation modules into an executable pipeline, responsibility passes to the **Execution Capability**.

The Execution Capability does not determine service intent, derive dependencies, or decide which automation modules belong in the pipeline. Those decisions have already been made upstream.

Its responsibility is to **execute the linked work**.

```text
SMV
 │
 │ compile
 ▼
Execution DAG
 │
 │ link
 ▼
Orchestrator
 │
 │ produces
 ▼
Executable Pipeline
 │
 │ run
 ▼
EXECUTION CAPABILITY
 │
 ├── Terraform
 ├── Ansible
 ├── API invocation
 ├── Script
 ├── Platform-native automation
 └── Other execution mechanism
 │
 ▼
State / Evidence
```

This preserves another important separation:

```text
SMV
"What must happen?"

Orchestrator
"How are the required automation modules
assembled into runnable work?"

Execution Capability
"Run this work."
```

The Execution Capability is therefore analogous to the **runtime environment**. Different automation technologies may perform different portions of the linked pipeline without becoming authoritative sources of service architecture.

The architecture does not require a single execution technology.

```text
             Executable Pipeline
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
      Terraform    Ansible      API
          │          │          │
          └──────────┼──────────┘
                     ▼
               State / Evidence
```

This provides another architectural test:

> **Replacing an execution technology should not require redefining the Service Model, provided the replacement satisfies the same automation capability contract.**

Execution technologies implement the realization.

They do not define the service.

---

## 8. Governance and Remediation

The SMV **detects, classifies, and reports** discrepancies. It does not determine how those discrepancies are resolved and MUST NOT silently modify either authoritative source.

The disposition of an SMV finding is a matter of **governance and policy**.

Depending upon the deployment and maturity of the environment, a finding may:

- be reported for information,
- require human review,
- prevent compilation or realization, or
- trigger a defined manual process or action.

Resolution occurs against the appropriate authoritative source. The Service Model is then reevaluated by the SMV.

The specific governance mechanisms and policies are intentionally **not prescribed at this stage of the IPERA architecture**.

> **Evolution Note:** This section is intentionally minimal and is expected to expand as IPERA moves from architectural validation and proof-of-concept work into production implementation. In particular, the classification, severity, routing, approval, remediation, and revalidation of SMV findings require further operational evidence before they can be defined as architectural requirements.

---

## 9. Foundational Architecture

The complete IPERA Service Model compilation architecture can therefore be represented as:

```text
Service Architect              Domain / Service SMEs
       │                               │
       │ decomposes                    │ composes
       ▼                               ▼
     SM-DAG                      Lifecycle Cards
          \                         /
           \                       /
            └──────────┬──────────┘
                       ▼
                      SMV
                   COMPILER
                       │
                       ▼
                Execution DAG
            COMPILED REPRESENTATION
                       │
                       ▼
                  Orchestrator
                     LINKER
                       │
                       ▼
               Executable Pipeline
                       │
                       ▼
              Execution Capability
                     RUNTIME
                       │
                       ▼
                State / Evidence
```

The architecture follows a familiar progression:

```text
AUTHOR
  │
  ▼
SOURCE
  │
  ▼
COMPILE
  │
  ▼
LINK
  │
  ▼
EXECUTE
  │
  ▼
EVIDENCE
```

Mapped directly to IPERA:

```text
Service Architect + Domain SMEs
              │
              ▼
     SM-DAG + Lifecycle Cards
              │
              ▼
             SMV
           COMPILE
              │
              ▼
        Execution DAG
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

The foundational principle is therefore:

> **IPERA separates service knowledge from compilation, compilation from linking, and linking from execution.**

Each construct has a distinct responsibility.

The Service Model remains authoritative.

The SMV validates and compiles that knowledge.

The Execution DAG expresses the compiled realization.

The Orchestrator links the required automation modules into an executable pipeline.

The Execution Capability runs that pipeline.

State and evidence record what occurred.

The separation is intentional.