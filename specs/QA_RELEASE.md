# Quality gates, independent review, and release evidence

## Gate sequence

G0: current sources and authority inventoried. G1: real runtime/model/depth attestation. G2: interfaces, tokens, copy, art map, and publication contracts coherent. G3: working local vertical slice. G4: all local implementation and mandatory assets delivered. G5: independent security/privacy/visual/browser/integration review. G6: authorized migration/deployment preflight. G7: actual approved rollout and verified smoke results. G8: handoff and operation state.

A blocked G1 prevents claiming the requested orchestration was achieved, not completion of independent authorized coding. Missing rights or gameplay footage blocks corresponding publication/evidence assets. Missing deployment authority blocks live rollout, not a complete tested implementation. Preserve all distinctions in the final report.

## Test families

1. Package/contract: schema validity, cross-reference integrity, source manifest digests, copy/capability consistency, required assets, and safe output paths.
2. Functional website: every route and empty/error state, media CTA behavior, local guess/reveal, complete mobile interaction, and post-migration links.
3. Subscription: validation, duplicate/confirmation/unsubscribe, rate limits, concurrency, storage failure, mail failure, and no unauthorized production sends.
4. Publication: private/synthetic/forced data rejected, changed digest invalidates approval, bounded inputs, safe HTML/SVG/URLs/paths, no live game authority, deterministic render.
5. Visual/accessibility: actual renders, keyboard, screen reader where available, contrast, zoom, light/dark, reduced motion, captions, small logo/thumbnail and real mobile crops. Automated checks do not replace manual review.
6. Migration: expected stable IDs, aliases, stale heads, name collision, Actions caller exception, Pages route preservation, retry idempotency, and rollback feasibility.
7. Orchestration: real native parent chain, correct settings, no fourth descendant level, all open parents counted, no budget deadlock, reviewer independence, and exclusive write ownership.
8. Security/rights: no credentials, hidden private artifacts, unsafe workflows, bundled fonts, unauthorized game assets, unsupported endorsement, or arbitrary-fetch rendering.
9. Marketing: asset links, source-qualified factual copy, content counts, measured versus planned labels, correct live indicators, and no fake testimonials/metrics.

## Evidence records

For every REQ ID keep the exact input source and revision, command/procedure, environment/tool versions, result/exit status, output hash or approved screenshot reference, reviewer, timestamp, and blockers. Use explicit not_run/skipped/blocked states. Do not summarize a missing host test as a pass because unit tests succeeded. Independent reviewers inspect actual outputs, not the root's confidence.

## Visual review procedure

Render all core pages in agreed viewport/theme states. Open them and record defects with viewport and component. Inspect every export at intended display size; a 4K logo can fail at 24 px. Verify factual labels, timeline alignment, chart values, cropping, legibility, focus, hover, invalid data, and no broken image/font requests. Font files stay outside handoff archives even when the live site uses existing licensed self-hosted files.

## Release and rollback

Freeze reviewed source revisions and art manifest. Re-run checks after integration, not only on isolated branches. Keep draft PR, merged commit, and deployed build separate. Production deploys require explicit authority and a known backup/rollback destination. Never claim a successful deploy from an upload command alone: verify the served version and intended route/form behavior. Do not send campaign emails as a smoke test to real subscribers.

Use minimal privileges, pin third-party CI actions to reviewed immutable references after checking them, and avoid giving publishing secrets to untrusted pull requests. Document which actions/settings the available connector cannot change. Provide an exact manual step only after the actual capability is checked; do not invent API support.

## Final acceptance report

Summarize completed code, visual assets, reviewed sources, companion PRs/commits, model/depth evidence, tests, rights/approval status, migration receipts, deployed routes, and the delivered content kit. Add a table of every blocked requirement/asset with the exact external dependency and all completed preparatory work. Distinguish a local implementation handoff from a live public launch and from ninety days of actual operation.

The final artifact package must be reproducibly assembled with SHA-256 hashes, Astra prompts, generation/edit history and original generated masters, export manifests, and clear licensing boundaries. No hidden TODO, placeholder button, synthetic statistic, or unexecuted command may masquerade as finished production work.

## Mandatory artwork source

All new artwork, including promotional images, exported diagrams, card artwork, icons, and creative revisions, follows `art/ASTRA_GPT_IMAGE_2_POLICY.md`: an actual `gpt-6-astra` author writes each final prompt and `gpt-image-2` generates the art. Functional HTML/CSS/data and approved real evidence are separate. Runtime serving uses already approved images with no implicit model calls. Missing art-model access blocks that asset, never authorizes code-drawn or reused-art substitutions.
