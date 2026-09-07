"""Read-only local ingestion, rendering, and approval-gated publication."""

from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .canonical import canonical_json
from .errors import DuplicatePublicationError, PublisherError
from .render import render_html
from .output_state import managed_write
from .security import ensure_separate_output, inspect_artifact_root, reject_symlink_path
from .validate import (
    validate_approval,
    validate_manifest,
    validate_production_publication,
)

MAX_INPUT_BYTES = 4 * 1024 * 1024


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise PublisherError("JSON input contains duplicate object keys")
        result[key] = value
    return result


def _read_json(path: Path) -> dict[str, Any]:
    raw_path = Path(path)
    # A real file below a symlinked directory is still outside the caller's
    # declared tree. Check every existing ancestor before resolving it.
    reject_symlink_path(raw_path)
    if raw_path.is_symlink():
        raise PublisherError(f"input must be a real JSON file: {path}")
    path = raw_path.resolve()
    if not path.is_file():
        raise PublisherError(f"input must be a real JSON file: {path}")
    try:
        with path.open('rb') as handle:
            raw = handle.read(MAX_INPUT_BYTES + 1)
        if len(raw) > MAX_INPUT_BYTES:
            raise PublisherError("JSON input exceeds the 4 MiB limit")
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=_unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PublisherError(f"cannot read JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PublisherError(f"JSON input must be an object: {path}")
    return value


@dataclass(frozen=True)
class PublicationResult:
    """Deterministic local publication result."""

    output_directory: Path
    manifest_path: Path
    html_path: Path
    source_digest: str
    idempotent: bool
    manifest_digest: str
    html_digest: str


class OfflinePublisher:
    """An offline publisher with no network or runtime mutation capability."""

    def ingest(self, manifest_path: Path | str) -> dict[str, Any]:
        manifest = _read_json(Path(manifest_path))
        validate_manifest(manifest)
        return manifest

    def read_approval(self, approval_path: Path | str) -> dict[str, Any]:
        approval = _read_json(Path(approval_path))
        validate_approval(approval)
        return approval

    def verify_artifact_root(self, artifact_root: Path | str) -> None:
        inspect_artifact_root(Path(artifact_root))

    def render(
        self,
        manifest_path: Path | str,
        output_root: Path | str,
        *,
        artifact_root: Path | str | None = None,
    ) -> PublicationResult:
        """Render a local page, including explicitly labeled synthetic fixtures."""

        input_path = Path(manifest_path)
        reject_symlink_path(Path(output_root))
        output_root = Path(output_root).resolve()
        ensure_separate_output(input_path.parent, output_root)
        if artifact_root is not None:
            ensure_separate_output(Path(artifact_root), output_root)
            self.verify_artifact_root(artifact_root)
        manifest = self.ingest(input_path)
        return managed_write(output_root, "local_preview", lambda: self._write(manifest, manifest, output_root, idempotent_ok=True, local_preview=True))

    def publish(
        self,
        manifest_path: Path | str,
        approval_path: Path | str,
        output_root: Path | str,
        *,
        now: datetime | None = None,
        artifact_root: Path | str | None = None,
    ) -> PublicationResult:
        """Publish only an approved, non-synthetic record to local output."""

        input_path = Path(manifest_path)
        reject_symlink_path(Path(output_root))
        output_root = Path(output_root).resolve()
        ensure_separate_output(input_path.parent, output_root)
        ensure_separate_output(Path(approval_path).parent, output_root)
        if artifact_root is not None:
            ensure_separate_output(Path(artifact_root), output_root)
            self.verify_artifact_root(artifact_root)
        manifest = self.ingest(input_path)
        approval = self.read_approval(approval_path)
        projection = validate_production_publication(manifest, approval, now=now, artifact_root=artifact_root)
        return managed_write(output_root, "approved_public", lambda: self._write(projection, manifest, output_root, idempotent_ok=True))

    def _write(
        self,
        projection: dict[str, Any],
        source_manifest: dict[str, Any],
        output_root: Path,
        *,
        idempotent_ok: bool,
        local_preview: bool = False,
    ) -> PublicationResult:
        run_id = source_manifest["public_run_id"]
        version = source_manifest["publication_version"]
        output_directory = output_root / "run-manifests" / run_id / f"v{version}"
        manifest_path = output_directory / "manifest.json"
        html_path = output_directory / "index.html"
        reject_symlink_path(output_directory)
        output_root.mkdir(parents=True, exist_ok=True)
        if output_directory.exists() and (output_directory.is_symlink() or not output_directory.is_dir()):
            raise PublisherError("publication destination is not a real directory")
        payload = canonical_json(projection) + b"\n"
        # Render the same allowlisted projection written to disk.  This keeps
        # an approval's field boundary effective for both JSON and HTML.
        page = render_html(projection)
        if local_preview:
            page = page.replace("<main>", '<main><p role="note">Local preview only. Not approved for publication.</p>', 1)
        if output_directory.exists():
            if {p.name for p in output_directory.iterdir()} != {'manifest.json', 'index.html'}:
                raise DuplicatePublicationError('Publication version contains unexpected files')
            if manifest_path.is_symlink() or html_path.is_symlink():
                raise PublisherError("publication files may not be symlinks")
            if not manifest_path.is_file() or not html_path.is_file():
                raise DuplicatePublicationError("publication version exists but is incomplete")
            existing_payload = manifest_path.read_bytes()
            existing_page = html_path.read_text(encoding="utf-8")
            if existing_payload == payload and existing_page == page and idempotent_ok:
                return PublicationResult(output_directory, manifest_path, html_path, source_manifest["source"]["content_digest"], True, hashlib.sha256(payload).hexdigest(), hashlib.sha256(page.encode("utf-8")).hexdigest())
            raise DuplicatePublicationError("publication version already exists with different content")
        output_directory.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix='.publication-', dir=output_directory.parent))
        try:
            for name, content in [('manifest.json', payload), ('index.html', page.encode('utf-8'))]:
                with (staging / name).open('xb') as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
            reject_symlink_path(output_directory)
            if output_directory.exists():
                raise DuplicatePublicationError('Publication destination appeared during staging')
            os.rename(staging, output_directory)
        finally:
            if staging.exists():
                shutil.rmtree(staging)
        return PublicationResult(output_directory, manifest_path, html_path, source_manifest["source"]["content_digest"], False, hashlib.sha256(payload).hexdigest(), hashlib.sha256(page.encode("utf-8")).hexdigest())


def verify(manifest_path: Path | str) -> dict[str, Any]:
    """Convenience wrapper for a read-only manifest verification."""

    return OfflinePublisher().ingest(manifest_path)


def render(manifest_path: Path | str, output_root: Path | str, **kwargs: Any) -> PublicationResult:
    """Convenience wrapper for local rendering."""

    return OfflinePublisher().render(manifest_path, output_root, **kwargs)


def publish(
    manifest_path: Path | str,
    approval_path: Path | str,
    output_root: Path | str,
    **kwargs: Any,
) -> PublicationResult:
    """Convenience wrapper for approval-gated local publication."""

    return OfflinePublisher().publish(manifest_path, approval_path, output_root, **kwargs)


Publisher = OfflinePublisher


__all__ = ["OfflinePublisher", "Publisher", "PublicationResult", "verify", "render", "publish"]
