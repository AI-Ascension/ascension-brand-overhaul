# Episode 01 launch package — What actually happened

Status: authored operating draft. The episode is scheduled by relative week only. No post, email, capture, or campaign operation has been performed.

## Editorial guardrails

The current season remains **Road to the First Verified Win**. The refreshed W01 baseline found no model-played campaign Victory. The public material currently supports two dated, maintainer-reported practice campaign reports:

- Windows STS2 v0.107.1, seed `AIASCENSIONV3FULL1`, visible Astra-controlled run to Defeat on floor 17, 333 settled operations, and a fresh complete replay.
- Linux STS2 v0.107.1, the same reported seed and model family, visible practice run to Defeat on floor 24 after one controller restart, 431 settled operations, and a fresh complete replay.

Both are report-only public artifacts. They are not an independently rerun matched benchmark. Raw trajectories, captures, saves, credentials, private prompts, and hidden reasoning remain outside this package. The forced native Victory fixture is not used as campaign success.

Source pins:

- [Windows campaign report](https://github.com/AI-Ascension/sts2-harness/blob/cb17b6c15262ce9356f1e85fd475af997aedc445/docs/evidence/seeded-astra-campaign-20260906.md) at `cb17b6c15262ce9356f1e85fd475af997aedc445`.
- [Linux campaign report](https://github.com/AI-Ascension/sts2-harness/blob/cb17b6c15262ce9356f1e85fd475af997aedc445/docs/evidence/linux-seeded-campaign-20260906.md) at `cb17b6c15262ce9356f1e85fd475af997aedc445`.
- W01 source baseline: `../brand-w01/execution/source-snapshot.json`, package pin `5a2acfd6690d2533af046a7afcf3a7782b29042b`, collected 2026-09-07.

All visual IDs below resolve to `art/asset-registry.json`, but their planned generated exports are blocked by `ORCH-NATIVE-SPAWN-UNAVAILABLE`, `IMAGE-BACKEND-UNVERIFIED`, and `ART-PROVENANCE-ABSENT`. Use accessible text and source links until the Astra → gpt-image-2 gate is independently satisfied. No thumbnail or poster has been delivered.

## Qualified copy variants

### Outcome title

- **Option A:** What actually happened: two documented defeats
- **Option B:** Road to the First Verified Win: the receipts so far
- **Option C:** How far did the run climb? Read the report

Use Option A when the page leads with both reports. Do not shorten it to “AI wins” or imply a completed milestone.

### Report-only title

- **Option A:** A documented climb, a clear defeat, and the next question
- **Option B:** Floor 17, floor 24: reading two practice run reports
- **Option C:** The Climb begins with evidence, not a victory lap

### Description

> The Climb is AI Ascension’s documented experiment in game-playing agents. This first report reads two dated STS2 v0.107.1 practice campaign records: a Windows run that reached Defeat on floor 17 after 333 settled operations, and a Linux run that reached Defeat on floor 24 after one controller restart and 431 settled operations. Both reports are maintainer-reported and report-only; they are not a matched benchmark, a verified win, or a public gameplay video. Read the source records and see what the next attempt must make observable.

### Short description

> Two dated practice reports. Two defeats. A precise next question.

### Thumbnail copy variants

These are exact copy briefs for blocked registry assets `MKT-03`, `MKT-04`, `WEB-02`, and `RUN-01`; they are not final art prompts.

1. `THE RECEIPTS SO FAR` / subline `FLOOR 17 · FLOOR 24`
2. `WHAT ACTUALLY HAPPENED` / subline `TWO REPORTS, NO WIN CLAIM`
3. `THE CLIMB STARTS HERE` / subline `READ THE RUN REPORT`

Approval gate: source owner verifies each displayed number against the pinned report immediately before export; rights owner clears any capture; Astra authors the final prompt and gpt-image-2 generation record; an independent reviewer checks readability and factual copy. If those gates are not met, use a plain text thumbnail with no generated visual claim.

## Version A — actual-capture-ready script

This is a production script with capture slots. It is ready to run only after a real approved capture and public manifest exist. Bracketed items are gates, not facts.

### Preflight card

- Episode: `EP-01`, relative week 1.
- Required state: `video_available` only after an approved playable capture is hash-bound to an approved run manifest.
- Required source: exact run source revision, game build, seed policy, observation/action interface, provider configuration, intervention log, and outcome.
- Capture owner: W06-C1 plus named evidence owner.
- Privacy: crop private paths, account identifiers, credentials, hidden reasoning, raw prompts, saves, and raw trajectory payloads before review.
- Asset IDs: `MKT-04`, `MKT-03`, `WEB-02`, `RUN-01` (all currently blocked).
- Fallback: if footage or generated assets are not approved, switch to Version B and label the page `report_only`.

### Shot list and narration

1. **Cold open — 00:00–00:12**

   Visual: approved capture begins at a source-approved, non-sensitive moment. If no capture is approved, do not simulate this shot.

   Narration: “How far can an AI climb when we keep the receipts? This is The Climb, a documented experiment by AI Ascension.”

   On-screen disclosure: “Capture state: [video_available only after evidence review].”

2. **Question — 00:12–00:30**

   Visual: title card using `MKT-04` only if the asset gate has passed; otherwise accessible text.

   Narration: “The season is Road to the First Verified Win. The current baseline does not record that win yet, so today starts with what the reports actually say.”

3. **Run context — 00:30–01:10**

   Visual: source-approved run context panel. Never display a private run ID or raw prompt.

   Narration: “The dated records describe STS2 version 0.107.1 practice campaigns with the seed and configuration listed in each report. We show the game build, the interface, the intervention log, and the evidence class before we show an outcome.”

   Lower third: “Configuration and date are source fields; they are not a permanent model ranking.”

4. **Windows report — 01:10–02:00**

   Visual: approved gameplay capture or report card linked to the Windows source report.

   Narration: “The Windows report reaches Defeat on floor 17 after 333 settled operations. It also records a later fresh complete replay. That is a maintainer-reported, report-only result; it is not a verified win, and the private capture is not automatically public.”

5. **Linux report — 02:00–02:50**

   Visual: approved gameplay capture or report card linked to the Linux source report.

   Narration: “The Linux report reaches Defeat on floor 24 after one controller restart and records 431 settled operations plus a later fresh complete replay. The restart is an intervention disclosure. The report does not, by itself, tell us that the restart caused the outcome.”

6. **What the reports do not prove — 02:50–03:25**

   Visual: text list with no generated artwork requirement.

   Narration: “These contexts are not a matched Windows-versus-Linux benchmark. They do not establish broad compatibility, a live service, a 24/7 agent, native multiplayer, a public video, or a public replay package. A report is useful precisely when its limits stay attached.”

7. **Next question — 03:25–03:55**

   Visual: approved decision card only if a reviewed public decision exists; otherwise report text.

   Narration: “The next attempt should make its change, invariants, failure handling, and evidence package explicit before we interpret the result.”

8. **Close — 03:55–04:15**

   Narration: “Read both source reports, inspect the evidence labels, and return for the next question. Watch AI play. Inspect the run. Help it climb.”

   CTA on screen: “Read the run reports → [real pinned report URLs]”.

### Capture acceptance

Before calling this version ready, the evidence owner must provide a hash-bound approved capture, rights/consent record, sanitized public manifest, and review reference. A successful encode or a local preview is not enough. If the capture is unavailable, use Version B without changing the title to “watch the run.”

## Version B — report-only publication script

This version is deliverable with the current public evidence. It contains no claim that a playable video exists.

### Opening

“Welcome to The Climb by AI Ascension. The first question is not whether an AI has already won. The current evidence says that milestone remains open. The useful question is what the recorded attempts let us inspect.”

### Section 1: Windows report

“The Windows source report describes a visible STS2 v0.107.1 practice campaign using the documented configuration and seed. It reached Defeat on floor 17 after 333 settled operations, followed by a fresh complete replay. The source is a dated maintainer report. The public artifact is Markdown; private captures and trajectories remain private.”

### Section 2: Linux report

“The Linux source report describes a visible STS2 v0.107.1 practice campaign reaching Defeat on floor 24 after one controller restart, with 431 settled operations and a fresh complete replay. The restart is recorded as an intervention. The report is not a matched benchmark and was not rerun by W01.”

### Section 3: Read the receipts

“The public page at [ai-ascension.github.io/proof.html](https://ai-ascension.github.io/proof.html) is a historical browser replay of a stale-epoch gateway contract test. It demonstrates a bounded contract behavior. It is not a live game run or provider call.”

### Section 4: The boundary

“A forced native Victory fixture exists in a separate source report, but input was disabled and ordinary play was bypassed. We do not use it as campaign success. We also do not use this report package to claim a public gameplay video, replay package, broad compatibility, 24/7 operation, or a matched Windows/Linux result.”

### Close

“Read the exact reports, note the source revisions, and bring a correction if a claim changes. The Climb continues toward the first verified win.”

CTA: “Read the Windows report” and “Read the Linux report,” each linking to the pinned public source revision. The subscription CTA is shown only after the host’s POST flow, privacy review, and delivery state are independently verified.

## Production checklist

- [ ] Source revisions refreshed immediately before publication.
- [ ] Outcome and intervention fields copied from the approved manifest.
- [ ] Capture rights and consent recorded, or report-only version selected.
- [ ] Asset IDs resolved; blocked IDs are not described as delivered visuals.
- [ ] All title, description, thumbnail and CTA copy passes content review.
- [ ] No private trajectory, save, prompt, credential, account identifier or hidden reasoning appears.
- [ ] Destination availability checked; planned routes remain gated.
- [ ] Independent reviewer signs the exact final artifact.
- [ ] Results and audience metrics remain `unobserved` until collected.

