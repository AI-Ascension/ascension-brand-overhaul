# W03 independent review: frozen W01 source baseline and brand/copy scope

This review checks the W01 source baseline and brand/copy outputs carried into
the exact integrated tree at `c9b3369cb182fce81c7b6c9d550ad6b95455a64d`.
The seven W01 output files were introduced by `f376e6914ce6a89804dc24d0f76801c699841b88`
and have no content changes between those heads. The reviewed files are
`execution/source-snapshot.json`, `execution/capabilities.json`,
`docs/BASELINE_AUDIT.md`, `brand/BRAND_GUIDE.md`, `brand/copy.json`,
`docs/NAME_COLLISION_REVIEW.md`, and `migration/repository-plan.json`.
`execution/requirements-status.json` and the package integrity records were
also checked as acceptance inputs. No source repository, remote metadata,
host, deployment, migration, publication, mail, or artwork operation was
performed by this review.

## Verification and boundary

- The seven W01 files match the top-level package `MANIFEST.json` byte counts
  and SHA-256 values. The 13 rows in `data/repository-map.json`,
  `migration/repository-plan.json`, and `brand/copy.json` have matching
  source/target/action keys. The source snapshot records 13 repositories and
  36 selected source documents; the capability envelope contains 17 unique
  capability IDs.
- JSON parsing succeeded for the W01 registries. Loading
  `execution/capabilities.json` through `publisher.capabilities.load_capability_registry`
  returned 17 validated records and the `ai-ascension.capabilities.v1` metadata
  envelope. `git diff --check` was clean for the W01 diff.
- `brand/copy.json` retains the requested AI Ascension / Ascension / The Climb
  hierarchy, report-only and independent-project disclosures, the first-win
  season framing, and explicit forbidden claims. The migration plan remains
  `dry_run_prepared` with `apply_performed: false`, no rename authorization,
  and runtime package, route, ABI, loader, environment, evidence, and PHP
  subscription identities preserved. These checks support the naming/copy
  requirements as source data; they do not authorize a remote rename or
  publication.
- On the exact W01 pre-descendant archive at `/tmp/sts2-w01-0e-DLuXH1`,
  `python3 scripts/validate_package.py` passed and
  `python3 -m unittest discover -s tests` passed all 170 tests.
- On the exact integrated `c9b3369` archive at `/tmp/sts2-w01-review-ruuKhj`,
  the package validator reports eight errors: five unlisted files
  (`execution/reviews/W07-L-W04-migration-repair-rereview.md`,
  `execution/reviews/W07-L-final-publication-measurement-capability-rereview.md`,
  `execution/w04-repair-implementation.json`,
  `tests/test_migration_residual_repairs.py`, and
  `tests/test_migration_review_repairs.py`) and three checksum/byte-size
  mismatches (`docs/MIGRATION_OPERATIONS.md`,
  `migration/tooling/github_migration.py`, and
  `tests/test_migration_tooling.py`). The integrated unittest discovery ran
  188 tests; its only two failures were the package-structure and local-
  dependency tests reporting those same eight errors.
- `execution/capabilities.json` and `execution/source-snapshot.json` both
  record that native W01 delegation and independent review were unavailable.
  The following findings are therefore an independent static/provenance
  review, not a native runtime rerun or an approval of the W01 acceptance
  state.

## Findings

### W01-SRC-01 — Runtime-v1 capability is not reproducibly bound to the pinned source (high/blocking)

`execution/capabilities.json:63-76` assigns
`CAP-MOD-RUNTIME-V1` source revision `8b71150895ea95c0625afc1389bb08e4034d9350`
and links the runtime-v1 host report at that revision. The linked report says
its source state was target HEAD `97f3a2068452d2c1616c531a7dfad51fbd484cac`
plus uncommitted runtime-v1 changes in an isolated worktree. Neither that
worktree state nor a patch/byte digest appears in
`execution/source-snapshot.json:227-263` or its selected-document inventory.
The snapshot does record the game-mod default head and the separate forced-
fixture report, but that is not a reproducible source binding for this
runtime-v1 result.

Keep this record maintainer-reported and report-only until the actual runtime
patch/package bytes and their digest are recorded as source evidence, or split
the source description from the dated host report and label the uncommitted
state explicitly. Do not present the capability as a run reproducible from
game-mod `8b711508` alone.

### W01-SRC-02 — Watchdog default-branch claim points at the draft PR head (medium)

`execution/capabilities.json:207-220` says that the watchdog **default branch**
documents the boundary, but uses PR URL `ascension-watchdog/pull/2` and source
revision `55480e05e983cade3f018da37634942cdbe6eac7`. The source snapshot
identifies the bootstrap default head as
`dc2d20badb9e86c12067316b92d6c8289b2e6995` at
`execution/source-snapshot.json:242-244`, while its PR row records
`55480e05` as the draft head at `:302-318`. The corresponding copy and
migration rows correctly use the bootstrap head, so the records disagree
within the same W01 package.

Separate the default-branch source record from the PR proposal, or record both
revisions and state which one supports each sentence. Preserve the existing
failed-check and no-live-service boundary.

### W01-SRC-03 — Canonical-domain capability combines source and host evidence (medium)

`execution/capabilities.json:255-268` labels
`CAP-CANONICAL-DOMAIN` as `source_derived` and links the repository README,
while its claim and `tested_configuration` assert the live HTTP response,
PHP version, and subscription behavior. Those observations actually reside in
the host record at `execution/source-snapshot.json:345-370` and are summarized
in `docs/BASELINE_AUDIT.md:85-96`. The notes correctly preserve the injected
monitoring and no-mail limitations, but the evidence type and source URL do
not identify the host observation as the support for the mixed claim.

Split the source-level and host-level capabilities, or add a standardized host
evidence reference and a mixed evidence type. Keep the current HTTP, POST, mail,
branch, and hosting-injection limitations visible.

### W01-SRC-04 — Audit claims a document inventory that the snapshot does not contain (medium)

`docs/BASELINE_AUDIT.md:49-53` says that `AGENTS.md`, architecture,
coding-standards, policy, layout, product, and other evidence documents were
inspected and that full document blob hashes are in the snapshot. The
`source_documents` inventory at `execution/source-snapshot.json:227-263`
contains selected README, product, policy, workflow, and evidence paths, but
does not contain the named AGENTS, architecture, coding-standards, layout, or
all workflow/policy files. The workflow summary at `:265-283` records paths and
branches, not the missing document bytes or hashes.

Either add every document used for a current claim to the source inventory with
its exact blob identity, or narrow the audit language to the files actually
recorded. This is a replayability gap in the source inspection record.

### W01-COPY-01 — Mixed season evidence is labeled as one native run (low/medium)

`brand/copy.json:36-48` combines the Windows and Linux maintainer-reported
defeat records with the forced terminal Victory fixture, but marks the season
`evidence_kind` as `native_run` and supplies only the harness revision at
`:41`. The fixture has a different game-mod revision and an
`evidence_kind` of `forced_fixture` in `execution/capabilities.json:79-92`.
Several message records likewise cite multiple `source_ids` while carrying one
primary `source_revision`, for example `brand/copy.json:50-66`.

Use an explicit mixed/source-revisions representation or split the records so
renderers cannot infer that the fixture shares the campaign source or that one
revision supports every message. The actual copy is careful not to call the
fixture a model-played win, and that wording should remain.

### W01-PKG-01 — Baseline audit records the wrong package result (medium)

`docs/BASELINE_AUDIT.md:127-129` says the W01 helper suite reported a
pre-existing `.gitignore` checksum failure. Re-running against the exact W01
archive shows the package validator passed, and the `.gitignore` manifest hash
matches. The exact integrated `c9b3369` archive instead fails on the eight
later W04/W07 inventory and checksum entries listed above. This makes the
current reproduction note misleading and obscures which revision owns the
failure.

Correct the reproduction note to distinguish the passing W01 result from the
later integrated-package failure, then refresh the integrated manifest and
checksums before treating the package as valid.

### W01-ACC-01 — W01 acceptance evidence and independent review remain incomplete (blocking acceptance)

`execution/requirements-status.json:6-111` leaves REQ-001 through REQ-006
`in_progress`; each has empty `implementation_paths` and
`verification_records`, a null `independent_reviewer`, and an expected
`execution/evidence/REQ-001.json` through `REQ-006.json` path. None of those
six evidence files exists in the reviewed archive. The capability and source
snapshot review boundaries also retain
`blocked_native_delegation_unavailable`.

The static checks above show that the naming map, disclaimers, and current
copy are internally consistent enough for continued work. They do not close
the required evidence records or supply the independent native review. Record
this as an acceptance gate and keep W01 status in progress until the six
requirement records and an eligible independent review are attached.

## Review disposition

The W01 naming and copy outputs have a sound structural foundation: all 13 map
rows align, runtime identities are preserved in the dry-run plan, and the
public language retains report-only, forced-fixture, and independent-project
disclosures. The source baseline is conditionally usable for planning, with
the provenance and replayability findings above unresolved. W01 is **changes
required / acceptance pending**. No repository rename, host edit, deployment,
publication, mail submission, artwork generation, or runtime/gameplay claim is
approved by this review.
