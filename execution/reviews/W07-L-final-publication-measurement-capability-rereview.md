# W07-L final re-review: publication, measurement, and capability boundaries

This review checks the five findings carried from the earlier W07-L 5b review
against an exact archive of source revision
`0e03d97bc6af6b7622d33d830bdde1eef1c2b1d8`. The relevant repairs are present
through `1a9ef67` (capability provenance and URI schemes), `cf88c46` (measurement
semantics and scope currentness), and the preceding publication repair at
`5b752cd49c16a5bec32816a09dd93920bb419437`; `2239569` and `0e03d97` add later
helper/content-sync work without changing these five reviewed boundaries. No
production approval, measurement receipt, network operation, or live
publication was created.

## Verification

- `python3 -m unittest discover -s tests -v` — **170 passed** in 17.327 seconds.
- Focused publication, measurement, and capability regression set — **66
  passed** in 14.585 seconds.
- `python3 -m py_compile publisher/*.py` and all focused test modules — passed.
- The exact frozen tree contains empty trusted registries:
  `config/publication-authorities.json` has zero approvals and
  `config/measurement-authorities.json` has zero receipts.
- All checks ran from a temporary archive of the frozen commit. Tests and
  adversarial probes used temporary inputs and local registry patches only; no
  remote or live service was contacted.

## Final finding dispositions

### W07-PUB-10 — Opaque URI schemes in emitted free text: addressed

`publisher/security.py:14-38` now scans scheme tokens even when they do not
contain `://`, along with protocol-relative and root-relative candidates. It
also validates every URI in the approved register with `safe_public_url` before
matching text. `publisher/validate.py:328-341` applies the check to the actual
allowlisted public projection after structured URI checks, so escaping cannot
hide a private value. `publisher/capability_renderer.py:50-56` applies the same
check to approved capability records.

A fresh production-projection probe rejected each of
`mailto:private@example.invalid`, `data:text/plain,PRIVATE`,
`javascript:private`, `urn:secret`, and `file:/private` with
`URL-like text is outside the approved public URI register`. The approved
parenthesized HTTPS-link case still passed. The capability regression probe
also rejected ordinary HTTPS, `mailto:`, and `data:` URLs embedded in claim
text. The false-negative finding is closed for both run and capability output.

### W07-MEA-07 — Mutable/unbound event-contract semantics: addressed

`publisher/events.py:21-35` reads the contract with
`unique_schema_object`, a 1 MiB bound, and strict schema/semantic validation.
`publisher/measurement_scope.py:23-25` derives a semantics digest from the
full contract and the installed publisher/schema/token digest;
`require_scope` requires that digest at `:43-53` before accepting an enrolled
receipt. The receipt schema requires `measurement_semantics_digest` at
`schemas/measurement-scope.schema.json:83-113`.

A duplicate `surface` member in a temporary contract failed before semantic
validation. Changing a metric numerator while reusing the enrolled receipt
failed with `measurement receipt semantics revision is stale`. This binds both
privacy/event rules and metric definitions to the trusted scope identity.

### W07-MEA-08 — Stale or future scope receipts: addressed

The receipt schema now requires an explicit `reporting_mode` and `reviewed_at`.
`require_scope` parses the cutoff, review time, and evaluation clock at
`publisher/measurement_scope.py:75-86`; it rejects future cutoffs/reviews,
requires current receipts to be within the documented 24-hour review and
48-hour cutoff bounds, and allows old data only through explicit historical
mode. `publisher/events.py:155-164` preserves the mode, exact bounds, review
and evaluation context, and complete/partial window state in output.

A current receipt from 2020 was rejected as stale. The same old data with an
explicit historical receipt was accepted and labelled
`historical_observation`. Receipts with either a 2099 cutoff or 2099 review time
were rejected in both current and historical modes. The stale/future finding is
closed under the documented operator clock and historical mode contract.

### W07-CAP-01 — Incomplete W01 capability envelope: addressed

`publisher/capabilities.py:56-94` parses the envelope with duplicate-key
rejection and validates it against the strict local schema. The schema requires
all collection, source, baseline, review-boundary, claim-policy, and capability
fields at `schemas/capability-registry.schema.json:127-135`, with nested required
fields and types at `:31-117`. The list compatibility form remains explicitly
metadata-free and is labelled as such by the renderer; an envelope cannot use
that weaker provenance lane accidentally.

A minimal envelope containing only `schema_version` and `capabilities` failed
with a missing `collected_at` schema error. The focused provenance tests also
removed each required field and supplied malformed types; every case failed.
The incomplete-envelope finding is closed.

### W07-CAP-02 — Unregistered URLs in capability claim text: addressed

For approved public output, `publisher/capability_renderer.py:43-56` requires
approved, dated records, validates every approved URI, scans all record text
with `require_approved_text_uris`, and then checks the fixed deployment approval
registry. The scan covers claims, labels, revisions, status, and source fields
recursively before HTML rendering.

A fresh capability probe with claims containing
`https://private.example/secret`, `mailto:private@example.invalid`, and
`data:text/plain,private` rejected each value before output creation. The full
capability provenance test additionally confirmed that no output file remains
on rejection. The claim-text privacy finding is closed for the public
capability path.

## Publication and authority boundary

The earlier 5b publication repairs remain present in the frozen tree. The
publisher separates manifest, approval, artifact, and output parents at
`publisher/publisher.py:121-132`; validates all structured and emitted-text URIs
at `publisher/validate.py:328-341`; bounds artifact roots in
`publisher/security.py:162-197`; and keeps a complete private output inventory
under `publisher/output_state.py:21-145`. The 66 focused tests cover these
boundaries as well as the five repaired findings.

These results establish source-level and local regression evidence only. Empty
trusted registries, absent operator approval, absent production event streams,
and absent served-route evidence mean this re-review grants no publication,
analytics, deployment, or release authority.

## Review disposition

W07-PUB-10, W07-MEA-07, W07-MEA-08, W07-CAP-01, and W07-CAP-02 are addressed at
the frozen source revision. No production record, approval, measurement result,
or live publication was created.
