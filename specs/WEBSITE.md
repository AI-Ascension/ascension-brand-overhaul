# Canonical website and audience/developer experience

## Implementation architecture

Inspect both existing sites, actual deployment branch/configuration, PHP runtime requirements, and target repository policies. Default to retaining static HTML/CSS/JavaScript plus the existing PHP backend. A small deterministic build/export step is acceptable when it reduces duplication, but it must work with the current hosting model. Do not introduce a server framework, remote CMS, analytics vendor, paid service, or new hosting dependency solely for fashion.

Brand sources live in the new repository. The website receives reviewed deterministic exports and records source revision/digest. Build assets locally or through approved CI, not through runtime dependency on a mutable private URL. Preserve working mail and form code. Historical GitHub Pages routes remain served from their current repository; deployment configuration must distinguish actual HTTP redirects from canonical tags, landing-page notices, or client navigation.

## Required routes and states

| Surface | Required content and behavior |
|---|---|
| Home | Clear hero, latest real outcome/report, primary CTA chosen by availability, Watch/Build paths, current milestone, brief compatibility boundary. |
| Watch | Actual available stream/video or honest no-stream state; no fake live label or embedded placeholder channels. |
| Runs | Approved run index with filterable outcome/configuration/evidence availability; empty state links to documentation. |
| Run detail | Summary, configuration, action timeline, intervention record, evidence access, video/replay availability, publication history, canonical URL. |
| Decision | State and legal choices where rights permit, local guess/reveal, actual selected action and consequence, explanatory provenance, deep link to run. |
| Build | Tested start path, prerequisites, exact compatibility, a minimal working example, architecture, contributor route. |
| Docs | Current capability matrix, integration instructions, full engineering context, historical evidence pointers. |
| Press | Boilerplate, approved logo/raster exports, screenshot rights/captions, contact method verified from authorized sources. |
| Privacy | Actual data collection, purposes, retention, subprocessors if any, unsubscribe and deletion path. |
| Missing/error | Real 404, unavailable media, withheld artifact, invalid run ID, failed subscription, temporarily stale live status. |

Every visible control must work. Hide unavailable social destinations rather than link to '#'. External video embeds should be click-to-load where feasible; retain a text/video-link alternative. Do not force account creation to inspect public records. Do not add an install command whose executable does not exist.

## Responsive and accessible behavior

Inspect at approximately 360, 390, 768, 1280, and 1440 px widths, plus 200% zoom. Preserve visible focus, logical tab order, semantic landmarks, skip link, descriptive link text, accessible dialogs, and non-color evidence distinctions. Support system and explicit light/dark preferences and reduced motion. Use captions/transcripts for editorial video. An illustration may be decorative with empty alt; factual charts need a text equivalent and source.

Target WCAG 2.2 AA and verify against the current authoritative reference. Test text contrast and important non-text controls; do not assume an earlier token audit covers new combinations. Automated accessibility checks supplement manual keyboard, zoom, and screen-reader checks; label checks not executed.

## Performance targets (project budgets, not measured results)

Target public reading routes at LCP ≤2.5 s, INP ≤200 ms, and CLS ≤0.1 where field measurement is available. Use reproducible lab conditions for initial diagnostics and never call laboratory metrics field results. Prefer no third-party JavaScript on initial reading routes. Target compressed first-party JavaScript ≤150 KiB on home/build routes, above-fold raster art ≤250 KiB, and responsive lazy-loaded media. Record and justify budget exceptions rather than downscale charts until illegible.

Use a real mobile crop rather than desktop art stretched into portrait. Define image dimensions to prevent layout shifts. Keep decorative images out of the critical path when they add no product information. Generate unique accurate titles, descriptions, canonical metadata, sitemap, robots rules, and social previews. Avoid fabricated review/rating structured data.

## Subscription journey

Inspect existing server validation, rate limits, persistence, notifications, and anti-bot behavior. Implement whatever is missing for a coherent consent, confirmation, successful subscription, duplicate, unsubscribe, and failure journey. Keep unsubscribe tokens opaque and expiring where appropriate; avoid endpoint behavior that exposes who is subscribed. Store secrets outside webroot and never include them in example output. Hashing an IP is not a claim of anonymity.

Exercise concurrent writes, idempotency, malformed content types and oversized bodies, rate-limit behavior, wrong-origin requests, HTML injection in notifications, storage failure, and mail transport failure. Origin/CORS checks are not authentication or complete abuse protection. Use an isolated mail sink and synthetic addresses. Production messages and any migration of subscriber data need scoped authorization and secure backup/rollback.

## Acceptance

Browser-test every core route/state, inspect screenshots in light/dark/mobile/desktop, verify no synthetic fixture appears in production, verify links after staged repository renames, confirm form behavior against the actual backend, and record deployment-specific smoke tests separately from local tests.

## Mandatory artwork source

All new artwork, including promotional images, exported diagrams, card artwork, icons, and creative revisions, follows `art/ASTRA_GPT_IMAGE_2_POLICY.md`: an actual `gpt-6-astra` author writes each final prompt and `gpt-image-2` generates the art. Functional HTML/CSS/data and approved real evidence are separate. Runtime serving uses already approved images with no implicit model calls. Missing art-model access blocks that asset, never authorizes code-drawn or reused-art substitutions.
