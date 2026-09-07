# W07 final acceptance-source review

This review checks the final acceptance source records and the narrow website
handoff requested for the private local audit. The canonical package was read
at root revision `3331af6058035a7dbcd3d577b93c7a25e7765f6b`. Its working tree
also contains deliberate handoff receipt updates to operations, local checks,
CI review, and the brand draft PR. The website checkout was checked at clean
head `56e532b21922f39480cd15dcbb465676770408f5`. No source, remote, merge,
deployment, publication, or campaign operation was performed by this review.

The website inspection is limited to the current homepage/report/build
source, the route map, the two private homepage renders, and the existing
receipts. It is not a rerun of the broader website matrix or a production
check.

## Requirement coverage

- The package contains **70 requirement rows and 70 evidence files**. Every
  evidence ID is present exactly once, every recorded status matches its
  requirement row, and all 70 `binding_requirements_sha256` values match the
  current `data/requirements.json` digest. The 70 rows are all mandatory;
  **55 are verified and 15 are specifically blocked** in
  `execution/requirements-status.json:211-240,1048-1078,1331-1361,1931-1991,2071-2134,2215-2284,2359-2388`.
- All referenced review paths and artifact paths exist. There are **752
  artifact references** and no missing files. Twenty-four references are
  stale because the current working-tree versions of
  `execution/operations.json` and `execution/reviews/final-local-checks.json`
  were updated after the evidence records: the affected requirements are
  REQ-037 through REQ-042, REQ-057 through REQ-060, and REQ-069 through
  REQ-070. Rebind those rows after the final metadata freeze; the stale
  references must not be described as exact current bytes.
- REQ-013 through REQ-018 and REQ-048 through REQ-050 each repeat the same
  three website review artifact rows. The duplicate rows have identical paths,
  sizes, and digests, so they do not hide a missing artifact, but they should
  be deduplicated during final evidence cleanup.
- REQ-041 is still `blocked` with the reason that final independent coverage
  review is pending (`execution/requirements-status.json:1407-1438`). This
  report supplies that coverage review: all requirement IDs, statuses, binding
  digests, review paths, and artifact paths were cross-checked. After this
  report is integrated and REQ-041's changed artifact bytes are rebound, the
  row can be changed to `verified` without promoting the package to complete
  or satisfying the separate native/art requirements.

## Website source and visual handoff

The current website checkout is clean at `56e532b21922f39480cd15dcbb465676770408f5`,
the exact head recorded by `github/website-pull-request.json:5-19`. That receipt
describes an open draft PR with no merge or deployment. The actual source has
the expected report-only handoff:

- `index.html:42-45` sends visitors to `run.html#linux-defeat-20260906` and
  `build.html`, and labels the current state as a dated report with no approved
  public video or replay package.
- `index.html:60-82` names the Linux seeded Astra report, Defeat on floor 24,
  431 settled operations, and one controller restart, with a source-record
  link. The latest-report and evidence-ledger copy keeps the result report-only.
- `run.html:22` repeats the Linux report with 433 action decisions, 431 settled
  operations, one restart, and an explicit no-win boundary.
- `build.html:17-34` provides the tested developer entry point and says that it
  runs an offline Runtime-v2 fake record without launching the game, reading a
  save, calling a model provider, or requiring credentials.
- `site/route-manifest.json:8-14` maps home and runs to the Linux report and
  maps the build route to the developer docs. Its `source_revision` at `:3`
  remains the website base revision; the separate PR receipt and output map
  bind the implementation under review to head `56e532b`.

I inspected both private homepage renders referenced by
`execution/reviews/website-home-review-001.json:3-23`. Their SHA-256 values
match the receipt: the 360px dark render is
`264249248640133d469c4824bf6229632a911f2edfe3edf0d666d0a276f6902d`, and the
1280px light render is
`f6ef6cafc4cfbe1512f87e63b463a5ea4e91bcbc459986d744203840c7e98dc2`. Both
renders show the latest Linux report, report-only status, floor 24, 431
settled operations, one restart, readable report/build controls, and no
overlap. The screenshots stay under ignored private evidence and are not
website artwork or package files.

## Website evidence scope

The older W03 website receipt reports 110 browser states and a full source hash
table (`execution/reviews/W03-repair-review-002.json:4-41`), but nine of its 18
source hashes no longer match the clean `56e532b` checkout:
`index.html`, `watch.html`, `runs.html`, `decision.html`, `build.html`,
`docs.html`, `api/_functions.php`, `api/confirm.php`, and
`api/unsubscribe.php`. The other nine files remain byte-identical. The current
subscription receipt does bind all four API files to `56e532b` and records 30
synthetic HTTP checks (`execution/reviews/subscription-http-review-002.json:2-4,122-139`).
The current homepage delta receipt covers 10 automated states and the two
manual renders, not the old 110-state matrix.

Therefore the current source supports the report/build CTA and the
report-only copy verified above. REQ-013 through REQ-018 and REQ-048 through
REQ-050 should retain the local/source qualification in their evidence and
must not be summarized as a fresh 110-state result at head `56e532b` until the
changed files are rerun or a new exact source-bound receipt is issued. This is
a scope qualifier, not evidence that the current report/build links are dead.

## Release ledger state

The current working-tree local-check receipt states **195 tests passed** on the
clean exact source revision `5d1c26ecee9ce753eae89c525c4a8764d29a18e5`
(`execution/reviews/final-local-checks.json:2-20`). This review did not rerun
that full suite. `execution/release-status.json:5-13` and the generated
`delivery/FINAL_REPORT.md:20-28` still state the prior 189-test result at
`0381236`, 24 operations, and a pending brand PR update. Rendering the current
ledgers with `scripts/render_handoff.py:64-130` succeeds but differs from the
checked-in final report at the operations section because the current ledger
has 28 operations. Refresh the release ledger, report, and their evidence
references together after the final metadata freeze.

The current package inventory returns **429 files / 3,643,412 bytes**, while
the root `MANIFEST.json` has 424 entries and `PACKAGE_STATS.json` reports 426
delivery files. `scripts/package_inventory.py:71-108` currently reports six
integrity errors: three unlisted current handoff files (the W03 final
rereview, brand remote receipt, and brand PR receipt) and three changed
execution files (operations, CI review, and local checks). This is the expected
fail-closed pre-freeze state; regenerate the intentional private manifest and
checksum index only after the report, evidence rows, and external archive
review scope are settled.

The release ledger still records the private-audit classification and the
absence of approved generated art, native depth-three evidence, publication
authority, deployment, and campaign operation (`execution/release-status.json:1-33`,
`delivery/MANIFEST.json:1-30`). The open findings remain W01-ACC-01,
W01-COMP-01, W01-COMP-02, W07-REL-01, and W07-REL-02
(`execution/findings.json:7-34,339-359`). Those boundaries remain valid after
this coverage review.

## Disposition

The final acceptance source coverage review passes: every mandatory row is
accounted for as verified or specifically blocked, every evidence record has
the expected binding input, and every referenced file exists. The homepage
and report source accurately expose the latest report-only Linux record and a
tested Build destination. REQ-041 may be promoted to `verified` once this
review is integrated and its two changed artifact references are refreshed.

Before treating the private archive as frozen, deduplicate the repeated
website artifact rows, rebind changed evidence, regenerate the manifest,
checksum index, release status, and final report, and obtain the separate
external exact-byte archive review. The older website matrix remains bounded
to its earlier source revision. Mandatory artwork, native depth-three
orchestration, rights/approval evidence, publication/measurement authority,
merge, deployment, and campaign gates remain unresolved. This review grants
no public export, merge, deployment, publication, campaign, or global
completion authority.
