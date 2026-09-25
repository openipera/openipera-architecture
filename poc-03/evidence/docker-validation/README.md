# Docker follow-up validation — 2026-09-25

Docker Desktop became available after the original POC-03 implementation was pushed.
This follow-up closes the previously recorded container-startup verification gap.
Docker Engine version: 29.8.0.

| Check | POC-01 | POC-02 |
|---|---|---|
| Original Compose build and startup | PASS | PASS |
| Model and orchestrator health checks | Healthy | Healthy |
| Unit tests inside Python 3.13 containers | 6 passed | 12 passed |
| Live HTTP conformance from container client | PASS | PASS |
| Test containers and networks removed | PASS | PASS |

Tests ran sequentially in disposable copies of the unchanged POC directories,
using their original Dockerfiles and Compose definitions. Container test clients
mounted each copy at `/test` and invoked the existing unit and conformance suites.
The original repository files and historical evidence were not modified.

The conformance suites performed the same model-only mutations and negative cases
as the earlier host regression. Full conformance JSON, startup/health output, unit
transcripts, service logs and cleanup logs are retained in this directory.

Initial setup attempts are retained under `attempts/`. The first image pull failed
because the configured macOS credential helper returned Keychain Error (100001).
Public anonymous image pulls succeeded using a temporary Docker configuration with
an empty Docker Hub authentication entry and Docker Desktop's CLI plugin directory.
Buildx initially tried writing outside the sandbox; setting `DOCKER_CONFIG` and
`BUILDX_CONFIG` to temporary directories resolved that. The Docker host was explicitly
set to the existing Desktop socket. No saved user Docker settings were edited.

The tested base image and build provenance are in the startup logs. Test-created
containers and networks were removed; Docker's downloaded image/build cache remains.

No runtime code changed. POC-03 has no container deployment or automation execution
requirement; its previously passing 39-test suite was not redundantly rerun here.
This follow-up validates the historical experiments' container behavior.
