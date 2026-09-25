# Derived Execution DAG

## Request

Run ID: `323b3f2bc4d14fd88bcfc11d9b7a20a2`

```json
{"entry_point": "Compute.AN-ValidateVM"}
```

The entry point selects an AN dependency closure; it does not define Service Node semantics.

## Model Snapshot

Source: `http://model:8000/service-model.json`

Content version (SHA-256 of exact source bytes): `7c3637bb3852a162d5c478e19da51f79b4d31196f2398a739941a27be68dab31`

Exact source bytes: `323b3f2bc4d14fd88bcfc11d9b7a20a2-model.json` (when fetched).

```json
{
  "nodes": [
    {
      "service": "Compute",
      "node": "AN-DeployVM",
      "dependencies": [
        "Compute.AN-ValidateVM"
      ]
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
        "Identity.AN-JoinDomain"
      ]
    }
  ]
}

```

## Resolved Nodes

No valid execution graph was produced. See the resolution error below.

## Dependency Edges

`A -> B` means **A must complete before B may execute.**


## Derived Execution Layers

Nodes in a layer may execute concurrently. Layers are derived, not model input.


## Visual Execution DAG

No DAG diagram: resolution did not succeed.

## Resolution Result

- Derived graph valid: no
- All dependencies resolved: yes
- Cycle detected: yes
- Execution completed successfully: no

```text
Dependency cycle (prerequisite -> dependent): Compute.AN-ValidateVM -> Compute.AN-DeployVM -> Compute.AN-ConfigureCPU -> Compute.AN-ValidateVM
```

Cycle path below uses **prerequisite -> dependent** semantics:

```text
Compute.AN-ValidateVM -> Compute.AN-DeployVM -> Compute.AN-ConfigureCPU -> Compute.AN-ValidateVM
```

## Execution Results

```json
[]
```

Ordered detailed events: `323b3f2bc4d14fd88bcfc11d9b7a20a2.jsonl`.
