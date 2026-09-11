"""Bounded validation of referenced, preapproved raster artwork inputs."""
from __future__ import annotations

import hashlib
import io
import warnings
from pathlib import Path

from PIL import Image, UnidentifiedImageError

from .errors import ApprovalError

MAX_ARTIFACT_BYTES = 16 * 1024 * 1024
MAX_ARTIFACT_PIXELS = 25_000_000
MEDIA = {'image/png': ('PNG', {'.png'}), 'image/jpeg': ('JPEG', {'.jpg', '.jpeg'}), 'image/webp': ('WEBP', {'.webp'})}
ENCODING_INFO = {'transparency', 'jfif', 'jfif_version', 'jfif_unit', 'jfif_density'}


def verify_raster_asset(path: Path, asset: dict) -> None:
    expected_format, extensions = MEDIA[asset['mime_type']]
    if path.suffix.lower() not in extensions:
        raise ApprovalError('artifact extension does not match its approved MIME type')
    with path.open('rb') as handle:
        raw = handle.read(MAX_ARTIFACT_BYTES + 1)
    if len(raw) > MAX_ARTIFACT_BYTES or len(raw) != asset['byte_size']:
        raise ApprovalError('artifact byte size differs from approval or exceeds the limit')
    if hashlib.sha256(raw).hexdigest() != asset['artifact_digest']:
        raise ApprovalError('decision card file digest does not match the approval')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(raw), formats=['PNG', 'JPEG', 'WEBP']) as decoded:
                if decoded.format != expected_format:
                    raise ApprovalError('artifact bytes do not match approved MIME type')
                width, height = decoded.size
                if width < 1 or height < 1 or width * height > MAX_ARTIFACT_PIXELS or max(width, height) > 16384:
                    raise ApprovalError('artifact pixel dimensions exceed the limit')
                if getattr(decoded, 'is_animated', False):
                    raise ApprovalError('decision card must be a static raster')
                if set(decoded.info) - ENCODING_INFO:
                    raise ApprovalError('artifact contains metadata requiring source-owner sanitization')
                decoded.verify()
            with Image.open(io.BytesIO(raw), formats=[expected_format]) as decoded:
                decoded.load()
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise ApprovalError('artifact is not a supported bounded raster image') from exc
    if expected_format == 'PNG' and not raw.endswith(b'\x00\x00\x00\x00IEND\xaeB`\x82'):
        raise ApprovalError('PNG contains trailing data or lacks its final chunk')
    if expected_format == 'JPEG' and not raw.endswith(b'\xff\xd9'):
        raise ApprovalError('JPEG contains trailing data or lacks its final marker')
    if expected_format == 'WEBP' and (raw[:4] != b'RIFF' or int.from_bytes(raw[4:8], 'little') + 8 != len(raw)):
        raise ApprovalError('WebP container length is invalid')
