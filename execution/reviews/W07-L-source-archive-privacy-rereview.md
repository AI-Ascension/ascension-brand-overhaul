# W07 independent source-archive privacy and release-scope review

This review audits the current canonical package inputs at root revision
`fd0e670c44b9929085ddea07d47a565858422f2e`, including the working-tree
workflow and execution receipts that are not yet committed there. It covers
`scripts/package_inventory.py`, `scripts/build_delivery.py`, the actual
`source_files` inventory, `execution/**`, `brand/**`, `config/**`,
`tests/fixtures/**`, and the W01-W06 marketing repairs. The canonical root was
read only. No source change, remote write, upload, deployment, or production
approval was performed.

## Verification

- `source_files(Path('.'))` returned **334 files / 2,691,461 bytes**. The
  scoped directories contain 39 execution files / 354,075 bytes, 6 brand
  files / 137,733 bytes, 2 config files / 143 bytes, and 4 publication
  fixtures / 6,215 bytes.
- `file --mime-type` classified every candidate as text-like: 208
  `text/plain`, 85 JSON, 1 HTML, 39 Python, and 1 JavaScript. No binary asset,
  font, game file, screenshot, or video entered the candidate inventory.
- The private `.execution-private` directory exists and contains 1,590 files,
  but `source_files` includes zero of them. `package_inventory.py:8-10,31-58`
  also excludes the private execution directories, virtual environments,
  vendor trees, common credential basenames, key/certificate suffixes, and
  symlinks or special files. The exclusion tests pass, but the helper itself
  correctly documents that filename patterns are not a secret scanner
  (`scripts/build_delivery.py:31`).
- A targeted heuristic scan over the scoped files found zero private-key
  headers, cloud/GitHub token forms, bearer/basic authorization values, or
  secret assignments. Its three email matches are synthetic examples in prior
  review text. The publication fixtures are explicitly synthetic and local
  only (`tests/fixtures/publication/run.synthetic.json:1-115`,
  `events.synthetic.json:1-31`, `capabilities.synthetic.json:1-17`, and
  `comparison.synthetic.json:1-44`). The intake record likewise states that
  no private trajectories, binary assets, captures, provider calls, or game
  runtime were accessed (`execution/authentic-report-intake.json:5-24`).
- `python3 -m unittest tests.test_package_inventory tests.test_delivery_privacy -v`:
  **5 passed**. The tests cover case-insensitive known-secret exclusions,
  duplicate control keys, unlisted files, review-digest binding, private
  execution-directory exclusion, and preservation of an existing archive.

## Findings

### W07-PRIV-01 — User-specific absolute paths remain in package inputs (medium; public-export blocker)

`execution/toolchain.json:6,28` records an absolute local tool-cache path in
both a wrapper field and a test command. `execution/w02-access.json:10`
records an absolute user worktree path. These values are not credentials, but
they disclose the local account/layout and make a shared or public archive
machine-specific. Replace them with a portable relative label or a redacted
command before accepting a public source archive. Keep exact private command
receipts in the ignored private evidence area.

### W07-PRIV-02 — Migration plans retain raw provider rate-limit diagnostics (high; public-export blocker)

The active plan embeds raw GitHub API rate-limit error strings, including a
caller account identifier, provider request identifiers, and exact request
times in `migration/plan.json:3013-3016,3096-3099,3173-3176,3304-3307,
3350-3353,3390-3393`. The copied prior plan has the same class of diagnostic
at `migration/plans/afef3fa110743ff13fe262d6f448af2820b0bffa4f80fa95ac3a891d7b839656.json:1958-1965,2024-2032,2108-2116,2138-2146,2239-2247,2286-2294`.
These are operational support details rather than source evidence and are
unnecessary in a public package. Replace the error value with a normalized
status such as `rate_limit_exceeded`, or keep the raw response only in a
private receipt. Do not quote or reproduce the provider identifiers in a
public report.

### W07-PRIV-03 — Internal execution and account metadata is mixed into the archive candidate (medium; scope blocker)

The source snapshot and runtime observation contain agent thread IDs,
timestamps, model/effort metadata, and account identity fields
(`execution/source-snapshot.json:4-54`; `execution/runtime-observation.json:2-40`).
The capability receipt repeats a collector thread identifier
(`execution/capabilities.json:6-11`), and the operations ledger records
repository-creation/push history and remote receipts
(`execution/operations.json:2-18`). None of this is hidden reasoning or a
credential, and it is useful to a private audit, but it is not required by a
public source archive. Keep these ledgers private or publish a deliberately
sanitized evidence projection that removes account/thread identifiers and
internal operation receipts. Reconcile the projection with the package
README's authoring-time claims before release.

### W07-REL-01 — Integrity metadata is stale against both the integrated head and dirty inputs (high; fail-closed release blocker)

The current candidate set has 334 files while `MANIFEST.json` has 313 entries
and `PACKAGE_STATS.json` still reports 121 delivery files. The working tree
adds untracked workflow, review, runtime, GitHub, and migration records and
modifies tracked execution, marketing, and migration files. Running
`python3 scripts/validate_package.py` reports **30** unlisted/checksum
errors. A clean archive of `fd0e670c44b9929085ddea07d47a565858422f2e` still
reports **14** integrity errors because integrated review and repair files are
not represented by the frozen manifest.

This behavior is safely fail-closed: `manifest_errors` compares the complete
candidate set and exact bytes (`scripts/package_inventory.py:79-107`), and
`build_delivery` validates before creating its destination
(`scripts/build_delivery.py:9-27`). A direct build probe raised the expected
manifest-validation error and left no destination file. Do not refresh the
manifest blindly. First choose the intentional release set, remove or redact
the privacy findings above, decide which internal execution records remain
private, then regenerate `MANIFEST.json` and `CHECKSUMS.sha256` and rerun the
validator and archive probe.

### W07-REL-02 — Filename exclusions provide no content-level secret guarantee (medium; residual release control)

The inventory's basename/suffix rules are useful defense in depth, but a
secret embedded in an ordinary Markdown or JSON file would still be a normal
candidate. The current heuristic scan found no obvious credential pattern,
but it does not replace a content-level secret scan and manual review of every
candidate before a public archive. The raw provider diagnostics above show why
an operational-privacy review remains necessary even when no token pattern is
found.

## CI workflow review

The untracked `.github/workflows/validate.yml:8-27` is narrowly scoped: it
grants `contents: read`, uses an immutable `actions/checkout` revision with
`persist-credentials: false`, installs the pinned development dependencies,
and runs package validation plus the local test suite. It has no publishing
secrets, mutation step, `pull_request_target` trigger, deployment, or upload.
`execution/reviews/ci-action-review-001.json:1-15` records the matching
immutable-action/source review and explicitly leaves `remote_result` as
`not_run_yet`. Static review passes; no remote CI success is claimed. The
workflow and its receipt are currently unlisted, so they must be intentionally
included and hashed if retained.

## W01-W06 marketing recheck

The three findings in `execution/reviews/W01-W06-review.md` are addressed by
the frozen marketing repair at `fd0e670c44b9929085ddea07d47a565858422f2e`:

- **W01-W06-MKT-01 addressed.** EXP-07 now measures `evidence_open` against
  eligible `run_page_view` events and explicitly says that the event is not a
  correction submission (`marketing/experiments.json:321-368`). The former
  unsupported event name is absent from the repaired experiment and test
  inputs.
- **W01-W06-MKT-02 addressed.** Former proxy labels now resolve to the
  declared `repeat-engagement-proxy`. Its mapping names every source event,
  matches the canonical numerator/denominator/window/exclusions/absence
  values, requires consented coarse cohorts, and limits interpretation to a
  non-person, non-retention count (`marketing/experiments.json:369-430`).
  `tests/test_marketing_experiments.py:39-63` cross-checks the schema,
  event contract, metric registry, and mapping.
- **W01-W06-MKT-03 addressed.** The current receipt records the 9 targeted
  tests and binds the 170-test full-suite result to the exact independent
  frozen revision, while preserving the old builder count under an explicitly
  historical section (`execution/w06-implementation.json:202-215,248-265`).

Evidence for the recheck:

- `python3 -m unittest tests.test_marketing_package tests.test_marketing_experiments tests.test_marketing_files -v`:
  **9 passed** at the repaired head.
- A clean archive of the recorded independent revision ran
  `python3 -m unittest discover -s tests -v`: **170 passed in 15.419 seconds**.
- The direct cross-file probe found schema and contract event sets equal, no
  unsupported former experiment names in the repaired inputs, and an exact
  derived-metric mapping. All experiment results remain `unobserved` and no
  campaign operation was performed.

## Disposition

The private-directory exclusion, synthetic-fixture classification, absence of
observed credential patterns, CI workflow boundaries, and W01-W06 marketing
repairs are supported by the checks above. W07-PRIV-01, W07-PRIV-02,
W07-PRIV-03, W07-REL-01, and W07-REL-02 remain open for a public archive.
The package is not approved for public export, publication, campaign
operation, deployment, or global completion. Both publication and measurement
authority registries remain empty (`config/publication-authorities.json:1-3`,
`config/measurement-authorities.json:1-3`), and the package metadata continues
to state that runtime, artwork, and GitHub mutations are unverified or absent
(`package-info.json:13-26`).
