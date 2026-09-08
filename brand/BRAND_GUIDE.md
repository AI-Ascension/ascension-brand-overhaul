# AI Ascension brand guide

Version 1.0 · 2026-09-07
Canonical copy registry: [copy.json](copy.json)
Evidence and source baseline: [execution/capabilities.json](../execution/capabilities.json) and [docs/BASELINE_AUDIT.md](../docs/BASELINE_AUDIT.md)

This guide fixes the public language for the overhaul. It does not change runtime package names, protocol identities, host contracts, or historical evidence. The public organization identity is **AI Ascension**. The flagship developer product is **Ascension**. The recurring audience series is **The Climb — by AI Ascension**. Keep the GitHub handle `AI-Ascension` and the canonical domain `aiascension.tech`.

## Positioning

AI Ascension is an independent project making open tooling for game-playing agents, starting with Slay the Spire 2. It makes a run inspectable: what the agent saw, what it chose, what settled, and what can be replayed. Current public evidence is bounded and dated. The project should feel like a research journal that people can watch, read, and contribute to.

The central promise is:

> **Watch AI play. Inspect the run. Help it climb.**

The technical descriptor is:

> **Open tooling for game-playing agents, starting with Slay the Spire 2.**

Use “experiment” when describing broad reliability, support, or future integrations. Use “toolkit” for Ascension when the sentence is about the complete developer-facing product. Describe each component by its function rather than giving every service a mythic name.

## Naming hierarchy and grammar

| Layer | Canonical name | Use |
| --- | --- | --- |
| Organization | AI Ascension | Public identity, people, docs, and community |
| Flagship | Ascension | The developer toolkit and its coordinated run workflow |
| Series | The Climb — by AI Ascension | Episodes, reports, and recurring audience content |
| Game integration | Slay the Spire 2 integration / STS2 game mod | The game-specific adapter; retain the repository's technical identity during the first rollout |
| Website | AI Ascension website | Canonical Watch and Build entry point at `aiascension.tech` |
| Evidence site | AI Ascension historical evidence | Legacy GitHub Pages material and stable proof links |

The first season remains **Road to the First Verified Win**. The current baseline contains dated model-controlled campaigns that reached Defeat and a forced terminal Victory observation fixture. It does not contain a model-played campaign Victory. Keep the season framing until a new source record proves otherwise.

### Repository naming map

Public display names may be clearer than repository slugs. The migration plan records exact IDs, current heads, aliases, compatibility anchors, and the order for any separately authorized rename. The initial presentation rollout may use display names while slugs remain unchanged.

| Current repository | Public display name | Planned slug action | Runtime identity |
| --- | --- | --- | --- |
| `sts2-harness` | Ascension | plan `ascension` | Preserve `sts2-harness`, binaries, schemas, and environment names initially |
| `sts2-mcp-server` | Slay the Spire 2 MCP | plan `sts2-mcp` | Preserve MCP methods, routes, package, and session header names |
| `sts2-game-mod` | Slay the Spire 2 Mod | plan `sts2-mod` | Preserve package, ABI, manifest, loader, and host-version identifiers |
| `sts2-game-core` | STS2 Domain Core | plan `sts2-core` | Preserve crate and schema identities |
| `sts2-gateway` | STS2 Gateway | keep | Preserve gateway routes and lifecycle identities |
| `sts2-protocol` | STS2 Protocol | keep | Preserve neutral contract and schema identities |
| `ascension-map-visualizer` | STS2 Map Viewer | deferred `sts2-map` | Reconcile the active dirty implementation first |
| `ascension-watchdog` | Ascension Watchdog | keep | Preserve the required operations name |
| `ai-agent-observability` | Ascension Observability | plan `ascension-observability` | Preserve upstream service and deployment identifiers |
| `aiascension.tech` | AI Ascension Website | plan `website` | Preserve PHP subscription paths and deployment branch until confirmed |
| `AI-Ascension.github.io` | AI Ascension Historical Evidence | keep | Preserve stable Pages URLs and anchors |
| `.github` | AI Ascension Community | keep | Preserve organization policy paths |
| `ascension-brand-overhaul` | AI Ascension Brand System | create/reuse private source | This repository's canonical brand and rollout source |

Do not introduce Arena, Oracle, Sentinel, Atlas, or a competing sub-brand. Do not rename package, binary, schema, MCP, HTTP, ABI, loader, manifest, environment, or evidence identifiers just to match a display name.

### Collision guard

Use **AI Ascension** in page titles, repository descriptions, social handles, and other external metadata. Pair **Ascension** with “by AI Ascension” or the Slay the Spire 2 descriptor when the surrounding context is not already explicit. Use the full **The Climb — by AI Ascension** series name rather than presenting “The Climb” as an unqualified show title. The bounded external review found established unrelated uses of “Ascension” and “The Climb”; this guard improves distinction without making a legal or trademark conclusion. See [NAME_COLLISION_REVIEW.md](../docs/NAME_COLLISION_REVIEW.md).

## Audiences and message order

Lead with the experience, then identify the evidence state, then offer the next useful action.

For spectators, show the outcome first: “A run reached floor 17 and ended in Defeat,” when linking the dated report. Give a short explanation of what was observed and link to the report. Use **Read the run report** when no approved playable video is available. Use **Watch the run** only when a reviewed public video exists. Use **Inspect the replay** only when an approved replay package is available.

For developers, show the tested entry point and boundary: “Build the controlled path from harness to MCP, gateway, and game adapter.” Name prerequisites and exact versions in the technical documentation. Say when a source or test is local, synthetic, or tied to one host fixture. Do not imply that every provider or game path is supported.

Ascension is model-agnostic: individuals choose their own model and provider. Explain compatible adapters and workflow requirements, and provide an extension path for additional models. Describe tested configurations accurately without making a tested model mandatory. See `docs/MODEL_CHOICE.md`.

For researchers, show the observation rules, seed/build, action and model budget, intervention or restart history, source revision, and evidence artifact state. Link to the structured record or report. Never expose private trajectories, hidden reasoning, credentials, saves, or host files.

For contributors, show one bounded task and the repository owner. Explain where a change belongs before asking someone to install the whole stack. Keep the contributor path aligned with the repository map.

## Voice

Write with clear verbs and visible evidence. Prefer “ran,” “chose,” “failed,” “replayed,” “recorded,” and “measured.” Keep sentences concrete and calm. Let the design carry warmth; let the evidence labels carry caution.

Use:

- “The Windows fixture reached Defeat on floor 17.”
- “The Linux campaign resumed after one controller restart and completed a fresh replay.”
- “This page is a report of a bounded source or host result.”
- “The map viewer is an experimental preview.”
- “The evidence is report-only; the underlying capture remains private.”

Avoid:

- “The AI won” when the record says Defeat or only a forced terminal observation.
- “Fully autonomous,” “always on,” “production-ready,” or “works with every model.”
- “Universal agent protocol” for `sts2-protocol`.
- “Live” when there is no current broadcast-status signal.
- “Official,” “endorsed,” or “partnered” with Mega Crit, Valve, or a model provider.
- “Trademark cleared,” “safe to use,” or another legal conclusion.

## Claim vocabulary

| Label | Meaning in public copy |
| --- | --- |
| `planned` | Described in an approved plan; no implementation result is claimed |
| `source-derived` | Read from a named source revision; not a fresh execution |
| `offline-test` | Deterministic local or CI check with no live host claim |
| `native-run` | A dated host execution with exact fixture/configuration scope |
| `forced-fixture` | A test path that intentionally bypasses ordinary play or control |
| `replay` | A recorded sequence was replayed under the named rules and source |
| `report-only` | A public report exists; no approved video or replay package is available |
| `unverified` | The current evidence does not establish the claim |
| `confirmed` | Use only when the linked record's exact scope supports it; it never means general support |

Place the evidence label in the same visual block as the claim. A footnote can provide the full source, but it cannot be the only place a material limitation appears. Do not turn a historical source label into a current status without a fresh source revision.

## Copy system

The central promise, audience messages, headlines, CTAs, repository descriptions, and disclosures are versioned in [brand/copy.json](copy.json). Every factual record carries a source reference, revision, observed date, evidence kind, verification actor, artifact availability, supported configuration, and review status.

### Headline variants

Use the first line for the current surface and the second line for the evidence state.

| Surface | Headline | Supporting line |
| --- | --- | --- |
| Home | How far can an AI climb? | Watch AI play. Inspect the run. Help it climb. |
| Watch | See what the agent saw. | Read the latest dated run report while public video is unavailable. |
| Build | Build the path. Keep the boundary visible. | Open tooling for game-playing agents, starting with Slay the Spire 2. |
| Docs | Every action leaves a trail. | Follow the source revision, observation, decision, and settled result. |
| Series | The Climb — by AI Ascension | Road to the First Verified Win |
| Empty state | The next run has not been published. | Check back when a reviewed report or video is ready. |

The phrase “first verified win” is a goal or season title until a source-linked record proves a model-played win. “Road to…” is valid current copy; “after the first verified win” is not.

## Visual language

The visual language is a warm Ascent Ledger: paper, ink, amber, clear charts, branching paths, and restrained editorial typography. Use generous margins, short measures, ruled sections, and evidence stamps. Show real approved gameplay or legible run diagrams when they exist. A generated editorial poster is a visual companion, not proof of a run.

The canonical functional token files are [brand/tokens.json](tokens.json) and [brand/tokens.css](tokens.css), delivered by W02 at commit `c09a9da28ff4ee2264139353ba2313804ab55104`. They define the current light/dark colors, hover and focus states, status treatments, typography, spacing, controls, and reduced-motion behavior. They are functional styling tokens; generated identity artwork remains a separate W02 deliverable governed by the recorded root image-tool amendment, generation provenance, and independent review. See [the authorization](../art/root-generation-authorization.json).

For historical context only, the earlier Ascent Ledger reference is [`assets/identity/tokens.css`](https://github.com/AI-Ascension/AI-Ascension.github.io/blob/bbe475998b0cd279309666f5cec3dc433d90a4a4/assets/identity/tokens.css), blob `9a993f97c06257cd0a2b3d5a023a4715d0250c31`. The table below is not authoritative for current hover, status, or control values; use the canonical token files for implementation:

| Token | Light | Dark | Use |
| --- | --- | --- | --- |
| Ground | `#F4EEE2` | `#0B0A08` | Page background |
| Ground 2 | `#EBE3D3` | `#15120E` | Panels and alternate bands |
| Rule | `#CFC3AE` | `#2A241C` | Borders, dividers, chart rules |
| Ink | `#1A1712` | `#EDE4D3` | Primary text |
| Ink dim | `#5E564A` | `#A89F8C` | Secondary text and evidence labels |
| Ember | `#9C5B12` | `#E39B3A` | Primary action and ascent path |
| Ember highlight | `#C8782A` | `#F2B75C` | Hover, focus, active emphasis |
| Confirmed | `#2F7F66` | `#5FA88F` | Confirmed evidence stamp |
| Source-derived | `#4E6A8F` | `#7F8FA6` | Source-derived evidence stamp |
| Proposed | `#9A7B1C` | `#D2B04C` | Planned/proposed work |
| Inferred | `#6F5A94` | `#A08AB8` | Inferred interpretation |
| Unverified | `#A8402F` | `#C25B4A` | Unverified boundary |

Use Fraunces for display, Bricolage Grotesque for body text, and JetBrains Mono for identifiers and evidence labels. The existing site licenses are referenced in its notices; this repository must not bundle font binaries.

### Logo and mark use

Use the approved generated identity exports from the W02 asset registry when available. Until then, treat the historical wordmark and glyph as reference/archive material only; do not copy them into new-brand artwork or redraw them in SVG/CSS. Keep clear space equal to the height of the mark's smallest major stroke. Use the wordmark in ink on paper and in light ink on dark ground. The amber accent is reserved for the ascent path/caret and interactive emphasis. Do not stretch, rotate, recolor, add publisher marks, or place the mark over unreadable evidence graphics.

## Accessibility and motion

Use text plus a visible evidence label; color alone never carries `confirmed`, `source-derived`, `proposed`, or `unverified`. Meet WCAG 2.2 AA contrast for body text and controls, with a visible keyboard focus ring in Ember highlight. Keep body measures near 62 characters, provide a skip link, preserve heading order, label form errors next to fields, and provide alt text for meaningful images. Decorative art gets empty alt text and no data claim.

Respect `prefers-reduced-motion`. A timeline or stamp may settle into place, but its final state must appear without animation. Generated art needs a reviewed mobile crop and a contrast check on light and dark grounds. Do not use a blinking live indicator; live state must come from an actual stream-status source and must have an explicit disconnected state.

## Disclosures

Place the independent-project notice in the footer and beside game-specific claims:

> AI Ascension is an independent project. It is not affiliated with or endorsed by Mega Crit or Valve and grants no rights to game files, assets, or marks.

When a model is named, identify the exact tested configuration and date. Say “OpenAI Astra `gpt-6-astra` in the dated fixture report,” not “the best model.” Credit upstream services and licenses in the source or asset notice. A sponsor or paid placement requires a plain-language disclosure at the same level as the claim; no sponsorship is implied by this guide.

## Surface rules

| Surface | Lead content | Required boundary |
| --- | --- | --- |
| Home | Promise, current report, Watch/Build paths | Do not show a live state from a clock or placeholder |
| Watch | Actual video when approved, otherwise a report | `report-only` and `video` are different states |
| Runs | Outcome, timeline, source and evidence panel | Keep private trajectories and raw provider output out |
| Build | Tested prerequisites, install path, boundaries | Do not imply every component or provider is stable |
| Docs | Interfaces, source revisions, reproducible checks | Explain source/static evidence separately from host proof |
| Map | Experimental route preview | Do not market it as complete gameplay or rename during active work |
| GitHub | Functional repository descriptions and contributor path | Preserve exact runtime names and independent-project notice |
| Subscribe | Clear value, privacy, error and success states | Preserve PHP endpoint and disclose host behavior accurately |
| Press | Approved report links and generated editorial art | Never use generated art as gameplay evidence |

## Review gate

Before a copy change reaches a public surface, check the matching source record, source revision, artifact availability, and current date. A reviewer must be able to answer: What happened? Where is the evidence? What remains unknown? What can the reader do next? If any answer is missing, use a narrower claim and a report link.

### Artwork review and distribution states

The asset manifest separates source/export verification from distribution approval. `generated_original_reviewed` means the independent review inspected the declared generated sources and input references and found no identified third-party artwork in that scope. It does not certify legal or trademark clearance. Public downloads still need a current, exact-digest approval enrolled by the operator. See [artwork access](ART_ACCESS.md) for actual family states and remaining exports.
