# W07-L independent re-review: W04 migration residual repairs

This review checks the GitHub migration implementation at the exact root freeze
`eb32e7efcf362f395cf44c7c020f2e1ebfc58a3d`. The migration module and residual
test module in the temporary review archive match the corresponding files at
that revision byte-for-byte. The review rechecks original W04-09 and W04-10
and the six residual findings W07-W04-11 through W07-W04-16. No GitHub API
request, repository rename, owner notification, or remote mutation was made.

## Verification

- `python3 -m unittest tests/test_migration_tooling.py tests/test_migration_review_repairs.py tests/test_migration_residual_repairs.py -v` — **37 passed** in 1.205 seconds.
- `python3 -m py_compile migration/tooling/github_migration.py tests/test_migration_tooling.py tests/test_migration_review_repairs.py tests/test_migration_residual_repairs.py` — passed.
- `git diff --check eb32e7e^ eb32e7e -- migration/tooling/github_migration.py tests/test_migration_review_repairs.py tests/test_migration_residual_repairs.py docs/MIGRATION_OPERATIONS.md` — passed.
- An offline CLI plan using `execution/source-snapshot.json` produced 13
  dry-run operations with only `blocked`, `deferred`, and `not_applicable`
  preflight statuses. The plan recorded the exact snapshot-file SHA-256
  `251a07d059c8ba279bf5fe3f33eaae233b205eb85418a71485be2d559ddee734`, which
  matched the file hash; all embedded backup digests also matched.
- Independent temporary-file and fake-client probes reproduced the receipt,
  lock, snapshot, inventory, map-conflict, and duplicate-key cases below.
  The probes used no live service.

## W04-09 and W04-10

### W07-W04-09 — operation-set lock: addressed

`operation_set_lock_path` derives the lock solely from the validated plan
digest under the shared local state directory at
`migration/tooling/github_migration.py:1075-1079`. `apply_plan` acquires that
lock with exclusive creation before taking the selected receipt lock and
removes it only after the operation-set call returns at `:1273-1305`. The
symlink check protects every existing component of the trusted lock path.

An exact-byte copy of a plan in a different directory returned the same lock
path. With that lock held, applying the copied plan with an alternate receipt
raised `Operation set is locked` and made zero rename calls. The documented
boundary remains a single local account; coordination across hosts or OS
accounts is outside this lock.

### W07-W04-10 — snapshot identity and exact provenance: addressed

`validate_snapshot` requires a schema marker, object repository rows, valid
owner/name identities, case-folded unique `full_name` values, and positive
unique stable IDs at `migration/tooling/github_migration.py:794-821`.
`snapshot_provenance` verifies supplied bytes decode to the supplied snapshot,
uses the exact-byte digest when bytes are available, and rejects a claimed
digest that differs from the computed value at `:824-843`. `build_plan` rejects
map identity fields that disagree with the supplied snapshot at `:896-909`.
The CLI reads bounded bytes with duplicate-key rejection and passes those exact
bytes to the planner at `:1487-1506`.

Fresh probes rejected duplicate case-folded names, duplicate stable IDs, each
of `source_head`, `default_branch`, and `visibility` when it contradicted the
snapshot, and a direct caller's all-zero digest. A formatted byte representation
whose decoded object matched the snapshot produced the SHA-256 of those exact
bytes. Duplicate JSON object fields were rejected by `read_json` at
`:110-127`.

## Residual findings

### W07-W04-11 — failed receipt reload and retry: addressed

`_validate_receipt_rows` now accepts the definite `failed` terminal status at
`migration/tooling/github_migration.py:1096-1117`. A prior failed or blocked
operation is freshly observed before `evaluate_operation` runs at `:1351-1368`;
the request is persisted as pending before a rename and a definite API refusal
is retained as `failed` at `:1403-1429`. Ambiguous outcomes remain `unknown`
and halt the set.

An HTTP 422 fake response produced a durable `failed` row. The next invocation
with a changed source head produced `blocked` and made no second PATCH. After
the head was restored, a subsequent invocation produced `applied` with exactly
one additional PATCH. This closes the receipt reload defect while retaining a
fresh preflight gate before a deliberate retry.

### W07-W04-12 — copied-plan operation lock race: addressed

The lock no longer includes `plan_path.name`; it is the digest-only path
described at `migration/tooling/github_migration.py:1075-1079`. The copied-plan
probe above exercised the previously divergent path case and blocked the
alternate receipt before any client mutation.

### W07-W04-13 — map fields overriding snapshot preconditions: addressed

When a snapshot is supplied, `build_plan` requires the mapped source to exist
in that snapshot and compares optional map `source_head`, `default_branch`, and
`visibility` values with the snapshot at
`migration/tooling/github_migration.py:896-907`. The generated operation then
records preconditions consistent with those validated snapshot values at
`:908-932`. Independent probes rejected all three conflicting map values before
a plan was produced.

### W07-W04-14 — false direct snapshot digest: addressed

`snapshot_provenance` computes the canonical object digest when only an object
is supplied and computes the exact raw-byte digest when bytes are supplied. A
non-matching caller digest is rejected at
`migration/tooling/github_migration.py:827-835`; `build_plan` also rejects
provenance arguments without a snapshot at `:876-882`. A direct planner call
with 64 zeroes now raised `Source snapshot digest disagrees with supplied
bytes`, while matching formatted bytes produced the exact file digest.

### W07-W04-15 — malformed API inventory rows: addressed

`GhApi._list_paginated` requires the expected list, rejects incomplete search or
pagination counts, and now rejects every non-object row at
`migration/tooling/github_migration.py:216-248`. `observe_repo` records the
resulting endpoint failure as unavailable, and `evaluate_operation` blocks the
active-work gate when workflow or pull inventory is unavailable at `:709-725`.

Independent probes supplied `None`, a number, and a string as rows for array,
workflow-run, and search-item responses. Every case raised the non-object-row
`ApiError`; a full fake repository observation set
`workflow_read_available=false`, and evaluation returned
`blocked / active_work_inventory_unavailable`.

### W07-W04-16 — duplicate targets and dependent renames: addressed

`validate_repository_rows` now rejects case-folded duplicate target identities
and any source/target overlap that would make one rename depend on another at
`migration/tooling/github_migration.py:758-791`. `validate_plan` invokes the
same validation before operation processing at `:999-1002`, so a hand-edited
plan receives the same protection. Fresh map probes rejected both two rows
targeting `shared` and a row sequence whose target was another row's source.

## Bookkeeping and authority boundary

The implementation source has the requested repairs, but
`execution/w04-repair-implementation.json:4-5` still names the earlier
`5ba8c65c361a7a0738557313289c4717e0ff5e52` implementation revision, and its
scope at `:92-96` still says independent review is pending. That receipt
predates the residual repair commit and should be refreshed by root to bind
the final W04 record to `eb32e7e` and the 37-test validation. This is integration
bookkeeping rather than a migration-code failure.

The results establish source-level and local fake-client evidence only. No
approval file, remote apply authority, rename receipt, owner notification,
deployment, or production release was created.

## Review disposition

W07-W04-09, W07-W04-10, and W07-W04-11 through W07-W04-16 are addressed at the
frozen source revision. Refresh the stale implementation receipt before marking
the W04 repair handoff complete. No remote mutation or production authority is
granted by this review.
