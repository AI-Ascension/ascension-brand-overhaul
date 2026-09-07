"""Compatibility import path for capability registry consumers."""

from .capabilities import (
    load_capability_registry,
    render_capabilities,
    validate_capability,
    validate_capabilities,
)

__all__ = ["load_capability_registry", "render_capabilities", "validate_capability", "validate_capabilities"]
