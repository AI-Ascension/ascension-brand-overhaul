#!/usr/bin/env python3
"""Render a status handoff from curated execution ledgers; never infer completion."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


def read(root, name):
    path = root / name
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('Unsafe ledger path: ' + name)
    if not path.is_file():
        raise ValueError('Ledger must be a regular file: ' + name)
    with path.open('rb') as handle:
        raw = handle.read(4 * 1024 * 1024 + 1)
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError('Ledger exceeds 4 MiB: ' + name)
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError('Duplicate ledger key: ' + key)
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique)


def validate_release(value):
    fields = {'schema_version', 'summary', 'dimensions', 'verified_work',
              'remaining_conditions', 'review_records', 'unverified_assumptions'}
    def nonempty(text):
        return isinstance(text, str) and bool(text.strip()) and len(text) <= 10000
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError('Invalid release ledger fields.')
    if value['schema_version'] != 'ai-ascension.release-status.v1' or not nonempty(value['summary']):
        raise ValueError('Invalid release ledger marker or summary.')
    dimensions = value['dimensions']
    if not isinstance(dimensions, dict) or not 1 <= len(dimensions) <= 20 or not all(nonempty(k) and nonempty(v) for k, v in dimensions.items()):
        raise ValueError('Invalid release ledger dimensions.')
    for field in fields - {'schema_version', 'summary', 'dimensions'}:
        rows = value[field]
        if not isinstance(rows, list) or not 1 <= len(rows) <= 200 or not all(nonempty(row) for row in rows):
            raise ValueError('Invalid release ledger string array: ' + field)
    return value


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\n', ' ')


def indexed(rows, field):
    result = {}
    for row in rows:
        key = row[field]
        if key in result:
            raise ValueError('Duplicate ledger identifier: ' + key)
        result[key] = row
    return result


def render(root, require_release=False):
    requirements = indexed(read(root, 'data/requirements.json'), 'id')
    status = read(root, 'execution/requirements-status.json')
    observed = indexed(status['requirements'], 'id')
    assets = indexed(read(root, 'art/asset-registry.json'), 'id')
    produced = indexed(read(root, 'brand/asset-manifest.json'), 'asset_id')
    if requirements.keys() != observed.keys() or assets.keys() != produced.keys():
        raise ValueError('Handoff must account for every required requirement and asset exactly once.')
    allowed = {'not_started', 'in_progress', 'implemented', 'verified', 'blocked', 'not_applicable_with_reason'}
    for key, row in observed.items():
        if row['status'] not in allowed:
            raise ValueError('Unknown requirement state: ' + key)
        if row['requirement'] != requirements[key]['requirement'] or row['mandatory'] != requirements[key]['mandatory']:
            raise ValueError('Execution ledger changed a binding requirement: ' + key)
        if row['status'] == 'verified' and not (row.get('verification_records') and row.get('independent_reviewer')):
            raise ValueError('Verified requirement lacks evidence or reviewer: ' + key)
        if row['status'] == 'not_applicable_with_reason' and not row.get('reason'):
            raise ValueError('Inapplicability lacks a reason: ' + key)
        if row['status'] == 'blocked' and not any(isinstance(row.get(field), str) and row[field].strip() for field in ('blocker', 'reason')):
            raise ValueError('Blocked requirement lacks a blocker or reason: ' + key)
    for key, row in produced.items():
        if row['status'] == 'blocked' and not isinstance(row.get('blocker'), str):
            raise ValueError('Blocked asset lacks a blocker: ' + key)
        if row['status'] == 'blocked' and not row['blocker'].strip():
            raise ValueError('Blocked asset has an empty blocker: ' + key)
    lines = ['# Implementation handoff', '',
             'This generated report records ledger states, not an independent completion verdict. Missing evidence remains incomplete. See the linked implementation, review and operational records before taking action.', '',
             'Requirement ledger updated: ' + cell(status['updated_at']), '',
             '## Requirement states', '', '| State | Count |', '| --- | ---: |']
    lines += [f'| {cell(key)} | {count} |' for key, count in sorted(Counter(r['status'] for r in observed.values()).items())]
    release_path = root / 'execution/release-status.json'
    release_present = release_path.exists() or release_path.is_symlink()
    if require_release and not release_present:
        raise ValueError('Final handoff requires execution/release-status.json.')
    if release_present:
        release = validate_release(read(root, 'execution/release-status.json'))
        lines += ['', '## Delivery scope', '', cell(release['summary']), '',
                  '| Dimension | State |', '| --- | --- |']
        lines += ['| ' + cell(key) + ' | ' + cell(value) + ' |' for key, value in release['dimensions'].items()]
        lines += ['', '## Verified local work and remaining dependencies', '']
        lines += ['- ' + cell(value) for value in release['verified_work']]
        lines += ['', 'Required next conditions:', '']
        lines += ['- ' + cell(value) for value in release['remaining_conditions']]
        lines += ['', 'Unverified assumptions and known limitations:', '']
        lines += ['- ' + cell(value) for value in release['unverified_assumptions']]
        lines += ['', 'Review records: ' + ', '.join(cell(value) for value in release['review_records']), '',
                  'Reproduction: `delivery/RUNBOOK.md`. Private archive scope: `delivery/PRIVACY_SCOPE.md`. The final archive and final remote-head receipts are external to the archive to avoid self-referential hashes.']
    lines += ['', '## Requirement inventory', '', '| ID | State | Requirement | Implementation | Reviewer | Blocker |', '| --- | --- | --- | --- | --- | --- |']
    for key, row in observed.items():
        lines.append('| ' + ' | '.join(map(cell, [key, row['status'], row['requirement'], ', '.join(row.get('implementation_paths', [])) or 'not recorded', row.get('independent_reviewer') or 'not recorded', row.get('blocker') or row.get('reason') or 'none recorded; state is authoritative'])) + ' |')
    lines += ['', '## Mandatory artwork inventory', '', '| ID | State | Required exports | Recorded exports | Blocker |', '| --- | --- | ---: | ---: | --- |']
    for key, row in produced.items():
        lines.append('| ' + ' | '.join(map(cell, [key, row['status'], len(assets[key]['exports']), len(row['exports']), row.get('blocker') or 'none recorded'])) + ' |')
    operations = read(root, 'execution/operations.json')
    lines += ['', '## External operation ledger', '']
    for category in ['operations', 'merges', 'renames', 'deployments', 'campaign_sends']:
        rows = operations[category]
        lines.append(f'- {category}: {len(rows)} recorded operation(s).')
        for row in rows:
            lines.append('  - ' + cell(json.dumps(row, sort_keys=True)))
    lines += ['', '## Reproduction and limits', '',
              'Run `python3 scripts/validate_package.py` and `python3 -m unittest discover -s tests` for package checks. Product and host validation are separate. Follow `docs/OPERATIONS.md` and `docs/ROLLBACK.md`; consult `execution/root-helper-checks.json`, `execution/toolchain.json`, and independent review records for the exact tested scope.', '',
              'Art authorship and image route: `execution/art-model-attestation.json`. Source claims: `execution/source-snapshot.json` and `execution/capabilities.json`. This report does not grant deployment, rename, merge, private-publication or campaign authority.', '',
              '## Input digests', '', '| Ledger | SHA-256 |', '| --- | --- |']
    for name in ['data/requirements.json', 'execution/requirements-status.json', 'art/asset-registry.json', 'brand/asset-manifest.json', 'execution/operations.json'] + (['execution/release-status.json'] if release_present else []) + [name for name in ['execution/source-snapshot.json', 'execution/source-tree-inventory.json'] if (root / name).is_file()]:
        lines.append(f'| {name} | {hashlib.sha256((root / name).read_bytes()).hexdigest()} |')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--require-release', action='store_true', help='Require the strict release ledger; always enabled for FINAL_REPORT.md')
    args = parser.parse_args()
    try:
        result = render(args.root, require_release=args.require_release or args.output.name == 'FINAL_REPORT.md')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('x') as handle:
            handle.write(result)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f'Handoff rendering failed: {error}\n')


if __name__ == '__main__':
    main()
