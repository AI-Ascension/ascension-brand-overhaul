# Package tooling standards

This repository is an execution-specification package with real Python 3.10+
standard-library validation/archive helpers, JSON schemas and an offline HTML
asset board. It is not a Rust product workspace and is not documentation-only.
Preserve its existing Python boundary; the Rust-only rule of sibling runtime
repositories does not apply here. AGENTS.md and orchestration/CONTRACT.md retain
local ownership, art-provenance and evidence requirements. This standards task
does not execute the brand implementation assignment or authorize artwork,
publication, repository renames or remote writes.

This repository is explicitly excluded from bundle adoption in AI-Ascension/.github
standards/repositories.yaml while its historical checksum boundary is unresolved.
No local profile/lock or Rust checker is installed. Preserve exact
schema IDs, generation metadata and historical source pins. Do not run formatters
over MANIFEST.json, CHECKSUMS.sha256 or archived package bytes. Existing checks:

```bash
python3 scripts/validate_package.py
python3 -m unittest discover -s tests -v
git diff --check
```

These are package/helper checks, not proof of native agent execution, delivered
art, deployment or product validation. Ordinary checks make no model calls and
need no credentials or sibling checkout. Dependency and generated-output trees
remain excluded from deliverable source.

At default commit 5a2acfd6690d2533af046a7afcf3a7782b29042b, the package validator
fails with `Checksum mismatch: .gitignore`; 40 of 41 unittest cases pass and
test_package_structure fails for the same reason. This pre-existing mismatch
is recorded as a failed baseline, not suppressed or repaired by rewriting a
historical digest. The package owner must reconcile the original archive and
current repository inventory before claiming package integrity. Standards
profile validation cannot substitute for that failing package gate.
