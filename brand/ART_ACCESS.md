# W02 artwork access and blocker register

Status as of 2026-09-07: **blocked for all generated-art asset IDs**.

This register records an execution capability result. It does not claim that
the art jobs ran, that a prompt was authored, or that an image exists.

## Observed capability

The source snapshot for this worktree is `5a2acfd6690d2533af046a7afcf3a7782b29042b`.
The package requests the lineage `ROOT → W02-L → W02-C1 → W02-C1-BUILD` and
requires `gpt-5.6-luna/max` for W02-L and W02-C1, followed by
`gpt-6-astra/max` for W02-C1-BUILD. Root supplied a native W02-L thread
`01a07a53-0521-7673-b4fd-15921bfaa4b8` with parent
`01a07a4b-38ad-7673-b653-dad49eed9dbd`, observed as Luna/max. No trustworthy
native IDs or accepted/observed model records are available for the deeper
W02-C1 and W02-C1-BUILD nodes. The callable tool surface did not expose a
native `collaboration.spawn_agent`, `collaboration.send_message`, or
`collaboration.wait_agent` control, so no W02-C1 slot reservation or spawn
receipt can be recorded here. A root-spawned Astra would not satisfy the
required ancestry and was not substituted.

The available image-generation tool is exposed as `image_gen.imagegen`, with
fields for a prompt and optional image references. Its callable schema does
not expose an explicit image-model selector, and no trusted response metadata
attests `gpt-image-2` or the accepted dated snapshot. Under
`art/generation-policy.json`, that is an unverified backend. Generation is
therefore withheld; no fallback renderer, CSS drawing, SVG path, tracing,
legacy image, or alternate model is used.

## Exact blockers

| Code | Scope | Required evidence | Current result |
|---|---|---|---|
| `ORCH-NATIVE-SPAWN-UNAVAILABLE` | W02-C1 and W02-C1-BUILD | Native IDs with actual parent IDs, depth, requested/accepted/observed model and effort | Missing; the child session cannot request or verify the required nested chain |
| `IMAGE-BACKEND-UNVERIFIED` | Every generated-art ID below | A generation call that explicitly selects `gpt-image-2` and returns trustworthy backend evidence | Missing; exposed image tool has no model selector or backend attestation |
| `ART-PROVENANCE-ABSENT` | Every generated-art ID below | Astra-authored prompt bytes/hash, raw output hash/dimensions, generation record, and independent review | Missing because the author and backend gates are unresolved |

No Luna-authored final art prompt is stored. `art/PROMPTBOOK.md` remains a
brief package, not an author attestation. The functional token files in this
worktree do not draw, recolor, or stand in for identity artwork.

## Blocked generated-art IDs

The 72 IDs below are copied from `art/asset-registry.json`. Each remains
`blocked` for the three reasons above until the exact job has its own evidence.

### Identity (8)

| ID | Asset |
|---|---|
| `ID-01` | Branching-A mark |
| `ID-02` | Organization wordmark |
| `ID-03` | Flagship product lockup |
| `ID-04` | The Climb title lockup |
| `ID-05` | Organization avatar set |
| `ID-06` | Browser and app icon set |
| `ID-07` | Product and evidence icon sprite |
| `ID-08` | Design token and typography specimen (generated PNG; functional HTML may be implemented separately) |

### Illustrative masters (4)

| ID | Asset |
|---|---|
| `BG-01` | Editorial ascent environment master |
| `BG-02` | Dark broadcast atmosphere master |
| `BG-03` | Series interstitial texture |
| `BG-04` | Light/dark route pattern |

### Website (8)

| ID | Asset |
|---|---|
| `WEB-01` | Homepage illustration crop set |
| `WEB-02` | Latest-run generated editorial poster |
| `WEB-03` | Watch and Build pathway graphics |
| `WEB-04` | Hero and primary-page social preview |
| `WEB-05` | 404 and unavailable artwork |
| `WEB-06` | Subscription success and confirmation art |
| `WEB-07` | Current capability diagram |
| `WEB-08` | Map viewer integration preview |

### Run sharing (5)

| ID | Asset |
|---|---|
| `RUN-01` | Run summary card template |
| `RUN-02` | Decision reveal card templates |
| `RUN-03` | Timeline graphic template |
| `RUN-04` | Replay receipt graphic template |
| `RUN-05` | Comparison and rules panel template |

### Broadcast (7)

| ID | Asset |
|---|---|
| `CAST-01` | Single-agent broadcast overlay |
| `CAST-02` | Comparison broadcast overlay |
| `CAST-03` | Mobile broadcast layout |
| `CAST-04` | Starting, intermission, and ended scenes |
| `CAST-05` | Lower thirds and disclosure bars |
| `CAST-06` | Short title transition |
| `CAST-07` | Operator scene map |

### Campaign (9)

| ID | Asset |
|---|---|
| `MKT-01` | Channel cover |
| `MKT-02` | Social header |
| `MKT-03` | Thumbnail system |
| `MKT-04` | Season key visual |
| `MKT-05` | Community challenge card |
| `MKT-06` | Release and contributor card |
| `MKT-07` | Email digest artwork |
| `MKT-08` | Sponsorship disclosure tile |
| `MKT-09` | Press-kit cover and index (generated cover; functional index HTML may be implemented separately) |

### Documentation (5)

| ID | Asset |
|---|---|
| `DOC-01` | Runtime architecture diagram |
| `DOC-02` | Publication and evidence-flow diagram |
| `DOC-03` | Repository and rename map |
| `DOC-04` | Three-level orchestration diagram |
| `DOC-05` | Maintainer and contributor onboarding graphic |

### GitHub (26)

| ID | Asset |
|---|---|
| `GH-01-B` | Ascension repository banner |
| `GH-01-S` | Ascension social preview |
| `GH-02-B` | Slay the Spire 2 MCP repository banner |
| `GH-02-S` | Slay the Spire 2 MCP social preview |
| `GH-03-B` | Slay the Spire 2 Mod repository banner |
| `GH-03-S` | Slay the Spire 2 Mod social preview |
| `GH-04-B` | STS2 Domain Core repository banner |
| `GH-04-S` | STS2 Domain Core social preview |
| `GH-05-B` | STS2 Gateway repository banner |
| `GH-05-S` | STS2 Gateway social preview |
| `GH-06-B` | STS2 Protocol repository banner |
| `GH-06-S` | STS2 Protocol social preview |
| `GH-07-B` | STS2 Map Viewer repository banner |
| `GH-07-S` | STS2 Map Viewer social preview |
| `GH-08-B` | Ascension Watchdog repository banner |
| `GH-08-S` | Ascension Watchdog social preview |
| `GH-09-B` | Ascension Observability repository banner |
| `GH-09-S` | Ascension Observability social preview |
| `GH-10-B` | AI Ascension Website repository banner |
| `GH-10-S` | AI Ascension Website social preview |
| `GH-11-B` | AI Ascension Historical Evidence repository banner |
| `GH-11-S` | AI Ascension Historical Evidence social preview |
| `GH-12-B` | AI Ascension Community repository banner |
| `GH-12-S` | AI Ascension Community social preview |
| `GH-13-B` | AI Ascension Brand System repository banner |
| `GH-13-S` | AI Ascension Brand System social preview |

## Separate source classes

The authentic evidence families `RUN-06`, `RUN-07`, and `RUN-08` remain
evidence-media records. They are not generated-art jobs and must never be
invented, repaired, or replaced by generated images. Historical/reference
records `OLD-01` through `OLD-05` remain archive/reference material and are
not new-brand artwork. Their presence does not unblock any ID above.

## Unblocking checklist

For each ID, the root/coordinator must first record the actual native
W02-C1-BUILD Astra/max identity and parent chain, then have that Astra leaf
write the exact prompt bytes and SHA-256, invoke a route explicitly selecting
`gpt-image-2`, preserve the raw response and its dimensions/hash, inspect the
candidate, and route it to an independent reviewer. Only then may permitted
mechanical exports be added and linked to that generation record.
