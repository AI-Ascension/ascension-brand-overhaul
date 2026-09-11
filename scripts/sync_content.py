#!/usr/bin/env python3
"""Synchronize canonical functional brand content from a pinned Git commit.

Default is a dry run. Existing copies may change only when they match pinned
source bytes and the receipt retained in protected canonical Git state.
Artwork uses the separate generation/export review gate.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_inventory import unique_object, load_json
from content_sync_state import LOCK_NAME, atomic_write, consumer_lock, install_transaction, read_optional, reject_symlinks

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
    result = subprocess.run(['git', '--no-replace-objects', '-C', str(repo), *args], capture_output=True, check=False)
    if result.returncode:
        raise ValueError('Pinned Git object could not be read.')
    return result.stdout


def pinned_content(repo, destination, plan):
    """Resolve only bounded regular blobs at a full immutable commit."""
    if not isinstance(plan, dict) or set(plan) != {'schema_version', 'source_revision', 'files'} or plan['schema_version'] != 'brand-content-sync-v1':
        raise ValueError('Unknown sync-plan schema or fields.')
    revision = plan['source_revision']
    if not isinstance(revision, str) or not re.fullmatch('[a-f0-9]{40}', revision):
        raise ValueError('Source revision must be a full immutable Git commit.')
    if git(repo, 'rev-parse', '--verify', revision + '^{commit}').decode().strip() != revision:
        raise ValueError('Source revision is not the requested commit.')
    entries = plan['files']
    if not isinstance(entries, list) or not 1 <= len(entries) <= len(SOURCES):
        raise ValueError('Sync requires a bounded nonempty content allowlist.')
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
        size = int(git(repo, 'cat-file', '-s', revision + ':' + source))
        if size > 1024 * 1024:
            raise ValueError('Canonical content exceeds size limit.')
        raw = git(repo, 'show', revision + ':' + source)
        if len(raw) > 1024 * 1024 or digest(raw) != entry['sha256']:
            raise ValueError('Canonical content exceeds size limit or digest differs.')
        raw.decode('utf-8')
        prepared.append((entry, target, raw))
    return prepared


def _sync(repo, destination, plan, apply):
    prepared_source = pinned_content(repo, destination, plan)
    receipt_path = destination / RECEIPT
    previous_raw = read_optional(receipt_path)
    previous = json.loads(previous_raw, object_pairs_hook=unique_object) if previous_raw is not None else None
    common = Path(git(repo, 'rev-parse', '--git-common-dir').decode().strip())
    common = common if common.is_absolute() else repo / common
    reject_symlinks(common)
    identity = digest(str(destination.resolve()).encode())
    authority_path = common.resolve() / 'ai-ascension-content-sync' / (identity + '.json')
    authority_raw = read_optional(authority_path)
    authority = json.loads(authority_raw, object_pairs_hook=unique_object) if authority_raw is not None else None
    if (previous is None) != (authority is None):
        raise ValueError('Consumer receipt and protected canonical authority disagree; reviewed migration is required.')
    previous_files = {}
    if previous is not None:
        if not isinstance(previous, dict):
            raise ValueError('Invalid existing sync receipt.')
        expected_authority = {'schema_version': 'brand-content-sync-authority-v1', 'consumer_id': identity, 'receipt_sha256': digest(previous_raw), 'source_revision': previous.get('source_revision')}
        if authority != expected_authority:
            raise ValueError('Existing sync receipt does not match protected canonical authority.')
        for entry, _, raw in pinned_content(repo, destination, previous):
            previous_files[entry['destination']] = (entry['source'], raw)
    if set(previous_files) - {entry['destination'] for entry, _, _ in prepared_source}:
        raise ValueError('Plan omits previously managed files; explicitly review migration first.')
    prepared = []
    for entry, target, raw in prepared_source:
        name = entry['destination']
        current = read_optional(target)
        if name in previous_files:
            previous_source, previous_bytes = previous_files[name]
            if entry['source'] != previous_source:
                raise ValueError('Canonical source mapping changed; explicitly review migration first.')
            if current not in (raw, previous_bytes):
                raise ValueError('Consumer copy has unrelated edits; refusing overwrite: ' + name)
        elif current is not None and current != raw:
            raise ValueError('Consumer copy has unrelated edits; refusing overwrite: ' + name)
        prepared.append((target, raw, current))
    receipt = {'schema_version': plan['schema_version'], 'source_revision': plan['source_revision'],
               'files': sorted(plan['files'], key=lambda entry: entry['destination'])}
    result = {'mode': 'apply' if apply else 'dry_run', 'source_revision': plan['source_revision'],
              'changed_files': [str(target.relative_to(destination)) for target, raw, current in prepared if raw != current],
              'receipt': receipt}
    if apply:
        receipt_bytes = (json.dumps(receipt, indent=2, sort_keys=True) + '\n').encode()
        new_authority = {'schema_version': 'brand-content-sync-authority-v1', 'consumer_id': identity, 'receipt_sha256': digest(receipt_bytes), 'source_revision': plan['source_revision']}
        authority_bytes = (json.dumps(new_authority, indent=2, sort_keys=True) + '\n').encode()
        install_transaction([*prepared, (receipt_path, receipt_bytes, previous_raw), (authority_path, authority_bytes, authority_raw)], authority_path, writer=atomic_write)
    return result


def sync(repo, destination, plan, apply=False):
    if destination.is_symlink() or not destination.is_dir():
        raise ValueError('Consumer root must be an existing non-symlink directory.')
    reject_symlinks(destination)
    if apply:
        with consumer_lock(destination):
            return _sync(repo, destination, plan, True)
    if (destination / LOCK_NAME).exists():
        raise ValueError('Consumer sync is locked; wait for or reconcile the active transaction.')
    return _sync(repo, destination, plan, False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-repo', required=True, type=Path)
    parser.add_argument('--consumer-root', required=True, type=Path)
    parser.add_argument('--plan', required=True, type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    try:
        result = sync(args.source_repo, args.consumer_root, load_json(args.plan), args.apply)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Content sync refused: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
