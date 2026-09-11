# Input integrity

These are the supplied package integrity records, retained unchanged. Repository initialization replaced the 113-byte package `.gitignore` with a 60-byte implementation ignore file before the first commit. Its original content was not retained; its original digest is recorded here. The active integrity records explicitly reflect this change. These retained records describe the supplied input, not the later implementation. Git history and the active root manifest record intentional implementation changes. The final package validator checks the complete current source candidate against that active manifest; it cannot reconstruct the lost original `.gitignore` bytes.

The archive helper was then hardened to exclude private execution/client directories (case-insensitively) and refuse overwriting an existing delivery. Active integrity records track that reviewed implementation change separately from these original records.

Package source validation now excludes local dependency/private/client directories while continuing to reject font binaries and symlinks in owned source paths. This keeps installed browser tooling outside prompt-package validation and delivery.

The asset status schema now permits truthful blocked entries with zero generation records. Verified entries still require actual generation records and exports and cannot retain a blocker; the release validator continues to reject all blocked assets.

The helper README now documents implemented runtime observation, content sync, browser review and handoff tools and their actual dependencies. Its active digest is updated; the supplied record remains unchanged here.
