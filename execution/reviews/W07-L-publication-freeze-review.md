# W07-L independent re-review: publication authority and projection

This re-review checks the integrated publication repair at `f33f24bc4222e3f58a5569f71a942e7df10da462` in an exact detached worktree. The root checkout had separate uncommitted measurement work; those files were not used for this publication result. Scope is the repaired publication authority, URI register, artifact lineage, output transaction, and public projection. No production record, approval enrollment, network operation, or live publication was created.

The exact-head publication suite passed:

- `python3 -m unittest tests.test_publication tests.test_publication_artifacts tests.test_publication_authority tests.test_publication_input_boundaries tests.test_publication_lineage tests.test_publication_render_behavior tests.test_publication_review_repairs -v`: **30 passed**.
- The checked-in `config/publication-authorities.json` contains zero approvals. An approved fixture supplied directly to the gate is rejected with `ApprovalError: approval is not enrolled in the trusted deployment registry`.

The earlier findings for duplicate schema members, nested and top-level decision-card approval, report-only action-state consistency, source-reference membership, projection of optional private source identities, and atomic version-directory publication are repaired at this head. The tests and probes confirmed strict duplicate-key schema loading, real matching artifact bytes for both card locations, rejection of report-only records carrying decisions, exact structured URI membership, omission of `source.record_id`, `source.revision`, and `source.content_digest` from a scoped projection, retryable staging after a write failure, and rejection of unexpected files in an existing version directory.

## Findings

### W07-PUB-07 — The output root is not required to be separate from every private input root (high)

`publisher/publisher.py:116-125` calls `ensure_separate_output` only with the manifest's parent. It does not compare `output_root` with `approval_path`'s parent or with `artifact_root`. `publisher/security.py:156-169` therefore cannot enforce the full boundary promised by `docs/PUBLISHING.md:98-100` and `specs/PUBLICATION.md:7,21,23`. The version-level inventory at `publisher/publisher.py:148-159` also says nothing about unrelated entries already present directly under the requested output root.

Three exact-head probes demonstrate the exposure:

1. With the manifest in one temporary directory and `approval.json` placed directly in the requested output root, `OfflinePublisher.publish` succeeds and leaves the approval record under that output root.
2. With an approved card, `artifact_root=output_root`, and an otherwise unapproved `private.txt` beside the approved card, publication succeeds and `private.txt` remains in the output tree.
3. With an unrelated `output_root/leak` symlink to a private file, publication succeeds; the symlink remains readable from the output root.

Serving or archiving the documented output root can consequently expose a private approval, an artifact-tree file, or a symlinked external file even though the version directory itself contains only the two publisher-owned files. Require the output root to be disjoint from the manifest, approval, and artifact trees, and either require a new empty destination or inventory/reject every pre-existing child that could be served. Keep the version-directory inventory as an additional idempotency check.

### W07-PUB-08 — The approved URI register does not cover URL-like values in rendered free text (high privacy risk)

`publisher/validate.py:329-336` constructs `public_uris` from source references, the structured evidence URL fields, card provenance, and action evidence references. `publisher/render.py:116-148,151-155,157-164` also emits arbitrary values from disclosures, policy strings, model and game metadata, intervention summaries, and observed-field labels. Those strings are HTML-escaped, but URL-like text in them is not compared with `approval["approved_public_uris"]`.

Using an enrolled temporary approval with `allowed_fields=["*"]`, adding `private evidence: https://private.example/secret` to `manifest["disclosures"]`, and recomputing the source digest produced a valid publication whose `index.html` contained that URL. The URL was absent from `approved_public_uris`. The exact registry digest correctly bound the supplied record, but it does not repair this incomplete URI invariant; an authority's manual review is the only remaining control.

Make URL-bearing values structured and register every emitted URI, or reject URL-like tokens in all free-text fields unless they are explicitly represented in the URI register. Keep the current exact structured-field check. A trusted approval still needs rights review because URI syntax alone cannot establish public rights.

### W07-PUB-09 — Approved artifact files have no MIME, size, or aggregate input bound (medium)

The approval asset schema records an ID, digest, relative path, and provenance reference, but no media type or byte limit. `publisher/validate.py:322-327` hashes the referenced file without a size bound, while `publisher/security.py:134-153` recursively inspects the entire artifact root without a count or total-size limit. A 5 MiB arbitrary `card.bin` with a matching approved digest was accepted at this head.

The current renderer does not copy or embed the artifact bytes, so this is primarily an input-resource and future-asset safety gap. Add an approved MIME/extension policy and per-file and aggregate byte limits before treating arbitrary artifact roots as production inputs. Bound the root scan as well.

## Registry trust and projection disposition

The code-level caller bypass found in the earlier review is closed. `publisher/authority.py:14-25,28-59` fixes the registry path relative to the installed publisher, rejects symlinked registry paths, rejects duplicate registry keys, matches the exact canonical approval digest together with its approval and authority IDs, and recomputes a digest over all publisher Python files, all checked-in schema JSON, and `brand/tokens.css`. There is no CLI, environment, or content-file registry override. `publisher/schema.py:107-120` and `publisher/render.py:46-49,157-160` now apply the same scoped projection to `manifest.json` and HTML; a scoped approval omits private source identity and content hash from both outputs. Exact structured URI removal, stale renderer, forged authority text, and projection probes fail as expected.

This remains an explicit deployment-owner trust boundary, as documented at `docs/PUBLISHING.md:116-122`: file permissions, the publisher installation, the Python/jsonschema runtime, and the identity of the person enrolling a record are not cryptographically authenticated by this package. That is a documented conditional design, not evidence of a caller-controlled bypass. Because the shipped registry is empty, no real production approval is currently enrolled and no production publication can be accepted.

## Review disposition

At `f33f24b`, the repaired publication authority and projection pass their exact-head local checks, but this review does not approve production publication. W07-PUB-07 and W07-PUB-08 need resolution before the output-root and URI-register claims are complete; W07-PUB-09 needs an explicit resource-bound decision. The empty trusted registry, absent real approved source/artifact, and lack of deployment or served-route evidence remain separate release gates.
