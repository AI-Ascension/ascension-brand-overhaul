# W01 source and capability baseline

Collection date: 2026-09-07
Collector: W01-L, thread `01a07a4e-d58b-7953-9513-872ffdf45469`
Parent: root thread `01a07a4b-38ad-7673-b653-dad49eed9dbd`
Package source pin: `5a2acfd6690d2533af046a7afcf3a7782b29042b`

This audit records current GitHub source and dated owner evidence. It keeps source, test, host, deployment, and public-artifact claims separate. The machine-readable companion files are [execution/source-snapshot.json](../execution/source-snapshot.json) and [execution/capabilities.json](../execution/capabilities.json).

## Collection and delegation boundary

Read-only source inspection used the GitHub API and `gh` CLI. The authenticated API request actor was verified as `CompleteDotTech` (user ID `5861166`) with `gh api user`; `gh auth status` listed a different stored account name (`romgenie`), so the API result is the account identity used for this audit. No token or credential value was copied.

The required useful native chain was attempted as a capability check:

```text
ROOT -> W01-L -> W01-C1 -> W01-C1-BUILD
requested child: W01-C1
requested model: gpt-5.6-luna
requested effort: max
```

The callable tool inventory exposed no `collaboration.spawn_agent`, `collaboration.send_message`, `followup_task`, or equivalent declaration to this lead. The checked expression returned an empty list. `codex queue` could notify the root session, but it did not create a child and is not evidence of a native spawn. Therefore no C1 coordinator or leaf ID, accepted model, observed model, or child result exists. The root accepted this limitation and instructed the lead to complete the scoped inspection directly. The independent C1 review is correspondingly `blocked_native_delegation_unavailable`; this audit is not presented as an independent review.

The exact interface result is retained in `execution/source-snapshot.json` under `native_delegation`. No client was launched and ancestry was not bypassed.

## Current organization inventory

The repository metadata below was read from `orgs/AI-Ascension/repos?per_page=100` and each default branch head was re-read from the commit API on 2026-09-07. IDs are stable GitHub repository IDs; names and descriptions are mutable presentation fields.

| Repository | ID | Visibility | Default branch | Exact head | Current role |
| --- | ---: | --- | --- | --- | --- |
| [`.github`](https://github.com/AI-Ascension/.github/tree/0cbdf744d515b16c042eb6e16b1537d8ccf11771) | 1354466045 | public | `main` | `0cbdf744d515b16c042eb6e16b1537d8ccf11771` | Organization policy, contributor guidance, and evidence status |
| [`AI-Ascension.github.io`](https://github.com/AI-Ascension/AI-Ascension.github.io/tree/bbe475998b0cd279309666f5cec3dc433d90a4a4) | 1354473981 | public | `main` | `bbe475998b0cd279309666f5cec3dc433d90a4a4` | Historical evidence site and GitHub Pages entry point |
| [`ai-agent-observability`](https://github.com/AI-Ascension/ai-agent-observability/tree/b25880376d3a3334c77f58637267db93581c4c77) | 1357224960 | public | `main` | `b25880376d3a3334c77f58637267db93581c4c77` | Self-hosted observability source; live telemetry unverified |
| [`aiascension.tech`](https://github.com/AI-Ascension/aiascension.tech/tree/4e2d99c95d89ce3d18981d331faad10c9f1f7376) | 1209899690 | public | `codex/wire-mailing-list-email` | `4e2d99c95d89ce3d18981d331faad10c9f1f7376` | Canonical-domain source and PHP subscription app |
| [`ascension-brand-overhaul`](https://github.com/AI-Ascension/ascension-brand-overhaul/tree/5a2acfd6690d2533af046a7afcf3a7782b29042b) | 1359787764 | private | `main` | `5a2acfd6690d2533af046a7afcf3a7782b29042b` | Brand operations source; this package was the baseline content |
| [`ascension-map-visualizer`](https://github.com/AI-Ascension/ascension-map-visualizer/tree/18915e5571829e582f460bf14b674cc2db39d9c5) | 1359701124 | public | `bootstrap` | `18915e5571829e582f460bf14b674cc2db39d9c5` | Active map assignment; rename deferred |
| [`ascension-watchdog`](https://github.com/AI-Ascension/ascension-watchdog/tree/dc2d20badb9e86c12067316b92d6c8289b2e6995) | 1359537708 | public | `bootstrap` | `dc2d20badb9e86c12067316b92d6c8289b2e6995` | Watchdog source; integrated service unverified |
| [`sts2-game-core`](https://github.com/AI-Ascension/sts2-game-core/tree/87e0f3d9355c0827e989d9fbc31804440852519b) | 1354377929 | public | `main` | `87e0f3d9355c0827e989d9fbc31804440852519b` | Host-independent typed domain core |
| [`sts2-game-mod`](https://github.com/AI-Ascension/sts2-game-mod/tree/8b71150895ea95c0625afc1389bb08e4034d9350) | 1354377975 | public | `main` | `8b71150895ea95c0625afc1389bb08e4034d9350` | Managed/native game-process adapter |
| [`sts2-gateway`](https://github.com/AI-Ascension/sts2-gateway/tree/33ea48f3b549f08e19db80d8c68c1438fa12a60a) | 1354378018 | public | `main` | `33ea48f3b549f08e19db80d8c68c1438fa12a60a` | Lifecycle and routing control plane |
| [`sts2-harness`](https://github.com/AI-Ascension/sts2-harness/tree/cb17b6c15262ce9356f1e85fd475af997aedc445) | 1354378100 | public | `main` | `cb17b6c15262ce9356f1e85fd475af997aedc445` | Experiment coordination, provider ports, records, replay |
| [`sts2-mcp-server`](https://github.com/AI-Ascension/sts2-mcp-server/tree/eb89ab251665f263c2fe3e6b735eeae3d3e40c83) | 1354378057 | public | `main` | `eb89ab251665f263c2fe3e6b735eeae3d3e40c83` | Thin MCP process and gateway mapping |
| [`sts2-protocol`](https://github.com/AI-Ascension/sts2-protocol/tree/8874b0951289fd943c7e14dea36557fa24c401d1) | 1354378136 | public | `main` | `8874b0951289fd943c7e14dea36557fa24c401d1` | Neutral metadata contracts and conformance vectors |

The current organization API description remains: “Independent Rust project building a path from AI agents to Slay the Spire 2 as small, tested boundaries that can refuse a request; nothing is live yet.” That text is a mutable GitHub presentation field. A served canonical website and a built GitHub Pages deployment are separate observations; HTTP success or deployment metadata does not prove a live runtime service, model gameplay, or that the runtime portion of the sentence has changed. The text is retained as a current-source fact and addressed as a proposed copy change in the W01-C2 outputs; no GitHub metadata was changed here.

## Source and policy inspection

The Rust targets expose `ci.yml` and `policy.yml` workflows that run on pull requests and pushes to `main`. The game-mod also exposes `source-release.yml`, triggered by manual dispatch or `sts2-game-mod-v*` tags. These workflows establish source checks and release-bundle mechanics, not a deployed game service. The replayable document scope is exactly the selected README, product, policy, workflow, and evidence paths enumerated in `source_documents`. Broader policy filenames are not a claim that their complete bytes are inventoried here.

The historical site has `pages.yml` and `validate.yml`; both push paths use `main`. The canonical-domain repository has no GitHub workflow and its README describes cPanel shared hosting, PHP 8.3+, Composer, PHPMailer, and an external production checkout. The observability, watchdog, map, and brand repositories have no deployment workflow in their current default trees. Blob identities for the selected documents and separate workflow-path summaries are in the source snapshot; the latter are not a complete workflow-byte inventory.

The source boundaries are explicit:

- `sts2-game-core` is a pure domain package and does not claim a simulator or host compatibility.
- `sts2-game-mod` owns managed loading, host translation, a bounded main-thread queue, ABI admission, and local HTTP; the game host remains authoritative. Current crate names include `sts2-game-mod`, `sts2-game-mod-host`, `sts2-game-mod-http-adapter`, and `sts2-game-mod-interop`; the managed manifest ID is `AIAscensionSTS2GameMod`.
- `sts2-gateway` owns lifecycle, instance leases, epoch fencing, and fixed routing. It does not own game rules, MCP semantics, host objects, or provider behavior.
- `sts2-mcp-server` owns MCP framing, schemas, bounded validation, and gateway mapping. It cannot bypass the gateway.
- `sts2-harness` owns coordination, provider ports, episodes, trajectories, replay, scoring/evaluation seams, and artifact lineage. It has no direct game access.
- `sts2-protocol` owns neutral metadata and conformance artifacts, not a generic implementation bucket or universal agent protocol.
- `ai-agent-observability` documents a private self-hosted Compose topology; current main does not establish that gameplay telemetry reaches either backend.
- `ascension-map-visualizer` has only a five-file bootstrap default branch. The shared local checkout has an active dirty `feat/complete-map-visibility` implementation with untracked files; it remains outside the default branch and must not be silently renamed.
- `ascension-watchdog` has a bootstrap default branch and an in-progress draft PR; a service or recovery guarantee is not established.

## Active pull requests

At collection time, only three pull requests were open in the mapped organization repositories:

| Repository / PR | State | Head → base | Checks and merge state |
| --- | --- | --- | --- |
| [`ai-agent-observability#10`](https://github.com/AI-Ascension/ai-agent-observability/pull/10) | open, draft | `b3a9fa64` → `b2588037` | Validate deployment contract passed; `CLEAN`, mergeable |
| [`ascension-watchdog#2`](https://github.com/AI-Ascension/ascension-watchdog/pull/2) | open, draft | `55480e05` → `dc2d20ba` | Ubuntu and Windows synthetic-process checks failed; dependency security passed; `UNSTABLE`, mergeable |
| [`sts2-game-mod#52`](https://github.com/AI-Ascension/sts2-game-mod/pull/52) | open, ready | `1628c22f` → `c41064a7` | Rust foundation, policy, and managed-source checks passed; `CLEAN`, mergeable |

The older `.github/STATUS.md` text saying protocol PR #11 and MCP PR #16 remained open is historical. Fresh PR inspection shows both merged on 2026-09-06. Game-mod PR #50 likewise merged on 2026-09-07. Current PR facts in [source-snapshot.json](../execution/source-snapshot.json) supersede those stale open-state statements without rewriting the historical record.

## Deployment and current journeys

### Historical GitHub Pages site

`AI-Ascension.github.io` Pages metadata reports `built`, source branch `main`, and deployment ID `6298437311` at `bbe475998b0cd279309666f5cec3dc433d90a4a4`, updated 2026-09-06 21:53:24 UTC. The site documents these journeys: a hero/evidence index, a deterministic browser replay at `proof.html`, starter cargo guidance and an honest empty gallery at `recipes.html`, architecture, repository inventory, evidence labels, contributor guidance, and a 404 page. The current proof page reports stale-epoch denial before transport and explicitly says runtime/game are unverified. This is a public historical report/replay artifact, not a current live game run.

### Canonical domain

The root's separate read-only host audit is stored at `execution/site-baseline.json` in the integration workspace. It records:

- live checkout branch `codex/wire-mailing-list-email` and host Git head `598ce386521f720f480c946486c4442b60610c9c`;
- GitHub source/default head `4e2d99c95d89ce3d18981d331faad10c9f1f7376`, with checked live tracked file hashes matching the current source files;
- `GET https://aiascension.tech/` returning HTTP 200 and 23,458 bytes;
- `GET /api/subscribe.php` returning HTTP 405, with no successful POST or email sent in this audit;
- PHP `8.3.33` on the host; and
- hosting-injected monitoring bootstrap plus `https://img1.wsimg.com/traffic-assets/js/tccl.min.js` in the served page.

The live source and host response are useful evidence of a served page, but source-level claims that the site makes no external request do not describe the hosting-injected document exactly. The README's declared production branch `master` differs from the GitHub default/live checkout branch; this requires operator confirmation before any migration. No host edits, deploy, mail, or DNS operation was performed.

## Evidence disposition

The following claims are available for careful presentation, with the labels shown in the capability registry:

| Evidence | What the source says | Presentation boundary |
| --- | --- | --- |
| Gateway browser proof | Historical deterministic stale-epoch replay; zero transport calls | Report/replay only; no game or provider claim |
| Windows seeded campaign | Visible Astra-controlled v0.107.1 practice campaign reached Defeat on floor 17; 333 settled operations; fresh complete replay | Dated report only; private trajectories/captures remain private; not a verified win |
| Linux seeded campaign | Visible v0.107.1 practice campaign reached Defeat on floor 24 after one controller restart; 431 settled operations; fresh complete replay | Dated report only; not uninterrupted control, a verified win, or broad compatibility |
| Forced Victory fixture | Native Victory surface observed with living player, disabled input, and empty legal catalog after fixture-forced terminal state | Forced terminal observation; not model gameplay or a campaign victory |
| MCP co-op synchronization | Read-only coordinator reports through MCP/gateway executables; rejected report writes; zero downstream game connections | Coordinator report only; not native multiplayer |
| Rust CI and policy | Formatting, Clippy, tests, metadata, checksums, and strict policy at named source heads where the owner reports pass | Source/static evidence only; not deployment or host proof |
| Observability source | Compose topology and docs exist; draft durability PR has one passed check | No current live telemetry proof |
| Watchdog source | Bootstrap docs and a draft implementation exist | Open PR has failing platform checks; no 24/7/recovery claim |

No current public video or replay package is established by this audit. The campaign records are public Markdown reports that point to private artifacts. `report_only` is therefore distinct from `video` and `replay_package` in `execution/capabilities.json`.

## Claim freeze and unresolved boundaries

The evidence check did not find a model-played campaign Victory. Keep **Road to the First Verified Win** as the season framing. Do not claim a first verified win, 24/7 autonomous operation, universal provider integration, native multiplayer, complete campaign/character/seed coverage, clean-install/update/rollback readiness, Workshop publication, current live observability, trademark clearance, or Mega Crit/Valve endorsement.

The exact remaining boundaries are:

1. Re-read stable IDs, default heads, redirects, and dependent Actions callers immediately before any authorized repository rename. No rename was performed.
2. Reconcile the active dirty map implementation before changing its identity.
3. Confirm the canonical-domain production branch and hosting control before a site migration; preserve the PHP subscription backend and account for injected monitoring.
4. Keep private campaign trajectories, captures, saves, host files, provider credentials, and hidden reasoning outside the brand repository and public exports.
5. W03 source review is recorded in `execution/reviews/W03-W01-review.md`; its provenance repairs require rereview. This does not establish the required depth-3 native reviewer ancestry.

## Reproduction and integrity checks

The selected source documents can be reviewed using the URLs and Git blob identities in [execution/source-snapshot.json](../execution/source-snapshot.json). W03 independently reproduced the exact `0e03d97bc6af6b7622d33d830bdde1eef1c2b1d8` archive: package validation and all 170 tests passed. The later `c9b3369cb182fce81c7b6c9d550ad6b95455a64d` archive had eight W04/W07 inventory/hash errors, yielding two package-related failures among 188 tests. The earlier claim of a `.gitignore` failure at this frozen revision was incorrect. The final integrated result is recorded separately at its exact source revision; none of these checks establishes gameplay, deployment, or image generation.
