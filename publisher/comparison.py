"""Comparison-context contract and renderer."""

from __future__ import annotations

import html
from typing import Any

from .schema import validate_comparison_schema


def validate_comparison(comparison: dict[str, Any]) -> dict[str, Any]:
    validate_comparison_schema(comparison)
    ids = [run["public_run_id"] for run in comparison["runs"]]
    if len(ids) != len(set(ids)):
        raise ValueError("comparison contains duplicate public run IDs")
    rules = comparison["rules"]
    if rules["ranking_claims_allowed"] is not False:
        raise ValueError("comparison ranking claims must remain disabled")
    fields = {
        "same_game_build": "game_build",
        "same_seed_policy": "seed_policy",
        "same_observation_policy": "observation_policy",
        "same_action_interface": "action_interface",
        "same_budget": "budget",
    }
    for rule, field in fields.items():
        if rules[rule] and len({run[field] for run in comparison["runs"]}) != 1:
            raise ValueError(f"{rule} is true but {field} differs")
    if comparison["comparison_kind"] == "same_start" and not rules["same_start_required"]:
        raise ValueError("same_start comparison must require the same start")
    if comparison["comparison_kind"] == "same_start" and not rules["interventions_declared"]:
        raise ValueError("same_start comparison must declare interventions")
    return comparison


def render_comparison(comparison: dict[str, Any]) -> str:
    validate_comparison(comparison)
    esc = lambda value: html.escape(str(value), quote=True)
    rows = "".join(
        "<tr>"
        f"<th scope=\"row\">{esc(run['label'])}</th>"
        f"<td>{esc(run['public_run_id'])}</td>"
        f"<td>{esc(run['game_build'])}</td>"
        f"<td>{esc(run['seed_policy'])}</td>"
        f"<td>{esc(run['observation_policy'])}</td>"
        f"<td>{esc(run['action_interface'])}</td>"
        f"<td>{esc(run['budget'])}</td>"
        f"<td>{esc(run['retry_policy'])}</td>"
        f"<td>{esc(run['intervention_policy'])}</td>"
        "</tr>"
        for run in comparison["runs"]
    )
    limitations = "".join(f"<li>{esc(item)}</li>" for item in comparison["limitations"])
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\"><title>Comparison · AI Ascension</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"></head><body><main>"
        f"<h1>{esc(comparison['title'])}</h1><p>Comparison kind: {esc(comparison['comparison_kind'])}.</p>"
        "<p>Context only. This view does not rank intelligence or infer a benchmark from a convenience sample.</p>"
        "<table><thead><tr><th>Run</th><th>Public ID</th><th>Game build</th><th>Seed policy</th>"
        "<th>Observation</th><th>Action interface</th><th>Budget</th><th>Retries</th><th>Interventions</th></tr></thead>"
        f"<tbody>{rows}</tbody></table><h2>Limitations</h2><ul>{limitations}</ul>"
        "</main></body></html>\n"
    )


__all__ = ["validate_comparison", "render_comparison"]
