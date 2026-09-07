#!/usr/bin/env python3
"""Validate this prompt package. No network, agents, GitHub writes, or deployment."""
from pathlib import Path, PurePosixPath
import hashlib, json, re, sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_inventory import load_json, manifest_errors

LOCAL_ONLY_DIRECTORIES={'.git','.execution','.execution-private','.codex','.agents','private','node_modules','.venv','venv','vendor','target','__pycache__','.pytest_cache'}

FONT_EXTENSIONS={'.ttf','.otf','.woff','.woff2','.ttc','.eot'}
def load(path):
    return load_json(path)
def safe_relative(value):
    if not isinstance(value,str) or '\\' in value or '\x00' in value:
        return False
    p=PurePosixPath(value)
    return bool(value) and not p.is_absolute() and '..' not in p.parts and ':' not in value

def validate(root):
    errors=[]
    def check(condition,message):
        if not condition: errors.append(message)
    required=['README.md','START_HERE.md','MASTER_PROMPT.md','AGENTS.md','SOURCES.md',
              'orchestration/CONTRACT.md','orchestration/roles.json','orchestration/waves.json',
              'art/ART_MAP.md','art/ART_BRIEF.md','art/PROMPTBOOK.md','art/asset-board.html',
              'art/ASTRA_GPT_IMAGE_2_POLICY.md','art/ASTRA_ART_PROMPT_AUTHOR.md','art/generation-policy.json',
              'art/evidence-media-registry.json','art/reference-registry.json','schemas/art-generation.schema.json',
              'data/requirements.json','data/repository-map.json','data/source-register.json',
              'specs/STRATEGY.md','specs/WEBSITE.md','specs/REPO_MIGRATION.md',
              'specs/PUBLICATION.md','specs/MARKETING.md','specs/MEASUREMENT.md','specs/QA_RELEASE.md']
    for f in required: check((root/f).is_file(),f'Missing required file: {f}')
    if errors: return errors
    for directory, subdirectories, filenames in os.walk(root, followlinks=False):
        subdirectories[:]=[name for name in subdirectories if name.casefold() not in LOCAL_ONLY_DIRECTORIES]
        for name in subdirectories+filenames:
            if name.casefold() in LOCAL_ONLY_DIRECTORIES: continue
            p=Path(directory)/name
            check(not p.is_symlink(),f'Symlink is not permitted: {p.relative_to(root)}')
            check(p.suffix.lower() not in FONT_EXTENSIONS,f'Font binary found: {p.relative_to(root)}')
            if p.is_file() and p.suffix=='.json':
                try: load(p)
                except (ValueError,UnicodeError) as exc: errors.append(f'Invalid JSON {p}: {exc}')
    if errors: return errors
    info=load(root/'package-info.json')
    check(info['runtime_verified'] is False,'Prompt package must not claim runtime verification.')
    check(info['art_generated'] is False,'Prompt package must not claim completed art generation.')
    roles=load(root/'orchestration/roles.json'); rolemap={r['id']:r for r in roles}
    check(len(rolemap)==len(roles)==49,'Expected 49 unique descendant role definitions.')
    for depth,count in [(1,7),(2,14),(3,28)]:
        check(sum(r['depth']==depth for r in roles)==count,f'Unexpected count at depth {depth}.')
    for r in roles:
        check((root/r['prompt']).is_file(),f'Missing role prompt: {r["id"]}')
        expected='gpt-6-astra' if r['id'] in ['W02-C1-BUILD','W02-C2-BUILD'] else 'gpt-5.6-luna'
        check(r['requested_model']==expected and r['requested_effort']=='max',f'Wrong role-specific settings: {r["id"]}')
        check(r['may_author_art_prompts']==(expected=='gpt-6-astra'),f'Wrong authorship permission: {r["id"]}')
        if r['depth']==1: check(r['parent']=='ROOT',f'Lead parent mismatch: {r["id"]}')
        else:
            p=rolemap.get(r['parent']); check(p is not None,f'Missing parent: {r["id"]}')
            if p: check(p['depth']==r['depth']-1 and r['id'] in p['children'],f'Ancestry mismatch: {r["id"]}')
        check(r['depth']!=3 or r['children']==[],f'Leaf can spawn: {r["id"]}')
    waves=load(root/'orchestration/waves.json'); wmap={w['workstream']:w for w in waves}
    def walk(node,stack):
        if node in stack: errors.append('Dependency cycle: '+' -> '.join(stack+[node])); return
        for dep in wmap[node]['depends_on']:
            if dep not in wmap: errors.append(f'Missing dependency: {dep}')
            else: walk(dep,stack+[node])
    for node in wmap: walk(node,[])
    artwork=load(root/'art/asset-registry.json')
    evidence=load(root/'art/evidence-media-registry.json'); references=load(root/'art/reference-registry.json')
    check(len(artwork)==72 and len(evidence)==3 and len(references)==5,'Unexpected visual-resource classification counts.')
    assets=artwork+evidence+references; amap={a['id']:a for a in assets}
    for a in artwork:
        check(a['method']=='generate' and a['generation_model']=='gpt-image-2' and a['prompt_author_model']=='gpt-6-astra',f'Wrong art pipeline: {a["id"]}')
        check(a['prompt_author_role_id'] in ['W02-C1-BUILD','W02-C2-BUILD'],f'Wrong art author role: {a["id"]}')
        check(all(e['format']!='svg' for e in a['exports']),f'Native vector art promise: {a["id"]}')
    for a in evidence:
        check(a['method']=='authentic_capture' and a['generation_prohibited'] is True,f'Unsafe evidence handling: {a["id"]}')
    for a in references:
        check(a['method']=='preserve_reference' and a['allowed_on_new_brand_surfaces'] is False,f'Legacy artwork substitution allowed: {a["id"]}')
    check(len(amap)==len(assets),'Duplicate asset ID.')
    surfaces=load(root/'art/surface-map.json'); smap={s['id']:s for s in surfaces}
    allpaths=[]
    for a in assets:
        check(a['status']=='planned',f'Incorrect package asset state: {a["id"]}')
        check(a['method'] in ['generate','authentic_capture','preserve_reference'],f'Unknown art method: {a["id"]}')
        check(bool(a['exports']) or a['method']=='preserve_reference',f'No required exports: {a["id"]}')
        for e in a['exports']:
            check(safe_relative(e['path']),f'Unsafe export path: {e["path"]}'); allpaths.append(e['path'])
        for parent in a['parent_asset_ids']: check(parent in amap,f'Missing parent asset: {parent}')
        for placement in a['placements']:
            check(placement in smap,f'Unknown placement: {placement}')
            if placement in smap: check(a['id'] in (smap[placement]['asset_ids']+smap[placement].get('evidence_media_ids',[])+smap[placement].get('reference_ids',[])),f'Unmapped placement: {a["id"]}')
    check(len(set(p.casefold() for p in allpaths))==len(allpaths),'Export paths collide, including case-insensitive matches.')
    visited=set()
    def asset_walk(node,stack):
        if node in stack: errors.append('Asset dependency cycle at '+node); return
        if node in visited: return
        for dep in amap[node]['parent_asset_ids']:
            if dep in amap: asset_walk(dep,stack+[node])
        visited.add(node)
    for node in amap: asset_walk(node,[])
    for surface in surfaces:
        for aid in surface['asset_ids']+surface.get('evidence_media_ids',[])+surface.get('reference_ids',[]):
            check(aid in amap,f'Unknown surface asset: {aid}')
    req=load(root/'data/requirements.json')
    check(len(req)==len({r['id'] for r in req}) and len(req)>=70,'Requirement ID/count error.')
    for r in req:
        check(r['workstream'] in wmap and r['status']=='not_started',f'Invalid requirement state/owner: {r["id"]}')
    policy=load(root/'art/generation-policy.json')
    check(policy['image_generation_model']=='gpt-image-2' and policy['art_prompt_author_model']=='gpt-6-astra','Wrong artwork model policy.')
    check(policy['allow_model_substitution'] is False,'Image/author model fallback enabled.')
    check(sum(r['requested_model']=='gpt-6-astra' for r in roles)==2,'Expected two Astra art-author roles.')
    check(sum(r['requested_model']=='gpt-5.6-luna' for r in roles)==47,'Expected forty-seven Luna roles.')
    config=(root/'orchestration/runtime-config.example.toml').read_text()
    check(not re.search(r'^\s*max_depth\s*=',config,re.M),'An unsupported depth config was assumed.')
    errors.extend(manifest_errors(root))
    return errors

def main():
    root=Path(__file__).resolve().parents[1]
    errors=validate(root)
    if errors:
        print('\n'.join('ERROR: '+e for e in errors)); return 1
    print('PASS: prompt-package structure, role tree, requirements, asset map, and available integrity records.')
    print('This does not verify native agents, generated art, GitHub mutations, or target implementation.')
    return 0
if __name__=='__main__': sys.exit(main())
