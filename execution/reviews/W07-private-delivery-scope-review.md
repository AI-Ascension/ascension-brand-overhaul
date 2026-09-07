# W07 private delivery scope and privacy repair review

This follow-up reviews the privacy repairs against canonical root revision
`b276375035ae3ff400efe5dfe3f7921f9978a9f4`, together with its current
working-tree delivery inputs. The requested delivery disposition is a **LOCAL
PRIVATE AUDIT** archive held in the private target repository. It is not a
public source export. The review covers the path and provider diagnostic
repairs, the fresh read-only migration plan, and the carried W07-PRIV-03
classification. The canonical root was read only: no source edit, remote
mutation, upload, deployment, or approval was performed.

## Verification

- `migration/tooling/github_migration.py:148-162` now reduces provider stderr
  to `rate_limit_exceeded`, an HTTP status class, or a generic failure. It does
  not copy caller, request, account, header, or credential text into a plan or
  receipt. The focused migration and residual repair suite recorded **38
  passed** in 2.096 seconds, including the non-disclosure regression at
  `tests/test_migration_residual_repairs.py:13-20`.
- The current portable path repair is present at
  `execution/toolchain.json:6,28` and `execution/w02-access.json:10`. These
  records no longer contain a user-specific absolute home or worktree path.
- The fresh read-only plan is byte-identified by SHA-256
  `676b32ebbd9a9fcde6e19926f2d83b2c265785c0e38b7a1a32a95e21626fcea5`, as
  recorded in `execution/reviews/migration-preflight-002.json:2-10`. It has 13
  dry-run operations and no remote mutations. A parse and marker scan found
  zero raw request-ID, API rate-limit, authorization, or token diagnostics;
  its 29 non-null error fields all use the normalized HTTP 404 class.
- The historical raw plan remains in ignored private staging only and is
  absent from `source_files`. The active normalized plan is included. This
  matches the private-directory exclusion in
  `scripts/package_inventory.py:8,40-68` and the preflight record's explicit
  private-only raw-receipt note at `execution/reviews/migration-preflight-002.json:18-24`.
- At the review snapshot, before the later delivery runbook was added, the
  candidate inventory was **337 files / 2,664,678 bytes** and
  `manifest_errors` reported **42** unlisted or mismatched entries, including
  the new delivery scope record. `scripts/package_inventory.py:71-108`
  compares the full candidate set and exact bytes, while
  `scripts/build_delivery.py:14-21` refuses to create an archive when those
  checks fail. The structural validator passed at that snapshot. A later
  build probe observed the newly added `delivery/RUNBOOK.md` before the
  manifest was refreshed and failed closed with an unlisted-file error; no
  archive was created. Re-run the inventory, validator, manifest, and archive
  probe after the complete private release set is frozen.

## Finding dispositions

### W07-PRIV-01 — machine-specific paths: addressed

The two reported personal filesystem disclosures were replaced with portable
environment and isolated-worktree labels. The private command context remains
available in ignored evidence when needed for audit reproduction. No absolute
user path was found in the current candidate scan.

### W07-PRIV-02 — raw provider diagnostics: addressed

The collector repair prevents provider stderr from entering delivery records,
and the fresh active plan contains only normalized status classes. The old raw
plan is excluded from the source inventory and is not part of the private
delivery archive. The package may retain the old plan's digest and a statement
that the raw receipt is private evidence; it must not copy the old diagnostic
contents into a public or shared export.

### W07-PRIV-03 — internal ancestry and execution metadata: addressed for the
declared private scope

The source snapshot, runtime observation, capability receipt, and operations
ledger retain thread, model, account, timestamp, and operation ancestry fields
(`execution/source-snapshot.json:2-15`, `execution/runtime-observation.json:2-10`,
`execution/capabilities.json:4-11`, and `execution/operations.json:2-25`).
Those fields are audit metadata, not hidden reasoning or credentials. Keeping
them in a private audit archive preserves the requested ancestry and does not
falsify the recorded execution boundary. Redacting them would lose evidence
that the private audit is meant to preserve.

Accordingly, PRIV-03 is closed **only because the delivery scope is explicitly
LOCAL PRIVATE AUDIT in a private repository**. That classification is now
recorded directly in `delivery/PRIVACY_SCOPE.md:1-9` and
`package-info.json:27-28`. The private boundary is a release condition: these
ledgers must not be copied into a public source archive, shared artifact, or
publication projection. Any future public export requires a separately
reviewed sanitized projection with its own manifest and an explicit scope
decision. The package's implementation and verification limits remain in
`package-info.json:7-26`; the classification grants no public export
authority.

## Remaining release gates

- **W07-REL-01 remains open pending the final freeze.** The snapshot errors,
  followed by the concurrent runbook addition, prevent this review from
  attesting to a final reviewed archive. Freeze the private file set, then
  regenerate `MANIFEST.json` and `CHECKSUMS.sha256`, validate exact bytes, and
  build outside the source tree.
- **W07-REL-02 remains a control.** Filename and directory exclusions are
  defense in depth, not a content-level secret guarantee
  (`scripts/build_delivery.py:47-50`). Review the final private archive
  contents before handing it to the authorized private repository.
- The trusted publication and measurement registries remain empty. This review
  grants no production, publication, deployment, campaign, or global-completion
  authority.

## Disposition

PRIV-01 and PRIV-02 are addressed by the verified repairs. PRIV-03 is addressed
for the declared local-private audit scope while preserving truthful ancestry
metadata. The package is **not approved for public export**. Archive integrity
and final content review remain open, and no remote or live operation was
performed by this review.
