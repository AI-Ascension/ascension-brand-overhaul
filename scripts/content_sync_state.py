"""Private sync authority, cooperative locking, and recoverable file installation."""
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile

LOCK_NAME = '.ai-ascension-brand-sync.lock'


class SyncRecoveryRequired(ValueError):
    """Preserve the lock and private transaction journal for operator recovery."""


def reject_symlinks(path):
    if any(candidate.is_symlink() for candidate in (path, *path.parents)):
        raise ValueError('Symlink in content-sync control or destination path.')


def read_optional(path):
    reject_symlinks(path)
    if not path.exists():
        return None
    if not path.is_file():
        raise ValueError('Content-sync state must be a regular file.')
    with path.open('rb') as handle:
        raw = handle.read(1024 * 1024 + 1)
    if len(raw) > 1024 * 1024:
        raise ValueError('Content-sync input exceeds 1 MiB.')
    return raw


@contextmanager
def consumer_lock(destination):
    lock = destination / LOCK_NAME
    reject_symlinks(lock)
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise ValueError('Consumer sync is locked; reconcile an interrupted transaction before retrying.') from error
    keep = False
    try:
        with os.fdopen(descriptor, 'w') as handle:
            handle.write(str(os.getpid()) + '\n')
            handle.flush()
            os.fsync(handle.fileno())
        try:
            yield
        except SyncRecoveryRequired:
            keep = True
            raise
    finally:
        if not keep:
            lock.unlink(missing_ok=True)


def atomic_write(path, raw):
    reject_symlinks(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix='.brand-sync-write-', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.chmod(0o644)
        reject_symlinks(path)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def install_transaction(items, authority_path, writer=atomic_write):
    """Stage every new/old byte set before changes; roll back ordinary failures.

    A killed process leaves the consumer lock and a journal in protected Git
    state. Automatic retry never guesses how that interrupted write settled.
    """
    changed = [(path, raw, old) for path, raw, old in items if raw != old]
    if not changed:
        return
    reject_symlinks(authority_path)
    authority_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    stage = Path(tempfile.mkdtemp(prefix=authority_path.stem + '.transaction-', dir=authority_path.parent))
    installed = []
    created_directories = set()
    keep_stage = False
    try:
        journal = []
        for index, (path, raw, old) in enumerate(changed):
            if read_optional(path) != old:
                raise ValueError('Consumer or authority changed after preflight.')
            for suffix, value in (('new', raw), ('old', old)):
                if value is not None:
                    with (stage / f'{index}.{suffix}').open('xb') as handle:
                        handle.write(value)
                        handle.flush()
                        os.fsync(handle.fileno())
            journal.append({'path': str(path.resolve()), 'new_sha256': hashlib.sha256(raw).hexdigest(), 'old_sha256': hashlib.sha256(old).hexdigest() if old is not None else None, 'backup_index': index})
            parent = path.parent
            while not parent.exists():
                created_directories.add(parent)
                parent = parent.parent
        with (stage / 'journal.json').open('x') as handle:
            json.dump({'schema_version': 'brand-sync-transaction-v1', 'state': 'prepared', 'files': journal}, handle, indent=2)
            handle.flush()
            os.fsync(handle.fileno())
        for path, raw, old in changed:
            if read_optional(path) != old:
                raise ValueError('Consumer or authority changed after preflight.')
            # Include the attempted file: a writer may raise after replacing it.
            installed.append((path, raw, old))
            writer(path, raw)
        if any(read_optional(path) != raw for path, raw, _ in changed):
            raise ValueError('Content-sync post-state changed during installation.')
    except BaseException as error:
        failures = []
        for path, raw, old in reversed(installed):
            try:
                current = read_optional(path)
                if current == old:
                    continue
                if current != raw:
                    raise ValueError('A concurrent edit prevents automatic rollback.')
                if old is None:
                    path.unlink()
                else:
                    writer(path, old)
            except BaseException:
                failures.append(path)
        for directory in sorted(created_directories, key=lambda path: len(path.parts), reverse=True):
            try:
                directory.rmdir()
            except OSError:
                pass  # Preserve directories containing any unrelated file.
        if failures:
            keep_stage = True
            raise SyncRecoveryRequired('Rollback is incomplete; retain the consumer lock and inspect the protected Git transaction journal.') from error
        raise
    finally:
        if not keep_stage:
            shutil.rmtree(stage)
