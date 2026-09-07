#!/usr/bin/env python3
"""Validate recorded native ancestry. This does not enforce native spawn permissions."""
import argparse, json
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from art_policy import expected_settings

def stamp(value):
    t=datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None: raise ValueError('Timestamp must include a timezone.')
    return t

def validate_ledger(data):
    root=data['root_id']; budget=data['budget']; nodes=data['agents']
    if not isinstance(budget,int) or isinstance(budget,bool) or not 1<=budget<=12:
        raise ValueError('Project descendant budget must be 1–12.')
    catalog={r['id']:r for r in json.loads((Path(__file__).resolve().parents[1]/'orchestration/roles.json').read_text())}
    mapping={n['id']:n for n in nodes}
    if len(mapping)!=len(nodes) or root in mapping: raise ValueError('Duplicate or root-colliding native IDs.')
    events=[]
    for n in nodes:
        d=n['depth']; parent=n['parent_id']
        if not isinstance(d,int) or isinstance(d,bool) or not 1<=d<=3: raise ValueError('Depth must be 1–3; no fourth descendant level.')
        MODEL,EFFORT=expected_settings(n['role_id'])
        role=catalog[n['role_id']]
        if role['depth']!=d: raise ValueError('Role depth differs from native depth.')
        if (n['requested_model'],n['requested_effort'])!=(MODEL,EFFORT): raise ValueError('Role-specific descendant model/effort request mismatch.')
        opened=stamp(n['opened_at']); closed=stamp(n['closed_at']) if n.get('closed_at') else None
        if closed and closed<=opened: raise ValueError('Close timestamp must follow opening.')
        if parent==root:
            if d!=1: raise ValueError('Only depth-1 leads have root as parent.')
        else:
            p=mapping.get(parent)
            if not p or p['depth']!=d-1: raise ValueError('Invalid native parent or depth.')
            if p['role_id']!=role['parent']: raise ValueError('Native parent role differs from registered role ancestry.')
            po=stamp(p['opened_at']); pc=stamp(p['closed_at']) if p.get('closed_at') else None
            if opened<po or (pc and opened>=pc): raise ValueError('Child opened outside parent lifetime.')
            if pc and (closed is None or closed>pc): raise ValueError('Parent closed while child remained open.')
        if not isinstance(n.get('model_verified', False), bool):
            raise ValueError('model_verified must be a boolean, not a truthy value.')
        if n.get('model_verified') is True:
            if (n.get('accepted_model'),n.get('accepted_effort'),n.get('observed_model'),n.get('observed_effort'))!=(MODEL,EFFORT,MODEL,EFFORT):
                raise ValueError('Verified flag contradicts accepted/observed settings.')
            if not n.get('runtime_evidence_reference'): raise ValueError('Verified settings need runtime evidence, not self-report.')
        events.append((opened,1))
        if closed: events.append((closed,-1))
    active=peak=0
    for _,delta in sorted(events,key=lambda x:(x[0],x[1])):
        active+=delta; peak=max(peak,active)
    if peak>budget: raise ValueError(f'Peak {peak} exceeds global project budget {budget}.')
    return {'recorded_descendants':len(nodes),'peak_open_descendants':peak,'currently_open_descendants':active,'has_depth_three_chain':any(n['depth']==3 for n in nodes),'astra_author_nodes':sum(n.get('requested_model')=='gpt-6-astra' for n in nodes),'all_models_verified':bool(nodes) and all(n.get('model_verified') is True for n in nodes)}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('ledger',type=Path); args=parser.parse_args()
    try: result=validate_ledger(json.loads(args.ledger.read_text()))
    except (OSError,ValueError,KeyError,TypeError) as exc: parser.exit(1,f'Ledger rejected: {exc}\n')
    print(json.dumps(result,indent=2)); print('A valid recorded ledger is not proof that these native calls occurred; inspect evidence references.')
if __name__=='__main__': main()
