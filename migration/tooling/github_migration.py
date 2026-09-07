#!/usr/bin/env python3
"""Plan and, with a separately recorded approval, rename GitHub repositories.

The command is deliberately plan-first.  ``plan`` performs read-only repository
and caller checks and writes a reviewable plan.  ``apply`` remains a dry run
unless ``--apply`` and an approval file whose digest matches the plan are both
provided.  The apply path re-reads every precondition immediately before a
PATCH, records a receipt, and verifies the target by a fresh GET.  It never
sends owner notifications or retries an unknown response automatically.

Only the standard library is used.  The live client invokes ``gh api`` so that
the authenticated actor and GitHub API semantics are explicit.  Tests inject a
small fake client and never contact GitHub.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Iterable, Mapping
from urllib.parse import quote, urlencode


SCHEMA_VERSION = "ai-ascension.github-migration.v1"
APPROVAL_SCHEMA_VERSION = "ai-ascension.github-rename-approval.v1"
RECEIPT_SCHEMA_VERSION = "ai-ascension.github-migration-receipt.v1"
RENAME_DOCS_URL = (
    "https://docs.github.com/en/repositories/creating-and-managing-repositories/"
    "renaming-a-repository"
)
DEFAULT_OWNER = "AI-Ascension"
RENAME_ACTIONS = {"rename"}
KEEP_ACTIONS = {"keep", "create-or-reuse"}
DEFERRED_ACTIONS = {"deferred-rename"}
ACTIVE_RUN_STATUSES = ("queued", "in_progress", "waiting", "requested", "pending")


def _valid_repo_name(value: Any) -> bool:
    return (
        isinstance(value, str)
        and bool(value.strip())
        and value not in {".", ".."}
        and "/" not in value
        and "\\" not in value
        and len(value) <= 100
    )


class MigrationError(RuntimeError):
    """A safe, user-facing refusal or API failure."""


class ApiError(MigrationError):
    """A GitHub API request failed without exposing credentials."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        ambiguous: bool | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code if status_code is not None else _status_code(message)
        if ambiguous is None:
            text = message.lower()
            ambiguous = (
                self.status_code is not None
                and (self.status_code >= 500 or self.status_code in {408, 425, 429})
            ) or any(
                marker in text
                for marker in (
                    "timeout",
                    "timed out",
                    "request failed",
                    "connection reset",
                    "connection aborted",
                    "broken pipe",
                    "network",
                )
            )
        self.ambiguous = bool(ambiguous)


def canonical_json(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def utc_now() -> str:
    # Avoid a dependency on dateutil and keep the receipt easy to compare.
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError(f"Could not read JSON {path}: {exc}") from exc


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError as exc:
        raise MigrationError(f"Could not write {path}: {exc}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _status_error(stderr: bytes | str) -> str:
    # gh includes the HTTP status in its final line.  Keep only a short public
    # diagnostic; never copy environment values or headers into a receipt.
    text = stderr.decode(errors="replace") if isinstance(stderr, bytes) else str(stderr)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return (lines[-1] if lines else "GitHub API request failed")[:400]


def _status_code(value: bytes | str) -> int | None:
    text = value.decode(errors="replace") if isinstance(value, bytes) else str(value)
    # gh has emitted both `HTTP 404` and `404 Not Found` forms over time.
    match = re.search(r"\b(?:HTTP(?:\s+status)?\s*)?([45]\d{2})\b", text, re.IGNORECASE)
    return int(match.group(1)) if match else None


def _append_page(path: str, page: int) -> str:
    return f"{path}{'&' if '?' in path else '?'}page={page}"


class GhApi:
    """Read/write adapter over the installed GitHub CLI's REST API."""

    def __init__(self, *, executable: str = "gh", host: str = "github.com", timeout: int = 45):
        self.executable = executable
        self.host = host
        self.timeout = timeout

    def request(self, method: str, path: str, body: Mapping[str, Any] | None = None) -> Any:
        args = [self.executable, "api", path.lstrip("/"), "--hostname", self.host, "--method", method]
        input_data: bytes | None = None
        if body is not None:
            args.extend(["--input", "-"])
            input_data = canonical_json(body)
        try:
            result = subprocess.run(
                args,
                input=input_data,
                capture_output=True,
                check=False,
                timeout=self.timeout,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ApiError(
                f"GitHub API request failed: {type(exc).__name__}",
                ambiguous=True,
            ) from exc
        if result.returncode != 0:
            message = _status_error(result.stderr)
            status_code = _status_code(result.stderr)
            raise ApiError(
                message,
                status_code=status_code,
                ambiguous=status_code is not None
                and (status_code >= 500 or status_code in {408, 425, 429}),
            )
        if not result.stdout.strip():
            return {}
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ApiError("GitHub API returned non-JSON data", ambiguous=True) from exc

    def current_user(self) -> dict[str, Any] | None:
        value = self.request("GET", "user")
        if not isinstance(value, dict):
            return None
        return {key: value.get(key) for key in ("login", "id", "html_url") if key in value}

    def _list_paginated(self, path: str, key: str | None = None) -> list[dict[str, Any]]:
        """Read every page, refusing to call an incomplete inventory complete."""
        rows: list[dict[str, Any]] = []
        page = 1
        # GitHub search results are capped at 1,000 rows.  Reaching this limit
        # with full pages is an incomplete inventory, so fail closed rather
        # than silently treating the first thousand rows as exhaustive.
        max_pages = 100
        while page <= max_pages:
            result = self.request("GET", path if page == 1 else _append_page(path, page))
            if key is None:
                batch = result if isinstance(result, list) else None
            else:
                batch = result.get(key) if isinstance(result, dict) else None
            if not isinstance(batch, list):
                label = key or "array"
                raise ApiError(f"GitHub API response for {path} has no {label} list")
            if isinstance(result, dict) and result.get("incomplete_results") is True:
                raise ApiError(f"GitHub API pagination for {path} is incomplete")
            rows.extend(item for item in batch if isinstance(item, dict))
            if key == "items" and len(rows) >= 1000 and len(batch) == 100:
                # GitHub code search exposes at most 1,000 rows.  A full
                # tenth page cannot prove that no additional caller exists.
                raise ApiError(f"GitHub API search inventory for {path} reached its result cap")
            if len(batch) < 100:
                total_count = result.get("total_count") if isinstance(result, dict) else None
                if isinstance(total_count, int) and not isinstance(total_count, bool) and total_count != len(rows):
                    raise ApiError(f"GitHub API pagination for {path} is incomplete")
                return rows
            page += 1
        raise ApiError("GitHub API pagination did not complete")

    def _list(self, path: str, key: str) -> list[dict[str, Any]]:
        return self._list_paginated(path, key)

    def _contents_exists(self, owner: str, name: str, path: str) -> bool | None:
        try:
            result = self.request("GET", f"repos/{quote(owner)}/{quote(name)}/contents/{quote(path)}")
        except ApiError as exc:
            if exc.status_code == 404:
                return False
            return None
        return isinstance(result, dict)

    def _action_consumers(self, owner: str, name: str) -> tuple[list[dict[str, str]], bool, str | None]:
        # A repository mention in prose is not a hosted-Action dependency.
        # Search for the workflow ``uses:`` form and retain the query scope in
        # the plan so a reviewer can see what the API check covered.
        query = urlencode({"q": f'"uses: {owner}/{name}" org:{owner}', "per_page": "100"})
        try:
            items = self._list_paginated(f"search/code?{query}", "items")
            consumers = []
            for item in items:
                repo = item.get("repository")
                full_name = repo.get("full_name") if isinstance(repo, dict) else None
                path = item.get("path") if isinstance(item, dict) else None
                if (
                    isinstance(full_name, str)
                    and isinstance(path, str)
                    and full_name.lower() != f"{owner}/{name}".lower()
                    and (path.startswith(".github/workflows/") or path.startswith(".github/actions/"))
                ):
                    consumers.append({"repository": full_name, "path": path})
            return consumers, True, None
        except MigrationError as exc:
            return [], False, str(exc)[:400]

    def rename_repo(self, owner: str, source_name: str, target_name: str) -> dict[str, Any]:
        result = self.request("PATCH", f"repos/{quote(owner)}/{quote(source_name)}", {"name": target_name})
        if not isinstance(result, dict):
            raise ApiError("GitHub rename returned no repository object")
        return result

    def observe_repo(self, owner: str, name: str) -> dict[str, Any]:
        path = f"repos/{quote(owner)}/{quote(name)}"
        try:
            raw = self.request("GET", path)
        except ApiError as exc:
            # A repository GET has a documented absence meaning.  Other
            # endpoints below keep 404 as unknown because absence is not
            # established by an unreadable optional endpoint.
            if exc.status_code == 404:
                return {"exists": False, "owner": owner, "name": name}
            raise
        if raw is None:
            # A test double or older gh wrapper may still use ``None`` for
            # the repository GET's documented 404 absence contract.
            return {"exists": False, "owner": owner, "name": name}
        if not isinstance(raw, dict):
            raise ApiError(f"Repository response for {owner}/{name} is not an object")
        default_branch = raw.get("default_branch")
        branch: dict[str, Any] | None = None
        branch_error: str | None = None
        protection: Any = None
        protection_error: str | None = None
        if isinstance(default_branch, str) and default_branch:
            try:
                branch = self.request("GET", f"{path}/branches/{quote(default_branch, safe='')}" )
            except MigrationError as exc:
                branch_error = str(exc)[:400]
            if not isinstance(branch, dict) and branch_error is None:
                branch_error = "default branch endpoint returned no object"
            if isinstance(branch, dict) and branch.get("protected"):
                try:
                    protection = self.request("GET", f"{path}/branches/{quote(default_branch, safe='')}/protection")
                except MigrationError as exc:
                    protection_error = str(exc)[:400]
                if not isinstance(protection, dict) and protection_error is None:
                    protection_error = "branch protection endpoint returned no object"
        pages: Any = None
        pages_error: str | None = None
        try:
            pages = self.request("GET", f"{path}/pages")
        except MigrationError as exc:
            pages_error = str(exc)[:400]
        if pages_error is None and not isinstance(pages, dict):
            pages_error = "Pages endpoint returned no object"
        workflow_error: str | None = None
        workflows: list[dict[str, Any]] = []
        active_runs: list[dict[str, Any]] = []
        pulls: list[dict[str, Any]] = []
        try:
            workflows = self._list(f"{path}/actions/workflows?per_page=100", "workflows")
        except MigrationError as exc:
            workflow_error = str(exc)[:400]
        for run_status in ACTIVE_RUN_STATUSES:
            try:
                active_runs.extend(
                    self._list(
                        f"{path}/actions/runs?status={run_status}&per_page=100",
                        "workflow_runs",
                    )
                )
            except MigrationError as exc:
                workflow_error = (workflow_error or "") + f" active-runs[{run_status}]: " + str(exc)[:260]
        pull_error: str | None = None
        try:
            pulls = self._list_paginated(f"{path}/pulls?state=open&per_page=100", None)
        except MigrationError as exc:
            pull_error = str(exc)[:400]

        hosted_action: bool | None
        action_checks = [self._contents_exists(owner, name, "action.yml"), self._contents_exists(owner, name, "action.yaml")]
        hosted_action = True if any(check is True for check in action_checks) else False if all(check is False for check in action_checks) else None
        consumers, consumers_known, consumers_error = self._action_consumers(owner, name)
        head_sha = None
        if isinstance(branch, dict):
            commit = branch.get("commit")
            if isinstance(commit, dict) and isinstance(commit.get("sha"), str):
                head_sha = commit["sha"]
        protected = branch.get("protected") if isinstance(branch, dict) else None
        protection_descriptor = {
            "branch_protected": protected if isinstance(protected, bool) else None,
            "configuration": protection if isinstance(protection, (dict, list)) else None,
            "available": (
                branch_error is None
                and protection_error is None
                and isinstance(protected, bool)
                and (not protected or protection is not None)
            ),
            "error": branch_error or protection_error,
        }
        def pull_summary(item: Mapping[str, Any]) -> dict[str, Any]:
            summary = {key: item.get(key) for key in ("number", "title", "state", "html_url") if key in item}
            for side in ("head", "base"):
                value = item.get(side)
                if isinstance(value, Mapping):
                    side_value: dict[str, Any] = {key: value.get(key) for key in ("ref", "sha") if key in value}
                    repo = value.get("repo")
                    if isinstance(repo, Mapping) and isinstance(repo.get("full_name"), str):
                        side_value["repo"] = repo["full_name"]
                    summary[side] = side_value
            return summary

        return {
            "exists": True,
            "owner": owner,
            "name": raw.get("name", name),
            "full_name": raw.get("full_name", f"{owner}/{name}"),
            "id": raw.get("id"),
            "default_branch": default_branch,
            "head_sha": head_sha,
            "visibility": raw.get("visibility"),
            "archived": raw.get("archived"),
            "branch_error": branch_error,
            "branch_protected": protected,
            "protected_configuration": protection_descriptor,
            "pages": pages if isinstance(pages, dict) else None,
            "pages_available": pages_error is None,
            "pages_error": pages_error,
            "workflows": [
                {key: item.get(key) for key in ("id", "name", "path", "state", "html_url") if key in item}
                for item in workflows
            ],
            "active_runs": [
                {key: item.get(key) for key in ("id", "name", "status", "head_sha", "html_url") if key in item}
                for item in active_runs
            ],
            "workflow_read_available": workflow_error is None,
            "workflow_error": workflow_error,
            "open_pull_requests": [pull_summary(item) for item in pulls],
            "pull_read_available": pull_error is None,
            "pull_error": pull_error,
            "active_run_statuses": list(ACTIVE_RUN_STATUSES),
            "hosted_action": hosted_action,
            "action_consumers": consumers,
            "action_consumers_known": consumers_known,
            "action_consumers_error": consumers_error,
        }


class SnapshotClient:
    """Offline adapter for the immutable W01 source snapshot."""

    def __init__(self, snapshot: Mapping[str, Any]):
        validate_snapshot(snapshot)
        self.snapshot = snapshot
        self.entries = {
            item.get("full_name", "").lower(): item
            for item in snapshot.get("repositories", [])
            if isinstance(item, dict) and isinstance(item.get("full_name"), str)
        }
        self.pulls = {}
        for pull in snapshot.get("active_pull_requests", []):
            if isinstance(pull, dict) and isinstance(pull.get("repository"), str):
                self.pulls.setdefault(pull["repository"].lower(), []).append(pull)

    def observe_repo(self, owner: str, name: str) -> dict[str, Any]:
        full_name = f"{owner}/{name}"
        source = self.entries.get(full_name.lower())
        if source is None:
            return {"exists": False, "owner": owner, "name": name}
        repo_pulls = self.pulls.get(full_name.lower(), [])
        # The snapshot intentionally did not claim that protected settings or
        # Action search were readable.  Preserve that limitation as unknown.
        return {
            "exists": True,
            "owner": owner,
            "name": name,
            "full_name": source.get("full_name", full_name),
            "id": source.get("stable_id"),
            "default_branch": source.get("default_branch"),
            "head_sha": source.get("default_head"),
            "visibility": source.get("visibility"),
            "archived": None,
            "branch_error": "not recorded in source snapshot",
            "branch_protected": None,
            "protected_configuration": {"branch_protected": None, "configuration": None, "available": False, "error": "not recorded in source snapshot"},
            "pages": None,
            "pages_available": False,
            "pages_error": "not recorded in source snapshot",
            "workflows": [],
            "active_runs": [],
            "workflow_read_available": False,
            "workflow_error": "not recorded in source snapshot",
            "open_pull_requests": repo_pulls,
            "pull_read_available": False,
            "pull_error": "not recorded in source snapshot",
            "active_run_statuses": list(ACTIVE_RUN_STATUSES),
            "hosted_action": None,
            "action_consumers": [],
            "action_consumers_known": False,
            "action_consumers_error": "not recorded in source snapshot",
        }

    def current_user(self) -> dict[str, Any] | None:
        value = self.snapshot.get("github_account")
        if not isinstance(value, Mapping):
            return None
        return {key: value.get(key) for key in ("login", "id") if key in value}


def protection_digest(observed: Mapping[str, Any]) -> str:
    value = observed.get("protected_configuration")
    return sha256_json(value)


def compact_repo(observed: Mapping[str, Any]) -> dict[str, Any]:
    """Keep only public, review-relevant fields in plans and receipts."""
    raw_owner = observed.get("owner")
    owner = raw_owner.get("login") if isinstance(raw_owner, Mapping) else raw_owner
    # GhApi.observe_repo returns an explicit ``exists`` marker.  A PATCH
    # response is the raw GitHub repository object, so infer existence from
    # its stable identity before sanitizing it into the receipt.
    exists = observed.get("exists")
    if exists is None:
        exists = isinstance(observed.get("id"), int) and isinstance(observed.get("name"), str)
    if not exists:
        return {"exists": False, "owner": owner, "name": observed.get("name")}
    protection = observed.get("protected_configuration")
    protection_out = None
    if isinstance(protection, Mapping):
        protection_out = {
            "branch_protected": protection.get("branch_protected"),
            "available": protection.get("available"),
            "digest": sha256_json(protection),
            "error": protection.get("error"),
        }
    return {
        "exists": True,
        "owner": owner,
        "name": observed.get("name"),
        "full_name": observed.get("full_name"),
        "id": observed.get("id"),
        "default_branch": observed.get("default_branch"),
        "head_sha": observed.get("head_sha"),
        "visibility": observed.get("visibility"),
        "archived": observed.get("archived"),
        "branch_error": observed.get("branch_error"),
        "branch_protected": observed.get("branch_protected"),
        "protected_configuration": protection_out,
        "pages": observed.get("pages"),
        "pages_available": observed.get("pages_available"),
        "pages_error": observed.get("pages_error"),
        "workflows": observed.get("workflows", []),
        "active_runs": observed.get("active_runs", []),
        "workflow_read_available": observed.get("workflow_read_available"),
        "workflow_error": observed.get("workflow_error"),
        "open_pull_requests": observed.get("open_pull_requests", []),
        "pull_read_available": observed.get("pull_read_available"),
        "pull_error": observed.get("pull_error"),
        "active_run_statuses": observed.get("active_run_statuses", list(ACTIVE_RUN_STATUSES)),
        "hosted_action": observed.get("hosted_action"),
        "action_consumers": observed.get("action_consumers", []),
        "action_consumers_known": observed.get("action_consumers_known"),
        "action_consumers_error": observed.get("action_consumers_error"),
    }


def gate(status: str, code: str, detail: Any = None) -> dict[str, Any]:
    result = {"status": status, "code": code}
    if detail is not None:
        result["detail"] = detail
    return result


def _expected_protection(op: Mapping[str, Any]) -> Mapping[str, Any] | None:
    value = op.get("preconditions", {}).get("protected_configuration")
    return value if isinstance(value, Mapping) else None


def _backup_reference_matches(op: Mapping[str, Any], source: Mapping[str, Any]) -> tuple[bool, str, Any]:
    reference = op.get("backup_reference")
    if not isinstance(reference, Mapping):
        return False, "backup_reference_missing", None
    snapshot = reference.get("snapshot")
    digest = reference.get("snapshot_sha256")
    if reference.get("immutable") is not True or not isinstance(snapshot, Mapping) or not isinstance(digest, str):
        return False, "backup_reference_invalid", None
    actual_snapshot_digest = sha256_json(snapshot)
    current_digest = sha256_json(compact_repo(source))
    if digest != actual_snapshot_digest:
        return False, "backup_reference_digest_invalid", {"expected": digest, "observed": actual_snapshot_digest}
    if digest != current_digest:
        return False, "stale_backup_reference", {"expected": digest, "observed": current_digest}
    return True, "backup_reference_matches", {"sha256": digest}


def evaluate_operation(
    op: Mapping[str, Any],
    source: Mapping[str, Any],
    target: Mapping[str, Any],
    *,
    authorized: bool,
) -> dict[str, Any]:
    """Evaluate all rename gates without making a remote mutation."""
    action = op.get("action")
    expected_id = op.get("preconditions", {}).get("expected_stable_repository_id")
    expected_name = op.get("source_name")
    expected_head = op.get("preconditions", {}).get("expected_current_head")
    expected_default_branch = op.get("preconditions", {}).get("expected_default_branch")
    expected_visibility = op.get("preconditions", {}).get("expected_visibility")
    gates: dict[str, dict[str, Any]] = {}
    blockers: list[str] = []

    if action in KEEP_ACTIONS:
        return {"status": "not_applicable", "gates": {"action": gate("pass", "keep_or_create_only")}, "blockers": []}
    if action in DEFERRED_ACTIONS:
        gates["active_work"] = gate("deferred", "active_assignment_pins_original_name", op.get("note"))
        gates["authority"] = gate("blocked", "rename_authorization_required")
        return {"status": "deferred", "gates": gates, "blockers": ["active_assignment_pins_original_name"]}
    if action not in RENAME_ACTIONS:
        return {"status": "blocked", "gates": {"action": gate("blocked", "unknown_action")}, "blockers": ["unknown_action"]}

    source_exists = bool(source.get("exists"))
    target_exists = bool(target.get("exists"))
    already_renamed = (
        target_exists
        and target.get("id") == expected_id
        and target.get("name") == op.get("target_name")
        and (not source_exists or source.get("id") in {None, expected_id})
    )
    if already_renamed:
        gates["stable_identity"] = gate("pass", "already_renamed_expected_id", expected_id)
        gates["target_collision"] = gate("pass", "target_is_expected_repository", expected_id)
        gates["authority"] = gate("pass", "no_mutation_required")
        return {"status": "already_satisfied", "gates": gates, "blockers": [], "idempotent": True}

    if not source_exists:
        gates["stable_identity"] = gate("blocked", "source_repository_missing", expected_name)
        blockers.append("source_repository_missing")
    elif source.get("id") != expected_id:
        gates["stable_identity"] = gate("blocked", "stale_stable_repository_id", {"expected": expected_id, "observed": source.get("id")})
        blockers.append("stale_stable_repository_id")
    elif source.get("name") != expected_name:
        gates["stable_identity"] = gate("blocked", "source_name_changed", {"expected": expected_name, "observed": source.get("name")})
        blockers.append("source_name_changed")
    else:
        gates["stable_identity"] = gate("pass", "expected_stable_repository_id")

    if not isinstance(expected_default_branch, str) or not expected_default_branch:
        gates["default_branch"] = gate("blocked", "missing_expected_default_branch")
        blockers.append("missing_expected_default_branch")
    elif source.get("default_branch") != expected_default_branch:
        gates["default_branch"] = gate(
            "blocked",
            "stale_default_branch",
            {"expected": expected_default_branch, "observed": source.get("default_branch")},
        )
        blockers.append("stale_default_branch")
    else:
        gates["default_branch"] = gate("pass", "expected_default_branch")

    if not isinstance(expected_visibility, str) or not expected_visibility:
        gates["visibility"] = gate("blocked", "missing_expected_visibility")
        blockers.append("missing_expected_visibility")
    elif source.get("visibility") != expected_visibility:
        gates["visibility"] = gate(
            "blocked",
            "stale_visibility",
            {"expected": expected_visibility, "observed": source.get("visibility")},
        )
        blockers.append("stale_visibility")
    else:
        gates["visibility"] = gate("pass", "expected_visibility")

    if target_exists:
        if target.get("id") == expected_id and target.get("name") == op.get("target_name"):
            gates["target_collision"] = gate("pass", "target_is_expected_repository", expected_id)
        else:
            gates["target_collision"] = gate("blocked", "target_name_collision", {"target_id": target.get("id"), "target_name": target.get("name")})
            blockers.append("target_name_collision")
    else:
        gates["target_collision"] = gate("pass", "target_name_available")

    if not expected_head:
        gates["current_head"] = gate("blocked", "missing_expected_current_head")
        blockers.append("missing_expected_current_head")
    elif source.get("head_sha") != expected_head:
        gates["current_head"] = gate("blocked", "stale_current_head", {"expected": expected_head, "observed": source.get("head_sha")})
        blockers.append("stale_current_head")
    else:
        gates["current_head"] = gate("pass", "expected_current_head")

    expected_protection = _expected_protection(op)
    observed_protection = source.get("protected_configuration")
    if not isinstance(observed_protection, Mapping) or not observed_protection.get("available"):
        gates["protected_configuration"] = gate("blocked", "protected_configuration_unavailable", source.get("workflow_error"))
        blockers.append("protected_configuration_unavailable")
    elif expected_protection is not None:
        observed_digest = sha256_json(observed_protection)
        expected_digest = expected_protection.get("digest")
        if expected_digest and observed_digest != expected_digest:
            gates["protected_configuration"] = gate("blocked", "stale_protected_configuration", {"expected": expected_digest, "observed": observed_digest})
            blockers.append("stale_protected_configuration")
        else:
            gates["protected_configuration"] = gate("pass", "protected_configuration_matches")
    else:
        gates["protected_configuration"] = gate("blocked", "missing_expected_protected_configuration")
        blockers.append("missing_expected_protected_configuration")

    backup_matches, backup_code, backup_detail = _backup_reference_matches(op, source)
    gates["backup"] = gate("pass" if backup_matches else "blocked", backup_code, backup_detail)
    if not backup_matches:
        blockers.append(backup_code)

    hosted_action = source.get("hosted_action")
    consumers_known = source.get("action_consumers_known") is True
    consumers = source.get("action_consumers") or []
    if hosted_action is True:
        gates["hosted_actions"] = gate("blocked", "repository_hosts_action", source.get("workflows", []))
        blockers.append("repository_hosts_action")
    elif not consumers_known:
        gates["hosted_actions"] = gate("blocked", "hosted_action_consumers_unavailable", source.get("action_consumers_error"))
        blockers.append("hosted_action_consumers_unavailable")
    elif consumers:
        gates["hosted_actions"] = gate("blocked", "hosted_action_consumers_found", consumers)
        blockers.append("hosted_action_consumers_found")
    else:
        gates["hosted_actions"] = gate("pass", "no_hosted_action_consumers_observed")

    open_prs = source.get("open_pull_requests") or []
    active_runs = source.get("active_runs") or []
    workflow_available = source.get("workflow_read_available") is True
    pull_available = source.get("pull_read_available", True) is True
    if open_prs or active_runs:
        gates["active_work"] = gate("blocked", "active_work_present", {"pull_requests": open_prs, "runs": active_runs})
        blockers.append("active_work_present")
    elif not workflow_available or not pull_available:
        detail = {
            "workflow_error": source.get("workflow_error"),
            "pull_error": source.get("pull_error"),
            "active_run_statuses": source.get("active_run_statuses", list(ACTIVE_RUN_STATUSES)),
        }
        gates["active_work"] = gate("blocked", "active_work_inventory_unavailable", detail)
        blockers.append("active_work_inventory_unavailable")
    else:
        gates["active_work"] = gate("pass", "no_open_pull_requests_or_runs")

    if source.get("pages") is not None:
        pages = source.get("pages")
        cname = pages.get("cname") if isinstance(pages, Mapping) else None
        gates["pages"] = gate("blocked", "pages_requires_custom_domain_check", {"cname": cname, "preserve": True})
        blockers.append("pages_requires_custom_domain_check")
    elif source.get("pages_available") is not True:
        gates["pages"] = gate("blocked", "pages_configuration_unavailable", source.get("pages_error"))
        blockers.append("pages_configuration_unavailable")
    else:
        gates["pages"] = gate("pass", "no_pages_configuration_observed")

    if authorized:
        gates["authority"] = gate("pass", "approval_matches_plan")
    else:
        gates["authority"] = gate("blocked", "rename_authorization_required")
        blockers.append("rename_authorization_required")

    return {"status": "ready" if not blockers else "blocked", "gates": gates, "blockers": blockers}


def load_map(path: Path) -> list[dict[str, Any]]:
    value = read_json(path)
    if not isinstance(value, list) or not value:
        raise MigrationError("Repository map must be a non-empty JSON array")
    rows = [item for item in value if isinstance(item, dict)]
    if len(rows) != len(value):
        raise MigrationError("Repository map contains a non-object row")
    validate_repository_rows(rows)
    return rows


def validate_repository_rows(rows: Iterable[Mapping[str, Any]]) -> None:
    """Reject ambiguous map identities before any observations are derived."""
    names: set[tuple[str, str]] = set()
    stable_ids: set[int] = set()
    for index, item in enumerate(rows):
        if not isinstance(item, Mapping):
            raise MigrationError(f"Repository map row {index} is not an object")
        source_name = item.get("source_name")
        target_name = item.get("target_name")
        if not _valid_repo_name(source_name):
            raise MigrationError(f"Repository map row {index} has no source_name")
        if not _valid_repo_name(target_name):
            raise MigrationError(f"Repository map row {index} has no target_name")
        owner = item.get("owner", DEFAULT_OWNER)
        if not isinstance(owner, str) or not owner.strip():
            raise MigrationError(f"Repository map row {index} has no owner")
        identity = (owner.casefold(), source_name.casefold())
        if identity in names:
            raise MigrationError(f"Repository map repeats {owner}/{source_name}")
        names.add(identity)
        stable_id = item.get("stable_repository_id")
        if stable_id is not None:
            if isinstance(stable_id, bool) or not isinstance(stable_id, int) or stable_id < 1:
                raise MigrationError(f"Repository map row {index} has an invalid stable_repository_id")
            if stable_id in stable_ids:
                raise MigrationError(f"Repository map repeats stable repository ID {stable_id}")
            stable_ids.add(stable_id)


def validate_snapshot(snapshot: Mapping[str, Any]) -> None:
    """Validate immutable snapshot identity rows before building a plan."""
    if not isinstance(snapshot, Mapping) or not isinstance(snapshot.get("repositories"), list):
        raise MigrationError("Source snapshot must contain a repositories array")
    schema_version = snapshot.get("schema_version")
    if not isinstance(schema_version, str) or re.fullmatch(r"[a-zA-Z0-9._-]+", schema_version) is None:
        raise MigrationError("Source snapshot has no valid schema_version")
    names: set[str] = set()
    stable_ids: set[int] = set()
    for index, item in enumerate(snapshot["repositories"]):
        if not isinstance(item, Mapping):
            raise MigrationError(f"Source snapshot row {index} is not an object")
        full_name = item.get("full_name")
        if not isinstance(full_name, str) or full_name.count("/") != 1 or not all(full_name.split("/")):
            raise MigrationError(f"Source snapshot row {index} has an invalid full_name")
        snapshot_owner, snapshot_name = full_name.split("/")
        if not snapshot_owner.strip() or not _valid_repo_name(snapshot_name):
            raise MigrationError(f"Source snapshot row {index} has an invalid full_name")
        normalized_name = full_name.casefold()
        if normalized_name in names:
            raise MigrationError(f"Source snapshot repeats {full_name}")
        names.add(normalized_name)
        stable_id = item.get("stable_id")
        if isinstance(stable_id, bool) or not isinstance(stable_id, int) or stable_id < 1:
            raise MigrationError(f"Source snapshot row {index} has an invalid stable_id")
        if stable_id in stable_ids:
            raise MigrationError(f"Source snapshot repeats stable_id {stable_id}")
        stable_ids.add(stable_id)


def snapshot_provenance(snapshot: Mapping[str, Any], digest: str | None = None) -> dict[str, Any]:
    """Return a digest and schema marker suitable for a reviewable plan."""
    validate_snapshot(snapshot)
    snapshot_digest = digest or sha256_json(snapshot)
    if not isinstance(snapshot_digest, str) or re.fullmatch(r"[0-9a-f]{64}", snapshot_digest) is None:
        raise MigrationError("Source snapshot digest is not a SHA-256 value")
    return {
        "provided": True,
        "schema_version": snapshot.get("schema_version"),
        "sha256": snapshot_digest,
        "collection_date": snapshot.get("collection_date"),
        "repository_count": len(snapshot["repositories"]),
    }


def load_snapshot(path: Path | None) -> Mapping[str, Any] | None:
    if path is None:
        return None
    value = read_json(path)
    if not isinstance(value, Mapping):
        raise MigrationError("Source snapshot must be a JSON object")
    validate_snapshot(value)
    return value


def expected_by_name(snapshot: Mapping[str, Any] | None, owner: str, name: str) -> Mapping[str, Any] | None:
    if snapshot is None:
        return None
    full_name = f"{owner}/{name}".lower()
    for item in snapshot.get("repositories", []):
        if isinstance(item, Mapping) and str(item.get("full_name", "")).lower() == full_name:
            return item
    return None


def build_plan(
    repository_map: Iterable[Mapping[str, Any]],
    client: Any,
    *,
    owner: str = DEFAULT_OWNER,
    snapshot: Mapping[str, Any] | None = None,
    observed_at: str | None = None,
    snapshot_sha256: str | None = None,
) -> dict[str, Any]:
    repository_rows = list(repository_map)
    validate_repository_rows(repository_rows)
    if snapshot is not None:
        validate_snapshot(snapshot)
    actor = client.current_user() if callable(getattr(client, "current_user", None)) else None
    generated_at = observed_at or utc_now()
    operations: list[dict[str, Any]] = []
    for item in repository_rows:
        source_name = item.get("source_name")
        target_name = item.get("target_name")
        if not isinstance(source_name, str) or not isinstance(target_name, str):
            raise MigrationError("Every repository-map row needs source_name and target_name")
        repo_owner = item.get("owner") if isinstance(item.get("owner"), str) else owner
        if repo_owner != DEFAULT_OWNER:
            raise MigrationError(f"Repository owner {repo_owner!r} is outside the approved migration scope")
        source = client.observe_repo(repo_owner, source_name)
        target = source if target_name == source_name else client.observe_repo(repo_owner, target_name)
        expected = expected_by_name(snapshot, repo_owner, source_name)
        mapped_id = item.get("stable_repository_id")
        if expected is not None and mapped_id is not None and mapped_id != expected.get("stable_id"):
            raise MigrationError(
                f"Repository map stable ID for {repo_owner}/{source_name} disagrees with the source snapshot"
            )
        expected_id = (expected.get("stable_id") if expected else mapped_id) or source.get("id")
        expected_head = item.get("source_head") or (expected.get("default_head") if expected else source.get("head_sha"))
        operation_id = f"rename:{repo_owner}/{source_name}->{target_name}"
        source_backup = compact_repo(source)
        op = {
            "operation_id": operation_id,
            "owner": repo_owner,
            "source_name": source_name,
            "target_name": target_name,
            "action": item.get("action"),
            "display_title": item.get("display_title"),
            "description": item.get("description"),
            "note": item.get("note"),
            "backup_reference": {
                "kind": "plan_embedded_repository_metadata",
                "immutable": True,
                "snapshot_sha256": sha256_json(source_backup),
                "snapshot": source_backup,
                "captured_at": generated_at,
            },
            "preconditions": {
                "expected_stable_repository_id": expected_id,
                "expected_current_head": expected_head,
                "expected_default_branch": item.get("default_branch") or (expected.get("default_branch") if expected else source.get("default_branch")),
                "expected_visibility": expected.get("visibility") if expected else source.get("visibility"),
                "protected_configuration": (
                    {"digest": protection_digest(source), "observed": compact_repo(source).get("protected_configuration")}
                    if isinstance(source.get("protected_configuration"), Mapping) and source.get("protected_configuration", {}).get("available")
                    else None
                ),
            },
            "expected_stable_id_source": "W01 source snapshot" if expected else "live API observation",
            "observed_source": compact_repo(source),
            "observed_target": compact_repo(target),
            "verification": {
                "read_after_write": f"GET /repos/{repo_owner}/{target_name}",
                "stable_id_must_equal": expected_id,
                "name_must_equal": target_name,
                "full_name_must_equal": f"{repo_owner}/{target_name}",
                "source_redirect": "probe only after approved rename; do not recreate old name",
            },
            "rollback": {
                "automatic": False,
                "decision": "forward_fix_or_operator_review",
                "preconditions": [
                    "target still has expected stable repository ID",
                    "source name is available and no unrelated repository owns it",
                    "default branch head and protected configuration are re-read",
                    "Pages custom-domain and hosted-Action callers are reviewed",
                    "separate approval covers the reverse rename",
                ],
            },
        }
        op["preflight"] = evaluate_operation(op, source, target, authorized=False)
        operations.append(op)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "mode": "dry_run",
        "operator": {
            "github_host": "github.com",
            "read_actor": actor or "unknown_until_gh_api_user",
            "owner_notification_authorized": False,
            "external_mutation_authorized": False,
        },
        "github": {
            "api": "REST via gh api",
            "rename_documentation": RENAME_DOCS_URL,
            "rename_limitations": [
                "project-site URLs are an exception to ordinary redirects",
                "GitHub-hosted Actions are not redirected and callers fail until migrated",
                "reusing the old name destroys the ordinary redirect",
            ],
        },
        "source_snapshot": "provided W01 source snapshot" if snapshot else "live API observations",
        "source_snapshot_provenance": (
            snapshot_provenance(snapshot, snapshot_sha256)
            if snapshot is not None
            else {"provided": False, "schema_version": None, "sha256": None}
        ),
        "operations": operations,
    }


def validate_plan(plan: Mapping[str, Any]) -> None:
    if not isinstance(plan, Mapping):
        raise MigrationError("Migration plan must be a JSON object")
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise MigrationError("Unsupported migration plan schema")
    if plan.get("mode") != "dry_run":
        raise MigrationError("Only plan-first dry-run plans can be applied")
    operations = plan.get("operations")
    if not isinstance(operations, list) or not operations:
        raise MigrationError("Migration plan has no operations")
    provenance = plan.get("source_snapshot_provenance")
    if not isinstance(provenance, Mapping) or not isinstance(provenance.get("provided"), bool):
        raise MigrationError("Migration plan has no source snapshot provenance")
    if provenance.get("provided"):
        if not isinstance(provenance.get("schema_version"), str) or not re.fullmatch(r"[a-zA-Z0-9._-]+", provenance["schema_version"]):
            raise MigrationError("Migration plan has invalid source snapshot schema provenance")
        if not isinstance(provenance.get("sha256"), str) or re.fullmatch(r"[0-9a-f]{64}", provenance["sha256"]) is None:
            raise MigrationError("Migration plan has invalid source snapshot digest provenance")
    seen: set[str] = set()
    for op in operations:
        if not isinstance(op, Mapping):
            raise MigrationError("Migration operation is not an object")
        operation_id = op.get("operation_id")
        if not isinstance(operation_id, str) or operation_id in seen:
            raise MigrationError("Migration operation IDs must be unique strings")
        seen.add(operation_id)
        if op.get("action") in RENAME_ACTIONS:
            if op.get("owner") != DEFAULT_OWNER:
                raise MigrationError(f"{operation_id} is outside the approved repository owner scope")
            if not _valid_repo_name(op.get("source_name")):
                raise MigrationError(f"{operation_id} has no source repository name")
            if not _valid_repo_name(op.get("target_name")):
                raise MigrationError(f"{operation_id} has no target repository name")
            preconditions = op.get("preconditions")
            if not isinstance(preconditions, Mapping):
                raise MigrationError(f"{operation_id} has no preconditions")
            stable_id = preconditions.get("expected_stable_repository_id")
            if isinstance(stable_id, bool) or not isinstance(stable_id, int) or stable_id < 1:
                raise MigrationError(f"{operation_id} has no stable-ID precondition")
            for key in ("expected_current_head", "expected_default_branch", "expected_visibility"):
                if not isinstance(preconditions.get(key), str) or not preconditions[key]:
                    raise MigrationError(f"{operation_id} has no {key} precondition")
            reference = op.get("backup_reference")
            if not isinstance(reference, Mapping) or reference.get("immutable") is not True:
                raise MigrationError(f"{operation_id} has no immutable backup reference")
            snapshot = reference.get("snapshot")
            digest = reference.get("snapshot_sha256")
            if not isinstance(snapshot, Mapping) or not isinstance(digest, str) or re.fullmatch(r"[0-9a-f]{64}", digest) is None:
                raise MigrationError(f"{operation_id} has an invalid backup reference")
            if not isinstance(reference.get("kind"), str) or not reference["kind"].strip():
                raise MigrationError(f"{operation_id} has an invalid backup reference kind")
            if sha256_json(snapshot) != digest:
                raise MigrationError(f"{operation_id} backup reference digest is invalid")


def load_approval(path: Path, plan_path: Path, plan: Mapping[str, Any]) -> Mapping[str, Any]:
    approval = read_json(path)
    if not isinstance(approval, Mapping) or approval.get("schema_version") != APPROVAL_SCHEMA_VERSION:
        raise MigrationError("Approval file has an unsupported schema")
    digest = sha256_bytes(plan_path.read_bytes())
    if approval.get("plan_sha256") != digest:
        raise MigrationError("Approval does not match the exact plan bytes")
    if not isinstance(approval.get("approved_by"), str) or not approval.get("approved_by").strip():
        raise MigrationError("Approval must name an approving operator")
    operation_ids = approval.get("operation_ids")
    plan_ids = {op.get("operation_id") for op in plan.get("operations", []) if isinstance(op, Mapping)}
    if not isinstance(operation_ids, list) or not set(operation_ids).issubset(plan_ids):
        raise MigrationError("Approval operation_ids are not a subset of this plan")
    if approval.get("owner_notification_authorized") is not False:
        raise MigrationError("Owner notification is outside this operation and must remain false")
    return approval


def fresh_operation_state(client: Any, op: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    owner = op.get("owner")
    if not isinstance(owner, str):
        raise MigrationError("Operation owner is missing")
    source = client.observe_repo(owner, str(op.get("source_name")))
    target = source if op.get("source_name") == op.get("target_name") else client.observe_repo(owner, str(op.get("target_name")))
    return source, target


def operation_set_lock_path(plan_path: Path, plan_digest: str) -> Path:
    """Return the lock shared by every receipt applying one exact plan."""
    plan_path = Path(plan_path)
    return plan_path.with_name(f".{plan_path.name}.{plan_digest}.operation-set.lock")


def _receipt_repo_identity(value: Any, owner: str, name: str, *, expected_id: int | None = None) -> bool:
    if not isinstance(value, Mapping):
        return False
    if not isinstance(value.get("exists"), bool):
        return False
    if value.get("owner") != owner or value.get("name") != name:
        return False
    if value.get("exists") and value.get("full_name") != f"{owner}/{name}":
        return False
    if expected_id is not None and value.get("id") != expected_id:
        return False
    return True


def _validate_receipt_rows(stored_operations: Any, plan: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(stored_operations, list):
        raise MigrationError("Existing migration receipt has no operation rows")
    plan_operations = {
        op.get("operation_id"): op
        for op in plan.get("operations", [])
        if isinstance(op, Mapping) and isinstance(op.get("operation_id"), str)
    }
    previous: dict[str, Mapping[str, Any]] = {}
    valid_statuses = {
        "applied",
        "already_satisfied",
        "unknown",
        "unknown_waiting_for_reconciliation",
        "verification_failed",
        "dry_run_blocked",
        "dry_run_ready",
        "blocked",
        "skipped",
        "deferred",
    }
    for item in stored_operations:
        if not isinstance(item, Mapping) or not isinstance(item.get("operation_id"), str):
            raise MigrationError("Existing migration receipt has an invalid operation row")
        operation_id = item["operation_id"]
        if operation_id in previous or operation_id not in plan_operations:
            raise MigrationError("Existing migration receipt has duplicate or unknown operation IDs")
        op = plan_operations[operation_id]
        if (
            item.get("owner") != op.get("owner")
            or item.get("source_name") != op.get("source_name")
            or item.get("target_name") != op.get("target_name")
        ):
            raise MigrationError(f"Existing migration receipt identity does not match {operation_id}")
        if item.get("status") not in valid_statuses:
            raise MigrationError(f"Existing migration receipt has no status for {operation_id}")
        if not isinstance(item.get("requested"), bool):
            raise MigrationError(f"Existing migration receipt has no request state for {operation_id}")
        expected_id = op.get("preconditions", {}).get("expected_stable_repository_id")
        for key, expected_name in (("observed_source", op.get("source_name")), ("observed_target", op.get("target_name"))):
            value = item.get(key)
            if value is not None and not _receipt_repo_identity(value, op.get("owner"), expected_name):
                raise MigrationError(f"Existing migration receipt has an invalid {key} for {operation_id}")
            if expected_id is not None and isinstance(value, Mapping) and value.get("exists") and value.get("id") != expected_id:
                raise MigrationError(f"Existing migration receipt has a stale {key} identity for {operation_id}")
        for key in ("response", "verification"):
            if key in item and not isinstance(item.get(key), Mapping):
                raise MigrationError(f"Existing migration receipt has an invalid {key} for {operation_id}")
        if item.get("status") == "applied":
            response = item.get("response")
            if not _receipt_repo_identity(response, op.get("owner"), op.get("target_name"), expected_id=expected_id):
                raise MigrationError(f"Existing migration receipt has an invalid response for {operation_id}")
        previous[operation_id] = item
    return previous


def _receipt_post_state_matches(
    prior: Mapping[str, Any],
    op: Mapping[str, Any],
    source: Mapping[str, Any],
    target: Mapping[str, Any],
) -> bool:
    """Accept a terminal receipt only after matching its fresh full state."""
    operation_id = op.get("operation_id")
    if prior.get("operation_id") != operation_id:
        return False
    status = prior.get("status")
    if status not in {"applied", "already_satisfied"}:
        return False
    if not isinstance(prior.get("requested"), bool):
        return False
    if status == "applied" and prior.get("requested") is not True:
        return False
    if status == "already_satisfied" and prior.get("requested") is not False:
        return False
    owner = op.get("owner")
    source_name = op.get("source_name")
    target_name = op.get("target_name")
    if not all(isinstance(value, str) and value for value in (owner, source_name, target_name)):
        return False
    expected_id = op.get("preconditions", {}).get("expected_stable_repository_id")
    if isinstance(expected_id, bool) or not isinstance(expected_id, int):
        return False
    if prior.get("owner") != owner:
        return False
    if not _receipt_repo_identity(prior.get("observed_source"), owner, source_name):
        return False
    if not _receipt_repo_identity(prior.get("observed_target"), owner, target_name):
        return False
    request = prior.get("request")
    if status == "applied":
        if not isinstance(request, Mapping) or request != {
            "method": "PATCH",
            "path": f"repos/{owner}/{source_name}",
            "body": {"name": target_name},
        }:
            return False
        response = prior.get("response")
        if not _receipt_repo_identity(response, owner, target_name, expected_id=expected_id):
            return False
    elif request is not None:
        return False
    verification = prior.get("verification")
    if not isinstance(verification, Mapping):
        return False
    expected_name = target_name
    expected_full_name = f"{owner}/{expected_name}"
    if not (
        target.get("exists")
        and target.get("id") == expected_id
        and target.get("name") == expected_name
        and target.get("full_name") == expected_full_name
    ):
        return False
    current = compact_repo(target)
    if dict(verification) != current:
        return False
    if not isinstance(prior.get("post_state_sha256"), str) or prior.get("post_state_sha256") != sha256_json(current):
        return False
    # A successful rename leaves the old name absent.  If a later observation
    # still resolves it, the receipt is not a safe success oracle.
    if source.get("exists") is not False:
        return False
    return True


def _merge_receipt_rows(
    previous: Mapping[str, Mapping[str, Any]],
    results: Iterable[Mapping[str, Any]],
    plan: Mapping[str, Any],
) -> list[dict[str, Any]]:
    merged: dict[str, Mapping[str, Any]] = dict(previous)
    for row in results:
        if isinstance(row.get("operation_id"), str):
            merged[row["operation_id"]] = row
    ordered: list[dict[str, Any]] = []
    seen: set[str] = set()
    for op in plan.get("operations", []):
        operation_id = op.get("operation_id") if isinstance(op, Mapping) else None
        if isinstance(operation_id, str) and operation_id in merged:
            ordered.append(dict(merged[operation_id]))
            seen.add(operation_id)
    ordered.extend(dict(row) for operation_id, row in merged.items() if operation_id not in seen)
    return ordered


def _approval_actor_login(client: Any) -> str:
    current_user = getattr(client, "current_user", None)
    actor = current_user() if callable(current_user) else None
    login = actor.get("login") if isinstance(actor, Mapping) else None
    if not isinstance(login, str) or not login.strip():
        raise MigrationError("Remote apply requires an authenticated GitHub actor")
    return login.strip()


def _validate_approval_scope(approval: Mapping[str, Any], plan: Mapping[str, Any], client: Any) -> None:
    actor_login = _approval_actor_login(client)
    if approval.get("approved_by") != actor_login:
        raise MigrationError("Approval actor does not match the authenticated GitHub actor")
    rename_ids = {
        str(op.get("operation_id"))
        for op in plan.get("operations", [])
        if isinstance(op, Mapping) and op.get("action") in RENAME_ACTIONS
    }
    approved_ids = approval.get("operation_ids")
    if not isinstance(approved_ids, list) or not rename_ids.issubset(set(approved_ids)):
        raise MigrationError("Approval does not cover every rename operation in the plan")
    for op in plan.get("operations", []):
        if isinstance(op, Mapping) and op.get("action") in RENAME_ACTIONS and op.get("owner") != DEFAULT_OWNER:
            raise MigrationError("Approval includes a repository outside the approved owner scope")


def apply_plan(
    plan, client, *, plan_path, receipt_path, approval=None, apply=False, retry_unknown=False,
):
    """Serialize one operation-set read/check/request cycle."""
    plan_path = Path(plan_path)
    receipt_path = Path(receipt_path)
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    plan_digest = sha256_bytes(plan_path.read_bytes())
    operation_lock = operation_set_lock_path(plan_path, plan_digest)
    receipt_lock = receipt_path.with_name(receipt_path.name + '.lock')
    try:
        operation_handle = operation_lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise MigrationError('Operation set is locked; reconcile the owning process before removing its lock') from exc
    try:
        with operation_handle:
            operation_handle.write(str(os.getpid()) + '\n')
            operation_handle.flush()
            os.fsync(operation_handle.fileno())
        try:
            receipt_handle = receipt_lock.open('x', encoding='utf-8')
        except FileExistsError as exc:
            raise MigrationError('Receipt is locked; reconcile the owning process before removing its lock') from exc
        try:
            with receipt_handle:
                receipt_handle.write(str(os.getpid()) + '\n')
                receipt_handle.flush()
                os.fsync(receipt_handle.fileno())
            return _apply_plan(plan, client, plan_path=plan_path, receipt_path=receipt_path,
                               approval=approval, apply=apply, retry_unknown=retry_unknown)
        finally:
            receipt_lock.unlink(missing_ok=True)
    finally:
        operation_lock.unlink(missing_ok=True)


def _apply_plan(
    plan: Mapping[str, Any],
    client: Any,
    *,
    plan_path: Path,
    receipt_path: Path,
    approval: Mapping[str, Any] | None = None,
    apply: bool = False,
    retry_unknown: bool = False,
) -> dict[str, Any]:
    validate_plan(plan)
    if apply and approval is None:
        raise MigrationError("Remote apply requires an approval file; dry run remains the default")
    plan_digest = sha256_bytes(plan_path.read_bytes())
    if read_json(plan_path) != plan:
        raise MigrationError("In-memory plan differs from exact plan bytes")
    if apply and approval.get('plan_sha256') != plan_digest:
        raise MigrationError("Approval does not match the exact plan bytes")
    if apply:
        _validate_approval_scope(approval, plan, client)
    approved_ids = set(approval.get("operation_ids", [])) if approval else set()
    previous: dict[str, Any] = {}
    if receipt_path.exists():
        value = read_json(receipt_path)
        if not isinstance(value, Mapping) or value.get("schema_version") != RECEIPT_SCHEMA_VERSION:
            raise MigrationError("Existing migration receipt has an unsupported schema")
        if value.get('plan_sha256') != plan_digest:
            raise MigrationError('Existing receipt belongs to a different plan')
        previous = _validate_receipt_rows(value.get("operations"), plan)

    results: list[dict[str, Any]] = []

    def persist_pending(rows):
        # Preserve prior later-operation receipts during an interrupted pass.
        write_json(receipt_path, {
            'schema_version': RECEIPT_SCHEMA_VERSION,
            'plan_sha256': plan_digest,
            'mode': 'apply' if apply else 'dry_run',
            'recorded_at': utc_now(),
            'operator': {'approved_by': approval.get('approved_by') if approval else None,
                         'owner_notification_sent': False},
            'operations': _merge_receipt_rows(previous, rows, plan),
        })
    for op in plan["operations"]:
        if not isinstance(op, Mapping):
            continue
        operation_id = str(op["operation_id"])
        action = op.get("action")
        prior = previous.get(operation_id)
        if prior and prior.get("status") in {"unknown", "unknown_waiting_for_reconciliation", "verification_failed"} and not retry_unknown:
            result = dict(prior)
            result["status"] = "unknown_waiting_for_reconciliation"
            results.append(result)
            persist_pending(results)
            break
        source, target = fresh_operation_state(client, op)
        if prior and prior.get("status") in {"applied", "already_satisfied"}:
            if _receipt_post_state_matches(prior, op, source, target):
                results.append(dict(prior))
                continue
        evaluation = evaluate_operation(op, source, target, authorized=operation_id in approved_ids)
        result: dict[str, Any] = {
            "operation_id": operation_id,
            "owner": op.get("owner"),
            "source_name": op.get("source_name"),
            "target_name": op.get("target_name"),
            "requested": False,
            "attempt": int(prior.get("attempt", 0)) + 1 if prior else 1,
            "observed_at": utc_now(),
            "preflight": evaluation,
            "observed_source": compact_repo(source),
            "observed_target": compact_repo(target),
        }
        if evaluation.get("status") == "already_satisfied":
            result["status"] = "already_satisfied"
            result["verification"] = compact_repo(target)
            result["post_state_sha256"] = sha256_json(result["verification"])
            results.append(result)
            continue
        if action in KEEP_ACTIONS:
            result["status"] = "skipped"
            results.append(result)
            continue
        if action in DEFERRED_ACTIONS:
            result["status"] = "deferred"
            results.append(result)
            continue
        if not apply:
            result["status"] = "dry_run_blocked" if evaluation.get("status") != "ready" else "dry_run_ready"
            results.append(result)
            continue
        if evaluation.get("status") != "ready":
            result["status"] = "blocked"
            results.append(result)
            continue
        rename_method = getattr(client, "rename_repo", None)
        if not callable(rename_method):
            raise MigrationError("The selected client cannot apply a rename")
        result["requested"] = True
        result["request"] = {
            "method": "PATCH",
            "path": f"repos/{op['owner']}/{op['source_name']}",
            "body": {"name": op["target_name"]},
        }
        result['status'] = 'unknown'
        result['rollback_decision'] = 'do_not_rollback_automatically'
        persist_pending(results + [result])
        try:
            response = rename_method(str(op["owner"]), str(op["source_name"]), str(op["target_name"]))
            result["response"] = compact_repo(response if isinstance(response, Mapping) else {})
        except (ApiError, TimeoutError, ConnectionError, OSError) as exc:
            # Any ambiguous post-request transport result is unknown: do not
            # call PATCH a second time without explicit reconciliation.
            ambiguous = not isinstance(exc, ApiError) or exc.ambiguous
            result["status"] = "unknown" if ambiguous else "failed"
            result["error"] = str(exc)[:400]
            result["rollback_decision"] = "do_not_rollback_automatically"
            results.append(result)
            persist_pending(results)
            if result["status"] == "unknown":
                break
            continue
        try:
            verified = client.observe_repo(str(op["owner"]), str(op["target_name"]))
        except MigrationError as exc:
            result["status"] = "verification_failed"
            result["verification_error"] = str(exc)[:400]
            result["rollback_decision"] = "do_not_rollback_automatically"
            result["rollback_preconditions"] = op.get("rollback", {}).get("preconditions", [])
            results.append(result)
            persist_pending(results)
            break
        result["verification"] = compact_repo(verified)
        result["post_state_sha256"] = sha256_json(result["verification"])
        if (
            verified.get("exists")
            and verified.get("id") == op["preconditions"].get("expected_stable_repository_id")
            and verified.get("name") == op.get("target_name")
            and verified.get("full_name") == f"{op.get('owner')}/{op.get('target_name')}"
        ):
            result["status"] = "applied"
            result["rollback_decision"] = "forward_state_verified"
        else:
            result["status"] = "verification_failed"
            result["rollback_decision"] = "do_not_rollback_automatically"
            result["rollback_preconditions"] = op.get("rollback", {}).get("preconditions", [])
        results.append(result)
        persist_pending(results)
        if result["status"] == "verification_failed":
            break

    receipt = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "plan_sha256": sha256_bytes(plan_path.read_bytes()),
        "mode": "apply" if apply else "dry_run",
        "recorded_at": utc_now(),
        "operator": {
            "approved_by": approval.get("approved_by") if approval else None,
            "owner_notification_sent": False,
        },
        "operations": _merge_receipt_rows(previous, results, plan),
    }
    if apply or results:
        write_json(receipt_path, receipt)
    return receipt


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--owner", default=DEFAULT_OWNER)
    parser.add_argument("--api-executable", default="gh")
    parser.add_argument("--host", default="github.com")
    parser.add_argument("--snapshot", type=Path, help="Immutable W01 snapshot; selecting it makes reads offline")


def make_client(args: argparse.Namespace) -> Any:
    snapshot = load_snapshot(args.snapshot)
    return SnapshotClient(snapshot) if snapshot is not None else GhApi(executable=args.api_executable, host=args.host)


def command_plan(args: argparse.Namespace) -> dict[str, Any]:
    repository_map = load_map(args.map)
    snapshot = load_snapshot(args.snapshot)
    client = SnapshotClient(snapshot) if snapshot is not None else GhApi(executable=args.api_executable, host=args.host)
    plan = build_plan(
        repository_map,
        client,
        owner=args.owner,
        snapshot=snapshot,
        observed_at=args.observed_at,
        snapshot_sha256=sha256_bytes(args.snapshot.read_bytes()) if args.snapshot else None,
    )
    write_json(args.output, plan)
    return {"output": str(args.output), "plan_sha256": sha256_bytes(args.output.read_bytes()), "operations": len(plan["operations"]), "mode": "dry_run"}


def command_apply(args: argparse.Namespace) -> dict[str, Any]:
    plan = read_json(args.plan)
    if not isinstance(plan, Mapping):
        raise MigrationError("Plan must be a JSON object")
    validate_plan(plan)
    approval = None
    if args.approval:
        approval = load_approval(args.approval, args.plan, plan)
    if args.apply and args.snapshot:
        raise MigrationError("Remote apply cannot use an offline snapshot")
    client = make_client(args)
    return apply_plan(plan, client, plan_path=args.plan, receipt_path=args.receipt, approval=approval, apply=args.apply, retry_unknown=args.retry_unknown)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan", help="read current state and write a dry-run plan")
    plan.add_argument("--map", type=Path, required=True)
    plan.add_argument("--output", type=Path, required=True)
    plan.add_argument("--observed-at")
    add_common(plan)
    apply_parser = sub.add_parser("apply", help="re-read and optionally apply a plan")
    apply_parser.add_argument("--plan", type=Path, required=True)
    apply_parser.add_argument("--receipt", type=Path, required=True)
    apply_parser.add_argument("--approval", type=Path)
    apply_parser.add_argument("--apply", action="store_true", help="required to send PATCH; still requires --approval")
    apply_parser.add_argument("--retry-unknown", action="store_true", help="reconcile an unknown prior attempt before retrying")
    add_common(apply_parser)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = command_plan(args) if args.command == "plan" else command_apply(args)
    except (MigrationError, OSError, TypeError, ValueError) as exc:
        print(f"migration refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
