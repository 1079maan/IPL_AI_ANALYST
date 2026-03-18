GLOBAL_CSS = """
<style>
/* ═══════════════════════════════════════════════════════
   IPL NEXUS — NEON STADIUM UI SYSTEM
   Fonts: Orbitron (display) + Barlow Condensed (body)
   Palette: #FF4D00 orange · #00F0FF cyan · #0A0A0F void
═══════════════════════════════════════════════════════ */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Barlow+Condensed:wght@300;400;500;600;700&family=Barlow:wght@300;400;500&display=swap');

:root {
  --orange:   #FF4D00;
  --orange2:  #FF7A30;
  --cyan:     #00F0FF;
  --cyan2:    #00B8CC;
  --void:     #06060A;
  --void2:    #0C0C14;
  --void3:    #12121E;
  --void4:    #1A1A2E;
  --glass:    rgba(255,255,255,0.03);
  --glass2:   rgba(255,255,255,0.06);
  --border-o: rgba(255,77,0,0.25);
  --border-c: rgba(0,240,255,0.2);
  --text:     #E8ECF4;
  --muted:    #5A6080;
  --muted2:   #8892AA;
}

/* ── Reset & Base ── */
html, body, [class*="css"], .main {
  font-family: 'Barlow', sans-serif !important;
  background-color: var(--void) !important;
  color: var(--text) !important;
}

/* Animated scanline grain overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.03) 2px,
      rgba(0,0,0,0.03) 4px
    );
  pointer-events: none;
  z-index: 9999;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #08080F 0%, #0C0C18 100%) !important;
  border-right: 1px solid var(--border-o) !important;
  position: relative;
}
[data-testid="stSidebar"]::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 1px; height: 100%;
  background: linear-gradient(180deg, transparent, var(--orange), transparent);
  opacity: 0.5;
}
[data-testid="stSidebar"] * { color: var(--text) !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* ── Page links (sidebar) ── */
[data-testid="stPageLink"] a {
  display: flex !important;
  align-items: center !important;
  gap: 0.6rem !important;
  padding: 0.55rem 1rem !important;
  border-radius: 0 !important;
  border-left: 2px solid transparent !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 0.9rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  color: var(--muted2) !important;
  text-decoration: none !important;
  transition: all 0.2s ease !important;
  background: transparent !important;
}
[data-testid="stPageLink"] a:hover {
  border-left-color: var(--orange) !important;
  color: var(--orange) !important;
  background: rgba(255,77,0,0.06) !important;
}

/* ── Headings ── */
h1, h2, h3 {
  font-family: 'Orbitron', sans-serif !important;
  color: var(--text) !important;
  letter-spacing: 0.04em !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
  background: var(--glass) !important;
  border: 1px solid var(--border-o) !important;
  border-top: 2px solid var(--orange) !important;
  border-radius: 0 !important;
  padding: 1rem 1.2rem !important;
  position: relative;
  clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 0 100%);
}
[data-testid="stMetricValue"] {
  color: var(--cyan) !important;
  font-family: 'Orbitron', sans-serif !important;
  font-size: 1.6rem !important;
  font-weight: 700 !important;
}
[data-testid="stMetricLabel"] {
  color: var(--muted2) !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.14em;
  text-transform: uppercase !important;
}
[data-testid="stMetricDelta"] { font-size: 0.72rem !important; }

/* ── Buttons ── */
.stButton > button {
  background: transparent !important;
  border: 1px solid var(--orange) !important;
  color: var(--orange) !important;
  font-family: 'Orbitron', sans-serif !important;
  font-weight: 700 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.15em !important;
  border-radius: 0 !important;
  padding: 0.7rem 2rem !important;
  text-transform: uppercase !important;
  clip-path: polygon(0 0, calc(100% - 8px) 0, 100% 8px, 100% 100%, 8px 100%, 0 calc(100% - 8px));
  transition: all 0.25s ease !important;
  position: relative;
}
.stButton > button::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(255,77,0,0.12), transparent);
  opacity: 0;
  transition: opacity 0.25s ease;
}
.stButton > button:hover {
  background: rgba(255,77,0,0.15) !important;
  color: #fff !important;
  border-color: var(--orange2) !important;
  box-shadow: 0 0 20px rgba(255,77,0,0.3), inset 0 0 20px rgba(255,77,0,0.05) !important;
  transform: translateY(-1px) !important;
}

/* ── Selectboxes ── */
[data-testid="stSelectbox"] > div > div {
  background: var(--void3) !important;
  border: 1px solid var(--border-o) !important;
  border-radius: 0 !important;
  color: var(--text) !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  clip-path: polygon(0 0, calc(100% - 6px) 0, 100% 6px, 100% 100%, 0 100%);
}
label[data-testid="stWidgetLabel"] p {
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.14em !important;
  text-transform: uppercase !important;
  color: var(--muted2) !important;
}

/* ── Progress bars ── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--orange), var(--cyan)) !important;
  border-radius: 0 !important;
  box-shadow: 0 0 8px rgba(0,240,255,0.4) !important;
}
.stProgress > div > div {
  background: var(--void3) !important;
  border-radius: 0 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
  gap: 0 !important;
  background: transparent !important;
  border-bottom: 1px solid var(--border-o) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  color: var(--muted) !important;
  font-family: 'Barlow Condensed', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  padding: 0.7rem 1.5rem !important;
  border-radius: 0 !important;
  transition: all 0.2s ease !important;
}
.stTabs [aria-selected="true"] {
  color: var(--orange) !important;
  border-bottom-color: var(--orange) !important;
  background: rgba(255,77,0,0.05) !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
  background: var(--void3) !important;
  border: 1px solid var(--border-o) !important;
  border-radius: 0 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--void2); }
::-webkit-scrollbar-thumb { background: var(--orange); }

/* ── Dividers ── */
hr { border: none !important; border-top: 1px solid var(--border-o) !important; }

/* ── Info / Warning boxes ── */
[data-testid="stInfo"] {
  background: rgba(0,240,255,0.06) !important;
  border: 1px solid var(--border-c) !important;
  border-radius: 0 !important;
  color: var(--text) !important;
}

/* ══ CUSTOM COMPONENTS ══════════════════════════════════ */

/* — Page hero — */
.neon-hero {
  position: relative;
  background: var(--void2);
  border: 1px solid var(--border-o);
  border-left: 3px solid var(--orange);
  padding: 2.5rem 2rem 2.5rem 2.5rem;
  margin-bottom: 2rem;
  overflow: hidden;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 16px), calc(100% - 16px) 100%, 0 100%);
}
.neon-hero::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, var(--orange), var(--cyan), transparent);
}
.neon-hero::after {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 240px; height: 240px;
  background: radial-gradient(circle, rgba(255,77,0,0.07) 0%, transparent 65%);
  pointer-events: none;
}
.hero-eyebrow {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--orange);
  margin-bottom: 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.hero-eyebrow::before {
  content: '';
  display: inline-block;
  width: 20px; height: 1px;
  background: var(--orange);
}
.hero-title {
  font-family: 'Orbitron', sans-serif;
  font-size: clamp(1.6rem, 3vw, 2.6rem);
  font-weight: 900;
  line-height: 1.1;
  color: #fff;
  letter-spacing: 0.02em;
}
.hero-title span { color: var(--orange); }
.hero-sub {
  font-family: 'Barlow', sans-serif;
  font-size: 0.9rem;
  color: var(--muted2);
  margin-top: 0.7rem;
  max-width: 560px;
  line-height: 1.65;
}

/* — Neon card — */
.nx-card {
  background: var(--void3);
  border: 1px solid rgba(255,255,255,0.06);
  border-top: 2px solid var(--orange);
  padding: 1.4rem;
  margin-bottom: 1rem;
  position: relative;
  clip-path: polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 0 100%);
  transition: border-color 0.25s ease, box-shadow 0.25s ease;
}
.nx-card:hover {
  border-color: rgba(255,77,0,0.5);
  box-shadow: 0 0 20px rgba(255,77,0,0.08);
}
.nx-card-cyan {
  border-top-color: var(--cyan);
}
.nx-card-cyan:hover {
  border-color: rgba(0,240,255,0.4);
  box-shadow: 0 0 20px rgba(0,240,255,0.08);
}

/* — Section label — */
.sec-label {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--muted);
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1rem;
}
.sec-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, var(--border-o), transparent);
}

/* — Tag pill — */
.nx-tag {
  display: inline-block;
  padding: 0.18rem 0.65rem;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  clip-path: polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%);
}
.tag-o  { background: rgba(255,77,0,0.15);  color: var(--orange); }
.tag-c  { background: rgba(0,240,255,0.1);  color: var(--cyan);   }
.tag-w  { background: rgba(255,255,255,0.07); color: var(--muted2); }

/* — Scoreboard stat — */
.score-stat {
  text-align: center;
  padding: 0.8rem;
  border: 1px solid rgba(255,255,255,0.05);
  border-bottom: 2px solid var(--cyan);
  background: var(--glass);
}
.score-stat .val {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--cyan);
  line-height: 1;
}
.score-stat .lbl {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.65rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 0.25rem;
}

/* — VS battle bar — */
.vs-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--void3);
  border: 1px solid var(--border-o);
  border-left: 3px solid var(--orange);
  border-right: 3px solid var(--cyan);
  padding: 1rem 1.5rem;
  margin: 0.8rem 0 1.2rem;
  clip-path: polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%);
}
.vs-team {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.04em;
}
.vs-team-1 { color: var(--orange); }
.vs-team-2 { color: var(--cyan);   }
.vs-glyph {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: 0.2em;
}
.vs-meta {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.72rem;
  color: var(--muted);
  letter-spacing: 0.1em;
  margin-top: 0.3rem;
}

/* — Prediction result — */
.pred-winner {
  background: linear-gradient(135deg, rgba(255,77,0,0.12), rgba(255,77,0,0.04));
  border: 1px solid rgba(255,77,0,0.5);
  border-top: 3px solid var(--orange);
  padding: 2rem;
  text-align: center;
  position: relative;
  clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
}
.pred-loser {
  background: var(--void3);
  border: 1px solid rgba(255,255,255,0.06);
  border-top: 3px solid var(--void4);
  padding: 2rem;
  text-align: center;
  clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px, 100% 100%, 0 100%);
}
.pred-pct-win {
  font-family: 'Orbitron', sans-serif;
  font-size: 3.8rem;
  font-weight: 900;
  color: var(--orange);
  line-height: 1;
  text-shadow: 0 0 30px rgba(255,77,0,0.5);
}
.pred-pct-lose {
  font-family: 'Orbitron', sans-serif;
  font-size: 3.8rem;
  font-weight: 900;
  color: var(--muted);
  line-height: 1;
}
.pred-tname {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  margin-top: 0.6rem;
}

/* — Glitch text (winner label) — */
@keyframes glitch1 {
  0%, 90%, 100% { clip-path: inset(0); transform: none; }
  91% { clip-path: inset(20% 0 60% 0); transform: translateX(-4px); }
  93% { clip-path: inset(60% 0 10% 0); transform: translateX(4px); }
  95% { clip-path: inset(40% 0 40% 0); transform: translateX(-2px); }
}
.glitch {
  position: relative;
  display: inline-block;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.3em;
  text-transform: uppercase;
  color: var(--orange);
  animation: glitch1 4s infinite;
}

/* — Animated neon glow dot — */
@keyframes pulse-dot {
  0%, 100% { opacity: 1; box-shadow: 0 0 4px var(--orange); }
  50%       { opacity: 0.4; box-shadow: 0 0 12px var(--orange); }
}
.live-dot {
  display: inline-block;
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--orange);
  animation: pulse-dot 1.5s infinite;
  vertical-align: middle;
  margin-right: 0.4rem;
}

/* — Diagonal slash divider — */
.slash-divider {
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, var(--orange), var(--cyan), transparent);
  margin: 1.5rem 0;
  position: relative;
}
.slash-divider::after {
  content: '//';
  position: absolute;
  top: -9px; left: 50%;
  transform: translateX(-50%);
  background: var(--void);
  padding: 0 0.6rem;
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.7rem;
  color: var(--muted);
  letter-spacing: 0.2em;
}

/* — Sidebar brand — */
.sb-brand {
  padding: 1.5rem 1rem 1rem;
  border-bottom: 1px solid var(--border-o);
  margin-bottom: 0.8rem;
  position: relative;
}
.sb-logo-text {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.1rem;
  font-weight: 900;
  color: #fff;
  letter-spacing: 0.06em;
}
.sb-logo-text span { color: var(--orange); }
.sb-tagline {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 0.6rem;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 0.2rem;
}

/* — Feature icon card — */
.feat-card {
  padding: 1.5rem 1.2rem;
  background: var(--void3);
  border: 1px solid rgba(255,255,255,0.05);
  border-bottom: 2px solid var(--orange);
  position: relative;
  transition: all 0.25s ease;
}
.feat-card:hover {
  border-bottom-color: var(--cyan);
  background: var(--void4);
  transform: translateY(-3px);
  box-shadow: 0 8px 30px rgba(0,240,255,0.07);
}
.feat-icon {
  font-size: 1.8rem;
  margin-bottom: 0.8rem;
  display: block;
}
.feat-title {
  font-family: 'Barlow Condensed', sans-serif;
  font-size: 1.05rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--text);
  margin-bottom: 0.4rem;
}
.feat-desc {
  font-size: 0.82rem;
  color: var(--muted2);
  line-height: 1.65;
}

/* — Step block — */
.step-block {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  margin-bottom: 1rem;
}
.step-num {
  flex-shrink: 0;
  width: 2rem; height: 2rem;
  background: var(--orange);
  color: var(--void);
  font-family: 'Orbitron', sans-serif;
  font-weight: 700;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  justify-content: center;
  clip-path: polygon(0 0, 100% 0, 100% calc(100% - 6px), calc(100% - 6px) 100%, 0 100%);
}
.step-body { font-size: 0.88rem; color: var(--muted2); line-height: 1.6; }
.step-body b { color: var(--text); }

/* Dataframe / table */
[data-testid="stDataFrame"] { border: 1px solid var(--border-o) !important; }
</style>
"""


def sidebar_html(active="home"):
    return """
    <div class="sb-brand">
        <div style="font-size:1.6rem; margin-bottom:0.4rem;">🏏</div>
        <div class="sb-logo-text">IPL Data Intelligence<span></span></div>
        <div class="sb-tagline">Analytics &amp; Prediction · 2026</div>
    </div>
    <div style="padding: 0.4rem 0;">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.6rem;letter-spacing:.25em;
                    text-transform:uppercase;color:var(--muted);padding:.4rem 1rem .6rem;">
            Navigation
        </div>
    </div>
    """


def sidebar_nav():
    """Render all 5 nav page links — call this inside every page's sidebar block."""
    import streamlit as st
    st.page_link("Home.py",                      label="🏠  Home")
    st.page_link("pages/1_IPL_Dashboard.py",     label="⚡  IPL Dashboard")
    st.page_link("pages/2_Match_Prediction.py",  label="🎯  IPL Match Prediction")
    st.page_link("pages/4_AI_Chat.py",           label="🤖  AI Analytics Chat")
    st.page_link("pages/3_About_Project.py",     label="◈   Project Architecture ")
    st.markdown("""
    <div style="margin:1rem .5rem 0;padding:.8rem;background:rgba(0,240,255,0.04);
                border:1px solid rgba(0,240,255,0.12);border-left:2px solid var(--cyan);">
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.6rem;letter-spacing:.18em;
                    text-transform:uppercase;color:var(--muted);margin-bottom:.5rem;">System</div>
        <div style="font-family:'Barlow Condensed',sans-serif;font-size:.76rem;
                    color:var(--muted2);line-height:2;">
            🤖 &nbsp;Groq AI · SQL Engine<br>
            🗄️ &nbsp;PostgreSQL · IPL Data<br>
            📊 &nbsp;Plotly · Neon Charts<br>
            ⚡ &nbsp;IPL 2008 – 2025
        </div>
    </div>
    """, unsafe_allow_html=True)
