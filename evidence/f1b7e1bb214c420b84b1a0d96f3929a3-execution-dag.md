# Derived Execution DAG

## Request

Run ID: `f1b7e1bb214c420b84b1a0d96f3929a3`

```json
{"entry_point": "Compute.AN-ValidateVM"}
```

The entry point selects an AN dependency closure; it does not define Service Node semantics.

## Model Snapshot

Source: `http://model:8000/service-model.json`

Content version (SHA-256 of exact source bytes): `b78f08fca2d455dfccfdeda651d70d847ab0d4c53e393e66cb32f7d886e65e07`

Exact source bytes: `f1b7e1bb214c420b84b1a0d96f3929a3-model.json` (when fetched).

```json
{
  "nodes": [
    {
      "service": "Compute",
      "node": "AN-DeployVM",
      "dependencies": []
    },
    {
      "service": "Compute",
      "node": "AN-ConfigureCPU",
      "dependencies": [
        "Compute.AN-DeployVM"
      ]
    },
    {
      "service": "Storage",
      "node": "AN-ProvisionDisk",
      "dependencies": []
    },
    {
      "service": "Compute",
      "node": "AN-ConfigureDisk",
      "dependencies": [
        "Compute.AN-DeployVM",
        "Storage.AN-ProvisionDisk"
      ]
    },
    {
      "service": "Network",
      "node": "AN-AllocateIP",
      "dependencies": []
    },
    {
      "service": "Network",
      "node": "AN-RegisterDNS",
      "dependencies": [
        "Network.AN-AllocateIP"
      ]
    },
    {
      "service": "Compute",
      "node": "AN-ConfigureIP",
      "dependencies": [
        "Compute.AN-DeployVM",
        "Network.AN-RegisterDNS"
      ]
    },
    {
      "service": "Identity",
      "node": "AN-JoinDomain",
      "dependencies": [
        "Compute.AN-DeployVM",
        "Network.AN-RegisterDNS"
      ]
    },
    {
      "service": "Compute",
      "node": "AN-ValidateVM",
      "dependencies": [
        "Compute.AN-ConfigureCPU",
        "Compute.AN-ConfigureDisk",
        "Compute.AN-ConfigureIP",
        "Identity.AN-JoinDomain",
        "Compute.AN-ConfigureMemory"
      ]
    },
    {
      "service": "Compute",
      "node": "AN-ConfigureMemory",
      "dependencies": [
        "Compute.AN-DeployVM"
      ]
    }
  ]
}

```

## Resolved Nodes

- `Compute.AN-ConfigureCPU`
- `Compute.AN-ConfigureDisk`
- `Compute.AN-ConfigureIP`
- `Compute.AN-ConfigureMemory`
- `Compute.AN-DeployVM`
- `Compute.AN-ValidateVM`
- `Identity.AN-JoinDomain`
- `Network.AN-AllocateIP`
- `Network.AN-RegisterDNS`
- `Storage.AN-ProvisionDisk`

## Dependency Edges

`A -> B` means **A must complete before B may execute.**

```text
Compute.AN-ConfigureCPU -> Compute.AN-ValidateVM
Compute.AN-ConfigureDisk -> Compute.AN-ValidateVM
Compute.AN-ConfigureIP -> Compute.AN-ValidateVM
Compute.AN-ConfigureMemory -> Compute.AN-ValidateVM
Compute.AN-DeployVM -> Compute.AN-ConfigureCPU
Compute.AN-DeployVM -> Compute.AN-ConfigureDisk
Compute.AN-DeployVM -> Compute.AN-ConfigureIP
Compute.AN-DeployVM -> Compute.AN-ConfigureMemory
Compute.AN-DeployVM -> Identity.AN-JoinDomain
Identity.AN-JoinDomain -> Compute.AN-ValidateVM
Network.AN-AllocateIP -> Network.AN-RegisterDNS
Network.AN-RegisterDNS -> Compute.AN-ConfigureIP
Network.AN-RegisterDNS -> Identity.AN-JoinDomain
Storage.AN-ProvisionDisk -> Compute.AN-ConfigureDisk
```

## Derived Execution Layers

Nodes in a layer may execute concurrently. Layers are derived, not model input.

```text
Layer 0
  Compute.AN-DeployVM
  Network.AN-AllocateIP
  Storage.AN-ProvisionDisk

Layer 1
  Compute.AN-ConfigureCPU
  Compute.AN-ConfigureDisk
  Compute.AN-ConfigureMemory
  Network.AN-RegisterDNS

Layer 2
  Compute.AN-ConfigureIP
  Identity.AN-JoinDomain

Layer 3
  Compute.AN-ValidateVM
```

## Visual Execution DAG

```mermaid
flowchart LR
    subgraph s0["Compute"]
        n0["Compute.AN-ConfigureCPU"]
        n1["Compute.AN-ConfigureDisk"]
        n2["Compute.AN-ConfigureIP"]
        n3["Compute.AN-ConfigureMemory"]
        n4["Compute.AN-DeployVM"]
        n5["Compute.AN-ValidateVM"]
    end
    subgraph s1["Identity"]
        n6["Identity.AN-JoinDomain"]
    end
    subgraph s2["Network"]
        n7["Network.AN-AllocateIP"]
        n8["Network.AN-RegisterDNS"]
    end
    subgraph s3["Storage"]
        n9["Storage.AN-ProvisionDisk"]
    end
    n0 --> n5
    n1 --> n5
    n2 --> n5
    n3 --> n5
    n4 --> n0
    n4 --> n1
    n4 --> n2
    n4 --> n3
    n4 --> n6
    n6 --> n5
    n7 --> n8
    n8 --> n2
    n8 --> n6
    n9 --> n1
```

## Resolution Result

- Derived graph valid: yes
- All dependencies resolved: yes
- Cycle detected: no
- Execution completed successfully: yes


## Execution Results

```json
[
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 7,
    "time_ns": 1790307439493398925,
    "event": "action_finished",
    "node": "Compute.AN-DeployVM",
    "returncode": 0,
    "stdout": "{\"action\": \"Compute.AN-DeployVM\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 8,
    "time_ns": 1790307439495126250,
    "event": "action_finished",
    "node": "Network.AN-AllocateIP",
    "returncode": 0,
    "stdout": "{\"action\": \"Network.AN-AllocateIP\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 9,
    "time_ns": 1790307439499880689,
    "event": "action_finished",
    "node": "Storage.AN-ProvisionDisk",
    "returncode": 0,
    "stdout": "{\"action\": \"Storage.AN-ProvisionDisk\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 14,
    "time_ns": 1790307439560277768,
    "event": "action_finished",
    "node": "Compute.AN-ConfigureCPU",
    "returncode": 0,
    "stdout": "{\"action\": \"Compute.AN-ConfigureCPU\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 15,
    "time_ns": 1790307439561572606,
    "event": "action_finished",
    "node": "Compute.AN-ConfigureDisk",
    "returncode": 0,
    "stdout": "{\"action\": \"Compute.AN-ConfigureDisk\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 16,
    "time_ns": 1790307439564868881,
    "event": "action_finished",
    "node": "Compute.AN-ConfigureMemory",
    "returncode": 0,
    "stdout": "{\"action\": \"Compute.AN-ConfigureMemory\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 17,
    "time_ns": 1790307439566211593,
    "event": "action_finished",
    "node": "Network.AN-RegisterDNS",
    "returncode": 0,
    "stdout": "{\"action\": \"Network.AN-RegisterDNS\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 20,
    "time_ns": 1790307439630810471,
    "event": "action_finished",
    "node": "Compute.AN-ConfigureIP",
    "returncode": 0,
    "stdout": "{\"action\": \"Compute.AN-ConfigureIP\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 21,
    "time_ns": 1790307439632031431,
    "event": "action_finished",
    "node": "Identity.AN-JoinDomain",
    "returncode": 0,
    "stdout": "{\"action\": \"Identity.AN-JoinDomain\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  },
  {
    "run_id": "f1b7e1bb214c420b84b1a0d96f3929a3",
    "sequence": 23,
    "time_ns": 1790307439699764965,
    "event": "action_finished",
    "node": "Compute.AN-ValidateVM",
    "returncode": 0,
    "stdout": "{\"action\": \"Compute.AN-ValidateVM\", \"result\": \"ok\"}\n",
    "stderr": "",
    "artifact_sha256": "b999ac0052b75baf78bcf0b5c594dd76b59d036c4b573d5c5aacd3299eebea7a"
  }
]
```

Ordered detailed events: `f1b7e1bb214c420b84b1a0d96f3929a3.jsonl`.
