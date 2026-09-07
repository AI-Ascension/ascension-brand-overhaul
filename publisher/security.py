"""Path, URL, and field-boundary checks for offline publication."""

from __future__ import annotations

import os
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlsplit

from .errors import SecurityError


FORBIDDEN_FIELD_NAMES = {
    "access_token",
    "api_key",
    "authorization",
    "cookie",
    "device_fingerprint",
    "email",
    "email_address",
    "full_referrer",
    "ip",
    "ip_address",
    "is_approved",
    "private_prompt",
    "private_run_id",
    "raw_action_payload",
    "raw_prompt",
    "save",
    "secret",
    "session_token",
    "token",
    "user_agent",
}


def reject_forbidden_fields(value: Any, path: str = "$") -> None:
    """Reject sensitive or authority-shaped keys at every nesting level."""

    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str):
                raise SecurityError(f"non-string object key at {path}")
            normalized = key.casefold().replace("-", "_")
            if normalized in FORBIDDEN_FIELD_NAMES:
                raise SecurityError(f"forbidden field at {path}.{key}")
            reject_forbidden_fields(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_forbidden_fields(child, f"{path}[{index}]")


def safe_relative_path(value: str) -> PurePosixPath:
    """Validate a path that may be joined beneath an approved root."""

    if not isinstance(value, str) or not value or "\x00" in value or "\\" in value:
        raise SecurityError("path must be a non-empty POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or ":" in value or value.startswith("//"):
        raise SecurityError(f"unsafe relative path: {value!r}")
    return path


def _absolute_path(path: Path) -> Path:
    return path if path.is_absolute() else Path.cwd() / path


def _reject_symlink_ancestors(path: Path) -> None:
    """Reject a symlink at any existing path component before resolving."""

    absolute = _absolute_path(Path(path))
    current = Path(absolute.anchor)
    for part in absolute.parts[1:]:
        current = current / part
        if current.is_symlink():
            raise SecurityError(f"symlink is not permitted in path: {path}")


def reject_symlink_path(path: Path) -> None:
    """Public wrapper used before creating any output path."""

    _reject_symlink_ancestors(path)


def safe_public_url(value: str | None) -> str | None:
    """Allow an HTTPS URL or a root-relative path without fetching it."""

    if value is None:
        return None
    if not isinstance(value, str) or not value or any(ord(char) < 0x20 for char in value):
        raise SecurityError("public URL must be a non-empty, printable string")
    if "\\" in value or value.startswith("//"):
        raise SecurityError(f"unsafe public URL: {value!r}")
    parsed = urlsplit(value)
    if parsed.scheme:
        if parsed.scheme.casefold() != "https" or not parsed.hostname:
            raise SecurityError(f"only HTTPS public URLs are allowed: {value!r}")
        if parsed.username or parsed.password:
            raise SecurityError("public URLs may not contain credentials")
        if ".." in PurePosixPath(parsed.path).parts:
            raise SecurityError(f"public URL contains traversal: {value!r}")
        return value
    if not value.startswith("/") or value.startswith("//"):
        raise SecurityError(f"URL must be HTTPS or root-relative: {value!r}")
    path = PurePosixPath(parsed.path)
    if ".." in path.parts:
        raise SecurityError(f"public URL contains traversal: {value!r}")
    return value


def checked_path(root: Path, relative: str, *, must_exist: bool = False) -> Path:
    """Resolve a relative artifact path and reject symlink escape."""

    raw_root = Path(root)
    _reject_symlink_ancestors(raw_root)
    root = raw_root.resolve()
    safe_path = safe_relative_path(relative)
    raw_candidate = root.joinpath(*safe_path.parts)
    current = root
    for part in safe_path.parts:
        current = current / part
        if current.is_symlink():
            raise SecurityError(f"symlink is not permitted: {relative!r}")
    candidate = raw_candidate.resolve(strict=False)
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise SecurityError(f"path escapes approved root: {relative!r}") from exc
    if must_exist and not candidate.is_file():
        raise SecurityError(f"artifact is missing: {relative!r}")
    return candidate


def inspect_artifact_root(root: Path) -> list[str]:
    """Inspect an input artifact root without reading or copying private data."""

    raw_root = Path(root)
    _reject_symlink_ancestors(raw_root)
    root = raw_root.resolve()
    if not root.is_dir():
        raise SecurityError(f"artifact root is not a real directory: {root}")
    findings: list[str] = []
    if root.name.startswith("."):
        findings.append(f"hidden:{root.name}")
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            findings.append(f"symlink:{relative}")
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            findings.append(f"hidden:{relative}")
    if findings:
        raise SecurityError("unsafe artifact root: " + ", ".join(findings))
    return findings


def ensure_separate_output(input_path: Path, output_root: Path) -> None:
    """Prevent writing publication artifacts into a source/private tree."""

    _reject_symlink_ancestors(input_path)
    _reject_symlink_ancestors(output_root)
    input_path = input_path.resolve()
    output_root = output_root.resolve()
    if output_root == input_path:
        raise SecurityError("publication output must be separate from its input")
    try:
        output_root.relative_to(input_path)
    except ValueError:
        return
    raise SecurityError("publication output may not be inside its input tree")
