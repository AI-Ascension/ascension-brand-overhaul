# ART-01 — From host boundary to inspectable report

Status: outline draft; one article per two-week pair.

- Audience: Developers and researchers
- Week pair: weeks 1-2
- Objective: Explain the path from host-independent source to report-only evidence without collapsing interfaces.
- Truthful hook: An inspectable report names its source boundary and evidence class before describing an outcome.
- CTA: Read pinned source files and evidence reports.
- Owner: W06-C1

## Outline
1. Architecture boundaries
2. source versus host evidence
3. Windows/Linux report scope
4. publication checklist.

## Source requirements
- `CAP-CORE-SEMANTICS` (offline_test): Host-independent typed state/action values, pure validation and in-memory tests; not a simulator or gameplay proof. Revision: `87e0f3d9355c0827e989d9fbc31804440852519b`.
- `HIST-WINDOWS-CAMPAIGN` (maintainer_reported_native_run): Dated visible Windows v0.107.1 practice campaign report: floor-17 Defeat, 333 settled operations, fresh complete replay; report-only. Revision: `cb17b6c15262ce9356f1e85fd475af997aedc445`.
- `HIST-LINUX-CAMPAIGN` (maintainer_reported_native_run): Dated visible Linux v0.107.1 practice campaign report: one controller restart, floor-24 Defeat, 431 settled operations, fresh complete replay; report-only. Revision: `cb17b6c15262ce9356f1e85fd475af997aedc445`.
- `HIST-PUBLIC-PROOF` (public_report): Historical public browser replay of a stale-epoch gateway contract test; not game or model-play evidence. Revision: `bbe475998b0cd279309666f5cec3dc433d90a4a4`.

## Destinations
- [planned_local_destination](https://aiascension.tech/docs): Docs route is a local implementation destination until deployed.
- [real_source_repository](https://github.com/AI-Ascension/sts2-harness): Source repository is implementation context.

## Assets
- `DOC-01`: blocked; ORCH-NATIVE-SPAWN-UNAVAILABLE; IMAGE-BACKEND-UNVERIFIED; ART-PROVENANCE-ABSENT. No delivered visual is claimed.
- `DOC-02`: blocked; ORCH-NATIVE-SPAWN-UNAVAILABLE; IMAGE-BACKEND-UNVERIFIED; ART-PROVENANCE-ABSENT. No delivered visual is claimed.
- `WEB-07`: blocked; ORCH-NATIVE-SPAWN-UNAVAILABLE; IMAGE-BACKEND-UNVERIFIED; ART-PROVENANCE-ABSENT. No delivered visual is claimed.

## Rights and approval
- Status: `draft_only`; send/publish authorized: `false`.
- Gate: Every architecture claim needs its exact source revision.

## Measurement
- Event: `meaningful_watch_or_read`
- Numerator: Readers reaching source table and opening a source pointer
- Denominator: Eligible article starts
- Window: 35 days after approval
- Stop rule: Stop if five reviewers cannot state the evidence class.
- Result status: `unobserved`.
