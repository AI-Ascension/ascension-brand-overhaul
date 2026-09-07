# W03 independent rereview: handoff release-boundary repair

This rereview checks only the uncommitted repair to the handoff renderer and
its focused tests in `AI-Ascension/ascension-brand-overhaul`. The target was
`work/brand-overhaul` at `HEAD`
`9975e4b` (`Record handoff inventory review`); the repaired files were kept
dirty and read only. The reviewed working-tree bytes were
`scripts/render_handoff.py` SHA-256
`8c5965b71d8b15b7e44fea31f9e39933d5591fcf9841d24e5d3388d45e6194cf`,
`tests/test_handoff.py` SHA-256
`8ddcf6d6ca92283f3436083cc8b8b20e85e81467ed054c2c00f0f70bebdee3b2`,
`execution/source-snapshot.json` SHA-256
`3e453ee6e11f544e911fa1c33df1e2b1335007d6a47f1e082f9b0bdf2e3ceed9`,
`execution/source-tree-inventory.json` SHA-256
`ae8b2fafe387df38645d7f779b862f5e9246f0c5ef153c6e11efcaf6ffef5453`, and
`execution/release-status.json` SHA-256
`6dc0922cbbfeb2629a7a61ed713f741774e00530f78890b17469d008f14ca691`.
No other implementation, ledger, remote, host, archive, or full-suite action
was performed by this rereview. This report is the only file written, in a
clean isolated worktree.

## Verification

- `python3 -m unittest tests.test_handoff -v` passed **8/8 tests** against the
  repaired dirty files. The five added boundary tests cover escaped release
  text and digest output, missing/incorrect/empty/extra release shapes,
  duplicate object keys, legacy-versus-final release requirements, and
  directory/dangling-symlink paths. `git diff --check --
  scripts/render_handoff.py tests/test_handoff.py execution/source-snapshot.json`
  passed.
- `read()` now rejects symlinks and non-regular files, bounds every parsed
  ledger at 4 MiB, and rejects duplicate JSON object keys. `validate_release()`
  requires the exact `ai-ascension.release-status.v1` field set, a nonempty
  bounded summary, one to twenty nonempty string-valued dimensions, and one to
  two hundred nonempty strings in each release array. The focused tests and
  additional temporary probes rejected overlong summaries, oversized arrays,
  null/numeric members, an oversized required ledger, and duplicate keys in a
  required ledger.
- Valid rendering with `require_release=True` was deterministic and emitted
  matching SHA-256 rows for `execution/release-status.json`,
  `execution/source-snapshot.json`, and
  `execution/source-tree-inventory.json`. A CLI invocation naming the output
  `FINAL_REPORT.md` failed closed when the release ledger was absent; a valid
  final render succeeded. Legacy `render(root)` remains usable without a
  release ledger as documented in `scripts/README.md:25`.

## Finding

### W03-HANDOFF-02 — Source evidence digest inputs bypass the safe bounded reader (medium, open)

The new source digest rows at `scripts/render_handoff.py:127-128` select
`execution/source-snapshot.json` and
`execution/source-tree-inventory.json` with `Path.is_file()` and then call
`read_bytes()` directly. The strict `read()` boundary at `:10-27` is therefore
not applied to these two inputs. In an isolated temporary fixture, both source
paths were symlinked to regular files outside the package; rendering succeeded
and emitted the outside bytes' digests. Replacing
`source-snapshot.json` with a 4 MiB + 1 byte non-JSON file also rendered
successfully and emitted a digest row. The release ledger itself remains
protected because it goes through `read()` at `:97-98`.

This lets a final handoff bind arbitrary external or unbounded bytes under a
source-evidence path, while the new helper documentation says the handoff
rejects non-regular paths. Use one safe bounded byte-reader for every digest
input (or validate these two JSON ledgers through the same path checks before
hashing), and add focused source-snapshot/source-tree symlink, dangling,
non-regular, oversize, and malformed-content tests. If source evidence is
intentionally optional for legacy reports, retain that absence policy while
rejecting a present unsafe path and require both source ledgers for the final
report if their digests are part of final provenance.

## Disposition

The W03-HANDOFF-01 repair is effective for the release ledger: the valid
release path renders deterministically, malformed release shapes fail through
the expected `ValueError` boundary, duplicate keys and unsafe release paths
are rejected, and `FINAL_REPORT.md` requires the release ledger. The source
snapshot/tree digest addition is present and correct for regular current files,
but W03-HANDOFF-02 remains open until those hash-only paths share the safe
bounded boundary. This rereview grants no merge, rename, deployment,
publication, campaign, archive, or global-completion authority.
