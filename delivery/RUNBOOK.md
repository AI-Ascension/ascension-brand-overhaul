# Review and continuation runbook

This is a local private engineering/text handoff. Read `FINAL_REPORT.md` and the requirement evidence before operating any release gate. GitHub draft PRs are the reviewable source changes; none is merged or deployed by this assignment.

## Canonical package

Use a clean checkout of the exact reviewed brand revision. Install the pinned Python dependencies into a local virtual environment, then run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_package.py
.venv/bin/python -m unittest discover -s tests -v
```

Read `execution/reviews/final-local-checks.json` for the tested source revision and results. The suite checks local contracts, negative cases, package integrity, migration fake clients, publication boundaries, and marketing definitions. It does not establish gameplay, a provider execution, deployment, or real campaign measurements.

## Website and companion sources

`github/website-pull-request.json` identifies the website branch and exact head. The website uses its committed Composer lockfile and PHP 8.3; run `php vendor/bin/phpunit` in that checkout. The completed local suite has 29 tests and 111 assertions. Real local HTTP journeys use a private temporary store and mail sink: `scripts/review_subscription_http.py --help` documents the harness. Do not target production subscribers or SMTP. The 30 HTTP checks, 110-state route/theme matrix, zoom/motion/interaction review, and final homepage recheck are separately scoped in `execution/reviews/`.

`github/companion-commits.json` enumerates ten reviewed draft PRs, exact source revisions, changed paths, and SHA-256 values. `execution/reviews/companion-validation-001.json` records commands and qualifications. Six Rust README policy checks and two byte-exact quickstart recipes passed; Pages passed five Node tests and its local viewport/theme review. Watchdog has no Cargo manifest at the reviewed bootstrap source. Observability deployment was not checked because Docker is unavailable. Neither limitation is hidden by the presentation review.

Before any merge, re-read each actual remote default and PR head, checks, mergeability, and current owner work. Reconcile any change in an isolated checkout and obtain review of the resulting diff. Never force-push or modify unrelated runtime/map/sync PRs.

## Artwork and native hierarchy

`execution/art-model-attestation.json` names every blocked job; `brand/asset-manifest.json` records zero approved exports. All 72 artwork families and 115 exports require actual native depth-3 Astra/max authors and an attested gpt-image-2 route. Restore those capabilities, then follow `art/ASTRA_GPT_IMAGE_2_POLICY.md` and the native role contract. Do not substitute an image backend, fake ancestry, hand-drawn artwork, or old-brand assets. The current seven observed leads are depth 1 only; retained threads count against the 250-descendant budget until native closure is established.

## Publication and measurement

`docs/PUBLISHING.md` describes the implemented offline publisher. The checked-in synthetic fixture is for local rendering tests only and fails production publication. `execution/authentic-report-intake.json` lists sanitized historical report-only intake and missing approval/rights evidence. Keep real trajectories and captures private. Both trusted authority registries are empty. A real public record needs exact content/renderer/asset digests, URI allowlists, rights, consent, and an independently issued, enrolled approval. No public video, replay package, or timeline may be invented from report-only evidence.

The marketing kit contains twelve episode drafts, twenty-four clip drafts, six article outlines, and seventy-two release gates. Its event/metric definitions are implemented, with outcomes still unobserved. Activate analytics or campaigns only under exact authority and consent configuration; no twelve-week outcome can be inferred from local tests.

## Migration, settings, deployment, and rollback

The latest `migration/plan.json` is a dated read-only observation, not authority to rename. Rebuild it immediately before an authorized operation with `python3 migration/tooling/github_migration.py plan --map migration/input-map.json --output NEW_PLAN.json`. Review stable IDs, fresh heads, open work, Pages and Actions consumers, protected settings, backup references, actor scope, and every failed gate. Read `docs/MIGRATION_OPERATIONS.md` for exact approval binding and idempotent retry. Map work remains deferred. Do not treat an unavailable Pages endpoint as proven absence.

`github/settings-manifest.json` contains thirteen concrete description/topic/homepage proposals and the six-pin checklist. These settings have not been applied. No production branch or document root is confirmed for deployment, and unrelated host changes/subscriber data must be preserved. Deployment needs an exact target, changed-file backup, rollback destination, authority, and served-version/form verification. Follow `docs/ROLLBACK.md`; a written rollback procedure is not a tested host restoration.

## Local archive

The final archive is created outside this source tree from the validated manifest with `scripts/build_delivery.py`, then independently inspected and rebuilt for byte equality. Its external SHA-256 receipt binds the source manifest; it cannot be embedded into itself. The archive is private audit material under `PRIVACY_SCOPE.md`. It contains no approved generated art and is not a complete visual release bundle. Public export requires a separate sanitized projection and exact publication approval.
