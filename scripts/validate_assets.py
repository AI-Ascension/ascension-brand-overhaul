#!/usr/bin/env python3
"""Verify future generated artwork, native author records, file hashes and safe derivatives."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art_policy import POLICY, validate_generation_record
from agent_ledger import validate_ledger

FONTS = {'.ttf', '.otf', '.woff', '.woff2', '.ttc', '.eot'}

def checked_path(root, value):
    p = PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Unsafe export path: ' + value)
    target = (root / str(p)).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Export escapes output root.')
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Symlink export is not allowed.')
    return target


def inspect_svg(raw):
    """Security utility for referenced legacy/functional SVG; not an allowed new-art method."""
    if b'<!DOCTYPE' in raw.upper() or b'<!ENTITY' in raw.upper():
        raise ValueError('SVG entity/doctype not permitted.')
    el = ET.fromstring(raw)
    for item in el.iter():
        tag = item.tag.rsplit('}', 1)[-1].lower()
        if tag in {'script', 'foreignobject', 'iframe', 'object', 'embed'}:
            raise ValueError('Active SVG element.')
        for key, value in item.attrib.items():
            k = key.rsplit('}', 1)[-1].lower()
            if k.startswith('on'):
                raise ValueError('SVG event handler.')
            if k == 'href' and not value.startswith('#'):
                raise ValueError('SVG external/embed reference.')
            if re.search(r'url\(\s*["\x27]?\s*(https?:|//|data:)', value, re.I):
                raise ValueError('External SVG style reference.')
    return el


def verify(registry, manifest, root, ledger=None):
    errors = []
    if ledger is not None:
        try:
            validate_ledger(ledger)
        except (ValueError, KeyError, TypeError) as exc:
            errors.append('Native ledger rejected: ' + str(exc))
    entries = {a['asset_id']: a for a in manifest}
    if len(entries) != len(manifest):
        errors.append('Duplicate delivered asset IDs.')
    expected = {a['id']: a for a in registry}
    for extra in set(entries) - set(expected):
        errors.append('Unregistered delivered art: ' + extra)
    for aid, planned in expected.items():
        if not planned['mandatory']:
            continue
        got = entries.get(aid)
        if not got:
            errors.append('Missing asset: ' + aid)
            continue
        if got.get('status') != 'verified':
            errors.append('Not verified: ' + aid)
            continue
        if planned.get('method') != 'generate' or got.get('method') != 'generate':
            errors.append('All new artwork must use generation: ' + aid)
        if got.get('origin') != 'astra_authored_gpt_image_2':
            errors.append('Wrong artwork origin: ' + aid)
        if not got.get('reviewer_reference'):
            errors.append('Missing independent reviewer: ' + aid)
        if got.get('rights_status') in {None, 'unreviewed', 'unknown', 'blocked'}:
            errors.append('Uncleared use: ' + aid)
        if not got.get('source_references'):
            errors.append('Missing source lineage: ' + aid)
        records = got.get('generation_records', [])
        if not records:
            errors.append('Missing Astra/gpt-image-2 generation records: ' + aid)
        record_map = {r['record_id']: r for r in records}
        if len(record_map) != len(records):
            errors.append('Duplicate generation record ID: ' + aid)
        for record in records:
            errors.extend(aid + ': ' + message for message in validate_generation_record(record, planned, root, ledger))
        export_map = {e['path']: e for e in got.get('exports', [])}
        if len(export_map) != len(got.get('exports', [])):
            errors.append('Duplicate export path: ' + aid)
        expected_paths = {e['path'] for e in planned['exports']}
        if set(export_map) != expected_paths:
            errors.append('Delivered exports must exactly match the planned export set: ' + aid)
        if len({path.casefold() for path in export_map}) != len(export_map):
            errors.append('Export paths collide on a case-insensitive filesystem: ' + aid)
        for e in planned['exports']:
            actual = export_map.get(e['path'])
            if not actual:
                errors.append('Missing export: ' + e['path'])
                continue
            try:
                path = checked_path(root, e['path'])
                if path.suffix.lower() in FONTS:
                    raise ValueError('Font binary prohibited in delivery.')
                if e.get('requires_generation_lineage', True):
                    if path.suffix.lower() == '.svg':
                        raise ValueError('Native/traced/SVG-wrapper artwork is not a gpt-image-2 raster master.')
                    rec = record_map.get(actual.get('generation_record_id'))
                    if rec is None:
                        raise ValueError('Export lacks a valid generation record.')
                    if actual.get('raw_source_path') not in {o['path'] for o in rec.get('raw_outputs', [])}:
                        raise ValueError('Export does not identify its original generated source.')
                    steps = actual.get('derivation_operations')
                    if not isinstance(steps, list) or not steps:
                        raise ValueError('Export needs explicit mechanical derivation operations.')
                    if any(s not in POLICY['allowed_export_operations'] for s in steps):
                        raise ValueError('Prohibited creative post-processing.')
                raw = path.read_bytes()
                if hashlib.sha256(raw).hexdigest() != actual['sha256']:
                    raise ValueError('SHA-256 mismatch.')
                if path.suffix.lower() == '.png':
                    if raw[:8] != b'\x89PNG\r\n\x1a\n' or len(raw) < 24:
                        raise ValueError('Invalid PNG header.')
                    width, height = struct.unpack('>II', raw[16:24])
                    if actual.get('width') != width or actual.get('height') != height:
                        raise ValueError('PNG dimensions mismatch.')
                    size = re.match(r'^(\d+)×(\d+)', e.get('size', ''))
                    if size and (width, height) != tuple(map(int, size.groups())):
                        raise ValueError('PNG dimensions do not match planned export.')
            except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as exc:
                errors.append(f'{aid} {e["path"]}: {exc}')
    return errors


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', required=True, type=Path)
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--ledger', required=True, type=Path, help='Actual native agent ledger, not a fabricated test fixture.')
    p.add_argument('--registry', type=Path, default=Path(__file__).resolve().parents[1] / 'art/asset-registry.json')
    a = p.parse_args()
    try:
        errors = verify(json.loads(a.registry.read_text()), json.loads(a.manifest.read_text()), a.root,
                        json.loads(a.ledger.read_text()))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, str(exc) + '\n')
    if errors:
        p.exit(1, '\n'.join(errors) + '\n')
    print('PASS: declared Astra/gpt-image-2 policy, native-ledger consistency, hashes and supported file checks.')
    print('Inspect referenced actual runtime/image-call evidence and all exports independently; this is not provider attestation.')

if __name__ == '__main__':
    main()
