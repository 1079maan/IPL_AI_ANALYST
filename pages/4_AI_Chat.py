"""
pages/4_AI_Chat.py — IPL NEXUS · Professional AI Chat

Features:
  1. Before chat starts → Data Overview Cards + Topic Categories only
  2. When model cannot answer → friendly "Can't Answer" message card
  3. ChatGPT-style clean chat bubbles
  4. Data limitation detection with yellow warning
  5. SQL Validator active
"""

import streamlit as st
import pandas as pd
import re
import time
import sys
import os

ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

from style         import GLOBAL_CSS, sidebar_html, sidebar_nav
from db            import run_query, test_connection
from sql_generator import generate_sql
from sql_validator import validate_sql
from charts        import auto_chart

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="IPL NEXUS · AI Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Barlow+Condensed:wght@300;400;500;600;700&family=Barlow:wght@300;400;500&display=swap');

#MainMenu,footer,header{visibility:hidden;}
[data-testid="stSidebarNav"]{display:none!important;}

/* ── Chat wrapper ── */
.chat-wrapper{max-width:880px;margin:0 auto;padding:0 1rem 6rem;}

/* ── Message rows ── */
.msg-row{display:flex;gap:1rem;margin:1.2rem 0;align-items:flex-start;}
.msg-row.user{flex-direction:row-reverse;}
.msg-row.bot{flex-direction:row;}

/* ── Avatars ── */
.avatar{
  flex-shrink:0;width:36px;height:36px;border-radius:50%;
  display:flex;align-items:center;justify-content:center;
  font-size:.95rem;font-weight:700;font-family:'Orbitron',sans-serif;
}
.avatar-user{
  background:linear-gradient(135deg,var(--orange),#FF7A30);
  color:var(--void);box-shadow:0 0 12px rgba(255,77,0,.4);
}
.avatar-bot{
  background:linear-gradient(135deg,var(--void3),var(--void4));
  border:1px solid var(--border-c);color:var(--cyan);
  box-shadow:0 0 12px rgba(0,240,255,.2);
}

/* ── Bubbles ── */
.bubble{max-width:78%;padding:.9rem 1.2rem;font-size:.92rem;line-height:1.7;color:var(--text);}
.bubble-user{
  background:linear-gradient(135deg,rgba(255,77,0,.15),rgba(255,77,0,.06));
  border:1px solid rgba(255,77,0,.3);border-radius:18px 4px 18px 18px;
}
.bubble-bot{
  background:var(--void2);border:1px solid rgba(255,255,255,.07);
  border-radius:4px 18px 18px 18px;
}
.msg-time{
  font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
  color:var(--muted);margin-top:.25rem;
}
.msg-row.user .msg-time{text-align:right;}

/* ── SQL code ── */
.sql-code{
  background:var(--void3);border:1px solid var(--border-o);
  border-left:3px solid var(--orange);border-radius:0 8px 8px 8px;
  padding:.9rem 1.1rem;font-family:'Courier New',monospace;
  font-size:.78rem;color:var(--cyan);white-space:pre-wrap;
  word-break:break-word;line-height:1.7;margin-top:.4rem;
}

/* ── Validation badges ── */
.v-badge{
  display:inline-flex;align-items:center;gap:.3rem;
  font-family:'Barlow Condensed',sans-serif;font-size:.62rem;
  font-weight:600;letter-spacing:.1em;text-transform:uppercase;
  padding:.2rem .6rem;
  clip-path:polygon(6px 0,100% 0,calc(100% - 6px) 100%,0 100%);
  margin-left:.5rem;
}
.v-valid    {background:rgba(0,240,255,.1); color:var(--cyan);}
.v-corrected{background:rgba(255,77,0,.12);color:var(--orange);}
.v-blocked  {background:rgba(255,77,0,.2); color:#FF6B6B;}

/* ── Result label ── */
.result-label{
  font-family:'Barlow Condensed',sans-serif;font-size:.65rem;
  font-weight:700;letter-spacing:.22em;text-transform:uppercase;
  color:var(--muted);margin:1rem 0 .4rem;
  display:flex;align-items:center;gap:.6rem;
}
.result-label::after{
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,var(--border-o),transparent);
}

/* ── Explanation ── */
.explain{
  background:rgba(0,240,255,.04);border-left:2px solid var(--cyan);
  padding:.6rem .9rem;font-size:.84rem;color:var(--muted2);
  line-height:1.6;margin-top:.6rem;border-radius:0 6px 6px 0;
}

/* ── Limitation box ── */
.limit-box{
  background:rgba(255,200,0,.06);border:1px solid rgba(255,200,0,.25);
  border-left:3px solid #FFC107;border-radius:0 8px 8px 0;
  padding:.9rem 1.1rem;font-size:.86rem;color:var(--text);
  line-height:1.8;margin-top:.4rem;
}
.limit-title{
  font-family:'Barlow Condensed',sans-serif;font-size:.7rem;
  font-weight:700;letter-spacing:.18em;text-transform:uppercase;
  color:#FFC107;margin-bottom:.5rem;
}

/* ── CANNOT ANSWER card ── */
.cant-answer{
  background:rgba(255,77,0,.05);
  border:1px solid rgba(255,77,0,.2);
  border-left:3px solid var(--orange);
  border-radius:0 12px 12px 0;
  padding:1.2rem 1.4rem;
  margin-top:.4rem;
}
.cant-title{
  font-family:'Barlow Condensed',sans-serif;font-size:.72rem;
  font-weight:700;letter-spacing:.2em;text-transform:uppercase;
  color:var(--orange);margin-bottom:.6rem;
  display:flex;align-items:center;gap:.5rem;
}
.cant-body{
  font-family:'Barlow',sans-serif;font-size:.88rem;
  color:var(--text);line-height:1.8;margin-bottom:.8rem;
}
.cant-suggest{
  font-family:'Barlow Condensed',sans-serif;font-size:.78rem;
  color:var(--muted2);letter-spacing:.04em;
  border-top:1px solid rgba(255,77,0,.15);
  padding-top:.7rem;margin-top:.4rem;line-height:2;
}
.cant-suggest b{color:var(--orange);}

/* ── Error ── */
.err-box{
  background:rgba(255,77,0,.08);border-left:2px solid var(--orange);
  padding:.6rem .9rem;font-size:.82rem;color:#FF8A80;
  border-radius:0 6px 6px 0;margin-top:.5rem;
}

/* ── Typing dots ── */
@keyframes bounce{0%,80%,100%{transform:translateY(0);}40%{transform:translateY(-6px);}}
.dot{
  display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--orange);margin:0 2px;
  animation:bounce 1.2s infinite ease-in-out;
}
.dot:nth-child(2){animation-delay:.15s;background:#FF7A30;}
.dot:nth-child(3){animation-delay:.30s;background:var(--cyan);}

/* ── Chat input ── */
[data-testid="stChatInput"]{
  background:var(--void2)!important;
  border-top:1px solid var(--border-o)!important;
  padding:.8rem 1rem!important;
}
[data-testid="stChatInput"] textarea{
  background:var(--void3)!important;border:1px solid var(--border-o)!important;
  border-radius:12px!important;color:var(--text)!important;
  font-family:'Barlow',sans-serif!important;font-size:.95rem!important;
}
[data-testid="stChatInput"] textarea:focus{
  border-color:var(--orange)!important;
  box-shadow:0 0 0 2px rgba(255,77,0,.15)!important;
}
[data-testid="stChatInput"] button{
  background:var(--orange)!important;border-radius:8px!important;border:none!important;
}

/* ── Sidebar buttons ── */
.stButton>button{
  background:var(--void3)!important;border:1px solid rgba(255,255,255,.07)!important;
  color:var(--muted2)!important;font-family:'Barlow Condensed',sans-serif!important;
  font-size:.78rem!important;border-radius:6px!important;
  padding:.4rem .8rem!important;width:100%!important;
  text-align:left!important;text-transform:none!important;
  font-weight:400!important;clip-path:none!important;
  transition:all .15s ease!important;letter-spacing:.04em!important;
}
.stButton>button:hover{
  background:rgba(255,77,0,.1)!important;
  border-color:var(--border-o)!important;color:var(--orange)!important;
  transform:none!important;box-shadow:none!important;
}

/* ── DataFrames ── */
[data-testid="stDataFrame"]{border:1px solid var(--border-o)!important;border-radius:6px!important;}
[data-testid="stDataFrame"] th{
  background:var(--void3)!important;color:var(--orange)!important;
  font-family:'Barlow Condensed',sans-serif!important;font-size:.78rem!important;
  letter-spacing:.1em!important;text-transform:uppercase!important;
}
[data-testid="stDataFrame"] td{background:var(--void2)!important;color:var(--text)!important;font-size:.85rem!important;}

/* ── Metrics ── */
[data-testid="stMetric"]{
  background:var(--void3)!important;border:1px solid var(--border-o)!important;
  border-top:2px solid var(--orange)!important;border-radius:6px!important;
  padding:.7rem 1rem!important;clip-path:none!important;
}
[data-testid="stMetricValue"]{color:var(--cyan)!important;font-family:'Orbitron',sans-serif!important;font-size:1.3rem!important;}
[data-testid="stMetricLabel"]{
  color:var(--muted2)!important;font-family:'Barlow Condensed',sans-serif!important;
  font-size:.68rem!important;letter-spacing:.12em!important;text-transform:uppercase!important;
}

/* ── Expander ── */
[data-testid="stExpander"]{
  background:var(--void3)!important;border:1px solid rgba(255,255,255,.07)!important;border-radius:8px!important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:var(--void2);}
::-webkit-scrollbar-thumb{background:var(--orange);border-radius:2px;}

/* ══ EMPTY STATE ══ */

/* Data stat card */
.stat-card{
  background:var(--void3);border:1px solid rgba(255,255,255,.07);
  border-top:2px solid var(--orange);border-radius:8px;
  padding:1rem 1.2rem;text-align:center;transition:all .2s ease;
}
.stat-card:hover{border-top-color:var(--cyan);transform:translateY(-2px);}
.stat-val{
  font-family:'Orbitron',sans-serif;font-size:1.5rem;font-weight:700;
  color:var(--cyan);line-height:1.1;
}
.stat-lbl{
  font-family:'Barlow Condensed',sans-serif;font-size:.68rem;
  font-weight:600;letter-spacing:.18em;text-transform:uppercase;
  color:var(--muted);margin-top:.3rem;
}
.stat-sub{font-family:'Barlow',sans-serif;font-size:.72rem;color:var(--muted2);margin-top:.15rem;}

/* Topic card */
.topic-card{
  background:var(--void3);border:1px solid rgba(255,255,255,.06);
  border-radius:10px;padding:1rem;transition:all .2s ease;
}
.topic-card:hover{border-color:var(--border-o);background:rgba(255,77,0,.04);transform:translateY(-2px);}
.topic-icon{font-size:1.5rem;margin-bottom:.5rem;display:block;}
.topic-name{
  font-family:'Barlow Condensed',sans-serif;font-size:.85rem;
  font-weight:700;letter-spacing:.06em;text-transform:uppercase;
  color:var(--text);margin-bottom:.3rem;
}
.topic-desc{font-family:'Barlow',sans-serif;font-size:.75rem;color:var(--muted2);line-height:1.5;}
.topic-count{
  font-family:'Barlow Condensed',sans-serif;font-size:.63rem;
  letter-spacing:.1em;text-transform:uppercase;color:var(--orange);margin-top:.5rem;
}

/* Section heading */
.sec-head{
  font-family:'Orbitron',sans-serif;font-size:.75rem;font-weight:700;
  letter-spacing:.12em;text-transform:uppercase;color:var(--text);
  margin:1.6rem 0 .8rem;display:flex;align-items:center;gap:.7rem;
}
.sec-head::after{
  content:'';flex:1;height:1px;
  background:linear-gradient(90deg,var(--border-o),transparent);
}

/* Live dot */
@keyframes pulse-dot{
  0%,100%{opacity:1;box-shadow:0 0 4px var(--cyan);}
  50%{opacity:.4;box-shadow:0 0 12px var(--cyan);}
}
.live-dot{
  display:inline-block;width:7px;height:7px;border-radius:50%;
  background:var(--cyan);animation:pulse-dot 1.5s infinite;
  vertical-align:middle;margin-right:.4rem;
}

/* Hint bar at bottom of empty state */
.hint-bar{
  text-align:center;padding:1.2rem 0 .5rem;
  font-family:'Barlow Condensed',sans-serif;font-size:.76rem;
  letter-spacing:.14em;text-transform:uppercase;color:var(--muted);
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════
if "messages"   not in st.session_state: st.session_state.messages   = []
if "pending_q"  not in st.session_state: st.session_state.pending_q  = None
if "db_ok"      not in st.session_state: st.session_state.db_ok      = None

# ══════════════════════════════════════════════════════════════════════════════
#  DATA CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
DATA_STATS = [
    ("1,169",   "Matches",    "2008 – 2025"),
    ("277,873", "Deliveries", "Ball-by-ball"),
    ("925",     "Players",    "All IPL players"),
    ("18",      "Seasons",    "Complete data"),
    ("2,365",   "Innings",    "All innings"),
    ("118+",    "Venues",     "Across India"),
]

TOPICS = [
    ("🏏", "Batting",  "Runs, averages, strike rates, sixes, fours",     "8 question types"),
    ("🎯", "Bowling",  "Wickets, economy rates, dot balls, powerplay",   "7 question types"),
    ("🏆", "Teams",    "Wins, toss impact, season performance",          "6 question types"),
    ("📈", "Trends",   "Season-wise stats, over-by-over analysis",       "6 question types"),
    ("🏟️", "Venues",   "Ground stats, venue scores, location data",      "4 question types"),
    ("⭐", "Awards",   "Player of match, super overs, milestones",       "3 question types"),
]

# ══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    sidebar_nav()

    st.markdown('<div style="height:1px;background:linear-gradient(90deg,var(--orange),transparent);margin:.8rem 0;"></div>', unsafe_allow_html=True)

    if st.button("🔌  Test DB Connection"):
        with st.spinner("Connecting…"):
            st.session_state.db_ok = test_connection()
    if st.session_state.db_ok is True:
        st.markdown('<p style="font-family:\'Barlow Condensed\',sans-serif;font-size:.75rem;color:var(--cyan);margin:.3rem 0;">✅ PostgreSQL · Connected</p>', unsafe_allow_html=True)
    elif st.session_state.db_ok is False:
        st.markdown('<p style="font-family:\'Barlow Condensed\',sans-serif;font-size:.75rem;color:var(--orange);margin:.3rem 0;">❌ PostgreSQL · Offline</p>', unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:linear-gradient(90deg,var(--orange),transparent);margin:.8rem 0;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Barlow Condensed\',sans-serif;font-size:.62rem;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;">Quick Questions</div>', unsafe_allow_html=True)

    QUICK = [
        "🏏  Top 10 batsmen all time",
        "🎯  Top wicket takers",
        "🏆  Which team has most wins",
        "📈  Runs per season trend",
        "💥  Most sixes in IPL",
        "🪙  Toss impact on results",
        "⭐  Player of match awards",
        "🎳  Best economy bowlers",
    ]
    for s in QUICK:
        if st.button(s, key=f"q_{s}"):
            st.session_state.pending_q = s.split("  ", 1)[-1]

    st.markdown('<div style="height:1px;background:linear-gradient(90deg,var(--orange),transparent);margin:.8rem 0;"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding:.7rem;background:rgba(0,240,255,.03);border:1px solid var(--border-c);border-radius:6px;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.6rem;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;">System</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.76rem;color:var(--muted2);line-height:2.1;">
            🤖 Groq · LLaMA3-70B<br>🛡️ SQL Validator · Active<br>🗄️ PostgreSQL · IPL_Data<br>⚡ IPL 2008–2025
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:linear-gradient(90deg,var(--orange),transparent);margin:.8rem 0;"></div>', unsafe_allow_html=True)
    if st.button("🗑  Clear Chat", key="clr"):
        st.session_state.messages = []
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  PAGE HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div style="max-width:880px;margin:0 auto 1.2rem;padding:0 1rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;
              padding:.8rem 1.4rem;background:var(--void2);
              border-bottom:1px solid var(--border-o);border-radius:10px 10px 0 0;">
    <div style="display:flex;align-items:center;gap:.9rem;">
      <div style="width:40px;height:40px;border-radius:50%;
                  background:linear-gradient(135deg,var(--void3),var(--void4));
                  border:1px solid var(--border-c);
                  display:flex;align-items:center;justify-content:center;font-size:1.2rem;">🏏</div>
      <div>
        <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;
                    color:#fff;letter-spacing:.04em;">
          IPL NEXUS <span style="color:var(--orange);">AI</span>
        </div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;
                    letter-spacing:.14em;text-transform:uppercase;color:var(--muted);">
          <span class="live-dot"></span>Groq LLaMA3 · SQL Validator · PostgreSQL · IPL 2008–2025
        </div>
      </div>
    </div>
    <div style="display:flex;gap:.4rem;">
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;font-weight:600;
                   letter-spacing:.1em;text-transform:uppercase;
                   background:rgba(0,240,255,.08);border:1px solid var(--border-c);
                   color:var(--cyan);padding:.2rem .6rem;border-radius:4px;">NL → SQL</span>
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:.62rem;font-weight:600;
                   letter-spacing:.1em;text-transform:uppercase;
                   background:rgba(255,77,0,.08);border:1px solid var(--border-o);
                   color:var(--orange);padding:.2rem .6rem;border-radius:4px;">Live DB</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  EMPTY STATE — Data Cards + Topic Categories only
# ══════════════════════════════════════════════════════════════════════════════
def show_empty_state():
    st.markdown('<div style="max-width:880px;margin:0 auto;padding:0 1rem;">', unsafe_allow_html=True)

    # Welcome line
    st.markdown("""
    <div style="text-align:center;padding:1.5rem 1rem .5rem;">
        <div style="font-family:'Barlow',sans-serif;font-size:.95rem;color:var(--muted2);line-height:1.8;">
            Ask any IPL cricket question in plain English —
            the AI generates SQL and queries the live database instantly.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── FEATURE 1: Data Overview Cards ───────────────────────────────────────
    st.markdown('<div class="sec-head">📊 Available Data</div>', unsafe_allow_html=True)

    cols = st.columns(6)
    for col, (val, lbl, sub) in zip(cols, DATA_STATS):
        with col:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-val">{val}</div>
                <div class="stat-lbl">{lbl}</div>
                <div class="stat-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    # ── FEATURE 2: Topic Categories ──────────────────────────────────────────
    st.markdown('<div class="sec-head">🗂️ Topics You Can Ask About</div>', unsafe_allow_html=True)

    tcols = st.columns(6)
    for col, (icon, name, desc, count) in zip(tcols, TOPICS):
        with col:
            st.markdown(f"""
            <div class="topic-card">
                <span class="topic-icon">{icon}</span>
                <div class="topic-name">{name}</div>
                <div class="topic-desc">{desc}</div>
                <div class="topic-count">{count}</div>
            </div>""", unsafe_allow_html=True)

    # Bottom hint
    st.markdown('<div class="hint-bar">↓ &nbsp; Type your question below to get started &nbsp; ↓</div>',
                unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CANNOT ANSWER MESSAGE — shown when model has no answer
# ══════════════════════════════════════════════════════════════════════════════
def render_cant_answer(question: str):
    """
    Professional friendly card shown when model cannot find an answer.
    Tells user exactly why + what they CAN ask instead.
    """
    st.markdown(f"""
    <div class="cant-answer">
        <div class="cant-title">🤔 &nbsp; Cannot Find Answer</div>
        <div class="cant-body">
            I could not find an answer for <b>"{question}"</b> in the IPL dataset.<br>
            This may be because:
            <br>• The data for this question is <b>not recorded</b> in the dataset
            <br>• The question needs data from <b>outside cricket statistics</b>
            <br>• Try rephrasing your question more specifically
        </div>
        <div class="cant-suggest">
            <b>✅ Questions I CAN answer:</b><br>
            🏏 &nbsp;Top 10 batsmen all time &nbsp;|&nbsp;
            🎯 &nbsp;Top wicket takers &nbsp;|&nbsp;
            🏆 &nbsp;Which team has most wins<br>
            📈 &nbsp;Runs per season trend &nbsp;|&nbsp;
            💥 &nbsp;Most sixes in IPL &nbsp;|&nbsp;
            🪙 &nbsp;Toss impact on results<br>
            🏟️ &nbsp;Highest average score venue &nbsp;|&nbsp;
            ⭐ &nbsp;Player of match awards &nbsp;|&nbsp;
            🎳 &nbsp;Best economy bowlers
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RENDER ONE MESSAGE
# ══════════════════════════════════════════════════════════════════════════════
def render_message(msg: dict):
    ts = msg.get("time", "")

    # ── User bubble ───────────────────────────────────────────────────────────
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="chat-wrapper">
          <div class="msg-row user">
            <div>
              <div class="bubble bubble-user">{msg['content']}</div>
              <div class="msg-time">{ts}</div>
            </div>
            <div class="avatar avatar-user">M</div>
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # ── Bot bubble ────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="chat-wrapper">
      <div class="msg-row bot">
        <div class="avatar avatar-bot">⚡</div>
        <div style="flex:1;min-width:0;">
    """, unsafe_allow_html=True)

    # ── Data limitation → yellow warning ─────────────────────────────────────
    if msg.get("limited"):
        explanation = msg.get("explanation", "")
        explanation = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', explanation)
        explanation = re.sub(r'\*(.*?)\*',     r'<em>\1</em>', explanation)
        explanation = explanation.replace('\n', '<br>')
        st.markdown(f"""
        <div class="limit-box">
            <div class="limit-title">⚠️ Data Not Available in Dataset</div>
            {explanation}
        </div>""", unsafe_allow_html=True)
        if not msg.get("sql"):
            st.markdown('</div></div></div>', unsafe_allow_html=True)
            return

    # ── Cannot answer → friendly card ────────────────────────────────────────
    elif msg.get("cant_answer"):
        render_cant_answer(msg.get("question", "your question"))
        st.markdown('</div></div></div>', unsafe_allow_html=True)
        return

    # ── Greeting / simple reply → clean bubble ────────────────────────────────
    elif not msg.get("sql"):
        exp = msg.get("explanation", "I could not understand that question. Please try again.")
        exp = exp.replace('\n', '<br>').replace('•', '&bull;')
        st.markdown(f"""
        <div class="bubble bubble-bot" style="max-width:90%;">{exp}</div>
        <div class="msg-time">{ts}</div>
        """, unsafe_allow_html=True)
        st.markdown('</div></div></div>', unsafe_allow_html=True)
        return

    # ── SQL expander ──────────────────────────────────────────────────────────
    if msg.get("sql"):
        vstatus = msg.get("validation_status", "")
        vnote   = msg.get("validation_note", "")
        badge = ""
        if vstatus == "valid":
            badge = '<span class="v-badge v-valid">✓ Validated</span>'
        elif vstatus == "corrected":
            badge = '<span class="v-badge v-corrected">⚡ Corrected</span>'
        elif vstatus == "blocked":
            badge = '<span class="v-badge v-blocked">🚫 Blocked</span>'

        src    = msg.get("source", "fallback")
        slabel = "Groq · LLaMA3" if src == "groq" else "Template"
        stag   = "v-valid" if src == "groq" else ""
        elabel = "📊  View Suggested SQL" if msg.get("limited") else f"🔍  View Generated SQL  {vstatus.upper() if vstatus else ''}"

        with st.expander(elabel, expanded=False):
            st.markdown(f'<div class="sql-code">{msg["sql"].strip()}</div>',
                        unsafe_allow_html=True)
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:.5rem;margin-top:.5rem;flex-wrap:wrap;">
                <span class="v-badge" style="background:rgba(255,255,255,.05);color:var(--muted2);">
                    Source: {slabel}
                </span>{badge}
            </div>""", unsafe_allow_html=True)

    # ── Error ─────────────────────────────────────────────────────────────────
    if msg.get("error"):
        err = msg["error"]
        if "connect" in err.lower() or "connection" in err.lower():
            friendly = "Unable to connect to the database. Please check your PostgreSQL connection."
        elif "column" in err.lower() or "relation" in err.lower():
            friendly = "The query referenced an invalid column. Please try rephrasing."
        elif "syntax" in err.lower():
            friendly = "There was a SQL syntax issue. Please try rephrasing your question."
        else:
            friendly = "Something went wrong. Please try a different question."
        st.markdown(f'<div class="err-box">⚠️ &nbsp;{friendly}</div>',
                    unsafe_allow_html=True)

    # ── Results table ─────────────────────────────────────────────────────────
    df = msg.get("df")
    if df is not None and not df.empty:
        label = "📊 Closest Available Answer" if msg.get("limited") else "Query Results"
        st.markdown(f'<div class="result-label">{label}</div>', unsafe_allow_html=True)

        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])][:4]
        if num_cols:
            for col, nc in zip(st.columns(min(len(num_cols), 4)), num_cols):
                with col:
                    st.metric(nc.replace("_", " ").title(),
                              f"{df[nc].sum():,.0f}", f"{len(df)} rows")

        st.dataframe(df, use_container_width=True,
                     height=min(380, 55 + len(df) * 36))

    # ── Chart ─────────────────────────────────────────────────────────────────
    if msg.get("fig") is not None:
        st.markdown('<div class="result-label">Visualisation</div>', unsafe_allow_html=True)
        st.plotly_chart(msg["fig"], use_container_width=True,
                        config={"displayModeBar": False})

    # ── Explanation ───────────────────────────────────────────────────────────
    if msg.get("explanation") and not msg.get("limited"):
        st.markdown(f'<div class="explain">💡 &nbsp;{msg["explanation"]}</div>',
                    unsafe_allow_html=True)

    st.markdown('</div></div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RENDER HISTORY OR EMPTY STATE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.messages:
    for m in st.session_state.messages:
        render_message(m)
else:
    show_empty_state()


# ══════════════════════════════════════════════════════════════════════════════
#  PROCESS QUESTION
# ══════════════════════════════════════════════════════════════════════════════
def process_question(question: str):
    now = time.strftime("%H:%M")

    # Add user message
    st.session_state.messages.append({
        "role": "user", "content": question, "time": now
    })
    render_message(st.session_state.messages[-1])

    bot = {
        "role": "bot", "content": "", "time": now,
        "sql": None, "error": None, "df": None,
        "fig": None, "explanation": None,
        "source": "fallback", "limited": False,
        "cant_answer": False, "question": question,
        "validation_status": None, "validation_note": None,
    }

    # Typing indicator
    typing = st.empty()
    typing.markdown("""
    <div class="chat-wrapper">
      <div class="msg-row bot">
        <div class="avatar avatar-bot">⚡</div>
        <div class="bubble bubble-bot" style="padding:.75rem 1rem;">
          <span class="dot"></span><span class="dot"></span><span class="dot"></span>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    time.sleep(0.5)
    typing.empty()

    # ── Step 1: Generate SQL (includes limitation + greeting check) ───────────
    gen                = generate_sql(question)
    raw_sql            = gen.get("sql", "").strip()
    bot["explanation"] = gen.get("explanation", "")
    bot["source"]      = gen.get("source", "fallback")
    bot["limited"]     = gen.get("limited", False)
    chart_type         = gen.get("chart_type", "bar")
    chart_x            = gen.get("chart_x")
    chart_y            = gen.get("chart_y")

    # ── Step 2: Validate SQL (skip for limitations) ───────────────────────────
    if raw_sql and not bot["limited"]:
        validated                = validate_sql(question, raw_sql)
        bot["sql"]               = validated.get("validated_sql", raw_sql).strip()
        bot["validation_status"] = validated.get("status", "skipped")
        bot["validation_note"]   = validated.get("explanation", "")
    else:
        bot["sql"] = raw_sql

    # ── Step 3: Run on PostgreSQL ─────────────────────────────────────────────
    if bot["sql"]:
        df, err      = run_query(bot["sql"])
        bot["df"]    = df
        bot["error"] = err

        # ── Step 4: Build chart ───────────────────────────────────────────────
        if df is not None and not df.empty:
            bot["fig"] = auto_chart(df, chart_type, chart_x, chart_y,
                                    title=question[:60])

        # ── Step 5: If DB returned nothing → mark as cant_answer ─────────────
        if df is None and err is None:
            bot["cant_answer"] = True
        if df is not None and df.empty and not bot["limited"]:
            bot["cant_answer"] = True

    # ── If no SQL generated and not a limitation/greeting → cant_answer ───────
    if not bot["sql"] and not bot["limited"] and not bot["explanation"]:
        bot["cant_answer"] = True

    st.session_state.messages.append(bot)
    st.rerun()


# ── Triggers ──────────────────────────────────────────────────────────────────
if st.session_state.pending_q:
    q = st.session_state.pending_q
    st.session_state.pending_q = None
    process_question(q)

if q := st.chat_input("Ask anything about IPL cricket…"):
    process_question(q)