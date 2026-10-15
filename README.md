# 📈 Stocks & Retirement FAQs

One Streamlit app to learn, plan and track the most important stock, investing, tax and retirement topics for a Silicon Valley tech household: a TPM in California with a spouse and an elementary-school child, paid in salary plus RSUs/ESPP, with goals of college, a home and a comfortable (maybe early) retirement. It follows the layout of [longevity-faqs](https://github.com/chennab12/longevity-faqs): dashboard, key numbers, gist and insights, tips, do/don't, next steps, quick checks, calculators, a planner, a tracker and a quiz center.

## Pages

- 🏠 **My dashboard**: progress, a ▶️ continue button, this month's 10 money habits with a score, 8 key 2026 numbers, the 10 highest-impact moves, every category as a card, and 🚩 red flags for scams and account takeover.
- 🗺️ **12-week money plan**: one money task a week (cash, 401(k), IRAs/HSA, RSUs, taxes, fees, allocation, 529, FI number, Social Security, insurance and estate), with dates, checkboxes and CSV download.
- 📌 **Master cheatsheet**: 2026 limits and thresholds with IRS/SSA links, every topic, key number, KPI, tip, mistake and glossary term on one page, with CSV downloads.
- **14 categories, 43 topics** in four groups:
  - 🧭 Foundations: Money foundations · How investing works · Mindset, myths & scams
  - 🏦 Accounts & taxes: 401(k) & workplace plans · IRAs & HSA · Taxes: federal & California · Equity comp: RSUs, ESPP & options
  - 📈 Invest: Index funds & ETFs · Portfolio & allocation · Stocks, bonds & cash basics
  - 🏖️ Family, retire & protect: Family goals (529, home, kids) · Your retirement number · Retirement income (Social Security & withdrawals) · Protect (insurance & estate)

  Every category has 4 key numbers, a visual cue, a "what to know and do" table, a KPI table, related calculator buttons, a common-mistakes table and previous/next buttons. Every topic has a 🎯 gist, 🧭 why it matters, 🗣️ plain-words explanation, 💡 worked example with numbers, 🏁 target, 🔑 3 insights, 🪄 3 tips/tricks/hacks, ✅ do / ⛔ don't, 🚀 next steps (today, this week, this month), 🧪 a small experiment, 📏 what to track, 🔗 trusted sources and a 📝 two-question quick check.
- 🧭 **Money checkup & year planner**: answer a few yes/no questions to get your money priority ladder and next rung, age milestones (catch-up, rule of 55, 59½, Social Security, Medicare, RMDs), and a yearly calendar (backdoor Roth, estimated tax dates, open enrollment, tax-loss harvesting, December 31 deadlines). CSV download.
- 📈 **Net-worth log**: an editable table of account balances (cash, 401(k)/IRA, Roth, HSA, 529, brokerage, company stock, home equity, debts) with net worth and company-stock % computed, charts and CSV download/upload.
- 📝 **Quiz center**: 86 questions with explanations, category filters and a missed-questions review list.
- 🧮 **16 calculators**: compound growth, retirement (FI) number, retirement projection, 401(k) match & max (with mega backdoor room), Roth vs traditional, federal + California tax estimator, RSU withholding gap, ESPP return, concentration check, allocation & rebalance, fee drag, 529 college, emergency fund, Social Security claiming age, how long will it last, and life insurance need.
- 🔎 **Search everything** (topics, 2026 limits, glossary) and 📚 **Sources & method** (all sources, formulas, disclaimer).
- 💾 **Save or restore progress** in the sidebar. **Deep links**: `?page=iras-hsa` opens a section directly.

## About the content

"Most important" is a curated editorial judgement, not a measured ranking. All text is original plain-language wording. Every link goes to a US government or California agency (IRS, SSA, SEC/Investor.gov, CFPB, FDIC, Treasury, DOL, FTB), a regulator (FINRA, SIPC) or a major broker's education pages; a test enforces the allowed domains. There are no stock picks or return promises; fund tickers appear only as examples of fund types.

**This is general education, not financial, tax or legal advice.** Calculators are estimates from the assumptions shown. Limits are for tax year 2026 and the California tax table is an approximation of the indexed schedule: update `calculations.py`, `content.py` (`KEY_NUMBERS`, `LIMITS`) and the `topics_*.py` files each November when the IRS and FTB publish new figures.

Content lives in `topics_foundations.py`, `topics_accounts.py`, `topics_invest.py` and `topics_retire.py`; sources, limits, habits, the plan and red flags are in `content.py`; the math is in `calculations.py`.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Run the tests with `pip install pytest && python -m pytest -q`. GitHub Actions runs them on every push. For Streamlit Community Cloud, deploy this repository with `app.py` as the entry point.
