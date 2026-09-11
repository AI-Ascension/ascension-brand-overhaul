#!/usr/bin/env python3
"""Review or refresh active package integrity records; original input stays archived."""
import argparse
import hashlib
import json
from pathlib import Path

from package_inventory import INTEGRITY_EXCLUSIONS, load_json, source_files


def refresh(root, write=False):
    manifest = load_json(root / 'MANIFEST.json')
    files = []
    for path in source_files(root):
        name = path.relative_to(root).as_posix()
        if name in INTEGRITY_EXCLUSIONS:
            continue
        raw = path.read_bytes()
        files.append({'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
    result = {'package': manifest['package'], 'version': manifest['version'], 'integrity_exclusions': sorted(INTEGRITY_EXCLUSIONS), 'files': files}
    if write:
        (root / 'MANIFEST.json').write_text(json.dumps(result, indent=2) + '\n')
        (root / 'CHECKSUMS.sha256').write_text(''.join(row['sha256'] + '  ' + row['path'] + '\n' for row in files))
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = refresh(args.root, args.write)
    print(json.dumps({'mode': 'write' if args.write else 'dry_run', 'files': len(result['files']), 'bytes': sum(row['bytes'] for row in result['files'])}))
