# Three-level Luna Max orchestration with Astra art-author exceptions

## Runtime preflight

Keep the root model. Request `gpt-5.6-luna` and `max` for ordinary descendants. W02-C1-BUILD and W02-C2-BUILD must instead request `gpt-6-astra` and `max`. Only these Astra leaves may author final artwork prompts; every creative result uses `gpt-image-2`. Check installed client version, trusted project configuration, custom-role overrides, provider model catalog, native spawn schema, and native permission controls. Record config paths and hashes without copying tokens or private environment values. A documentation example is a candidate, not effective-session proof.

`runtime-config.example.toml` contains currently documented candidate default settings. Explicit spawn overrides can supersede defaults, so inspect them. Do not add `max_depth`, feature flags, new hook schemas, or CLI arguments unless the installed schema explicitly supports them. If there is a supported native depth cap, use it; also enforce the project depth through a root-owned ancestry ledger and leaf tool restrictions. A text instruction is not a hard runtime fence.

First perform one useful bounded inspection task along root → W01 lead → W01 coordinator → Luna leaf. Then verify root → W02 lead → W02 coordinator → Astra art-author leaf with a substantive bounded art task. Collect native IDs, parent IDs, requested configuration, accepted configuration, observed model and effort, and the evidence location. Missing observed metadata is `unverified`, not failure or proof of a different model. If native nesting is blocked, do not open other clients or reset ancestry to bypass it. Continue independent work and make the capability limitation explicit.

## Scheduling

The 49 descendants in roles.json are a catalog to execute over multiple waves, not concurrent fan-out. Global budget is at most 250 open descendants, subject to stricter actual limits. Count paused/waiting lead and coordinator threads. Before each spawn reserve a slot in the root ledger; reconcile it with native thread state. A reservation cannot be released merely because an agent is waiting.

A safe active pattern is two leads + two coordinators + four leaf workers/reviewers = eight open descendants, leaving headroom for integration review. Another is one lead + two coordinators + four leaves = seven. Run reviews after implementers return when slots are scarce. Close completed threads before spawning replacements. Failed or expired threads retain history and consume a slot until native closure is established. Never use all slots for parents waiting for unspawned children.

Read waves.json as dependencies, not parallel start times. Discovery and interface contracts precede art exports and page integration. Workstream 07 can define tests early, then performs final independent reviews once implementation is frozen. Roles may be reopened as new native threads with new IDs; preserve role identity and record the new parent chain.

## Task packet and handoff

Every task needs: task ID, role ID, actual parent ID, depth, source snapshot and input hashes, objective, allowed read/write paths, forbidden paths, dependencies, expected outputs, test plan, acceptance criteria, bounded resource budget, and result destination. Use task.schema.json. Do not share the entire root transcript or all repository checkouts with every child. Pass immutable context once, then compact diffs and evidence references.

Each worker returns changes, source pins, commands and exit results, output paths/hashes, unmet acceptance criteria, and a short decision summary. Do not request hidden reasoning. A child must not claim another child's test ran. Leads aggregate results; root checks integration seams. Shared registries, release state, naming decisions, and cross-repository merge order have one writer: root or a specifically delegated integration owner.

Use isolated worktrees/branches and explicit write leases. Two tasks may read the same input but cannot simultaneously own the same output path. Case-insensitive filesystems and renamed paths count when checking collisions. Avoid unrelated refactors, transient files in source trees, and unnecessary dependency changes.

## Reviewer independence

For each coordinator, builder and reviewer are distinct native agents. Reviewer is read-only on implementation and may write only review records and separately assigned tests. If a reviewer authors a corrective patch, a different reviewer must approve that patch. Approval includes substantive diff inspection, meaningful verification, output inspection when visual, and remaining risks. No automatic approval from a zero-exit lint command.

## Efficiency

Use deterministic scripts for checksums, noncreative exports, functional HTML/data tables, and report assembly. Creative visual assets are exclusively Astra-prompted gpt-image-2 outputs. Cache source reads by repository ID and commit, not mutable URLs alone. Set explicit image-generation call budgets per asset family; generate one master and deterministic derivatives rather than repeatedly generating a logo. Stop after bounded candidate/revision batches and choose with an explicit rubric. Do not lower the required model/effort to save tokens. Reduce redundant work instead.

## Durable execution state

Maintain private run-state, task ledger, native spawn registry, write leases, approvals, source snapshots, and findings. Sanitize only the necessary summaries for public delivery. `scripts/agent_ledger.py` validates a recorded ancestry ledger; it does not itself hook or control native spawning. Integrate a supported runtime enforcement mechanism if available, and record what is technically enforced versus procedurally checked.

After interruption read the actual ledgers, Git status, native sessions, and existing artifacts. Resume the smallest incomplete dependency; do not replay destructive operations, regenerate approved assets, or create duplicate PRs. An external publication or rename needs an idempotent operation record and fresh target check.

## Art prompt routing and runtime identity

The 49-role topology remains: 47 Luna/max roles and two Astra/max art-author leaves. The image renderer is a tool, not a child agent. Leaves cannot spawn. An ordinary implementation leaf needing artwork sends a bounded brief to its coordinator/root; the root schedules the existing W02 lineage and returns approved artifacts. Do not send an ad hoc Astra request from a depth-3 Luna leaf as an unrecorded depth-4 agent. Reopen a valid W02 chain when needed, retaining history and the global budget.

The role catalog and generation-policy.json are authoritative for model exceptions. All native-ledger entries include role_id. A W02 art coordinator remains Luna and may not claim to be Astra or write final prompts. Designated Astra leaves author initial and edit prompts rather than only approving another model's completed prompt. An unchanged earlier Astra-authored prompt may be reused with its verified provenance; a changed creative prompt requires a new Astra-authored revision.

Image-generation calls must request gpt-image-2 explicitly or have equivalent trusted backend attestation. Record any documented resolved snapshot and its alias evidence. A request for the right model without accepted/observed evidence remains unverified. Do not start generation until rights and available budget permit the bounded job. A failed call is recorded, not laundered into a successful asset.
