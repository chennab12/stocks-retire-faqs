"""Stocks & Retirement FAQs: one place to learn, plan and track investing, taxes and retirement for a Silicon Valley family."""
import csv
import io
import json
import random
import re
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from calculations import (
    HSA_FAMILY,
    IRA_LIMIT,
    K401_EMPLOYEE,
    K401_TOTAL,
    after_tax_room,
    college_plan,
    concentration,
    emergency_fund,
    employer_match,
    espp,
    fee_drag,
    fi_number,
    future_value,
    growth_by_year,
    household_taxes,
    k401_employee_limit,
    life_insurance_need,
    milestones,
    money_lasts,
    money_ladder,
    months_to_target,
    quiz_score,
    real_rate,
    rebalance,
    roth_vs_traditional,
    rsu_tax_gap,
    rule_of_72,
    shuffled_options,
    ss_break_even,
    ss_factor,
    years_to_fi,
)
from content import (
    CATEGORIES,
    DISCLAIMER,
    FAST_TRACK,
    GLOSSARY,
    GROUPS,
    KEY_NUMBERS,
    LIMITS,
    MONTHLY_HABITS,
    PERSONA,
    PLAN_12_WEEKS,
    RED_FLAGS,
    REVIEWED,
    SOURCES,
    TAX_YEAR,
    TOP_20_NOTE,
)
from visuals import show

st.set_page_config(page_title="Stocks & Retirement FAQs", page_icon="📈", layout="wide")

HOME = "🏠 My dashboard"
PLAN = "🗺️ 12-week money plan"
CHEATSHEET = "📌 Master cheatsheet"
CAT_NAMES = [c["name"] for c in CATEGORIES]
CHECKUP = "🧭 Money checkup & year planner"
LOG = "📈 Net-worth log"
QUIZ = "📝 Quiz center"
CALCULATORS = "🧮 Calculators"
SEARCH = "🔎 Search everything"
ABOUT = "📚 Sources & method"
SECTIONS = [HOME, PLAN, CHEATSHEET] + CAT_NAMES + [CHECKUP, LOG, QUIZ, CALCULATORS, SEARCH, ABOUT]
SLUGS = {name: re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") for name in SECTIONS}
BY_SLUG = {slug: name for name, slug in SLUGS.items()}
BY_TITLE = {c["title"]: c["name"] for c in CATEGORIES}
CALCS = [
    "💰 Compound growth",
    "🎯 Retirement number",
    "📅 Retirement projection",
    "🏦 401(k) match & max",
    "⚖️ Roth vs traditional",
    "🧾 Tax bracket estimator",
    "📦 RSU tax gap",
    "🛒 ESPP return",
    "🧺 Concentration check",
    "🥧 Allocation & rebalance",
    "💸 Fee drag",
    "🎓 529 college",
    "🛟 Emergency fund",
    "🪪 Social Security claiming",
    "🏖️ How long will it last",
    "🛡️ Life insurance need",
]
# Calculators that go with each category page.
CALC_FOR = {
    "Money foundations": ["🛟 Emergency fund", "💰 Compound growth"],
    "How investing works": ["💰 Compound growth", "💸 Fee drag"],
    "Mindset, myths & scams": ["🧺 Concentration check"],
    "401(k) & workplace plans": ["🏦 401(k) match & max", "⚖️ Roth vs traditional"],
    "IRAs & HSA": ["⚖️ Roth vs traditional", "💰 Compound growth"],
    "Taxes: federal & California": ["🧾 Tax bracket estimator", "📦 RSU tax gap"],
    "Equity comp: RSUs, ESPP & options": ["📦 RSU tax gap", "🛒 ESPP return", "🧺 Concentration check"],
    "Index funds & ETFs": ["💸 Fee drag"],
    "Portfolio & allocation": ["🥧 Allocation & rebalance"],
    "Stocks, bonds & cash basics": ["🛟 Emergency fund", "🥧 Allocation & rebalance"],
    "Family goals: college, home & kids": ["🎓 529 college"],
    "Your retirement number": ["🎯 Retirement number", "📅 Retirement projection"],
    "Retirement income: Social Security & withdrawals": ["🪪 Social Security claiming", "🏖️ How long will it last"],
    "Protect: insurance & estate": ["🛡️ Life insurance need"],
}
TOPICS = [(c, t) for c in CATEGORIES for t in c["topics"]]
QUESTIONS = [{**item, "category": c["name"], "topic": t["title"]} for c, t in TOPICS for item in t["quiz"]]
ASSETS = ["Cash", "401k/IRA", "Roth", "HSA", "529", "Taxable brokerage", "Company stock", "Home equity"]
LOG_COLUMNS = ["Date"] + ASSETS + ["Debts"]

if "section" not in st.session_state:
    # Deep links: ?page=iras-hsa opens that section directly.
    st.session_state.section = BY_SLUG.get(st.query_params.get("page", ""), HOME)
st.session_state.setdefault("done", set())
st.session_state.setdefault("habits", set())
st.session_state.setdefault("weeks_done", set())
st.session_state.setdefault("quiz_seed", 0)
st.session_state.setdefault("quiz_history", [])
st.session_state.setdefault("missed", set())
st.session_state.setdefault("quiz_cats", [])
st.session_state.setdefault("calc", CALCS[0])
st.session_state.setdefault("log_df", pd.DataFrame(columns=LOG_COLUMNS))


def go_to(section):
    st.session_state.section = section


def open_calc(name):
    st.session_state.calc = name
    st.session_state.section = CALCULATORS


def go_quiz(category_name):
    st.session_state.quiz_cats = [category_name]
    st.session_state.quiz_seed += 1
    st.session_state.section = QUIZ


def toggle(store, item, widget_key):
    if st.session_state[widget_key]:
        st.session_state[store].add(item)
    else:
        st.session_state[store].discard(item)


def new_quiz():
    st.session_state.quiz_seed += 1


def md(text):
    """Escape dollar signs so Streamlit markdown does not render them as math."""
    return str(text).replace("$", "\\$")


def money(x):
    """Whole dollars with a minus sign in front for negatives."""
    return f"-${-x:,.0f}" if x < 0 else f"${x:,.0f}"


def md_table(header, rows):
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(str(c).replace("|", "/") for c in row) + " |" for row in rows]
    st.markdown(md("\n".join(lines)))


def to_csv(rows):
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return out.getvalue()


def mistakes_table(rows):
    st.subheader("⚠️ Common mistakes and how to avoid them")
    md_table(["Mistake ⛔", "Why it hurts", "Do this instead ✅"], [(f"**{a}**", b, c) for a, b, c in rows])


def links_row(names):
    st.markdown("🔗 **Trusted sources:** " + " · ".join(f"[{n} ↗]({SOURCES[n]})" for n in names))


def dollars(label, value, key, step=1_000, max_value=50_000_000, help=None, col=st):
    return col.number_input(label, 0, max_value, value, step, key=key, help=help)


def pct(label, value, key, max_value=100.0, step=0.5, help=None, col=st):
    """Percent input that returns a fraction."""
    return col.number_input(label, 0.0, max_value, float(value), step, key=key, help=help, format="%.2f") / 100


def progress_json():
    return json.dumps({
        "done": sorted(st.session_state.done), "habits": sorted(st.session_state.habits),
        "weeks_done": sorted(st.session_state.weeks_done), "quiz_history": st.session_state.quiz_history,
        "missed": sorted(st.session_state.missed),
    }, indent=1)


def load_progress():
    upload = st.session_state.get("progress_upload")
    if upload is None:
        return
    try:
        data = json.loads(upload.getvalue())
    except (ValueError, UnicodeDecodeError):
        st.session_state.load_error = True
        return
    titles = {t["title"] for _, t in TOPICS}
    habits = {h for _, h, _ in MONTHLY_HABITS}
    questions = {q["q"] for q in QUESTIONS}
    st.session_state.done = {t for t in data.get("done", []) if t in titles}
    st.session_state.habits = {h for h in data.get("habits", []) if h in habits}
    st.session_state.weeks_done = {w for w in data.get("weeks_done", []) if isinstance(w, int) and 1 <= w <= 12}
    st.session_state.quiz_history = [tuple(x) for x in data.get("quiz_history", []) if len(x) == 2]
    st.session_state.missed = {q for q in data.get("missed", []) if q in questions}
    st.session_state.load_error = False


def next_topic():
    """First topic, in app order, not yet marked as done."""
    return next(((c, t) for c, t in TOPICS if t["title"] not in st.session_state.done), None)


def cat_done(c):
    return sum(t["title"] in st.session_state.done for t in c["topics"])


def log_with_totals(df):
    """Log rows with Net worth and Company stock % columns added."""
    out = df.copy()
    nums = out[ASSETS + ["Debts"]].apply(pd.to_numeric, errors="coerce").fillna(0)
    out["Net worth"] = nums[ASSETS].sum(axis=1) - nums["Debts"]
    out["Company stock %"] = (100 * nums["Company stock"] / out["Net worth"].where(out["Net worth"] > 0)).round(1)
    return out


with st.sidebar:
    st.title("📈 Stocks & Retirement FAQs")
    # Only the selected section runs on each rerun, so pages stay fast.
    st.radio("Section", SECTIONS, key="section")
    st.divider()
    done = len(st.session_state.done)
    st.progress(done / len(TOPICS), text=f"✅ {done} of {len(TOPICS)} topics done")
    st.progress(len(st.session_state.weeks_done) / 12, text=f"🗺️ {len(st.session_state.weeks_done)} of 12 plan weeks")
    with st.expander("💾 Save or restore progress"):
        st.download_button("⬇️ Download my progress", progress_json(), "money-progress.json", "application/json", width="stretch")
        st.file_uploader("Upload a progress file", type="json", key="progress_upload", on_change=load_progress)
        if st.session_state.get("load_error"):
            st.error("That file couldn't be read.")
    st.caption("🚩 Fraud: reportfraud.ftc.gov · sec.gov/tcr · Elder fraud 1-833-372-8311")

st.title("📈 Stocks & Retirement FAQs")
st.caption(f"Investing, taxes and retirement for a Silicon Valley family · {TAX_YEAR} limits · Federal + California · Reviewed {REVIEWED}")
st.info("🧭 " + DISCLAIMER)
section = st.session_state.section


# ---------------------------------------------------------------- Home

def render_home():
    st.header("🏠 My dashboard")
    habits_done = len(st.session_state.habits)
    history = st.session_state.quiz_history
    nxt = next_topic()
    a, b, c, d = st.columns(4)
    a.metric("Topics done", f"{len(st.session_state.done)} / {len(TOPICS)}")
    b.metric("This month's habits", f"{habits_done} / {len(MONTHLY_HABITS)}")
    c.metric("Best quiz", f"{max(s / n for s, n in history):.0%}" if history else "—")
    d.metric("Plan weeks done", f"{len(st.session_state.weeks_done)} / 12")
    if nxt:
        cat, topic = nxt
        st.button(f"▶️ Continue: {topic['icon']} {topic['title']} ({cat['title']})", on_click=go_to, args=(cat["name"],), type="primary")
    st.caption("👪 " + PERSONA)

    st.subheader("✅ This month's 10 money habits")
    st.caption("Tick what's true this month. Aim for 8+. Ticks are saved in the progress file (sidebar).")
    cols = st.columns(2)
    for i, (icon, habit, cat_title) in enumerate(MONTHLY_HABITS):
        key = f"habit_{i}"
        cols[i % 2].checkbox(f"{icon} {habit}", value=habit in st.session_state.habits, key=key, on_change=toggle, args=("habits", habit, key))
    score = len(st.session_state.habits) / len(MONTHLY_HABITS)
    st.progress(score, text=f"Monthly money score: {score:.0%}" + (" 🎉 Great month!" if score >= 0.8 else ""))

    st.subheader(f"🎯 Key {TAX_YEAR} numbers at a glance")
    for row in (KEY_NUMBERS[:4], KEY_NUMBERS[4:]):
        for col, (label, value, help_text) in zip(st.columns(4), row):
            col.metric(label, value, help=help_text)

    st.subheader("🚀 Fast track: the 10 highest-impact moves")
    for i, (icon, action, cat_title) in enumerate(FAST_TRACK, 1):
        left, right = st.columns([5, 2], vertical_alignment="center")
        left.markdown(f"**{i}.** {icon} {action}")
        right.button("Learn how →", key=f"fast_{i}", on_click=go_to, args=(BY_TITLE[cat_title],), width="stretch")

    st.subheader("🧭 Categories")
    for group in GROUPS:
        st.markdown(f"#### {group}")
        members = [c for c in CATEGORIES if c["group"] == group]
        cols = st.columns(3)
        for i, cat in enumerate(members):
            with cols[i % 3].container(border=True):
                st.markdown(f"**{cat['name']}**")
                label, value, _ = cat["numbers"][0]
                st.caption(md(f"{label}: **{value}** · {cat_done(cat)}/{len(cat['topics'])} topics done"))
                st.write(md(" · ".join(f"{t['icon']} {t['title']}" for t in cat["topics"])))
                st.button("Open →", key="open_" + cat["name"], on_click=go_to, args=(cat["name"],), width="stretch")

    st.subheader("🚩 Red flags: stop and verify")
    md_table(["Red flag", "What it looks like", "What to do"], [(f"**{a}**", b, f"**{c}**") for a, b, c in RED_FLAGS])
    mistakes_table([
        ("Trying to fix everything at once", "Big overhauls stall within weeks.", "Follow the 12-week plan: one money task a week."),
        ("Not knowing your numbers", "You can't tell if you're on track.", "Log net worth quarterly in the 📈 Net-worth log."),
        ("Chasing hot stocks", "Most stock pickers trail the index.", "Do the Fast track list first; keep speculation ≤ 5%."),
    ])


# ---------------------------------------------------------------- Plan

def render_plan():
    st.header("🗺️ 12-week money plan")
    st.caption("One money task a week. By week 12 you'll have touched every big lever: cash, accounts, taxes, equity, investing, family, retirement and protection.")
    start = st.date_input("Start date", value=date.today(), key="plan_start")
    done = st.session_state.weeks_done
    st.progress(len(done) / 12, text=f"{len(done)} of 12 weeks done")
    for week, focus, task, cat_title in PLAN_12_WEEKS:
        begins = start + timedelta(weeks=week - 1)
        with st.container(border=True):
            left, mid, right = st.columns([1, 5, 2], vertical_alignment="center")
            key = f"week_{week}"
            left.checkbox(f"Week {week}", value=week in done, key=key, on_change=toggle, args=("weeks_done", week, key))
            mid.markdown(md(f"**{focus}** · {begins:%b %d}  \n{task}"))
            right.button("Open topic →", key=f"plan_open_{week}", on_click=go_to, args=(BY_TITLE[cat_title],), width="stretch")
    rows = [{"Week": w, "Starts": str(start + timedelta(weeks=w - 1)), "Focus": f, "Task": h, "Category": c} for w, f, h, c in PLAN_12_WEEKS]
    st.download_button("⬇️ Download plan (CSV)", to_csv(rows), "money-12-week-plan.csv", "text/csv")
    show("12-week plan", [f for _, f, _, _ in PLAN_12_WEEKS[:6]])
    mistakes_table([
        ("Skipping the boring weeks", "Insurance and estate gaps matter most in a crisis.", "Finish all 12, even the dull ones."),
        ("Stopping after a busy week", "Progress isn't a straight line.", "Pick up the current week; don't restart."),
    ])


# ---------------------------------------------------------------- Cheatsheet

def render_cheatsheet():
    st.header("📌 Master cheatsheet")
    st.caption("Every topic, number and rule on one page. Download any table as CSV.")
    st.subheader(f"🔢 {TAX_YEAR} limits & thresholds")
    limits = [{"Item": a, f"{TAX_YEAR}": b, "Note": c, "Source": SOURCES[s]} for a, b, c, s in LIMITS]
    st.dataframe(limits, hide_index=True, width="stretch", column_config={"Source": st.column_config.LinkColumn("Source", display_text="Open ↗")})
    st.download_button("⬇️ Limits (CSV)", to_csv(limits), f"limits-{TAX_YEAR}.csv", "text/csv")
    rows = [
        {"Category": c["name"], "Topic": f"{t['icon']} {t['title']}", "Gist": t["gist"], "Aim for": t["target"],
         "First step (today)": t["actions"][0][1], "Track": t["metric"]}
        for c, t in TOPICS
    ]
    st.subheader("🧭 Every topic")
    st.dataframe(rows, hide_index=True, width="stretch")
    st.download_button("⬇️ Topics (CSV)", to_csv(rows), "money-topics.csv", "text/csv")
    st.subheader("📏 Key numbers by category")
    nums = [{"Category": c["name"], "Measure": a, "Value": b, "Note": n} for c in CATEGORIES for a, b, n in c["numbers"]]
    st.dataframe(nums, hide_index=True, width="stretch")
    st.subheader("📊 What to track (KPI library)")
    kpis = [{"Category": c["name"], "Metric": a, "Target": b, "How to measure": h} for c in CATEGORIES for a, b, h in c["kpis"]]
    st.dataframe(kpis, hide_index=True, width="stretch")
    st.subheader("💡 Tips, tricks & hacks")
    tips = [{"Topic": t["title"], "Tip": tip} for _, t in TOPICS for tip in t["tips"]]
    st.dataframe(tips, hide_index=True, width="stretch")
    st.download_button("⬇️ Tips (CSV)", to_csv(tips), "money-tips.csv", "text/csv")
    st.subheader("📖 Glossary")
    md_table(["Term", "Meaning"], [(f"**{k}**", v) for k, v in GLOSSARY.items()])
    mistakes_table([(a, b, c) for cat in CATEGORIES for a, b, c in cat["mistakes"]])


# ---------------------------------------------------------------- Category pages

def render_quick_check(cat, t):
    st.markdown("#### 📝 Quick check")
    for i, item in enumerate(t["quiz"]):
        options, answer = shuffled_options(item)
        pick = st.radio(md(f"**Q{i + 1}.** {item['q']}"), options, index=None, key=f"tq_{t['title']}_{i}")
        if pick is not None:
            if pick == options[answer]:
                st.success(md(f"✅ Correct. {item['why']}"))
            else:
                st.error(md(f"❌ Not quite. The answer is **{options[answer]}**. {item['why']}"))
    st.button(f"📝 Take the full {cat['title']} quiz →", key=f"quiz_{t['title']}", on_click=go_quiz, args=(cat["name"],))


def render_topic(cat, t):
    st.success(md(f"🎯 **Gist:** {t['gist']}"))
    left, right = st.columns(2)
    left.markdown(md(f"🧭 **Why it matters:** {t['purpose']}"))
    right.markdown(md(f"🗣️ **In plain words:** {t['plain']}"))
    st.info(md(f"💡 **Example:** {t['example']}"))
    st.markdown(md(f"🏁 **Aim for:** {t['target']}"))
    st.markdown("#### 🔑 Key insights")
    st.markdown(md("\n".join(f"{n}. {x}" for n, x in enumerate(t["insights"], 1))))
    st.markdown("#### 🪄 Tips, tricks & hacks")
    st.markdown(md("\n".join(f"- {tip}" for tip in t["tips"])))
    do_col, dont_col = st.columns(2)
    with do_col.container(border=True):
        st.markdown("**✅ Do**  \n" + md("  \n".join(f"✔️ {x}" for x in t["do"])))
    with dont_col.container(border=True):
        st.markdown("**⛔ Don't**  \n" + md("  \n".join(f"✖️ {x}" for x in t["dont"])))
    st.markdown("#### 🚀 Next steps for real progress")
    st.dataframe([{"When": w, "Action": a} for w, a in t["actions"]], hide_index=True, width="stretch")
    name, how = t["experiment"]
    with st.container(border=True):
        st.markdown(md(f"🧪 **Try this: {name}**  \n{how}"))
    st.markdown(md(f"📏 **Track this:** {t['metric']}"))
    links_row(t["sources"])
    render_quick_check(cat, t)
    widget = "done_" + t["title"]
    st.toggle("✅ I've started this topic's next steps", value=t["title"] in st.session_state.done, key=widget,
              on_change=toggle, args=("done", t["title"], widget))


def render_category(index):
    cat = CATEGORIES[index]
    st.header(cat["name"])
    st.caption(f"{cat['group']} · {cat_done(cat)} of {len(cat['topics'])} topics done")
    st.markdown(md(f"🌟 **Why this matters:** {cat['why']}"))
    st.markdown(md(f"🏁 **After this section you can:** {cat['outcome']}"))
    for col, (label, value, help_text) in zip(st.columns(4), cat["numbers"]):
        col.metric(label, value, help=help_text)
    tabs = st.tabs([f"{t['icon']} {t['title']}" + (" ✅" if t["title"] in st.session_state.done else "") for t in cat["topics"]])
    for tab, t in zip(tabs, cat["topics"]):
        with tab:
            render_topic(cat, t)
    st.divider()
    show(cat["title"], [t["title"] for t in cat["topics"]])
    st.subheader("📋 What to know and do")
    md_table(["Topic", "Gist", "Aim for", "Do this today"], [(f"{t['icon']} **{t['title']}**", t["gist"], t["target"], t["actions"][0][1]) for t in cat["topics"]])
    st.subheader("📊 What to track")
    md_table(["Metric", "Target", "How to measure"], cat["kpis"])
    st.markdown("**🧮 Related calculators**")
    calcs = CALC_FOR[cat["title"]]
    for col, name in zip(st.columns(len(calcs)), calcs):
        col.button(name, key=f"calc_{cat['title']}_{name}", on_click=open_calc, args=(name,), width="stretch")
    mistakes_table(cat["mistakes"])
    prev_col, next_col = st.columns(2)
    if index > 0:
        prev_col.button("← Previous category", on_click=go_to, args=(CAT_NAMES[index - 1],), width="stretch")
    if index + 1 < len(CATEGORIES):
        next_col.button("Next category →", on_click=go_to, args=(CAT_NAMES[index + 1],), type="primary", width="stretch")
    else:
        next_col.button("Run my money checkup →", on_click=go_to, args=(CHECKUP,), type="primary", width="stretch")


# ---------------------------------------------------------------- Money checkup & year planner

YEAR_PLAN = [
    ("January", "🚪 Backdoor Roth for both spouses · 🏢 reset 401(k) and HSA % for new limits · 📈 update net worth"),
    ("Jan 15 · Apr 15 · Jun 15 · Sep 15", "🧾 Estimated tax due dates if RSU withholding falls short"),
    ("February–March", "📄 Gather W-2s, 1099-B, Form 3922 and RSU/ESPP supplemental basis statements"),
    ("April 15", "🧾 Tax day · last day for prior-year IRA and HSA contributions"),
    ("June", "🧮 IRS Withholding Estimator check · 🥧 mid-year allocation check"),
    ("Each vest or ESPP purchase", "📦 Sell per your plan, reinvest, record cost basis"),
    ("Your birthday", "🪪 Check my Social Security statements · 🛡️ review insurance and beneficiaries"),
    ("October–November", "🏥 Open enrollment: HDHP/HSA, life, disability, legal plan · 🔢 new IRS limits announced"),
    ("November–December", "✂️ Tax-loss harvesting · 🎁 charitable gifts or donor-advised fund · 🎓 529 gifts"),
    ("December 31", "🏢 Last day for 401(k) contributions and Roth conversions · 🚪 pre-tax IRA balance at $0"),
]


def render_checkup():
    st.header("🧭 Money checkup & year planner")
    st.caption("Answer a few questions to see your money priority ladder, upcoming age milestones, and a year calendar. Nothing leaves your browser session.")
    a, b, c = st.columns(3)
    age = a.number_input("Your age", 18, 90, 40, key="ck_age")
    birth_year = date.today().year - age
    emergency = b.number_input("Months of essentials in cash", 0.0, 36.0, 3.0, 0.5, key="ck_em")
    stock_share = c.number_input("Company stock, % of net worth", 0, 100, 20, key="ck_stock")
    x, y, z = st.columns(3)
    with x:
        match_ok = st.checkbox("Getting the full 401(k) match", True, key="ck_match")
        card_debt = st.checkbox("Carrying credit-card or other high-rate debt", key="ck_debt")
        k401_maxed = st.checkbox(f"Maxing the 401(k) (${K401_EMPLOYEE:,})", key="ck_401")
    with y:
        hsa_eligible = st.checkbox("On an HSA-eligible health plan", True, key="ck_hsae")
        hsa_maxed = st.checkbox("Maxing the HSA", key="ck_hsa")
        backdoor = st.checkbox("Backdoor Roth done for both spouses", key="ck_bd")
    with z:
        has_kid = st.checkbox("Have a child", True, key="ck_kid")
        saving_529 = st.checkbox("Saving in a 529", key="ck_529")
        mega_avail = st.checkbox("Plan offers mega backdoor Roth", key="ck_mega_a")
        mega_used = st.checkbox("Using the mega backdoor", key="ck_mega") if mega_avail else False
    ladder = money_ladder(match_ok, card_debt, emergency, hsa_eligible, hsa_maxed, k401_maxed, backdoor, has_kid,
                          saving_529, mega_avail, mega_used, stock_share)
    done_count = sum(1 for _, ok, _, _ in ladder if ok)
    first = next(((rung, action, cat) for rung, ok, action, cat in ladder if ok is False), None)
    st.subheader("🪜 Your money priority ladder")
    st.progress(done_count / 9, text=f"{done_count} of 9 rungs done")
    if first:
        rung, action, cat = first
        st.success(md(f"👉 **Next rung: {rung}.** {action}"))
        st.button("Learn how →", key="ck_learn", on_click=go_to, args=(BY_TITLE[cat],))
    else:
        st.success("🎉 Every rung is done. Invest extra cash in broad index funds and review yearly.")
    ladder_rows = [{"Rung": r, "Status": "✅ Done" if ok else ("➡️ Then" if ok is None else "⬜ To do"), "Next action": act} for r, ok, act, _ in ladder]
    st.dataframe(ladder_rows, hide_index=True, width="stretch")
    st.subheader("🎂 Age milestones ahead")
    miles = milestones(age, birth_year)
    st.dataframe([{"Age": f"{m:g}", "Year (about)": birth_year + int(m), "Milestone": t} for m, t in miles], hide_index=True, width="stretch")
    st.subheader("📅 Year planner")
    md_table(["When", "What"], YEAR_PLAN)
    rows = ([{"Type": "Ladder", "Item": r["Rung"], "When/Status": r["Status"], "Detail": r["Next action"]} for r in ladder_rows]
            + [{"Type": "Milestone", "Item": t, "When/Status": f"Age {m:g}", "Detail": ""} for m, t in miles]
            + [{"Type": "Calendar", "Item": w, "When/Status": w, "Detail": what} for w, what in YEAR_PLAN])
    st.download_button("⬇️ Download my checklist (CSV)", to_csv(rows), "money-checkup.csv", "text/csv")
    links_row(["IRS 401(k) limits", "IRS IRA limits", "IRS withholding estimator", "SSA my Social Security"])
    mistakes_table([
        ("Skipping rungs", "Investing in taxable accounts while missing the match or carrying card debt.", "Climb the ladder in order."),
        ("Missing December 31 deadlines", "401(k) contributions and Roth conversions can't be done later.", "Set a December reminder."),
        ("Ignoring new limits each January", "You under-contribute for months.", "Update payroll % every January."),
    ])


# ---------------------------------------------------------------- Net-worth log

def load_log():
    upload = st.session_state.get("log_upload")
    if upload is None:
        return
    try:
        df = pd.read_csv(upload)
        df = df[[c for c in LOG_COLUMNS if c in df.columns]].reindex(columns=LOG_COLUMNS)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
        st.session_state.log_df = df
        st.session_state.log_error = False
    except Exception:
        st.session_state.log_error = True


def render_log():
    st.header("📈 Net-worth log")
    st.caption("Add a row each quarter (or month) with account balances in dollars. Download it as CSV to keep it, and upload it next time.")
    df = st.session_state.log_df.copy()
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date
    cfg = {"Date": st.column_config.DateColumn("Date", required=True)}
    cfg.update({c: st.column_config.NumberColumn(c, min_value=0, format="$%d") for c in LOG_COLUMNS[1:]})
    edited = st.data_editor(df, num_rows="dynamic", column_config=cfg, hide_index=True, width="stretch", key="log_editor")
    left, right = st.columns(2)
    left.download_button("⬇️ Download log (CSV)", edited.to_csv(index=False), "net-worth-log.csv", "text/csv", width="stretch")
    right.file_uploader("Upload a saved log", type="csv", key="log_upload", on_change=load_log)
    if st.session_state.get("log_error"):
        st.error("That file couldn't be read. Use a CSV downloaded from this page.")
    data = log_with_totals(edited.dropna(subset=["Date"])).sort_values("Date")
    if len(data):
        last = data.iloc[-1]
        a, b, c = st.columns(3)
        first_nw = data["Net worth"].iloc[0]
        a.metric("Net worth", money(last["Net worth"]), delta=money(last["Net worth"] - first_nw) + " since first entry", delta_color="normal")
        share = last["Company stock %"]
        b.metric("Company stock share", f"{share:.0f}%" if pd.notna(share) else "—", help="Target ≤ 10%")
        c.metric("Debts", money(last["Debts"] if pd.notna(last["Debts"]) else 0))
        if pd.notna(share) and share > 10:
            st.warning(f"🧺 Company stock is {share:.0f}% of net worth. Consider a sell plan to get under 10%.")
        st.line_chart(data, x="Date", y="Net worth")
        mix = {k: float(last[k]) for k in ASSETS if pd.notna(last[k]) and last[k] > 0}
        if mix:
            st.markdown("**🥧 Latest mix**")
            st.bar_chart({"Account": list(mix), "Dollars": list(mix.values())}, x="Account", y="Dollars", horizontal=True, sort=False)
    else:
        st.info("➕ Add your first row above: today's date and each balance you know.")
    mistakes_table([
        ("Checking daily", "Market noise causes anxiety and bad trades.", "Log quarterly and watch the trend."),
        ("Counting unvested RSUs", "They can disappear if you leave or the stock falls.", "Log vested shares only."),
        ("Using a hopeful home value", "Inflates net worth.", "Use a conservative estimate minus ~8% selling costs."),
    ])


# ---------------------------------------------------------------- Quiz

def render_quiz():
    st.header("📝 Quiz center")
    st.caption("Pick categories, answer, then check. Missed questions go to a review list so you can retry them.")
    missed = st.session_state.missed
    mode = st.segmented_control("Mode", ["🎲 New mix", f"🔁 My missed questions ({len(missed)})"], default="🎲 New mix", key="quiz_mode")
    review = bool(mode) and mode.startswith("🔁")
    a, b = st.columns([3, 1])
    cats = a.multiselect("Categories", CAT_NAMES, key="quiz_cats", placeholder="All categories")
    count = b.slider("Questions", 5, 30, 10)
    pool = [item for item in QUESTIONS if (not cats or item["category"] in cats) and (not review or item["q"] in missed)]
    if not pool:
        st.success("🎉 Nothing to review here. Take a new mix.") if review else st.info("No questions match. Clear the filter.")
        return
    rng = random.Random(st.session_state.quiz_seed)
    items = rng.sample(pool, min(count, len(pool)))
    st.button("🔀 New question set", on_click=new_quiz)
    seed = st.session_state.quiz_seed
    with st.form("quiz"):
        shown = []
        for i, item in enumerate(items):
            options, answer = shuffled_options(item)
            shown.append((options, answer))
            st.markdown(f"*{item['category']} · {item['topic']}*")
            st.radio(md(f"**Q{i + 1}.** {item['q']}"), options, index=None, key=f"quiz_{seed}_{i}")
        submitted = st.form_submit_button("✅ Check my answers", type="primary")
    if not submitted:
        return
    picks = [st.session_state.get(f"quiz_{seed}_{i}") for i in range(len(items))]
    score = quiz_score(items, picks)
    st.session_state.quiz_history.append((score, len(items)))
    for item, pick, (options, answer) in zip(items, picks, shown):
        (missed.discard if pick == options[answer] else missed.add)(item["q"])
    x, y, z = st.columns(3)
    x.metric("Score", f"{score} / {len(items)}")
    y.metric("Percent", f"{score / len(items):.0%}")
    z.metric("In review list", len(missed))
    if score / len(items) >= 0.8:
        st.success("🎉 Strong result. You know this well.")
    else:
        st.info("📖 Review the topics below, then retry with 'My missed questions'.")
    for i, (item, pick, (options, answer)) in enumerate(zip(items, picks, shown), 1):
        mark = "✅" if pick == options[answer] else "❌"
        st.markdown(md(f"{mark} **Q{i}. {item['q']}**  \nAnswer: **{options[answer]}**. {item['why']}  \n_Review: {item['category']} → {item['topic']}_"))


# ---------------------------------------------------------------- Calculators

def calc_growth():
    a, b, c = st.columns(3)
    start = dollars("Starting balance ($)", 100_000, "cg_start", col=a)
    monthly = dollars("Monthly investment ($)", 3_000, "cg_monthly", step=100, col=b)
    years = c.slider("Years", 1, 50, 20, key="cg_years")
    x, y = st.columns(2)
    rate = pct("Expected yearly return (%)", 7.0, "cg_rate", 20.0, col=x)
    inflation = pct("Inflation (%)", 3.0, "cg_inf", 10.0, col=y)
    end = future_value(start, monthly, rate, years)
    contributed = start + monthly * 12 * years
    today = end / (1 + inflation) ** years
    p, q, r = st.columns(3)
    p.metric("Ending balance", money(end))
    q.metric("In today's dollars", money(today), help="Adjusted for inflation")
    r.metric("Growth (not contributions)", money(end - contributed))
    rows = growth_by_year(start, monthly, rate, years)
    st.area_chart({"Year": [y for y, _, _ in rows], "Balance": [b for _, b, _ in rows], "Contributed": [c for _, _, c in rows]},
                  x="Year", y=["Contributed", "Balance"])
    wait = future_value(start, monthly, rate, max(0, years - 5))
    st.info(md(f"⏳ Waiting 5 years to start would cost about **{money(end - wait)}**. Rule of 72: money doubles about every **{rule_of_72(rate * 100):.0f} years** at {rate:.1%}."))
    st.caption("Monthly compounding; returns are not guaranteed and real markets are bumpy.")


def calc_fi():
    a, b, c = st.columns(3)
    spend = dollars("Yearly retirement spending, today's $", 140_000, "fi_spend", col=a)
    ss = dollars("Social Security + pensions per year ($)", 60_000, "fi_ss", col=b, help="From your my Social Security statements")
    wr = pct("Withdrawal rate (%)", 4.0, "fi_wr", 10.0, 0.25, col=c, help="4% for ~30 years; 3.25–3.5% for early retirement")
    x, y, z = st.columns(3)
    have = dollars("Invested today ($)", 900_000, "fi_have", col=x)
    monthly = dollars("Monthly investing ($)", 6_000, "fi_monthly", step=100, col=y)
    real = pct("Real return after inflation (%)", 5.0, "fi_real", 12.0, col=z)
    target = fi_number(spend, ss, wr)
    months = months_to_target(have, monthly, real, target)
    p, q, r = st.columns(3)
    p.metric("Your FI number", money(target), help=f"({money(spend)} − {money(ss)}) ÷ {wr:.2%}")
    q.metric("Progress", f"{have / target:.0%}" if target else "100%")
    r.metric("Years to FI", f"{months / 12:.1f}" if months is not None else "80+")
    st.progress(min(have / target, 1.0) if target else 1.0, text="Progress to financial independence")
    st.caption("All values in today's dollars. Social Security usually starts at 62–70; if you retire earlier, the gap years need extra savings (see 📅 Retirement projection).")


def calc_projection():
    a, b, c = st.columns(3)
    age = a.number_input("Your age", 18, 80, 40, key="pj_age")
    retire = b.number_input("Retire at", 40, 80, 58, key="pj_retire")
    real = pct("Real return (%)", 5.0, "pj_real", 12.0, col=c)
    x, y, z = st.columns(3)
    balance = dollars("Retirement savings today ($)", 900_000, "pj_bal", col=x)
    yearly = dollars("Yearly saving incl. match ($)", 70_000, "pj_save", col=y)
    spend = dollars("Yearly spending in retirement ($)", 140_000, "pj_spend", col=z)
    years = max(0, retire - age)
    at_retire = future_value(balance, yearly / 12, real, years)
    lasts, path = money_lasts(at_retire, spend, real, max_years=50)
    p, q, r = st.columns(3)
    p.metric(f"Balance at {retire} (today's $)", money(at_retire))
    q.metric("Supports at 4%", money(at_retire * 0.04) + "/yr")
    r.metric("Money lasts", f"to age {retire + lasts}" if lasts else f"past {retire + 50}")
    ages = list(range(age, retire + 1)) + list(range(retire + 1, retire + len(path)))
    balances = [future_value(balance, yearly / 12, real, a_ - age) for a_ in range(age, retire + 1)] + path[1:]
    st.line_chart({"Age": ages, "Balance (today's $)": balances}, x="Age", y="Balance (today's $)")
    st.caption("Ignores Social Security, which reduces withdrawals once it starts. Uses inflation-adjusted (real) returns, so all numbers are in today's dollars.")


def calc_401k():
    a, b, c = st.columns(3)
    salary = dollars("Salary (base) ($)", 220_000, "k_salary", col=a)
    age = b.number_input("Age this year", 18, 80, 40, key="k_age")
    contrib = pct("Your contribution (% of salary)", 8.0, "k_pct", 100.0, 1.0, col=c)
    x, y = st.columns(2)
    match_rate = pct("Employer match rate (% of your contribution)", 50.0, "k_mrate", 200.0, 5.0, col=x)
    match_cap = pct("Matched up to (% of salary)", 8.0, "k_mcap", 100.0, 1.0, col=y)
    m = employer_match(salary, contrib, match_rate, match_cap, age)
    limit = k401_employee_limit(age)
    room = after_tax_room(m["yours"], m["match"])
    p, q, r, s = st.columns(4)
    p.metric("You contribute", money(m["yours"]), help=f"Limit {money(limit)} at age {age}")
    q.metric("Employer match", money(m["match"]), delta=money(m["match"] - m["max_match"]) + " vs max" if m["match"] < m["max_match"] else "Full match ✅", delta_color="normal")
    r.metric("Room to your limit", money(max(0, limit - m["yours"])))
    s.metric("Mega backdoor room", money(room), help=f"{money(K401_TOTAL)} total − your regular deferral − match")
    pct_needed = min(limit, salary * match_cap) / salary if salary else 0
    st.info(md(f"🎯 Contribute at least **{pct_needed:.0%}** of salary for the full match, and **{limit / salary:.1%}** to hit the {money(limit)} limit." if salary else "Enter a salary."))
    st.caption("Some plans match per paycheck without a year-end true-up; spread contributions across the year in that case.")


def calc_roth():
    a, b = st.columns(2)
    amount = dollars("Pre-tax dollars to invest this year ($)", K401_EMPLOYEE, "r_amt", col=a)
    years = b.slider("Years until withdrawal", 1, 50, 20, key="r_years")
    x, y, z = st.columns(3)
    now = pct("Combined marginal rate now (%)", 41.3, "r_now", 60.0, col=x, help="e.g. 32% federal + 9.3% CA")
    later = pct("Expected rate in retirement (%)", 24.0, "r_later", 60.0, col=y, help="Lower if you'll retire in a lower bracket or leave CA")
    ret = pct("Yearly return (%)", 6.0, "r_ret", 15.0, col=z)
    r = roth_vs_traditional(amount, now, later, years, ret)
    p, q = st.columns(2)
    p.metric("Traditional, spendable after tax", money(r["traditional"]))
    q.metric("Roth, spendable", money(r["roth"]))
    winner = "Traditional" if r["traditional"] > r["roth"] else "Roth" if r["roth"] > r["traditional"] else "Tie"
    st.success(f"🏆 **{winner}** wins by {money(abs(r['traditional'] - r['roth']))}. Rule of thumb: whichever side has the lower tax rate wins.")
    st.caption("Assumes the same pre-tax dollars go in either way. Doesn't model RMDs, state moves, or investing the traditional tax savings.")


def calc_tax():
    a, b, c = st.columns(3)
    wages = dollars("Your salary + bonus ($)", 230_000, "t_w", col=a)
    rsu = dollars("Your RSU income this year ($)", 90_000, "t_rsu", col=b)
    spouse = dollars("Spouse's salary ($)", 60_000, "t_sp", col=c)
    x, y, z = st.columns(3)
    other = dollars("Other income (interest, gains) ($)", 5_000, "t_other", col=x)
    k401 = dollars("Pre-tax 401(k) total ($)", K401_EMPLOYEE, "t_401", col=y)
    hsa = dollars("HSA via payroll ($)", HSA_FAMILY, "t_hsa", col=z)
    i1, i2 = st.columns(2)
    item_fed = dollars("Federal itemized deductions (0 = standard)", 0, "t_ifed", col=i1, help="Mortgage interest, SALT (capped), charity")
    item_ca = dollars("California itemized deductions (0 = standard)", 0, "t_ica", col=i2, help="CA has no SALT cap but excludes state income tax")
    t = household_taxes(wages, rsu, other, k401, hsa, item_fed, item_ca, spouse)
    p, q, r, s = st.columns(4)
    p.metric("Federal income tax", money(t["federal"]), help=f"Taxable {money(t['fed_taxable'])}")
    q.metric("California income tax", money(t["california"]), help=f"Taxable {money(t['ca_taxable'])}")
    r.metric("Marginal rate (fed + CA)", f"{t['fed_marginal']:.0%} + {t['ca_marginal']:.1%}")
    s.metric("Effective total rate", f"{t['effective']:.1%}", help="All taxes incl. payroll ÷ gross income")
    parts = {"Federal": t["federal"], "California": t["california"], "Social Security": t["social_security"], "Medicare": t["medicare"], "CA SDI": t["sdi"]}
    st.bar_chart({"Tax": list(parts), "Dollars": list(parts.values())}, x="Tax", y="Dollars", horizontal=True, sort=False)
    st.caption(f"Married filing jointly, {TAX_YEAR} federal brackets and an approximate indexed California schedule. Excludes credits (child tax credit, CA exemption credits), AMT and NIIT. For filing, use the IRS and FTB tools.")


def calc_rsu():
    a, b, c = st.columns(3)
    vest = dollars("RSU value vesting this year ($)", 100_000, "rsu_v", col=a)
    fed = pct("Your federal marginal rate (%)", 32.0, "rsu_fed", 37.0, 1.0, col=b)
    ca = pct("Your California marginal rate (%)", 9.3, "rsu_ca", 13.3, 0.1, col=c)
    g = rsu_tax_gap(vest, fed, ca)
    p, q, r = st.columns(3)
    p.metric("Income tax owed on RSUs", money(g["owed"]))
    q.metric("Withheld (22% + 10.23%)", money(g["withheld"]))
    r.metric("Gap to cover", money(g["gap"]), delta="Owe more in April" if g["gap"] > 0 else "Over-withheld", delta_color="inverse")
    if g["gap"] > 0:
        st.warning(md(f"🧾 Set aside **{money(g['gap'])}** or add about **{money(g['gap'] / 24)}** per paycheck of extra W-4 withholding (24 pay periods)."))
    st.caption("Federal supplemental withholding is 22% on up to $1M of supplemental pay (37% above). Check the IRS Withholding Estimator for your full picture.")


def calc_espp():
    a, b, c = st.columns(3)
    offer = a.number_input("Offering-date price ($)", 1.0, 5000.0, 50.0, key="es_offer")
    purchase = b.number_input("Purchase-date price ($)", 1.0, 5000.0, 60.0, key="es_buy")
    sale = c.number_input("Sale price ($)", 1.0, 5000.0, 60.0, key="es_sale")
    x, y, z = st.columns(3)
    discount = pct("Discount (%)", 15.0, "es_disc", 15.0, 1.0, col=x)
    lookback = y.checkbox("Plan has a lookback", True, key="es_lb")
    contribution = dollars("Payroll saved this period ($)", 12_500, "es_amt", step=500, col=z)
    e = espp(offer, purchase, sale, discount, lookback, contribution)
    p, q, r, s = st.columns(4)
    p.metric("Price you pay", f"${e['price_paid']:,.2f}")
    q.metric("Shares", f"{e['shares']:,.1f}")
    r.metric("Gain if sold at sale price", money(e["gain"]))
    s.metric("Return", f"{e['return']:.1%}")
    st.info(md(f"🧾 On a quick sale, about **{money(e['ordinary_income'])}** (the discount) is taxed as ordinary income; any change after purchase is a capital gain or loss."))
    st.caption("The IRS caps ESPP purchases at $25,000 of stock (valued at the offering price) per calendar year.")


def calc_concentration():
    a, b, c = st.columns(3)
    stock = dollars("Company stock (vested) ($)", 300_000, "co_stock", col=a)
    nw = dollars("Total net worth ($)", 1_500_000, "co_nw", col=b)
    drop = pct("Hypothetical drop (%)", 50.0, "co_drop", 100.0, 5.0, col=c)
    r = concentration(stock, nw, drop)
    p, q, s = st.columns(3)
    p.metric("Share of net worth", f"{r['share']:.0%}", help="Target ≤ 10%")
    q.metric(f"Loss if it falls {drop:.0%}", money(r["loss"]), delta=f"−{r['loss_share']:.0%} of net worth", delta_color="off")
    s.metric("Sell to reach 10%", money(r["to_sell_for_10pct"]))
    if r["to_sell_for_10pct"] > 0:
        st.warning(md(f"🧺 Selling about **{money(r['to_sell_for_10pct'] / 8)} a quarter for 2 years** would bring you near 10% (before new vests). Sell the highest-basis lots first to keep taxes low."))
    else:
        st.success("✅ Company stock is within a 10% cap.")


def calc_rebalance():
    st.caption("Enter what you hold across all accounts and your target %. Targets should add up to 100.")
    names = ["US stocks", "International stocks", "Bonds", "Cash"]
    defaults = [(620_000, 55), (150_000, 25), (130_000, 15), (100_000, 5)]
    holdings, targets = {}, {}
    for name, (value, target) in zip(names, defaults):
        a, b = st.columns([2, 1])
        holdings[name] = dollars(f"{name} ($)", value, f"rb_h_{name}", col=a)
        targets[name] = b.number_input(f"Target % {name}", 0, 100, target, key=f"rb_t_{name}")
    total_t = sum(targets.values())
    if total_t != 100:
        st.error(f"Targets add up to {total_t}%. Adjust them to 100%.")
        return
    total = sum(holdings.values())
    trades = rebalance(holdings, targets)
    rows = [{"Asset": k, "Now": money(v), "Now %": f"{v / total:.0%}" if total else "—", "Target %": f"{targets[k]}%",
             "Trade": ("Buy " if trades[k] > 0 else "Sell " if trades[k] < 0 else "") + money(abs(trades[k]))} for k, v in holdings.items()]
    st.dataframe(rows, hide_index=True, width="stretch")
    drift = max(abs(100 * holdings[k] / total - targets[k]) for k in holdings) if total else 0
    (st.warning if drift >= 5 else st.success)(f"Largest drift: {drift:.1f} points " + ("→ time to rebalance (inside 401(k)/IRA first)." if drift >= 5 else "→ within the 5-point band."))


def calc_fees():
    a, b, c = st.columns(3)
    balance = dollars("Balance today ($)", 500_000, "fd_bal", col=a)
    monthly = dollars("Monthly investing ($)", 2_000, "fd_m", step=100, col=b)
    years = c.slider("Years", 1, 50, 30, key="fd_years")
    x, y, z = st.columns(3)
    ret = pct("Return before fees (%)", 7.0, "fd_ret", 15.0, col=x)
    low = pct("Low-cost fee (%)", 0.03, "fd_low", 3.0, 0.01, col=y)
    high = pct("Higher fee (%)", 1.0, "fd_high", 3.0, 0.05, col=z)
    f = fee_drag(balance, monthly, ret, years, low, high)
    p, q, r = st.columns(3)
    p.metric(f"With {low:.2%} fee", money(f["low"]))
    q.metric(f"With {high:.2%} fee", money(f["high"]))
    r.metric("Fees cost you", money(f["cost"]), delta=f"−{f['cost'] / f['low']:.0%} of ending balance" if f["low"] else None, delta_color="off")


def calc_529():
    a, b, c = st.columns(3)
    kid_age = a.number_input("Child's age", 0, 17, 8, key="c_age")
    cost = dollars("Yearly cost today ($)", 42_000, "c_cost", col=b, help="UC in-state total cost is roughly $40k+; private often $90k+")
    balance = dollars("529 balance today ($)", 40_000, "c_bal", col=c)
    x, y, z = st.columns(3)
    infl = pct("College cost inflation (%)", 5.0, "c_infl", 10.0, col=x)
    ret = pct("529 return (%)", 6.0, "c_ret", 12.0, col=y)
    share = pct("Share you want to cover (%)", 100.0, "c_share", 100.0, 5.0, col=z)
    p = college_plan(kid_age, cost * share, infl, balance, ret)
    m, n, o = st.columns(3)
    m.metric(f"4-year cost in {p['years']} years", money(p["future_cost"]))
    n.metric("Today's balance grows to", money(p["grown"]))
    o.metric("Monthly saving needed", money(p["monthly"]))
    st.progress(min(p["grown"] / p["future_cost"], 1.0) if p["future_cost"] else 1.0, text=f"{p['grown'] / p['future_cost']:.0%} funded by today's balance" if p["future_cost"] else "Funded")
    st.caption("California gives no state deduction for 529s. Grandparents can each give $19,000 a year ($95,000 with 5-year superfunding).")


def calc_emergency():
    st.caption("Enter essential monthly costs (what you'd still pay after a layoff).")
    items = {"🏠 Rent or mortgage + property tax": 4_800, "🛒 Food": 1_400, "💡 Utilities, phone, internet": 500, "🩺 Insurance (health/COBRA, auto, home)": 1_500,
             "🧒 Childcare and school": 1_200, "🚗 Car and transport": 600, "💳 Minimum debt payments": 0, "📦 Other essentials": 400}
    cols = st.columns(2)
    total = sum(dollars(label, value, f"ef_{i}", step=100, col=cols[i % 2]) for i, (label, value) in enumerate(items.items()))
    months = st.slider("Months to cover", 1, 12, 6, key="ef_months")
    have = dollars("Cash you have now ($)", 30_000, "ef_have")
    target = emergency_fund(total, months)
    a, b, c = st.columns(3)
    a.metric("Essential monthly costs", money(total))
    b.metric(f"{months}-month target", money(target))
    c.metric("Months covered now", f"{have / total:.1f}" if total else "—")
    st.progress(min(have / target, 1.0) if target else 1.0, text=f"{have / target:.0%} of target" if target else "")
    st.caption("If most pay comes from RSUs or one income, lean toward 6–12 months. Keep it in FDIC-insured savings or T-bills (state-tax free).")


def calc_ss():
    a, b = st.columns(2)
    pia = dollars("Benefit at full retirement age ($/month)", 3_600, "ss_pia", step=50, col=a, help="From your my Social Security statement")
    fra = b.selectbox("Full retirement age", [67, 66.5, 66], key="ss_fra", help="67 for anyone born in 1960 or later")
    ages = list(range(62, 71))
    benefits = [pia * ss_factor(age, fra) for age in ages]
    st.bar_chart({"Claim age": [str(a_) for a_ in ages], "Monthly benefit": benefits}, x="Claim age", y="Monthly benefit", sort=False)
    x, y, z = st.columns(3)
    x.metric("At 62", money(pia * ss_factor(62, fra)) + "/mo", delta=f"{ss_factor(62, fra):.0%} of full", delta_color="off")
    y.metric(f"At {fra:g}", money(pia) + "/mo")
    z.metric("At 70", money(pia * ss_factor(70, fra)) + "/mo", delta=f"{ss_factor(70, fra):.0%} of full", delta_color="off")
    be = ss_break_even(pia, 62, 70, fra)
    if be:
        st.info(f"⚖️ Claiming at 70 overtakes claiming at 62 in total dollars around **age {be:.0f}**. If you or your spouse may live past that, delaying usually pays.")
    st.caption("Uses SSA's reduction (5/9% a month for the first 36 months early, 5/12% after) and delayed credits (8% a year). Benefits also rise with yearly COLAs.")


def calc_lasts():
    a, b, c = st.columns(3)
    balance = dollars("Portfolio at retirement ($)", 3_000_000, "ml_bal", col=a)
    spend = dollars("Yearly withdrawal ($)", 120_000, "ml_spend", col=b)
    real = pct("Real return (%)", 4.0, "ml_real", 10.0, 0.5, col=c)
    years, path = money_lasts(balance, spend, real)
    years_low, path_low = money_lasts(balance, spend, real - 0.02)
    x, y, z = st.columns(3)
    x.metric("Withdrawal rate", f"{spend / balance:.1%}" if balance else "—", help="3.5–4% is a common starting range")
    y.metric("Lasts", f"{years} years" if years else "60+ years")
    z.metric("If returns are 2 points lower", f"{years_low} years" if years_low else "60+ years")
    n = max(len(path), len(path_low))
    pad = lambda p: p + [0] * (n - len(p))  # noqa: E731
    st.line_chart({"Year": list(range(n)), "Expected": pad(path), "2 points lower": pad(path_low)}, x="Year", y=["Expected", "2 points lower"])
    st.caption("Today's dollars, withdrawals taken at the start of each year. Real markets vary year to year; a bad first few years (sequence risk) shortens these numbers.")


def calc_life():
    a, b, c = st.columns(3)
    income = dollars("Income to replace per year ($)", 200_000, "li_inc", col=a, help="Take-home pay your family relies on")
    years = b.slider("Years of income", 0, 30, 15, key="li_years")
    debts = dollars("Mortgage and other debts ($)", 900_000, "li_debt", col=c)
    x, y, z = st.columns(3)
    college = dollars("College funding ($)", 250_000, "li_col", col=x)
    final = dollars("Final costs and buffer ($)", 50_000, "li_fin", col=y)
    savings = dollars("Savings and investments ($)", 900_000, "li_sav", col=z)
    existing = dollars("Existing life insurance ($)", 440_000, "li_exist", help="Include work coverage (often 1–2× salary), but it ends if you leave")
    need = life_insurance_need(income, years, debts, college, final, savings, existing)
    p, q = st.columns(2)
    p.metric("Estimated additional coverage", money(need))
    q.metric("As a multiple of income", f"{need / income:.1f}×" if income else "—")
    st.caption("A simple needs-based estimate. Get quotes for level term (20–25 years) for both spouses; a non-working spouse needs coverage too.")


CALC_FUNCS = dict(zip(CALCS, [calc_growth, calc_fi, calc_projection, calc_401k, calc_roth, calc_tax, calc_rsu, calc_espp,
                              calc_concentration, calc_rebalance, calc_fees, calc_529, calc_emergency, calc_ss, calc_lasts, calc_life]))


def render_calculators():
    st.header("🧮 Calculators")
    st.caption("Estimates to guide decisions, not tax or investment advice. Defaults show an example Bay Area tech family; change them to yours.")
    choice = st.segmented_control("Calculator", CALCS, key="calc") or CALCS[0]
    st.subheader(choice)
    CALC_FUNCS[choice]()
    mistakes_table([
        ("Treating estimates as promises", "Returns, tax law and inflation all change.", "Use them for direction; recheck yearly."),
        ("Using optimistic returns", "Plans fail in ordinary markets.", "Use 5–6% real for stocks, less for mixed portfolios."),
    ])


# ---------------------------------------------------------------- Search and about

def render_search():
    st.header("🔎 Search everything")
    query = st.text_input("Search topics, tips, limits and the glossary", placeholder="e.g. backdoor, wash sale, RSU, 529")
    if not query.strip():
        st.caption("Try: match, HSA, wash sale, ESPP, Social Security, umbrella, 4% rule.")
        return
    words = query.lower().split()

    def hit(text):
        text = text.lower()
        return all(w in text for w in words)

    found = 0
    for cat, t in TOPICS:
        blob = " ".join([t["title"], t["gist"], t["purpose"], t["plain"], t["example"], t["target"], t["metric"],
                         *t["insights"], *t["tips"], *t["do"], *t["dont"], *(a for _, a in t["actions"])])
        if hit(blob):
            found += 1
            with st.container(border=True):
                left, right = st.columns([5, 1], vertical_alignment="center")
                left.markdown(md(f"**{t['icon']} {t['title']}** · {cat['name']}  \n{t['gist']}"))
                right.button("Open →", key=f"search_{t['title']}", on_click=go_to, args=(cat["name"],))
    for item, value, note, _ in LIMITS:
        if hit(f"{item} {value} {note}"):
            found += 1
            st.markdown(md(f"🔢 **{item}** ({TAX_YEAR}): {value} · {note}"))
    for term, meaning in GLOSSARY.items():
        if hit(term + " " + meaning):
            found += 1
            st.markdown(md(f"📖 **{term}**: {meaning}"))
    if not found:
        st.info("No matches. Try a shorter word.")


def render_about():
    st.header("📚 Sources & method")
    st.markdown(TOP_20_NOTE)
    st.markdown(PERSONA)
    st.markdown(
        "**How the content was written.** All text is original plain-language wording based on guidance from the IRS, SSA, SEC "
        "(Investor.gov), FINRA, CFPB, FDIC, Treasury, the California Franchise Tax Board and other agencies, plus investor-education "
        "pages from large brokers. Examples use illustrative families, not real people. Fund tickers are examples of fund types, not "
        f"recommendations. Limits are for {TAX_YEAR}; the IRS announces new ones each fall."
    )
    st.warning("🧭 " + DISCLAIMER)
    st.subheader("🔗 All sources")
    st.dataframe([{"Source": n, "Link": u} for n, u in SOURCES.items()], hide_index=True, width="stretch",
                 column_config={"Link": st.column_config.LinkColumn("Link", display_text="Open ↗")})
    st.subheader("🧮 Formulas used")
    md_table(["Calculator", "Formula or source"], [
        ("Compound growth", "FV = P(1+r/12)^(12n) + monthly × ((1+r/12)^(12n) − 1) ÷ (r/12)"),
        ("Real return", "(1 + nominal) ÷ (1 + inflation) − 1"),
        ("FI number", "(spending − guaranteed income) ÷ withdrawal rate (4% → 25×)"),
        ("Taxes", f"{TAX_YEAR} IRS joint brackets and standard deduction; approximate indexed CA schedule; FICA 6.2% to ${184_500:,}, Medicare 1.45% + 0.9% over $250k"),
        ("RSU gap", "Vest value × (fed + CA marginal) − vest value × (22% + 10.23%)"),
        ("ESPP", "Price paid = lower of offer/purchase price × (1 − discount) with lookback"),
        ("Social Security", "SSA: −5/9% per month for 36 months early, −5/12% after; +2/3% per month delayed to 70"),
        ("529", "Future cost = Σ cost × (1 + college inflation)^year; monthly = gap × r ÷ ((1+r)^n − 1)"),
        ("Life insurance", "Income × years + debts + college + final costs − savings − existing coverage"),
        ("Savings rate → years", "n = ln(1 + r × (1−s) ÷ (w × s)) ÷ ln(1 + r)"),
    ])
    st.caption(f"Example: a 25% savings rate gives about {years_to_fi(0.25):.0f} years to FI at 5% real; 50% gives about {years_to_fi(0.5):.0f}. "
               f"401(k) limit {money(K401_EMPLOYEE)}, IRA {money(IRA_LIMIT)} per person, total 401(k) {money(K401_TOTAL)}. Real return at 7% nominal and 3% inflation: {real_rate(0.07, 0.03):.1%}.")
    mistakes_table([
        ("Using this app instead of a professional for complex cases", "ISOs, big RSU sales and estate plans have many traps.", "Bring your numbers to a fee-only fiduciary or CPA."),
    ])


if section == HOME:
    render_home()
elif section == PLAN:
    render_plan()
elif section == CHEATSHEET:
    render_cheatsheet()
elif section in CAT_NAMES:
    render_category(CAT_NAMES.index(section))
elif section == CHECKUP:
    render_checkup()
elif section == LOG:
    render_log()
elif section == QUIZ:
    render_quiz()
elif section == CALCULATORS:
    render_calculators()
elif section == SEARCH:
    render_search()
else:
    render_about()
