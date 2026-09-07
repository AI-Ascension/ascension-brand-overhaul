# Operator runbook

This is a local implementation handoff under construction, not a production release receipt. Start with `execution/ROOT_STATUS.md`, `execution/requirements-status.json`, and the exact reviewed revisions in the eventual companion commit map. The immutable input brief is preserved separately from execution status.

## Resume safely

1. Inspect `git status --short`, branch, HEAD, applicable repository policy, and current native agent state. Preserve unrelated changes; continue in the assigned isolated checkout.
2. Reconcile the root-owned private task, spawn, write-lease and approval records. A retained completed thread still consumes the project budget until native closure is established. Do not recreate work from an observation timeout.
3. Check exact source revisions and file digests before integration. Claim records describe their pinned source; refresh mutable repository heads before any external write.
4. Inspect pending review findings. Return implementation defects to their owner, then obtain a separate reviewer’s recheck. A package test cannot approve a website, host, gameplay run or artwork.

## Local verification

From the canonical repository, the following commands validate package contracts and helpers:

```sh
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate_package.py
python3 -m unittest discover -s tests
npm ci --ignore-scripts
npx playwright install chromium
```

Dependency installation and browser download require network access. Browser tools and caches are local development dependencies; delivery archives exclude them. `execution/toolchain.json` records the separately installed local PHP/Composer tools. Website PHPUnit checks must run in the website checkout against its lockfile, using the local mail sink rather than production subscribers or SMTP.

Run `node scripts/browser_review.mjs --base-url http://127.0.0.1:PORT --routes ROUTES.json --output NEW_DIRECTORY`, replacing the explicit arguments. The route manifest contains a `routes` array of `{ "id": "home", "path": "/", "status": 200 }` records; expected status may be 200 or 404. Use a new output directory in ignored private storage. Start a local site server with a dedicated process handle, inspect screenshots and interaction results, and stop that exact process after review. The runner covers five widths and two themes with reduced motion; manual keyboard, zoom, ordinary motion, form behavior and available assistive-technology checks remain separate evidence.

## Canonical content and evidence

`scripts/sync_content.py` reads allowlisted Git objects from a full immutable commit. Run a dry run first with `integration/website-content-plan.json` and the isolated website consumer. Review the changed-file list, then use `--apply` within the existing local implementation authority. Keep the consumer receipt with its copied files. It rejects unrelated edits and omitted previously managed paths. It does not approve artwork or publish content.

Public run inputs pass through the publication boundary and its independent review before staging as production content. Report-only, video and replay availability are separate states. A public historical report is not independent reproduction. Synthetic decisions remain in the local test lane; never promote them into a latest-run page or a public vote.

Private approvals, subscriber storage, raw captures, credentials and hidden reasoning remain outside the deliverable. Deployment hosting may inject resources absent from repository source: the baseline records an injected third-party traffic script. A future production privacy check must inspect served HTML and actual network requests, not only the checkout.

## Artwork and release gates

Every new creative asset requires the designated native depth-3 Astra author and verified gpt-image-2 generation path. Current blocked rows have no generated outputs or prompts. Do not substitute legacy artwork, stock images or code-drawn illustrations. After access is restored, follow the existing W02 ancestry, provenance and independent export review contract; do not flatten the role tree.

Before live work, freeze reviewed commits, complete applicable tests, prepare rollback destinations and record exact operation authority. Repository rename, merge, deployment, hosting/DNS change, private artifact publication and campaign sends require their own valid authority. Draft implementation PRs, merged changes and served production builds must remain distinct records. The current task has not performed those live operations.

## Handoff archive

Use `scripts/build_delivery.py SOURCE NEW_DESTINATION.zip` only after reviewing the source inventory. The destination must be outside the source and must not already exist. The helper emits the archive SHA-256 and excludes dependency trees, ignored private directories, font binaries and common credential extensions. Pattern exclusions are not a secret scanner: inspect the final archive listing and contents before sharing. Keep missing required art and unverified gates explicit in the final report, and compare two independently built archives when asserting reproducibility.

## Routine maintenance

For each release, refresh capability evidence, tested quickstart configuration, links, subscriber failure handling and reviewed publication records. Before each episode, verify its source-qualified claims and media availability. Record campaign observations only after the declared window has elapsed, with denominators and confounders. Correct inaccurate public material with a dated correction; retain historical source evidence. The ninety-day schedule is an operating plan, not a record of audience results.
