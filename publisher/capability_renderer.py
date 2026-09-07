"""CLI for deterministic capability registry rendering."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .capabilities import load_capability_registry, render_capabilities


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render capability records without network access")
    parser.add_argument("records", type=Path, help="JSON array of capability records")
    parser.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    records, _metadata = load_capability_registry(args.records)
    args.output.write_text(render_capabilities(records), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
