# W01 independent review of frozen companion presentation commits

This review checks the ten presentation commits recorded in the canonical
`github/companion-commits.json` input, using each row's `base_revision` and
`revision`. The scope is the declared README/profile/index presentation files
and the canonical `github/settings-manifest.json`. The canonical checkout had
unrelated dirty and untracked work; it was read only and left unchanged. No
companion source, artwork, deployment, GitHub setting, pin, notification,
publication, or remote write was performed by this review.

## Frozen revisions and scope

The ledger identifies every branch as `local_commit_pending_independent_review`
with `pushed: false` (`github/companion-commits.json:3-160`). Each listed
worktree was at the expected revision, its listed base was an ancestor, and its
full diff contained only the declared paths.

| Repository | Base revision | Presentation revision | Changed paths |
| --- | --- | --- | --- |
| `AI-Ascension/.github` | `d8fb867dede3ec1cde424d7f6f6f56e49dc21227` | `d84523795a64556b82d29f6da1dab62eb9b8b4c8` | `README.md`, `profile/README.md` |
| `AI-Ascension/AI-Ascension.github.io` | `e81dd4e9ff2f8e5f8ffafc8b1a489d1e1cc7ef9f` | `b50f7d725c8d6abb6306963d059fbb7fa067402c` | `README.md`, `index.html` |
| `AI-Ascension/sts2-harness` | `cb17b6c15262ce9356f1e85fd475af997aedc445` | `d2105005ebdb6a5f7dd5e266e80b139e294cf89e` | `README.md` |
| `AI-Ascension/sts2-game-core` | `87e0f3d9355c0827e989d9fbc31804440852519b` | `9a27a80c32dcadd8030cf42c861e9e5da4daed1c` | `README.md` |
| `AI-Ascension/sts2-game-mod` | `8b71150895ea95c0625afc1389bb08e4034d9350` | `7cc0af3c64da639b191060251e667782d535bb0c` | `README.md` |
| `AI-Ascension/sts2-gateway` | `33ea48f3b549f08e19db80d8c68c1438fa12a60a` | `22d780c12c60d8a2e5e1310f57deeea172decbd6` | `README.md` |
| `AI-Ascension/sts2-mcp-server` | `eb89ab251665f263c2fe3e6b735eeae3d3e40c83` | `6ad97aeead88cdb2097675ddff076bc4bb97529d` | `README.md` |
| `AI-Ascension/sts2-protocol` | `8874b0951289fd943c7e14dea36557fa24c401d1` | `0c39c5a53b005d94df59f14f0962255d0962203a` | `README.md` |
| `AI-Ascension/ascension-watchdog` | `dc2d20badb9e86c12067316b92d6c8289b2e6995` | `9e240e916726b367dbae2cfd0eea64c3afeb35fa` | `README.md` |
| `AI-Ascension/ai-agent-observability` | `b25880376d3a3334c77f58637267db93581c4c77` | `f872902ed987f5946bf843824063d10884a1bd29` | `README.md` |

The full revisions and per-file SHA-256 values are recorded in the ledger;
all ten worktrees matched those values. All ten presentation diffs pass
`git diff --check`. The companion validation receipt also records
`source_code_changed: false` (`execution/reviews/companion-validation-001.json:821-827`).

## Verification

The public identity is applied consistently: organization `AI Ascension`,
flagship `Ascension`, and series `The Climb — by AI Ascension` agree with
the presentation manifest (`github/presentation-manifest.json:2-10`). The
new headings and descriptions explicitly preserve repository slugs and
runtime/package identities. Read-only `cargo metadata --locked --no-deps
--format-version 1` confirmed the product package names remain
`sts2-harness`, `sts2-game-core`, `sts2-game-mod`, `sts2-gateway`,
`sts2-mcp-server`, and `sts2-protocol`; game-mod's managed package
validation also retains its `ai-ascension.sts2-game-mod` identity. No
Cargo, .NET, source, schema, fixture, or package file is changed by these
commits.

The flagship inline quickstart in `sts2-harness/README.md:18-37` is
executable at its exact pinned commit. I ran its final command with an isolated
`CARGO_TARGET_DIR`:

```
CARGO_TARGET_DIR=/tmp/w01-harness-quickstart-target cargo run --locked --offline --package sts2-harness --bin sts2-harness-runtime-v2-fake
```

It exited 0 and emitted `schema_bytes_verified: true`,
`mutation_count: 1`, duplicate replay without a second mutation, stale-epoch
rejection, and `no_blind_retry_after_disconnect: true`. The checkout's
`rust-toolchain.toml` selects Rust 1.97.1, and the pinned commit is contained
by `main`, so the clone, checkout, fetch, and offline-run sequence is coherent.
This is deterministic fake-boundary evidence; it is not live game, provider,
or model-play evidence.

The report-linked runtime numbers agree with their source-owner records.
The pinned harness Linux report records Defeat on floor 24 after 431 settled
operations and one controller restart (`docs/evidence/linux-seeded-campaign-20260906.md:3-20`).
Its complete fresh replay is separately described as 431 actions with no
provider calls (`docs/evidence/linux-seeded-campaign-20260906.md:55-72`). The Windows report records Defeat on floor 17 after
333 settled operations and a complete fresh replay
(`docs/evidence/seeded-astra-campaign-20260906.md:1-13,37-49`). The profile
calls the linked material a source-owner report and says that no public
playable video accompanies it (`.github/profile/README.md:15-20`). The
presentation therefore preserves the distinction between dated source-owner
records, deterministic proof, forced terminal observation, and unverified
model-played Victory; this review does not upgrade those records to independent
host-play evidence.

The Pages presentation keeps the existing historical routes and evidence
assets. `proof.html`, `recipes.html`, `architecture.html`,
`repositories.html`, `evidence.html`, `contributing.html`, `404.html`,
the hero image variants, and `assets/identity/MANIFEST.md` all exist at
`AI-Ascension.github.io@b50f7d72`. The four audience sections are present at
`index.html#path-player`, `#path-rust`, `#path-mcp`, and
`#path-security` (`:141-200`), with the proof, recipe, architecture,
evidence, contribution, and security destinations intact. The exact Pages
suite passed **5/5**:

```
node --test tests/proof.test.cjs tests/site.test.cjs
```

This includes byte-for-byte fixture preservation, replay controls, duplicate-ID
checks, and local link/fragment resolution (`tests/site.test.cjs:8-31`).
Both pinned Rust reproductions also passed and matched their fixtures:
`recipes/gateway-lease-fence` produced SHA-256
`68f8180b2110b92bdcc283bcbbaf4461bda4ba66e9a7bce78151b6409dcdc769`, and
`recipes/mcp-seam` produced
`158b964ec7c3647e96283b660ed5d0e6285f7c94314d0d1911a0c37998ecc5cd`.
No asset or proof route was added or altered by the companion commits; the
presentation manifest explicitly preserves that policy
(`github/presentation-manifest.json:40-59,143-149`).

The component receipt records successful fetch, metadata, strict policy,
format, Clippy, and workspace-test checks for game-core, game-mod, gateway,
MCP, and protocol (`execution/reviews/companion-validation-001.json:265-727`);
the corresponding strict policy checks for all six Rust product workspaces
are independently reproducible and each exited 0. The managed game-mod
build and Workshop probe also exited 0 (`execution/reviews/companion-validation-001.json:95-123`). These are source and
component checks. The receipt correctly does not present them as deployment,
host-play, model, or release evidence.

The watchdog and observability limits remain explicit. At the pinned watchdog
source, `cargo` cannot run because there is no `Cargo.toml`; all six
recorded Cargo checks are non-passes (`execution/reviews/companion-validation-001.json:7-94`).
For observability, shell syntax, ShellCheck, fixture, bootstrap, and regression
checks pass, while the actual Compose check exits 127 because Docker is absent;
Docker/buildx checks remain unverified (`execution/reviews/companion-validation-001.json:125-262`). The respective READMEs
state implementation/deployment limits rather than claiming a live service
(`ascension-watchdog/README.md:5-11`,
`ai-agent-observability/README.md:71-77`). No watchdog service, observability
stack, public route, or telemetry ingestion was inferred from these checks.

The settings manifest is structurally safe and its observed values are current
in the live read-only API check. It has schema `ai-ascension.github-settings.v1`,
mode `review_only`, and explicit no-write authority
(`github/settings-manifest.json:1-6`). All 13 repository rows have unique
stable IDs, matching current repository IDs, names, descriptions, topics,
homepages, visibility, and default branches in the read-only GitHub API query;
all remain `proposed_not_applied` with `rename_included: false`
(`:7-348`). The six manual pin names are present in the manifest and retain
their rollback/checklist instructions (`:350-368`). A read-only GraphQL
query at 2026-09-07T17:10Z returned `pinnedItems.totalCount: 0`; the listed
six names are therefore an unapplied target order, not evidence that pins were
changed. No setting, pin, notification, or remote repository write occurred.

## Findings

### W01-COMP-01 — Watchdog Rust implementation is not validated (medium, pre-existing qualification)

The frozen watchdog tree contains documentation, governance files, and prompts
but no Cargo project. Its opening descriptor says
“Deterministic Rust deployment supervision and crash recovery”
(`ascension-watchdog/README.md:1-3`), while the pinned validation receipt records
missing-Cargo failures for fetch, metadata, build, Clippy, and test
(`execution/reviews/companion-validation-001.json:7-94`). The new presentation
paragraph correctly says that no watchdog service, 24/7 operation, or recovery
guarantee has been verified (`ascension-watchdog/README.md:5-11`), so the
companion diff does not create a new runtime claim. Keep the opening descriptor
source-derived and unverified; add an actual Rust package or qualify that
descriptor before treating it as implementation evidence.

### W01-COMP-02 — Observability deployment remains unverified (medium, pre-existing qualification)

The observability README describes a Docker Compose topology and local endpoints
(`ai-agent-observability/README.md:10-50`), but the only available receipt
records source checks and a Docker-unavailable Compose attempt
(`execution/reviews/companion-validation-001.json:125-262`). Its own evidence
section correctly says that source/build checks do not prove a running
deployment, trace ingestion, persistence, or a public route
(`ai-agent-observability/README.md:71-77`). Treat the topology and endpoints as
documented configuration only until a Docker/Podman composition and a separate
live deployment/telemetry check succeed. The presentation commit itself adds
the bounded companion wording and does not claim that the stack is operated.

## Review disposition

The ten presentation diffs are source-only, path-scoped, hash-matched, and
internally consistent with the recorded identity, runtime, and package
boundaries. The exact flagship quickstart, Pages suite, two Pages Rust
reproductions, six strict Rust policy checks, and the settings metadata audit
pass. The source-owner runtime records and live metadata snapshot are correctly
kept separate from independent component proof.

This review finds no changed-path defect that fabricates gameplay, Victory,
video, deployment, settings, pins, or package renames. The two findings above
are pre-existing verification qualifications: they remain release limits, not
evidence that the presentation commits changed implementation behavior. Do not
promote either unverified lane to a live or production claim until its stated
validation is available.
