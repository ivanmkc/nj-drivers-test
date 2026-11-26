import json

import setup_state


def test_refresh_preserves_language_evidence_and_content_review_hold(tmp_path):
    state = tmp_path / "ar"
    state.mkdir()
    (state / "config.json").write_text(
        json.dumps(
            {
                "code": "ar",
                "official_test_languages": ["English"],
                "official_test_languages_evidence": ["Evidence kept from the source"],
                "content_review_required": True,
            }
        )
    )
    setup_state._write_config(
        str(state),
        {
            "code": "ar",
            "name": "Arkansas",
            "agency": "ASP",
            "manual_url": "https://example.gov/current.pdf",
            "passing_score_pct": 80,
            "test_question_count": 25,
        },
    )
    refreshed = json.loads((state / "config.json").read_text())
    assert refreshed["content_review_required"] is True
    assert refreshed["official_test_languages"] == ["English"]
    assert refreshed["official_test_languages_evidence"] == ["Evidence kept from the source"]
    assert refreshed["manual_url"] == "https://example.gov/current.pdf"
