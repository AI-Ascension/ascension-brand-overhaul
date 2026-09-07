#!/usr/bin/env python3
"""Consistency checks for declared Astra -> gpt-image-2 provenance, not runtime attestation."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
from datetime import datetime
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'art/generation-policy.json').read_text(encoding='utf-8'))
ART_ROLES = frozenset(POLICY['art_prompt_author_role_ids'])


def expected_settings(role_id: str) -> tuple[str, str]:
    """Resolve an explicitly registered role; reject unknown author identities."""
    roles = json.loads((ROOT / 'orchestration/roles.json').read_text(encoding='utf-8'))
    registered = {r['id']: r for r in roles}
    if role_id not in registered:
        raise ValueError('Unregistered role ID: ' + str(role_id))
    return ('gpt-6-astra', 'max') if role_id in ART_ROLES else ('gpt-5.6-luna', 'max')


def safe_file(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('Unsafe provenance path.')
    p = PurePosixPath(value)
    if p.is_absolute() or '..' in p.parts:
        raise ValueError('Unsafe provenance path.')
    root = root.resolve()
    target = root.joinpath(*p.parts)
    cursor = root
    for part in p.parts:
        cursor = cursor / part
        if cursor.is_symlink():
            raise ValueError('Symlink in provenance path.')
    if not target.resolve().is_relative_to(root):
        raise ValueError('Provenance path escapes root.')
    return target


def verify_hash(root: Path, path: str, digest: str, max_bytes: int = 64 * 1024 * 1024) -> bytes:
    if not isinstance(digest, str) or not re.fullmatch(r'[a-f0-9]{64}', digest):
        raise ValueError('Invalid provenance SHA-256.')
    target = safe_file(root, path)
    if not target.is_file():
        raise ValueError('Provenance must reference a regular file.')
    with target.open('rb') as handle:
        raw = handle.read(max_bytes + 1)
    if len(raw) > max_bytes:
        raise ValueError('Provenance file exceeds its size limit.')
    if hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('Provenance hash mismatch: ' + path)
    return raw


def validate_alias_evidence(record: dict, root: Path) -> None:
    """Verify bounded declared alias documentation, not provider attestation."""
    raw = verify_hash(root, record['snapshot_alias_evidence_reference'], record['snapshot_alias_evidence_sha256'], 64 * 1024)
    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError('Duplicate alias-evidence key.')
            value[key] = item
        return value
    value = json.loads(raw, object_pairs_hook=unique)
    required = {'schema_version', 'requested_model', 'resolved_model', 'source_reference', 'captured_at', 'reviewer_reference'}
    if not isinstance(value, dict) or set(value) != required or not all(isinstance(item, str) and item.strip() for item in value.values()):
        raise ValueError('Invalid image-model alias evidence envelope.')
    if value['schema_version'] != 'image-model-alias-v1' or value['requested_model'] != 'gpt-image-2' or value['resolved_model'] != record['image_model_observed']:
        raise ValueError('Alias documentation does not identify the requested and resolved model.')
    source = urlsplit(value['source_reference'])
    if source.scheme != 'https' or source.hostname not in {'openai.com', 'platform.openai.com', 'developers.openai.com', 'help.openai.com'} or source.username or source.password:
        raise ValueError('Alias documentation needs an official HTTPS source reference.')
    if datetime.fromisoformat(value['captured_at'].replace('Z', '+00:00')).tzinfo is None:
        raise ValueError('Alias capture timestamp needs a timezone.')


def validate_generation_record(record: dict, planned: dict, root: Path, ledger: dict | None) -> list[str]:
    """Validate actual file/hash references and declared models. Inspect native logs separately."""
    errors = []
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)
    check(record.get('status') == 'verified', 'Generation job is not verified.')
    check(record.get('test_fixture') is False, 'Test/unclassified generation provenance cannot be released.')
    check(record.get('asset_id') == planned['id'], 'Generation asset ID mismatch.')
    check(record.get('author_role_id') == planned['prompt_author_role_id'], 'Wrong Astra author role for asset.')
    check(record.get('author_role_id') in ART_ROLES, 'Art prompt author is not a designated Astra leaf.')
    check(record.get('author_depth') == 3, 'Art author must be a depth-3 leaf.')
    for phase in ('requested', 'accepted', 'observed'):
        check(record.get(phase + '_author_model') == 'gpt-6-astra', 'Missing/wrong ' + phase + ' Astra author model.')
        check(record.get(phase + '_author_effort') == 'max', 'Missing/wrong ' + phase + ' Astra author effort.')
    check(record.get('image_model_requested') == 'gpt-image-2', 'Artwork must request exactly gpt-image-2.')
    observed = record.get('image_model_observed')
    check(observed in POLICY['accepted_resolved_image_model_ids'], 'Unverified or prohibited image backend.')
    if observed != 'gpt-image-2':
        try:
            validate_alias_evidence(record, root)
        except (OSError, KeyError, ValueError, TypeError, UnicodeError) as exc:
            errors.append('Dated image model alias evidence: ' + str(exc))
    for field in ('record_id', 'author_agent_id', 'author_parent_id', 'author_runtime_evidence_reference',
                  'image_model_evidence_reference', 'tool_name', 'tool_execution_reference', 'reviewer_reference', 'created_at'):
        check(bool(record.get(field)), 'Missing generation provenance: ' + field)
    check(record.get('reviewer_reference') != record.get('author_agent_id'), 'Author cannot independently review their own art.')
    try:
        raw = verify_hash(root, record['prompt_path'], record['prompt_sha256'], 1024 * 1024)
        check(bool(raw.decode('utf-8').strip()), 'Astra prompt is empty.')
        if record.get('provider_revised_prompt_path'):
            verify_hash(root, record['provider_revised_prompt_path'], record['provider_revised_prompt_sha256'])
            check(bool(record.get('revised_prompt_astra_review_reference')), 'Tool-revised prompt needs Astra review evidence.')
        outputs = record.get('raw_outputs', [])
        check(bool(outputs), 'No original generated output.')
        check(len({o['path'] for o in outputs}) == len(outputs), 'Duplicate raw output path.')
        for output in outputs:
            verify_hash(root, output['path'], output['sha256'])
            check(output.get('format') in ('png', 'webp', 'jpeg', 'jpg'), 'Original generated output must be a supported raster, not SVG/video.')
            check(isinstance(output.get('width'), int) and not isinstance(output.get('width'), bool) and output['width'] > 0,
                  'Invalid raw output width.')
            check(isinstance(output.get('height'), int) and not isinstance(output.get('height'), bool) and output['height'] > 0,
                  'Invalid raw output height.')
    except (OSError, KeyError, ValueError, TypeError, UnicodeError) as exc:
        errors.append(str(exc))
    if ledger is None:
        errors.append('Native agent ledger is required for artwork acceptance.')
    else:
        node = next((n for n in ledger.get('agents', []) if n.get('id') == record.get('author_agent_id')), None)
        check(node is not None, 'Astra author not found in native ledger.')
        if node:
            check(node.get('role_id') == record.get('author_role_id'), 'Native author role mismatch.')
            check(node.get('parent_id') == record.get('author_parent_id'), 'Native author parent mismatch.')
            check(node.get('depth') == 3, 'Native author ancestry mismatch.')
            check(node.get('model_verified') is True, 'Native Astra identity is not verified.')
            for phase in ('requested', 'accepted', 'observed'):
                check(node.get(phase + '_model') == 'gpt-6-astra' and node.get(phase + '_effort') == 'max',
                      'Native author settings mismatch: ' + phase)
            check(bool(node.get('runtime_evidence_reference')), 'Missing native identity evidence.')
    return errors
