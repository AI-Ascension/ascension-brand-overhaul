"""Synthetic collection metadata; never a real independent review."""


def capability_envelope(records):
    return {
        "schema_version": "ai-ascension.capabilities.v1",
        "collected_at": "2026-09-07",
        "source_snapshot": "synthetic/source-snapshot.json",
        "baseline_package_revision": "a" * 40,
        "review_boundary": {
            "collector_role": "synthetic",
            "collector_thread_id": "synthetic-thread",
            "independent_reviewer": None,
            "independent_review_status": "test_only",
            "interpretation": "Synthetic metadata for local tests only",
        },
        "claim_policy": {
            "verified_win": False,
            "current_public_video": False,
            "current_public_replay_package": False,
            "live_autonomous_service": False,
            "native_multiplayer": False,
            "trademark_clearance": False,
            "unsupported_claims_to_avoid": ["Production approval"],
        },
        "capabilities": records,
    }
