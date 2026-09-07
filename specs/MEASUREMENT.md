# Privacy-minimal measurement and growth evaluation

Use separate audience and developer funnels. Audience: eligible impression/view → engaged episode or run page → decision interaction/inspection → return visit. Developer: docs visit → attempted setup → completed useful workflow → repeat use or contribution. Stars and followers are secondary context, not the north-star objective.

Define events with schema version, coarse timestamp, public content ID, event name, surface, campaign tag where appropriate, and only optional consented coarse session/cohort state. Never emit email addresses, private run IDs, model prompts, raw action payloads, secrets, saves, account tokens, full referrers with private queries, or device fingerprints. Use anonymous aggregation where practical. Do not reuse private runtime telemetry as public marketing analytics.

Required event concepts: run_page_view, media_start, meaningful_watch_or_read, decision_presented, decision_guess, decision_reveal, evidence_open, replay_download, build_start, quickstart_success, docs_error, subscribe_confirmed, and unsubscribe_completed. Server-side success signals must not be inferred from button clicks. Never treat an unverified client self-report as measured installation success without labeling that limitation.

Each metric must define numerator, denominator, exclusion rules, time window, bot/test filtering, attribution limits, and privacy retention. If repeat-user identity cannot be measured without unwanted tracking, use aggregate return proxies or consented cohorts and explain the limitation rather than fingerprinting users. Distinguish a complete case-study view from an impression. A logged local guess is not a community vote.

Dashboard sections: traffic source and eligible denominator; content engagement; run/evidence inspection; returning engagement; developer activation; contributor repeat participation; infrastructure/publication failures; and corrections. Display absent data as no observations, not zero conversion. Keep experimental configuration changes and audience changes in the result notes.

For comparative agent outcomes, define the evaluation population, attempted runs, exclusions, intervention rules, game build, model configuration, action/observation interface, seed policy, time/token/resource budgets, and infrastructure-failure handling. Report uncertainty and sample size. Show failures and unsuccessful attempts rather than cherry-picking a montage into a benchmark.

The executor must implement event validation and documentation, consent gating where needed, retention/deletion behavior, and a synthetic non-production test dataset. It must not invent real visitors, subscribers, creators, installs, costs, or conversion results. Longitudinal outcomes remain unobserved until collected.

## Mandatory artwork source

All new artwork, including promotional images, exported diagrams, card artwork, icons, and creative revisions, follows `art/ASTRA_GPT_IMAGE_2_POLICY.md`: an actual `gpt-6-astra` author writes each final prompt and `gpt-image-2` generates the art. Functional HTML/CSS/data and approved real evidence are separate. Runtime serving uses already approved images with no implicit model calls. Missing art-model access blocks that asset, never authorizes code-drawn or reused-art substitutions.
