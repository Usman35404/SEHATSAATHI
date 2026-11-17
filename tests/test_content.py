"""
Tests for curated public-health content integrity (content/topics.json).
"""

from pathlib import Path
import pytest

from app import get_topic_by_id, load_topics_catalog, summarize_topic_for_client


def test_topics_catalog_loads_two_valid_topics():
    topics = load_topics_catalog()
    assert isinstance(topics, list)
    assert len(topics) >= 2
    ids = {t["id"] for t in topics}
    assert "handwashing" in ids
    assert "sleep" in ids


def test_topics_have_authoritative_https_sources_and_bilingual_titles():
    topics = load_topics_catalog()
    for topic in topics:
        assert topic["title_en"].strip()
        assert topic["title_ur"].strip()
        assert topic["summary_en"].strip()
        assert topic["source_title"].startswith("CDC")
        assert topic["source_url"].startswith("https://www.cdc.gov/")
        assert isinstance(topic["facts"], list)
        assert len(topic["facts"]) >= 4
        for fact in topic["facts"]:
            assert isinstance(fact, str)
            assert len(fact.strip()) >= 20


def test_get_topic_by_id_allowlist_only():
    assert get_topic_by_id("handwashing") is not None
    assert get_topic_by_id("HANDWASHING")["id"] == "handwashing"
    assert get_topic_by_id("sleep")["id"] == "sleep"
    assert get_topic_by_id("unknown-topic") is None
    assert get_topic_by_id("") is None
    assert get_topic_by_id("https://evil.example.com") is None


def test_summarize_topic_for_client_excludes_internal_facts():
    topic = get_topic_by_id("handwashing")
    summary = summarize_topic_for_client(topic)
    assert summary["id"] == "handwashing"
    assert "facts" not in summary
    assert summary["source_url"] == "https://www.cdc.gov/clean-hands/about/"


def test_invalid_catalog_rejected(tmp_path: Path):
    bad_file = tmp_path / "bad_topics.json"
    bad_file.write_text('[{"id": "only_one"}]', encoding="utf-8")
    with pytest.raises(ValueError):
        load_topics_catalog(bad_file)
