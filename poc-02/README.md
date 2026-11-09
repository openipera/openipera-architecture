# IPERA POC-02: derive and expose the Execution DAG

> **The Service Dependency Model contains persistent dependency knowledge. The
> Execution DAG is derived dynamically for a particular realization. They are not
> the same artifact.**

We provide dependency facts. The system derives the workflow. We do not provide
the workflow. This iteration resolves **Atomic Nodes only**; `S-*` Service Node
semantics remain the next architectural question and are deliberately rejected.

## Run

From the `poc-02/` directory, with Docker Engine and Compose available:

```sh
docker compose up --build
```

One command builds the runtime and starts the external model server and orchestrator.
`--build` also updates an existing POC-01 image. The first run needs the public Python
image; no cloud account is required. Docker Engine on Linux is sufficient; Docker
Desktop is optional. Wait for both services to be healthy (`docker compose ps`).

## Request a realization

The entry point selects that Atomic Node and its recursive prerequisites. It is a
resolver request context, not a new service contract or invented `S-*` behavior.
The old POC-01 `{"service":"A"}` request is replaced by a fully qualified entry point.

### Windows Command Prompt (cmd.exe)

```bat
curl -X POST http://localhost:18081/requests -H "Content-Type: application/json" -d "{\"entry_point\":\"Compute.AN-ValidateVM\"}"
```

The backslashes preserve JSON double quotes for curl. Single quotes do not quote
arguments in cmd.exe.

### PowerShell

Use `Invoke-RestMethod` to avoid `curl` alias and native argument quoting differences:

```powershell
Invoke-RestMethod http://localhost:18081/requests -Method Post -ContentType application/json -Body '{"entry_point":"Compute.AN-ValidateVM"}' | ConvertTo-Json -Depth 30
```

### bash/zsh

```sh
curl -X POST http://localhost:18081/requests -H 'Content-Type: application/json' -d '{"entry_point":"Compute.AN-ValidateVM"}'
```

The response returns `run_id`, `status`, the derived `dag` (nodes, edges, layers),
the Markdown evidence filename, and detailed events. Resolution failures return
HTTP 422 with an explanation; malformed requests return HTTP 400.

## Inspect the derived graph

Open **`evidence/<run_id>-execution-dag.md`** in a Markdown viewer with Mermaid support
or publish that generated file to GitHub for rendering. It contains the request,
exact model hash and snapshot, resolved node set, explicit edges, derived layers,
service-grouped Mermaid diagram, resolution status and execution results.

Reports are generated from actual resolver output, including failure reports for
missing references/cycles. There is no separately authored runtime diagram.
`evidence/<run_id>-model.json` preserves the exact fetched bytes; `.jsonl` stores
ordered execution events. Evidence remains on the host when containers stop.
Generated evidence is ignored by Git; explicitly add a chosen report if sharing it.

The authoritative input is visible at http://localhost:18080/service-model.json.
Each node has exactly `service`, `node`, `dependencies`. JSON is retained from
POC-01; it expresses the supplied YAML model without adding a YAML dependency.
Names are fully qualified as `<Service>.<Node>`.

Input `dependencies` list prerequisites. In the **derived report**, `A -> B` means
**A must complete before B may execute**. Execution layers group simultaneously
eligible nodes; execution within a layer is nondeterministic. Layers are calculated
by the resolver and never stored in the authoritative model.

## Automated conformance and model-only mutations

With the demo running and otherwise idle, Python 3.13+ on the host can run:

```sh
python tests/conformance.py
python -m unittest discover -s tests -v
```

Without host Python, use the runtime image as a separate test client:

```sh
docker compose run --rm --no-deps -v .:/test -w /test orchestrator python tests/conformance.py http://orchestrator:8080
docker compose run --rm --no-deps -v .:/test -w /test orchestrator python -m unittest discover -s tests -v
```

The independent expected graph is **test-only** in `tests/oracle.json`. The runtime
image does not contain tests/oracle or the model. The conformance client compares
exact node sets, edge sets and layers (ignoring order within a layer), and verifies
the generated Mermaid represents the actual graph. Event ordering is supplementary.

The test changes **only `model/service-model.json`**, without restarting the runtime:

1. Adds `Compute.AN-ConfigureMemory`, dependent on DeployVM and required by ValidateVM.
2. Adds a cross-service prerequisite: RegisterDNS also requires ConfigureCPU.
3. Adds a nonexistent `Storage.AN-MissingDisk` reference: rejects before execution.
4. Makes DeployVM require ValidateVM: rejects the cycle before execution.

Each mutation starts from the baseline, checks its expected result, and saves its own
Markdown report. Runtime/artifact/binding fingerprints must stay unchanged. The test
restores exact baseline bytes in `finally`; results go to `evidence/poc02-conformance.json`.
Do not run concurrent requests/tests during these temporary model edits.

## Boundaries and scope

The independent HTTP model container serves a persistent host file. The generic
resolver has no service-specific workflow and no authoritative model mount. The
execution capability uses a separate `artifacts/binding.json` to select the existing
`artifacts/v1/record.py` by SHA-256. Every AN reuses this deterministic demonstration
implementation, so a new valid AN needs no code or binding edit. This is not a general
per-AN production binding scheme. Executable automation never appears in the model.

No major platforms, real infrastructure, reconciliation or production security are
introduced. Stop with `docker compose down`.

See [POC-02 architecture/conformance](docs/POC-02-CONFORMANCE.md) and
[POC-02 actual validation](docs/POC-02-VALIDATION.md).
The original [v0.3 draft](https://github.com/openipera/openipera-architecture/blob/fa0bfcd10de70be07315b4c7dd758d3248f6237a/docs/IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md) remains unchanged.
[POC-01 notes](../poc-01/docs/POC-01-CONFORMANCE.md) and [results](../poc-01/docs/VALIDATION.md) are historical;
their schema and tests are superseded by this iteration and retained in Git history.
