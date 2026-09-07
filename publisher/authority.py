"""Operator-controlled approval registry; never selected by content input."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from .canonical import canonical_json
from .errors import ApprovalError
from .schema import unique_schema_object
from .security import reject_symlink_path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / 'config' / 'publication-authorities.json'


def renderer_digest() -> str:
    """Pin all local publisher code, schemas and canonical token bytes."""
    paths = sorted([*ROOT.joinpath('publisher').glob('*.py'), *ROOT.joinpath('schemas').glob('*.json'), ROOT / 'brand/tokens.css'])
    identities = {}
    for path in paths:
        reject_symlink_path(path)
        identities[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashlib.sha256(canonical_json(identities)).hexdigest()


def require_registered_approval(approval: dict) -> None:
    """Match exact approval bytes to the deployment's trusted registry.

    The deployment owner must protect the installed code and registry. This
    does not defend against someone who can replace the publisher itself.
    No input file, command option or environment variable selects a registry.
    """
    reject_symlink_path(REGISTRY_PATH)
    try:
        with REGISTRY_PATH.open("rb") as handle:
            raw = handle.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ApprovalError('approval registry exceeds size limit')
        registry = json.loads(raw, object_pairs_hook=unique_schema_object)
    except (OSError, ValueError) as exc:
        raise ApprovalError('trusted approval registry is unavailable or invalid') from exc
    if not isinstance(registry, dict) or set(registry) != {'schema_version', 'approvals'} or registry['schema_version'] != 'publication-authorities-v1' or not isinstance(registry['approvals'], list):
        raise ApprovalError('invalid trusted approval registry')
    ids = set()
    for record in registry['approvals']:
        if not isinstance(record, dict) or set(record) != {'approval_id', 'authority_reference', 'approval_digest'} or not all(isinstance(value, str) for value in record.values()):
            raise ApprovalError('invalid trusted approval registry entry')
        if not re.fullmatch(r'[a-f0-9]{64}', record['approval_digest']) or not record['authority_reference'] or len(record['authority_reference']) > 300:
            raise ApprovalError('invalid trusted approval identity')
        if record['approval_id'] in ids:
            raise ApprovalError('duplicate approval ID in trusted registry')
        ids.add(record['approval_id'])
    expected = {'approval_id': approval['approval_id'], 'authority_reference': approval['authority_reference'], 'approval_digest': hashlib.sha256(canonical_json(approval)).hexdigest()}
    if expected not in registry['approvals']:
        raise ApprovalError('approval is not enrolled in the trusted deployment registry')
    if approval['renderer_digest'] != renderer_digest():
        raise ApprovalError('approval renderer or token revision is stale')
