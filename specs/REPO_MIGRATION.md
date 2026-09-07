# Repository presentation and migration engineering

## Desired map

Use data/repository-map.json as the exact target map. The hub is ascension-brand-overhaul, the flagship is the current sts2-harness renamed to ascension, and the website is the current aiascension.tech renamed to website. Retain .github and AI-Ascension.github.io, the gateway/protocol names, and the explicit ascension-watchdog identity.

The proposed sts2-map rename is deferred while an active assignment requires ascension-map-visualizer. Resolve that conflict explicitly with the owner and the current job, not by breaking the ongoing checkout. A display-name update can proceed while the mechanical rename remains gated. Do not pause runtime work merely to make the naming table look uniform.

## Preflight per repository

Record the stable numeric repository ID, owner, current/canonical name, permissions, visibility, default and deployment branches, exact relevant heads, open PRs, rulesets, Pages configuration, active jobs, package registries, hosted Actions, submodules, Git dependencies, and external callers known to the project. If a connector cannot read protected administrative fields, record the access limit instead of assuming defaults.

Search for old owner/name references in workflow `uses`, raw asset links, badges, markdown, install recipes, scripts, service files, environment examples, deploy remotes, Cargo/package metadata, documentation anchors, OCI labels, and downloadable release names. Classify each as mutable presentation, runtime identity, immutable historical evidence, or third-party caller. Only the first category is broadly eligible for initial replacement.

GitHub's official rename documentation distinguishes ordinary redirects from project-site and hosted-Action exceptions. Recheck it before apply (SRC-06). Do not assume all raw, registry, API, and Pages references will keep working; test relevant callers. Never create a new repository under a retired name to “preserve” an ordinary redirect. If a repository hosts an Action, inventory consumers and execute a separately reviewed compatibility strategy before cutover.

## Delivery mechanism

Build a plan-first tool using the actually available GitHub connector/API/CLI schema. No invented rename endpoint or unsupported flag. Dry run is the default. Plan records expected stable ID, source/target name, current-head precondition, authorized action, caller inventory, backup reference, verification probes, and rollback decision. Re-read target state immediately before apply. Block a name collision, stale identity, changed protected configuration, missing approval, or uncoordinated active work.

Idempotency: already-renamed expected ID is reported as already satisfied; a different repository at the target name is a hard conflict. Retrying never creates duplicates or claims success from a local config edit. Record requested operation, actual response, timestamp, operator authority, and observed post-state. Local `git remote set-url` is not a remote rename.

## Non-breaking source rollout

Update display names and sources first, using aliases until cutover. Do not rename Rust package names, binary names, environment prefixes, .NET identities, protocol profiles, artifact digests, or historical fixtures in this brand pass. Such work requires a separate compatibility release if later justified.

Preserve or restore complete route-level historical Pages content. Keep the exact organization Pages repository name. Do not promise a 301 if the platform only serves a static page or canonical metadata; document the actual mechanism. Test historical anchors and fixture fetches, not just root homepages.

## GitHub presentation

The profile needs a plain-language headline, actual available result, Watch/Build links, current capability summary, four useful starting routes, and preserved policy/evidence links. The flagship README needs a product explanation, one representative approved visual, a verified quickstart, prerequisites, compatibility, examples, architecture, contribution path, and license. Component READMEs identify the canonical flagship and their own bounded responsibility. Use real CI/release badges only.

Descriptions and topics are settings, not markdown. Create a settings manifest with current/desired values and apply only when authorized. Pin the flagship and the most useful demonstrated integrations; do not imply a pin API exists if it does not. Provide an exact manual checklist where the available tool cannot perform the setting.

## Rollback

Preserve backups and exact prior metadata. Reverse a rename only after checking name availability and caller consequences; otherwise prefer a forward fix. Do not reverse metadata while leaving code references half-migrated. Distinguish source rollback, hosting rollback, and GitHub metadata rollback. Never rewrite history or alter old evidence to simplify rollback.

## Mandatory artwork source

All new artwork, including promotional images, exported diagrams, card artwork, icons, and creative revisions, follows `art/ASTRA_GPT_IMAGE_2_POLICY.md`: an actual `gpt-6-astra` author writes each final prompt and `gpt-image-2` generates the art. Functional HTML/CSS/data and approved real evidence are separate. Runtime serving uses already approved images with no implicit model calls. Missing art-model access blocks that asset, never authorizes code-drawn or reused-art substitutions.
