# Privacy-minimal measurement contract

W05 measurement is an event contract and a reviewable dashboard definition,
not a claim about current traffic. The source baseline and any real analytics
observations remain the responsibility of W01 and the eventual deployed
operator.

The audience funnel is eligible impression or view → meaningful episode or run
page engagement → decision presentation and interaction → evidence inspection
→ a consented coarse repeat-visit proxy. The developer funnel is docs visit →
setup start → server-confirmed useful workflow → repeat use or contribution.
Stars and followers are context only.

The capability renderer accepts either a list of records matching the existing
`schemas/capability.schema.json` or W01's
`ai-ascension.capabilities.v1` envelope. It preserves exact source IDs and
revisions, including uppercase IDs, and only sorts a copy for display. It does
not treat a source-derived record as an independent reproduction or release
support, and it does not create a current claim when W01 has not supplied a
dated source.

Every event uses `event-v1` and includes a public content ID, a coarse day or
minute timestamp, event name, surface, optional campaign tag, consent state,
optional consented cohort, server-observation state, environment, and a small
allowlist of coarse properties. The validator rejects unknown fields and
sensitive fields. A local guess is an anonymous local interaction; it is not a
community vote and produces no aggregate count in the publisher.

The contract keeps game outcomes, infrastructure failures, publication errors,
and client validation errors distinct. Server-confirmed subscription and
quickstart events cannot be inferred from a button click. If repeat identity
cannot be measured without tracking people, the dashboard shows an aggregate
cohort proxy or `No observations`.

Run `python3 -m unittest tests/test_measurement.py -v` for the synthetic local
checks. The synthetic records and their metric output are local test data and
must not be used as production observations.


## Trusted scope and exclusions

`aggregate_events(events, scope_receipt=receipt)` requires an operator-enrolled `measurement-scope-v1` receipt whenever production observations are supplied. A caller changing `environment` or `server_observation` does not establish authority. The fixed deployment file `config/measurement-authorities.json` ships empty; the deployment owner enrolls the exact canonical SHA-256 of a reviewed upstream receipt. There is no input/CLI/environment registry override. Protect installed code and the registry from content authors. This trusts the enrolled upstream collector's event origin, server completion checks, and bot/test/infrastructure classifications; the offline package is not itself a collector or authentication service.

The receipt binds the canonical event stream after exact retry deduplication, an eligible public-content ID snapshot, its digest, a server-rules reference, and explicit excluded event IDs/reasons. `public_content_registry_digest` is the SHA-256 of canonical JSON for the sorted eligible ID array. Conflicting duplicate event IDs fail before filtering. Unknown exclusion IDs, invalid calendar boundaries, changed event bytes, changed scope, or an unenrolled receipt fail closed.

Weekly metrics use `[Monday 00:00 UTC, next Monday 00:00 UTC)`. The cohort proxy separately uses `[month start 00:00 UTC, next month start 00:00 UTC)`. Both exclude events beyond the receipt's `observed_through` cutoff. Output declares the exact bounds and whether the week/month was complete at the cutoff; partial windows are not full-period results. All metrics exclude synthetic events, ineligible public content IDs, and the receipt's bot/test/infrastructure exclusions. No eligible observations remain `None`.

`include_synthetic=True` is explicitly `local_unscoped_test`; it exercises calculations without claiming a production reporting window. Empty input without a receipt reports no observations. The package neither enrolls production receipts nor stores or deletes a deployed event stream; the 90-day retention policy remains an operator responsibility.


## Capability previews and public outputs

`python3 -m publisher.capability_renderer RECORDS.json OUTPUT.html` creates an explicitly labelled local preview. It refuses output within the input tree, symlink ancestors, and existing destinations. It installs a complete file atomically without replacing an existing file; a failed install removes only its own temporary file. JSON input is bounded to 4 MiB and duplicate object keys fail.

Add `--approval CAPABILITY_APPROVAL.json` only for reviewed public output. A `capability-approval-v1` record binds the SHA-256 of canonical `{"records": validated_sorted_records, "metadata": registry_metadata_or_null}`, the exact renderer digest, and approved source URLs. Every public record needs approved, dated review. The same fixed deployment approval registry used by the run publisher must contain the exact approval digest. The shipped registry remains empty. Evidence kind stays separate from review and release support: an approved offline-test record remains an offline-test record.

An envelope must supply every collection, source, baseline, review-boundary, and claim-policy field with the types in `schemas/capability-registry.schema.json`; partial envelopes fail. The compatibility list form has no collection envelope and displays that limitation on both preview and public pages. Public capability text uses the same URI register checks as run pages, including opaque scheme strings such as `mailto:` and `data:`. Escaped text still needs rights review.

## Same-start comparison evidence

Exploratory comparisons remain available without a same-start claim. A `same_start` comparison or `same_start_required` rule requires `start_evidence_root` and a per-run `start_evidence` path/digest. The validator reads each bounded, symlink-free `comparison-start-v1` file, verifies its bytes, and compares its game build, source-owned seed digest, and initial-state digest. A matching policy string alone is insufficient. Changed bytes, differing identities, missing files, or a game-build mismatch fail.

These are comparisons of supplied source-owned start records. The offline tool does not reproduce the initial game state, recover a hidden seed, authenticate a gameplay host, or authorize the records for public release. Source owners must sanitize and review those records; private seed/state hashes can themselves be sensitive. Ranking claims remain disabled, and renderer output continues to disclose comparison context and limitations.
