# W03 independent final rereview: handoff digest boundary

This bounded rereview checks only the final source-digest repair in
`AI-Ascension/ascension-brand-overhaul`. The target is
`work/brand-overhaul` at `HEAD`
`5d1c26ecee9ce753eae89c525c4a8764d29a18e5` (`Bind handoff digests to safe
bounded JSON reads`). The reviewed implementation and test bytes are
`scripts/render_handoff.py` SHA-256
`f4d77c03a5a31836489f42f9379e8e279555de34d238215bbc2a1bcb229c2386` and
`tests/test_handoff.py` SHA-256
`402b95b2d8c20cd5a29e0858a9145a5d79adf3bc7588e78a13709c1e8d7771cf`.
The target checkout was read only. This report is the only file written, in a
clean isolated worktree. No broad discovery, package validation, full suite,
remote, host, archive, or release operation was performed.

## Verification

- `python3 -m unittest tests.test_handoff -v` passed **9/9 tests** in 2.144
  seconds against the exact committed target implementation. The final test
  covers source-tree digest inputs as external symlink, oversized, non-JSON,
  directory, and dangling paths. The earlier eight tests continue to cover
  release schema/type bounds, duplicate keys, escaping, digest output,
  legacy-versus-final requirements, and release path safety.
- `read(root, name, include_bytes=True)` now applies the same root/ancestor
  symlink check, regular-file check, 4 MiB bound, duplicate-key rejection, and
  JSON parse to every digest input, then hashes the exact raw bytes returned by
  that read. This removes the former direct `Path.read_bytes()` bypass.
- Additional temporary probes independently rejected an external
  `source-snapshot.json` symlink and a root-directory ancestor symlink. They
  also rejected an oversized required ledger and a duplicate key in a required
  ledger. A valid `require_release=True` render was deterministic and emitted
  exact digest rows for `execution/release-status.json`,
  `execution/source-snapshot.json`, and
  `execution/source-tree-inventory.json`. Naming the CLI output
  `FINAL_REPORT.md` still fails closed when the release ledger is absent.
- `git diff --check -- scripts/render_handoff.py tests/test_handoff.py`
  passed at the reviewed target. No finding from the prior W03 handoff review
  was reopened by this delta.

## Disposition

The final source-digest repair passes. Release and source evidence digest
inputs now share the bounded, duplicate-rejecting, symlink-safe JSON reader;
the digest table binds the exact bytes read; and the nine focused tests cover
the repaired input boundary. No findings remain against this delta. This
rereview grants no merge, rename, deployment, publication, campaign, archive,
or global-completion authority.
