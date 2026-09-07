# W07-L independent review: publisher and measurement

Reviewed the integrated `work/brand-overhaul` tree at `df532bd36f99f3c2fac5ae51c093d7b8bd191f0b`, including the root-authored UI repair in `df532bd`. The review covers `publisher/`, the publication/action/event/comparison schemas, `analytics/`, `docs/PUBLISHING.md`, `docs/MEASUREMENT.md`, and the publication/measurement tests. No production record, approval record, network operation, or live publication was created.

The current root UI repair is substantively present. `publisher/render.py:68-77` puts the timeline result behind a native `details` disclosure, `publisher/render.py:95-98` keeps the local consequence behind the explicit reveal, and `publisher/render.py:121-132` embeds the checked-in token CSS, records its digest, and makes the table wrapper keyboard-focusable. The current fixture page rendered with escaped record text, no active HTML from the fixture, a usable mobile overflow region, and visible focus outlines. The root's `execution/publisher-ui-checks.json` correctly labels this evidence synthetic and keeps independent review pending.

## Verification

- `python3 -m unittest discover -s tests -v`: **98 passed**.
- `python3 -m unittest tests/test_publication.py tests/test_publication_input_boundaries.py tests/test_publication_render_behavior.py tests/test_measurement.py -v`: **27 passed**.
- The existing tests cover missing approval, changed digest, private/synthetic/forced-fixture rejection, unsafe URLs, input/output symlinks, 4 MiB input bounds, duplicate input keys, escaping, consent/server gates, synthetic event filtering, and exact rerender idempotency.
- Independent adversarial probes found the issues below. In particular, an approved manifest with an unapproved nested action card passed production validation; an approved top-level card whose digest was absent from an empty artifact root passed; an approved `report_only` record with an available action timeline passed; conflicting duplicate event IDs produced different results when input order changed; and a server-confirmed `quickstart_success` with `status: failed` produced a 1.0 activation rate.

## Findings

### W07-PUB-01 — The publication manifest schema has duplicate top-level object members (blocker)

`schemas/publication-manifest.schema.json` defines top-level `properties` three times at lines 236, 391, and 552. The first two definitions are silently discarded by the ordinary `json.loads` call in `publisher/schema.py:26-39`; a strict duplicate-key reader reports both duplicate members. The shipped validator therefore tests only the last definition, while another JSON implementation may reject the schema or retain a different definition. This violates the strict-schema acceptance boundary and makes the contract parser-dependent.

Remove the duplicate blocks and add a schema-file duplicate-key check. The input duplicate-key check in `publisher/publisher.py:25-31` does not protect the checked-in schemas because `publisher/schema.py:34` uses ordinary `json.loads`.

### W07-PUB-02 — Artifact lineage is metadata-only, and nested action cards bypass approval (blocker)

`publisher/publisher.py:81-82,97-99,117-119` passes an optional artifact root only to `inspect_artifact_root`; `publisher/security.py:134-153` checks hidden names and symlinks but never maps an asset ID to a file or hashes file content. The otherwise suitable `checked_path` helper at `publisher/security.py:111-131` is never called. `publisher/validate.py:280-288` checks only the manifest's top-level `decision_card` ID/digest against `approved_assets`.

This permits a top-level card with `asset_id: missing-art` and digest `b...b` to publish with an empty artifact root. It also permits an available `action_timeline.decisions[].decision_card` with an unapproved ID/digest and `/private/provenance.json`; `publisher/validate.py:96-100` checks that it has fields and a syntactically safe URL, but the production gate never checks that nested card against the approval. The nested card is retained in the published `manifest.json`, so omitting it from the HTML does not remove the publication-boundary failure. The acceptance statement in `execution/w05-implementation.json:84-93` and the requirement in `specs/PUBLICATION.md:21,35` require referenced digest identity and complete lineage for any decision card.

Require an approved artifact root and explicit asset-path mapping, hash the real file after rejecting symlink/traversal, and apply the same approval check recursively to every action decision card (or prohibit nested cards at this boundary).

### W07-PUB-03 — Report-only records can publish invented action decisions (blocker)

`docs/PUBLISHING.md:58-66` directs historical `report_only` intake to use an unavailable action timeline and zero local options because raw trajectories are unavailable. `publisher/validate.py:75-106` validates only the timeline's internal status/ID/sequence invariants; it never relates `evidence_kind` or `evidence_context.capture_scope` to timeline availability. Consequently the repository's own approved test shape (`tests/test_publication.py:24-61`) has `evidence_kind: report_only`, `evidence.availability: report_only`, an available decision timeline, and an available local guess, and it passes `validate_production_publication`.

Either enforce `report_only -> action_timeline.status=unavailable` and `local_guess_reveal.status=unavailable` with `legal_option_count=0`, or add an explicit source-owner action-record provenance contract and validate it before allowing those fields into production.

### W07-PUB-04 — Source-reference lineage is not cross-validated (high)

`publisher/validate.py:152-158` checks membership only for `case_study.source_reference`. It does not check `evidence_context.source_reference` or `action_timeline.decisions[].explanation.source_reference` against `source.references`, and the schema does not require unique source-reference labels. An otherwise valid manifest can therefore carry an unlisted provenance label or ambiguous duplicate labels into the public projection. `safe_public_url` also accepts a root-relative path such as `/private/provenance.json`; syntax safety does not establish public rights or source identity.

Require unique source labels and validate every source-reference field against the same source register, with an explicit approved-public URI/reference policy.

### W07-PUB-05 — Approval field scope is effectively all-or-nothing, and authority is not authenticated (high)

`publisher/validate.py:20-45` lists every top-level manifest field in `REQUIRED_APPROVAL_FIELDS`; `publisher/validate.py:262-265` then requires each one to be approved at complete top-level scope. This makes `allowed_fields` unable to withhold a field from the rendered page. In particular, `publisher/render.py:156-161` always emits `source.content_digest`, even though `specs/PUBLICATION.md:7` warns that a private source hash can itself be sensitive and says only approved lineage may be exposed.

Separately, `schemas/publication-approval.schema.json:10-18` treats `authority_reference` as free text. `publisher/validate.py:174-180` validates shape and duplicate asset IDs but does not authenticate an issuer, signature, or trusted approval registry. A caller able to supply files can construct a digest-matching approval with arbitrary authority text. This is an operator-trust assumption, not an independently enforced production authority boundary. Define a real allowlist/projection policy for optional fields and an authenticated or trusted approval source before treating this as standalone production publication.

### W07-PUB-06 — Publication output is not atomic and idempotency ignores extra files (high)

`publisher/publisher.py:145-157` writes `manifest.json` and then `index.html` directly. If the second write fails, the destination retains a partial manifest; a retry then raises `DuplicatePublicationError` for an incomplete version. An existing version is considered idempotent after comparing only those two files at `publisher/publisher.py:145-154`; extra files, hidden files, and an extra symlink are not inventoried. An adversarial rerender accepted a pre-existing `secret.txt` and a symlink to an external file while returning `idempotent=True`.

Stage both files in a new sibling directory, flush/rename atomically, and require an exact safe destination inventory before returning idempotent. On failure, remove only the publisher-owned temporary directory and leave a retryable destination state.

### W07-MEA-01 — Conflicting duplicate event IDs make aggregation order-dependent (blocker)

`publisher/events.py:119-128` silently keeps the first event for each `event_id`. It does not require later records with the same ID to be byte/canonical-equivalent. A production `run_page_view` and a production `meaningful_watch_or_read` sharing one ID produced `audience-engagement-rate = 0.0` in page-then-watch order and `no_observations` in watch-then-page order. This violates deterministic measurement and permits conflicting retries to change reported results.

Reject a duplicate ID unless its canonical event payload is identical, or reconcile through a server-owned immutable event store before aggregation.

### W07-MEA-02 — Success-event states are not semantically gated (high)

The contract calls `quickstart_success` a useful completion at `analytics/event-contract.json:92-98`, but `publisher/events.py:78-90` checks only required property names, consent, and the boolean-like server observation. The shared status enum accepts `failed`, and `publisher/events.py:140` counts every `quickstart_success` event in the activation numerator. A granted, server-confirmed `quickstart_success` with `status: failed` is accepted and yields activation `1.0` when paired with one `build_start`. The same ambiguity applies to the confirmed subscription event names at `analytics/event-contract.json:110-125`.

Require `status: completed` for success/completion event names, use a distinct failure event or state for failed attempts, and count only the semantically successful state.

### W07-MEA-03 — Documented metric windows, eligibility, and bot/test exclusions are not implemented (high)

The contract declares calendar-week windows and eligible public run-page denominators at `analytics/event-contract.json:134-167`, with bot/test and missing-content exclusions. `aggregate_events` accepts no time window or current-time parameter and aggregates every supplied event at `publisher/events.py:108-140`. It has no public-content registry/eligibility check, bot/test filter, or infrastructure-failure input; any syntactically valid `content_id` in an event labeled `production` enters the denominator. The dashboard specification promises these exclusions at `analytics/dashboard-spec.md:13-17,31-37`, but the offline implementation cannot enforce them.

Either make the upstream server filtering and window/eligibility receipt an explicit trusted input, or implement date-bounded aggregation against a public-content and server-rule registry. Until then, results are only unscoped event counts and must not be presented as the documented dashboard metrics.

### W07-MEA-04 — An anonymous cohort value is accepted without consent (high privacy issue)

`schemas/event.schema.json:26-38` permits `coarse_cohort.kind: anonymous` with a non-null bucket. `publisher/events.py:91-96` gates only `consented_cohort`; an event with `consent_state: not_collected` and `{"kind":"anonymous","value":"bucket-a"}` validates. This conflicts with the contract's `optional_consented_coarse_cohort` privacy declaration at `analytics/event-contract.json:3-7` and permits an unconsented repeat-tracking value to be stored, even though the current proxy does not count that kind.

Disallow a non-null cohort value unless consent is granted, or remove the anonymous-valued variant and retain only an explicitly non-identifying `none` state.

### W07-MEA-05 — Synthetic/production and same-start claims are caller assertions (medium)

Events carry `environment` and `server_observation` as ordinary schema values. There is no trusted source or server receipt; changing a synthetic fixture's environment to `production` makes it count, and the validator accepts a caller-supplied `server_observation: confirmed` once the other fields match. This is acceptable only if an external server owns and authenticates the event stream; the offline package does not enforce the claim.

Similarly, `publisher/comparison.py:29-32` accepts a `same_start` comparison when `same_start_required` is true, but `schemas/comparison.schema.json:20-35` contains no start identity, seed digest, or source reference. A comparison can therefore assert same-start context without evidence. Add a verifiable start identity/digest or keep such comparisons exploratory.

### W07-MEA-06 — Capability rendering bypasses the publisher's output safety (medium)

`publisher/capability_renderer.py:12-19` writes directly to the caller's output path without `reject_symlink_path`, `ensure_separate_output`, atomic staging, or a production/synthetic classification gate. A valid `offline_test` capability registry can be rendered into its own source tree or an arbitrary pre-existing file. This helper is outside the run `publish` method, but it is part of the W05 capability-rendering output and should inherit the same safe-output contract before any generated capability page is treated as public.

## Residual contract gaps

`publisher/validate.py:160-164` checks only that an available local guess has at least one option; it does not require `legal_option_count` to equal the first decision's legal-choice count, or require an unavailable guess to report zero. `publisher/validate.py:96-100` likewise permits an action timing record with `captured: true` and no media offset. These are lower-severity metadata inconsistencies but can make a page claim an interaction or media alignment that its own record does not support.

The root-authored token embedding makes the current fixture page visually coherent and records the token digest, but the token/template revision is not part of the approval digest. A later `brand/tokens.css` or renderer change can produce a different page for the same approved manifest; approval should pin the renderer/token revision if byte-stable rerender is required.

## Review disposition

The integrated tests and root UI repair pass their declared local checks, and the offline package has no provider, HTTP, game-control, or host-runtime call path. The production and measurement boundaries remain blocked by W07-PUB-01 through W07-PUB-03 and W07-MEA-01; the remaining findings need resolution or an explicit operator-trust/measurement-scope decision before a production acceptance record is appropriate. This review does not approve publication or create an approval record.
