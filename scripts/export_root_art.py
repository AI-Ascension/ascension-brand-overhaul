#!/usr/bin/env python3
"""Mechanically export recorded generated masters; never draw or repair artwork.

The recipe names every source and crop. This receipt proves byte lineage only;
design review and publication approval remain separate requirements.
"""
import hashlib
import json
from pathlib import Path

from PIL import Image
from art_policy import safe_file

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    recipe = json.loads((ROOT / 'brand/provenance/root-export-recipe.json').read_text())
    sources = json.loads((ROOT / 'brand/provenance/root-generation-index.json').read_text())['records']
    recorded = {row['source_path']: row['source_sha256'] for row in sources}
    receipts = []
    for row in recipe['exports']:
        source = safe_file(ROOT, row['source_path'])
        if digest(source) != recorded[row['source_path']]:
            raise ValueError('Generated master hash mismatch: ' + row['source_path'])
        with Image.open(source) as master:
            box = tuple(row['crop_box'])
            if not (0 <= box[0] < box[2] <= master.width and 0 <= box[1] < box[3] <= master.height):
                raise ValueError('Crop exceeds source bounds')
            target_size = tuple(row['size'])
            if abs((box[2]-box[0])/(box[3]-box[1]) / (target_size[0]/target_size[1]) - 1) > 0.005:
                raise ValueError('Recipe would distort artwork: ' + row['output_path'])
            output = safe_file(ROOT, row['output_path'])
            output.parent.mkdir(parents=True, exist_ok=True)
            exported = master.crop(box).resize(target_size, Image.Resampling.LANCZOS)
            if output.suffix == '.webp':
                encoding = row.get('encoding', {'lossless': True, 'method': 6})
                if (not isinstance(encoding, dict)
                        or set(encoding) - {'lossless', 'quality', 'method'}
                        or type(encoding.get('lossless', True)) is not bool
                        or type(encoding.get('quality', 100)) is not int
                        or not 1 <= encoding.get('quality', 100) <= 100
                        or type(encoding.get('method', 6)) is not int
                        or not 0 <= encoding.get('method', 6) <= 6):
                    raise ValueError('Invalid WebP encoding settings')
                exported.save(output, **encoding)
            else:
                exported.save(output, optimize=True)
            receipts.append({**row, 'source_sha256': digest(source),
                             'output_sha256': digest(output), 'output_bytes': output.stat().st_size,
                             'operations': ['crop', 'resize', 'encode', 'metadata_strip'],
                             'publication_approved': False})
    target = ROOT / 'brand/provenance/root-export-receipts.json'
    target.write_text(json.dumps({'schema_version': 'root-mechanical-export-receipts-v1',
                                  'exports': receipts}, indent=2) + '\n')
    print(f'Exported {len(receipts)} raster files with source hashes and crop receipts.')


if __name__ == '__main__':
    main()
