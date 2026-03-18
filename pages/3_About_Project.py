import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from style import GLOBAL_CSS, sidebar_html, sidebar_nav

st.set_page_config(page_title="IPL NEXUS · About", page_icon="◈", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    sidebar_nav()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="neon-hero" style="border-left-color:var(--muted);">
    <div class="hero-eyebrow" style="color:var(--muted2);">
        <span style="background:var(--muted2);display:inline-block;width:20px;height:1px;"></span>
        FINAL YEAR CAPSTONE PROJECT · DATA SCIENCE
    </div>
    <div class="hero-title">PROJECT  <span>ARCHITECTURE</span></div>
    <div class="hero-sub">
        It includes data processing, feature engineering, machine learning modeling, interactive dashboards, and deployment through a Streamlit web application.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tech Stack Grid ────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Technology Stack</div>', unsafe_allow_html=True)

stack = [
    ("🐍", "Python 3.10+",     "Core language &amp; ML pipeline",    "tag-o"),
    ("📊", "Streamlit",        "Multi-page web framework",           "tag-c"),
    ("🤖", "Scikit-learn",     "Random Forest classifier",           "tag-o"),
    ("🔢", "Pandas / NumPy",   "Data wrangling &amp; feature eng.",  "tag-w"),
    ("📈", "Power BI",         "Embedded analytics dashboard",       "tag-c"),
    ("💾", "Joblib",           "Model serialisation / loading",      "tag-w"),
    ("🗄️", "SQLite / CSV",     "Ball-by-ball data storage",          "tag-w"),
    ("☁️", "Streamlit Cloud",  "One-click cloud deployment",         "tag-c"),
]
cols = st.columns(4)
for i, (icon, name, desc, tag) in enumerate(stack):
    with cols[i % 4]:
        st.markdown(f"""
        <div class="nx-card nx-card-cyan" style="padding:1rem;text-align:center;">
            <div style="font-size:1.6rem;margin-bottom:.5rem;">{icon}</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.92rem;
                        font-weight:700;letter-spacing:.06em;color:var(--text);margin-bottom:.3rem;">{name}</div>
            <div style="font-size:.76rem;color:var(--muted2);margin-bottom:.6rem;">{desc}</div>
            <span class="nx-tag {tag}">{name.split('/')[0].strip()}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)

# ── Schema + Feature Engineering ──────────────────────────────────────────────
left, right = st.columns([3, 2])
with left:
    st.markdown('<div class="sec-label">Database Schema</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="nx-card">
        <table style="width:100%;border-collapse:collapse;font-size:.82rem;">
            <thead>
                <tr style="border-bottom:1px solid var(--border-o);">
                    <th style="text-align:left;padding:.5rem;color:var(--orange);
                               font-family:'Barlow Condensed',sans-serif;letter-spacing:.1em;">TABLE</th>
                    <th style="text-align:left;padding:.5rem;color:var(--orange);
                               font-family:'Barlow Condensed',sans-serif;letter-spacing:.1em;">KEY COLUMNS</th>
                    <th style="text-align:right;padding:.5rem;color:var(--orange);
                               font-family:'Barlow Condensed',sans-serif;letter-spacing:.1em;">ROWS</th>
                </tr>
            </thead>
            <tbody style="color:var(--muted2);">
                <tr style="border-bottom:1px solid rgba(255,255,255,.04);">
                    <td style="padding:.5rem;color:var(--cyan);font-family:'Barlow Condensed',sans-serif;">matches</td>
                    <td style="padding:.5rem;">match_id, season, winner, venue, toss…</td>
                    <td style="padding:.5rem;text-align:right;font-family:'Orbitron',sans-serif;
                               font-size:.75rem;color:var(--text);">1,034</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,.04);">
                    <td style="padding:.5rem;color:var(--cyan);font-family:'Barlow Condensed',sans-serif;">innings</td>
                    <td style="padding:.5rem;">innings_id, total_runs, run_rate…</td>
                    <td style="padding:.5rem;text-align:right;font-family:'Orbitron',sans-serif;
                               font-size:.75rem;color:var(--text);">~2,068</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,.04);">
                    <td style="padding:.5rem;color:var(--cyan);font-family:'Barlow Condensed',sans-serif;">deliveries</td>
                    <td style="padding:.5rem;">delivery_id, batter_id, runs_batter…</td>
                    <td style="padding:.5rem;text-align:right;font-family:'Orbitron',sans-serif;
                               font-size:.75rem;color:var(--text);">250K+</td>
                </tr>
                <tr style="border-bottom:1px solid rgba(255,255,255,.04);">
                    <td style="padding:.5rem;color:var(--cyan);font-family:'Barlow Condensed',sans-serif;">players</td>
                    <td style="padding:.5rem;">player_id, player_name, registry_id</td>
                    <td style="padding:.5rem;text-align:right;font-family:'Orbitron',sans-serif;
                               font-size:.75rem;color:var(--text);">~600</td>
                </tr>
                <tr>
                    <td style="padding:.5rem;color:var(--cyan);font-family:'Barlow Condensed',sans-serif;">player_teams</td>
                    <td style="padding:.5rem;">player_id, team_name, season</td>
                    <td style="padding:.5rem;text-align:right;font-family:'Orbitron',sans-serif;
                               font-size:.75rem;color:var(--text);">~3,500</td>
                </tr>
            </tbody>
        </table>
    </div>
    """, unsafe_allow_html=True)

with right:
    st.markdown('<div class="sec-label">ML Feature Engineering</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="nx-card nx-card-cyan">
    """, unsafe_allow_html=True)
    features = [
        ("team1 / team2",          "Label encoded team names"),
        ("venue",                  "Stadium — encoded by win history"),
        ("toss_winner",            "Which team won the toss"),
        ("toss_decision",          "Bat or Field (binary)"),
        ("toss_winner_is_team1",   "Binary derived flag"),
        ("decision_bat",           "Binary derived flag"),
    ]
    for feat, desc in features:
        st.markdown(f"""
        <div style="padding:.5rem 0;border-bottom:1px solid rgba(255,255,255,.04);
                    display:flex;gap:.8rem;align-items:flex-start;">
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.75rem;
                        color:var(--cyan);letter-spacing:.04em;min-width:140px;">{feat}</div>
            <div style="font-size:.76rem;color:var(--muted2);">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("""
        <div style="margin-top:.8rem;font-family:'Barlow Condensed',sans-serif;
                    font-size:.7rem;color:var(--muted);letter-spacing:.1em;">
            TARGET: <span style="color:var(--orange);">winner</span> (team name string)
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)

# ── Model Architecture KPIs ────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Model Architecture</div>', unsafe_allow_html=True)
mc1, mc2, mc3, mc4 = st.columns(4)
for col, (v, l, d) in zip([mc1,mc2,mc3,mc4], [
    ("RF",    "Algorithm",      "Random Forest"),
    ("200",   "Estimators",     "n_estimators"),
    ("~72%",  "Test Accuracy",  "Cross-validated"),
    ("2025",  "Holdout Year",   "Test set"),
]):
    with col:
        st.metric(l, v, d)

st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)

# ── How to Run ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Local Setup Guide</div>', unsafe_allow_html=True)

steps_run = [
    ("01", "Clone / Download the repo",
     "<code>git clone https://github.com/your-username/ipl-nexus.git && cd ipl-nexus</code>"),
    ("02", "Install Python dependencies",
     "<code>pip install -r requirements.txt</code>"),
    ("03", "Copy your trained model to the app root",
     "<code>cp /path/to/ipl_model.pkl .</code> &nbsp;— must be alongside Home.py"),
    ("04", "Launch Streamlit",
     "<code>streamlit run Home.py</code>"),
    ("05", "Open in browser",
     "Auto-opens at <code>http://localhost:8501</code>"),
]
for num, title, detail in steps_run:
    st.markdown(f"""
    <div class="step-block">
        <div class="step-num">{num}</div>
        <div class="step-body">
            <b>{title}</b><br>
            <span style="font-size:.8rem;">{detail}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with st.expander("◈  requirements.txt"):
    st.code("""streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
joblib>=1.3.0""", language="text")

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="slash-divider"></div>
<div style="text-align:center;padding:1rem 0;font-family:'Barlow Condensed',sans-serif;
            font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);">
    IPL NEXUS · Final Year Data Science Capstone · Built with Python &amp; Streamlit<br>
    <span style="color:var(--muted);font-size:.62rem;">
        Predictions are probabilistic — not intended for betting or wagering.
    </span>
</div>
""", unsafe_allow_html=True)
