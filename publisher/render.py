"""Deterministic, escaping-only HTML rendering for approved records."""

from __future__ import annotations

import html
from typing import Any

from .security import safe_public_url


def _text(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _link(label: str, url: str | None) -> str:
    if not url:
        return "<span class=\"unavailable\">Unavailable</span>"
    safe_public_url(url)
    return f'<a href="{_text(url)}" rel="noreferrer">{_text(label)}</a>'


def _status(manifest: dict[str, Any]) -> tuple[str, str]:
    if manifest["classification"] == "synthetic":
        return "synthetic", "Synthetic fixture — local test only"
    availability = manifest["evidence"]["availability"]
    labels = {
        "none": "No public evidence media",
        "report_only": "Report only",
        "video": "Video available",
        "replay_package": "Replay package available",
        "video_and_replay": "Video and replay package available",
    }
    return availability, labels[availability]


def render_html(manifest: dict[str, Any]) -> str:
    """Render one manifest using only static templates and escaped values."""

    _, status_label = _status(manifest)
    evidence = manifest["evidence"]
    source = manifest["source"]
    source_refs = "".join(
        f"<li>{_text(reference['label'])} · {_text(reference['revision'])} · "
        f"{_link('source', reference['uri'])}</li>"
        for reference in source["references"]
    )
    timeline = manifest["action_timeline"]
    rows: list[str] = []
    for decision in timeline["decisions"]:
        choices = ", ".join(_text(choice) for choice in decision["legal_choices"]) or "Unavailable"
        state = decision["state_summary"] if decision["state_visibility"] == "approved" else "Redacted"
        explanation = "Unavailable"
        if decision["explanation"]:
            explanation = (
                f"{_text(decision['explanation']['text'])} "
                f"<small>({_text(decision['explanation']['kind'])})</small>"
            )
        rows.append(
            "<tr>"
            f"<td>{_text(decision['sequence'])}</td>"
            f"<td>{_text(decision['floor']) if decision['floor'] is not None else '—'}</td>"
            f"<td>{_text(state)}</td>"
            f"<td>{choices}</td>"
            f"<td>{_text(decision['chosen_action']) if decision['chosen_action'] is not None else 'Unavailable'}</td>"
            f"<td>{_text(decision['observed_consequence']) if decision['observed_consequence'] is not None else 'Unavailable'}</td>"
            f"<td>{explanation}</td>"
            "</tr>"
        )
    timeline_body = (
        "<table><thead><tr><th>Step</th><th>Floor</th><th>Observed state</th><th>Legal choices</th>"
        "<th>Recorded action</th><th>Consequence</th><th>Explanation provenance</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        if rows
        else "<p class=\"unavailable\">Decision timeline unavailable.</p>"
    )

    local_guess = manifest["local_guess_reveal"]
    if local_guess["status"] == "available" and timeline["decisions"]:
        first = timeline["decisions"][0]
        options = []
        for position, choice in enumerate(first["legal_choices"]):
            options.append(
                f'<label><input type="radio" name="local-guess" value="{_text(position)}"> '
                f"{_text(choice)}</label>"
            )
        guess_html = (
            "<section id=\"your-move\"><h2>Your move</h2>"
            "<p>Choose locally, then open the reveal. This is not a community poll and has no aggregate count.</p>"
            f"<fieldset><legend>What should the agent do?</legend>{''.join(options)}</fieldset>"
            "<details><summary>Reveal the recorded decision</summary>"
            f"<p>{_text(first['chosen_action']) if first['chosen_action'] is not None else 'Unavailable'}</p>"
            "</details></section>"
        )
    else:
        guess_html = "<section id=\"your-move\"><h2>Your move</h2><p class=\"unavailable\">Local decision interaction unavailable.</p></section>"

    case_study = manifest["case_study"]
    case_html = ""
    if case_study["status"] == "published":
        case_html = (
            "<section><h2>Case study</h2>"
            f"<p>{_text(case_study['summary'])}</p>"
            f"<p>Source: {_text(case_study['source_reference'])}</p></section>"
        )

    model = manifest["model_configuration"]
    game = manifest["game_configuration"]
    budget = manifest["resource_budget"]
    intervention = manifest["intervention"]
    disclosures = "".join(f"<li>{_text(item)}</li>" for item in manifest["disclosures"])
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{_text(manifest['title'])} · AI Ascension</title>"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<style>"
        ":root{color-scheme:light dark;--paper:#f6f0e4;--ink:#211f1a;--amber:#a86620;--muted:#706b61}"
        "body{margin:0;padding:2rem;max-width:72rem;margin-inline:auto;font:16px/1.5 system-ui,sans-serif;background:var(--paper);color:var(--ink)}"
        "a{color:var(--amber)}main{display:grid;gap:1.5rem}section{border:1px solid color-mix(in srgb,var(--ink) 20%,transparent);padding:1rem;border-radius:.4rem}"
        ".eyebrow{color:var(--amber);font-weight:700;letter-spacing:.08em;text-transform:uppercase}.unavailable{color:var(--muted)}"
        ".notice{border-left:.35rem solid var(--amber);padding:.65rem 1rem;background:color-mix(in srgb,var(--amber) 12%,transparent)}"
        "table{border-collapse:collapse;width:100%;font-size:.92rem}th,td{border-bottom:1px solid color-mix(in srgb,var(--ink) 20%,transparent);padding:.5rem;text-align:left;vertical-align:top}"
        "fieldset{display:grid;gap:.5rem;border:0;padding:0}details{margin-top:1rem}small{color:var(--muted)}"
        "@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}@media (max-width:50rem){body{padding:1rem;overflow-wrap:anywhere}table{display:block;overflow:auto;white-space:normal}}"
        "</style></head><body><main>"
        f"<header><p class=\"eyebrow\">AI Ascension · Run report</p><h1>{_text(manifest['title'])}</h1>"
        f"<p class=\"notice\"><strong>{_text(status_label)}</strong> · Outcome: {_text(manifest['outcome'])}</p></header>"
        "<section><h2>Run context</h2><dl>"
        f"<dt>Public run ID</dt><dd>{_text(manifest['public_run_id'])}</dd>"
        f"<dt>Recorded at</dt><dd>{_text(manifest['recorded_at']) if manifest['recorded_at'] else 'Unavailable'}</dd>"
        f"<dt>Model</dt><dd>{_text(model['identifier'])} · {_text(model['revision'])}</dd>"
        f"<dt>Game build</dt><dd>{_text(game['game'])} · {_text(game['build'])}</dd>"
        f"<dt>Platform</dt><dd>{_text(game.get('platform', 'unknown'))}</dd>"
        f"<dt>Mod revision</dt><dd>{_text(game['mod_revision'])}</dd>"
        f"<dt>Harness revision</dt><dd>{_text(game['harness_revision'])}</dd>"
        f"<dt>Observation policy</dt><dd>{_text(manifest['observation_policy'])}</dd>"
        f"<dt>Seed policy</dt><dd>{_text(manifest['seed_policy'])}</dd>"
        f"<dt>Budget</dt><dd>{_text(budget['description'])}</dd>"
        f"<dt>Measured provider calls</dt><dd>{_text(budget['provider_calls']) if budget['provider_calls'] is not None else 'Not measured'}</dd>"
        f"<dt>Intervention</dt><dd>{_text(intervention['summary'])}</dd>"
        "</dl></section>"
        "<section><h2>Evidence</h2>"
        f"<p>{_text(status_label)}. Rights status: {_text(evidence['rights_status'])}. Caption support: {_text(evidence['caption_support'])}.</p>"
        f"<p>{_link('Open video', evidence['video_url'])} · {_link('Download replay package', evidence['replay_url'])}</p>"
        f"<p>Evidence reference: {_link(evidence['evidence_reference'] or 'Unavailable', evidence['evidence_reference'])}</p>"
        f"<p>Observed fields: {_text(', '.join(manifest['evidence_context']['observed_fields']) or 'None')}</p>"
        f"<p>Redacted fields: {_text(', '.join(manifest['evidence_context']['redacted_fields']) or 'None')}</p></section>"
        "<section><h2>Lineage</h2>"
        f"<p>Source record: {_text(source['record_id'])} · revision {_text(source['revision'])}</p>"
        f"<p>Source content digest: <code>{_text(source['content_digest'])}</code></p>"
        f"<ul>{source_refs}</ul>"
        f"<p>Decision card: {_text(manifest['decision_card']['status'])}"
        f"{(' · ' + _text(manifest['decision_card']['asset_id']) + ' · ' + _text(manifest['decision_card']['artifact_digest'])) if manifest['decision_card']['status'] == 'available' else ''}</p></section>"
        f"<section><h2>Decision timeline</h2>{timeline_body}</section>"
        f"{guess_html}{case_html}"
        f"<section><h2>Disclosures</h2><ul>{disclosures}</ul></section>"
        "</main></body></html>\n"
    )
