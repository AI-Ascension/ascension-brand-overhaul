# Offline publisher package

`OfflinePublisher` (also exported as `Publisher`) exposes `ingest`, `render`,
`publish`, and `verify` operations. All inputs are local sanitized JSON; all
outputs are local deterministic files. There is no provider, HTTP, host, game,
credential, or remote mutation capability in this package.

Use `python3 -m publisher --help` for the command line entry point. See
`docs/PUBLISHING.md` for the digest rule, approval boundary, output layout, and
production gate.
