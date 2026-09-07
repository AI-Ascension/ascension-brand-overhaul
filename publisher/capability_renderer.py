"""Safe local previews and approval-gated capability publication."""
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
from datetime import date, datetime, timezone
from pathlib import Path

from .authority import require_registered_approval
from .canonical import canonical_json
from .capabilities import load_capability_registry, render_capabilities
from .errors import ApprovalError, PublisherError
from .publisher import _read_json
from .schema import validate_instance
from .security import ensure_separate_output, reject_symlink_path, safe_public_url
from .validate import _parse_datetime


def render_registry(records_path: Path, output: Path, *, approval_path: Path | None = None, now: datetime | None = None) -> Path:
    """Write a new file atomically; never overwrite or write into source trees."""
    reject_symlink_path(output)
    ensure_separate_output(records_path.parent, output.parent)
    if approval_path is not None:
        ensure_separate_output(approval_path.parent, output.parent)
    if output.exists():
        raise PublisherError('capability output already exists')
    records, metadata = load_capability_registry(records_path)
    if approval_path is None:
        page = render_capabilities(records).replace('<main>', '<main><p role="note">Local preview only. Not approved for publication.</p>', 1)
    else:
        approval = _read_json(approval_path)
        validate_instance(approval, 'capability-approval.schema.json')
        digest = hashlib.sha256(canonical_json({'records': records, 'metadata': metadata})).hexdigest()
        if approval['source_digest'] != digest:
            raise ApprovalError('capability approval does not match the registry')
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        if approval['revoked'] or _parse_datetime(approval['approved_at'], 'approved_at') > current:
            raise ApprovalError('capability approval is revoked or not yet valid')
        if approval['expires_at'] is not None and _parse_datetime(approval['expires_at'], 'expires_at') <= current:
            raise ApprovalError('capability approval has expired')
        for record in records:
            if record['review_status'] != 'approved' or not record.get('last_reviewed_at'):
                raise ApprovalError('public capability records require dated review')
            reviewed_text = record['last_reviewed_at']
            reviewed = date.fromisoformat(reviewed_text) if len(reviewed_text) == 10 else _parse_datetime(reviewed_text, 'last_reviewed_at').date()
            if reviewed > current.date():
                raise ApprovalError('capability review is dated in the future')
            if record['source_url'] not in approval['approved_public_uris']:
                raise ApprovalError('capability source URL is not approved')
        for uri in approval['approved_public_uris']:
            safe_public_url(uri)
        require_registered_approval(approval)
        page = render_capabilities(records)
    output.parent.mkdir(parents=True, exist_ok=True)
    reject_symlink_path(output)
    descriptor, temporary = tempfile.mkstemp(prefix='.capability-', dir=output.parent)
    staging = Path(temporary)
    try:
        with os.fdopen(descriptor, 'wb') as handle:
            handle.write(page.encode('utf-8'))
            handle.flush()
            os.fsync(handle.fileno())
        # An exclusive hard-link install cannot replace a file that appeared
        # while rendering. Source and destination are on the same filesystem.
        os.link(staging, output)
    finally:
        staging.unlink(missing_ok=True)
    return output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Render a local capability preview or enrolled public registry')
    parser.add_argument('records', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--approval', type=Path, help='Operator-enrolled capability approval; omitted means local preview only')
    args = parser.parse_args(argv)
    try:
        render_registry(args.records, args.output, approval_path=args.approval)
    except (PublisherError, OSError, ValueError) as exc:
        parser.exit(2, f'ERROR: {exc}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
