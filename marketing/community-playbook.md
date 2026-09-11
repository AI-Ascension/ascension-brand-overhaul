# Community and contribution playbook

Status: operating draft. The playbook describes journeys and moderation; no community post, poll, contributor result, or creator agreement has occurred.

## Community promise

AI Ascension invites people to inspect an attempt, ask a bounded question, and help make the next record easier to reproduce. The central promise is “Watch AI play. Inspect the run. Help it climb.” Current season framing is Road to the First Verified Win because the refreshed baseline has no model-played campaign Victory.

A report, source check, host run, replay, deployment, and campaign result are separate evidence classes. Use the exact source revision and evidence kind beside each claim.

## Journey: spectator

1. **Arrive:** see the outcome-qualified title and evidence state. If there is no approved playable capture, CTA says “Read the run report.”
2. **Understand:** read the short outcome, build/configuration context, intervention disclosure, and source pointer.
3. **Inspect:** open the report, timeline, decision card, or replay receipt only when its manifest is approved.
4. **Participate:** make an anonymous local guess when a reviewed decision exists. Label this a guess-and-reveal, never a community vote.
5. **Return:** receive an approved next-question update or inspect a correction. No engagement action is required for access.

Events are aggregate only: run_page_view, meaningful_watch_or_read, decision_presented, decision_guess, decision_reveal, evidence_open, and a coarse return proxy. Do not join spectator identity to subscriber or runtime records.

## Journey: contributor

1. **Choose:** select a bounded good-first task from a public repository and confirm prerequisites.
2. **Prepare:** read the repository policy, expected command, source revision, and privacy exclusions.
3. **Change:** make the smallest diff that addresses the task; never include credentials, saves, raw trajectories, hidden prompts, or private host paths.
4. **Verify:** attach exact command/output and label source/test/host/public evidence separately.
5. **Review:** request code-owner review; accept corrections without rewriting historical evidence.
6. **Credit:** contributor name/handle and diff are published only with consent. A source check is not a gameplay or deployment claim.
7. **Next step:** receive one bounded follow-up task or documentation improvement; access is never gated on stars, follows, or shares.

Target public guidance: [AI-Ascension contribution guide](https://github.com/AI-Ascension/.github/blob/0cbdf744d515b16c042eb6e16b1537d8ccf11771/CONTRIBUTING.md). Verify current rules before inviting work.

## Journey: annotator

- Receive one approved public report or sanitized decision manifest.
- Agree to a time-boxed annotation, name/handle, recording, quotation, and correction/withdrawal terms.
- Read the fact layer before the commentary layer.
- Mark interpretation, uncertainty, and missing context.
- Review final copy and attribution before publication.
- Keep the source owner and creator owner distinct.

No annotator is assumed or named. Creator drafts are in marketing/creator-kit.

## Journey: challenge proposer

A proposal must contain the question, game/build scope, seed rule, observation/action interface, resource budget, intervention policy, expected evidence, and privacy statement. It must not include a private save, credential, raw trajectory, hidden prompt, or control endpoint. Maintainers accept, request changes, defer, or decline. An accepted proposal is not a result; only a reviewed public artifact can become a featured challenge.

## Journey: correction reporter

A correction can be submitted with content ID/URL, exact sentence or visual text, source URL/revision, reason, and requested disposition. Optional contact is handled separately from aggregate events. The maintainer acknowledges, investigates, records the source and update date, and preserves the dated historical record. A correction request does not become a public accusation or a deletion demand by default.

## Moderation rules

Remove or hold:

- credentials, access tokens, private saves, raw trajectories, private prompts, personal contact details, and private host paths;
- fabricated run results, screenshots, replay packages, endorsements, testimonials, or audience numbers;
- instructions to bypass gateway, game authority, authentication, lease fencing, or repository policy;
- vote manipulation, paid engagement, referral spam, bulk unsolicited outreach, or undisclosed sponsorship;
- personal attacks, harassment, doxxing, discriminatory abuse, and provider/model rivalry aimed at people.

Ask for a source revision and evidence class when someone makes a factual result claim. Keep good-faith disagreement visible when it identifies a missing field or alternative interpretation. Do not moderate criticism merely because it is unfavorable.

## Moderator response templates

### Privacy hold

“Please remove the private credential/save/trajectory or contact detail. The public discussion can continue with a sanitized summary and source revision. Do not paste secrets here.”

### Evidence request

“Can you link the exact source revision and identify whether this is source, test, host, replay, public artifact, or independently reproduced evidence? Until then, we will label the result unverified.”

### Correction accepted

“Thanks for the source pointer. We recorded the sentence, source revision, reviewer, and update date. The public copy will show the scope of the correction while preserving the dated source record.”

### Sponsorship disclosure

“Please add the support disclosure beside the affected content. Support cannot condition publication on a favorable outcome or purchase a benchmark claim.”

### Harassment boundary

“We can discuss the evidence and method. Personal attacks, doxxing, and pressure on contributors are out of bounds; further posts may be held for moderation.”

## Privacy and event boundary

Required marketing event fields are schema version, coarse timestamp, public content ID, event name, surface, optional campaign tag, and optional consented coarse cohort. Do not emit email addresses, private run IDs, model prompts, raw action payloads, secrets, saves, full private referrers, or device fingerprints. Server-side success must be verified at the server boundary; a button click is not quickstart_success.

Display “no observations” when a metric has not been collected. Do not present a local guess as a vote or raw runtime telemetry as public analytics. Keep observability systems private and separate from marketing events.

## Maintainer checklist

- [ ] Pin the source revision and evidence class.
- [ ] Verify destination and rights/consent.
- [ ] Check asset registry state; blocked art receives text fallback.
- [ ] Remove private data before moderation or export.
- [ ] Keep response, correction, and attribution records.
- [ ] Record aggregate events only after consent policy passes.
- [ ] Close or hand off the thread using the supported moderation workflow.

