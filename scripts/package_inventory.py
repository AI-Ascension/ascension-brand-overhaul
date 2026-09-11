"""Shared safe source inventory and strict, exact package manifest checks."""
import hashlib
import json
import os
from pathlib import Path
import re

LOCAL_ONLY = {'.git', '.execution', '.execution-private', '.codex', '.agents', 'private', 'node_modules', '.venv', 'venv', 'vendor', 'target', '__pycache__', '.pytest_cache', '.ssh', '.aws', '.azure', '.kube', '.gnupg', '.docker'}
FONTS = {'.ttf', '.otf', '.woff', '.woff2', '.ttc', '.eot'}
SECRET_NAMES = {'.npmrc', '.pypirc', '.netrc', 'credentials', 'credentials.json', 'credentials.yaml', 'credentials.yml', 'auth.json', 'secrets.json', 'secrets.yaml', 'secrets.yml', 'id_rsa', 'id_ed25519', 'id_ecdsa', 'cookies.txt'}
INTEGRITY_EXCLUSIONS = {'MANIFEST.json', 'CHECKSUMS.sha256'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON object key: ' + key)
        result[key] = value
    return result


def load_json(path):
    with Path(path).open('rb') as handle:
        raw = handle.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError('Package control JSON exceeds 4 MiB.')
    return json.loads(raw, object_pairs_hook=unique_object)


def safe_relative(value):
    return isinstance(value, str) and bool(value) and not any(part in {'', '.', '..'} for part in value.split('/')) and not any(char in value for char in '\\\x00:')


def excluded_file(path):
    name = path.name.casefold()
    return name.startswith('.env') or name in SECRET_NAMES or path.suffix.casefold() in FONTS | {'.pem', '.key', '.p12', '.pfx', '.pyc', '.pyo'}


def source_files(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir():
        raise ValueError('Package source must be a real directory.')
    files = []
    folded = set()
    total = 0
    for directory, children, names in os.walk(root, followlinks=False):
        children[:] = [name for name in children if name.casefold() not in LOCAL_ONLY]
        for name in children + names:
            path = Path(directory) / name
            if name.casefold() in LOCAL_ONLY or excluded_file(path):
                continue
            relative = path.relative_to(root).as_posix()
            if path.is_symlink() or not safe_relative(relative):
                raise ValueError('Unsafe package source path: ' + relative)
            if path.is_dir():
                continue
            if not path.is_file():
                raise ValueError('Special package source file: ' + relative)
            if relative.casefold() in folded:
                raise ValueError('Case-insensitive source path collision: ' + relative)
            folded.add(relative.casefold())
            size = path.stat().st_size
            total += size
            if size > 64 * 1024 * 1024 or total > 512 * 1024 * 1024 or len(files) >= 10000:
                raise ValueError('Package source exceeds its bounded file/byte inventory.')
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(root).as_posix())


def manifest_errors(root):
    root = Path(root)
    errors = []
    try:
        manifest = load_json(root / 'MANIFEST.json')
        if not isinstance(manifest, dict) or set(manifest) != {'package', 'version', 'integrity_exclusions', 'files'}:
            raise ValueError('Invalid package manifest fields.')
        if not all(isinstance(manifest[key], str) and manifest[key].strip() for key in ('package', 'version')) or not isinstance(manifest['files'], list):
            raise ValueError('Invalid package manifest field types.')
        exclusions = manifest['integrity_exclusions']
        if not isinstance(exclusions, list) or len(exclusions) != 2 or set(exclusions) != INTEGRITY_EXCLUSIONS:
            raise ValueError('Only the manifest and checksum index may exclude their own digests.')
        entries = {}
        folded = set()
        for row in manifest['files']:
            if not isinstance(row, dict) or set(row) != {'path', 'bytes', 'sha256'} or not safe_relative(row.get('path')):
                raise ValueError('Invalid package manifest entry.')
            if row['path'].casefold() in folded or row['path'] in INTEGRITY_EXCLUSIONS:
                raise ValueError('Duplicate, case-colliding, or self-referential manifest entry.')
            if not isinstance(row['bytes'], int) or isinstance(row['bytes'], bool) or row['bytes'] < 0 or not isinstance(row['sha256'], str) or not re.fullmatch(r'[a-f0-9]{64}', row['sha256']):
                raise ValueError('Invalid manifest size or SHA-256.')
            entries[row['path']] = row
            folded.add(row['path'].casefold())
        actual = {path.relative_to(root).as_posix(): path for path in source_files(root) if path.relative_to(root).as_posix() not in INTEGRITY_EXCLUSIONS}
        for name in sorted(set(actual) - set(entries)):
            errors.append('Unlisted package file: ' + name)
        for name in sorted(set(entries) - set(actual)):
            errors.append('Missing or excluded manifest file: ' + name)
        for name in sorted(set(actual) & set(entries)):
            raw = actual[name].read_bytes()
            if len(raw) != entries[name]['bytes'] or hashlib.sha256(raw).hexdigest() != entries[name]['sha256']:
                errors.append('Checksum or byte-size mismatch: ' + name)
        expected_checksums = ''.join(row['sha256'] + '  ' + row['path'] + '\n' for row in manifest['files'])
        if (root / 'CHECKSUMS.sha256').read_text() != expected_checksums:
            errors.append('Checksum index differs from the exact manifest.')
    except (OSError, ValueError, TypeError) as error:
        errors.append(str(error))
    return errors
