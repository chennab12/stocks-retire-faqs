"""Animated step cues with reduced-motion, dark-mode and narrow-screen support."""
from html import escape

import streamlit as st

# Rendered inline with st.html (no iframe), so every class is prefixed to avoid clashing with Streamlit's own CSS.
STYLE = """
.cue-wrap{--bg1:#e8f1fb;--bg2:#f4f8fd;--card:#fff;--line:#b8cfe8;--ink:#0f2a4a;--accent:#1f6fd1;
  border:1px solid var(--line);border-radius:16px;background:linear-gradient(110deg,var(--bg1),var(--bg2));padding:14px;font-family:system-ui,Arial,sans-serif}
@media(prefers-color-scheme:dark){.cue-wrap{--bg1:#0f1a2b;--bg2:#142238;--card:#13233a;--line:#2f4f7a;--ink:#d9e7fa;--accent:#6aa8f5}}
.cue-title{font-size:17px;font-weight:750;color:var(--ink);margin:0 0 10px}
.cue-steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
.cue-card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:10px 12px;animation:cue-glow 4.8s infinite}
.cue-num{font-size:15px;font-weight:800;color:var(--accent)}
.cue-label{font-size:14px;font-weight:650;color:var(--ink)}
.cue-c1{animation-delay:1.2s}.cue-c2{animation-delay:2.4s}.cue-c3{animation-delay:3.6s}
@keyframes cue-glow{20%{box-shadow:0 4px 10px var(--accent)}}
@media(prefers-reduced-motion:reduce){.cue-card{animation:none}}
"""


def show(title, stages):
    """Render a compact numbered step cue that wraps on narrow screens."""
    cards = "".join(
        f'<div class="cue-card cue-c{i}"><div class="cue-num">{i + 1:02}</div><div class="cue-label">{escape(label)}</div></div>'
        for i, label in enumerate(stages)
    )
    st.html(
        f"<style>{STYLE}</style>"
        f'<div class="cue-wrap" role="img" aria-label="{escape(title)}: {escape(" to ".join(stages))}">'
        f'<p class="cue-title">{escape(title)} · visual memory cue</p><div class="cue-steps">{cards}</div></div>'
    )
