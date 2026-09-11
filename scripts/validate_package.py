#!/usr/bin/env python3
"""Validate this prompt package. No network, agents, GitHub writes, or deployment."""
from pathlib import Path, PurePosixPath
import hashlib, json, re, sys, os
sys.path.insert(0, str(Path(__file__).resolve().parent))
from package_inventory import load_json, manifest_errors, source_files
from art_policy import ART_ROLES, LEGACY_ROUTE, ROOT_ROUTE, ROUTES, validate_root_authorization

LOCAL_ONLY_DIRECTORIES={'.git','.execution','.execution-private','.codex','.agents','private','node_modules','.venv','venv','vendor','target','__pycache__','.pytest_cache'}

FONT_EXTENSIONS={'.ttf','.otf','.woff','.woff2','.ttc','.eot'}

# Workstation-specific filesystem paths identify a contributor's machine and never belong in
# delivery or review evidence. Records must use a neutral placeholder such as
# <workstation>/sts2-project/... or a repository-relative path. Case-insensitive forms cover
# absolute Linux home directories, WSL mounts, macOS homes, Windows profiles (both slash
# directions), and UNC WSL shares; relative "home" or "users" segments (site/home/, api/users/) are not.
PERSONAL_PATH_PATTERN=re.compile(r'(?<![a-z0-9._/-])/(?:home|mnt/[a-z]/users|users)/[a-z]|[a-z]:[\\/]+users[\\/]|\\\\wsl(\$|\.localhost)\\',re.I)
PERSONAL_PATH_TEXT_SUFFIXES={'.json','.md','.txt','.py','.mjs','.js','.html','.css','.yml','.yaml','.toml','.mmd','.svg','.csv','.sha256','.gitignore'}
# The pattern's own self-test must spell out the forbidden forms with synthetic user names.
PERSONAL_PATH_PATTERN_SOURCES={'tests/test_package_personal_paths.py'}
# Frozen review records whose SHA-256 is pinned inside other evidence receipts
# (execution/evidence/REQ-*.json and review-chain records). Rewriting them would silently
# invalidate reviewer attestations, so they stay exempt until the owner re-issues those receipts.
# An exemption that no longer matches is reported so the list only shrinks.
PERSONAL_PATH_EXEMPTIONS={
    'delivery/github-art-candidates/github-art-candidates-map.json',
    'execution/reviews/W02-broadcast-source-review-008.json',
    'execution/reviews/W02-broadcast-source-review-009.json',
    'execution/reviews/W02-email-art-context-review.json',
    'execution/reviews/W02-final-art-acceptance-review.json',
    'execution/reviews/W02-marketing-concrete-copy-review.json',
    'execution/reviews/W03-github-art-candidates-followup.json',
    'execution/reviews/W03-github-art-candidates-review.json',
    'execution/reviews/W03-image-c2pa-provenance-review.json',
    'execution/reviews/W03-requirements-refresh-recommendations.json',
    'execution/reviews/W03-root-motion-browser-review.json',
    'execution/reviews/W03-root-motion-metadata-review.json',
    'execution/reviews/W03-root-motion-review.json',
    'execution/reviews/W03-root-website-art-followup.json',
    'execution/reviews/W03-root-website-art-review.json',
}
def load(path):
    return load_json(path)
def safe_relative(value):
    if not isinstance(value,str) or '\\' in value or '\x00' in value:
        return False
    p=PurePosixPath(value)
    return bool(value) and not p.is_absolute() and '..' not in p.parts and ':' not in value

def personal_path_errors(root, exemptions=None):
    """Report workstation-specific paths in package text without echoing the path itself."""
    root=Path(root)
    exemptions=PERSONAL_PATH_EXEMPTIONS if exemptions is None else set(exemptions)
    errors=[]
    seen=set()
    try: files=source_files(root)
    except ValueError as exc: return [str(exc)]
    for path in files:
        if path.suffix.casefold() not in PERSONAL_PATH_TEXT_SUFFIXES and path.suffix!='': continue
        relative=path.relative_to(root).as_posix()
        if relative in PERSONAL_PATH_PATTERN_SOURCES: continue
        try: text=path.read_text(encoding='utf-8')
        except UnicodeError: continue
        lines=[number for number,line in enumerate(text.splitlines(),1) if PERSONAL_PATH_PATTERN.search(line)]
        if not lines: continue
        seen.add(relative)
        if relative in exemptions: continue
        errors.append(f'Personal filesystem path in {relative}: line(s) {", ".join(str(n) for n in lines)}')
    for relative in sorted(set(exemptions)-seen):
        errors.append(f'Stale personal-path exemption (no longer matches, remove it): {relative}')
    return errors

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
    root_origin=ROUTES.get(ROOT_ROUTE,{}).get('origin')
    artwork_routes=[]
    for a in artwork:
        route=a.get('generation_route')
        if route is None and a.get('origin')==root_origin:
            route=ROOT_ROUTE
        if route is None:
            route=LEGACY_ROUTE
        artwork_routes.append(route)
        spec=ROUTES.get(route) if isinstance(route, str) else None
        check(spec is not None,f'Unknown art generation route: {a["id"]}')
        if spec is not None:
            check(a.get('origin')==spec.get('origin'),f'Wrong art origin for route: {a["id"]}')
        if route==ROOT_ROUTE:
            check(a.get('method')=='generate' and a.get('generation_model')=='unknown' and a.get('prompt_author_model')=='unknown',f'Wrong root art pipeline: {a["id"]}')
            if 'prompt_author_effort' in a: check(a.get('prompt_author_effort')=='unknown',f'Wrong root prompt effort: {a["id"]}')
            check(a.get('prompt_author_role_id')=='ROOT',f'Wrong root art author role: {a["id"]}')
        else:
            check(a.get('method')=='generate' and a.get('generation_model')=='gpt-image-2' and a.get('prompt_author_model')=='gpt-6-astra',f'Wrong art pipeline: {a["id"]}')
            check(a.get('prompt_author_role_id') in ART_ROLES,f'Wrong art author role: {a["id"]}')
        check(all(e['format']!='svg' for e in a['exports']),f'Native vector art promise: {a["id"]}')
    if ROOT_ROUTE in artwork_routes:
        auth_path=root/'art/root-generation-authorization.json'
        schema_path=root/'schemas/art-generation-authorization.schema.json'
        check(auth_path.is_file(),'Missing root generation authorization record.')
        check(schema_path.is_file(),'Missing root generation authorization schema.')
        if auth_path.is_file():
            auth_spec=ROUTES[ROOT_ROUTE].get('authorization',{})
            digest=auth_spec.get('sha256')
            try:
                validate_root_authorization(auth_spec.get('path'), digest)
            except (OSError, KeyError, TypeError, ValueError, UnicodeError) as exc:
                errors.append('Invalid root generation authorization: '+str(exc))
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
    errors.extend(personal_path_errors(root))
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
