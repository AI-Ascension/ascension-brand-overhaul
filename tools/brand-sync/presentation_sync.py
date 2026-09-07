#!/usr/bin/env python3
"""Apply an allowlisted canonical brand-content manifest to one local checkout.

This is a local source synchronizer.  It defaults to a dry run, reads the
canonical files from an immutable Git revision, preserves unrelated consumer
edits, and writes no GitHub settings.  Remote repository presentation is
handled by the migration plan and requires separate operator approval.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SYNC_PATH = ROOT / "scripts" / "sync_content.py"
spec = importlib.util.spec_from_file_location("canonical_content_sync", SYNC_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("canonical sync helper is unavailable")
content_sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content_sync)


SCHEMA_VERSION = "ai-ascension.presentation-manifest.v1"


def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read manifest: {exc}") from exc


def validate(manifest, source_repo: Path):
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported presentation manifest schema")
    canonical = manifest.get("canonical_source")
    if not isinstance(canonical, dict):
        raise ValueError("manifest has no canonical_source")
    revision = canonical.get("revision")
    files = canonical.get("files")
    if not isinstance(revision, str) or len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ValueError("canonical revision must be a full lowercase Git commit")
    if not isinstance(files, list) or not files:
        raise ValueError("canonical source files are required")
    plan = {
        "schema_version": "brand-content-sync-v1",
        "source_revision": revision,
        "files": files,
    }
    # Delegate path, object, UTF-8, digest, and previous-receipt checks to the
    # existing hardened helper.  A dry run still performs all validation.
    if not source_repo.is_dir():
        raise ValueError("source repository must be an existing directory")
    return plan


def run(manifest_path: Path, source_repo: Path, consumer_root: Path, apply: bool):
    manifest = load(manifest_path)
    plan = validate(manifest, source_repo)
    result = content_sync.sync(source_repo, consumer_root, plan, apply=apply)
    return {
        "schema_version": SCHEMA_VERSION,
        "mode": "apply" if apply else "dry_run",
        "manifest": str(manifest_path),
        "canonical_revision": plan["source_revision"],
        "consumer_root": str(consumer_root),
        "changed_files": result["changed_files"],
        "receipt": result["receipt"],
        "github_settings_changed": False,
    }


def parser():
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--manifest", type=Path, required=True)
    root.add_argument("--source-repo", type=Path, required=True)
    root.add_argument("--consumer-root", type=Path, required=True)
    root.add_argument("--apply", action="store_true", help="write local files; never writes remote settings")
    root.add_argument("--apply-settings", action="store_true", help=argparse.SUPPRESS)
    return root


def main(argv=None):
    args = parser().parse_args(argv)
    if args.apply_settings:
        print("brand sync refused: GitHub settings require the migration approval path", file=sys.stderr)
        return 1
    try:
        result = run(args.manifest, args.source_repo, args.consumer_root, args.apply)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"brand sync refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

