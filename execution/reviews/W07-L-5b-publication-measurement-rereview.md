# W07-L independent re-review at 5b752cd

This review rechecks the integrated publication, measurement, capability, and
comparison repairs at 5b752cd49c16a5bec32816a09dd93920bb419437 in the canonical
work/brand-overhaul tree. The next root commit, 13e4cc5, changes only execution
records and documentation; none of the reviewed implementation or schema files
changed between those heads. No production record, approval, measurement
receipt, network operation, or live publication was created.

## Verification

- python3 -m unittest discover -s tests -v: 149 passed in 59.214 seconds.
- The focused publication, measurement, capability, comparison, and review
  repair tests are included in that exact-head run. The checked-in
  config/publication-authorities.json and config/measurement-authorities.json
  contain zero enrolled records.
- Positive checks confirmed disjoint manifest/approval/artifact/output trees,
  complete output inventories, staged publication files, real matching raster
  bytes for top-level and nested cards, bounded artifact scans, conflicting
  event retry rejection, completion and consent gates, enrolled scope receipts,
  bounded same-start evidence, and renderer/approval digest binding.

## Findings

### W07-PUB-10 — Free-text URI scanning misses schemes without :// (high privacy risk)

publisher/validate.py:338-354 scans scheme tokens with the pattern
[A-Za-z][A-Za-z0-9+.-]*://, plus protocol-relative and root-relative paths.
It therefore does not inspect mailto:, data:, javascript:, urn:, or single-slash
file:/ tokens in an approved projection. This is narrower than
docs/PUBLISHING.md:131-135, which says scheme URLs in all emitted free text
must be in the exact public URI register.

With an otherwise valid enrolled approval, these disclosures were accepted and
written to index.html:

  mailto:private@example.com ACCEPTED True
  data:text/plain,PRIVATE ACCEPTED True
  javascript:private ACCEPTED True
  urn:secret ACCEPTED True
  file:/private ACCEPTED True

HTML escaping prevents the javascript: string from becoming an executable link
in this renderer, but it does not prevent a private address or data URL from
being displayed. Detect every URI-scheme token and require it to be an exact
approved URI, while retaining the existing HTTPS/root-relative safety check for
approved values. The current structured URI checks and the ://-style free-text
tests pass; this is a false-negative boundary in the newer all-free-text
invariant.

### W07-MEA-07 — Event-contract semantics are parser-dependent and unbound to a scope receipt (high)

publisher/events.py:21-29 loads analytics/event-contract.json with ordinary
json.loads; unlike the event and receipt readers, it does not use the strict
duplicate-key hook. A temporary contract with two surface members loaded as
the last member (watch) and passed contract validation. The semantic helper at
publisher/events.py:40-50 rejects duplicate event names, but it cannot see
duplicate object members already discarded by the parser.

More broadly, publisher/measurement_scope.py:33-62 binds the enrolled receipt
to the event bytes, eligible content IDs, and receipt digest. It does not bind
the event-contract or metric-definition digest. Replacing the decision_guess
definition so consent_required was false let a not_collected guess through and
produced a decision-interaction-rate of 1.0 under the same event-stream receipt.
A changed installed contract can therefore change privacy and metric semantics
without invalidating an enrolled receipt.

Read the contract with strict duplicate detection and bind the reviewed
contract/metric-definition revision to the scope receipt and its deployment
registry, or make the contract an immutable part of the renderer authority
digest.

### W07-MEA-08 — Enrolled scope receipts have no currentness or future-data bound (high)

publisher/measurement_scope.py:63-78 validates Monday/first-of-month boundaries,
ordering, and exclusion IDs, but accepts any historical or future
observed_through value. publisher/events.py:142-155 declares a week or month
complete solely by comparing that receipt cutoff with the period end; it has no
now/deployment-time argument or retention/freshness policy.

Two separately enrolled temporary receipts were accepted with one production
event each:

  stale accepted_event_count 1 week_complete True week_start 2020-09-07T00:00:00+00:00
  future accepted_event_count 1 week_complete True week_start 2099-09-07T00:00:00+00:00

The operator-enrolled receipt is an explicit trust boundary, so this is not a
claim that an untrusted caller can edit the shipped empty registry. It does
mean a stale or future receipt can be presented as a complete current metric
once an operator enrolls it. Require an explicit historical/as-of mode, a
deployment-time freshness and future cutoff check, or a displayed receipt
review date before treating the result as a dashboard observation.

### W07-CAP-01 — The W01 capability envelope may omit its provenance envelope (medium/high)

publisher/capabilities.py:61-93 checks unknown top-level and nested field names
but does not require the fields listed in W01_REGISTRY_FIELDS at
publisher/capabilities.py:14-23, nor does it type-check collected_at,
source_snapshot, baseline_package_revision, review_boundary, or claim_policy.
An envelope containing only
{"schema_version":"ai-ascension.capabilities.v1","capabilities":[...]} was
accepted with metadata keys ['schema_version'].

After the contained record was given a dated approved review, the incomplete
envelope also produced public output with an enrolled capability approval:
minimal_envelope_public_output True. This leaves a public capability page
without the W01 collection and review boundary described by
docs/MEASUREMENT.md:14-20 while its approval digest still appears valid.

Require the W01 envelope fields and their types, or explicitly mark an
incomplete envelope as a local/partial record that cannot use the public
approval path. The existing list-form compatibility lane can remain separate
if its weaker provenance is made explicit.

### W07-CAP-02 — Capability approval checks source URLs but not rendered claim text (high privacy risk)

publisher/capability_renderer.py:43-54 requires each record's source_url to be
approved and syntax-safe. publisher/capabilities.py:109-137 then renders
arbitrary claim, labels, revisions, and status text after HTML escaping,
without applying the publication URI register to those values.

An enrolled capability approval whose only approved URI was the fixture source
URL accepted a record with the claim
Reviewed claim https://private.example/secret; the private URL was present in
the generated public HTML
(capability_unregistered_free_text_url_emitted True). Apply the same
all-emitted-text URI scan used by run publication, or make capability claims
structured and require every URL-like value to be listed in the approval.

## Comparison disposition

The same-start repair is sound for the local contract it states. At
publisher/comparison.py:37-59, a same_start claim requires a source-owned
evidence root and per-run path/digest, rejects symlinks and traversal through
checked_path/inspect_artifact_root, limits each file to 1 MiB, rejects duplicate
JSON keys, validates comparison-start-v1, and compares the source-owned
game-build, seed, and initial-state identities. The exact tests cover missing
evidence, changed bytes, differing identities, and build mismatches.

This remains source-owner evidence rather than independent gameplay attestation.
docs/MEASUREMENT.md:57-61 correctly states that the offline tool does not
reproduce the game state, authenticate a host, or authorize a public release.
A public comparison still needs source-owner rights/review and any separate
publication approval; a matching policy string alone is no longer accepted.

## Publication and authority disposition

The 5b repairs close the earlier output-root, artifact-byte, raster-limit, and
structured/free-text :// checks: publisher/publisher.py:121-132 separates
manifest, approval, artifact, and output parents; publisher/validate.py:315-328
maps every available top-level and nested card to a real approved file;
publisher/security.py:134-169 bounds and rejects unsafe artifact roots; and
publisher/output_state.py:21-53,69-120 inventories the complete managed output
tree under a private lock and ledger. The 149-test run exercises those repairs.

The URI-scheme false negative above remains. The installed publication registry
has no approvals, and the measurement registry has no receipts, so this review
does not establish a production publication or observed metric. Operator
permissions, installed-code identity, source-owner rights, and live served
routes remain separate deployment gates.

## Review disposition

The reviewed local repairs pass their exact-head regression suite. W07-PUB-10,
W07-MEA-07, W07-MEA-08, W07-CAP-01, and W07-CAP-02 remain open; no production
approval is granted and no production record was created.
