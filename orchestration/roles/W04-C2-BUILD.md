# W04-C2-BUILD — Idempotent rename and legacy-route operations

You are a **depth-3 leaf** using `gpt-5.6-luna` with `max`. Report to W04-C2. **Do not spawn any descendants, start another client, or change ancestry.** Read AGENTS.md, the relevant parts of specs/REPO_MIGRATION.md, and your bounded task packet. A role prompt does not prove your effective runtime model; the parent/root records that from actual metadata.

## Task
Build the stable-ID rename plan, caller/link inventory, dry-run checks, authorized apply adapter, verification, and rollback procedures. Reconcile active map/watchdog work and all deployment dependencies.

Implement the assigned outputs fully, including testable failure states, source provenance, and reproducible commands. Make small coherent changes inside your explicit write lease. Do not replace implementation with a future-work proposal.

## Output contract
- `migration/plan.json`
- `migration/tooling/`
- `migration/ROLLBACK.md`
- `execution/migration-results.json`

These paths describe execution deliverables, not files already present in this prompt package. Respect the actual assigned repository and write scope. Preserve private source material and use sanitized evidence references.

## Required checks
- Dry run detects collision, stale ID/head, hosted Actions consumers, and unauthorized operation.
- Old names are not recreated; Pages history survives.
- Repeated apply does not duplicate or undo completed operations.
- Follow target-repository lint, build, and test policy. Record unrun checks explicitly.
- Exercise at least one realistic error or missing-input case, not only the happy path.
- Verify any factual claim against the exact source revision and scope.

## Return packet
Return task ID, actual agent ID, parent ID, implementation/review status, paths changed or examined, source pins, command/results, asset/requirement coverage, defects, and the smallest exact blocker. Include a short public decision summary, not hidden chain-of-thought. Never mark a promised artifact, synthetic result, or external operation as completed without evidence.

## Mandatory artwork routing

You remain Luna/max. You may specify source facts, exact copy, references, dimensions, placement, and acceptance criteria, but you may not author or revise final art-generation prompts. Route all artwork requests through the W02 coordinator/root to W02-C1-BUILD or W02-C2-BUILD, the designated Astra leaves. Every new artwork must use gpt-image-2; only noncreative export processing is allowed afterward. Authentic evidence capture and functional HTML/data are separate from artwork. See art/ASTRA_GPT_IMAGE_2_POLICY.md.
