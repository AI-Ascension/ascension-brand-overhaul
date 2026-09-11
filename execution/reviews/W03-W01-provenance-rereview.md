# W03 independent provenance rereview: W01 repairs

This rereview checks the six repairs identified in
`execution/reviews/W03-W01-review.md` at exact commit
`dd380bac134f768783dc8ba284ef6efd29546088`:

- `W01-SRC-01` runtime-v1 report/source provenance;
- `W01-SRC-02` watchdog default-branch and draft-PR provenance;
- `W01-SRC-03` canonical-domain source versus host evidence;
- `W01-SRC-04` selected-document inventory language;
- `W01-COPY-01` mixed-source copy records; and
- `W01-PKG-01` frozen package-result wording.

The review is bound to the four repaired source files:
`execution/capabilities.json`, `execution/source-snapshot.json`,
`brand/copy.json`, and `docs/BASELINE_AUDIT.md`. The target branch had unrelated
dirty work outside this scope; this report was produced in a clean isolated
worktree based on the repair commit. No source repository, host, deployment,
migration, publication, mail, or runtime operation was performed.

## Verification

- JSON parsing succeeded for all four repaired files. Loading
  `execution/capabilities.json` through
  `publisher.capabilities.load_capability_registry` returned 17 validated
  capability records and the `ai-ascension.capabilities.v1` metadata envelope.
  `git diff --check c9b3369..dd380ba --` over the repaired paths was clean.
- The exact pinned runtime report was fetched read-only from
  `AI-Ascension/sts2-game-mod` at revision
  `8b71150895ea95c0625afc1389bb08e4034d9350`. GitHub returned blob
  `718e9fa55c29d151d8108ce68a71ab49791d5e24`, 4,376 bytes, and raw SHA-256
  `7ea6e14804926c17a92980d205ebde1f001c611de0d91cbae04eeb9bf7144b4b`.
  Those values exactly match the new 37th `source_documents` entry at
  `execution/source-snapshot.json:445-450`.
- A targeted provenance assertion pass checked the runtime addendum, watchdog
  default/PR relationship, domain host/source separation, every multi-source
  copy record, and the corrected frozen-result text. It reported
  `W01 provenance repair assertions: PASS`: 37 source documents, 17
  capabilities, and seven multi-source copy objects with no legacy singular
  `source_revision`.
- The focused publisher tests
  `python3 -m unittest tests.test_capability_output tests.test_capability_provenance -v`
  passed all 5 tests. The full package validator and full test suite were not
  rerun because the integrated package manifest/checksums still require the
  separately planned refresh.

## Repair results

### W01-SRC-01 — Runtime-v1 report provenance: repaired

`execution/capabilities.json:63-76` now identifies `8b711508` as the revision
of the report document and says that the reported build used source HEAD
`97f3a206` plus uncommitted runtime-v1 changes. It explicitly says the runtime
patch and package bytes were not collected or verified and that the result is
not reproducible from the report revision alone. The source snapshot addendum
at `execution/source-snapshot.json:706-713` repeats the report revision and
reported build base and records both uncommitted-patch and package-byte
collection flags as false.

The remote report itself states the same source state, and its exact blob and
SHA-256 are now recorded in the selected-document inventory. The repair keeps
the result maintainer-reported and report-only, so it does not imply that the
uncommitted runtime is a reproducible source build. **Pass.**

### W01-SRC-02 — Watchdog default branch versus draft PR: repaired

`execution/capabilities.json:207-220` now describes only PR #2, uses its
`55480e05` head, and states that the draft is against bootstrap and is not part
of the default source. The source snapshot identifies the default branch as
`bootstrap` at `dc2d20badb9e86c12067316b92d6c8289b2e6995` and the PR row at
`:516-534` records `55480e05` as its head and `dc2d20ba` as its base. The copy
and migration records continue to use the bootstrap revision for the source
description.

The failed platform-check and no-live-service boundaries remain explicit.
There is no longer a default-branch claim supported by the PR head. **Pass.**

### W01-SRC-03 — Canonical-domain source versus host evidence: repaired

`execution/capabilities.json:255-268` now labels the capability
`Canonical-domain website source`, limits its claim to the PHP repository
documentation, and states that host behavior is not established by that
source-derived record. Its notes point to the separate host observations in
`execution/site-baseline.json` and the source snapshot deployment surfaces.
The deployment surface at `execution/source-snapshot.json:625-642` remains
explicitly `operator_observed_live` with its own HTTP, PHP, branch, monitoring,
POST, and mail limits.

The source record therefore cannot promote an HTTP response or host version to
a source claim, and the host record cannot be mistaken for a successful mail
or brand-branch deployment. **Pass.**

### W01-SRC-04 — Selected-document inventory language: repaired

`docs/BASELINE_AUDIT.md:49-53` now defines the replayable scope as the selected
README, product, policy, workflow, and evidence paths listed in
`source_documents`. It distinguishes the selected blob identities from the
workflow-path summaries and says that broader policy filenames do not mean
their complete bytes are inventoried. This matches the 37-entry source
inventory and the `source_inventory_scope` addendum at
`execution/source-snapshot.json:706-709`.

The audit no longer claims that unlisted AGENTS, architecture, coding-standard,
layout, or every workflow file has a recorded blob. **Pass.**

### W01-COPY-01 — Mixed-source copy provenance: repaired

The season at `brand/copy.json:36-72` is now `evidence_kind: mixed`, removes
the ambiguous top-level revision, and records the Windows defeat, Linux defeat,
and forced-fixture sources separately with their own URLs, revisions, and
evidence kinds. The same structure is present on all six message records at
`brand/copy.json:74-374`; the seven multi-source objects have matching
`source_ids` and `source_records`, and none retains a singular top-level
`source_revision`.

The targeted assertion compared every source record against the corresponding
capability or historical-evidence record. It found no mismatched revision, URL,
or evidence kind. Single-source headline, repository, disclosure, and CTA
records retain their direct provenance fields. The copy continues to state
that the fixture is terminal observation only and that the current campaign
records end in Defeat. **Pass.**

### W01-PKG-01 — Frozen package-result wording: repaired

`docs/BASELINE_AUDIT.md:127-129` now records that the exact
`0e03d97bc6af6b7622d33d830bdde1eef1c2b1d8` archive passed package validation
and all 170 tests, and that the later `c9b3369cb182fce81c7b6c9d550ad6b95455a64d`
archive had eight W04/W07 inventory or hash errors and two package-related
failures among 188 tests. It explicitly removes the earlier false
`.gitignore` failure attribution. The wording matches the retained test logs
and keeps package checks separate from gameplay, deployment, and art claims.
**Pass.**

## Acceptance boundary

All six repaired findings pass the targeted rereview. The repaired commit still
records `source_provenance_repairs_pending_rereview` in its review boundary and
the audit says the provenance repairs require rereview; that status was correct
at the reviewed commit and should be reconciled when this report is integrated.
The required depth-3 native reviewer ancestry remains unavailable, and the
root's separate REQ-001 through REQ-006 evidence work remains an acceptance
gate. The package manifest/checksum refresh is also still required before a
full package result can be asserted.

## Review disposition

The runtime report is now pinned at report-byte level without claiming the
uncommitted runtime patch or package bytes. Watchdog, domain, selected-document,
mixed-copy, and frozen-result provenance are internally consistent at
`dd380ba`. **No findings remain against these six repairs; the W01 provenance
repair rereview passes.** This does not close the native-depth or final package
acceptance gates.
