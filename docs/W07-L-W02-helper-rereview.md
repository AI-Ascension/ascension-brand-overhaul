# W07-L independent re-review: W02 helper repairs

Reviewer: W03 lead, independent of the helper implementation. Reviewed source
revision `0e03d97bc6af6b7622d33d830bdde1eef1c2b1d8` from a read-only archive.
The review created no native/provider records, remote operation, deployment,
artwork, or live write.

## Verification

- `python3 -m unittest discover -s tests -v`: **170 tests passed** in 16.526
  seconds at the frozen source revision.
- `python3 scripts/validate_package.py`: **PASS**.
- The focused W02/helper set (`test_art_policy`, `test_runtime_snapshot`,
  `test_delivery_privacy`, `test_handoff`, `test_package_inventory`, and
  `test_content_sync`) ran **48 tests passed** in 4.359 seconds.
- A positive browser fixture completed all ten reduced-motion viewport/theme
  states with `automatedPass: true`. A negative fixture missing `h1` and
  keyboard focus treatment completed all ten states with runner exit 1,
  `semanticPass: false`, and `sampledKeyboardPass: false`. The runner source
  hash at review was SHA-256
  `4ca3b19f8911ada297d071995484a6579e7e042708b35f82c0a6a5aa76553353`.

## Finding disposition

| Finding | Disposition and evidence |
| --- | --- |
| W07-W02-01 | **Resolved.** `scripts/agent_ledger.py:42-54` requires a real boolean and computes `all_models_verified` only from `is True`; the existing test rejects string and numeric values. |
| W07-W02-02 | **Resolved.** `scripts/art_policy.py:24-77` uses bounded, regular-file, symlink-safe, SHA-256-checked alias evidence, rejects duplicate JSON members, requires the exact envelope and model pairing, and limits the source to approved HTTPS hosts. The dated-alias test covers missing, valid, and tampered evidence. |
| W07-W02-03 | **Resolved.** `scripts/validate_assets.py:93-100` requires the delivered export path set to equal the planned set and rejects duplicate and case-folded collisions. The extra and case-collision test passed. |
| W07-W02-04 | **Resolved.** `scripts/runtime_snapshot.py:24-65` rejects duplicate thread IDs and validates every selected depth against observed parent ancestry; `:29-30,74-75` removes raw agent paths and records the redaction boundary. The duplicate/depth and private-text tests passed. |
| W07-W02-05 | **Resolved at the declared filename boundary.** `scripts/package_inventory.py:8-68` supplies case-insensitive `.env*`, credential, key, certificate, font, dependency, and private-directory exclusions used by `build_delivery.py`. The privacy test and mixed-case secret/digest-gate test passed. |
| W07-W02-06 | **Resolved for the cooperative local sync contract.** `scripts/sync_content.py:95-155` binds the consumer receipt to protected canonical Git state, rejects receipt tampering and unrelated/deleted copies, and applies under an exclusive consumer lock. `scripts/content_sync_state.py:76-145` stages all bytes and backups, rolls back ordinary failures, and retains the lock/journal when concurrent edits prevent rollback. The focused suite passed; an independent probe rejected a forged receipt with the operator edit preserved, and six injected failures (writer calls 1–3, before and after replacement) restored the managed content, receipt, and authority and removed the lock. |
| W07-W02-07 | **Resolved.** `scripts/render_handoff.py:49-55` requires a nonempty string blocker or reason for blocked requirements and a nonempty blocker for blocked assets. The blocked requirement regression passed. |
| W07-W02-08 | **Resolved.** `scripts/package_inventory.py:14-108` performs strict duplicate-key parsing and exact safe-tree inventory, rejects unknown/missing/case-colliding entries, verifies byte counts and hashes, and binds `CHECKSUMS.sha256` to the manifest. `scripts/validate_package.py:11-116` uses that validator for package controls. The unlisted-file, duplicate-entry, duplicate-key, secret, and full package checks passed. |
| W07-W02-09 | **Resolved for the automated subset.** `scripts/browser_review.mjs:62-99` records and gates title, language, landmark, heading, requested reduced-motion state, and sampled visible focus indicators before setting `automatedPass`. Positive and negative ten-state fixture probes exercised both outcomes. Manual screenshots, complete keyboard traversal, normal motion, zoom, forms, and assistive-technology review remain separate gates as the script states. |

## Boundaries

The helper results are local consistency and safety evidence. They do not
attest native agent execution, provider-side model identity, generated artwork,
rights, publication, deployment, or a live service. The alias envelope is
bounded documentation rather than provider attestation. Archive filename and
directory exclusions are not a content secret scanner; the reviewed-manifest
digest is an operator review input. Content sync uses a cooperative lock and
leaves a journal for an interrupted or incomplete rollback; an operator must
reconcile that journal before removing the lock. Browser automation uses
reduced motion and sampled focus checks, with the remaining interaction and
visual gates still required.

## Disposition

All nine W07-W02 helper findings are addressed at the frozen source revision
with meaningful negative coverage. This is a **PASS for the local helper
repair re-review**. It grants no publication, rename, merge, deployment,
campaign, or production-acceptance authority.
