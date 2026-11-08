# Repository reorganization record

Reorganization validated on 2026-09-25. This is a preservation and path-maintenance
change, not a revision of either experiment's architecture.

## Original top-level structure

```text
.dockerignore
.gitattributes
.gitignore
Dockerfile
IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md
IPERA_Minimum_Viable_Service_Model.md
README.md
artifacts/
docker-compose.yml
docs/
evidence/
model/
runtime/
tests/
```

The executable root tree was POC-02. POC-01's implementation was retained only in
Git history, with its historical conformance and validation notes still under `docs/`.

## Resulting top-level structure

```text
.gitattributes
README.md
docs/
  IPERA_FUNCTIONAL_ARCHITECTURE_REQUIREMENTS.md
  IPERA_Minimum_Viable_Service_Model.md
  REPOSITORY_REORGANIZATION.md
poc-01/
  .dockerignore
  .gitignore
  Dockerfile
  README.md
  artifacts/
  docker-compose.yml
  docs/
  evidence/
  model/
  runtime/
  tests/
poc-02/
  .dockerignore
  .gitignore
  Dockerfile
  README.md
  artifacts/
  docker-compose.yml
  docs/
  evidence/
  model/
  runtime/
  tests/
```

No POC-03 implementation or empty placeholder directories were created. No shared
framework was introduced. Architecture document filenames and contents are preserved.

## Assignment and provenance

- **POC-01:** Restored `README.md`, `model/`, `runtime/`, `tests/`, `artifacts/`,
  `evidence/.gitkeep`, `Dockerfile`, `docker-compose.yml`, `.dockerignore`, and
  `.gitignore` from commit `7728802`, the final POC-01 snapshot before the POC-02
  implementation commit `925c7fd`. Moved the latest historical notes
  `docs/POC-01-CONFORMANCE.md` and `docs/VALIDATION.md` from `d61773a` into
  `poc-01/docs/`, retaining their later historical annotations.
- **POC-02:** Moved the current executable root tree from `d61773a` into `poc-02/`:
  `model/`, `runtime/`, `tests/`, `artifacts/`, `evidence/`, `README.md`, `Dockerfile`,
  `docker-compose.yml`, `.dockerignore`, and `.gitignore`. Moved
  `docs/POC-02-CONFORMANCE.md` and `docs/POC-02-VALIDATION.md` into `poc-02/docs/`.
- **Repository:** Moved the two architecture documents into `docs/`, retained
  `.gitattributes` at the root, and added the repository overview and this record.

Existing files were moved with Git where practical. POC-01 restoration uses the
original committed bytes; no historical commits were rewritten or branches deleted.

## References and configuration

README startup instructions now specify the appropriate POC directory. Repaired the
POC-02 README's architecture and POC-01 links, the POC-01 notes' links to POC-02,
and the POC-01 architecture baseline link. Other historical wording is preserved,
including descriptions of the then-active root implementation and then-uncommitted
files; those statements describe the original checkout, not the reorganized layout.

Dockerfiles, Compose files, test paths, and ignore files require no content changes:
each experiment keeps the relative layout expected by its original implementation.
Both Compose definitions still use ports 18080 and 18081; the root README directs
users to stop one experiment before starting the other. This preserves runtime behavior.

## Verification

| Check | Result |
|---|---|
| POC-01 unit tests | All 6 passed on Python 3.14.2. |
| POC-02 unit tests | All 12 passed on Python 3.14.2. |
| POC-01 live HTTP conformance | PASS: baseline and model-only E change; unchanged runtime/artifact fingerprints; exact baseline restored. |
| POC-02 live HTTP conformance | PASS: baseline, new AN, cross-service dependency, missing reference, and cycle; unchanged runtime/artifact/binding fingerprints; exact baseline restored. |
| Compose configuration | `docker compose config --quiet` passed independently in both POC directories. |
| Preservation | All 12 POC-01 and 30 POC-02 implementation/configuration/evidence files checked byte-for-byte against their source commits; both architecture documents also byte-identical. |
| Documentation links | Relative Markdown file links checked after relocation. |

Live HTTP checks used isolated copies of the reorganized POC directories, a separate
HTTP model process, and the unchanged server and conformance client. They exercised
real subprocess automation on the host. Fresh generated results were kept outside
the repository, so they cannot be confused with historical evidence.

Docker container execution was not rerun: the installed Docker client could not
connect to its stopped/unavailable engine. Host checks do not establish container
startup success; the original Docker validation records remain available per POC.

## Evidence gaps, ambiguities, and preservation limits

All 15 committed POC-02 run artifacts (eight Markdown reports and seven model
snapshots), plus its `.gitkeep`, are preserved unchanged under `poc-02/evidence/`.
The report for malformed JSON intentionally has no model snapshot.

POC-01's original `conformance.json` and JSONL runs were documented as Git-ignored
local files and are absent from the repository history inspected. POC-02's original
`poc02-conformance.json` and JSONL runs are likewise not tracked. Their historical
validation notes are retained, but those missing files cannot be recovered from this
checkout and have not been invented or replaced by fresh results.

No tracked artifact has unresolved POC ownership. `docs/VALIDATION.md` is explicitly
titled POC-01 validation; committed run evidence is identified as POC-02 by its
reports and validation references. No tracked file required a behavior change to
preserve it. No POC was retrofitted to the current service model, and POC-03 remains
an unimplemented future experiment.
