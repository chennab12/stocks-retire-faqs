import math

from calculations import (
    CA_BRACKETS, FED_BRACKETS, after_tax_room, bracket_tax, college_plan, concentration, employer_match, espp, fee_drag,
    fi_number, future_value, household_taxes, k401_employee_limit, life_insurance_need, marginal_rate, milestones,
    money_ladder, money_lasts, months_to_target, quiz_score, real_rate, rebalance, roth_vs_traditional, rsu_tax_gap,
    shuffled_options, ss_break_even, ss_factor, years_to_fi,
)


def test_future_value_and_real_rate():
    assert round(future_value(1000, 0, 0.12, 1)) == round(1000 * 1.01 ** 12)
    assert future_value(0, 100, 0, 2) == 2400
    assert round(future_value(0, 1000, 0.07, 25), -3) == 810_000
    assert round(real_rate(0.07, 0.03), 4) == 0.0388
    f = fee_drag(500_000, 0, 0.07, 30, 0.0003, 0.01)
    assert f["low"] > f["high"] and 0.2 < f["cost"] / f["low"] < 0.3


def test_fi_and_years():
    assert fi_number(140_000, 60_000) == 2_000_000
    assert fi_number(50_000, 60_000) == 0
    assert round(years_to_fi(0.25)) == 32 and round(years_to_fi(0.5)) == 17
    assert months_to_target(100, 0, 0.05, 50) == 0
    assert months_to_target(0, 1000, 0, 12_000) == 12
    assert months_to_target(0, 1, 0, 10**9) is None
    years, path = money_lasts(1_000_000, 100_000, 0)
    assert years == 10 and path[0] == 1_000_000
    assert money_lasts(1_000_000, 30_000, 0.04)[0] is None


def test_401k_limits_and_match():
    assert k401_employee_limit(40) == 24_500 and k401_employee_limit(52) == 32_500 and k401_employee_limit(61) == 35_750
    m = employer_match(220_000, 0.08, 0.5, 0.08)
    assert m["yours"] == 17_600 and m["match"] == 8_800 and m["max_match"] == 8_800
    assert employer_match(220_000, 0.04, 0.5, 0.08)["match"] == 4_400
    assert employer_match(500_000, 0.20, 1.0, 0.10)["yours"] == 24_500
    assert after_tax_room(24_500, 12_000) == 35_500


def test_roth_vs_traditional_follows_rates():
    r = roth_vs_traditional(10_000, 0.40, 0.25, 20, 0.06)
    assert r["traditional"] > r["roth"]
    same = roth_vs_traditional(10_000, 0.3, 0.3, 10, 0.05)
    assert math.isclose(same["traditional"], same["roth"])


def test_tax_brackets():
    assert bracket_tax(24_800, FED_BRACKETS) == 2_480
    assert round(bracket_tax(100_000, FED_BRACKETS)) == 2_480 + round(75_200 * 0.12)
    assert marginal_rate(300_000, FED_BRACKETS) == 0.24 and marginal_rate(450_000, FED_BRACKETS) == 0.32
    assert marginal_rate(300_000, CA_BRACKETS) == 0.093
    t = household_taxes(230_000, 90_000, 0, 24_500, 8_750, wages_spouse=60_000)
    assert t["gross"] == 380_000 and t["fed_taxable"] == 380_000 - 24_500 - 8_750 - 32_200
    assert t["ca_taxable"] > t["fed_taxable"]  # CA adds back the HSA and has a smaller standard deduction.
    assert 0.2 < t["effective"] < 0.4
    assert t["social_security"] == round(184_500 * 0.062 + 60_000 * 0.062, 2)


def test_equity_comp():
    g = rsu_tax_gap(100_000, 0.32, 0.093)
    assert round(g["gap"]) == round(100_000 * (0.413 - 0.3223))
    e = espp(50, 70, 70, 0.15, True, 8_500)
    assert e["price_paid"] == 42.5 and e["shares"] == 200 and round(e["return"], 3) == 0.647
    assert espp(50, 70, 70, 0.15, False, 1000)["price_paid"] == 59.5
    c = concentration(500_000, 1_200_000)
    assert round(c["share"], 2) == 0.42 and c["loss"] == 250_000 and c["to_sell_for_10pct"] == 380_000


def test_rebalance_and_family():
    trades = rebalance({"stocks": 90, "bonds": 10}, {"stocks": 80, "bonds": 20})
    assert trades == {"stocks": -10, "bonds": 10}
    p = college_plan(8, 40_000, 0.05, 40_000, 0.06)
    assert p["years"] == 10 and 270_000 < p["future_cost"] < 290_000 and 1_200 < p["monthly"] < 1_400
    assert college_plan(17, 1, 0, 1_000_000, 0.05)["monthly"] == 0
    assert life_insurance_need(200_000, 15, 900_000, 250_000, 50_000, 900_000, 440_000) == 2_860_000


def test_social_security_rules():
    assert math.isclose(ss_factor(62), 0.70) and math.isclose(ss_factor(70), 1.24) and ss_factor(67) == 1
    assert math.isclose(ss_factor(64), 1 - 36 * 5 / 9 / 100)
    assert 80 < ss_break_even(3_600, 62, 70) < 81


def test_checkup_helpers():
    ladder = money_ladder(True, True, 3, True, False, False, False, True, False, False, False, 20)
    assert [ok for _, ok, _, _ in ladder][:3] == [True, False, False]
    assert all(cat for *_, cat in ladder)
    ms = milestones(40, 1986)
    assert ms[0][0] == 50 and any("age 75" in m for _, m in ms)
    assert any("age 73" in m for _, m in milestones(70, 1955))
    assert all(a >= 66 for a, _ in milestones(66, 1960))


def test_quiz_shuffle_is_stable():
    item = {"q": "Which?", "options": ["a", "b", "c", "d"], "answer": 2}
    options, answer = shuffled_options(item)
    assert options[answer] == "c" and shuffled_options(item) == (options, answer)
    assert quiz_score([item, item], ["c", None]) == 1
