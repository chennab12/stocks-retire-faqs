"""Smoke tests: every section and calculator renders, and the main interactions work."""
from streamlit.testing.v1 import AppTest

from content import CATEGORIES


def run(section=None):
    at = AppTest.from_file("../app.py", default_timeout=30)
    if section is not None:
        at.session_state["section"] = section
    at.run()
    assert not at.exception, at.exception
    return at


def test_every_section_renders():
    at = run()
    for section in at.sidebar.radio[0].options:
        run(section)


def test_every_page_ends_with_a_mistakes_table():
    for section in run().sidebar.radio[0].options:
        if section in ("🔎 Search everything", "📝 Quiz center"):
            continue
        at = run(section)
        assert any("Common mistakes" in h.value for h in at.subheader), section


def test_every_calculator_renders():
    at = run("🧮 Calculators")
    options = at.button_group[0].options
    assert len(options) == 16
    for option in options:
        at.button_group[0].set_value(option).run()
        assert not at.exception, (option, at.exception)


def test_next_category_button_advances():
    at = run(CATEGORIES[0]["name"])
    [b for b in at.button if b.label == "Next category →"][0].click().run()
    assert at.session_state["section"] == CATEGORIES[1]["name"]


def test_related_calculator_button_opens_it():
    at = run(CATEGORIES[0]["name"])
    [b for b in at.button if b.label == "🛟 Emergency fund"][0].click().run()
    assert at.session_state["section"] == "🧮 Calculators"
    assert at.session_state["calc"] == "🛟 Emergency fund"
    assert not at.exception


def test_habit_checkbox_updates_score():
    at = run()
    at.checkbox(key="habit_0").check().run()
    assert any(m.label == "This month's habits" and m.value.startswith("1 /") for m in at.metric)


def test_topic_toggle_marks_done():
    at = run(CATEGORIES[0]["name"])
    title = CATEGORIES[0]["topics"][0]["title"]
    at.toggle(key="done_" + title).set_value(True).run()
    assert title in at.session_state["done"]


def test_search_finds_topic_and_limit():
    at = run("🔎 Search everything")
    at.text_input[0].input("backdoor").run()
    assert any("Backdoor Roth IRA" in m.value for m in at.markdown)
    at.text_input[0].input("ESPP purchase cap").run()
    assert any("$25,000" in m.value for m in at.markdown)


def test_quiz_submits():
    at = run("📝 Quiz center")
    at.button(key="FormSubmitter:quiz-✅ Check my answers").click().run()
    assert not at.exception, at.exception
    assert any(m.label == "Score" for m in at.metric)


def test_checkup_points_to_next_rung():
    at = run("🧭 Money checkup & year planner")
    assert any("Next rung" in s.value and "debt" not in s.value for s in at.success)
    at.checkbox(key="ck_debt").check().run()
    assert any("No high-interest debt" in s.value for s in at.success)


def test_tax_estimator_shows_marginal_rates():
    at = run("🧮 Calculators")
    at.button_group[0].set_value("🧾 Tax bracket estimator").run()
    assert any(m.label == "Marginal rate (fed + CA)" and m.value == "24% + 9.3%" for m in at.metric)


def test_deep_link_opens_section():
    at = AppTest.from_file("../app.py", default_timeout=30)
    at.query_params["page"] = "iras-hsa"
    at.run()
    assert at.session_state["section"] == "🪙 IRAs & HSA"
