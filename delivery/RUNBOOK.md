# Review and continuation runbook

This is a local private engineering and partial-artwork handoff. Read `FINAL_REPORT.md` and the requirement evidence before operating any release gate. GitHub draft PRs are the reviewable source changes; none is merged or deployed by this assignment.

## Canonical package

Use a clean checkout of the exact reviewed brand revision. Install the pinned Python dependencies into a local virtual environment, then run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_package.py
.venv/bin/python -m unittest discover -s tests -v
```

Read the external `RECEIPT.json` beside the current ZIP for final source and test results; `execution/reviews/final-local-checks.json` retains the earlier engineering-only test scope. The suite checks local contracts, negative cases, package integrity, migration fake clients, publication boundaries, and marketing definitions. It does not establish gameplay, a provider execution, deployment, or real campaign measurements.

## Website and companion sources

`github/website-pull-request.json` identifies the website branch and exact head. The website uses its committed Composer lockfile and PHP 8.3; run `php vendor/bin/phpunit` in that checkout. The existing public draft PR has 29 tests and 111 assertions. The private artwork candidate extends this to 30 tests and 114 assertions; its exact local revision and Git bundle are recorded in `github/website-art-candidate.json`. Real local HTTP journeys use a private temporary store and mail sink: `scripts/review_subscription_http.py --help` documents the harness. Do not target production subscribers or SMTP. The earlier public-draft review includes a 110-state route/theme matrix and zoom/motion/interaction checks. The private artwork candidate has 30 HTTP checks, a 48-state browser matrix, six normal-motion states and nine focused fallback states, separately scoped in `execution/reviews/` and `delivery/WEBSITE_CANDIDATE.md`.

`github/companion-commits.json` enumerates ten reviewed draft PRs, exact source revisions, changed paths, and SHA-256 values. `execution/reviews/companion-validation-001.json` records commands and qualifications. Six Rust README policy checks and two byte-exact quickstart recipes passed; Pages passed five Node tests and its local viewport/theme review. Watchdog has no Cargo manifest at the reviewed bootstrap source. Observability deployment was not checked because Docker is unavailable. Neither limitation is hidden by the presentation review.

The twelve private GitHub artwork candidates are indexed in `github-art-candidates/github-art-candidates-map.json`. Follow `github-art-candidates/README.md` to restore a candidate in a fresh clone and verify its exact prerequisite, head, bundle digest and copied PNG hashes. The thirteen social preview proposals are in `../github/social-preview-candidates.json`. These local candidates have not been applied to public repositories or live settings.

Before any merge, re-read each actual remote default and PR head, checks, mergeability, and current owner work. Reconcile any change in an isolated checkout and obtain review of the resulting diff. Never force-push or modify unrelated runtime/map/sync PRs.

## Artwork and native hierarchy

The current user-authorized route is recorded in `art/root-generation-authorization.json`: root may generate with the available image tool, while the author model and image backend stay unknown. `brand/ART_ACCESS.md` and `brand/asset-manifest.json` give actual per-family review states. The package retains 123 generated sources, including superseded attempts, exact prompts and generation observations. All 115 planned exports exist: 112 raster images, one WebM and two functional HTML files. Generated artwork is never gameplay evidence.

The full inventory remains 72 families and 115 exports. All 115 export paths now exist; 70 families pass scoped acceptance and two still require approved footage integration or real challenge approval. Image generation resumed successfully after the historical service limit. Read `brand/remaining-artwork.json` for the current gates. Preserve source bytes and generation IDs, use a new prompt/attempt for creative revisions, then run mechanical exports and obtain independent source-use, visual and export review. `generated_original_reviewed` records that bounded source-use review; it is not legal/trademark clearance or public distribution authority.

The original native depth-three hierarchy is still a separate unmet requirement. Current descendants report no callable child-spawn tools even after the proactive delegation setting changed. Do not invent ancestry or replace the required chain with role names.

To refresh local artwork views after an accepted change:

```sh
python3 scripts/export_root_art.py
python3 scripts/build_press_index.py
python3 scripts/build_art_catalog.py
```

The press builder requires complete reviewed source lineage and a digest-bound approval independently enrolled in the protected `config/press-authorities.json`. That registry is empty. Neither an image-generation request nor a verified asset status issues publication authority.

## Publication and measurement

`docs/PUBLISHING.md` describes the implemented offline publisher. The checked-in synthetic fixture is for local rendering tests only and fails production publication. `execution/authentic-report-intake.json` lists sanitized historical report-only intake and missing approval/rights evidence. Keep real trajectories and captures private. Both trusted authority registries are empty. A real public record needs exact content/renderer/asset digests, URI allowlists, rights, consent, and an independently issued, enrolled approval. No public video, replay package, or timeline may be invented from report-only evidence.

The marketing kit contains twelve episode drafts, twenty-four clip drafts, six article outlines, and seventy-two release gates. Its event/metric definitions are implemented, with outcomes still unobserved. Activate analytics or campaigns only under exact authority and consent configuration; no twelve-week outcome can be inferred from local tests.

## Migration, settings, deployment, and rollback

The latest `migration/plan.json` is a dated read-only observation, not authority to rename. Rebuild it immediately before an authorized operation with `python3 migration/tooling/github_migration.py plan --map migration/input-map.json --output NEW_PLAN.json`. Review stable IDs, fresh heads, open work, Pages and Actions consumers, protected settings, backup references, actor scope, and every failed gate. Read `docs/MIGRATION_OPERATIONS.md` for exact approval binding and idempotent retry. Map work remains deferred. Do not treat an unavailable Pages endpoint as proven absence.

`github/settings-manifest.json` contains thirteen concrete description/topic/homepage proposals and the six-pin checklist. These settings have not been applied. No production branch or document root is confirmed for deployment, and unrelated host changes/subscriber data must be preserved. Deployment needs an exact target, changed-file backup, rollback destination, authority, and served-version/form verification. Follow `docs/ROLLBACK.md`; a written rollback procedure is not a tested host restoration.

## Local archive

The final archive is created outside this source tree from the validated manifest with `scripts/build_delivery.py`, then independently inspected and rebuilt for byte equality. Its external SHA-256 receipt binds the source manifest; it cannot be embedded into itself. The archive is private audit material under `PRIVACY_SCOPE.md`. It contains all planned export files, with 70 of 72 families accepted and no public distribution approvals; it is not a complete visual release bundle. Public export requires a separate sanitized projection and exact publication approval.
