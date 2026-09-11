"""Canonical serialization and source-digest helpers.

The digest is calculated over the sanitized manifest while removing the
publisher approval reference and the digest field itself.  This prevents a
self-referential digest and keeps publication version/approval bookkeeping out
of the source content identity.  The exact rule is documented in
docs/PUBLISHING.md and is covered by the fixtures and tests.
"""

from __future__ import annotations

import copy
import hashlib
import json
from typing import Any


def canonical_json(value: Any) -> bytes:
    """Return stable UTF-8 JSON bytes for hashing and deterministic output."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def source_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return the exact payload represented by ``source.content_digest``."""

    payload = copy.deepcopy(manifest)
    payload.pop("approval_reference", None)
    source = payload.get("source")
    if isinstance(source, dict):
        source.pop("content_digest", None)
    return payload


def source_digest(manifest: dict[str, Any]) -> str:
    """Compute the SHA-256 identity of a sanitized manifest."""

    return hashlib.sha256(canonical_json(source_payload(manifest))).hexdigest()


def attach_source_digest(manifest: dict[str, Any]) -> dict[str, Any]:
    """Mutate and return a manifest with a freshly computed source digest.

    This helper is intended for local fixture construction.  Production
    callers should receive a digest already issued by the source owner and
    let :func:`publisher.validate.validate_manifest_integrity` verify it.
    """

    manifest["source"]["content_digest"] = source_digest(manifest)
    return manifest
