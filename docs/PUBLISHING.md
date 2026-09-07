# Offline public run publishing

W05 supplies a deterministic, read-only publisher for sanitized run records.
It has no HTTP client, provider client, game-control endpoint, host access,
credential input, save-file access, or remote mutation path. A publication is a local
directory produced only after the input and its separately issued approval
have passed validation.

The checked-in `schemas/public-run.schema.json` remains the original
`public-run-v1` interface. W05 adds `public-run-v2` in
`schemas/publication-manifest.schema.json`; its richer action timeline,
evidence context, resource budget, decision-card lineage, and explicit local
guess/reveal state are a versioned extension. Existing interfaces are not
silently changed.

## Digest and approval boundary

`source.content_digest` is the SHA-256 of canonical UTF-8 JSON: keys are
sorted, separators are compact, Unicode is preserved, `approval_reference` is
removed, and `source.content_digest` is removed before hashing. The helper
`publisher.attach_source_digest` is provided for local fixture construction;
source owners issue the digest for real records.

An approval is a separate `publication-approval-v1` record. It binds the
approval ID, authority reference, operation, target public run ID, exact
source digest, allowed surfaces, allowed fields, approved asset digests,
scope notes, and validity period. The schema intentionally has no
`is_approved` (or equivalent) boolean. A changed source digest fails before
anything can be written.

Production publication requires all of the following:

- `classification` is `approved_public`, `test_fixture` is false, and the
  evidence kind is not `forced_fixture`;
- a recorded timestamp, approved evidence rights, and a supported caption;
- a current approval whose target, ID, digest, fields, and surfaces match the
  manifest;
- approved artifact lineage for any decision card; and
- a separate output root.

Synthetic, private, forced-fixture, unapproved, stale, revoked, rights-unknown,
and malformed records fail closed. Local `render` is intentionally broader so
the synthetic lane can exercise the page and error states, but its page is
explicitly labeled synthetic and is never a production export.

## Historical report-only intake

When a source owner supplies a real Windows or Linux historical summary, stage
one sanitized `public-run-v2` manifest per run. Set `evidence_kind` to
`native_run`, `evidence.availability` to `report_only`, keep `video_url` and
`replay_url` null, and point `evidence_reference` at the dated report or other
approved source. Use `game_configuration.platform` for `windows` or `linux`
when that fact is known; keep the exact game, mod, and harness revisions in the
same object. Preserve only measured provider calls and resource values. Use
null with an explanatory description when a historical report did not measure
them.

Report-only summaries do not receive invented action records. Set
`action_timeline.status` to `unavailable` with an empty `decisions` array and
set `local_guess_reveal.status` to `unavailable` with `legal_option_count` set
to `0`. Put any known aggregate result, such as outcome, floor, or a controller
restart, in the source-owner summary and intervention fields, with a source
reference; raw trajectories, hidden prompts, legal-choice lists, and selected
actions stay outside the manifest. The source owner supplies the digest after
sanitization. The record remains `private` until evidence rights, caption
support, and a separate approval authorize the report-only surfaces.

## Commands

From the repository root:

```sh
python3 -m publisher verify tests/fixtures/publication/run.synthetic.json
python3 -m publisher render tests/fixtures/publication/run.synthetic.json /tmp/ascension-w05-render
python3 -m publisher publish MANIFEST.json APPROVAL.json /tmp/ascension-w05-published
```

The last command is an example shape only; it must receive a real
digest-bound approval and a `public-run-v2` record. `render` and `publish` do
not fetch the URLs in a record. URLs are syntax-checked as HTTPS or
root-relative links and are emitted as links only.

Output is `run-manifests/<public_run_id>/v<publication_version>/` with a
canonical `manifest.json` projection and `index.html`. A repeat publish of the
same projection and version is idempotent. Reusing a version with different
content raises an error and leaves the existing files unchanged.

The generated page separates report-only, video, and replay-package states;
shows evidence and intervention disclosures; escapes all record text; and
shows unavailable states explicitly. A local guess/reveal panel uses browser
controls and a disclosure element. It is not a poll, does not expose an
aggregate count, and does not call a backend.

The output directory is deliberately separate from the input tree. Before
ingest, an artifact root can be checked for symlinks and hidden files. Production records with any available decision card require `--artifact-root`. Every top-level or nested card must match an `approved_assets` entry containing `asset_id`, `artifact_digest`, `artifact_path` relative to that root, and `provenance_reference`. The publisher rejects missing files, unsafe paths, and file bytes that do not match the approved SHA-256. This verifies referenced input identity; it does not generate or deploy the artwork.
Raw source records are never copied to hide them with CSS, robots metadata, or
navigation.

## Review limits

An approved record may still be report-only. A replay with no new provider
calls does not prove the original run used no model or that replay cost was
zero. A defeat is an outcome, not automatically a system error. A forced
victory fixture cannot be rendered as a model-earned win because production
publication rejects the fixture classification entirely.

Input JSON is bounded to 4 MiB and rejects duplicate keys. Both input and output paths reject symlink ancestors before resolution. This check does not replace source-owner review of the sanitized values.

Generated pages embed the canonical `brand/tokens.css` and record its SHA-256 in a meta field. Both timeline results and the local guess consequence remain behind explicit reveal controls. The scrollable timeline is keyboard-focusable; its wider table preserves mobile readability. This is a functional HTML interface, not generated decision-card artwork.
