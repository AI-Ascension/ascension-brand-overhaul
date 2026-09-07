# ART-03 — Model, control and replay are separate claims

Status: outline draft; one article per two-week pair.

- Audience: Developers and evaluation readers
- Week pair: weeks 5-6
- Objective: Explain why model identifier, settled action and replay result require different evidence.
- Truthful hook: A model name in configuration is not a ranking, and a settled action is not a verified win.
- CTA: Use evidence vocabulary in pinned baseline.
- Owner: W06-C1

## Outline
1. Configuration/date
2. provider port
3. settled/requested actions
4. intervention
5. season evidence check.

## Source requirements
- `HIST-WINDOWS-CAMPAIGN` (maintainer_reported_native_run): Dated visible Windows v0.107.1 practice campaign report: floor-17 Defeat, 333 settled operations, fresh complete replay; report-only. Revision: `cb17b6c15262ce9356f1e85fd475af997aedc445`.
- `HIST-LINUX-CAMPAIGN` (maintainer_reported_native_run): Dated visible Linux v0.107.1 practice campaign report: one controller restart, floor-24 Defeat, 431 settled operations, fresh complete replay; report-only. Revision: `cb17b6c15262ce9356f1e85fd475af997aedc445`.
- `W01-SNAPSHOT` (source_snapshot): W01 current source and capability baseline collected 2026-09-07. Revision: `5a2acfd6690d2533af046a7afcf3a7782b29042b`.

## Destinations
- [planned_local_destination](https://aiascension.tech/docs): Docs route is a local implementation destination until deployed.
- [real_source_repository](https://github.com/AI-Ascension/sts2-harness): Source repository is implementation context.

## Assets
- `RUN-01`: blocked; ORCH-NATIVE-SPAWN-UNAVAILABLE; IMAGE-BACKEND-UNVERIFIED; ART-PROVENANCE-ABSENT. No delivered visual is claimed.
- `RUN-05`: blocked; ORCH-NATIVE-SPAWN-UNAVAILABLE; IMAGE-BACKEND-UNVERIFIED; ART-PROVENANCE-ABSENT. No delivered visual is claimed.
- `MKT-03`: blocked; ORCH-NATIVE-SPAWN-UNAVAILABLE; IMAGE-BACKEND-UNVERIFIED; ART-PROVENANCE-ABSENT. No delivered visual is claimed.

## Rights and approval
- Status: `draft_only`; send/publish authorized: `false`.
- Gate: Refresh revisions before model-specific copy.

## Measurement
- Event: `meaningful_watch_or_read`
- Numerator: Readers reaching source table and opening a source pointer
- Denominator: Eligible article starts
- Window: 35 days after approval
- Stop rule: Stop if five reviewers cannot state the evidence class.
- Result status: `unobserved`.
