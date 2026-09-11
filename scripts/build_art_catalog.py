#!/usr/bin/env python3
"""Refresh local artwork access views from the current source and asset records."""
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    registry_path = ROOT / 'art/asset-registry.json'
    registry = json.loads(registry_path.read_text())
    manifest = json.loads((ROOT / 'brand/asset-manifest.json').read_text())
    delivered = {row['asset_id']: row for row in manifest}
    if len(delivered) != len(manifest) or set(delivered) != {row['id'] for row in registry}:
        raise ValueError('Catalog inventory differs from asset manifest')
    rows = []
    for planned in registry:
        actual = delivered[planned['id']]
        rows.append({**planned, 'status': actual['status'],
                     'rights_status': actual['rights_status'],
                     'reviewer_reference': actual['reviewer_reference'],
                     'delivered_exports': actual['exports'], 'blocker': actual['blocker']})
    for name in ('evidence-media-registry.json', 'reference-registry.json'):
        rows.extend(json.loads((ROOT / 'art' / name).read_text()))
    board_path = ROOT / 'art/asset-board.html'
    board = board_path.read_text()
    payload = json.dumps(rows, ensure_ascii=False).replace('</', '<\\/')
    board, count = re.subn(r'(<script id="registry" type="application/json">).*?(</script>)',
                          lambda match: match[1] + payload + match[2], board, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Catalog data anchor missing')
    sources = json.loads((ROOT / 'brand/provenance/root-generation-index.json').read_text())['records']
    formats = Counter(export['format'] for row in manifest for export in row['exports'])
    statuses = Counter(row['status'] for row in manifest)
    raster_count = sum(formats[name] for name in ('png', 'webp', 'jpeg', 'jpg'))
    notice = (f'{len(registry)} artwork families · 3 authentic evidence-media families · 5 historical/reference records. '
              f'{len(sources)} preserved generated sources; {sum(formats.values())} planned export files exist. '
              f'{statuses["verified"]} families verified; {statuses["blocked"]} still require approved content or integration. '
              'Root generation is user-authorized. Model/backend identity remains unknown.')
    board, count = re.subn(r'(<p class="notice">).*?(</p>)',
                          lambda match: match[1] + notice + match[2], board, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Catalog notice anchor missing')
    board_path.write_text(board)
    lines = [
        '# Artwork access and execution status', '',
        'Updated ' + datetime.now(timezone.utc).isoformat() + '. The user authorized root generation with the available image tool; see [the recorded amendment](../art/root-generation-authorization.json).', '',
        f'{len(sources)} generated sources, including superseded attempts, are preserved with exact prompts, input references and SHA-256 hashes. {raster_count} raster exports, {formats["webm"]} WebM transition and {formats["html"]} functional HTML exports exist. Asset-family states: ' + ', '.join(f'{count} {state}' for state, count in sorted(statuses.items())) + '.', '',
        'The full requirement remains 72 families and 115 exports. Verified artwork means the scoped generation, source-use and export review passed; it does not authorize public distribution.', '',
        'Image access resumed after the historical service-limit failures. See the [successful access observation](../execution/reviews/root-image-access-restored.json) and the subsequent source/export records. The [earlier failure receipt](../execution/reviews/root-image-service-limit.json) is retained as history, not a current capacity blocker.', '',
        'A file can exist while its asset brief remains incomplete. Blank campaign layouts are preparatory templates; they do not supply approved episode outcomes, challenge rules, release facts or contributor permissions. The transition has separate mechanical and local-browser receipts, not live broadcast proof.', '',
        'The image backend and root author model remain unknown. The original native agent hierarchy is a separate unmet requirement. Generated artwork is not gameplay or provider evidence. The press approval registry remains empty.', '',
        '| Family | Current status | Existing exports | Remaining gate |',
        '| --- | --- | ---: | --- |',
    ]
    for row in manifest:
        blocker = (row['blocker'] or 'No remaining source/export gate; public distribution approval is separate.').replace('|', '\\|').replace('\n', ' ')
        lines.append(f'| {row["asset_id"]} | {row["status"]} | {len(row["exports"])} | {blocker} |')
    lines.extend(['', 'Review the [asset board](../art/asset-board.html), [functional specimen](assets/identity/specimen.html), [press catalog](assets/press/index.html), [source records](provenance/root-generation-records.json), and [export receipts](provenance/root-export-receipts.json).', ''])
    (ROOT / 'brand/ART_ACCESS.md').write_text('\n'.join(lines))
    print(f'Refreshed {len(registry)} artwork families and {len(rows)} catalog resources.')


if __name__ == '__main__':
    main()
