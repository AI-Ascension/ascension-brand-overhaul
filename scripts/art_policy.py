#!/usr/bin/env python3
"""Consistency checks for declared artwork provenance, not runtime attestation."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import re
from datetime import date, datetime
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
POLICY = json.loads((ROOT / 'art/generation-policy.json').read_text(encoding='utf-8'))
ART_ROLES = frozenset(POLICY['art_prompt_author_role_ids'])
LEGACY_ROUTE = 'astra_gpt_image_2'
ROOT_ROUTE = 'user_authorized_root_image_tool'
ROUTES = POLICY.get('generation_routes', {})
ROOT_ROUTE_SPEC = ROUTES.get(ROOT_ROUTE, {})
ROOT_AUTHORIZATION = ROOT_ROUTE_SPEC.get('authorization', {})
ROOT_AUTHORIZATION_PATH = 'art/root-generation-authorization.json'
ROOT_AUTHORIZATION_ID = 'root-image-tool-route-20260907'
ROOT_AUTHORIZATION_SHA256 = '230445ea910b47ae3f45af282a58f119872738e6659faa0761ea8065c7b6d9de'


def _unique(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate authorization key.')
        value[key] = item
    return value


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


def validate_root_authorization(reference: str, digest: str) -> None:
    """Verify the one recorded user override; a self-authored substitute is not enough."""
    if reference != ROOT_AUTHORIZATION_PATH:
        raise ValueError('Root image generation needs the canonical user authorization reference.')
    if ROOT_AUTHORIZATION.get('path') != ROOT_AUTHORIZATION_PATH or ROOT_AUTHORIZATION.get('authorization_id') != ROOT_AUTHORIZATION_ID:
        raise ValueError('Root image generation policy does not identify the canonical authorization record.')
    if ROOT_AUTHORIZATION.get('sha256') != ROOT_AUTHORIZATION_SHA256 or digest != ROOT_AUTHORIZATION_SHA256:
        raise ValueError('Root image generation authorization hash does not match policy.')
    raw = verify_hash(ROOT, reference, digest, 64 * 1024)
    value = json.loads(raw, object_pairs_hook=_unique)
    expected = {
        'schema_version': 'ai-ascension.root-generation-authorization.v1',
        'authorization_id': ROOT_AUTHORIZATION_ID,
        'authorized_by': 'user',
        'authorization_text': 'you can of course generate them images instead.',
        'scope': 'all_requested_new_artwork',
        'author_role_id': 'ROOT',
        'tool_name': 'image_gen__imagegen',
        'image_model_policy': 'unknown_unless_observed',
        'backend_policy': 'unspecified',
        'native_agent_attestation': False,
        'independent_design_review_required': True,
        'exact_prompt_and_output_hashes_required': True,
        'evidence_media_generation_prohibited': True,
    }
    if not isinstance(value, dict) or set(value) != set(expected) | {'authorized_at'}:
        raise ValueError('Invalid root image generation authorization envelope.')
    if any(value.get(key) != item for key, item in expected.items()):
        raise ValueError('Root image generation authorization does not match the recorded user override.')
    try:
        captured = date.fromisoformat(value['authorized_at'])
    except (AttributeError, TypeError, ValueError) as exc:
        raise ValueError('Root authorization date is invalid.') from exc
    if captured.isoformat() != value['authorized_at']:
        raise ValueError('Root authorization date must be an ISO date.')


def validate_generation_record(record: dict, planned: dict, root: Path, ledger: dict | None) -> list[str]:
    """Validate actual file/hash references and route-specific declarations."""
    errors = []
    def check(ok: bool, message: str) -> None:
        if not ok:
            errors.append(message)
    route = record.get('generation_route', LEGACY_ROUTE)
    known_route = isinstance(route, str) and route in {LEGACY_ROUTE, ROOT_ROUTE}
    check(known_route, 'Unknown artwork generation route.')
    if 'generation_route' in planned:
        check(planned.get('generation_route') == route, 'Generation route does not match the planned asset.')
    check(record.get('status') == 'verified', 'Generation job is not verified.')
    check(record.get('test_fixture') is False, 'Test/unclassified generation provenance cannot be released.')
    check(record.get('asset_id') == planned['id'], 'Generation asset ID mismatch.')
    if route == LEGACY_ROUTE:
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
    elif route == ROOT_ROUTE:
        check(record.get('author_role_id') == 'ROOT', 'Root route requires author role ROOT.')
        check(record.get('author_agent_id') == 'root', 'Root route requires the root author ID.')
        check('author_parent_id' in record and record.get('author_parent_id') is None,
              'Root route requires an explicit null parent agent.')
        check(record.get('author_depth') == 0, 'Root route author depth must be zero.')
        for phase in ('requested', 'accepted', 'observed'):
            check(record.get(phase + '_author_model') == 'unknown', 'Root author model must remain unknown unless observed.')
            check(record.get(phase + '_author_effort') == 'unknown', 'Root author effort must remain unknown unless observed.')
        check(record.get('image_model_requested') == 'unknown', 'Root route cannot claim a requested image model.')
        check(record.get('image_model_observed') == 'unknown', 'Root route cannot claim an observed image model without a policy update.')
        check(record.get('image_backend') == 'unspecified', 'Root route backend must remain unspecified.')
        check(record.get('tool_name') == 'image_gen__imagegen', 'Root route must identify image_gen__imagegen.')
        try:
            validate_root_authorization(record['user_authorization_reference'], record['user_authorization_sha256'])
        except (OSError, KeyError, ValueError, TypeError, UnicodeError) as exc:
            errors.append('User-authorized root route: ' + str(exc))
    for field in ('record_id', 'author_agent_id', 'author_parent_id', 'author_runtime_evidence_reference',
                  'image_model_evidence_reference', 'tool_name', 'tool_execution_reference', 'reviewer_reference', 'created_at'):
        if field == 'author_parent_id' and route == ROOT_ROUTE:
            continue
        check(bool(record.get(field)), 'Missing generation provenance: ' + field)
    check(record.get('reviewer_reference') != record.get('author_agent_id'), 'Author cannot independently review their own art.')
    try:
        raw = verify_hash(root, record['prompt_path'], record['prompt_sha256'], 1024 * 1024)
        check(bool(raw.decode('utf-8').strip()), 'Astra prompt is empty.')
        if record.get('provider_revised_prompt_path'):
            verify_hash(root, record['provider_revised_prompt_path'], record['provider_revised_prompt_sha256'])
            check(bool(record.get('revised_prompt_astra_review_reference')), 'Tool-revised prompt needs Astra review evidence.')
        for reference in record.get('reference_inputs', []):
            verify_hash(root, reference['reference'], reference['sha256'])
            rights = reference.get('rights_reference')
            check(isinstance(rights, str) and bool(rights.strip()) and not rights.startswith('pending:'),
                  'Reference input needs a completed source-use review.')
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
    if route == ROOT_ROUTE:
        # Root authorship is explicitly user-authorized and has no fabricated native child record.
        return errors
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
