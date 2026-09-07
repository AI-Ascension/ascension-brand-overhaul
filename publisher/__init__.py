"""Offline, approval-aware publication and measurement helpers.

The package deliberately has no provider, HTTP, game-control, or host-runtime
integration.  It accepts sanitized records and writes deterministic local
artifacts only.
"""

from .canonical import attach_source_digest, canonical_json, source_digest
from .errors import (
    ApprovalError,
    DuplicatePublicationError,
    ProductionGateError,
    PublisherError,
    SchemaValidationError,
    SecurityError,
)
from .publisher import OfflinePublisher, PublicationResult, Publisher, publish, render, verify

__all__ = [
    "OfflinePublisher",
    "Publisher",
    "PublicationResult",
    "publish",
    "render",
    "verify",
    "PublisherError",
    "ApprovalError",
    "ProductionGateError",
    "SchemaValidationError",
    "SecurityError",
    "DuplicatePublicationError",
    "canonical_json",
    "source_digest",
    "attach_source_digest",
]
