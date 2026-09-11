# The Climb digest template

Status: draft assembly template. The existing host supports a PHP subscription path, but the W01 audit observed only HTTP 200 for the home and HTTP 405 for GET `/api/subscribe.php`; no successful POST or email delivery was recorded. Do not send or promise delivery until the subscription owner verifies the POST flow, privacy notice, duplicate/throttle behavior, and mail result.

## Subject variants

- What actually happened in The Climb
- Two reports, one next question
- The Climb dispatch: receipts before results

## Preheader variants

- A dated Windows report, a dated Linux report, and the fields the next attempt must expose.
- Floor 17 and floor 24 are report facts, not a victory claim.
- Read the source revisions; bring a correction or a reproducible question.

## Plain-text body

Hello,

The Climb is AI Ascension’s documented experiment in game-playing agents. This dispatch begins with the current evidence.

A dated Windows STS2 v0.107.1 practice campaign report records Defeat on floor 17 after 333 settled operations and a later fresh complete replay.

A dated Linux STS2 v0.107.1 practice campaign report records Defeat on floor 24 after one controller restart and 431 settled operations, plus a later fresh complete replay.

These are maintainer-reported, report-only artifacts. They are not a verified model-played win, a matched Windows/Linux benchmark, a public gameplay video, or a public replay package. Private captures and trajectories remain private.

Read the [Windows report](https://github.com/AI-Ascension/sts2-harness/blob/cb17b6c15262ce9356f1e85fd475af997aedc445/docs/evidence/seeded-astra-campaign-20260906.md).

Read the [Linux report](https://github.com/AI-Ascension/sts2-harness/blob/cb17b6c15262ce9356f1e85fd475af997aedc445/docs/evidence/linux-seeded-campaign-20260906.md).

Next: a bounded question about what a compatible, inspectable attempt must record.

Watch AI play. Inspect the run. Help it climb.

Source revisions and artifact states are checked before each approved send. If a sentence is outdated, reply with the sentence, source, revision, and correction.

— AI Ascension

## HTML content blocks

1. **Masthead:** “The Climb — by AI Ascension”; the reviewed blank `MKT-07` layout and accessible [HTML](email-run-card.html)/[plain-text](email-run-card.txt) assembly previews are available. Approved run values and send authorization remain required; the previews are not a populated digest.
2. **What changed:** one sentence tied to the approved content ID and source revision.
3. **Evidence card:** outcome, build, configuration, intervention, evidence kind, public artifact state, and source link. Never expose private run IDs.
4. **Next question:** one bounded question with `result_status: unobserved` until collected.
5. **Developer link:** pinned source file or tested quickstart, labeled with source/test scope.
6. **Correction link:** correction form or reply instructions with the source revision.
7. **Unsubscribe:** use the host’s approved unsubscribe route. Do not put email addresses or tracking identifiers in campaign events.

## Send gate

- [ ] Subscriber consent and unsubscribe behavior have passed the website owner’s tests.
- [ ] Recipient list is handled only by the subscription system; it is not exported into the brand repository.
- [ ] Source links and revisions rechecked.
- [ ] Any capture has written rights/consent.
- [ ] Asset `MKT-07` is either independently approved or omitted in favor of text.
- [ ] Privacy review covers hosting-injected monitoring noted in the W01 site audit.
- [ ] Independent reviewer signs subject, body, links, and disclosure.
- [ ] Operator authorization is recorded for the send.

