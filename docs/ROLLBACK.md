# Rollback boundaries and procedure

No production deployment, repository rename, merge or campaign send has occurred in this execution. A rollback destination for a future live operation must be prepared and recorded before that operation. This document does not authorize a live restore.

## Local implementation

Keep unrelated dirty checkouts intact. Work exists on isolated implementation branches and in the canonical repository. To revise a committed change, create a focused follow-up commit after reviewing the diff. Do not reset, clean, stash, broadly stage or force-push shared work. Restore only explicitly owned files from a verified prior revision when their current bytes match the expected implementation digest; otherwise reconcile the conflicting edit first.

For a canonical content sync, retain the old consumer receipt and exact old Git revision. A prior sync plan can restore its managed content if current consumer bytes still match the latest receipt. Run the helper’s dry run before apply. Files introduced by a newer plan require an explicit reviewed removal: the helper intentionally rejects a plan omitting previously managed paths. Do not delete those files automatically or overwrite intervening consumer edits.

## Website deployment

Before an approved deployment, capture the actual served file inventory and hashes plus a protected backup of the specific document-root files being changed. Record the host, document root, deployment revision, rollback destination and approval scope without copying secrets into this repository. The current host has unrelated dirty content, so repository HEAD alone is not an adequate backup. Preserve existing subscriber data, mail credentials and other hosted domains.

If the deployed routes, subscription safety, privacy behavior or served revision fail the approved smoke checks, stop further rollout. Within valid restore authority, restore only the backed-up changed files after checking for intervening edits. Restore mutable subscriber data only through a separately reviewed recovery procedure; reverting application files must not discard new confirmations or unsubscribe requests.

Verify the restored served HTML, expected route status, assets, headers and privacy behavior. Check subscription paths through an isolated test recipient or approved sink, never a campaign send to real subscribers. Record hashes and timestamps of both the failed build and restored build. Hosting-injected scripts may survive a code rollback and require a separate hosting-setting operation.

## Repository presentation and names

Revert presentation changes through ordinary reviewed commits without changing runtime identifiers or historical evidence. Follow `docs/MIGRATION_OPERATIONS.md` for the integrated migration tooling. Before any reverse rename, re-query the stable repository ID, current name, default head, destination availability and current approval. A reverse rename is a new live operation, not a harmless local undo. Recheck redirects, Pages routes and Actions callers independently; a successful API response does not prove those consumers work. Never create placeholders at retired names.

## Public reports and campaign material

For an incorrect staged report, stop its publication and invalidate any approval whose digest no longer matches. Preserve the historical source pointer and correction record. For already public material, use the authorized correction or withdrawal path and verify the actual destination afterward. Do not rewrite private or historical evidence to match marketing copy. Sent emails and third-party reposts cannot be reliably recalled; use a dated correction under explicit messaging authority.

## Recovery receipt

For each actual recovery, record the triggering failure, exact before/after revisions and hashes, approved scope, protected backup reference, commands or API operation IDs, exit results, reviewer, served postconditions and unresolved effects. An unexecuted rollback procedure is preparation, not evidence of a tested production restore.
