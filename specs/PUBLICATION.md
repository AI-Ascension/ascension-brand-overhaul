# Public run publisher and evidence-aware sharing

## Boundary

Implement a deterministic publication tool in the new repository. It consumes only explicitly approved sanitized exports from source owners. No direct gateway, game-mod, model credential, game save, raw private trace, or runtime mutation capability belongs here. Do not publish private Laminar/MLflow dashboards or expose their ports. Serving and rebuilding functional pages must work without an LLM call by using preapproved gpt-image-2 artwork. Creating or creatively revising art is a separate explicit Astra → gpt-image-2 job.

Separate ingestion/quarantine, schema validation, classification/redaction, approval, rendering, and publication. A private source's hash may itself be sensitive metadata; expose only the lineage approved for public use. Do not copy raw inputs into an output directory and attempt to hide them with CSS, robots.txt, or navigation removal.

## Public records

A run manifest needs: public run ID; title; recorded timestamp; publication version; real versus synthetic classification; evidence kind; source references/digests allowed for publication; model/configuration identifier; game/mod/harness revisions when known; observation/seed policy; resource-budget description; intervention summary; outcome; provider-call counts only when actually measured; media/replay availability; rights/approval references; and disclosures.

An action record needs: public run ID; stable public decision ID; observed state/turn/floor only if approved; legal choices or redacted availability; chosen action; observed consequence; evidence link; optional explanation with provenance (contemporaneously published model explanation, human analysis, or retrospective summary); and timing relative to actual captured media where available. Never imply hidden reasoning access.

Store outcomes separately from episode/execution status. Game defeat is not necessarily a system error; a controller crash is not necessarily a game defeat. A forced Victory observation fixture cannot appear as a model-earned win. A replay with no new provider calls is not a claim that the original run used no model or that replay execution had zero compute cost.

## Approval and export

Approvals bind exact source content digest, approved public fields/assets, intended surfaces, reviewer/authority reference, time, and optional expiry. Edited source or a new crop exposing private material requires revalidation. A changed digest invalidates an old approval. Never trust an arbitrary boolean inside a user-supplied manifest as authority.

Use strict object schemas with no unknown fields for the final public boundary. Prefer allowlisting to credential-key blacklists. Validate length, numeric bounds, identifiers, UTF-8, URLs, relative paths, MIME types, file sizes, and referenced digest identity. Refuse symlinks/path traversal out of the approved artifact root. Do not fetch arbitrary URLs or embedded resources during rendering; prefetch through an approved, domain-constrained ingestion path if needed. Escape all user/model/game text in HTML and SVG. Strip scripts, event handlers, external SVG references, metadata, and unsafe embedded content.

Generate stable functional HTML pages from accepted data and preapproved artwork. New exported card artwork requires a new Astra-authored gpt-image-2 generation tied to the changed data; do not paint creative card images with code. Keep publish outputs distinct from private working directories. Provide verify, render, and publish phases so local rendering cannot silently send content to a remote destination. Publish is approval-gated and idempotent. Permit report-only pages while accurately disclosing that raw trajectories are unavailable.

## Growth features

Implement anonymous local “Your move”: show a reviewed public state and legal options, hold the actual result until reveal, record only consented coarse events, then link to the run. Use local state; no fake aggregate vote counts. A community poll backend is outside the initial default and requires additional privacy/abuse scope. Display unavailable options honestly.

Comparison views must show matching or differing configuration, seed visibility, action interface, budgets, retries, and interventions. Do not rank “intelligence” from a small convenience sample. A live map is functional software; its authentic screen captures belong to the evidence-media lane. Exported presentation diagrams are gpt-image-2 artwork prompted by Astra from validated map data, reviewed node by node, and excluded from empirical-evidence claims.

## Tests

Include authentic-approved fixture handling when access permits and a separate synthetic test lane. Test missing approval, forged approval reference, changed digest, unapproved fields, unknown fields, hidden file in artifact directory, unsafe URL, traversal, symlink, HTML/SVG injection, oversized payload, missing footage, unavailable replay, forced fixture mislabeling, mismatched model metadata, duplicate publication version, and deterministic rerender. Test source records remain unchanged and provider/network calls remain zero in the offline renderer.

Production export must fail closed on synthetic test content, private classification, missing rights, invalid lineage, or a factual caption unsupported by available evidence. A compile pass alone does not certify privacy.

## Mandatory artwork source

All new artwork, including promotional images, exported diagrams, card artwork, icons, and creative revisions, follows `art/ASTRA_GPT_IMAGE_2_POLICY.md`: an actual `gpt-6-astra` author writes each final prompt and `gpt-image-2` generates the art. Functional HTML/CSS/data and approved real evidence are separate. Runtime serving uses already approved images with no implicit model calls. Missing art-model access blocks that asset, never authorizes code-drawn or reused-art substitutions.
