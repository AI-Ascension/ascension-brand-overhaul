# GitHub migration operations

This runbook covers repository-name presentation changes for AI Ascension. It
does not rename a repository by itself. The migration tool uses the GitHub REST
API through the installed `gh api` command, resolves the current actor with
`GET /user`, and writes a reviewable plan before any possible PATCH.

The official [GitHub rename documentation](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)
says that ordinary repository information and Git operations redirect, while
project-site URLs are an exception. It also says that GitHub-hosted Actions are
not redirected: callers fail with `repository not found`. Reusing the old name
later destroys the ordinary redirect. These limits are represented as explicit
gates in every plan.

## Read-only plan

From the brand repository root, use a current map and output path:

```sh
python3 migration/tooling/github_migration.py plan \
  --map migration/input-map.json \
  --output migration/plan.json
```

The command is dry-run by construction. It reads stable repository IDs,
default-branch heads, visibility, branch protection, Pages configuration,
workflow inventory, in-progress runs, open pull requests, hosted-Action
consumers, and target-name availability. It does not call `PATCH`, change
settings, push branches, or notify owners. Re-run it immediately before an
authorized operation; the plan embeds the observed actor, timestamp,
preconditions, and API limitation fields.

For offline review against the immutable W01 snapshot:

```sh
python3 migration/tooling/github_migration.py plan \
  --map migration/input-map.json \
  --snapshot /path/to/source-snapshot.json \
  --output /tmp/ai-ascension-migration-plan.json
```

Offline data intentionally reports unavailable protected-configuration and
caller inventories as blocked. It must not be treated as current GitHub state.

## Gate meanings

Each rename operation records these gates:

- `stable_identity`: the source must still have the expected numeric ID and
  current name.
- `target_collision`: the target must be absent, or already be the expected
  repository ID. A different target repository is a hard conflict.
- `current_head`: the expected default-branch commit must still match.
- `protected_configuration`: the branch-protection response is available and
  its digest still matches the plan.
- `hosted_actions`: the source cannot host an Action and the scoped `uses:`
  search must find no caller. Unknown search is blocked.
- `active_work`: open pull requests, in-progress runs, and unavailable run
  inventory block the operation.
- `pages`: a Pages configuration requires a custom-domain/route review before
  cutover; historical Pages repositories remain `keep`.
- `authority`: remote mutation needs a separate approval file.

`ascension-map-visualizer -> sts2-map` is explicitly `deferred-rename`. Its
active assignment requires the original name, so the plan keeps that identity
pinned and records the owner coordination dependency. A display-copy change
can be reviewed independently.

## Applying a reviewed plan

The `apply` subcommand still performs a dry run unless `--apply` is present:

```sh
python3 migration/tooling/github_migration.py apply \
  --plan migration/plan.json \
  --receipt execution/migration-results.json
```

To make a remote request, a root-approved JSON file must name the exact plan
SHA-256 and operation IDs:

```json
{
  "schema_version": "ai-ascension.github-rename-approval.v1",
  "plan_sha256": "<sha256 of migration/plan.json>",
  "approved_by": "<operator>",
  "approved_at": "<timestamp>",
  "operation_ids": ["rename:AI-Ascension/sts2-harness->ascension"],
  "owner_notification_authorized": false
}
```

Then, and only then:

```sh
python3 migration/tooling/github_migration.py apply \
  --plan migration/plan.json \
  --receipt execution/migration-results.json \
  --approval /path/to/approval.json \
  --apply
```

The code re-reads every gate before each request. It records the sanitized
request/response, attempt number, timestamp, and read-after-write target
observation. A target with the expected ID is `already_satisfied`, so a retry
cannot create a duplicate. A timeout is `unknown`; the receipt blocks a second
request until a reviewer explicitly uses `--retry-unknown` after reconciling
the target. No automatic rollback or owner notification is performed.

## Rollback decision

A failed verification never triggers a reverse rename. Before a separately
approved reverse operation, re-read target identity, source-name availability,
head, protected configuration, Pages/custom-domain state, hosted-Action
callers, active work, and the redirect consequences. Prefer a forward fix
when the target is healthy. See [ROLLBACK.md](ROLLBACK.md) for the decision
record and preconditions.


## Interrupted operations and receipt ownership

The tool writes a pending unknown receipt before each remote rename request and persists its result before continuing. Unknown, waiting-for-reconciliation and verification-failed attempts remain gated on explicit reconciliation; repeated ordinary invocations cannot silently reopen them. A receipt must match the exact plan digest. The receipt lock serializes invocations using that receipt and is never aged out automatically. After a hard interruption, verify that the owning process is terminal and reconcile the pending operation before removing its specific lock. Use one root-owned receipt per operation set; distinct receipt paths do not provide a global cross-process lock.

`migration/input-map.json` binds the approved name map to W01 stable repository IDs and source heads. Reconcile changed heads before issuing a new plan; never replace the stable identity merely because a name resolves to a different repository. The checked-in plan recomputes preflights from captured live API observations at its recorded timestamp, with exact input digests; it is not authority for a future rename.
