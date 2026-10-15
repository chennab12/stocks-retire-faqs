"""Money math used by the calculators, checkup and quiz. Every result is an estimate from the stated assumptions.

Tax tables are for married filing jointly. Federal figures are the IRS 2026 numbers; California figures are an
approximation of the indexed 2025 schedule (the FTB publishes the new table each fall). Update both yearly.
"""
import math
import random
import zlib

# ---- 2026 limits ----

K401_EMPLOYEE = 24_500
K401_CATCHUP_50 = 8_000
K401_CATCHUP_60_63 = 11_250
K401_TOTAL = 72_000
IRA_LIMIT = 7_500
HSA_FAMILY = 8_750
HSA_SELF = 4_400

FED_STANDARD_DEDUCTION = 32_200
FED_BRACKETS = [(24_800, 0.10), (100_800, 0.12), (211_400, 0.22), (403_550, 0.24), (512_450, 0.32), (768_700, 0.35), (math.inf, 0.37)]
CA_STANDARD_DEDUCTION = 11_400
CA_BRACKETS = [(22_158, 0.01), (52_528, 0.02), (82_904, 0.04), (115_084, 0.06), (145_448, 0.08), (742_958, 0.093),
               (891_542, 0.103), (1_485_906, 0.113), (math.inf, 0.123)]
CA_MENTAL_HEALTH_RATE = 0.01  # Extra 1% on CA taxable income above $1M.
SS_WAGE_BASE = 184_500
ADDL_MEDICARE_THRESHOLD = 250_000  # Joint wages.
CA_SDI_RATE = 0.013  # Approximate; no wage cap since 2024.
FED_SUPPLEMENTAL = 0.22
CA_SUPPLEMENTAL = 0.1023


# ---- Growth ----

def future_value(present, monthly, annual_rate, years):
    """Balance after `years` with monthly contributions and monthly compounding."""
    r = annual_rate / 12
    n = round(years * 12)
    if r == 0:
        return present + monthly * n
    growth = (1 + r) ** n
    return present * growth + monthly * (growth - 1) / r


def growth_by_year(present, monthly, annual_rate, years):
    """Year-end balances and total contributed, for charts: list of (year, balance, contributed)."""
    return [(y, future_value(present, monthly, annual_rate, y), present + monthly * 12 * y) for y in range(years + 1)]


def real_rate(nominal, inflation):
    """Return after inflation (Fisher formula)."""
    return (1 + nominal) / (1 + inflation) - 1


def rule_of_72(rate_percent):
    return 72 / rate_percent if rate_percent > 0 else math.inf


def fee_drag(balance, monthly, annual_rate, years, fee_low, fee_high):
    """Ending balances with a low and a high yearly fee, and the dollar difference."""
    low = future_value(balance, monthly, annual_rate - fee_low, years)
    high = future_value(balance, monthly, annual_rate - fee_high, years)
    return {"low": low, "high": high, "cost": low - high}


# ---- Retirement ----

def fi_number(yearly_spending, guaranteed_income=0, withdrawal_rate=0.04):
    """Invested amount needed so withdrawals cover spending not met by pensions or Social Security."""
    return max(0, yearly_spending - guaranteed_income) / withdrawal_rate


def months_to_target(present, monthly, annual_rate, target, max_years=80):
    """Months of saving until the balance reaches the target, or None if not within max_years."""
    if present >= target:
        return 0
    r = annual_rate / 12
    balance = present
    for month in range(1, max_years * 12 + 1):
        balance = balance * (1 + r) + monthly
        if balance >= target:
            return month
    return None


def years_to_fi(savings_rate, real_return=0.05, withdrawal_rate=0.04):
    """Years to financial independence from zero savings, given a savings rate (share of take-home kept).

    Spending is (1 − s) of income; the target is spending ÷ withdrawal rate; saving s of income a year.
    """
    if savings_rate <= 0:
        return math.inf
    if savings_rate >= 1:
        return 0
    target_multiple = (1 - savings_rate) / withdrawal_rate / savings_rate  # target in years of savings
    if real_return == 0:
        return target_multiple
    return math.log(1 + target_multiple * real_return) / math.log(1 + real_return)


def money_lasts(balance, yearly_withdrawal, annual_real_rate, max_years=60):
    """Years a portfolio lasts with inflation-adjusted withdrawals at the start of each year, and the balance path."""
    path = [balance]
    for year in range(1, max_years + 1):
        balance = (balance - yearly_withdrawal) * (1 + annual_real_rate)
        if balance <= 0:
            path.append(0)
            return year, path
        path.append(balance)
    return None, path  # None means it lasts at least max_years.


# ---- 401(k) and accounts ----

def k401_employee_limit(age):
    """Employee deferral limit for 2026 including catch-up for the age reached this year."""
    if 60 <= age <= 63:
        return K401_EMPLOYEE + K401_CATCHUP_60_63
    if age >= 50:
        return K401_EMPLOYEE + K401_CATCHUP_50
    return K401_EMPLOYEE


def employer_match(salary, contribution_pct, match_rate, match_up_to_pct, age=40):
    """Yearly match: match_rate × your contributions on the first match_up_to_pct of salary (deferral capped at the IRS limit)."""
    yours = min(salary * contribution_pct, k401_employee_limit(age))
    matched_base = min(yours, salary * match_up_to_pct)
    return {"yours": yours, "match": matched_base * match_rate, "max_match": min(salary * match_up_to_pct, k401_employee_limit(age)) * match_rate}


def after_tax_room(employee_regular, employer, total_limit=K401_TOTAL):
    """Space left for after-tax (mega backdoor) contributions. Catch-up contributions don't count toward the total."""
    return max(0, total_limit - min(employee_regular, K401_EMPLOYEE) - employer)


def roth_vs_traditional(amount, rate_now, rate_later, years, annual_return):
    """Spendable value of the same pre-tax dollars put in Roth (taxed now) vs traditional (taxed later)."""
    growth = (1 + annual_return) ** years
    return {"roth": amount * (1 - rate_now) * growth, "traditional": amount * growth * (1 - rate_later)}


# ---- Taxes (married filing jointly) ----

def bracket_tax(taxable, brackets):
    tax, lower = 0.0, 0.0
    for upper, rate in brackets:
        if taxable <= lower:
            break
        tax += (min(taxable, upper) - lower) * rate
        lower = upper
    return tax


def marginal_rate(taxable, brackets):
    for upper, rate in brackets:
        if taxable < upper:
            return rate
    return brackets[-1][1]


def household_taxes(wages, rsu_income=0, other_income=0, pretax_401k=0, hsa=0, itemized_fed=0, itemized_ca=0, wages_spouse=0):
    """Rough 2026 federal + California income tax and payroll tax for a married couple filing jointly.

    `wages` and `wages_spouse` are each spouse's salary + bonus; RSU income is added to the first spouse's wages.
    HSA payroll contributions are deductible federally but added back for California. Itemized amounts below the
    standard deduction are ignored. Credits (child tax credit, CA exemption credits) are not included.
    """
    gross = wages + wages_spouse + rsu_income + other_income
    fed_taxable = max(0, gross - pretax_401k - hsa - max(FED_STANDARD_DEDUCTION, itemized_fed))
    ca_taxable = max(0, gross - pretax_401k - max(CA_STANDARD_DEDUCTION, itemized_ca))
    federal = bracket_tax(fed_taxable, FED_BRACKETS)
    california = bracket_tax(ca_taxable, CA_BRACKETS) + max(0, ca_taxable - 1_000_000) * CA_MENTAL_HEALTH_RATE
    earned = [wages + rsu_income, wages_spouse]
    social_security = sum(min(w, SS_WAGE_BASE) * 0.062 for w in earned)
    medicare = sum(earned) * 0.0145 + max(0, sum(earned) - ADDL_MEDICARE_THRESHOLD) * 0.009
    sdi = sum(earned) * CA_SDI_RATE
    ca_marginal = marginal_rate(ca_taxable, CA_BRACKETS) + (CA_MENTAL_HEALTH_RATE if ca_taxable > 1_000_000 else 0)
    total = federal + california + social_security + medicare + sdi
    return {
        "gross": gross, "fed_taxable": fed_taxable, "ca_taxable": ca_taxable, "federal": federal, "california": california,
        "social_security": social_security, "medicare": medicare, "sdi": sdi, "total": total,
        "fed_marginal": marginal_rate(fed_taxable, FED_BRACKETS), "ca_marginal": ca_marginal,
        "effective": total / gross if gross else 0,
    }


def rsu_tax_gap(vest_value, fed_marginal, ca_marginal, fed_withheld=FED_SUPPLEMENTAL, ca_withheld=CA_SUPPLEMENTAL):
    """Tax owed vs withheld on RSU income (income tax only; payroll taxes are withheld at the right rate)."""
    owed = vest_value * (fed_marginal + ca_marginal)
    withheld = vest_value * (fed_withheld + ca_withheld)
    return {"owed": owed, "withheld": withheld, "gap": owed - withheld}


def espp(offer_price, purchase_price, sale_price, discount=0.15, lookback=True, contribution=10_000):
    """Shares bought, price paid, gain and return for one ESPP purchase period, and the discount taxed as income on a quick sale."""
    base = min(offer_price, purchase_price) if lookback else purchase_price
    paid = base * (1 - discount)
    shares = contribution / paid
    gain = (sale_price - paid) * shares
    return {"price_paid": paid, "shares": shares, "gain": gain, "return": sale_price / paid - 1,
            "ordinary_income": (purchase_price - paid) * shares}


def concentration(stock_value, net_worth, drop=0.5):
    share = stock_value / net_worth if net_worth else 0
    loss = stock_value * drop
    return {"share": share, "loss": loss, "loss_share": loss / net_worth if net_worth else 0,
            "to_sell_for_10pct": max(0, stock_value - 0.10 * net_worth)}


def rebalance(holdings, targets):
    """Dollar trades (+ buy, − sell) to move holdings to target percentages (targets sum to 100)."""
    total = sum(holdings.values())
    return {k: round(total * targets.get(k, 0) / 100 - holdings.get(k, 0)) for k in holdings}


# ---- Family ----

def college_plan(child_age, yearly_cost_today, college_inflation, balance, annual_return, start_age=18, years_of_college=4):
    """Future cost of college, what today's balance grows to, and the monthly saving needed to close the gap by start_age."""
    years = max(0, start_age - child_age)
    future_cost = sum(yearly_cost_today * (1 + college_inflation) ** (years + i) for i in range(years_of_college))
    grown = balance * (1 + annual_return) ** years
    gap = max(0, future_cost - grown)
    r = annual_return / 12
    n = years * 12
    if gap == 0 or n == 0:
        monthly = 0 if gap == 0 else gap
    elif r == 0:
        monthly = gap / n
    else:
        monthly = gap * r / ((1 + r) ** n - 1)
    return {"years": years, "future_cost": future_cost, "grown": grown, "gap": gap, "monthly": monthly}


def emergency_fund(monthly_essentials, months):
    return monthly_essentials * months


def life_insurance_need(income, years_of_income, debts, college, final_costs, savings, existing):
    """Simple needs-based estimate: income replacement + debts + college + final costs − savings − existing coverage."""
    return max(0, income * years_of_income + debts + college + final_costs - savings - existing)


# ---- Social Security ----

def ss_factor(claim_age, fra=67):
    """Share of the full (FRA) benefit paid when claiming at claim_age (62–70), using SSA's reduction and delay rules."""
    months = round((claim_age - fra) * 12)
    if months >= 0:
        return 1 + min(months, (70 - fra) * 12) * (2 / 3) / 100
    early = -months
    first = min(early, 36)
    rest = max(0, early - 36)
    return 1 - first * (5 / 9) / 100 - rest * (5 / 12) / 100


def ss_break_even(pia, early_age, late_age, fra=67):
    """Age when total benefits from claiming late catch up with claiming early (ignoring COLAs, which scale both)."""
    early = pia * ss_factor(early_age, fra)
    late = pia * ss_factor(late_age, fra)
    if late <= early:
        return None
    months = (late_age - early_age) * 12 * late / (late - early)
    return early_age + months / 12


# ---- Checkup ----

def money_ladder(match_ok, card_debt, emergency_months, hsa_eligible, hsa_maxed, k401_maxed, backdoor_done, has_kid,
                 saving_529, mega_available, mega_used, stock_share):
    """The money priority ladder with a done flag per rung: (rung, done, next action, category)."""
    rows = [
        ("🎁 Full 401(k) match", match_ok, "Raise your 401(k) % to capture every match dollar.", "401(k) & workplace plans"),
        ("💳 No high-interest debt", not card_debt, "Send every spare dollar to the highest-rate card.", "Money foundations"),
        ("🛟 Emergency fund 6 months", emergency_months >= 6, f"Add {max(0, 6 - emergency_months):g} more months of essentials in cash.", "Money foundations"),
        ("🩺 Max HSA", hsa_maxed or not hsa_eligible, "Max the HSA through payroll and invest it.", "IRAs & HSA"),
        ("🏢 Max 401(k)", k401_maxed, "Raise contributions to the $24,500 limit.", "401(k) & workplace plans"),
        ("🚪 Backdoor Roth × 2", backdoor_done, "Do a $7,500 backdoor Roth for each spouse.", "IRAs & HSA"),
        ("🎓 529 for your child", saving_529 or not has_kid, "Open a 529 and automate a monthly amount.", "Family goals: college, home & kids"),
        ("🚀 Mega backdoor Roth", mega_used or not mega_available, "Fill after-tax 401(k) room with auto-conversion.", "401(k) & workplace plans"),
        ("🧺 Company stock ≤ 10%", stock_share <= 10, "Write a sell schedule to get under 10% of net worth.", "Equity comp: RSUs, ESPP & options"),
        ("📈 Taxable index investing", None, "Invest what's left in a broad index ETF.", "Index funds & ETFs"),
    ]
    return rows


def milestones(age, birth_year):
    """Upcoming age-based money milestones: (age, milestone)."""
    rmd_age = 75 if birth_year >= 1960 else 73
    items = [
        (50, "🏢 401(k) and IRA catch-up contributions begin"),
        (55, "🩺 HSA catch-up (+$1,000) · 🚪 401(k) rule of 55 if you leave your job this year or later"),
        (59.5, "🔓 Penalty-free withdrawals from IRAs and 401(k)s"),
        (60, "🚀 Super catch-up in the 401(k) for ages 60–63"),
        (62, "🪪 Earliest Social Security (about 70% of full benefit)"),
        (65, "🏥 Medicare enrollment window; HSA contributions stop once on Medicare"),
        (67, "🪪 Full Social Security retirement age (born 1960+)"),
        (70, "🪪 Maximum Social Security (124%); delayed credits stop"),
        (70.5, "🎁 Qualified charitable distributions from IRAs allowed"),
        (rmd_age, f"📤 Required minimum distributions begin (age {rmd_age})"),
    ]
    return [(a, m) for a, m in items if a >= age]


# ---- Quiz helpers ----

def shuffled_options(item):
    """Options in a stable shuffled order (same every run) and the new index of the right answer."""
    order = list(range(len(item["options"])))
    random.Random(zlib.crc32(item["q"].encode())).shuffle(order)
    return [item["options"][i] for i in order], order.index(item["answer"])


def quiz_score(items, picks):
    """Number of picks (shown option text, or None) matching each item's correct answer."""
    return sum(1 for item, pick in zip(items, picks) if pick == item["options"][item["answer"]])
