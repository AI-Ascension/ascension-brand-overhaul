#!/usr/bin/env python3
"""Build the static press catalog from explicitly approved raster exports."""
import hashlib
import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from art_policy import safe_file
from validate_assets import verify

ROOT = Path(__file__).resolve().parents[1]


def approval_digest(approval):
    raw = json.dumps(approval, ensure_ascii=False, sort_keys=True,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def require_enrolled_approval(approval):
    """The operator protects this fixed registry independently of content input."""
    registry = json.loads(safe_file(ROOT, 'config/press-authorities.json').read_text())
    if (not isinstance(registry, dict)
            or set(registry) != {'schema_version', 'approvals'}
            or registry['schema_version'] != 'press-authorities-v1'
            or not isinstance(registry['approvals'], list)):
        raise ValueError('Invalid trusted press approval registry')
    ids = set()
    for record in registry['approvals']:
        if (not isinstance(record, dict)
                or set(record) != {'approval_id', 'authority_reference', 'approval_digest'}
                or not all(isinstance(v, str) and v for v in record.values())
                or not re.fullmatch('[a-f0-9]{64}', record['approval_digest'])
                or record['approval_id'] in ids):
            raise ValueError('Invalid trusted press approval registry entry')
        ids.add(record['approval_id'])
    expected = {'approval_id': approval['approval_id'],
                'authority_reference': approval['authority_reference'],
                'approval_digest': approval_digest(approval)}
    if expected not in registry['approvals']:
        raise ValueError('Press approval is not enrolled in the trusted registry')


def verify_lineage(asset, registry, manifest):
    """Check the approved family and its actual shared-generation ancestors."""
    plans = {row['id']: row for row in registry}
    deliveries = {row['asset_id']: row for row in manifest}
    if len(plans) != len(registry) or len(deliveries) != len(manifest):
        raise ValueError('Duplicate asset ID in press source records')
    selected = set()
    pending = [asset['asset_id']]
    while pending:
        aid = pending.pop()
        if aid in selected:
            continue
        if aid not in plans or aid not in deliveries:
            raise ValueError('Missing press generation ancestor: ' + aid)
        selected.add(aid)
        for record in deliveries[aid].get('generation_records', []):
            source = record.get('asset_id')
            if source != aid:
                pending.append(source)
    # Every selected asset is checked even if a future registry makes it optional.
    scoped_plans = [{**plans[aid], 'mandatory': True} for aid in sorted(selected)]
    failures = verify(scoped_plans, [deliveries[aid] for aid in sorted(selected)], ROOT)
    if failures:
        raise ValueError('Press asset lineage rejected: ' + '; '.join(failures))


def main():
    manifest = json.loads((ROOT / 'brand/asset-manifest.json').read_text())
    registry = json.loads((ROOT / 'art/asset-registry.json').read_text())
    titles = {a['id']: a['title'] for a in registry}
    approval_schema = Draft202012Validator(json.loads((ROOT / 'schemas/approval.schema.json').read_text()), format_checker=FormatChecker())
    now = datetime.now(timezone.utc)
    entries = []
    for asset in manifest:
        if (asset['status'] != 'verified'
                or not asset.get('approval_references')
                or asset['rights_status'] in {'unknown', 'unreviewed', 'blocked'}):
            continue
        # Approval references must be actual local records; a nonempty label
        # alone is not enough to create a public download.
        approvals = []
        for reference in asset['approval_references']:
            approval = json.loads(safe_file(ROOT, reference).read_text())
            approval_schema.validate(approval)
            approvals.append(approval)
        for export in asset['exports']:
            if export['format'] not in {'png', 'webp', 'jpeg', 'jpg'}:
                continue
            approved = False
            for approval in approvals:
                expiry = approval.get('expires_at')
                expires_at = datetime.fromisoformat(expiry.replace('Z', '+00:00')) if expiry else None
                if expires_at is not None and expires_at.tzinfo is None:
                    raise ValueError('Approval expiry requires a timezone')
                issued_at = datetime.fromisoformat(approval['approved_at'].replace('Z', '+00:00'))
                if (approval['operation'] == 'publish_asset'
                        and approval['target'] == export['path']
                        and approval['source_digest'] == export['sha256']
                        and 'press_kit' in approval['allowed_surfaces']
                        and 'asset' in approval['allowed_fields']
                        and approval['revoked'] is False
                        and issued_at <= now
                        and (expires_at is None or expires_at > now)):
                    approved = True
                    break
            if not approved:
                continue
            require_enrolled_approval(approval)
            verify_lineage(asset, registry, manifest)
            path = safe_file(ROOT, export['path'])
            if hashlib.sha256(path.read_bytes()).hexdigest() != export['sha256']:
                raise ValueError('Press export hash mismatch')
            label = html.escape(titles[asset['asset_id']])
            href = '../../../' + html.escape(export['path'], quote=True)
            caption = html.escape(asset['alt_text'])
            rights = html.escape(asset['rights_status'])
            entries.append(f'<article><h2>{label}</h2><p>{caption}</p>'
                           f'<p>{export["width"]} × {export["height"]} · {export["format"].upper()} · {rights}</p>'
                           f'<p><a href="{href}" download>Download {label}</a></p>'
                           f'<p>Source: generated artwork. SHA-256: <code>{export["sha256"]}</code></p></article>')
    content = '\n'.join(entries) if entries else '<p>No artwork has completed approval for public distribution yet. This catalog will list approved files when they are available.</p>'
    page = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Ascension — press assets</title><link rel="stylesheet" href="../../tokens.css">
<style>body{margin:0;background:var(--aa-color-surface-page);color:var(--aa-color-text-primary);font-family:var(--aa-font-body);line-height:1.6}main{max-width:66rem;padding:clamp(1rem,5vw,4rem);margin:auto}h1,h2{font-family:var(--aa-font-display);line-height:1.1}h1{font-size:clamp(2.5rem,8vw,5rem)}article,footer{border-top:1px solid var(--aa-color-border-default);padding-top:1.5rem;margin-top:2rem}p{max-width:65ch}a{color:var(--aa-color-accent-text)}code{overflow-wrap:anywhere}</style>
<main><header><p>AI Ascension</p><h1>Press assets</h1><p>Approved artwork, captions, source labels, and usage records.</p></header>
''' + content + '''
<footer><p>Generated illustrations are not gameplay captures or evidence of a model result. Font binaries are not included.</p><p><a href="../../BRAND_GUIDE.md">Brand and attribution guidance</a></p></footer></main></html>
'''
    path = ROOT / 'brand/assets/press/index.html'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(page)
    print(f'Built press index with {len(entries)} approved raster downloads.')


if __name__ == '__main__':
    main()
