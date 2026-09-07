# Deterministic brand-content sync

`presentation_sync.py` copies only the canonical functional content allowlist
from an immutable Git commit. It uses the hardened
[`scripts/sync_content.py`](../../scripts/sync_content.py) helper, including
safe path checks, UTF-8 and SHA-256 verification, a previous-receipt check, and
atomic local writes.

A dry run is the default:

```sh
python3 tools/brand-sync/presentation_sync.py \
  --manifest github/presentation-manifest.json \
  --source-repo /path/to/ascension-brand-overhaul \
  --consumer-root /path/to/AI-Ascension.github.io
```

Use `--apply` only for a local checkout after reviewing the changed paths. The
flag writes no GitHub settings, sends no notifications, and does not publish a
branch. `--apply-settings` is intentionally refused; descriptions, topics,
pins, and visibility belong to the separate migration approval path.

The manifest's companion branch list is descriptive evidence for the isolated
branches prepared by W04. It never authorizes a push or a remote rename.
