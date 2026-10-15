"""Stocks & Retirement FAQs content: sources, key numbers, monthly habits, the 12-week plan and red flags.

Every link points to a US government agency, a California state agency, a regulator, or a major investor-education
page. Topic content lives in the topics_*.py files. Dollar limits are for tax year 2026; update them each November.
"""
import topics_accounts
import topics_foundations
import topics_invest
import topics_retire

REVIEWED = "15 October 2026"
TAX_YEAR = 2026

PERSONA = (
    "Written for a Silicon Valley tech professional (for example a TPM) in California, married, with an elementary-school "
    "child: salary plus RSUs/ESPP, a 401(k) at work, high federal and California tax brackets, and goals of college, a "
    "home and a comfortable (maybe early) retirement."
)

TOP_20_NOTE = (
    "\"Most important\" is a curated editorial judgement, not a measured ranking. Topics were picked because regulators "
    "and agencies (SEC, FINRA, IRS, SSA, CFPB) stress them, they apply to most tech households, and they give the biggest "
    "financial benefit for the effort."
)

DISCLAIMER = (
    "General education, not financial, tax or legal advice. No stock picks and no promised returns: markets can lose money. "
    "Tax rules and limits change every year; confirm with the linked IRS/FTB pages or a fiduciary adviser or CPA before "
    "acting. Calculators give rough estimates from the assumptions shown."
)

SOURCES = {
    # Getting started and investor protection
    "Investor.gov getting started": "https://www.investor.gov/introduction-investing",
    "Investor.gov investing basics": "https://www.investor.gov/introduction-investing/investing-basics",
    "Investor.gov compound interest calculator": "https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator",
    "Investor.gov asset allocation": "https://www.investor.gov/introduction-investing/getting-started/asset-allocation",
    "Investor.gov risk tolerance": "https://www.investor.gov/introduction-investing/getting-started/assessing-your-risk-tolerance",
    "Investor.gov fees": "https://www.investor.gov/introduction-investing/getting-started/understanding-fees",
    "Investor.gov retirement": "https://www.investor.gov/additional-resources/retirement-toolkit",
    "Investor.gov protect your investments": "https://www.investor.gov/protect-your-investments",
    "SEC EDGAR": "https://www.sec.gov/edgar/search/",
    "SEC tips & complaints": "https://www.sec.gov/tcr",
    "FINRA BrokerCheck": "https://brokercheck.finra.org/",
    "FINRA Fund Analyzer": "https://tools.finra.org/fund_analyzer/",
    "FINRA investor insights": "https://www.finra.org/investors/insights",
    "SIPC": "https://www.sipc.org/for-investors/what-sipc-protects",
    "FDIC deposit insurance": "https://www.fdic.gov/resources/deposit-insurance",
    "FTC credit freeze": "https://consumer.ftc.gov/articles/what-know-about-credit-freezes-and-fraud-alerts",
    "FTC report fraud": "https://reportfraud.ftc.gov/",
    "IdentityTheft.gov": "https://www.identitytheft.gov/",
    "FBI IC3": "https://www.ic3.gov/",
    # Consumer money
    "CFPB money tools": "https://www.consumerfinance.gov/consumer-tools/",
    "CFPB debt": "https://www.consumerfinance.gov/consumer-tools/credit-cards/",
    "CFPB emergency fund": "https://www.consumerfinance.gov/an-essential-guide-to-building-an-emergency-fund/",
    "CFPB owning a home": "https://www.consumerfinance.gov/owning-a-home/",
    "CFPB retirement planning": "https://www.consumerfinance.gov/consumer-tools/retirement/",
    "TreasuryDirect T-bills": "https://www.treasurydirect.gov/marketable-securities/treasury-bills/",
    "TreasuryDirect I bonds": "https://www.treasurydirect.gov/savings-bonds/i-bonds/",
    "BLS CPI": "https://www.bls.gov/cpi/",
    # Retirement accounts
    "IRS 401(k) limits": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-401k-and-profit-sharing-plan-contribution-limits",
    "IRS COLA limits": "https://www.irs.gov/retirement-plans/cola-increases-for-dollar-limitations-on-benefits-and-contributions",
    "IRS IRA limits": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-ira-contribution-limits",
    "IRS Roth IRAs": "https://www.irs.gov/retirement-plans/roth-iras",
    "IRS Roth comparison": "https://www.irs.gov/retirement-plans/roth-comparison-chart",
    "IRS Pub 590-A": "https://www.irs.gov/publications/p590a",
    "IRS Pub 590-B": "https://www.irs.gov/publications/p590b",
    "IRS rollover chart": "https://www.irs.gov/pub/irs-tege/rollover_chart.pdf",
    "IRS RMDs": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-required-minimum-distributions-rmds",
    "IRS early withdrawal exceptions": "https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-exceptions-to-tax-on-early-distributions",
    "IRS Pub 969 (HSA)": "https://www.irs.gov/publications/p969",
    "DOL retirement plans": "https://www.dol.gov/general/topic/retirement",
    "DOL lost & found": "https://lostandfound.dol.gov/",
    # Taxes
    "IRS tax brackets": "https://www.irs.gov/filing/federal-income-tax-rates-and-brackets",
    "IRS withholding estimator": "https://www.irs.gov/individuals/tax-withholding-estimator",
    "IRS estimated taxes": "https://www.irs.gov/businesses/small-businesses-self-employed/estimated-taxes",
    "IRS capital gains (Topic 409)": "https://www.irs.gov/taxtopics/tc409",
    "IRS Pub 550": "https://www.irs.gov/publications/p550",
    "IRS NIIT": "https://www.irs.gov/individuals/net-investment-income-tax",
    "IRS Pub 525": "https://www.irs.gov/publications/p525",
    "IRS stock options (Topic 427)": "https://www.irs.gov/taxtopics/tc427",
    "IRS Form 3922": "https://www.irs.gov/forms-pubs/about-form-3922",
    "IRS home sale (Topic 701)": "https://www.irs.gov/taxtopics/tc701",
    "IRS estate tax": "https://www.irs.gov/businesses/small-businesses-self-employed/estate-tax",
    "IRS gift tax": "https://www.irs.gov/businesses/small-businesses-self-employed/frequently-asked-questions-on-gift-taxes",
    "CA FTB": "https://www.ftb.ca.gov/",
    "CA FTB tax rates": "https://www.ftb.ca.gov/file/personal/tax-calculator-tables-rates.asp",
    # Family, retirement income, protection
    "IRS 529 plans (Topic 313)": "https://www.irs.gov/taxtopics/tc313",
    "IRS Pub 970": "https://www.irs.gov/publications/p970",
    "ScholarShare 529": "https://www.scholarshare529.com/",
    "Federal Student Aid": "https://studentaid.gov/",
    "SSA my Social Security": "https://www.ssa.gov/myaccount/",
    "SSA claiming age effect": "https://www.ssa.gov/benefits/retirement/planner/agereduction.html",
    "SSA delayed credits": "https://www.ssa.gov/benefits/retirement/planner/delayret.html",
    "SSA spouse benefits": "https://www.ssa.gov/benefits/retirement/planner/applying7.html",
    "SSA life expectancy": "https://www.ssa.gov/oact/population/longevity.html",
    "SSA disability": "https://www.ssa.gov/disability",
    "Medicare.gov": "https://www.medicare.gov/basics/get-started-with-medicare",
    "Covered California": "https://www.coveredca.com/",
    "CA Department of Insurance": "https://www.insurance.ca.gov/",
    "California Earthquake Authority": "https://www.earthquakeauthority.com/",
    "CA courts self-help": "https://selfhelp.courts.ca.gov/",
    # Broker education (no product endorsement)
    "Vanguard investor education": "https://investor.vanguard.com/investor-resources-education",
    "Fidelity learning center": "https://www.fidelity.com/learning-center/overview",
}

ALLOWED_DOMAINS = (
    ".gov", "finra.org", "sipc.org", "scholarshare529.com", "coveredca.com", "earthquakeauthority.com",
    "vanguard.com", "fidelity.com",
)

CATEGORIES = topics_foundations.CATEGORIES + topics_accounts.CATEGORIES + topics_invest.CATEGORIES + topics_retire.CATEGORIES
for _c in CATEGORIES:
    _c["name"] = f"{_c['icon']} {_c['title']}"
GROUPS = list(dict.fromkeys(c["group"] for c in CATEGORIES))

# Key 2026 numbers for the dashboard: (label, value, note).
KEY_NUMBERS = [
    ("🏢 401(k) you", "$24,500", "2026 employee limit; +$8,000 at 50+, +$11,250 at 60–63"),
    ("🚀 401(k) total", "$72,000", "Employee + employer + after-tax (mega backdoor room)"),
    ("🪙 IRA each", "$7,500", "Backdoor Roth if joint MAGI is above $242k–$252k"),
    ("🩺 HSA family", "$8,750", "Needs a high-deductible plan; CA taxes HSAs"),
    ("🎓 529 gift", "$19,000", "Per giver per child per year; $95k with 5-year superfunding"),
    ("🛟 Emergency fund", "6 months", "Of essential expenses, in T-bills or high-yield savings"),
    ("💸 Fund fees", "< 0.10%", "Weighted average expense ratio"),
    ("🧺 Company stock", "≤ 10%", "Of net worth, with a written sell plan"),
]

# Full table of 2026 limits and thresholds for the cheatsheet: (item, 2026 value, note, source name).
LIMITS = [
    ("401(k)/403(b) employee deferral", "$24,500", "Traditional + Roth combined", "IRS 401(k) limits"),
    ("401(k) catch-up, age 50+", "$8,000", "Must be Roth if prior-year FICA wages > $150,000", "IRS 401(k) limits"),
    ("401(k) super catch-up, ages 60–63", "$11,250", "Replaces the regular catch-up at those ages", "IRS 401(k) limits"),
    ("401(k) total (415(c))", "$72,000", "Employee + employer + after-tax, excluding catch-up", "IRS COLA limits"),
    ("IRA contribution", "$7,500", "+$1,100 catch-up at 50+", "IRS IRA limits"),
    ("Roth IRA phase-out (joint)", "$242,000–$252,000", "MAGI; use the backdoor above it", "IRS Roth IRAs"),
    ("HSA (self / family)", "$4,400 / $8,750", "+$1,000 at 55+; not tax-free in California", "IRS Pub 969 (HSA)"),
    ("Standard deduction (joint)", "$32,200", "Federal; compare with itemizing", "IRS tax brackets"),
    ("24% bracket ends (joint)", "$403,550", "Taxable income; 32% to $512,450, 35% to $768,700", "IRS tax brackets"),
    ("0% long-term gains (joint)", "≤ $98,900", "15% up to $613,700, then 20%", "IRS capital gains (Topic 409)"),
    ("Net investment income tax", "3.8% over $250k", "Joint MAGI threshold (not indexed)", "IRS NIIT"),
    ("Social Security wage base", "$184,500", "6.2% employee tax stops above this", "SSA my Social Security"),
    ("Annual gift exclusion", "$19,000", "Per giver per recipient", "IRS gift tax"),
    ("Estate tax exemption", "$15,000,000", "Per person", "IRS estate tax"),
    ("ESPP purchase cap", "$25,000", "Stock value at offering price per calendar year", "IRS Form 3922"),
    ("RSU federal supplemental withholding", "22% (37% over $1M)", "Often below your real marginal rate", "IRS Pub 525"),
    ("Capital-loss offset", "$3,000", "Against ordinary income per year; rest carries forward", "IRS capital gains (Topic 409)"),
    ("Home-sale gain exclusion (joint)", "$500,000", "Owned and lived in 2 of last 5 years", "IRS home sale (Topic 701)"),
    ("529 → Roth IRA rollover", "$35,000 lifetime", "529 open 15+ years; federal rule (check CA)", "IRS 529 plans (Topic 313)"),
    ("RMD start age", "75 (born 1960+)", "73 if born 1951–1959", "IRS RMDs"),
]

# Ten monthly money habits for the dashboard; each maps to the category that explains it.
MONTHLY_HABITS = [
    ("📊", "Updated net worth and checked savings rate", "Money foundations"),
    ("🤖", "Automatic investing ran every paycheck", "How investing works"),
    ("💳", "Paid every credit card in full", "Money foundations"),
    ("🛟", "Emergency fund at target (or growing)", "Money foundations"),
    ("🏢", "On pace to max the 401(k) and get the full match", "401(k) & workplace plans"),
    ("📦", "Sold vested RSUs / ESPP shares per my written plan", "Equity comp: RSUs, ESPP & options"),
    ("🧾", "Tax withholding on track (no April surprise)", "Taxes: federal & California"),
    ("🥧", "Allocation within 5 points of target", "Portfolio & allocation"),
    ("📵", "No panic trades, no tips acted on", "Mindset, myths & scams"),
    ("👨‍👩‍👧", "Had a money chat with my spouse (and kid)", "Family goals: college, home & kids"),
]

# Ten highest-leverage actions, in suggested order.
FAST_TRACK = [
    ("🎁", "Get every dollar of the 401(k) match", "401(k) & workplace plans"),
    ("💳", "Pay off credit cards and other high-interest debt", "Money foundations"),
    ("🛟", "Hold 6 months of essential expenses in cash", "Money foundations"),
    ("🪙", "Max the 401(k), HSA and two backdoor Roth IRAs", "IRAs & HSA"),
    ("🧺", "Cap company stock at 10% of net worth with a sell plan", "Equity comp: RSUs, ESPP & options"),
    ("🧾", "Close the RSU withholding gap before April", "Taxes: federal & California"),
    ("💸", "Move to low-cost broad index funds (< 0.10%)", "Index funds & ETFs"),
    ("🥧", "Write a target allocation and rebalance yearly", "Portfolio & allocation"),
    ("🛡️", "Get term life, disability, umbrella and a will with a guardian", "Protect: insurance & estate"),
    ("🎯", "Know your FI number and Social Security estimate", "Your retirement number"),
]

# A 12-week starter plan: one money task a week, building on the last.
PLAN_12_WEEKS = [
    (1, "📊 Measure", "Log net worth, savings rate and every account in the 📈 Net-worth log.", "Money foundations"),
    (2, "🛟 Cash", "Size your emergency fund; move it to high-yield savings or T-bills.", "Money foundations"),
    (3, "🏢 401(k)", "Get the full match, set the max, check for a mega backdoor Roth.", "401(k) & workplace plans"),
    (4, "🪙 IRAs & HSA", "Backdoor Roth for both spouses; invest the HSA.", "IRAs & HSA"),
    (5, "📦 Equity", "Estimate the RSU tax gap; write a sell-at-vest and ESPP rule.", "Equity comp: RSUs, ESPP & options"),
    (6, "🧾 Taxes", "Run the IRS Withholding Estimator; set specific-lot cost basis.", "Taxes: federal & California"),
    (7, "💸 Fees", "Fee audit; switch expensive funds to index funds.", "Index funds & ETFs"),
    (8, "🥧 Allocation", "Write a one-page investment plan and rebalance.", "Portfolio & allocation"),
    (9, "🎓 Family", "529 plan and contribution; start kid money jars.", "Family goals: college, home & kids"),
    (10, "🎯 FI number", "Calculate your retirement number and projected FI age.", "Your retirement number"),
    (11, "🪪 Income plan", "Download Social Security statements; sketch withdrawal order.", "Retirement income: Social Security & withdrawals"),
    (12, "🛡️ Protect", "Term life, disability, umbrella quotes; book estate documents.", "Protect: insurance & estate"),
]

# Red flags shown on the dashboard: (flag, what it looks like, what to do).
RED_FLAGS = [
    ("🎣 'Guaranteed' high returns", "No-risk promises, secret strategies, pressure to act today.", "Walk away; check FINRA BrokerCheck; report at sec.gov/tcr"),
    ("💘 Online 'friend' with an investing app", "Someone met online or by a wrong-number text shows big crypto gains, then asks for 'fees' to withdraw.", "Stop sending money; report at ic3.gov and reportfraud.ftc.gov"),
    ("🏛️ Fake IRS, SSA or bank calls", "Threats of arrest; demands for gift cards, wires or crypto.", "Hang up; call the agency at its official number"),
    ("🔐 Account takeover signs", "Password-reset emails you didn't request, new payees, unknown logins.", "Call your broker; change passwords; freeze credit; IdentityTheft.gov"),
    ("📈 Pump-and-dump tips", "Group chats or social posts hyping tiny stocks.", "Ignore; read the company's SEC filings"),
    ("🧓 A parent being targeted", "A secretive new 'adviser', sudden large withdrawals or wires.", "Add a trusted contact on their accounts; Elder Fraud Hotline 1-833-372-8311"),
]

GLOSSARY = {
    "401(k)": "A workplace retirement account with tax breaks; contributions come straight from your paycheck.",
    "Asset allocation": "How your money is split between stocks, bonds and cash.",
    "Backdoor Roth": "A non-deductible traditional IRA contribution converted to a Roth IRA, used when income is above Roth limits.",
    "Basis (cost basis)": "What you paid for an investment, used to compute gain or loss. For RSUs it's the value at vest.",
    "Bear market": "A fall of 20% or more from a recent high.",
    "Capital gain": "Profit when you sell an investment for more than its basis. Long-term means held over 1 year.",
    "Dollar-cost averaging": "Investing a fixed amount on a schedule regardless of price.",
    "ESPP": "Employee Stock Purchase Plan: buy company stock through payroll at a discount (up to 15%).",
    "Expense ratio": "A fund's yearly cost as a % of your balance.",
    "FI number": "The invested amount that can fund your spending indefinitely, roughly 25× yearly spending.",
    "HSA": "Health Savings Account: deductible, tax-free growth and tax-free medical withdrawals (federal).",
    "Index fund": "A fund that owns every stock (or bond) in a market index at very low cost.",
    "IRMAA": "Higher Medicare premiums charged when income (from 2 years earlier) is above set thresholds.",
    "Marginal tax rate": "The tax rate on your next dollar of income.",
    "Mega backdoor Roth": "After-tax 401(k) contributions converted to Roth, up to the $72k total limit.",
    "P/E ratio": "Stock price divided by yearly earnings per share.",
    "Pro-rata rule": "Makes part of an IRA conversion taxable if you hold any pre-tax IRA money.",
    "Rebalancing": "Trading back to your target allocation after markets move.",
    "RMD": "Required minimum distribution: yearly withdrawals from pre-tax accounts starting at 73 or 75.",
    "RSU": "Restricted stock unit: company shares that become yours (and taxable) when they vest.",
    "Sequence risk": "The danger of poor returns early in retirement while you're withdrawing.",
    "Tax-loss harvesting": "Selling an investment at a loss to offset gains, then buying a similar one.",
    "Wash sale": "Buying the same or a substantially identical security within 30 days of a loss sale; the loss is disallowed.",
}
