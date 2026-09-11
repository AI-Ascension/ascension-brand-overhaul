#!/usr/bin/env python3
"""Create a deterministic local ZIP. Does not upload or publish anything."""
from pathlib import Path
import argparse, hashlib, json, zipfile, sys, os, tempfile
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_inventory import source_files, manifest_errors, load_json
def build(source,destination,reviewed_manifest_sha256=None):
    if destination.is_symlink() or any(parent.is_symlink() for parent in destination.parents):
        raise ValueError('Archive destination may not use symlinks.')
    if destination.exists(): raise FileExistsError('Archive destination already exists.')
    paths=source_files(source)
    source=source.resolve(); destination=destination.resolve()
    if destination.is_relative_to(source): raise ValueError('ZIP destination must be outside the source directory.')
    manifest_path=source/'MANIFEST.json'
    manifest_digest=None
    if manifest_path.exists():
        problems=manifest_errors(source)
        if problems: raise ValueError('Source manifest validation failed: '+'; '.join(problems))
        manifest_digest=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    if reviewed_manifest_sha256 is not None and (manifest_digest is None or reviewed_manifest_sha256!=manifest_digest):
        raise ValueError('Reviewed manifest digest does not match the validated source manifest.')
    expected={entry['path']:entry for entry in load_json(manifest_path)['files']} if manifest_digest else {}
    entries=[]
    for p in paths:
        p=p.resolve()
        rel=p.relative_to(source)
        raw=p.read_bytes()
        if rel.as_posix() in expected:
            entry=expected[rel.as_posix()]
            if len(raw)!=entry['bytes'] or hashlib.sha256(raw).hexdigest()!=entry['sha256']:
                raise ValueError('Source changed after manifest verification: '+str(rel))
        entries.append((rel.as_posix(),raw))
    destination.parent.mkdir(parents=True,exist_ok=True)
    descriptor,name=tempfile.mkstemp(prefix='.ascension-archive-',dir=destination.parent)
    staging=Path(name); os.close(descriptor)
    try:
        with zipfile.ZipFile(staging,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in entries:
                info=zipfile.ZipInfo(source.name+'/'+name,date_time=(2026,9,7,0,0,0))
                info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
                z.writestr(info,data)
        os.link(staging,destination)
    finally:
        staging.unlink(missing_ok=True)
    return {'files':len(entries),'archive':str(destination),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'classification':'reviewed_source_archive' if reviewed_manifest_sha256 else 'unreviewed_local_archive','reviewed_manifest_sha256':reviewed_manifest_sha256}
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('source',type=Path); p.add_argument('destination',type=Path); p.add_argument('--reviewed-manifest-sha256',help='Exact digest after manual content review; does not authorize publication'); a=p.parse_args()
    try: result=build(a.source,a.destination,a.reviewed_manifest_sha256)
    except (OSError,ValueError) as exc: p.exit(1,str(exc)+'\n')
    print(json.dumps(result,indent=2)); print('Pattern exclusions are not a secret scanner; review archive contents before publication.')
if __name__=='__main__': main()
