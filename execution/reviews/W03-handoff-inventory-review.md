# W03 independent review: release handoff and source-tree inventory

This review checks the uncommitted handoff renderer and the generated source
inventory in `AI-Ascension/ascension-brand-overhaul` at target `HEAD`
`f6060af7d3601664c8a8fe2ae56b41bb4e4cf83b`. The reviewed working-tree bytes
are `scripts/render_handoff.py` SHA-256
`26cf4bf5069476d824498573116b16ae27323d943ac2a8499783c8ce9d360314`,
`execution/release-status.json` SHA-256
`6dc0922cbbfeb2629a7a61ed713f741774e00530f78890b17469d008f14ca691`, and
`execution/source-tree-inventory.json` SHA-256
`ae8b2fafe387df38645d7f779b862f5e9246f0c5ef153c6e11efcaf6ffef5453`.
The target checkout was read only. This report is the only file written, in a
clean isolated worktree. No source, remote, deployment, publication, or full
test-suite operation was performed.

## Verification

- `python3 -m unittest tests.test_handoff -v` passed all **3 tests** against
  the dirty renderer. `git diff --check -- scripts/render_handoff.py` also
  passed. The focused tests cover the pre-existing requirement/artwork
  renderer, duplicate inventory accounting, binding-requirement protection,
  verified-state evidence, and blocked-state reasons.
- Rendering the target to a temporary output succeeded, was deterministic on
  repeated calls, and produced a 265-line report. It included `## Delivery
  scope`, the verified-work and remaining-condition sections, the operation
  ledger, and the release input digest. The emitted release digest matched
  the exact bytes of `execution/release-status.json` above. External existing
  symlink substitution for that ledger was rejected as
  `Unsafe ledger path: execution/release-status.json`.
- The current release record has the expected shape: schema marker, string
  summary, nine string-valued dimensions, and string arrays for verified work,
  remaining conditions, review records, and assumptions. Its concrete counts
  agree with the adjacent records: 189 local checks at
  `038123684946a4be4ea830af4c04c2ea7059ad88`, 72 planned asset families and
  115 required exports, 72 blocked manifest rows with zero exports, seven
  recorded native depth-1 leads with no depth-3 chain, thirteen settings
  proposals, and eleven open/draft remote receipts representing the website
  plus ten companion repositories. All listed review, runbook, and privacy
  paths existed at review time. These are ledger and receipt cross-checks;
  they do not refresh mutable remote or host state.
- `execution/source-tree-inventory.json` parses with duplicate-key rejection
  and contains 13 unique repositories and **2,045** sorted, unique entries.
  Every repository name, stable ID, and baseline revision matches the 13
  rows in `execution/source-snapshot.json`. For the nine available local
  checkouts, `git rev-parse BASELINE_REVISION^{tree}` matched every recorded
  `tree_object`, and the parsed `git ls-tree -r -z --long BASELINE_REVISION`
  entries and SHA-256 stream matched exactly. For `.github`,
  `AI-Ascension.github.io`, `ai-agent-observability`, and `aiascension.tech`,
  read-only `gh api` commit/tree requests returned the recorded commit-tree
  objects, all entries, and all four recorded stream hashes; every recursive
  response was untruncated. The `160000` submodule entry is retained as a
  commit pointer with a null byte size, as produced by `git ls-tree`.
  No file contents, private machine paths, credentials, or special files were
  copied into the inventory.

## Findings

### W03-HANDOFF-01 — Release ledger values are not schema-validated (medium, open)

The new release branch at `scripts/render_handoff.py:61-74` loads a file whose
declared schema is `ai-ascension.release-status.v1`, but it only indexes fields
and iterates them. There is no release schema or type validator, and the
existing tests do not add the release ledger to their fixture or assert any of
the new sections. `cell()` turns arbitrary values into strings, so a malformed
`verified_work` value of the string `"oops"` was accepted with exit code zero
and rendered as four character bullets. Empty objects and arrays are also
accepted, producing a report with missing delivery facts. Conversely,
changing `dimensions` to a list caused the CLI to exit without a report while
printing an uncaught `AttributeError: 'list' object has no attribute 'items'`;
`main()` catches `TypeError` and related errors at `:107-108` but not
`AttributeError`.

The checked-in release record is well-formed and rendered correctly, so this
finding is about the input boundary. Add a strict release-ledger loader (at
least the schema marker, exact required fields, string summary, string-valued
dimension object, and string arrays), convert shape failures into the helper's
normal `ValueError` path, and add focused positive/negative tests for missing,
wrong-type, empty, duplicate-key, and escaped free-text values. Decide and
document whether the release ledger is optional for legacy reports or
required for `delivery/FINAL_REPORT.md`; a missing/dangling non-regular path
is currently silently omitted by `is_file()` at `:61-63`.

## Delivery bookkeeping and acceptance boundary

The source inventory itself passes the immutable-tree verification above. The
source snapshot points to it at `execution/source-snapshot.json:706-715`, but
the current generated report's digest table at `scripts/render_handoff.py:88-93`
does not expose a source-snapshot or source-tree-inventory digest. The newly
generated inventory and release ledger are also outside the committed
`MANIFEST.json`/`CHECKSUMS.sha256` and the older helper receipt at
`execution/root-helper-checks.json:8-17` until the final private package
freeze. This is integration bookkeeping rather than a defect in the checked
inventory: refresh the final manifest/checksum and bind the source evidence
before treating the archive or final handoff as frozen.

The focused renderer tests pass, and the valid release and inventory paths are
accepted. W03-HANDOFF-01 remains open; malformed release input must fail with
a validated, reviewable error before the final handoff can be called robust.
This review grants no merge, rename, deployment, publication, campaign, or
global-completion authority.
