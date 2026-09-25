# SMV: VALID — compiled Execution DAG

## Forward and reverse comparison

| Service | Target | Architecture | SME | Status |
|---|---|---|---|---|
| boot | vm | NO | YES | UNMODELED |
| cmdb | register-ci | YES | NO | UNCORROBORATED |
| compute | cpu | YES | NO | UNCORROBORATED |
| compute | memory | YES | NO | UNCORROBORATED |
| compute | vm | YES | NO | UNCORROBORATED |
| cyberark | domain | NO | YES | UNMODELED |
| domain | validate | NO | YES | UNMODELED |
| gpc | allocate-ip | YES | NO | UNCORROBORATED |
| gpc | boot | YES | NO | UNCORROBORATED |
| gpc | cmdb | YES | NO | UNCORROBORATED |
| gpc | compute | YES | YES | CORROBORATED |
| gpc | cpu | YES | NO | UNCORROBORATED |
| gpc | cyberark | YES | NO | UNCORROBORATED |
| gpc | domain | YES | NO | UNCORROBORATED |
| gpc | identity | YES | NO | UNCORROBORATED |
| gpc | memory | YES | NO | UNCORROBORATED |
| gpc | network | YES | NO | UNCORROBORATED |
| gpc | register-ci | YES | NO | UNCORROBORATED |
| gpc | register-dns | YES | NO | UNCORROBORATED |
| gpc | security | YES | NO | UNCORROBORATED |
| gpc | storage | YES | YES | CORROBORATED |
| gpc | validate | YES | NO | UNCORROBORATED |
| gpc | vm | YES | NO | UNCORROBORATED |
| identity | domain | YES | NO | UNCORROBORATED |
| network | allocate-ip | YES | NO | UNCORROBORATED |
| network | register-dns | YES | NO | UNCORROBORATED |
| register-ci | validate | NO | YES | UNMODELED |
| register-dns | allocate-ip | NO | YES | UNMODELED |
| security | cyberark | YES | NO | UNCORROBORATED |
| validate | boot | NO | YES | UNMODELED |
| vm | cpu | NO | YES | UNMODELED |
| vm | memory | NO | YES | UNMODELED |
| vm | network | NO | YES | UNMODELED |
| vm | storage | NO | YES | UNMODELED |

Service vertices are completion milestones; Atomic Nodes are actions. No automation was executed.

```mermaid
flowchart TD
  n0["Allocate IP / allocate-ip (service_complete)"]
  n1["Power On VM / an-boot (action)"]
  n2["Configure CPU / an-cpu (action)"]
  n3["Onboard Account / an-cyberark (action)"]
  n4["Deploy VM / an-deploy-vm (action)"]
  n5["Provision Disk / an-disk (action)"]
  n6["Register DNS / an-dns (action)"]
  n7["Join Domain / an-domain (action)"]
  n8["Allocate IP / an-ip (action)"]
  n9["Configure Memory / an-memory (action)"]
  n10["Create CI / an-register-ci (action)"]
  n11["Run VM Validation / an-validate (action)"]
  n12["Boot VM / boot (service_complete)"]
  n13["CMDB / cmdb (service_complete)"]
  n14["Compute / compute (service_complete)"]
  n15["CPU / cpu (service_complete)"]
  n16["Register with CyberArk / cyberark (service_complete)"]
  n17["Register with Domain / domain (service_complete)"]
  n18["General Purpose Compute / gpc (service_complete)"]
  n19["Identity / identity (service_complete)"]
  n20["Memory / memory (service_complete)"]
  n21["Network / network (service_complete)"]
  n22["Register CI in CMDB / register-ci (service_complete)"]
  n23["Register DNS / register-dns (service_complete)"]
  n24["Security / security (service_complete)"]
  n25["Storage / storage (service_complete)"]
  n26["Validate VM / validate (service_complete)"]
  n27["VM / vm (service_complete)"]
  n0 --> n6
  n0 --> n21
  n0 --> n23
  n1 --> n12
  n2 --> n15
  n3 --> n16
  n4 --> n27
  n5 --> n25
  n6 --> n23
  n7 --> n17
  n8 --> n0
  n9 --> n20
  n10 --> n22
  n11 --> n26
  n12 --> n11
  n12 --> n18
  n12 --> n26
  n13 --> n18
  n14 --> n18
  n15 --> n4
  n15 --> n14
  n15 --> n27
  n16 --> n24
  n17 --> n3
  n17 --> n16
  n17 --> n19
  n19 --> n18
  n20 --> n4
  n20 --> n14
  n20 --> n27
  n21 --> n4
  n21 --> n18
  n21 --> n27
  n22 --> n13
  n23 --> n21
  n24 --> n18
  n25 --> n4
  n25 --> n18
  n25 --> n27
  n26 --> n7
  n26 --> n10
  n26 --> n17
  n26 --> n18
  n26 --> n22
  n27 --> n1
  n27 --> n12
  n27 --> n14
```

## Derived parallel layers

1. an-cpu, an-disk, an-ip, an-memory
2. allocate-ip, cpu, memory, storage
3. an-dns
4. register-dns
5. network
6. an-deploy-vm
7. vm
8. an-boot, compute
9. boot
10. an-validate
11. validate
12. an-domain, an-register-ci
13. domain, register-ci
14. an-cyberark, cmdb, identity
15. cyberark
16. security
17. gpc

## Validated automation symbols (linking deferred)

- an-boot: `54af18cc-31eb-5c4a-804d-d68a1caea269` (Power On VM)
- an-cpu: `d2bf2f4e-8b53-5942-ade4-75796bc252c9` (Configure CPU)
- an-cyberark: `ac242887-89b7-55b0-b1d8-500c57748d16` (Onboard Account)
- an-deploy-vm: `39c45414-d3c4-5596-964d-3f7821a645e9` (Deploy VM)
- an-disk: `2124882e-62b0-5f25-9753-ec915164a1c5` (Provision Disk)
- an-dns: `2873ad87-1d8d-5f6c-b130-df639ed139a0` (Register DNS)
- an-domain: `ecf32e26-53b4-58ad-bff4-d070a50846ec` (Join Domain)
- an-ip: `271817c4-99f6-5b24-9da0-0db3e508f6a5` (Allocate IP)
- an-memory: `c348ea21-fa84-5209-b3e0-34241c2b652e` (Configure Memory)
- an-register-ci: `f15db5bf-ddea-566f-9f5c-2ac081794a5f` (Create CI)
- an-validate: `708d3532-08e4-5db8-aced-e1b5ef647006` (Run VM Validation)
