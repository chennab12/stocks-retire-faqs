"""Content checks: every topic is complete, consistent and only links to trusted sources."""
from urllib.parse import urlparse

from content import ALLOWED_DOMAINS, CATEGORIES, FAST_TRACK, LIMITS, MONTHLY_HABITS, PLAN_12_WEEKS, SOURCES

TOPIC_FIELDS = {"icon", "title", "gist", "purpose", "plain", "example", "target", "insights", "tips", "do", "dont",
                "actions", "experiment", "metric", "quiz", "sources"}
TITLES = {c["title"] for c in CATEGORIES}


def test_fourteen_categories_with_full_topics():
    assert len(CATEGORIES) == 14
    for c in CATEGORIES:
        assert len(c["numbers"]) == 4 and len(c["kpis"]) >= 3 and len(c["mistakes"]) >= 3, c["title"]
        assert len(c["topics"]) >= 3, c["title"]
        for t in c["topics"]:
            assert set(t) == TOPIC_FIELDS, (t["title"], set(t) ^ TOPIC_FIELDS)
            assert len(t["insights"]) == 3 and len(t["tips"]) == 3 and len(t["do"]) == 3 and len(t["dont"]) == 3
            assert [w for w, _ in t["actions"]] == ["Today", "This week", "This month"]
            assert len(t["quiz"]) == 2 and len(t["sources"]) >= 1


def test_quiz_answers_are_valid_and_options_unique():
    for c in CATEGORIES:
        for t in c["topics"]:
            for item in t["quiz"]:
                assert 0 <= item["answer"] < len(item["options"]) == 4, item["q"]
                assert len(set(item["options"])) == 4, item["q"]


def test_titles_are_unique():
    titles = [t["title"] for c in CATEGORIES for t in c["topics"]]
    assert len(titles) == len(set(titles))


def test_every_cited_source_exists():
    for c in CATEGORIES:
        for t in c["topics"]:
            for name in t["sources"]:
                assert name in SOURCES, (t["title"], name)
    for *_, name in LIMITS:
        assert name in SOURCES, name


def test_links_only_go_to_trusted_sources():
    for name, url in SOURCES.items():
        host = urlparse(url).hostname
        assert url.startswith("https://"), name
        assert any(host.endswith(d) for d in ALLOWED_DOMAINS), (name, host)


def test_habits_plan_and_fast_track_point_at_real_categories():
    for _, _, cat in MONTHLY_HABITS + FAST_TRACK:
        assert cat in TITLES, cat
    assert [w for w, *_ in PLAN_12_WEEKS] == list(range(1, 13))
    assert all(cat in TITLES for *_, cat in PLAN_12_WEEKS)


def test_no_return_promises_or_hype():
    text = str(CATEGORIES).lower()
    for phrase in ["will double your money", "can't lose", "risk-free return", "get rich quick", "to the moon", "buy now"]:
        assert phrase not in text, phrase
