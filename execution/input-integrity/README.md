# Input integrity

These are the supplied package integrity records, retained unchanged. Repository initialization replaced the 113-byte package `.gitignore` with a 60-byte implementation ignore file before the first commit. Its original content was not retained; its original digest is recorded here. The active integrity records explicitly reflect this change. All other supplied entries remain checked against the supplied digests. New implementation files are tracked by Git and their own delivery evidence; the package integrity check alone does not cover them.

The archive helper was then hardened to exclude private execution/client directories (case-insensitively) and refuse overwriting an existing delivery. Active integrity records track that reviewed implementation change separately from these original records.
