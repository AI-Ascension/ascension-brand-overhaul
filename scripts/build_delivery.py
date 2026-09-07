#!/usr/bin/env python3
"""Create a deterministic local ZIP. Does not upload or publish anything."""
from pathlib import Path
import argparse, hashlib, json, zipfile
EXCLUDE={'.git','.execution','.execution-private','.codex','.agents','private','node_modules','.venv','venv','vendor','target','__pycache__','.pytest_cache'}
FONT={'.ttf','.otf','.woff','.woff2','.ttc','.eot'}
def build(source,destination):
    source=source.resolve(); destination=destination.resolve()
    if destination.is_relative_to(source): raise ValueError('ZIP destination must be outside the source directory.')
    entries=[]
    for p in sorted(source.rglob('*')):
        rel=p.relative_to(source)
        if any(part.casefold() in EXCLUDE for part in rel.parts): continue
        if p.is_symlink(): raise ValueError('Review symlink before packaging: '+str(rel))
        if not p.is_file(): continue
        if p.suffix.lower() in FONT: continue
        if p.name.startswith('.env') or p.suffix.lower() in {'.pem','.key','.p12','.pfx'}: continue
        if p.suffix in {'.pyc','.pyo'}: continue
        entries.append((rel.as_posix(),p.read_bytes()))
    destination.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in entries:
            info=zipfile.ZipInfo(source.name+'/'+name,date_time=(2026,9,7,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o644<<16
            z.writestr(info,data)
    return {'files':len(entries),'archive':str(destination),'sha256':hashlib.sha256(destination.read_bytes()).hexdigest()}
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('source',type=Path); p.add_argument('destination',type=Path); a=p.parse_args()
    try: result=build(a.source,a.destination)
    except (OSError,ValueError) as exc: p.exit(1,str(exc)+'\n')
    print(json.dumps(result,indent=2)); print('Pattern exclusions are not a secret scanner; review archive contents before publication.')
if __name__=='__main__': main()
