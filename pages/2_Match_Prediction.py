import streamlit as st
import pandas as pd
import numpy as np
import joblib, os, time, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from style import GLOBAL_CSS, sidebar_html, sidebar_nav

st.set_page_config(page_title="IPL NEXUS · Predict", page_icon="🎯", layout="wide")
st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(sidebar_html(), unsafe_allow_html=True)
    sidebar_nav()
    st.markdown("""
    <div style="margin-top:1rem;padding:.8rem;background:var(--void3);border:1px solid var(--border-o);">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.6rem;letter-spacing:.18em;
                    text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;">Model Info</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.78rem;color:var(--muted2);line-height:2;">
            📦 &nbsp;<b style="color:var(--text);">ipl_model.pkl</b><br>
            🎯 &nbsp;Accuracy: <b style="color:var(--orange);">~72%</b><br>
            📅 &nbsp;Trained: 2008–2024<br>
            🔧 &nbsp;Algorithm: Random Forest
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:1.5rem;">
        <div class="sec-label" style="padding:0 .5rem;">Model Info</div>
        <div style="padding:.8rem;background:var(--void3);border:1px solid var(--border-o);
                    font-family:'Barlow Condensed',sans-serif;font-size:.78rem;color:var(--muted2);
                    line-height:2;">
            📦 &nbsp;<b style="color:var(--text);">ipl_model.pkl</b><br>
            🎯 &nbsp;Accuracy: <b style="color:var(--orange);">~72%</b><br>
            📅 &nbsp;Trained: 2008–2024<br>
            🔧 &nbsp;Algorithm: Random Forest
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Data ───────────────────────────────────────────────────────────────────────
IPL_TEAMS = [
    "Chennai Super Kings", "Delhi Capitals", "Gujarat Titans",
    "Kolkata Knight Riders", "Lucknow Super Giants", "Mumbai Indians",
    "Punjab Kings", "Rajasthan Royals",
    "Royal Challengers Bengaluru", "Sunrisers Hyderabad",
]
IPL_VENUES = [
    "Wankhede Stadium, Mumbai",
    "M. A. Chidambaram Stadium, Chennai",
    "Eden Gardens, Kolkata",
    "Arun Jaitley Stadium, Delhi",
    "M. Chinnaswamy Stadium, Bengaluru",
    "Rajiv Gandhi Intl. Cricket Stadium, Hyderabad",
    "Narendra Modi Stadium, Ahmedabad",
    "Sawai Mansingh Stadium, Jaipur",
    "Punjab Cricket Association IS Bindra Stadium, Mohali",
    "BRSABV Ekana Cricket Stadium, Lucknow",
    "Barsapara Cricket Stadium, Guwahati",
    "Himachal Pradesh Cricket Association Stadium, Dharamsala",
]

# ── Model ──────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_model():
    for path in ["ipl_model.pkl",
                 os.path.join(os.path.dirname(__file__), "..", "ipl_model.pkl")]:
        if os.path.exists(path):
            return joblib.load(path)
    return None

def build_input_df(team1, team2, venue, toss_winner, toss_decision):
    """
    Build the feature DataFrame. EDIT column names to match your training pipeline.
    """
    return pd.DataFrame({
        "team1":                [team1],
        "team2":                [team2],
        "venue":                [venue],
        "toss_winner":          [toss_winner],
        "toss_decision":        [toss_decision.lower()],
        "toss_winner_is_team1": [int(toss_winner == team1)],
        "decision_bat":         [int(toss_decision.lower() == "bat")],
    })

def get_prediction(model, df, team1, team2):
    if model is None:
        rng = np.random.default_rng(seed=abs(hash(team1 + team2)) % (2**31))
        p1 = float(rng.uniform(0.35, 0.72))
        p2 = 1.0 - p1
        return (team1 if p1 > p2 else team2), round(p1*100,1), round(p2*100,1)
    try:
        if hasattr(model, "predict_proba"):
            probs   = model.predict_proba(df)[0]
            classes = list(model.classes_)
            i1 = classes.index(team1) if team1 in classes else 0
            i2 = classes.index(team2) if team2 in classes else 1
            p1, p2 = float(probs[i1]), float(probs[i2])
            total  = p1 + p2
            p1, p2 = p1/total, p2/total
        else:
            pred = model.predict(df)[0]
            p1 = 0.64 if pred == team1 else 0.36
            p2 = 1.0 - p1
        winner = team1 if p1 >= p2 else team2
        return winner, round(p1*100,1), round(p2*100,1)
    except Exception as e:
        st.warning(f"Model error: {e}. Showing demo output.")
        rng = np.random.default_rng(42)
        p1 = float(rng.uniform(0.4, 0.7))
        p2 = 1.0 - p1
        return (team1 if p1 > p2 else team2), round(p1*100,1), round(p2*100,1)

# ── Page hero ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="neon-hero">
    <div class="hero-eyebrow">
        <span class="live-dot"></span> AI PREDICTION ENGINE · IPL 2026 SEASON
    </div>
    <div class="hero-title">IPL MATCH OUTCOME <span>PREDICTION</span></div>
    <div class="hero-sub">
        Select match conditions to generate win probabilities using
        a trained machine learning model.
    </div>
</div>
""", unsafe_allow_html=True)

# ── Input Form ─────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-label">Configure Match Parameters</div>', unsafe_allow_html=True)

with st.container():
    st.markdown('<div class="nx-card">', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        team1 = st.selectbox("TEAM 1  ▸  HOME / LISTED FIRST", IPL_TEAMS, index=5)
    with col2:
        team2 = st.selectbox("TEAM 2  ▸  AWAY / LISTED SECOND",
                             [t for t in IPL_TEAMS if t != team1], index=0)

    venue = st.selectbox("VENUE / STADIUM", IPL_VENUES)

    col3, col4 = st.columns(2)
    with col3:
        toss_winner   = st.selectbox("TOSS WINNER", [team1, team2])
    with col4:
        toss_decision = st.selectbox("TOSS DECISION", ["Bat", "Field"])

    st.markdown('</div>', unsafe_allow_html=True)

# ── VS Bar ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="vs-bar">
    <div>
        <div class="vs-team vs-team-1">{team1}</div>
        <div class="vs-meta">Team 1</div>
    </div>
    <div style="text-align:center;">
        <div class="vs-glyph">VS</div>
        <div class="vs-meta">📍 {venue.split(',')[0]}</div>
    </div>
    <div style="text-align:right;">
        <div class="vs-team vs-team-2">{team2}</div>
        <div class="vs-meta">Team 2</div>
    </div>
</div>
<div style="font-family:'Barlow Condensed',sans-serif;font-size:.8rem;color:var(--muted2);
            margin-bottom:1.2rem;letter-spacing:.06em;">
    🪙 &nbsp;<b style="color:var(--text);">{toss_winner}</b> won the toss and elected to
    <b style="color:var(--orange);">{toss_decision.upper()}</b>
</div>
""", unsafe_allow_html=True)

# Predict button
predict_btn = st.button("◈  ENGAGE PREDICTION ENGINE  ◈")

# ── RESULT ─────────────────────────────────────────────────────────────────────
if predict_btn:
    with st.spinner(""):
        time.sleep(0.9)
        model       = load_model()
        demo_mode   = model is None
        inp_df      = build_input_df(team1, team2, venue, toss_winner, toss_decision)
        winner, p1, p2 = get_prediction(model, inp_df, team1, team2)

    if demo_mode:
        st.markdown("""
        <div style="padding:.7rem 1rem;background:rgba(0,240,255,0.05);border:1px solid var(--border-c);
                    border-left:2px solid var(--cyan);font-family:'Barlow Condensed',sans-serif;
                    font-size:.82rem;color:var(--muted2);margin-bottom:1rem;">
            ℹ &nbsp;<b style="color:var(--cyan);">DEMO MODE</b> — place
            <code>ipl_model.pkl</code> in the app root to enable real predictions.
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="slash-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Prediction Output</div>', unsafe_allow_html=True)

    # ── Win Probability Cards ──────────────────────────────────────────────────
    r1, r2 = st.columns(2)
    with r1:
        is_w = winner == team1
        st.markdown(f"""
        <div class="{'pred-winner' if is_w else 'pred-loser'}">
            {'<div class="glitch" style="margin-bottom:.8rem;">◈ PREDICTED WINNER ◈</div>' if is_w else
             '<div style="font-family:Barlow Condensed,sans-serif;font-size:.65rem;letter-spacing:.2em;color:var(--muted);margin-bottom:.8rem;">RUNNER UP</div>'}
            <div class="{'pred-pct-win' if is_w else 'pred-pct-lose'}">{p1}%</div>
            <div class="pred-tname" style="color:{'var(--orange)' if is_w else 'var(--muted2)'};">
                {team1}
            </div>
            <div style="margin-top:.8rem;font-family:'Barlow Condensed',sans-serif;
                        font-size:.7rem;color:var(--muted);letter-spacing:.1em;">WIN PROBABILITY</div>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        is_w = winner == team2
        st.markdown(f"""
        <div class="{'pred-winner' if is_w else 'pred-loser'}">
            {'<div class="glitch" style="margin-bottom:.8rem;">◈ PREDICTED WINNER ◈</div>' if is_w else
             '<div style="font-family:Barlow Condensed,sans-serif;font-size:.65rem;letter-spacing:.2em;color:var(--muted);margin-bottom:.8rem;">RUNNER UP</div>'}
            <div class="{'pred-pct-win' if is_w else 'pred-pct-lose'}">{p2}%</div>
            <div class="pred-tname" style="color:{'var(--orange)' if is_w else 'var(--muted2)'};">
                {team2}
            </div>
            <div style="margin-top:.8rem;font-family:'Barlow Condensed',sans-serif;
                        font-size:.7rem;color:var(--muted);letter-spacing:.1em;">WIN PROBABILITY</div>
        </div>
        """, unsafe_allow_html=True)

    # ── Probability bars ───────────────────────────────────────────────────────
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<div class="sec-label">Probability Distribution</div>', unsafe_allow_html=True)

    bar_l, bar_r = st.columns([1, 8])
    with bar_r:
        st.markdown(f"""
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.72rem;
                    letter-spacing:.1em;color:var(--orange);margin-bottom:.3rem;">{team1.upper()}</div>
        """, unsafe_allow_html=True)
        st.progress(int(p1))
        st.markdown(f"""
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.72rem;
                    letter-spacing:.1em;color:var(--cyan);margin:.5rem 0 .3rem;">{team2.upper()}</div>
        """, unsafe_allow_html=True)
        st.progress(int(p2))

    # ── Verdict Panel ──────────────────────────────────────────────────────────
    margin = abs(p1 - p2)
    if margin >= 25:
        conf, conf_tag = "HIGH CONFIDENCE", "tag-o"
    elif margin >= 10:
        conf, conf_tag = "MODERATE",        "tag-c"
    else:
        conf, conf_tag = "COIN FLIP",       "tag-w"

    st.markdown(f"""
    <div class="nx-card" style="margin-top:1rem;display:flex;gap:2rem;flex-wrap:wrap;align-items:center;">
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;letter-spacing:.18em;
                        text-transform:uppercase;color:var(--muted);margin-bottom:.3rem;">Predicted Winner</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:1.2rem;
                        font-weight:700;color:var(--orange);">{winner}</div>
        </div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;letter-spacing:.18em;
                        text-transform:uppercase;color:var(--muted);margin-bottom:.3rem;">Confidence</div>
            <span class="nx-tag {conf_tag}">{conf}</span>
        </div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;letter-spacing:.18em;
                        text-transform:uppercase;color:var(--muted);margin-bottom:.3rem;">Probability Gap</div>
            <div style="font-family:'Orbitron',sans-serif;font-size:1rem;font-weight:700;color:var(--text);">
                {margin:.1f}%
            </div>
        </div>
        <div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.65rem;letter-spacing:.18em;
                        text-transform:uppercase;color:var(--muted);margin-bottom:.3rem;">Toss Factor</div>
            <div style="font-family:'Barlow Condensed',sans-serif;font-size:.88rem;color:var(--muted2);">
                {toss_winner} chose to <b style="color:var(--orange);">{toss_decision.upper()}</b>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("◈  VIEW RAW INPUT FEATURES"):
        st.dataframe(inp_df.T.rename(columns={0: "Value"}),
                     use_container_width=True)
