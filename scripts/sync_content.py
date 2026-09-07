#!/usr/bin/env python3
"""Synchronize canonical functional brand content from a pinned Git commit.

Default is a dry run. Existing copies may change only when they still match the
previous sync receipt. Artwork uses the separate generation/export review gate.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile
import os

SOURCES = {'brand/tokens.css', 'brand/tokens.json', 'brand/copy.json', 'execution/capabilities.json'}
RECEIPT = '.ai-ascension-brand-sync.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(root, name):
    if not isinstance(name, str) or not name or len(name) > 240:
        raise ValueError('Invalid destination path.')
    parts = name.split('/')
    if any(part in {'', '.', '..'} or part.startswith('.') for part in parts):
        raise ValueError('Hidden or traversing destination path.')
    if '\\' in name or ':' in name or '\x00' in name or PurePosixPath(name).is_absolute():
        raise ValueError('Unsafe destination path.')
    cursor = root
    for part in parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Symlink destination is prohibited.')
    if not cursor.resolve().is_relative_to(root.resolve()):
        raise ValueError('Destination escapes consumer root.')
    return cursor


def git(repo, *args):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise ValueError('Pinned Git object could not be read.')
    return result.stdout


def sync(repo, destination, plan, apply=False):
    if destination.is_symlink() or not destination.is_dir():
        raise ValueError('Consumer root must be an existing non-symlink directory.')
    if set(plan) != {'schema_version', 'source_revision', 'files'} or plan['schema_version'] != 'brand-content-sync-v1':
        raise ValueError('Unknown sync-plan schema or fields.')
    revision = plan['source_revision']
    if not isinstance(revision, str) or not re.fullmatch('[a-f0-9]{40}', revision):
        raise ValueError('Source revision must be a full immutable Git commit.')
    if git(repo, 'rev-parse', '--verify', revision + '^{commit}').decode().strip() != revision:
        raise ValueError('Source revision is not the requested commit.')
    entries = plan['files']
    if not isinstance(entries, list) or not 1 <= len(entries) <= len(SOURCES):
        raise ValueError('Sync requires a bounded nonempty content allowlist.')
    receipt_path = destination / RECEIPT
    if receipt_path.is_symlink():
        raise ValueError('Symlink sync receipt is prohibited.')
    previous = json.loads(receipt_path.read_text()) if receipt_path.exists() else None
    if previous is not None and (not isinstance(previous, dict) or previous.get('schema_version') != 'brand-content-sync-v1'):
        raise ValueError('Unknown existing sync receipt.')
    previous_files = {entry['destination']: entry['sha256'] for entry in previous['files']} if previous else {}
    prepared = []
    names = set()
    sources = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {'source', 'destination', 'sha256'}:
            raise ValueError('Unknown content entry fields.')
        source = entry['source']
        name = entry['destination']
        if source not in SOURCES or source in sources:
            raise ValueError('Source is not a unique canonical content path.')
        target = safe_path(destination, name)
        if target.suffix != PurePosixPath(source).suffix:
            raise ValueError('Content export must preserve its file type.')
        folded = name.casefold()
        if any(folded == other or folded.startswith(other + '/') or other.startswith(folded + '/') for other in names):
            raise ValueError('Destination paths collide.')
        names.add(folded)
        sources.add(source)
        if git(repo, 'ls-tree', revision, '--', source).split(b' ', 1)[0] not in {b'100644', b'100755'}:
            raise ValueError('Canonical content must be a regular tracked file.')
        raw = git(repo, 'show', revision + ':' + source)
        if len(raw) > 1024 * 1024 or digest(raw) != entry['sha256']:
            raise ValueError('Canonical content exceeds size limit or digest differs.')
        raw.decode('utf-8')
        current = target.read_bytes() if target.exists() else None
        if current is not None and current != raw and digest(current) != previous_files.get(name):
            raise ValueError('Consumer copy has unrelated edits; refusing overwrite: ' + name)
        prepared.append((target, raw, current))
    if set(previous_files) - {entry['destination'] for entry in entries}:
        raise ValueError('Plan omits previously managed files; explicitly review migration first.')
    receipt = {'schema_version': plan['schema_version'], 'source_revision': revision,
               'files': sorted(entries, key=lambda entry: entry['destination'])}
    result = {'mode': 'apply' if apply else 'dry_run', 'source_revision': revision,
              'changed_files': [str(target.relative_to(destination)) for target, raw, current in prepared if raw != current],
              'receipt': receipt}
    if apply:
        for target, raw, current in prepared:
            safe_path(destination, target.relative_to(destination).as_posix())
            if (target.read_bytes() if target.exists() else None) != current:
                raise ValueError('Consumer changed after preflight.')
        for target, raw, current in prepared:
            if raw != current:
                atomic_write(target, raw)
        atomic_write(receipt_path, (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode())
    return result


def atomic_write(path, raw):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        except BaseException:
            temporary.unlink(missing_ok=True)
            raise
    try:
        temporary.chmod(0o644)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-repo', required=True, type=Path)
    parser.add_argument('--consumer-root', required=True, type=Path)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = sync(args.source_repo, args.consumer_root, json.loads(args.plan.read_text()), args.apply)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Content sync refused: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
