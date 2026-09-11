# W07-L independent review: frozen W04 migration repairs

This review checks the migration implementation at exact revision
`5ba8c65c361a7a0738557313289c4717e0ff5e52`. The accompanying validation receipt
at `58b16e586c9c20834589d7da6bc5156ce413cb45` records that implementation and
adds only `execution/w04-repair-implementation.json`; no migration source changed
between those revisions. The review uses the implementation worktree
`work/w04-review-repairs` and writes this report only in the independent `work/w07`
worktree. No GitHub API request, rename, owner notification, or remote mutation
was performed.

## Verification

- `python3 -m unittest tests/test_migration_tooling.py tests/test_migration_review_repairs.py -v` — **30 passed** in 1.139 seconds.
- `python3 -m py_compile migration/tooling/github_migration.py tests/test_migration_tooling.py tests/test_migration_review_repairs.py` — passed.
- `git diff --check 5ba8c65^ 58b16e5` — passed.
- Python 3.12.3 and Git 2.43.0 were used. All probes used temporary files,
  fake clients, or fake `gh` subprocess responses.
- An offline CLI plan against `execution/source-snapshot.json` produced 13
  dry-run operations and recorded the exact snapshot-file SHA-256; its statuses
  were `blocked`, `deferred`, and `not_applicable`, as required for unavailable
  protected and caller inventories.

## W07-W04-01 through W07-W04-10 dispositions

| Finding | Disposition and evidence |
| --- | --- |
| W07-W04-01 recorded branch/visibility preconditions | **Addressed.** `evaluate_operation` requires and compares `expected_default_branch` and `expected_visibility` at `migration/tooling/github_migration.py:614-638`; `validate_plan` requires both at `:993-995`. A fake source with `main/public` against `develop/private` returned `blocked` with `stale_default_branch` and `stale_visibility`. |
| W07-W04-02 backup reference/gate | **Addressed for the implemented plan contract.** `build_plan` embeds a compact metadata snapshot and SHA-256 at `:883-889`; `:545-559` checks the internal digest and fresh-source digest, and `validate_plan` rejects a missing or altered reference at `:996-1006`. Changing the backed-up head produced `blocked / backup_reference_digest_invalid`. The backup is plan-embedded, so its durability still depends on retaining the exact approved plan bytes. |
| W07-W04-03 optional 404 handling | **Addressed.** `GhApi.request` now raises endpoint errors; repository absence is interpreted only by the repository GET at `:277-291`, while Action-file 404s are the documented absence case at `:239-246`. Pages, workflow/run, pull, and code-search failures remain unavailable at `:313-348`, and evaluation blocks those gates. A fake 404 for every optional endpoint returned `pages_available=false`, `workflow_read_available=false`, `pull_read_available=false`, `action_consumers_known=false`, and the corresponding blockers. |
| W07-W04-04 active-work completeness | **Addressed for valid GitHub responses.** `ACTIVE_RUN_STATUSES` includes queued, in-progress, waiting, requested, and pending at `:41`; `observe_repo` queries all at `:329-338`, and `_list_paginated` checks every page and count/cap condition at `:204-234`. A fake inventory observed all five statuses, 101 pull requests over two pages, and 101 search rows over two pages. |
| W07-W04-05 ambiguous transport classification | **Addressed for the supported transport exceptions.** `ApiError` classifies 5xx, timeout, reset, aborted, broken-pipe, and network errors at `:59-88`; the apply path catches connection/OS/timeout failures and leaves them `unknown` at `:1371-1385`. A fake 502 and connection reset each produced one `unknown` attempt. |
| W07-W04-06 halt after unknown/verification failure | **Addressed.** The apply loop breaks after an unknown result at `:1381-1385`, after verification failure at `:1386-1395`, and after a final verification failure at `:1410-1413`. Two ready fake operations with a 502 on the first produced one receipt row and one PATCH call. |
| W07-W04-07 stale applied receipt | **Addressed.** A fresh source/target read occurs before terminal receipt reuse at `:1319-1323`; `_receipt_post_state_matches` binds identity, request, response, full compact verification, post-state digest, and source absence at `:1112-1179`. After a successful fake rename, changing the target ID made the next call `blocked` with no second PATCH. |
| W07-W04-08 approval actor/owner scope | **Addressed for the CLI apply contract.** Plan construction rejects owners outside `AI-Ascension` at `:855-862`, plan validation repeats the owner gate at `:980-983`, and apply binds `approved_by` to `current_user().login` and requires every rename ID at `:1202-1225`. A mismatched actor and `OtherOrg` map row were both rejected before mutation. |
| W07-W04-09 operation-set lock | **Partially addressed; see W07-W04-12.** The digest-qualified operation lock prevents an alternate receipt path when the same plan path is used (`:1036-1040`, `:1235-1261`), and the corresponding focused test passed. The lock name also contains the plan filename, so copied exact-byte plans do not share it. |
| W07-W04-10 immutable snapshot provenance | **Partially addressed; see W07-W04-13 and W07-W04-14.** `validate_snapshot` rejects malformed rows, duplicate case-folded full names, duplicate/nonpositive IDs, and missing schema at `:773-800`; the CLI records the exact source-file digest at `:1443-1454`. The direct planner API does not enforce that all map preconditions agree with the snapshot or that a caller-supplied digest matches the snapshot value. |

## Residual findings

### W07-W04-11 — A definite failed rename receipt cannot be loaded on retry (high, blocking)

The apply path persists a non-ambiguous API refusal as `status: "failed"` at
`migration/tooling/github_migration.py:1371-1385`. `_validate_receipt_rows` accepts
many terminal and unresolved statuses at `:1065-1076`, but omits `failed`. A fake
`HTTP 422 Unprocessable Entity` therefore produced a durable receipt row with
`status=failed`; the next ordinary invocation raised:

`MigrationError: Existing migration receipt has no status for rename:AI-Ascension/source->target`

This leaves the documented receipt path unusable after a normal API rejection.
Add `failed` to the receipt schema and define whether a fresh invocation may
re-evaluate it or must stop for explicit operator acknowledgement. Keep the
operation request and response bound to the row.

### W07-W04-12 — Operation-set locking is still path-scoped (high concurrency risk)

`operation_set_lock_path` at `:1036-1040` builds the filename from both
`plan_path.name` and the plan digest. Copying the same plan bytes from
`plan.json` to `copied-plan.json` produced two different lock names:

` .plan.json.<digest>.operation-set.lock`
` .copied-plan.json.<digest>.operation-set.lock`

Two invocations can therefore pass the operation-set lock with different plan
paths while targeting the same remote repositories. This contradicts
`docs/MIGRATION_OPERATIONS.md:103-108`, which says the lock is derived from the
exact plan digest and covers all receipt paths. Derive the shared lock from the
digest alone in a trusted common lock directory, or bind plan identity to a
canonical immutable plan location before applying.

### W07-W04-13 — Map branch/head fields can override the supplied snapshot (high provenance risk)

When a snapshot is supplied, `build_plan` compares only the mapped stable ID at
`:864-869`. It then chooses `item["source_head"]` before the snapshot head at
`:870-871` and `item["default_branch"]` before the snapshot branch at
`:890-894`. A snapshot recording `default_head=a…` and `default_branch=main`,
a map row recording `source_head=b…` and `default_branch=develop`, and a live
source matching the map produced a plan with expected head `b…` and branch
`develop` without refusal. The plan can consequently carry an accurate snapshot
SHA-256 while its mutation preconditions describe different source state.

With a supplied snapshot, reject any map head/branch/visibility mismatch, or use
the validated snapshot values exclusively. If a map override is intentional,
record it as an explicit reviewed transition rather than silently replacing the
snapshot precondition.

### W07-W04-14 — Direct planner callers can assert a false snapshot digest (medium provenance risk)

`snapshot_provenance` accepts an optional digest at `:803-815` and checks only
that it has SHA-256 shape. `build_plan` passes that value through at `:945-948`.
A direct call supplied 64 zeroes for `snapshot_sha256` and returned a valid plan
with that false digest, even though the snapshot's canonical digest was
`7f37f3f6b1284463f41d24f57230b1a6293ecc71d60ae49fcb6dc0f26023d2fd`. The CLI
path is safer because `command_plan` computes the digest from exact file bytes
at `:1453`, but the exported planner API can still create misleading
provenance. Require the helper to verify the supplied digest against the exact
bytes it receives, or make the file-reading command the only path that accepts
an exact-byte digest.

### W07-W04-15 — Malformed list entries are silently dropped and can pass active-work checks (medium/high integrity risk)

`_list_paginated` retains only dictionary items at `:223`. A fake response with
`workflow_runs: [null]`, an empty pull list, and an empty search result yielded
`workflow_read_available=true`, `active_runs=[]`, `pull_read_available=true`, and
`action_consumers_known=true`; the active-work gate then returned
`pass / no_open_pull_requests_or_runs`. A malformed API response should make the
inventory unknown rather than erase a possible blocking run or pull. Reject any
non-object list entry and propagate an unavailable/incomplete gate.

### W07-W04-16 — Duplicate target names allow a partial operation set (high mutation risk)

`validate_repository_rows` checks duplicate source identities and stable IDs at
`:744-770`, but does not reject duplicate target names or source/target overlap
between rows. Two otherwise ready fake rename operations targeting the same
initially absent `shared` name both passed their initial target-collision gates.
Applying the set renamed the first repository (`applied`) and then blocked the
second on the now occupied target (`blocked`), leaving a partial migration.
Reject duplicate case-folded target names and source/target dependency cycles
before producing an authorized plan, or require an explicit ordered plan with a
separate review for each dependent operation.

## Review disposition

The 30 focused tests and the adversarial probes establish that the principal
W07-W04-01 through W07-W04-10 repairs are present and effective for their
covered contracts. W07-W04-09 and W07-W04-10 are incomplete at the edges noted
above. W07-W04-11 through W07-W04-16 remain open, including the failed-receipt
reload blocker and cross-path lock race. The implementation receipt's
`unaddressed_w04_findings: []` is therefore not an independent review result.
No rename, merge, deployment, notification, or production authority is granted.
