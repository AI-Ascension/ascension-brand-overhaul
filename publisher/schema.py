"""Strict local JSON-schema validation with no network resolver."""

from __future__ import annotations

import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from typing import Any

from .errors import SchemaValidationError

try:
    import jsonschema
    from jsonschema import Draft202012Validator, FormatChecker, RefResolver
except ImportError as exc:  # pragma: no cover - exercised only in bare installs
    raise RuntimeError(
        "The offline publisher requires the local 'jsonschema' package; no network fallback is used."
    ) from exc


SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"
_FORMAT_CHECKER = FormatChecker()


def unique_schema_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise SchemaValidationError('Schema contains duplicate object key: ' + key)
        result[key] = value
    return result


@lru_cache(maxsize=None)
def load_schema(filename: str) -> dict[str, Any]:
    raw_path = SCHEMA_ROOT / filename
    if raw_path.is_symlink():
        raise SchemaValidationError(f"schema is outside the checked-in schema root: {filename}")
    path = raw_path.resolve()
    if path.parent != SCHEMA_ROOT.resolve() or not path.is_file():
        raise SchemaValidationError(f"schema is outside the checked-in schema root: {filename}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_schema_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise SchemaValidationError(f"cannot read schema {filename}: {exc}") from exc
    if not isinstance(value, dict):
        raise SchemaValidationError(f"schema {filename} must be an object")
    return value


def _validator(filename: str) -> Draft202012Validator:
    schema = load_schema(filename)
    # The publication boundary must never resolve a remote $ref.  All
    # references used by the shipped schemas are local or internal.
    resolver = RefResolver(base_uri=SCHEMA_ROOT.as_uri() + "/", referrer=schema)
    validator = Draft202012Validator(schema, resolver=resolver, format_checker=_FORMAT_CHECKER)
    validator.check_schema(schema)
    return validator


def validate_instance(instance: Any, filename: str) -> Any:
    """Validate an instance and raise one deterministic, useful error."""

    errors = sorted(_validator(filename).iter_errors(instance), key=lambda error: list(error.path))
    if errors:
        error = errors[0]
        location = ".".join(str(item) for item in error.path) or "$"
        raise SchemaValidationError(f"{filename} at {location}: {error.message}")
    return instance


def validate_manifest_schema(manifest: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(manifest, "publication-manifest.schema.json")


def validate_approval_schema(approval: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(approval, "publication-approval.schema.json")


def validate_action_schema(action: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(action, "action-record.schema.json")


def validate_timeline_schema(timeline: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(timeline, "action-timeline.schema.json")


def validate_event_schema(event: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(event, "event.schema.json")


def validate_event_contract_schema(contract: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(contract, "event-contract.schema.json")


def validate_comparison_schema(comparison: dict[str, Any]) -> dict[str, Any]:
    return validate_instance(comparison, "comparison.schema.json")


def validate_capability_schema(capability: dict[str, Any]) -> dict[str, Any]:
    # capability.schema.json is an existing public interface and is kept
    # unchanged; this wrapper makes its strict validation reusable.
    return validate_instance(capability, "capability.schema.json")


def validate_public_projection(projection: dict[str, Any]) -> dict[str, Any]:
    """Strict manifest shape with optional private-side source identities.

    Derive from the input contract so field types and unknown-field rejection
    cannot drift. Only the documented private source identities are optional.
    """
    schema = deepcopy(load_schema("publication-manifest.schema.json"))
    schema["$defs"]["source"]["required"] = ["references"]
    schema["$defs"]["source_reference"]["required"] = ["label", "uri"]
    validator = Draft202012Validator(schema, format_checker=_FORMAT_CHECKER)
    errors = sorted(validator.iter_errors(projection), key=lambda error: str(list(error.path)))
    if errors:
        raise SchemaValidationError("invalid public projection: " + errors[0].message)
    return projection
