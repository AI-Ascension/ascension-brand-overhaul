"""Typed errors used by the fail-closed offline publisher."""


class PublisherError(ValueError):
    """Base class for expected input or publication failures."""


class SchemaValidationError(PublisherError):
    """A record did not conform to one of the strict JSON schemas."""


class SecurityError(PublisherError):
    """A path, URL, field, or content boundary was unsafe."""


class ApprovalError(PublisherError):
    """A separately issued approval is absent, stale, or out of scope."""


class ProductionGateError(ApprovalError):
    """The record is suitable only for local rendering, not production output."""


class DuplicatePublicationError(PublisherError):
    """A publication version already exists with different content."""
