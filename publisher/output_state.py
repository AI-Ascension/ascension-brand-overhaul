"""Track publisher-owned output inventories outside every served directory."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Callable, Any

from .canonical import canonical_json
from .errors import DuplicatePublicationError, PublisherError, SecurityError
from .schema import unique_schema_object
from .security import ensure_separate_output, reject_symlink_path

STATE_ROOT = Path(__file__).resolve().parents[1] / '.execution-private/publisher-output-state'
MAX_ENTRIES = 10000
MAX_BYTES = 128 * 1024 * 1024


def inventory(root: Path) -> dict:
    files = {}
    directories = []
    total = 0
    if not root.exists():
        return {'files': files, 'directories': directories}
    if not root.is_dir():
        raise PublisherError('output root must be a directory')
    count = 0
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in sorted(dirs + names):
            count += 1
            if count > MAX_ENTRIES:
                raise PublisherError('output inventory exceeds entry limit')
            path = Path(parent) / name
            if path.is_symlink():
                raise SecurityError('output tree contains a symlink')
            relative = path.relative_to(root).as_posix()
            if path.is_dir():
                directories.append(relative)
            elif path.is_file():
                size = path.stat().st_size
                total += size
                if total > MAX_BYTES:
                    raise PublisherError('output inventory exceeds byte limit')
                digest = hashlib.sha256()
                with path.open('rb') as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                        digest.update(chunk)
                files[relative] = digest.hexdigest()
            else:
                raise SecurityError('output tree contains a special file')
    return {'files': files, 'directories': sorted(directories)}


def _save(path: Path, ledger: dict) -> None:
    descriptor, temporary = tempfile.mkstemp(prefix='.output-state-', dir=path.parent)
    staging = Path(temporary)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(canonical_json(ledger) + b'\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)


def managed_write(output_root: Path, classification: str, operation: Callable[[], Any]) -> Any:
    """Serialize writes and accept only previously inventoried public outputs.

    The fixed, private state directory is protected by the deployment owner,
    like the installed code and authority registry. It is never a CLI input.
    Existing unregistered directories must be empty; no adoption is implicit.
    """
    reject_symlink_path(STATE_ROOT)
    ensure_separate_output(STATE_ROOT, output_root)
    STATE_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = STATE_ROOT / 'writer.lock'
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise PublisherError('publisher output state is locked; reconcile the prior writer before retrying') from exc
    ledger_path = STATE_ROOT / 'outputs.json'
    result = None
    before = None
    try:
        os.close(descriptor)
        reject_symlink_path(ledger_path)
        if ledger_path.exists():
            with ledger_path.open('rb') as handle:
                raw = handle.read(4 * 1024 * 1024 + 1)
            if len(raw) > 4 * 1024 * 1024:
                raise PublisherError('publisher output state exceeds size limit')
            ledger = json.loads(raw, object_pairs_hook=unique_schema_object)
        else:
            ledger = {'schema_version': 'publisher-output-state-v1', 'roots': {}}
        if not isinstance(ledger, dict) or set(ledger) != {'schema_version', 'roots'} or ledger['schema_version'] != 'publisher-output-state-v1' or not isinstance(ledger['roots'], dict):
            raise PublisherError('invalid publisher output state')
        key = str(output_root.resolve())
        for known_root in ledger['roots']:
            other = Path(known_root)
            if known_root != key and other.exists() and (other.is_relative_to(output_root) or output_root.is_relative_to(other)):
                raise PublisherError('managed output roots must be disjoint')
        before = inventory(output_root)
        entry = ledger['roots'].get(key)
        if entry is None:
            if before['files'] or before['directories']:
                raise PublisherError('unregistered output root must be empty')
        elif entry != {'classification': classification, 'inventory': before}:
            raise DuplicatePublicationError('output tree differs from its private publisher inventory or classification')
        result = operation()
        after = inventory(output_root)
        expected_files = dict(before['files'])
        expected_files[result.manifest_path.relative_to(output_root).as_posix()] = result.manifest_digest
        expected_files[result.html_path.relative_to(output_root).as_posix()] = result.html_digest
        if after['files'] != expected_files:
            raise PublisherError('output changed outside the current publication transaction')
        ledger['roots'][key] = {'classification': classification, 'inventory': after}
        _save(ledger_path, ledger)
        return result
    except BaseException:
        # A successful new version whose state commit failed belongs to this
        # transaction. Existing versions and unrelated files are preserved.
        if result is not None and not result.idempotent:
            for path, digest in ((result.manifest_path, result.manifest_digest), (result.html_path, result.html_digest)):
                if path.is_file() and not path.is_symlink() and hashlib.sha256(path.read_bytes()).hexdigest() == digest:
                    path.unlink()
            try:
                result.output_directory.rmdir()
            except OSError:
                pass
        if before is not None and output_root.is_dir():
            original_dirs = set(before['directories'])
            for parent, dirs, _ in os.walk(output_root, topdown=False, followlinks=False):
                for name in dirs:
                    path = Path(parent) / name
                    if not path.is_symlink() and path.relative_to(output_root).as_posix() not in original_dirs:
                        try:
                            path.rmdir()
                        except OSError:
                            pass
        raise
    finally:
        lock.unlink(missing_ok=True)
