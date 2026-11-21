import json

from check_release_content import pending_reviews


def test_pending_review_does_not_disappear_when_source_url_is_repaired(tmp_path):
    state = tmp_path / "ut"
    state.mkdir()
    config = {
        "code": "ut",
        "manual_url": "https://dld.utah.gov/current.pdf",
        "content_review_required": True,
        "content_review_note": "Different source bytes",
    }
    (state / "config.json").write_text(json.dumps(config))
    assert pending_reviews(tmp_path) == [("ut", "Different source bytes")]
    config["content_review_required"] = False
    (state / "config.json").write_text(json.dumps(config))
    assert pending_reviews(tmp_path) == []


def test_legacy_configs_without_a_review_flag_keep_working(tmp_path):
    state = tmp_path / "nj"
    state.mkdir()
    (state / "config.json").write_text(json.dumps({"code": "nj"}))
    assert pending_reviews(tmp_path) == []
