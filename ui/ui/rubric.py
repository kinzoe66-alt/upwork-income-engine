import re

# Simple, deterministic rubric (no AI). Tune weights anytime.
# Score is bounded 0..100.
RUBRIC = [
    # Positive signals
    {"key": "budget_present", "weight": 18, "pattern": r"\$\s?\d+|\bbudget\b|\brate\b|\bper hour\b|\bhourly\b|\bfixed\b"},
    {"key": "clear_deliverables", "weight": 16, "pattern": r"\bdeliverable(s)?\b|\bmilestone(s)?\b|\brequirements\b|\bscope\b|\bacceptance\b"},
    {"key": "timeline_present", "weight": 10, "pattern": r"\bdeadline\b|\btimeline\b|\bby\s+\w+\b|\bwithin\s+\d+\s+(day|week|month)s?\b"},
    {"key": "long_term", "weight": 10, "pattern": r"\blong[- ]term\b|\bongoing\b|\bretainer\b|\bmonthly\b|\bmaintenance\b"},
    {"key": "tech_stack_present", "weight": 12, "pattern": r"\bpython\b|\bflask\b|\bapi\b|\baws\b|\bgcp\b|\bazure\b|\bpostgres\b|\bmysql\b|\bdocker\b|\bkubernetes\b"},
    {"key": "good_client_language", "weight": 8, "pattern": r"\blooking for\b|\bseeking\b|\bneed\b|\bwe would like\b|\bplease\b"},

    # Risk / red flags (negative)
    {"key": "unpaid_trial", "weight": -25, "pattern": r"\bunpaid\b|\bfree\b|\bno pay\b|\btrial task\b"},
    {"key": "vague_scope", "weight": -14, "pattern": r"\bnot sure\b|\bfigure it out\b|\bwhatever\b|\banything\b|\basap\b"},
    {"key": "urgent_pressure", "weight": -10, "pattern": r"\basap\b|\burgent\b|\bimmediately\b|\bright now\b"},
    {"key": "suspicious_access", "weight": -18, "pattern": r"\bpassword\b|\badmin access\b|\broot access\b|\bgive me credentials\b"},
    {"key": "payment_off_platform", "weight": -30, "pattern": r"\boff platform\b|\bpaypal\b|\bvenmo\b|\bcashapp\b|\bwire\b|\btelegram\b|\bwhatsapp\b"},
]

def detect_signals(text: str):
    t = text.strip()
    hits = []
    for rule in RUBRIC:
        if re.search(rule["pattern"], t, flags=re.IGNORECASE):
            hits.append(rule)
    return hits
