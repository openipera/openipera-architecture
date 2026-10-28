# OpenIPERA Acronyms and Abbreviations

This is the canonical terminology reference for the OpenIPE architecture repository. The first table contains **IPERA-specific vocabulary**; the second contains **established industry acronyms and external product names** used in the architecture. Entries are alphabetized within each table. Product names that are not acronyms are labeled explicitly.

## IPERA-specific terms

| Acronym / Term | Expansion | Meaning in OpenIPERA |
|---|---|---|
| **AN** | Atomic Node | Terminal service-model node with a governed automation binding; an AN has no further service decomposition. |
| **FC** | Functional Component | Capability and responsibility boundary documented in the functional architecture table; not necessarily its own container. |
| **IPE** | Infrastructure Platform Engineering | Engineering discipline addressed by the architecture. |
| **IPERA** | Infrastructure Platform Engineering Reference Architecture | The architectural model and principles underlying OpenIPERA. |
| **LC** | Lifecycle Card | Versioned metadata associated with a modeled service node; expresses obligations, governance, provenance, and applicable automation references. |
| **OpenIPE** | Open Infrastructure Platform Engineering | Project and repository umbrella for the open architecture effort. |
| **OpenIPERA** | Open Infrastructure Platform Engineering Reference Architecture | Open implementation of the IPERA concepts, including model validation and SOG compilation; **not** an execution engine. |
| **SM-DAG** | Service Model Directed Acyclic Graph | Authoritative service-decomposition/dependency graph; source input to validation and compilation, **not** an executable workflow. |
| **SMV** | Service Model Validator | Independently callable **validation subsystem of the OpenIPERA compiler**; validates bounded modules or request dependency closures. |
| **SN** | Service Node | Nonterminal modeled service that decomposes into subordinate service or atomic nodes. |
| **SOG** | Service Object Graph | Compiler-generated graph representing operations, dependencies, and milestones necessary to realize a requested service; consumed by external orchestration. |
| **SOM** | Service Object Model | Authoritative modeled service objects and relationships accessed through a replaceable SOM adapter; **not** the compiled SOG. |

## Industry acronyms and product names

| Acronym / Term | Expansion | Meaning in OpenIPERA |
|---|---|---|
| **AAP** | Ansible Automation Platform | External automation execution/control-plane capability; not assumed to be the DAG orchestrator. |
| **API** | Application Programming Interface | Programmatic contract used for northbound requests and southbound integration. |
| **Argo** | *Product name; not an acronym* | Candidate external Kubernetes-native workflow/orchestration engine. |
| **CI/CD** | Continuous Integration / Continuous Delivery (or Deployment) | External pipeline capabilities for testing, packaging, and promoting software and automation artifacts. |
| **CLI** | Command-Line Interface | Optional client for invoking compiler validation and compilation operations. |
| **CMDB** | Configuration Management Database | Enterprise configuration-data system; may be integrated through ServiceNow or another authority. |
| **CSDM** | Common Service Data Model | ServiceNow model for organizing service and configuration relationships; potential source for SOM integration. |
| **DAG** | Directed Acyclic Graph | Graph with directed dependencies and no cycles; foundational to the service model and compiled operational dependencies. |
| **etcd** | *Project name; not an acronym* | Key-value store proposed as a demonstration SOM authority; separate from any Kubernetes control-plane datastore. |
| **Git** | *Project name; not an acronym* | Version-control system used for model-related and automation artifacts. |
| **IaC** | Infrastructure as Code | Declarative or programmatic infrastructure automation invoked through external execution capabilities. |
| **ITSM** | IT Service Management | Enterprise service/change/incident management domain, including integrations with ServiceNow. |
| **K3s** | *Product name; not an acronym* | Lightweight Kubernetes distribution selected as the reference OpenIPERA runtime. |
| **K8s** | Kubernetes (numeronym) | Mandatory orchestration substrate for the OpenIPERA application; existing OpenShift is an alternative to K3s. |
| **OCP** | OpenShift Container Platform | Red Hat Kubernetes distribution targeted for native OpenIPERA deployment. |
| **OPA** | Open Policy Agent | Potential external policy-decision capability referenced by governance obligations. |
| **OVA** | Open Virtualization Appliance | VMware-compatible packaging format considered for a K3s-based VM appliance. |
| **PoC / POC** | Proof of Concept | Incremental architecture demonstration and implementation milestone. |
| **PVC** | PersistentVolumeClaim | Kubernetes request for persistent storage, such as the demonstration etcd data volume. |
| **REST** | Representational State Transfer | Candidate style for the versioned OpenIPERA API. |
| **SOW** | Statement of Work | Delivery document; not an OpenIPERA runtime component. |
| **UUID** | Universally Unique Identifier | Stable identifier used for automation registry bindings and model integrity checks. |
| **VCS** | Version Control System | External authority for versioned artifacts and provenance, commonly Git-based. |
| **VM** | Virtual Machine | Possible host for a K3s appliance; OpenIPERA still runs inside Kubernetes. |
| **vSphere** | *Product name; not an acronym* | VMware virtualization platform; a possible OVA deployment target, not an OpenIPERA prerequisite. |

## Terms that must not be conflated

| Term | Defines or represents | Does **not** represent |
|---|---|---|
| **SM-DAG** | The modeled service structure and its dependencies | An executable orchestration workflow |
| **SOM** | The authoritative service-model objects and relationships | The compiled operations graph |
| **SOG** | The operational dependency graph compiled for a particular request | The authoritative service model or an executed workflow |
| **SMV** | Compiler-internal validation of a bounded model or request | A separately deployed execution or reconciliation service |
| **SN** | A decomposable service node | A terminal automation binding |
| **AN** | A terminal service node with an automation binding | An independently authored end-to-end workflow |
| **LC** | A node's lifecycle metadata and governed obligations | A workflow engine or operational state reconciler |

**Terminology rule:** Validation may reconcile *model assertions* for consistency; OpenIPERA does **not** reconcile desired versus observed operational infrastructure state.
