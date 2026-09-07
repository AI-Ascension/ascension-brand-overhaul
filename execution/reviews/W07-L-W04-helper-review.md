# W07-L independent review: W04 migration, helpers, and companion READMEs

This review checks the W04 migration tool at the exact implementation hash
d6cb72c carried into root 5b752cd49c16a5bec32816a09dd93920bb419437, the
W01/W02 helper scripts and runbooks, and the isolated companion README diffs.
The migration probes use fake clients only. No GitHub mutation, owner
notification, companion commit, deployment, or live service operation was
performed.

## Verification and scope

- python3 -m unittest tests/test_migration_tooling.py -v: 19 passed.
- The exact root run python3 -m unittest discover -s tests -v passed 149
  tests. execution/root-helper-checks.json:1-89 now records the 5b source
  revision and all 149 synthetic local tests, while independent_review remains
  pending.
- The ten companion repositories are at the exact base_revision values in
  github/presentation-manifest.json. Their expected presentation files are the
  only modified files, and git diff --check passed for each repository. The
  manifest keeps settings: manual_review_required, apply: false, and owner
  notifications disabled.

The README changes preserve repository slugs, package/runtime names, Pages
routes and evidence anchors, and existing unverified/status language. The
Pages and flagship CTAs put “Watch AI play. Inspect the run. Help it climb.”
near the presentation copy; the surrounding text still identifies the
available deterministic or bounded evidence and explicitly keeps model-played
Victory, native multiplayer, and broader compatibility unverified. This is a
manual wording/order review item, not evidence of a remote migration.

## Migration findings

### W07-W04-01 — Recorded branch and visibility preconditions are ignored (high)

build_plan records expected_default_branch and expected_visibility at
migration/tooling/github_migration.py:594-603, but evaluate_operation at
:405-534 compares only stable ID/name, head, protected configuration, hosted
Actions, active work, Pages, and authority. A source observed as
default_branch=main, visibility=public with an operation expecting
develop/private returned ready with authorized=True and no branch/visibility
blocker. A rename can therefore pass while two explicitly recorded identity
preconditions are stale.

Compare both fields before a mutation and record separate stale-precondition
gates. If visibility or branch is intentionally allowed to change, encode that
decision in the map and plan rather than silently ignoring the expectation.

### W07-W04-02 — Generated rename operations have no backup reference or backup gate (high/blocking)

The required delivery contract in specs/REPO_MIGRATION.md:17-21 calls for a
backup reference in every plan. build_plan at :585-625 emits preconditions,
verification, and rollback prose, but no backup_reference field and no backup
gate. The generated operation probe returned
generated_backup_reference False generated_backup_gate False.

The rollback section remains a decision record, not a recoverable backup of
prior metadata. Add a concrete immutable backup/metadata snapshot reference
and fail closed when it is absent before any authorized rename.

### W07-W04-03 — Optional 404s become false availability and incomplete state (high/blocking)

GhApi.request at :111-137 maps any error containing 404 or Not Found to None.
_list at :145-151 turns None into an empty list, while observe_repo at
:207-234,271-288 reports pages_available and workflow_read_available from the
absence of a transport error and _action_consumers at :159-181 returns
([], True, None) when the search result is None. A fake observer returning None
for every optional endpoint produced:

  {'pages_available': True, 'workflow_read_available': True,
   'action_consumers_known': True, 'active_runs': [], 'open_pull_requests': []}

The same source consequently looks clear when Pages, workflow/run inventory,
and hosted-Action consumer search were actually unreadable. Treat a 404 as
endpoint-specific unknown unless the endpoint contract proves absence, and
retain completeness/error state in the plan. This is especially important for
the “all gates observed” language in docs/MIGRATION_OPERATIONS.md:25-31,47-62.

### W07-W04-04 — Active-work inventory omits queued/waiting jobs and complete pagination (high)

observe_repo at :218-225 asks only for
actions/runs?status=in_progress&per_page=100; queued and waiting runs are not
queried. Pulls and code search also use a single per_page=100 request with no
page traversal or completeness marker. A repository with a queued deployment
or more than 100 relevant rows can therefore be evaluated from an incomplete
inventory. Query every blocking state and prove pagination completion, or
return an explicit unknown blocker.

### W07-W04-05 — Transport failures are marked failed and retried as ordinary operations (high)

_apply_plan at :817-832 persists a pending row, but classifies an ApiError as
unknown only when its text contains timeout or request failed; a connection
reset by peer, 5xx, or equivalent post-send transport failure is marked
failed. The ordinary next invocation only blocks prior statuses in unknown,
unknown_waiting_for_reconciliation, or verification_failed at
:772-781, so it sends another PATCH. An exact fake-client probe reported
transport_retry_statuses ['failed', 'failed'] patch_calls 2 for a connection
reset.

Classify every ambiguous post-request transport outcome as unknown and require
the same explicit reconciliation path before retrying. A client cannot know
whether GitHub committed a request that ended in a reset or 5xx.

### W07-W04-06 — An unknown operation does not halt the operation set (high)

The exception branch at migration/tooling/github_migration.py:824-832 persists
the unknown row and then continues the loop. A two-operation fake plan with a
timeout produced two PATCH calls and statuses ['unknown', 'unknown'].
docs/MIGRATION_OPERATIONS.md:120-124 says a pending operation must be
reconciled before continuing; enforce that boundary by stopping the set after
the first unknown, verification failure, or unresolved state.

### W07-W04-07 — Prior applied receipts are trusted without fresh state (high)

_apply_plan at :744-775 checks only the receipt schema and plan digest, then
returns any prior applied, already_satisfied, or skipped row without calling
fresh_operation_state. After a successful fake rename, mutating the target ID
to 999 still made the second call return applied with one PATCH total:
stale_applied_receipt applied target_id_after_mutation 999 patch_calls 1.

Bind a completed row to its full observed post-state and re-read the target
before accepting it as already applied. Validate every receipt operation ID,
source/target identity, request/response and verification row; do not treat a
plan digest alone as receipt integrity. A forged or stale applied receipt must
not be a success oracle.

### W07-W04-08 — Approval actor and repository owner are not bound to authority scope (high)

load_approval at :675-690 requires only a nonempty approved_by string and the
plan/operation subset. build_plan at :573-580 accepts a map-supplied owner,
and the apply path does not compare that owner with DEFAULT_OWNER or bind the
approval to client.current_user(). A fake plan with
approved_by=arbitrary-operator and owner OtherOrg was accepted and called
rename_repo('OtherOrg', 'source', 'target').

Bind approval to the authenticated actor, permitted organization/repository
scope, and the exact stable IDs in the source snapshot. Reject map owners
outside the intended scope unless a separately reviewed scope explicitly
authorizes them.

### W07-W04-09 — The lock is per receipt path rather than per operation set (medium/high)

apply_plan at :702-721 creates only
receipt_path.with_name(receipt_path.name + .lock). With receipt-one.json.lock
present, a second receipt path still renamed the same fake repository:
different_receipt_lock_allows_patch applied patch_calls 1 first_lock_exists True.
The runbook documents this limitation at docs/MIGRATION_OPERATIONS.md:120-124,
but separate receipt paths remain a cross-process race unless a root-owned
operation-set lock or repository lock is used.

### W07-W04-10 — Source snapshots and plans lack immutable snapshot provenance (medium)

load_snapshot at :544-550 checks only that JSON contains a repositories list.
build_plan at :581-605,648-650 records whether the snapshot was provided and
copies selected fields, but does not bind a snapshot digest, schema revision,
or duplicate stable-identity check to the plan. The plan is therefore
reviewable text with weak provenance if the snapshot file is replaced. Include
the exact snapshot bytes/digest and validate unique owner/name/stable-ID rows
before deriving preconditions.

## Helper findings

### W07-W02-01 — String model_verified values pass as true (high gate risk)

scripts/agent_ledger.py:42-52 tests if n.get('model_verified') and later
computes all_models_verified with bool(nodes) and all(...). A valid native
fixture with every value changed to the string 'false' returned
all_models_verified True. Require an actual boolean (is True/is False) before
treating the ledger as a model-identity gate. The script's own observation
limitation remains valid, but truthiness must not strengthen a claim.

### W07-W02-02 — Art alias evidence is presence-only (medium/high provenance)

scripts/art_policy.py:64-65 requires only a truthy
snapshot_alias_evidence_reference when a dated image-model ID is used. It does
not resolve, hash, schema-check, or trust that reference. A record with
image_model_observed=gpt-image-2-2026-04-21 and
snapshot_alias_evidence_reference=fake-not-a-file returned an empty error list.
Require a bounded, symlink-safe file and digest or clearly label the reference
as an unverified pointer.

### W07-W02-03 — Extra delivered exports are ignored (medium/high)

scripts/validate_assets.py:93-132 builds an export map and validates only
the exports listed in each planned asset. It never rejects an unplanned export.
Adding an unlisted extra.png with a bad digest, missing generation record, and
prohibited derivation to a valid manifest still returned []. Require the
delivered export set to equal the planned set (including paths and case-folded
uniqueness) before validating each row.

### W07-W02-04 — Runtime snapshot accepts duplicate IDs and emits raw paths (high privacy/provenance)

scripts/runtime_snapshot.py:24-57 stores rows in a dictionary keyed by
record['id'], so later duplicate rows silently replace earlier metadata. It
trusts the source-supplied parent/depth and emits agent_path unchanged. A
temporary database with two child rows returned the last row's
{'depth': 99, 'agent_path': '/private/secret'}. Reject duplicate IDs, validate
ancestry/depth against the observed tree, and redact or explicitly classify
private path fields before any report consumes this output.

### W07-W02-05 — Delivery exclusions miss common secret files (medium)

scripts/build_delivery.py:17-18 excludes .env only case-sensitively and has no
rules for .npmrc or common credential filenames. A temporary archive included
source/.ENV, source/.npmrc, and source/credentials.json, each containing a
token. The script correctly says at :31 that patterns are not a secret scanner;
the helper still needs a case-insensitive denylist plus a content/manifest
review gate before an archive can be treated as deliverable.

### W07-W02-06 — Content sync trusts a mutable prior receipt and is not transactional (medium/high)

scripts/sync_content.py:62-68 loads the prior receipt and uses its listed
hashes without authenticating the receipt or binding it to canonical bytes.
sync at :93-112 applies several file replacements before atomically writing the
receipt, with no lock or rollback. In a temporary consumer, editing the copy
to operator edit and changing only the receipt hash allowed a new pinned source
to overwrite it: sync_forged_receipt_overwrite ['assets/brand/tokens.css'].
Protect and authenticate the receipt, lock the consumer operation, and stage a
complete multi-file transaction before replacing any destination.

### W07-W02-07 — Blocked handoffs may omit a blocker or reason (medium)

scripts/render_handoff.py:39-48 requires a reason for
not_applicable_with_reason but has no corresponding requirement for a blocked
row. The output fallback at :54-56 prints “none recorded; state is
authoritative”. A temporary blocked requirement with both blocker and reason
removed rendered successfully and contained that fallback. Require a nonempty
blocker/reason for every blocked state.

### W07-W02-08 — Package validation ignores unlisted files and is schema-light (medium)

scripts/validate_package.py:114-120 verifies only paths listed by
MANIFEST.json; it does not reject or inventory other deliverable files and
load at :9-10 uses ordinary JSON parsing without schema validation. A clean
git archive with an added unlisted.json returned
package_unlisted_file_errors []. Make the manifest an exact safe-tree inventory,
reject duplicate/unknown entries, and use strict schema parsing for package
control files.

### W07-W02-09 — Browser automated pass omits key semantic and interaction gates (medium)

scripts/browser_review.mjs:62-95 records title, language, main/h1 counts,
reduced-motion state, and ten keyboard samples, but automatedPass at line 95
checks none of those values. It checks status, overflow, images, placeholder
links, axe violations, request failures, console errors, and external requests.
A page can therefore be reported as automatically passing while missing a
heading/landmark, while focus samples are invisible, or while normal-motion
behavior and controls remain untested. The manual-review limitation at
:109-114 is accurate but does not prevent a consumer from treating
automatedPass: true as a complete accessibility or interaction result. Turn
the recorded semantic/focus assertions into explicit failure conditions and
keep normal-motion, zoom, and control behavior in the manual gate.

## Runbook and evidence consistency

specs/REPO_MIGRATION.md:9-21 and docs/MIGRATION_OPERATIONS.md:47-62,103-108
describe complete inventory, backup, all-gate observation, and read-after-write
requirements. The implementation has the positive stable-ID/head/collision,
protected-configuration, Pages, hosted-Action, active-work, approval, and
read-after-write checks, but the findings above leave those claims incomplete.

execution/w04-implementation.json:2-43 still labels the implementation source
as 4d09cd40fb077cc3364197a1cb1056950b980361, even though the current W04
migration/helper implementation is carried into the later 5b root. Its
19-test count is useful historical evidence, but the stale source revision and
independent_reviewer: null prevent it from serving as an exact-head
independent receipt. Update it only through the root coordination process.

## Review disposition

The companion presentation diffs are bounded, cleanly formatted, and preserve
the documented runtime and evidence caveats. The migration and helper tests
are green, but they do not cover the negative cases above. W04 migration
mutation, helper-derived evidence gates, companion commits, GitHub settings,
and publication remain unapproved pending remediation or an explicit
operator-trust decision. This report grants no rename, merge, deployment, or
notification authority.
