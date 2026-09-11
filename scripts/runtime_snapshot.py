#!/usr/bin/env python3
"""Read installed Codex metadata for one actual thread tree; never read transcripts.

This is observation, not a spawn hook or a claim of provider-side attestation.
Write its output to ignored private execution storage.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3


def snapshot(database, root_id):
    connection = sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = connection.execute(
            'SELECT id, source, model, reasoning_effort, agent_path, cli_version, '
            'created_at_ms FROM threads'
        ).fetchall()
    finally:
        connection.close()
    records = {}
    for row in rows:
        record = dict(row)
        if not isinstance(record['id'], str) or not record['id'] or record['id'] in records:
            raise ValueError('Invalid or duplicate native thread ID.')
        record.pop('agent_path')
        record['agent_path_redacted'] = True
        try:
            source = json.loads(record.pop('source'))
        except (ValueError, TypeError):
            source = {}
        subagent = source.get('subagent') if isinstance(source, dict) else None
        spawn = subagent.get('thread_spawn') if isinstance(subagent, dict) else None
        if not isinstance(spawn, dict):
            spawn = {}
        record['parent_id'] = spawn.get('parent_thread_id')
        record['depth'] = spawn.get('depth')
        records[record['id']] = record
    if root_id not in records:
        raise ValueError('Requested root thread is absent from installed metadata.')
    if records[root_id]['parent_id'] is not None or records[root_id]['depth'] not in (None, 0):
        raise ValueError('Requested root is not an observed native root.')
    records[root_id]['depth'] = 0
    selected = {root_id}
    while True:
        children = {key for key, row in records.items() if row['parent_id'] in selected}
        expanded = selected | children
        if expanded == selected:
            break
        selected = expanded
    pending = selected - {root_id}
    depths = {root_id: 0}
    while pending:
        ready = {key for key in pending if records[key]['parent_id'] in depths}
        if not ready:
            raise ValueError('Native ancestry contains a cycle or missing parent.')
        for key in ready:
            expected = depths[records[key]['parent_id']] + 1
            declared = records[key]['depth']
            if not isinstance(declared, int) or isinstance(declared, bool) or declared != expected:
                raise ValueError('Declared native depth disagrees with observed ancestry.')
            depths[key] = expected
        pending -= ready
    return {
        'observed_at': datetime.now(timezone.utc).isoformat(),
        'root_id': root_id,
        'evidence_kind': 'installed_client_thread_metadata',
        'limitations': [
            'Client metadata does not independently attest a provider execution.',
            'Thread existence does not establish current liveness or closure.',
            'Requested settings and native spawn receipts must be recorded separately.',
            'Agent filesystem paths are redacted; ancestry is checked from parent IDs.',
        ],
        'threads': sorted((records[key] for key in selected), key=lambda row: (row['created_at_ms'] or 0, row['id'])),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--root-id', required=True)
    args = parser.parse_args()
    try:
        result = snapshot(args.database, args.root_id)
    except (OSError, sqlite3.Error, ValueError) as error:
        parser.exit(1, f'Runtime observation failed: {error}\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
