import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from style import GLOBAL_CSS, sidebar_html, sidebar_nav

st.set_page_config(
    page_title="CricIntel · Home",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    sidebar_nav()

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="neon-hero">
    <div class="hero-eyebrow">
        <span class="live-dot"></span> IPL 2026 SEASON PLATFORM — POWERED BY MACHINE LEARNING &amp; AI
    </div>
    <div class="hero-title">
        ANALYZE.<br>PREDICT.<br><span>WIN WITH DATA.</span>
    </div>
    <div class="hero-sub">
        The platform integrates advanced data analytics, interactive dashboards,
        and a trained ML model to generate real-time match predictions.
    </div>
    <div style="display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1.4rem;">
        <span class="nx-tag tag-o">ML Predictions</span>
        <span class="nx-tag tag-c">AI Chat · NL→SQL</span>
        <span class="nx-tag tag-w">250K+ Deliveries</span>
        <span class="nx-tag tag-o">17 Seasons</span>
        <span class="nx-tag tag-c">Power BI Embedded</span>
        <span class="nx-tag tag-w">PostgreSQL Backend</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── KPI SCOREBOARD ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Platform Intelligence</div>', unsafe_allow_html=True)
kpis = [("1,034+","Matches"),("17","IPL Seasons"),("250K+","Deliveries"),
        ("~72%","ML Accuracy"),("10","Active Teams"),("35+","Venues")]
for col, (val, lbl) in zip(st.columns(6), kpis):
    with col:
        st.markdown(f'<div class="score-stat"><div class="val">{val}</div>'
                    f'<div class="lbl">{lbl}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)

# ── FEATURE GRID — 5 features ─────────────────────────────────────────────────
st.markdown('<div class="sec-label">What\'s Inside</div>', unsafe_allow_html=True)
features = [
    ("⚡","IPL Dashboard",
     "Power BI embedded visuals — season stats, toss analysis, team performance & venue heatmaps.","tag-c"),
    ("🎯","Match Prediction",
     "Select two teams + venue + toss. The ML model returns win probability in under a second.","tag-o"),
    ("🤖","AI Analytics Chat",
     "Ask anything in plain English — AI generates SQL, hits the live DB, and charts the answer.","tag-c"),
    ("📡","Ball-by-Ball Data",
     "250K+ deliveries across 17 seasons. Every run, wicket, and extra stored in PostgreSQL.","tag-w"),
    ("🧬","ML Pipeline",
     "Random Forest trained on toss, venue, head-to-head features. Served via joblib + Streamlit.","tag-o"),
]
for col, (icon, title, desc, tag) in zip(st.columns(5), features):
    with col:
        st.markdown(f"""
        <div class="feat-card">
            <span class="feat-icon">{icon}</span>
            <div class="feat-title">{title}</div>
            <div class="feat-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)

# ── HOW TO USE + TROPHIES ─────────────────────────────────────────────────────
left, right = st.columns([3, 2])
with left:
    st.markdown('<div class="sec-label">How To Use</div>', unsafe_allow_html=True)
    for num, text in [
        ("01","<b>Explore the Dashboard</b> — open IPL Dashboard to browse 17 seasons of Power BI analytics."),
        ("02","<b>Configure a Match</b> — go to Match Prediction, select teams, venue &amp; toss outcome."),
        ("03","<b>Chat with the AI</b> — open AI Analytics Chat and ask any IPL question in plain English."),
        ("04","<b>Read the Docs</b> — visit About Project for the full data pipeline &amp; model architecture."),
    ]:
        st.markdown(f'<div class="step-block"><div class="step-num">{num}</div>'
                    f'<div class="step-body">{text}</div></div>', unsafe_allow_html=True)

with right:
    st.markdown('<div class="sec-label">Most Successful Teams</div>', unsafe_allow_html=True)
    for name, titles, color in [
        ("Mumbai Indians",5,"var(--orange)"),("Chennai Super Kings",5,"var(--orange)"),
        ("Kolkata Knight Riders",3,"var(--cyan)"),("Sunrisers Hyderabad",2,"var(--cyan2)"),
        ("Rajasthan Royals",2,"var(--cyan2)"),
    ]:
        short = "".join(w[0] for w in name.split())
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.7rem;">
            <div style="font-family:'Orbitron',sans-serif;font-size:.68rem;font-weight:700;
                        color:{color};width:2.2rem;flex-shrink:0;">{short}</div>
            <div style="flex:1;">
                <div style="font-family:'Barlow Condensed',sans-serif;font-size:.8rem;
                            color:var(--muted2);margin-bottom:.25rem;">{name}</div>
                <div style="height:3px;background:var(--void4);">
                    <div style="height:100%;width:{titles/5*100}%;
                                background:linear-gradient(90deg,{color},transparent);
                                box-shadow:0 0 6px {color};"></div>
                </div>
            </div>
            <div style="font-family:'Orbitron',sans-serif;font-size:.9rem;font-weight:700;
                        color:{color};">{'🏆'*titles}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("""
<div style="margin-top:2.5rem;padding:1rem;border-top:1px solid var(--border-o);
            display:flex;justify-content:space-between;flex-wrap:wrap;gap:.5rem;">
    <span style="font-family:'Barlow Condensed',sans-serif;font-size:.68rem;
                 letter-spacing:.14em;text-transform:uppercase;color:var(--muted);">
        IPL NEXUS · Final Year Capstone · Data Science
    </span>
    <span style="font-family:'Barlow Condensed',sans-serif;font-size:.68rem;color:var(--muted);">
        Python · Streamlit · Scikit-learn · PostgreSQL · Groq AI · Power BI
    </span>
</div>""", unsafe_allow_html=True)
