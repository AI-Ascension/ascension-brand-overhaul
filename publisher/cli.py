"""Small offline CLI; all commands are local file operations."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .errors import PublisherError
from .publisher import OfflinePublisher
from .validate import validate_manifest


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate and render AI Ascension public run records offline")
    sub = parser.add_subparsers(dest="command", required=True)
    verify = sub.add_parser("verify", help="validate a sanitized manifest without writing")
    verify.add_argument("manifest", type=Path)
    render = sub.add_parser("render", help="render a local page; synthetic fixtures remain local-only")
    render.add_argument("manifest", type=Path)
    render.add_argument("output", type=Path)
    render.add_argument("--artifact-root", type=Path)
    publish = sub.add_parser("publish", help="publish a current approved manifest to local output")
    publish.add_argument("manifest", type=Path)
    publish.add_argument("approval", type=Path)
    publish.add_argument("output", type=Path)
    publish.add_argument("--artifact-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    publisher = OfflinePublisher()
    try:
        if args.command == "verify":
            manifest = publisher.ingest(args.manifest)
            print(json.dumps({"status": "valid", "public_run_id": manifest["public_run_id"], "source_digest": manifest["source"]["content_digest"]}, sort_keys=True))
        elif args.command == "render":
            result = publisher.render(args.manifest, args.output, artifact_root=args.artifact_root)
            print(json.dumps({"status": "rendered", "output": str(result.output_directory), "idempotent": result.idempotent}, sort_keys=True))
        else:
            result = publisher.publish(args.manifest, args.approval, args.output, artifact_root=args.artifact_root)
            print(json.dumps({"status": "published", "output": str(result.output_directory), "idempotent": result.idempotent}, sort_keys=True))
        return 0
    except (PublisherError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


__all__ = ["main"]
