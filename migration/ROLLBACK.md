# Migration rollback entry point

The implemented approval, identity, precondition, backup, retry, and reverse-rename procedure is in [MIGRATION_OPERATIONS.md](../docs/MIGRATION_OPERATIONS.md). The website/source/data recovery boundary is in [ROLLBACK.md](../docs/ROLLBACK.md).

No rename or rollback has been performed. Reverse rename is a new live operation requiring fresh stable-ID/head/destination checks, Pages and Actions reconciliation, a valid backup reference, and exact actor/plan/operation approval. Never recreate retired names or overwrite another actor's changes. `execution/migration-results.json` records the read-only state.
